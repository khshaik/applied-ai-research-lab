"""Prespecified forecast and bottleneck metrics for synthetic evaluation."""

from __future__ import annotations

from math import log, sqrt
from statistics import stdev
from typing import Iterable, Mapping, Sequence


def _validate_binary_inputs(probabilities: Sequence[float], outcomes: Sequence[int]) -> None:
    if not probabilities or len(probabilities) != len(outcomes):
        raise ValueError("probabilities and outcomes must be non-empty and equal length")
    if any(not 0.0 <= float(p) <= 1.0 for p in probabilities):
        raise ValueError("probabilities must be in [0, 1]")
    if any(y not in (0, 1) for y in outcomes):
        raise ValueError("outcomes must be binary")


def brier_score(probabilities: Sequence[float], outcomes: Sequence[int]) -> float:
    _validate_binary_inputs(probabilities, outcomes)
    return sum((float(p) - y) ** 2 for p, y in zip(probabilities, outcomes)) / len(outcomes)


def relative_brier_skill(candidate: float, reference: float) -> float:
    """Positive values mean improvement; undefined when reference is zero."""
    if reference <= 0:
        raise ValueError("reference Brier score must be > 0")
    return (reference - candidate) / reference


def log_loss(probabilities: Sequence[float], outcomes: Sequence[int], epsilon: float = 1e-15) -> float:
    _validate_binary_inputs(probabilities, outcomes)
    return -sum(
        y * log(min(1 - epsilon, max(epsilon, p)))
        + (1 - y) * log(min(1 - epsilon, max(epsilon, 1 - p)))
        for p, y in zip(probabilities, outcomes)
    ) / len(outcomes)


def calibration_table(
    probabilities: Sequence[float], outcomes: Sequence[int], bins: int = 10
) -> list[dict[str, float | int]]:
    _validate_binary_inputs(probabilities, outcomes)
    if bins < 2:
        raise ValueError("bins must be >= 2")
    grouped: list[list[tuple[float, int]]] = [[] for _ in range(bins)]
    for probability, outcome in zip(probabilities, outcomes):
        index = min(int(float(probability) * bins), bins - 1)
        grouped[index].append((float(probability), outcome))
    rows: list[dict[str, float | int]] = []
    for index, values in enumerate(grouped):
        if not values:
            continue
        rows.append({
            "bin": index,
            "lower": index / bins,
            "upper": (index + 1) / bins,
            "count": len(values),
            "mean_forecast": sum(p for p, _ in values) / len(values),
            "observed_rate": sum(y for _, y in values) / len(values),
        })
    return rows


def expected_calibration_error(
    probabilities: Sequence[float], outcomes: Sequence[int], bins: int = 10
) -> float:
    rows = calibration_table(probabilities, outcomes, bins)
    total = len(probabilities)
    return sum(
        int(row["count"]) / total
        * abs(float(row["mean_forecast"]) - float(row["observed_rate"]))
        for row in rows
    )


def bottleneck_accuracy(predicted: Sequence[str | None], actual: Sequence[str]) -> dict[str, float | int]:
    if len(predicted) != len(actual) or not actual:
        raise ValueError("predicted and actual bottlenecks must be non-empty and equal length")
    eligible = [(p, a) for p, a in zip(predicted, actual) if p is not None]
    correct = sum(p == a for p, a in eligible)
    return {
        "accuracy": correct / len(eligible) if eligible else 0.0,
        "eligible_n": len(eligible),
        "abstained_n": len(actual) - len(eligible),
    }


def quantile(values: Sequence[float], probability: float) -> float:
    """Dependency-free, linearly interpolated sample quantile (type 7)."""
    if not values or not 0 <= probability <= 1:
        raise ValueError("values must be non-empty and probability in [0, 1]")
    ordered = sorted(float(value) for value in values)
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def quantile_absolute_error(
    predicted: Sequence[float], actual: Sequence[float], probability: float
) -> float:
    """Absolute error for cycle-time or role-queue-delay quantiles."""
    return abs(quantile(predicted, probability) - quantile(actual, probability))


def paired_brier_contrast(
    candidate: Sequence[float], reference: Sequence[float], outcomes: Sequence[int]
) -> dict[str, float]:
    """Paired candidate improvement with a normal Monte Carlo interval.

    Positive differences favor the candidate.  The interval is appropriate for
    independent replication-level observations. Clustered portfolios require a
    cluster-aware interval in the final evaluation pipeline.
    """
    _validate_binary_inputs(candidate, outcomes)
    _validate_binary_inputs(reference, outcomes)
    if len(candidate) < 2:
        raise ValueError("at least two paired observations are required")
    differences = [
        (float(r) - y) ** 2 - (float(c) - y) ** 2
        for c, r, y in zip(candidate, reference, outcomes)
    ]
    improvement = sum(differences) / len(differences)
    standard_error = stdev(differences) / sqrt(len(differences))
    reference_score = brier_score(reference, outcomes)
    return {
        "absolute_improvement": improvement,
        "relative_skill": relative_brier_skill(brier_score(candidate, outcomes), reference_score),
        "standard_error": standard_error,
        "ci95_lower": improvement - 1.96 * standard_error,
        "ci95_upper": improvement + 1.96 * standard_error,
    }


def adjudicate_proposed_model(
    contrast: Mapping[str, float],
    configuration_improvements: Sequence[float],
    bottleneck_improvement: float,
    *,
    relative_skill_threshold: float = 0.05,
    absolute_equivalence_margin: float = 0.01,
    robustness_fraction: float = 0.80,
    bottleneck_improvement_threshold: float = 0.10,
) -> dict[str, float | bool | str]:
    """Apply the provisional Gate 3B conventions without overclaiming.

    Passing supports only the synthetic mechanism claim. It is not empirical
    evidence that the proposed model improves organizational delivery.
    """
    if not configuration_improvements:
        raise ValueError("configuration_improvements cannot be empty")
    direction_fraction = sum(value > 0 for value in configuration_improvements) / len(configuration_improvements)
    interval_excludes_zero = float(contrast["ci95_lower"]) > 0
    practically_non_equivalent = float(contrast["absolute_improvement"]) >= absolute_equivalence_margin
    checks = {
        "relative_skill_pass": float(contrast["relative_skill"]) >= relative_skill_threshold,
        "interval_pass": interval_excludes_zero,
        "absolute_margin_pass": practically_non_equivalent,
        "robustness_pass": direction_fraction >= robustness_fraction,
        "bottleneck_pass": bottleneck_improvement >= bottleneck_improvement_threshold,
    }
    passed = all(checks.values())
    return {
        **checks,
        "direction_fraction": direction_fraction,
        "bottleneck_improvement": bottleneck_improvement,
        "synthetic_decision": "retain_for_field_testing" if passed else "do_not_claim_advantage",
    }


def evaluate_forecasts(
    forecasts: Mapping[str, Sequence[float]],
    outcomes: Sequence[int],
    *,
    strongest_deployable: str | None = None,
    bins: int = 10,
) -> dict[str, dict[str, float | list[dict[str, float | int]]]]:
    """Evaluate each model without treating the oracle as deployable."""
    if not forecasts:
        raise ValueError("forecasts cannot be empty")
    scores: dict[str, dict[str, float | list[dict[str, float | int]]]] = {}
    for model, probabilities in forecasts.items():
        scores[model] = {
            "brier_score": brier_score(probabilities, outcomes),
            "log_loss": log_loss(probabilities, outcomes),
            "ece": expected_calibration_error(probabilities, outcomes, bins),
            "calibration": calibration_table(probabilities, outcomes, bins),
        }
    if strongest_deployable is not None:
        if strongest_deployable == "oracle":
            raise ValueError("oracle cannot be the deployable reference")
        if strongest_deployable not in scores:
            raise ValueError("strongest_deployable is absent from forecasts")
        reference = float(scores[strongest_deployable]["brier_score"])
        for model in scores:
            scores[model]["relative_brier_skill"] = (
                0.0 if model == strongest_deployable
                else relative_brier_skill(float(scores[model]["brier_score"]), reference)
            )
    return scores
