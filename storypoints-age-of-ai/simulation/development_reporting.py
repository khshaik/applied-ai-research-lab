"""Deterministic manuscript reporting for developmental simulation outputs.

The module reads only development artifacts. It produces cluster-bootstrap
uncertainty by resampling complete simulation runs and labels every output as
synthetic development evidence. It does not authorize or access locked seeds.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import random
import shutil
import tempfile
from typing import Any, Mapping, Sequence


STATUS = "developmental_synthetic_not_empirical_validation"
MODELS = (
    "story_points",
    "hie_compatible",
    "simple_role_load",
    "proposed_model",
    "oracle",
)
DEPLOYABLE_MODELS = MODELS[:-1]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _quantile(values: Sequence[float], probability: float) -> float:
    if not values:
        raise ValueError("quantile requires nonempty values")
    ordered = sorted(values)
    index = (len(ordered) - 1) * probability
    lower = math.floor(index)
    upper = math.ceil(index)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] * (upper - index) + ordered[upper] * (index - lower)


def _cluster_bootstrap_interval(run_values: Mapping[str, float], *,
                                bootstrap_replications: int,
                                seed_key: str) -> tuple[float, float]:
    if len(run_values) < 2:
        raise ValueError("cluster bootstrap requires at least two runs")
    if bootstrap_replications < 100:
        raise ValueError("at least 100 bootstrap replications are required")
    run_ids = sorted(run_values)
    seed = int.from_bytes(hashlib.sha256(seed_key.encode("utf-8")).digest()[:8], "big")
    rng = random.Random(seed)
    estimates = []
    for _ in range(bootstrap_replications):
        sample = [run_values[rng.choice(run_ids)] for _ in run_ids]
        estimates.append(sum(sample) / len(sample))
    return _quantile(estimates, 0.025), _quantile(estimates, 0.975)


def summarize_item_forecasts(rows: Sequence[Mapping[str, str]], *,
                             bootstrap_replications: int = 5000) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not rows:
        raise ValueError("item forecast rows cannot be empty")
    required = {"status", "scenario_id", "run_id", "item_id", "outcome_completed", *MODELS}
    if not required.issubset(rows[0]):
        raise ValueError(f"item forecast fields missing: {sorted(required - set(rows[0]))}")
    if any(row["status"] != "developmental_synthetic" for row in rows):
        raise ValueError("reporting accepts developmental synthetic rows only")

    model_rows: list[dict[str, Any]] = []
    scenario_rows: list[dict[str, Any]] = []
    for scenario_id in sorted({row["scenario_id"] for row in rows}):
        scenario = [row for row in rows if row["scenario_id"] == scenario_id]
        run_ids = sorted({row["run_id"] for row in scenario})
        brier_by_model: dict[str, float] = {}
        for model in MODELS:
            run_brier: dict[str, float] = {}
            for run_id in run_ids:
                selected = [row for row in scenario if row["run_id"] == run_id]
                errors = [
                    (float(row[model]) - int(row["outcome_completed"])) ** 2
                    for row in selected
                ]
                run_brier[run_id] = sum(errors) / len(errors)
            brier = sum(run_brier.values()) / len(run_brier)
            low, high = _cluster_bootstrap_interval(
                run_brier,
                bootstrap_replications=bootstrap_replications,
                seed_key=f"{scenario_id}:{model}:brier:{bootstrap_replications}",
            )
            brier_by_model[model] = brier
            model_rows.append({
                "status": STATUS,
                "scenario_id": scenario_id,
                "model": model,
                "deployable": str(model != "oracle").lower(),
                "n_runs": len(run_ids),
                "n_items": len(scenario),
                "brier_score": brier,
                "cluster_bootstrap_ci_low": low,
                "cluster_bootstrap_ci_high": high,
                "bootstrap_replications": bootstrap_replications,
                "brier_delta_vs_story_points": brier - brier_by_model.get("story_points", brier),
            })
        # Story Points is first, so overwrite exact deltas for later models and
        # calculate paired run-level contrast intervals.
        story_run: dict[str, float] = {}
        for run_id in run_ids:
            selected = [row for row in scenario if row["run_id"] == run_id]
            story_run[run_id] = sum(
                (float(row["story_points"]) - int(row["outcome_completed"])) ** 2
                for row in selected
            ) / len(selected)
        for record in [r for r in model_rows if r["scenario_id"] == scenario_id]:
            model = record["model"]
            model_run: dict[str, float] = {}
            for run_id in run_ids:
                selected = [row for row in scenario if row["run_id"] == run_id]
                model_run[run_id] = sum(
                    (float(row[model]) - int(row["outcome_completed"])) ** 2
                    for row in selected
                ) / len(selected)
            paired = {run_id: model_run[run_id] - story_run[run_id] for run_id in run_ids}
            delta_low, delta_high = _cluster_bootstrap_interval(
                paired,
                bootstrap_replications=bootstrap_replications,
                seed_key=f"{scenario_id}:{model}:paired:{bootstrap_replications}",
            )
            record["brier_delta_vs_story_points"] = sum(paired.values()) / len(paired)
            record["delta_ci_low"] = delta_low
            record["delta_ci_high"] = delta_high
        winner = min(DEPLOYABLE_MODELS, key=lambda model: brier_by_model[model])
        scenario_rows.append({
            "status": STATUS,
            "scenario_id": scenario_id,
            "n_runs": len(run_ids),
            "n_items": len(scenario),
            "descriptive_lowest_brier_model": winner,
            "descriptive_lowest_brier": brier_by_model[winner],
            "interpretation": "descriptive development-set result; not a superiority decision",
        })
    return model_rows, scenario_rows


def _write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"refusing empty report: {path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _plot_brier_deltas(path_svg: Path, path_png: Path,
                       model_rows: Sequence[Mapping[str, Any]]) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    scenarios = sorted({str(row["scenario_id"]) for row in model_rows})
    models = [model for model in DEPLOYABLE_MODELS if model != "story_points"]
    lookup = {(str(row["scenario_id"]), str(row["model"])): float(row["brier_delta_vs_story_points"])
              for row in model_rows}
    values = np.array([[lookup[(scenario, model)] for model in models] for scenario in scenarios])
    limit = max(0.01, float(np.max(np.abs(values))))
    fig_height = max(5.2, 0.43 * len(scenarios) + 2.2)
    fig, ax = plt.subplots(figsize=(8.2, fig_height))
    fig.subplots_adjust(left=0.29, right=0.88, bottom=0.14, top=0.88)
    image = ax.imshow(values, cmap="RdBu_r", vmin=-limit, vmax=limit, aspect="auto")
    ax.set_xticks(range(len(models)), [m.replace("_", " ") for m in models])
    ax.set_yticks(range(len(scenarios)), [s.replace("_", " ") for s in scenarios])
    ax.set_xlabel("Deployable comparator", labelpad=8, fontsize=10)
    ax.set_ylabel("Development scenario", fontsize=10)
    ax.set_title("Brier-score difference from Story Points\nDevelopmental synthetic evidence — lower is better",
                 fontsize=13, pad=10)
    ax.tick_params(axis="both", labelsize=9)
    for row_index in range(values.shape[0]):
        for column_index in range(values.shape[1]):
            value = values[row_index, column_index]
            color = "white" if abs(value) > limit * 0.55 else "black"
            ax.text(column_index, row_index, f"{value:+.3f}", ha="center", va="center",
                    fontsize=8, color=color)
    colorbar = fig.colorbar(image, ax=ax, shrink=0.8)
    colorbar.set_label("Brier(model) − Brier(Story Points)")
    fig.text(0.5, 0.025,
             "Negative values favor the row's comparator. Descriptive development results; not empirical or causal validation.",
             ha="center", va="bottom", fontsize=7.5)
    fig.savefig(path_svg, format="svg", metadata={"Title": "Developmental synthetic comparator differences"})
    fig.savefig(path_png, format="png", dpi=300, metadata={"Title": "Developmental synthetic comparator differences"})
    plt.close(fig)


def publish_report(input_dir: str | Path, output_dir: str | Path, *,
                   bootstrap_replications: int = 5000) -> dict[str, Any]:
    source = Path(input_dir)
    target = Path(output_dir)
    if target.exists():
        raise ValueError("immutable report output directory already exists")
    item_path = source / "item_forecasts.csv"
    development_manifest_path = source / "development_manifest.json"
    with item_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    model_rows, scenario_rows = summarize_item_forecasts(
        rows, bootstrap_replications=bootstrap_replications
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{target.name}.staging-", dir=target.parent))
    try:
        _write_csv(staging / "scenario_model_brier.csv", model_rows)
        _write_csv(staging / "scenario_summary.csv", scenario_rows)
        _plot_brier_deltas(
            staging / "figure_brier_difference_vs_story_points.svg",
            staging / "figure_brier_difference_vs_story_points.png",
            model_rows,
        )
        generated = [
            "scenario_model_brier.csv",
            "scenario_summary.csv",
            "figure_brier_difference_vs_story_points.svg",
            "figure_brier_difference_vs_story_points.png",
        ]
        manifest = {
            "manifest_version": "1.0.0-development",
            "status": STATUS,
            "interpretation_boundary": "Cluster-bootstrap uncertainty over synthetic runs; not empirical validation or a superiority test.",
            "bootstrap_unit": "simulation_run",
            "bootstrap_replications": bootstrap_replications,
            "input_sha256": {
                "item_forecasts.csv": _sha256(item_path),
                "development_manifest.json": _sha256(development_manifest_path),
            },
            "implementation_sha256": _sha256(Path(__file__)),
            "output_sha256": {name: _sha256(staging / name) for name in generated},
            "outputs": generated,
        }
        manifest_bytes = json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8") + b"\n"
        (staging / "report_manifest.json").write_bytes(manifest_bytes)
        os.replace(staging, target)
        return manifest
    except Exception:
        if staging.exists():
            shutil.rmtree(staging)
        raise


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="simulation/output/development")
    parser.add_argument("--output", required=True)
    parser.add_argument("--bootstrap-replications", type=int, default=5000)
    args = parser.parse_args(argv)
    manifest = publish_report(
        args.input, args.output,
        bootstrap_replications=args.bootstrap_replications,
    )
    print(json.dumps({"status": manifest["status"], "output": args.output}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
