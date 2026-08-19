import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from simulation.g4b_ablation import (
    DEVELOPMENT_STATUS,
    MECHANISMS,
    ablate_configuration,
    evaluate_ablations,
    generate_ablation_pairs,
    publish_ablation,
)


class Gate4BAblationTests(unittest.TestCase):
    def observations(self):
        return [
            {"world_id": "world_sp", "configuration_id": "base", "mechanism_id": "role_queues",
             "mechanism_state": state, "primary_metric": primary, "bottleneck_accuracy": accuracy}
            for state, primary, accuracy in (("baseline", 0.10, 0.80), ("ablated", 0.14, 0.60))
        ]

    def test_paired_development_ablation_and_contract(self):
        effects = evaluate_ablations(self.observations(), development_world_ids=["world_sp"],
                                     locked_world_ids=["world_mixed"])
        self.assertAlmostEqual(effects[0]["primary_delta"], 0.04)
        self.assertAlmostEqual(effects[0]["bottleneck_delta"], 0.20)
        self.assertEqual(effects[0]["status"], DEVELOPMENT_STATUS)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "g4b"
            receipt = publish_ablation(output, effects, development_world_ids=["world_sp"])
            self.assertEqual(receipt["status"], "verified_developmental")
            self.assertEqual({p.name for p in output.iterdir()},
                             {"ablation_manifest.json", "ablation_effects.csv", "ablation_pairs.csv",
                              "ablation_receipt.json"})
            with self.assertRaises(ValueError): publish_ablation(output, effects, development_world_ids=["world_sp"])

    def test_locked_world_is_a_hard_rejection(self):
        rows = self.observations(); rows[0]["world_id"] = "world_mixed"
        with self.assertRaisesRegex(ValueError, "locked"):
            evaluate_ablations(rows, development_world_ids=["world_sp"], locked_world_ids=["world_mixed"])

    def test_unpaired_ablation_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "paired"):
            evaluate_ablations(self.observations()[:1], development_world_ids=["world_sp"],
                               locked_world_ids=["world_mixed"])

    def executable_config(self):
        return {
            "experimental_design": {"development_world_ids": ["world_sp"],
                                    "locked_evaluation_world_ids": ["world_mixed"]},
            "randomization": {"master_seed": 1234},
            "arrival_models": [{"parameters": {"count": 2}}],
            "role_pools": [
                {"id": "product", "concurrent_servers": 1, "stage_eligibility": ["context"]},
                {"id": "developer", "concurrent_servers": 2, "stage_eligibility": ["build"]},
                {"id": "reviewer", "concurrent_servers": 1, "stage_eligibility": ["review"]},
            ],
            "lifecycle_stages": [
                {"id": "context", "eligible_role_pool_ids": ["product"]},
                {"id": "build", "eligible_role_pool_ids": ["developer"]},
                {"id": "review", "eligible_role_pool_ids": ["reviewer"]},
            ],
            "gate_definitions": [{"id": "quality", "accountable_role_pool_id": "reviewer",
                                  "required_evidence_ids": ["tests"]}],
            "dependency_models": [{"id": "deps", "edges": [["base", "dependent"]]}],
            "work_item_templates": [{"id": "base", "dependency_ids": []},
                                    {"id": "dependent", "dependency_ids": ["deps"]}],
            "demand_models": [
                {"id": "context_demand", "role_pool_id": "product"},
                {"id": "build_demand", "role_pool_id": "developer"},
                {"id": "review_demand", "role_pool_id": "reviewer"},
            ],
        }

    def test_each_mutator_changes_only_its_declared_mechanism(self):
        config = self.executable_config()
        for mechanism in MECHANISMS:
            mutated, audit = ablate_configuration(config, mechanism)
            self.assertEqual(audit.mechanism_id, mechanism)
            self.assertTrue(audit.changed_paths)
            # The caller-owned baseline must never be mutated.
            self.assertEqual(config["role_pools"][0]["concurrent_servers"], 1)
            if mechanism == "queues":
                self.assertTrue(all("concurrent_servers" in path for path in audit.changed_paths))
            elif mechanism == "readiness":
                self.assertTrue(all("required_evidence_ids" in path for path in audit.changed_paths))
            elif mechanism == "dependencies":
                self.assertTrue(all("dependency" in path for path in audit.changed_paths))
            else:
                self.assertEqual(len(mutated["role_pools"]), 1)

    def test_generator_runs_same_seed_pairs_in_development_namespace(self):
        calls = []

        def fake_runner(config, world, seed):
            calls.append((config, world, seed))
            completed = len(config["role_pools"]) > 1
            return SimpleNamespace(
                items=(SimpleNamespace(terminal_state="completed" if completed else "failed"),),
                services=(SimpleNamespace(role_pool_id=config["role_pools"][0]["id"], demand=1.0),),
            )

        rows = generate_ablation_pairs(self.executable_config(), world_id="world_sp",
                                       replications=2, runner=fake_runner)
        self.assertEqual(len(rows), len(MECHANISMS) * 2 * 2)
        self.assertTrue(all(row["seed_namespace"] == "development:g4b_ablation" for row in rows))
        self.assertTrue(all(row["configuration_id"] == "g4b_development:world_sp" for row in rows))
        for mechanism in MECHANISMS:
            selected = [row for row in rows if row["mechanism_id"] == mechanism]
            for replication in range(2):
                pair = [row for row in selected if row["replication_id"] == replication]
                self.assertEqual({row["mechanism_state"] for row in pair}, {"baseline", "ablated"})
        # Adjacent calls are baseline/ablated and use common random numbers.
        self.assertTrue(all(calls[index][2] == calls[index + 1][2]
                            for index in range(0, len(calls), 2)))
        effects = evaluate_ablations(rows, development_world_ids=["world_sp"],
                                     locked_world_ids=["world_mixed"])
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "executable"
            publish_ablation(output, effects, development_world_ids=["world_sp"], pairs=rows)
            self.assertGreater((output / "ablation_pairs.csv").stat().st_size, 100)
            import json
            manifest = json.loads((output / "ablation_manifest.json").read_text())
            self.assertEqual(manifest["manifest_version"], "0.2.0-development")
            self.assertEqual(manifest["pair_count"], len(rows))

    def test_generator_refuses_locked_world_and_nondevelopment_namespace_before_run(self):
        called = False

        def runner(config, world, seed):
            nonlocal called; called = True
            raise AssertionError("must not run")

        config = self.executable_config()
        with self.assertRaisesRegex(ValueError, "development worlds"):
            generate_ablation_pairs(config, world_id="world_mixed", replications=2, runner=runner)
        with self.assertRaisesRegex(ValueError, "development-only"):
            generate_ablation_pairs(config, world_id="world_sp", replications=2, runner=runner,
                                    seed_namespace="locked_evaluation")
        self.assertFalse(called)


if __name__ == "__main__": unittest.main()
