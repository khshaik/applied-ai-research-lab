"""Seeded discrete-event truth generator with explicit role queues and gates."""
from __future__ import annotations

import hashlib
import heapq
import json
import math
import random
from dataclasses import asdict, dataclass
from types import MappingProxyType
from typing import Any, Mapping

from .scheduling import (
    CalendarSemanticsError,
    DependencySemanticsError,
    compile_capacity_calendars,
    compile_template_dependencies,
)


class GateSemanticsError(ValueError):
    """Raised when a gate cannot be executed without inventing semantics."""


@dataclass(frozen=True)
class EventRow:
    sequence: int; time: float; item_id: str; event: str; stage_id: str; role_pool_id: str; detail: str = ""

@dataclass(frozen=True)
class ServiceRow:
    item_id: str; stage_id: str; role_pool_id: str; queue_enter: float; service_start: float; service_end: float; demand: float; calendar_pause: float; kind: str

@dataclass(frozen=True)
class GateRow:
    item_id: str; gate_id: str; time: float; decision: str; loop: int; residual_risk_id: str | None = None; rationale: str | None = None

@dataclass(frozen=True)
class ItemRow:
    item_id: str; template_id: str; arrival: float; terminal_time: float | None; terminal_state: str; rework_loops: int; residual_risk_id: str | None = None

@dataclass(frozen=True)
class SimulationResult:
    run_id: str
    events: tuple[EventRow, ...]
    services: tuple[ServiceRow, ...]
    gates: tuple[GateRow, ...]
    items: tuple[ItemRow, ...]
    metadata: Mapping[str, Any]

    def as_tables(self) -> dict[str, list[dict[str, Any]]]:
        """Return fresh plain records for comparator and persistence adapters."""
        return {"event_log": [asdict(x) for x in self.events],
                "role_stage_service": [asdict(x) for x in self.services],
                "gate_decisions": [asdict(x) for x in self.gates],
                "item_outcomes": [asdict(x) for x in self.items]}

    def digest(self) -> str:
        payload = {"events": [asdict(x) for x in self.events], "services": [asdict(x) for x in self.services],
                   "gates": [asdict(x) for x in self.gates], "items": [asdict(x) for x in self.items]}
        return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _sample(dist: dict[str, Any], rng: random.Random) -> float:
    p, family = dist["parameters"], dist["family"]
    if family == "fixed": value = float(p["value"])
    elif family == "triangular": value = rng.triangular(float(p["low"]), float(p["high"]), float(p["mode"]))
    elif family == "lognormal": value = rng.lognormvariate(float(p["mu"]), float(p["sigma"]))
    elif family == "gamma": value = rng.gammavariate(float(p["shape"]), float(p["scale"]))
    elif family == "weibull": value = rng.weibullvariate(float(p["scale"]), float(p["shape"]))
    elif family == "empirical_discrete": value = rng.choices(p["values"], weights=p.get("weights"), k=1)[0]
    else: raise ValueError(f"unsupported production-scope distribution: {family}")
    if "truncation" in dist: value = max(dist["truncation"][0], min(value, dist["truncation"][1]))
    return float(value)


def _gate_applies(gate: Mapping[str, Any], template: Mapping[str, Any]) -> bool:
    """Return applicability without allowing a template to bypass a mandatory gate.

    A gate is risk-applicable only for a listed risk class.  Within that scope,
    mandatory gates always apply; optional gates apply when explicitly listed by
    the work-item template.  A template that requires a gate outside the gate's
    risk scope is contradictory and therefore rejected.
    """
    risk_class = template["risk_class"]
    listed = gate["id"] in template.get("required_gate_ids", [])
    risk_applicable = risk_class in gate["risk_classes"]
    if listed and not risk_applicable:
        raise GateSemanticsError(
            f"template {template['id']} requires gate {gate['id']} outside its risk scope"
        )
    return risk_applicable and (bool(gate.get("mandatory", False)) or listed)


def _evidence_contract(
    config: Mapping[str, Any], template: Mapping[str, Any]
) -> tuple[dict[str, bool], dict[str, frozenset[str]], dict[str, str], bool]:
    """Compile the deliberately small executable evidence/readiness contract.

    The prototype has no generic rule language.  It therefore implements only
    same-run freshness, explicit t0 presence states, and invalidation caused by
    a declared rework/stage-change event.  Anything else is rejected rather
    than being accepted as configuration that the engine silently ignores.
    """
    definitions = {record["id"]: record for record in config["evidence_definitions"]}
    required = {
        evidence_id
        for gate in config["gate_definitions"]
        if _gate_applies(gate, template)
        for evidence_id in gate["required_evidence_ids"]
    }
    if not required:
        return {}, {}, {}, False

    models = config.get("readiness_models", [])
    if len(models) != 1:
        raise GateSemanticsError(
            "prototype requires exactly one readiness model when applicable gates require evidence"
        )
    model = models[0]
    runtime = model["runtime_state_model"]
    unsupported_runtime = set(runtime) - {"invalidate_on_rework"}
    if unsupported_runtime:
        raise GateSemanticsError(
            f"unsupported readiness runtime declarations: {sorted(unsupported_runtime)}"
        )
    invalidate_on_rework = runtime.get("invalidate_on_rework")
    if not isinstance(invalidate_on_rework, bool):
        raise GateSemanticsError("readiness invalidate_on_rework must be explicitly boolean")

    t0 = model["t0_state"]
    unknown_t0 = set(t0) - set(definitions)
    if unknown_t0:
        raise GateSemanticsError(f"readiness model declares unknown evidence: {sorted(unknown_t0)}")
    missing_t0 = required - set(t0)
    if missing_t0:
        raise GateSemanticsError(f"readiness model omits required evidence: {sorted(missing_t0)}")

    truthy = {"present", "current", "valid"}
    falsy = {"missing", "absent", "stale", "invalid"}
    initial: dict[str, bool] = {}
    invalidating: dict[str, frozenset[str]] = {}
    producers: dict[str, str] = {}
    stage_ids = {stage["id"] for stage in config["lifecycle_stages"]}
    supported_events = {"rework"} | {
        f"{stage['id']}_change" for stage in config["lifecycle_stages"]
    }
    for evidence_id in required:
        definition = definitions[evidence_id]
        producer_stage = definition.get("producer_stage_id")
        producer_event = definition.get("producer_event")
        if producer_stage not in stage_ids or producer_event != "service_complete":
            raise GateSemanticsError(
                f"evidence {evidence_id} must declare a known producer_stage_id "
                "and producer_event='service_complete'"
            )
        producers[evidence_id] = str(producer_stage)
        freshness = definition["freshness_rule"]
        if freshness != "same_run":
            raise GateSemanticsError(
                f"unsupported freshness rule {freshness!r} for evidence {evidence_id}"
            )
        state_name = t0[evidence_id]
        if state_name in truthy:
            initial[evidence_id] = True
        elif state_name in falsy:
            initial[evidence_id] = False
        else:
            raise GateSemanticsError(
                f"unsupported t0 evidence state {state_name!r} for {evidence_id}"
            )
        events = frozenset(definition["invalidating_events"])
        unsupported_events = events - supported_events
        if unsupported_events:
            raise GateSemanticsError(
                f"unsupported invalidating events for {evidence_id}: {sorted(unsupported_events)}"
            )
        if events and not invalidate_on_rework:
            raise GateSemanticsError(
                f"evidence {evidence_id} declares invalidation but readiness model disables it"
            )
        invalidating[evidence_id] = events
    return initial, invalidating, producers, invalidate_on_rework


def _validate_gate_semantics(
    config: Mapping[str, Any], template: Mapping[str, Any], truth: Mapping[str, Any]
) -> None:
    """Reject ambiguous gate configurations before the event loop starts."""
    stages = config["lifecycle_stages"]
    stage_ids = {stage["id"] for stage in stages}
    gates = config["gate_definitions"]
    gate_ids = {gate["id"] for gate in gates}
    if len(gate_ids) != len(gates):
        raise GateSemanticsError("gate identifiers must be unique")
    if len({gate["stage_id"] for gate in gates}) != len(gates):
        raise GateSemanticsError("prototype supports at most one gate per stage")
    unknown_required = set(template.get("required_gate_ids", [])) - gate_ids
    if unknown_required:
        raise GateSemanticsError(f"template requires unknown gates: {sorted(unknown_required)}")

    fail_p = float(truth.get("gate_fail_probability", 0.0))
    conditional_p = float(truth.get("gate_conditional_probability", 0.0))
    if fail_p < 0 or conditional_p < 0 or fail_p + conditional_p > 1:
        raise GateSemanticsError("gate decision probabilities must be nonnegative and sum to at most one")

    supported_targets = {"next", "advance", "terminal", "terminal_with_risk", "terminal_failure", "rework"}
    for gate in gates:
        if gate.get("expiry_rule") != "none_in_prototype":
            raise GateSemanticsError(
                f"unsupported expiry rule {gate.get('expiry_rule')!r} for gate {gate['id']}"
            )
        allowed = gate["allowed_states"]
        if not allowed or len(set(allowed)) != len(allowed):
            raise GateSemanticsError(f"gate {gate['id']} must declare unique allowed states")
        transitions = gate["transitions"]
        missing = set(allowed) - set(transitions)
        if missing:
            raise GateSemanticsError(f"gate {gate['id']} lacks transitions for {sorted(missing)}")
        for decision in allowed:
            target = transitions[decision]
            if not isinstance(target, str) or (target not in supported_targets and target not in stage_ids):
                raise GateSemanticsError(
                    f"gate {gate['id']} has unsupported {decision} transition {target!r}"
                )
        conditional_allowed = gate["conditional_policy"].get("allowed", False) is True
        if "Conditional" in allowed and not conditional_allowed:
            raise GateSemanticsError(
                f"gate {gate['id']} allows Conditional but conditional_policy.allowed is not true"
            )
        if conditional_p > 0 and _gate_applies(gate, template) and "Conditional" not in allowed:
            raise GateSemanticsError(
                f"world can emit Conditional but gate {gate['id']} does not allow it"
            )
        if fail_p > 0 and _gate_applies(gate, template) and "Fail" not in allowed:
            raise GateSemanticsError(f"world can emit Fail but gate {gate['id']} does not allow it")
        if (1.0 - fail_p - conditional_p) > 0 and _gate_applies(gate, template) and "Pass" not in allowed:
            raise GateSemanticsError(f"world can emit Pass but gate {gate['id']} does not allow it")
        if not _gate_applies(gate, template):
            if "NotApplicable" not in allowed:
                raise GateSemanticsError(
                    f"gate {gate['id']} is not applicable but does not explicitly allow NotApplicable"
                )


def run_truth(config: dict[str, Any], world_id: str, seed: int | None = None) -> SimulationResult:
    """Generate realized delivery outcomes; no comparator sees runtime events."""
    if config["time_model"]["unit"] != "hours":
        raise CalendarSemanticsError("minimum production scope requires time_model.unit='hours'")
    for role in config["role_pools"]:
        if role["queue_discipline"] != "FIFO":
            raise GateSemanticsError("minimum production scope supports only FIFO queues")
        if role.get("preemption_policy", "none") != "none":
            raise GateSemanticsError("minimum production scope does not support preemption")
        if int(role["initial_backlog"]) != 0:
            raise GateSemanticsError("minimum production scope requires zero initial_backlog")
        if role.get("setup_penalty_distribution_id") is not None:
            raise GateSemanticsError("minimum production scope does not support setup penalties")
    for stage_index, stage in enumerate(config["lifecycle_stages"]):
        if stage["parallelization_policy"] != "single_role":
            raise GateSemanticsError("minimum production scope supports single_role stages only")
        expected_prerequisites = [] if stage_index == 0 else [config["lifecycle_stages"][stage_index - 1]["id"]]
        if stage["entry_prerequisite_ids"] != expected_prerequisites:
            raise GateSemanticsError("minimum production scope requires sequential stage prerequisites")
        expected_release = "none" if stage_index == 0 else "after_predecessor"
        if stage.get("dependency_release_rule", expected_release) != expected_release:
            raise GateSemanticsError("minimum production scope requires sequential stage release rules")
    if any(d["base_distribution"]["family"] == "mixture" for d in config["demand_models"]):
        raise GateSemanticsError("minimum production scope does not support mixture distributions")
    seed = config["randomization"]["master_seed"] if seed is None else seed
    rng = random.Random(seed)
    stages = config["lifecycle_stages"]
    stage_ix = {s["id"]: i for i, s in enumerate(stages)}
    demands = {(d["work_item_selector"], d["stage_id"], d["role_pool_id"]): d
               for d in config["demand_models"]}
    gates = {g["stage_id"]: g for g in config["gate_definitions"]}
    gate_dists = {d["base_distribution"]["id"]: d["base_distribution"] for d in config["demand_models"]}
    reworks = {(r["from_gate_id"], r["decision"]): r for r in config["rework_models"]}
    worlds = {w["id"]: w for w in config["data_generating_worlds"]}
    truth = worlds[world_id]["truth_parameters"]
    templates = {template["id"]: template for template in config["work_item_templates"]}
    for template in templates.values():
        _validate_gate_semantics(config, template, truth)
    evidence_contracts = {
        template_id: _evidence_contract(config, template)
        for template_id, template in templates.items()
    }
    horizon = float(config["time_model"]["horizon"])
    calendars = compile_capacity_calendars(config["capacity_calendars"], config["time_model"]["unit"])
    role_calendars = {role["id"]: calendars[role["capacity_calendar_id"]]
                      for role in config["role_pools"]}
    # The role pool declares service slots per calendar instance; calendar
    # concurrency declares how many identical instances are available.
    servers = {role["id"]: int(role["concurrent_servers"]) * role_calendars[role["id"]].concurrency
               for role in config["role_pools"]}
    busy = {r: 0 for r in servers}
    queues: dict[str, list[tuple[int, float, str, str, str, float | None]]] = {r: [] for r in servers}
    pq: list[tuple[float, int, str, dict[str, Any]]] = []; counter = 0
    event_rows: list[EventRow] = []; service_rows: list[ServiceRow] = []; gate_rows: list[GateRow] = []
    state: dict[str, dict[str, Any]] = {}

    def emit(at: float, kind: str, data: dict[str, Any]) -> None:
        nonlocal counter
        counter += 1; heapq.heappush(pq, (at, counter, kind, data))

    def log(at: float, item: str, event: str, stage: str = "", role: str = "", detail: str = "") -> None:
        event_rows.append(EventRow(len(event_rows) + 1, at, item, event, stage, role, detail))

    def enqueue(at: float, item: str, stage: str, role: str, kind: str) -> None:
        queues[role].append((len(queues[role]), at, item, stage, kind, None))
        # FIFO is by entry time. Exact-time ties use the immutable item ID,
        # followed by insertion sequence for multiple requests from one item.
        queues[role].sort(key=lambda row: (row[1], row[2], row[0]))
        log(at, item, "queue_enter", stage, role, kind)
        dispatch(at, role)

    def dispatch(at: float, role: str) -> None:
        while busy[role] < servers[role] and queues[role]:
            order, entered, item, stage, kind, sampled = queues[role][0]
            start = role_calendars[role].next_available(at)
            if start is None or start > horizon:
                break
            template_id = state[item]["template"]
            if kind == "service":
                key = (template_id, stage, role)
                if key not in demands:
                    raise GateSemanticsError(
                        f"no demand model for template {template_id}, stage {stage}, role {role}"
                    )
                dist = demands[key]["base_distribution"]
            else:
                gate = gates[stage]; dist = gate_dists[gate["evaluation_demand_distribution_id"]]
            demand = sampled if sampled is not None else _sample(dist, rng) * float(truth.get("service_multiplier", 1.0))
            queues[role][0] = (order, entered, item, stage, kind, demand)
            end = role_calendars[role].finish_time(start, demand)
            if end is None or end > horizon:
                log(at, item, "capacity_insufficient", stage, role, kind)
                break
            queues[role].pop(0)
            busy[role] += 1
            pause = max(0.0, (end - start) - demand)
            service_rows.append(ServiceRow(item, stage, role, entered, start, end, demand, pause, kind))
            if start > at:
                log(at, item, "capacity_wait", stage, role, f"until={start:.12g}")
            if end - start > demand + 1e-12:
                log(start, item, "capacity_pause_applied", stage, role, f"elapsed={end-start:.12g};touch={demand:.12g}")
            log(start, item, "service_start", stage, role, kind)
            emit(end, "complete", {"item": item, "stage": stage, "role": role, "kind": kind})

    arrival = config["arrival_models"][0]
    if arrival["type"] != "fixed_portfolio": raise ValueError("prototype supports fixed_portfolio arrivals")
    if arrival["initial_wip"]:
        raise DependencySemanticsError("minimum production scope does not support initial_wip")
    count = int(arrival["parameters"]["count"])
    template_sequence = arrival["parameters"].get("template_ids")
    if template_sequence is None:
        template_sequence = [next(iter(templates))] * count
    if not isinstance(template_sequence, list) or len(template_sequence) != count:
        raise DependencySemanticsError("fixed_portfolio template_ids must be a list with one entry per item")
    unknown_templates = set(template_sequence) - set(templates)
    if unknown_templates:
        raise DependencySemanticsError(f"fixed_portfolio references unknown templates: {sorted(unknown_templates)}")
    template_predecessors = compile_template_dependencies(
        templates.values(), config.get("dependency_models", [])
    )
    template_items: dict[str, list[str]] = {template_id: [] for template_id in templates}
    for i, template_id in enumerate(template_sequence):
        at = float(arrival["parameters"].get("start", 0)) + i * float(arrival["parameters"].get("spacing", 0))
        item = f"item_{i+1:04d}"
        initial_evidence = evidence_contracts[template_id][0]
        state[item] = {"template": template_id, "arrival": at, "arrived": False,
                       "stage": 0, "loops": 0, "terminal": None,
                       "status": "active", "evidence": dict(initial_evidence),
                       "dependency_wait": False, "residual_risk_id": None}
        template_items[template_id].append(item)
        emit(at, "arrival", {"item": item})

    def unresolved_predecessors(item: str) -> list[str]:
        predecessor_templates = template_predecessors[state[item]["template"]]
        return sorted(
            predecessor_item
            for predecessor_template in predecessor_templates
            for predecessor_item in template_items[predecessor_template]
            if state[predecessor_item]["status"] != "completed"
        )

    def release_or_wait(at: float, item: str) -> None:
        unresolved = unresolved_predecessors(item)
        if unresolved:
            state[item]["dependency_wait"] = True
            log(at, item, "dependency_wait", detail=",".join(unresolved))
            return
        state[item]["dependency_wait"] = False
        stage = stages[state[item]["stage"]]
        role = stage["eligible_role_pool_ids"][0]
        log(at, item, "dependency_release", stage["id"], role)
        enqueue(at, item, stage["id"], role, "service")

    def release_dependents(at: float) -> None:
        for candidate in sorted(state):
            candidate_state = state[candidate]
            if (candidate_state["arrived"] and candidate_state["terminal"] is None
                    and candidate_state["dependency_wait"]
                    and not unresolved_predecessors(candidate)):
                release_or_wait(at, candidate)

    while pq:
        at, _, kind, data = heapq.heappop(pq)
        if at > horizon: break
        item = data["item"]
        if kind == "arrival":
            state[item]["arrived"] = True
            stage = stages[0]
            role = stage["eligible_role_pool_ids"][0]
            log(at, item, "arrival", stage["id"], role)
            release_or_wait(at, item)
            continue
        role, stage_id = data["role"], data["stage"]; busy[role] -= 1; log(at, item, "service_complete", stage_id, role, data["kind"]); dispatch(at, role)
        template = templates[state[item]["template"]]
        if data["kind"] == "service":
            _, _, evidence_producers, _ = evidence_contracts[template["id"]]
            for evidence_id, producer_stage in sorted(evidence_producers.items()):
                if producer_stage != stage_id:
                    continue
                prior = state[item]["evidence"].get(evidence_id, False)
                state[item]["evidence"][evidence_id] = True
                log(at, item, "evidence_refreshed" if prior else "evidence_produced",
                    stage_id, role, evidence_id)
        if data["kind"] == "service" and stage_id in gates:
            gate = gates[stage_id]
            if _gate_applies(gate, template):
                enqueue(at, item, stage_id, gate["accountable_role_pool_id"], "gate")
                continue
            decision = "NotApplicable"
            rationale = "excluded_by_frozen_risk_and_template_applicability_rule"
            gate_rows.append(GateRow(item, gate["id"], at, decision,
                                     state[item]["loops"], rationale=rationale))
            log(at, item, "gate_not_applicable", stage_id, role,
                f"{gate['id']}:{rationale}")
            transition = gate["transitions"][decision]
        elif data["kind"] == "gate":
            template = templates[state[item]["template"]]
            initial_evidence, invalidating_events, evidence_producers, invalidate_on_rework = evidence_contracts[template["id"]]
            gate = gates[stage_id]; fail_p = float(truth.get("gate_fail_probability", 0)); cond_p = float(truth.get("gate_conditional_probability", 0))
            missing_evidence = [
                evidence_id for evidence_id in gate["required_evidence_ids"]
                if not state[item]["evidence"].get(evidence_id, False)
            ]
            if missing_evidence:
                if "Fail" not in gate["allowed_states"]:
                    raise GateSemanticsError(
                        f"gate {gate['id']} has unready evidence but does not allow Fail"
                    )
                decision = "Fail"
                log(at, item, "evidence_not_ready", stage_id, role, ",".join(sorted(missing_evidence)))
            else:
                u = rng.random(); decision = "Fail" if u < fail_p else "Conditional" if u < fail_p + cond_p else "Pass"
            if decision not in gate["allowed_states"]:
                raise GateSemanticsError(f"gate {gate['id']} emitted disallowed state {decision}")
            if decision == "Conditional" and gate["conditional_policy"].get("allowed", False) is not True:
                raise GateSemanticsError(f"gate {gate['id']} emitted Conditional contrary to policy")
            residual_risk_id = None
            if decision == "Conditional":
                residual_risk_id = f"risk-{item}-{gate['id']}-{state[item]['loops']}"
                state[item]["residual_risk_id"] = residual_risk_id
                log(at, item, "residual_risk_recorded", stage_id, role, residual_risk_id)
            transition = gate["transitions"].get(decision)
            if transition is None:
                raise GateSemanticsError(f"gate {gate['id']} has no declared transition for {decision}")
            model = reworks.get((gate["id"], decision)); loops = state[item]["loops"]
            if model and loops < model["maximum_loops"]:
                state[item]["loops"] += 1; route = rng.choices(model["routes"], weights=[x["probability"] for x in model["routes"]], k=1)[0]
                dest = route["destination_stage_id"]
                if transition not in {"rework", dest}:
                    raise GateSemanticsError(
                        f"gate {gate['id']} declares {transition!r} but rework route selected {dest!r}"
                    )
                gate_rows.append(GateRow(item, gate["id"], at, decision, state[item]["loops"], residual_risk_id)); state[item]["stage"] = stage_ix[dest]
                if invalidate_on_rework:
                    event_names = {"rework", f"{dest}_change"}
                    for evidence_id, triggers in invalidating_events.items():
                        if triggers & event_names and state[item]["evidence"].get(evidence_id, False):
                            state[item]["evidence"][evidence_id] = False
                            log(at, item, "evidence_invalidated", stage_id, role, evidence_id)
                log(at, item, "rework", stage_id, role, dest); enqueue(at, item, dest, stages[stage_ix[dest]]["eligible_role_pool_ids"][0], "service"); continue
            gate_rows.append(GateRow(item, gate["id"], at, decision, loops, residual_risk_id))
            if decision == "Fail" and gate.get("mandatory", False):
                # Exhausted rework and missing rework are both closed failures.
                # A mandatory failure can never reach the generic advance path.
                if model is None and transition != "terminal_failure":
                    raise GateSemanticsError(
                        f"mandatory gate {gate['id']} failed without rework or terminal_failure transition"
                    )
                state[item]["terminal"] = at; state[item]["status"] = "failed"; log(at, item, "terminal_failure", stage_id, role); continue
            if model and loops >= model["maximum_loops"]:
                terminal_rule = model.get("terminal_failure_rule", "")
                if terminal_rule:
                    state[item]["terminal"] = at; state[item]["status"] = "failed"; log(at, item, "terminal_failure", stage_id, role); continue
        else:
            transition = "next"

        # Interpret the declared transition.  No gate decision is permitted to
        # fall through to sequential advancement implicitly.
        if transition == "terminal_failure":
            state[item]["terminal"] = at; state[item]["status"] = "failed"; log(at, item, "terminal_failure", stage_id, role); continue
        if transition in {"terminal", "terminal_with_risk"}:
            if not stages[stage_ix[stage_id]]["terminal_eligible"]:
                raise GateSemanticsError(f"stage {stage_id} is not terminal eligible")
            has_residual_risk = transition == "terminal_with_risk" or state[item]["residual_risk_id"] is not None
            state[item]["terminal"] = at
            state[item]["status"] = "completed_with_residual_risk" if has_residual_risk else "completed"
            log(at, item, "completed", stage_id, role, transition)
            if not has_residual_risk:
                release_dependents(at)
            continue
        if transition == "rework":
            raise GateSemanticsError(f"gate {gate['id']} declared rework but no executable rework model remained")
        if transition in stage_ix:
            dest = transition; state[item]["stage"] = stage_ix[dest]
            log(at, item, "declared_transition", stage_id, role, dest)
            enqueue(at, item, dest, stages[stage_ix[dest]]["eligible_role_pool_ids"][0], "service"); continue
        if transition not in {"next", "advance"}:
            raise GateSemanticsError(f"unsupported runtime transition {transition!r}")
        next_ix = stage_ix[stage_id] + 1
        if next_ix >= len(stages):
            has_residual_risk = state[item]["residual_risk_id"] is not None
            state[item]["terminal"] = at
            state[item]["status"] = "completed_with_residual_risk" if has_residual_risk else "completed"
            log(at, item, "completed", stage_id, role,
                "terminal_with_risk" if has_residual_risk else "terminal")
            if not has_residual_risk:
                release_dependents(at)
        else:
            state[item]["stage"] = next_ix; nxt = stages[next_ix]; enqueue(at, item, nxt["id"], nxt["eligible_role_pool_ids"][0], "service")

    # Propagate failed dependency chains to an explicit timestamped terminal
    # state. Iterate so A -> B -> C propagates without depending on item order.
    changed = True
    while changed:
        changed = False
        for item, item_state in sorted(state.items()):
            if item_state["terminal"] is not None or not item_state["dependency_wait"]:
                continue
            unresolved = unresolved_predecessors(item)
            failed = [predecessor for predecessor in unresolved
                      if state[predecessor]["status"] in {"failed", "dependency_failed"}]
            if not failed:
                continue
            failure_time = max(float(state[predecessor]["terminal"]) for predecessor in failed
                               if state[predecessor]["terminal"] is not None)
            terminal_time = max(float(item_state["arrival"]), failure_time)
            item_state["terminal"] = terminal_time
            item_state["status"] = "dependency_failed"
            log(terminal_time, item, "dependency_failed", detail=",".join(failed))
            changed = True
    items = tuple(ItemRow(i, s["template"], s["arrival"], s["terminal"],
                          s["status"] if s["terminal"] is not None or s["status"] != "active" else "censored",
                          s["loops"], s["residual_risk_id"]) for i, s in sorted(state.items()))
    run_id = f"{world_id}-seed-{seed}"
    metadata = MappingProxyType({"world_id": world_id, "seed": seed, "horizon": horizon,
                                 "layer": "synthetic_truth", "deadlocked_items": 0})
    return SimulationResult(run_id, tuple(event_rows), tuple(service_rows), tuple(gate_rows), items, metadata)
