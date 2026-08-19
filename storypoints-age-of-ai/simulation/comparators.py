"""Transparent comparator forecasts for the locked Route B evaluation.

All non-oracle comparators consume only pre-commitment (t0) fields.  The
functions deliberately avoid fitting on the evaluation set: coefficients must
be frozen in :class:`ComparatorParameters` before locked seeds are opened.

Expected item mapping
---------------------
``story_points``: non-negative scalar
``story_point_budget``: historical point allowance for one interval
``hie_context_load``, ``hie_interaction_load``, ``hie_oversight_load``:
    non-negative, pre-task HIE-compatible demand fields
``role_demand`` and ``role_capacity``: mappings keyed by role; demand/capacity
    use the same unit and planning interval
``role_stage_demand`` and ``role_stage_capacity``: nested role/stage mappings
    derived from declared t0 demand models and executable calendars
``readiness_probability``: t0 probability that mandatory evidence is ready
``rework_probability``: t0 rework probability
``dependency_block_probability``: t0 probability mass exposed to an
    unreleased portfolio dependency
``true_completion_probability``: simulated truth, oracle only

These are deliberately simple decision models, not claims about empirical
functional form.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, isfinite
from typing import Any, Mapping


def _logistic(value: float) -> float:
    if value >= 0:
        z = exp(-value)
        return 1.0 / (1.0 + z)
    z = exp(value)
    return z / (1.0 + z)


def _number(item: Mapping[str, Any], key: str, *, minimum: float = 0.0) -> float:
    if key not in item:
        raise ValueError(f"missing required t0 field: {key}")
    value = float(item[key])
    if not isfinite(value) or value < minimum:
        raise ValueError(f"{key} must be finite and >= {minimum}")
    return value


def _probability(item: Mapping[str, Any], key: str) -> float:
    value = _number(item, key)
    if value > 1.0:
        raise ValueError(f"{key} must be in [0, 1]")
    return value


@dataclass(frozen=True)
class ComparatorParameters:
    """Coefficients frozen using development worlds only.

    Positive margin means spare capacity and therefore higher completion
    probability.  ``temperature`` prevents any comparator from returning
    unjustified hard classifications.
    """

    story_point_temperature: float = 0.25
    hie_temperature: float = 0.25
    role_load_temperature: float = 0.20
    proposed_temperature: float = 0.20
    hie_context_weight: float = 0.35
    hie_interaction_weight: float = 0.30
    hie_oversight_weight: float = 0.35
    proposed_readiness_weight: float = 0.75
    proposed_rework_weight: float = 0.75
    proposed_dependency_weight: float = 0.75

    def __post_init__(self) -> None:
        for name in (
            "story_point_temperature", "hie_temperature",
            "role_load_temperature", "proposed_temperature",
        ):
            if getattr(self, name) <= 0:
                raise ValueError(f"{name} must be > 0")


class ComparatorSuite:
    """Five prespecified comparators evaluated on the same synthetic item."""

    names = (
        "story_points", "hie_compatible", "simple_role_load",
        "proposed_model", "oracle",
    )

    def __init__(self, parameters: ComparatorParameters | None = None) -> None:
        self.p = parameters or ComparatorParameters()

    @staticmethod
    def _role_loads(item: Mapping[str, Any]) -> dict[str, float]:
        demand = item.get("role_demand")
        capacity = item.get("role_capacity")
        if not isinstance(demand, Mapping) or not demand:
            raise ValueError("role_demand must be a non-empty mapping")
        if not isinstance(capacity, Mapping):
            raise ValueError("role_capacity must be a mapping")
        if set(demand) != set(capacity):
            raise ValueError("role_demand and role_capacity must have identical roles")
        loads: dict[str, float] = {}
        for role in sorted(demand):
            d = float(demand[role])
            c = float(capacity[role])
            if not isfinite(d) or d < 0 or not isfinite(c) or c <= 0:
                raise ValueError("role demand must be >= 0 and capacity must be > 0")
            loads[str(role)] = d / c
        return loads

    def story_points(self, item: Mapping[str, Any]) -> float:
        points = _number(item, "story_points")
        budget = _number(item, "story_point_budget", minimum=1e-15)
        margin = 1.0 - points / budget
        return _logistic(margin / self.p.story_point_temperature)

    def hie_compatible(self, item: Mapping[str, Any]) -> float:
        points = _number(item, "story_points")
        budget = _number(item, "story_point_budget", minimum=1e-15)
        extra = (
            self.p.hie_context_weight * _number(item, "hie_context_load")
            + self.p.hie_interaction_weight * _number(item, "hie_interaction_load")
            + self.p.hie_oversight_weight * _number(item, "hie_oversight_load")
        )
        effective_load = points / budget + extra
        return _logistic((1.0 - effective_load) / self.p.hie_temperature)

    def simple_role_load(self, item: Mapping[str, Any]) -> float:
        maximum_load = max(self._role_loads(item).values())
        return _logistic((1.0 - maximum_load) / self.p.role_load_temperature)

    @staticmethod
    def _role_stage_loads(item: Mapping[str, Any]) -> dict[str, dict[str, float]]:
        demand = item.get("role_stage_demand")
        capacity = item.get("role_stage_capacity")
        if not isinstance(demand, Mapping) or not demand:
            raise ValueError("role_stage_demand must be a non-empty mapping")
        if not isinstance(capacity, Mapping) or set(demand) != set(capacity):
            raise ValueError("role_stage demand/capacity roles must match")
        result: dict[str, dict[str, float]] = {}
        for role in sorted(demand):
            role_demand = demand[role]
            role_capacity = capacity[role]
            if not isinstance(role_demand, Mapping) or not role_demand:
                raise ValueError("each role_stage_demand role must contain stages")
            if not isinstance(role_capacity, Mapping) or set(role_demand) != set(role_capacity):
                raise ValueError("role_stage demand/capacity stages must match")
            result[str(role)] = {}
            for stage in sorted(role_demand):
                d = float(role_demand[stage])
                c = float(role_capacity[stage])
                if not isfinite(d) or d < 0 or not isfinite(c) or c <= 0:
                    raise ValueError("role-stage demand must be >= 0 and capacity must be > 0")
                result[str(role)][str(stage)] = d / c
        return result

    def proposed_model(self, item: Mapping[str, Any]) -> float:
        # Sum stage demand within each shared role pool before taking the
        # portfolio bottleneck. This consumes role-stage structure without
        # double-counting the same calendar capacity for every stage.
        stage_loads = self._role_stage_loads(item)
        maximum_load = max(sum(stages.values()) for stages in stage_loads.values())
        readiness = _probability(item, "readiness_probability")
        rework = _probability(item, "rework_probability")
        dependency_block = _probability(item, "dependency_block_probability")
        effective_load = (
            maximum_load
            + self.p.proposed_readiness_weight * (1.0 - readiness)
            + self.p.proposed_rework_weight * rework
            + self.p.proposed_dependency_weight * dependency_block
        )
        return _logistic((1.0 - effective_load) / self.p.proposed_temperature)

    @staticmethod
    def oracle(item: Mapping[str, Any]) -> float:
        return _probability(item, "true_completion_probability")

    def forecast(self, item: Mapping[str, Any], *, include_oracle: bool = True) -> dict[str, float]:
        result = {
            "story_points": self.story_points(item),
            "hie_compatible": self.hie_compatible(item),
            "simple_role_load": self.simple_role_load(item),
            "proposed_model": self.proposed_model(item),
        }
        if include_oracle:
            result["oracle"] = self.oracle(item)
        return result

    def predicted_bottleneck(self, item: Mapping[str, Any], model: str) -> str | None:
        """Return a role prediction only for role-aware models.

        Story Points and HIE-compatible task effort do not encode role queues;
        scoring them as if they did would manufacture information.
        """
        if model not in {"simple_role_load", "proposed_model", "oracle"}:
            return None
        if model == "oracle" and "true_role_load" in item:
            loads = item["true_role_load"]
            if not isinstance(loads, Mapping) or not loads:
                raise ValueError("true_role_load must be a non-empty mapping")
        elif model == "proposed_model":
            loads = {
                role: sum(stages.values())
                for role, stages in self._role_stage_loads(item).items()
            }
        else:
            loads = self._role_loads(item)
        return min(loads, key=lambda role: (-float(loads[role]), str(role)))
