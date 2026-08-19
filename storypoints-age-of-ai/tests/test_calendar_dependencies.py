"""Hand-calculated and adversarial tests for calendars and dependencies."""
from __future__ import annotations

import copy
import unittest

from simulation.config import ConfigError, cross_validate, load_and_validate
from simulation.engine import run_truth
from simulation.scheduling import CalendarSemanticsError, DependencySemanticsError
from simulation.verification import check_queue_area_reconciliation


SCHEMA = "research-design/03b_simulation_schema.json"
EXAMPLE = "simulation/configs/example.yaml"


class CalendarAndDependencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = load_and_validate(EXAMPLE, SCHEMA)

    def one_item_fixed(self) -> dict:
        config = copy.deepcopy(self.base)
        config["arrival_models"][0]["parameters"].update(count=1, start=0, spacing=0)
        config["arrival_models"][0]["parameters"]["template_ids"] = ["standard_feature"]
        config["time_model"]["horizon"] = 100
        stage_values = {"context_preparation": 1.0, "implementation": 0.5,
                        "verification": 0.5, "acceptance": 0.5}
        for demand in config["demand_models"]:
            if demand["work_item_selector"] != "standard_feature":
                continue
            value = stage_values[demand["stage_id"]]
            demand["base_distribution"]["family"] = "fixed"
            demand["base_distribution"]["parameters"] = {"value": value}
            demand["base_distribution"].pop("truncation", None)
        for world in config["data_generating_worlds"]:
            world["truth_parameters"].update(
                service_multiplier=1, gate_fail_probability=0,
                gate_conditional_probability=0,
            )
        return config

    @staticmethod
    def add_dependent_template(config: dict, *, cyclic: bool = False) -> None:
        if any(template["id"] == "dependent_feature" for template in config["work_item_templates"]):
            model = next(model for model in config["dependency_models"] if model["id"] == "feature_dependency")
            if cyclic:
                model["edges"].append(["dependent_feature", "standard_feature"])
                config["work_item_templates"][0]["dependency_ids"] = ["feature_dependency"]
            config["arrival_models"][0]["parameters"].update(
                count=2, start=0, spacing=0,
                template_ids=["standard_feature", "dependent_feature"],
            )
            return
        base_template = config["work_item_templates"][0]
        dependent = copy.deepcopy(base_template)
        dependent["id"] = "dependent_feature"
        dependent["dependency_ids"] = ["portfolio_dependencies"]
        if cyclic:
            base_template["dependency_ids"] = ["portfolio_dependencies"]
        config["work_item_templates"].append(dependent)
        for original in list(config["demand_models"]):
            cloned = copy.deepcopy(original)
            cloned["id"] = "dependent_" + original["id"]
            cloned["work_item_selector"] = "dependent_feature"
            cloned["base_distribution"]["id"] = "dependent_" + original["base_distribution"]["id"]
            config["demand_models"].append(cloned)
        edges = [["standard_feature", "dependent_feature"]]
        if cyclic:
            edges.append(["dependent_feature", "standard_feature"])
        config["dependency_models"] = [{
            "id": "portfolio_dependencies",
            "edges": edges,
            "cycles_allowed_for_test": False,
            "release_rule": "all_predecessor_items_completed_successfully",
            "failure_policy": "block_successor",
            "scope": "template_all_to_all",
        }]
        config["arrival_models"][0]["parameters"].update(
            count=2, start=0, spacing=0,
            template_ids=["standard_feature", "dependent_feature"],
        )

    def test_blackout_pauses_touch_work_hand_calculation(self):
        config = self.one_item_fixed()
        config["capacity_calendars"][0]["blackout_periods"] = [{
            "start": "2026-08-13T00:30:00Z",
            "end": "2026-08-13T02:30:00Z",
        }]
        result = run_truth(config, "world_sp", seed=501)
        # Four stage services total 2.5 hours, gate assessment adds 0.5,
        # and the declared blackout adds 2.0 hours.
        self.assertAlmostEqual(result.items[0].terminal_time, 5.0, places=12)
        implementation = next(row for row in result.services if row.stage_id == "implementation")
        context = next(row for row in result.services if row.stage_id == "context_preparation")
        self.assertAlmostEqual(context.demand, 1.0, places=12)
        self.assertAlmostEqual(context.service_end - context.service_start, 3.0, places=12)
        self.assertAlmostEqual(context.calendar_pause, 2.0, places=12)
        self.assertTrue(any(row.event == "capacity_pause_applied" for row in result.events))

    def test_aggregate_effective_capacity_multiplier_is_rejected(self):
        config = self.one_item_fixed()
        interval = config["capacity_calendars"][0]["intervals"][0]
        interval.update(gross_hours=80, absence_hours=0, nonproject_hours=40, effective_hours=40)
        with self.assertRaisesRegex(CalendarSemanticsError, "explicit fully available window"):
            run_truth(config, "world_sp", seed=502)

    def test_full_horizon_blackout_censors_without_false_service(self):
        config = self.one_item_fixed()
        config["time_model"]["horizon"] = 5
        config["capacity_calendars"][0]["blackout_periods"] = [{
            "start": "2026-08-13T00:00:00Z",
            "end": "2026-08-13T10:00:00Z",
        }]
        result = run_truth(config, "world_sp", seed=503)
        self.assertEqual(result.items[0].terminal_state, "censored")
        self.assertEqual(result.services, ())

    def test_overlapping_intervals_are_a_hard_error(self):
        config = self.one_item_fixed()
        first = config["capacity_calendars"][0]["intervals"][0]
        second = copy.deepcopy(first)
        second.update(start="2026-08-14T00:00:00Z", end="2026-08-15T00:00:00Z",
                      gross_hours=24, effective_hours=24)
        config["capacity_calendars"][0]["intervals"].append(second)
        with self.assertRaisesRegex(ConfigError, "must not overlap"):
            cross_validate(config)
        with self.assertRaisesRegex(CalendarSemanticsError, "overlapping intervals"):
            run_truth(config, "world_sp", seed=504)

    def test_dependency_release_has_hand_calculated_order(self):
        config = self.one_item_fixed()
        self.add_dependent_template(config)
        result = run_truth(config, "world_sp", seed=505)
        items = {item.template_id: item for item in result.items}
        self.assertGreater(items["standard_feature"].terminal_time, 0)
        self.assertGreater(items["dependent_feature"].terminal_time,
                           items["standard_feature"].terminal_time)
        dependent_services = [row for row in result.services if row.item_id == "item_0002"]
        self.assertAlmostEqual(dependent_services[0].service_start,
                               items["standard_feature"].terminal_time, places=12)
        self.assertTrue(any(row.item_id == "item_0002" and row.event == "dependency_wait"
                            for row in result.events))
        self.assertTrue(any(row.item_id == "item_0002" and row.event == "dependency_release"
                            for row in result.events))

    def test_unpermitted_dependency_cycle_is_a_hard_error(self):
        config = self.one_item_fixed()
        self.add_dependent_template(config, cyclic=True)
        with self.assertRaisesRegex(DependencySemanticsError, "cycle is not allowed"):
            run_truth(config, "world_sp", seed=506)

    def test_cycle_test_override_is_rejected_even_before_cycle_execution(self):
        config = self.one_item_fixed()
        self.add_dependent_template(config, cyclic=True)
        config["dependency_models"][0]["cycles_allowed_for_test"] = True
        with self.assertRaisesRegex(DependencySemanticsError, "must set cycles_allowed_for_test=false"):
            run_truth(config, "world_sp", seed=507)

    def test_failed_predecessor_blocks_successor_without_false_deadlock(self):
        config = self.one_item_fixed()
        self.add_dependent_template(config)
        config["rework_models"][0]["maximum_loops"] = 0
        for world in config["data_generating_worlds"]:
            world["truth_parameters"].update(gate_fail_probability=1, gate_conditional_probability=0)
        result = run_truth(config, "world_sp", seed=508)
        items = {item.template_id: item for item in result.items}
        self.assertEqual(items["standard_feature"].terminal_state, "failed")
        self.assertEqual(items["dependent_feature"].terminal_state, "dependency_failed")
        self.assertEqual(items["dependent_feature"].terminal_time,
                         items["standard_feature"].terminal_time)
        self.assertEqual(result.metadata["deadlocked_items"], 0)

    def test_calendar_dependency_trace_is_seed_deterministic(self):
        config = self.one_item_fixed()
        self.add_dependent_template(config)
        config["capacity_calendars"][0]["blackout_periods"] = [{
            "start": "2026-08-13T00:15:00Z",
            "end": "2026-08-13T00:45:00Z",
        }]
        first = run_truth(copy.deepcopy(config), "world_sp", seed=509)
        second = run_truth(copy.deepcopy(config), "world_sp", seed=509)
        self.assertEqual(first.digest(), second.digest())

    def test_runtime_rejects_excluded_declarations_even_without_validator(self):
        mutations = {
            "non-FIFO": lambda c: c["role_pools"][0].update(queue_discipline="risk_priority"),
            "preemption": lambda c: c["role_pools"][0].update(preemption_policy="resume"),
            "backlog": lambda c: c["role_pools"][0].update(initial_backlog=1),
            "setup": lambda c: c["role_pools"][0].update(setup_penalty_distribution_id="implementation_time"),
            "parallel": lambda c: c["lifecycle_stages"][0].update(parallelization_policy="parallel"),
            "non-fixed": lambda c: c["arrival_models"][0].update(type="renewal"),
            "initial WIP": lambda c: c["arrival_models"][0]["initial_wip"].append({"id": "work"}),
            "mixture": lambda c: c["demand_models"][0]["base_distribution"].update(family="mixture"),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                config = self.one_item_fixed()
                mutate(config)
                with self.assertRaises((ValueError, CalendarSemanticsError, DependencySemanticsError)):
                    run_truth(config, "world_sp", seed=510)

    def test_blackout_outside_open_window_is_rejected(self):
        config = self.one_item_fixed()
        config["capacity_calendars"][0]["blackout_periods"] = [{
            "start": "2026-08-20T00:00:00Z",
            "end": "2026-08-20T01:00:00Z",
        }]
        with self.assertRaisesRegex(CalendarSemanticsError, "contained in one availability window"):
            run_truth(config, "world_sp", seed=511)

    def test_simultaneous_arrivals_use_fifo_item_id_tie_break(self):
        config = self.one_item_fixed()
        config["arrival_models"][0]["parameters"].update(
            count=3, spacing=0, template_ids=["standard_feature"] * 3,
        )
        config["capacity_calendars"][0]["blackout_periods"] = []
        for role in config["role_pools"]:
            role["concurrent_servers"] = 1
        result = run_truth(config, "world_sp", seed=512)
        context = [row.item_id for row in result.services
                   if row.stage_id == "context_preparation" and row.kind == "service"]
        self.assertEqual(context, ["item_0001", "item_0002", "item_0003"])

    def test_queue_area_and_resource_busy_integrals_reconcile(self):
        config = self.one_item_fixed()
        config["arrival_models"][0]["parameters"].update(
            count=4, spacing=0, template_ids=["standard_feature"] * 4,
        )
        config["capacity_calendars"][0]["blackout_periods"] = []
        for role in config["role_pools"]:
            role["concurrent_servers"] = 1
        result = run_truth(config, "world_sp", seed=513)
        for role in {row.role_pool_id for row in result.services}:
            role_services = [row for row in result.services if row.role_pool_id == role]
            item_wait_area = sum(row.service_start - row.queue_enter for row in role_services)
            changes = []
            for event in result.events:
                if event.role_pool_id != role:
                    continue
                if event.event == "queue_enter":
                    changes.append((event.time, event.sequence, 1))
                elif event.event == "service_start":
                    changes.append((event.time, event.sequence, -1))
            queue_length = 0
            prior = changes[0][0]
            queue_area = 0.0
            for at, _, delta in sorted(changes):
                queue_area += queue_length * (at - prior)
                queue_length += delta
                prior = at
            self.assertAlmostEqual(queue_area, item_wait_area, places=12)
            elapsed_busy = sum(row.service_end - row.service_start for row in role_services)
            touch = sum(row.demand for row in role_services)
            pause = sum(row.calendar_pause for row in role_services)
            self.assertAlmostEqual(elapsed_busy, touch + pause, places=12)

    def test_queue_area_explicitly_accounts_for_horizon_censored_queue(self):
        config = self.one_item_fixed()
        config["arrival_models"][0]["parameters"].update(
            count=4, spacing=0, template_ids=["standard_feature"] * 4,
        )
        config["time_model"]["horizon"] = 0.5
        config["capacity_calendars"][0]["blackout_periods"] = []
        for role in config["role_pools"]:
            role["concurrent_servers"] = 1
        result = run_truth(config, "world_sp", seed=514)
        context_entries = [event for event in result.events
                           if event.stage_id == "context_preparation" and event.event == "queue_enter"]
        context_starts = [event for event in result.events
                          if event.stage_id == "context_preparation" and event.event == "service_start"]
        self.assertEqual(len(context_entries), 4)
        # No one can finish the one-hour touch demand before the 0.5-hour
        # horizon, so all four remain explicitly represented in queue area.
        self.assertEqual(len(context_starts), 0)
        self.assertTrue(all(item.terminal_state == "censored" for item in result.items))
        self.assertTrue(check_queue_area_reconciliation(
            [event.__dict__ for event in result.events], horizon=0.5
        ).passed)


if __name__ == "__main__":
    unittest.main()
