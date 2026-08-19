"""Deterministic calendar and portfolio-dependency scheduling primitives.

The simulation clock is measured from the earliest configured calendar
interval start. Calendar timestamps are converted into the configured time
unit. Each interval is an explicit, fully available window; aggregate
utilization multipliers are rejected. Explicit blackout periods subtract
availability and pause service.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import math
from typing import Any, Iterable, Mapping


class CalendarSemanticsError(ValueError):
    """Raised when capacity timing cannot be executed unambiguously."""


class DependencySemanticsError(ValueError):
    """Raised when portfolio dependency semantics are invalid or unsupported."""


def _parse_datetime(value: str, context: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)
    except (TypeError, ValueError) as exc:
        raise CalendarSemanticsError(f"{context} must be an RFC 3339 timestamp") from exc
    if parsed.tzinfo is None:
        raise CalendarSemanticsError(f"{context} must include a UTC offset")
    return parsed


def _seconds_per_unit(unit: str) -> float:
    try:
        return {"minutes": 60.0, "hours": 3600.0, "days": 86400.0}[unit]
    except KeyError as exc:
        raise CalendarSemanticsError(f"unsupported simulation time unit: {unit!r}") from exc


@dataclass(frozen=True)
class AvailabilityWindow:
    start: float
    end: float


@dataclass(frozen=True)
class CapacityCalendar:
    calendar_id: str
    windows: tuple[AvailabilityWindow, ...]
    concurrency: int

    def next_available(self, at: float) -> float | None:
        """Return the first available instant at or after ``at``."""
        for window in self.windows:
            if window.end <= at:
                continue
            return max(at, window.start)
        return None

    def finish_time(self, start: float, work: float) -> float | None:
        """Consume touch-work over open windows, pausing across closures.

        ``work`` is in simulation work-time units. Open-window time and touch
        time advance one-for-one; closures are reported separately by the
        engine. ``None`` means the calendar has insufficient future capacity.
        """
        if not math.isfinite(work) or work < 0:
            raise CalendarSemanticsError("service demand must be finite and nonnegative")
        if work == 0:
            return self.next_available(start)
        remaining = work
        cursor = start
        for window in self.windows:
            if window.end <= cursor:
                continue
            active_start = max(cursor, window.start)
            available_work = window.end - active_start
            if available_work + 1e-12 >= remaining:
                return active_start + remaining
            remaining -= available_work
            cursor = window.end
        return None


def compile_capacity_calendars(
    records: Iterable[Mapping[str, Any]], unit: str
) -> dict[str, CapacityCalendar]:
    """Compile timestamp intervals and blackouts into disjoint open windows."""
    records = tuple(records)
    interval_starts = [
        _parse_datetime(interval["start"], f"calendar {record['id']} interval start")
        for record in records
        for interval in record["intervals"]
    ]
    if not interval_starts:
        raise CalendarSemanticsError("at least one capacity interval is required")
    origin = min(interval_starts)
    scale = _seconds_per_unit(unit)
    compiled: dict[str, CapacityCalendar] = {}
    for record in records:
        calendar_id = str(record["id"])
        intervals: list[tuple[float, float]] = []
        for index, interval in enumerate(record["intervals"]):
            start_dt = _parse_datetime(interval["start"], f"calendar {calendar_id} interval {index} start")
            end_dt = _parse_datetime(interval["end"], f"calendar {calendar_id} interval {index} end")
            if end_dt <= start_dt:
                raise CalendarSemanticsError(f"calendar {calendar_id} interval {index} has nonpositive duration")
            gross = float(interval["gross_hours"])
            effective = float(interval["effective_hours"])
            elapsed_hours = (end_dt - start_dt).total_seconds() / 3600.0
            absence = float(interval["absence_hours"])
            nonproject = float(interval["nonproject_hours"])
            if (not math.isclose(gross, elapsed_hours, abs_tol=1e-9)
                    or not math.isclose(effective, elapsed_hours, abs_tol=1e-9)
                    or absence != 0 or nonproject != 0):
                raise CalendarSemanticsError(
                    f"calendar {calendar_id} interval {index} must be an explicit fully "
                    "available window; encode closures as blackouts"
                )
            intervals.append(((start_dt - origin).total_seconds() / scale,
                              (end_dt - origin).total_seconds() / scale))
        intervals.sort()
        for prior, current in zip(intervals, intervals[1:]):
            if current[0] < prior[1]:
                raise CalendarSemanticsError(f"calendar {calendar_id} contains overlapping intervals")

        blackouts: list[tuple[float, float]] = []
        for index, blackout in enumerate(record.get("blackout_periods", [])):
            if set(blackout) != {"start", "end"}:
                raise CalendarSemanticsError(
                    f"calendar {calendar_id} blackout {index} must contain only start and end"
                )
            start_dt = _parse_datetime(blackout["start"], f"calendar {calendar_id} blackout {index} start")
            end_dt = _parse_datetime(blackout["end"], f"calendar {calendar_id} blackout {index} end")
            if end_dt <= start_dt:
                raise CalendarSemanticsError(f"calendar {calendar_id} blackout {index} has nonpositive duration")
            blackout_start = (start_dt - origin).total_seconds() / scale
            blackout_end = (end_dt - origin).total_seconds() / scale
            if not any(interval_start <= blackout_start and blackout_end <= interval_end
                       for interval_start, interval_end in intervals):
                raise CalendarSemanticsError(
                    f"calendar {calendar_id} blackout {index} must be contained in one availability window"
                )
            blackouts.append((blackout_start, blackout_end))
        blackouts.sort()
        merged: list[list[float]] = []
        for start, end in blackouts:
            if merged and start <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], end)
            else:
                merged.append([start, end])

        windows: list[AvailabilityWindow] = []
        for start, end in intervals:
            pieces = [(start, end)]
            for blackout_start, blackout_end in merged:
                next_pieces: list[tuple[float, float]] = []
                for piece_start, piece_end in pieces:
                    if blackout_end <= piece_start or blackout_start >= piece_end:
                        next_pieces.append((piece_start, piece_end))
                    else:
                        if piece_start < blackout_start:
                            next_pieces.append((piece_start, blackout_start))
                        if blackout_end < piece_end:
                            next_pieces.append((blackout_end, piece_end))
                pieces = next_pieces
            windows.extend(AvailabilityWindow(piece_start, piece_end)
                           for piece_start, piece_end in pieces if piece_end > piece_start)
        concurrency = int(record["concurrency"])
        if concurrency < 1:
            raise CalendarSemanticsError(f"calendar {calendar_id} concurrency must be positive")
        compiled[calendar_id] = CapacityCalendar(calendar_id, tuple(windows), concurrency)
    return compiled


def compile_template_dependencies(
    templates: Iterable[Mapping[str, Any]], models: Iterable[Mapping[str, Any]]
) -> dict[str, frozenset[str]]:
    """Return predecessor templates and templates participating in cycles.

    A dependency model is activated by the successor template's
    ``dependency_ids``.  Its edge ``[A, B]`` means every portfolio item using
    template B waits for all items using template A to complete successfully.
    """
    templates = tuple(templates)
    known = {str(template["id"]) for template in templates}
    by_id = {str(model["id"]): model for model in models}
    predecessors: dict[str, set[str]] = {template_id: set() for template_id in known}
    for template in templates:
        successor_id = str(template["id"])
        for model_id in template.get("dependency_ids", []):
            if model_id not in by_id:
                raise DependencySemanticsError(
                    f"template {successor_id} references unknown dependency model {model_id}"
                )
            model = by_id[model_id]
            expected = {
                "release_rule": "all_predecessor_items_completed_successfully",
                "failure_policy": "block_successor",
                "scope": "template_all_to_all",
            }
            for field, value in expected.items():
                if model.get(field) != value:
                    raise DependencySemanticsError(
                        f"dependency model {model_id} requires {field}={value!r}"
                    )
            if model.get("cycles_allowed_for_test") is not False:
                raise DependencySemanticsError(
                    f"dependency model {model_id} must set cycles_allowed_for_test=false"
                )
            for edge in model["edges"]:
                predecessor, successor = map(str, edge)
                if predecessor not in known or successor not in known:
                    raise DependencySemanticsError(
                        f"dependency model {model_id} references unknown template"
                    )
                if successor == successor_id:
                    predecessors[successor].add(predecessor)

    visiting: set[str] = set()
    visited: set[str] = set()
    cyclic: set[str] = set()

    def visit(node: str, path: tuple[str, ...]) -> None:
        if node in visiting:
            start = path.index(node)
            cyclic.update(path[start:])
            return
        if node in visited:
            return
        visiting.add(node)
        for predecessor in sorted(predecessors[node]):
            visit(predecessor, path + (predecessor,))
        visiting.remove(node)
        visited.add(node)

    for template_id in sorted(known):
        visit(template_id, (template_id,))
    if cyclic:
        raise DependencySemanticsError(
            f"dependency cycle is not allowed: {sorted(cyclic)}"
        )
    return {key: frozenset(value) for key, value in predecessors.items()}
