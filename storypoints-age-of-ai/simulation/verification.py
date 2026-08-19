"""Hard-stop checks applied before any synthetic result is interpreted."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from math import isclose, isfinite
from typing import Any, Iterable, Mapping, Sequence

from .seeds import SeedManifest


class HardStopError(RuntimeError):
    """Raised when a preregistered verification invariant fails."""


@dataclass(frozen=True)
class VerificationResult:
    check_id: str
    passed: bool
    detail: str


def stable_output_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()
    return sha256(encoded).hexdigest()


def _result(check_id: str, passed: bool, detail: str) -> VerificationResult:
    if not passed:
        raise HardStopError(f"{check_id}: {detail}")
    return VerificationResult(check_id, True, detail)


def check_seed_manifest(manifest: SeedManifest) -> VerificationResult:
    disjoint = not set(manifest.development_seeds) & set(manifest.locked_evaluation_seeds)
    unique = (
        len(set(manifest.development_seeds)) == len(manifest.development_seeds)
        and len(set(manifest.locked_evaluation_seeds)) == len(manifest.locked_evaluation_seeds)
    )
    return _result(
        "seed_manifest",
        manifest.verify() and disjoint and unique,
        "checksum invalid, duplicate seed, or development/evaluation overlap",
    )


def check_entity_reconciliation(counts: Mapping[str, int]) -> VerificationResult:
    required = {"created", "completed", "terminal_failed", "in_system"}
    if set(counts) != required or any(int(v) < 0 for v in counts.values()):
        raise HardStopError("entity_reconciliation: invalid count fields")
    passed = counts["created"] == counts["completed"] + counts["terminal_failed"] + counts["in_system"]
    return _result("entity_reconciliation", passed, "entities were lost or duplicated")


def check_time_accounting(records: Iterable[Mapping[str, float]], tolerance: float = 1e-9) -> VerificationResult:
    for index, row in enumerate(records):
        elapsed = float(row["elapsed"])
        components = sum(float(row[key]) for key in ("waiting", "service", "gate", "rework"))
        if not all(isfinite(v) and v >= 0 for v in (elapsed, components)):
            raise HardStopError(f"time_accounting: non-finite/negative time at record {index}")
        if not isclose(elapsed, components, rel_tol=0.0, abs_tol=tolerance):
            raise HardStopError(f"time_accounting: unexplained time at record {index}")
    return VerificationResult("time_accounting", True, "all elapsed time reconciled")


def check_probability_outputs(forecasts: Mapping[str, Sequence[float]]) -> VerificationResult:
    for model, values in forecasts.items():
        if not values:
            raise HardStopError(f"probability_outputs: {model} has no forecasts")
        if any(not isfinite(float(value)) or not 0 <= float(value) <= 1 for value in values):
            raise HardStopError(f"probability_outputs: {model} emitted invalid probability")
    return VerificationResult("probability_outputs", True, "all probabilities are finite and bounded")


def check_fixed_seed_reproducibility(first: Any, second: Any) -> VerificationResult:
    return _result(
        "fixed_seed_reproducibility",
        stable_output_hash(first) == stable_output_hash(second),
        "identical fixed-seed runs produced different output hashes",
    )


def check_deterministic_toy_cases(cases: Sequence[Mapping[str, float]], tolerance: float = 1e-9) -> VerificationResult:
    """Each case supplies ``observed`` and hand-calculated ``expected``."""
    if not cases:
        raise HardStopError("deterministic_toy_cases: no cases supplied")
    for index, case in enumerate(cases):
        if not isclose(float(case["observed"]), float(case["expected"]), rel_tol=0.0, abs_tol=tolerance):
            raise HardStopError(f"deterministic_toy_cases: mismatch at case {index}")
    return VerificationResult("deterministic_toy_cases", True, "all hand calculations matched")


def check_mandatory_failure(trace: Sequence[Mapping[str, Any]]) -> VerificationResult:
    """A failed mandatory gate must not be followed by an undeclared advance."""
    for index, event in enumerate(trace):
        if event.get("mandatory") and event.get("gate_state") == "Fail":
            # Inspect the next transition for this item.  A declared rework or
            # terminal failure is valid; an immediate advance is not.  Later
            # advancement after successful rework must remain possible.
            next_transition = next(
                (
                    e.get("transition")
                    for e in trace[index + 1 :]
                    if e.get("item_id") == event.get("item_id") and e.get("transition")
                ),
                None,
            )
            if next_transition not in {"rework", "terminal_failure"}:
                raise HardStopError("mandatory_failure: failed gate lacked declared rework/terminal transition")
    return VerificationResult("mandatory_failure", True, "mandatory failures did not silently advance")


def check_queue_area_reconciliation(events: Sequence[Mapping[str, Any]], *, horizon: float,
                                    tolerance: float = 1e-9) -> VerificationResult:
    """Reconcile queue-length area including items still queued at horizon."""
    if not isfinite(float(horizon)) or horizon < 0:
        raise HardStopError("queue_area: horizon must be finite and nonnegative")
    roles = {str(row.get("role_pool_id", "")) for row in events
             if row.get("event") in {"queue_enter", "service_start"}}
    for role in roles:
        role_events = [row for row in events if str(row.get("role_pool_id", "")) == role
                       and row.get("event") in {"queue_enter", "service_start"}]
        changes: list[tuple[float, int, int]] = []
        entered: dict[tuple[str, str, str], list[float]] = {}
        item_wait = 0.0
        for sequence, row in enumerate(role_events):
            at = float(row["time"]); order = int(row.get("sequence", sequence))
            if not isfinite(at) or at < 0 or at > horizon:
                raise HardStopError("queue_area: event outside horizon")
            key = (str(row.get("item_id", "")), str(row.get("stage_id", "")),
                   str(row.get("detail", "")))
            if row["event"] == "queue_enter":
                entered.setdefault(key, []).append(at); changes.append((at, order, 1))
            else:
                if key not in entered or not entered[key]:
                    raise HardStopError("queue_area: service start has no matching queue entry")
                start = entered[key].pop(0)
                if at < start:
                    raise HardStopError("queue_area: service starts before queue entry")
                item_wait += at - start; changes.append((at, order, -1))
        item_wait += sum(horizon - at for values in entered.values() for at in values)
        queue_length = 0; area = 0.0; prior = 0.0
        for at, _, delta in sorted(changes):
            area += queue_length * (at - prior); queue_length += delta; prior = at
            if queue_length < 0:
                raise HardStopError("queue_area: negative queue length")
        area += queue_length * (horizon - prior)
        if not isclose(area, item_wait, rel_tol=0.0, abs_tol=tolerance):
            raise HardStopError(f"queue_area: role {role} integral does not reconcile")
    return VerificationResult("queue_area", True, "queue area includes served and horizon-censored waits")


def run_hard_stop_checks(
    *,
    manifest: SeedManifest,
    counts: Mapping[str, int],
    time_records: Iterable[Mapping[str, float]],
    forecasts: Mapping[str, Sequence[float]],
    reproducibility_pair: tuple[Any, Any],
    toy_cases: Sequence[Mapping[str, float]],
    gate_trace: Sequence[Mapping[str, Any]],
) -> list[VerificationResult]:
    """Run all engine-independent hard stops; any failure aborts evaluation."""
    return [
        check_seed_manifest(manifest),
        check_entity_reconciliation(counts),
        check_time_accounting(time_records),
        check_probability_outputs(forecasts),
        check_fixed_seed_reproducibility(*reproducibility_pair),
        check_deterministic_toy_cases(toy_cases),
        check_mandatory_failure(gate_trace),
    ]
