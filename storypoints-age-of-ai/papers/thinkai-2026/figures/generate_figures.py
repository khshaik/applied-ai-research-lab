#!/usr/bin/env python3
"""Generate publication figures for the THINKAI working manuscript."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


HERE = Path(__file__).resolve().parent
NAVY = "#184E77"
BLUE = "#1D70A2"
TEAL = "#168AAD"
GREEN = "#2A9D8F"
AMBER = "#E9C46A"
ORANGE = "#F4A261"
RED = "#C44E52"
LIGHT = "#F5F7FA"
MID = "#DCE6EF"
DARK = "#17202A"
MUTED = "#566573"


def setup() -> None:
    matplotlib.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.linewidth": 0.8,
        "svg.hashsalt": "thinkai-vdcm-figures-v1",
    })


def canvas(width: float = 10.0, height: float = 5.8):
    fig, ax = plt.subplots(figsize=(width, height))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    return fig, ax


def box(ax, x, y, w, h, text, *, fill=LIGHT, edge=NAVY, fontsize=8.5,
        weight="normal", radius=0.015, text_color=DARK, zorder=2):
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.008,rounding_size={radius}",
        facecolor=fill, edgecolor=edge, linewidth=1.2, zorder=zorder,
    )
    ax.add_patch(patch)
    line_width = max(12, int(w * 105))
    wrapped = "\n".join(
        segment
        for raw_line in text.splitlines()
        for segment in (textwrap.wrap(raw_line, width=line_width) or [""])
    )
    ax.text(x + w / 2, y + h / 2, wrapped, ha="center", va="center",
            fontsize=fontsize, weight=weight, color=text_color, zorder=zorder + 1)
    return patch


def arrow(ax, start, end, *, color=MUTED, style="-", width=1.2,
          connectionstyle="arc3,rad=0", zorder=1):
    patch = FancyArrowPatch(
        start, end, arrowstyle="-|>", mutation_scale=11,
        linewidth=width, linestyle=style, color=color,
        connectionstyle=connectionstyle, zorder=zorder,
    )
    ax.add_patch(patch)
    return patch


def title(ax, text, subtitle=None):
    ax.text(0.5, 0.965, text, ha="center", va="top", fontsize=14,
            weight="bold", color=DARK)
    if subtitle:
        ax.text(0.5, 0.915, subtitle, ha="center", va="top", fontsize=8.5,
                color=MUTED)


def footer(ax, text):
    ax.text(0.5, 0.015, text, ha="center", va="bottom", fontsize=7.5,
            color=MUTED)


def save(fig, stem: str, title_text: str) -> list[str]:
    svg = HERE / f"{stem}.svg"
    png = HERE / f"{stem}.png"
    fig.savefig(svg, format="svg", bbox_inches="tight", metadata={"Title": title_text, "Date": None})
    fig.savefig(png, format="png", dpi=300, bbox_inches="tight", metadata={"Title": title_text})
    plt.close(fig)
    return [svg.name, png.name]


def framework_figure() -> list[str]:
    fig, ax = canvas(10.5, 5.7)
    title(ax, "Role-constrained verified delivery framework",
          "A pre-commitment resource-and-flow profile—not a replacement scalar")
    box(ax, 0.035, 0.62, 0.20, 0.21,
        "Pre-commitment demand drivers\nIU • CPE • CPD • AO • CT",
        fill="#EAF2F8", edge=BLUE, weight="bold")
    box(ax, 0.035, 0.34, 0.20, 0.17,
        "Stage automation enablement\nAI mode • context • tests • controls",
        fill="#E8F6F3", edge=GREEN)
    box(ax, 0.035, 0.10, 0.20, 0.14,
        "Risk tier and required evidence",
        fill="#FCF3CF", edge=ORANGE)
    box(ax, 0.31, 0.51, 0.20, 0.24,
        "Role–stage service-demand profile\nD(w,r,s) at commitment cutoff t₀",
        fill="#D6EAF8", edge=NAVY, weight="bold")
    box(ax, 0.58, 0.65, 0.17, 0.16,
        "Effective role capacity\nC(r,t)", fill="#E8F6F3", edge=GREEN)
    box(ax, 0.58, 0.42, 0.17, 0.16,
        "Evidence readiness\nPass • Conditional • Fail • N/A",
        fill="#FCF3CF", edge=ORANGE)
    box(ax, 0.58, 0.19, 0.17, 0.16,
        "Dependencies, queues, handoffs and bounded rework",
        fill="#FDEDEC", edge=RED)
    box(ax, 0.81, 0.39, 0.16, 0.31,
        "Verified delivery outputs\n\nTouch time\nQueue delay\nCycle time\nCompletion probability\nUnresolved obligations",
        fill=MID, edge=NAVY, weight="bold")
    for y in (0.725, 0.425, 0.17):
        arrow(ax, (0.235, y), (0.31, 0.63))
    for start, end in (
        ((0.51, 0.63), (0.58, 0.73)),
        ((0.51, 0.63), (0.58, 0.50)),
        ((0.51, 0.63), (0.58, 0.27)),
        ((0.75, 0.73), (0.81, 0.59)),
        ((0.75, 0.50), (0.81, 0.54)),
        ((0.75, 0.27), (0.81, 0.49)),
    ):
        arrow(ax, start, end)
    ax.text(0.41, 0.80, "forecast input", ha="center", fontsize=7.5, color=MUTED)
    ax.text(0.665, 0.86, "delivery-system mechanisms", ha="center", fontsize=7.5, color=MUTED)
    footer(ax, "Active service, waiting, blocking and subjective workload remain distinct quantities.")
    return save(fig, "figure_framework_architecture", "Role-constrained verified delivery framework")


def causal_figure() -> list[str]:
    fig, ax = canvas(10.5, 6.0)
    title(ax, "Hypothesized mechanism ordering",
          "Route B tests conditional model behavior; arrows are not estimated causal effects")
    box(ax, 0.04, 0.67, 0.22, 0.17, "Demand drivers + risk tier", fill="#EAF2F8", edge=BLUE, weight="bold")
    box(ax, 0.31, 0.72, 0.18, 0.12, "Stage automation enablement", fill="#E8F6F3", edge=GREEN)
    box(ax, 0.31, 0.51, 0.18, 0.14, "Forecast role–stage demand", fill="#D6EAF8", edge=NAVY, weight="bold")
    box(ax, 0.55, 0.70, 0.18, 0.14, "Capacity + existing queue", fill="#E8F6F3", edge=GREEN)
    box(ax, 0.55, 0.48, 0.18, 0.14, "Capacity pressure + queue delay", fill="#FDEDEC", edge=RED)
    box(ax, 0.31, 0.28, 0.18, 0.14, "Evidence readiness state", fill="#FCF3CF", edge=ORANGE)
    box(ax, 0.55, 0.27, 0.18, 0.14, "Gate decision + rework", fill="#FCE4D6", edge=ORANGE)
    box(ax, 0.79, 0.45, 0.17, 0.22, "Touch + wait + block + rework\n\nVerified completion and cycle time", fill=MID, edge=NAVY, weight="bold")
    box(ax, 0.79, 0.17, 0.17, 0.14, "External quality, UAT and delivery criteria", fill=LIGHT, edge=MUTED)
    arrow(ax, (0.26, 0.75), (0.31, 0.58), style="--")
    arrow(ax, (0.40, 0.72), (0.40, 0.65), style="--")
    arrow(ax, (0.49, 0.58), (0.55, 0.55), style="--")
    arrow(ax, (0.64, 0.70), (0.64, 0.62), style="--")
    arrow(ax, (0.49, 0.55), (0.55, 0.55), style="--")
    arrow(ax, (0.49, 0.35), (0.55, 0.34), style="--")
    arrow(ax, (0.73, 0.55), (0.79, 0.56), style="--")
    arrow(ax, (0.73, 0.34), (0.79, 0.50), style="--")
    arrow(ax, (0.875, 0.45), (0.875, 0.31), style="--")
    arrow(ax, (0.55, 0.31), (0.49, 0.38), style="--", connectionstyle="arc3,rad=-0.25")
    ax.text(0.17, 0.61, "observable at t₀", fontsize=7.5, color=MUTED)
    footer(ax, "Prospective models exclude realized prompt counts, churn, review comments, failures and post-t₀ evidence.")
    return save(fig, "figure_causal_mechanism", "Hypothesized causal and mechanism ordering")


def lifecycle_figure() -> list[str]:
    fig, ax = canvas(11.2, 5.7)
    title(ax, "Lifecycle and accountable role-stage demand",
          "Illustrative mapping; organizations may combine pools but must preserve traceability")
    stages = [
        ("1", "Intent & acceptance", "Product / domain"),
        ("2", "Architecture & risk", "Architecture / security"),
        ("3", "Context & generation plan", "Product / development"),
        ("4", "Implementation & refinement", "Development"),
        ("5", "Independent review", "Peer review / security"),
        ("6", "Integration & QA", "QA / test"),
        ("7", "Release validation", "Operations / release"),
        ("8", "UAT & acceptance", "Business acceptance"),
    ]
    positions = []
    for index, (number, name, role) in enumerate(stages):
        row = 1 if index < 4 else 0
        # Snake layout: stage 5 sits below stage 4, then progression moves
        # right-to-left across the second row.
        column = index if row else 7 - index
        x = 0.045 + column * 0.24
        y = 0.55 if row else 0.18
        positions.append((x, y))
        box(ax, x, y, 0.19, 0.22, f"{number}. {name}\n\n{role}",
            fill="#EAF2F8" if row else "#E8F6F3", edge=BLUE if row else GREEN,
            fontsize=8.2, weight="bold")
    for index in range(3):
        arrow(ax, (positions[index][0] + 0.19, positions[index][1] + 0.11),
              (positions[index + 1][0], positions[index + 1][1] + 0.11))
    arrow(ax, (positions[3][0] + 0.095, positions[3][1]),
          (positions[4][0] + 0.095, positions[4][1] + 0.22))
    for index in range(4, 7):
        arrow(ax, (positions[index][0], positions[index][1] + 0.11),
              (positions[index + 1][0] + 0.19, positions[index + 1][1] + 0.11))
    ax.text(0.5, 0.47, "Evidence failure or conditional risk can trigger a declared bounded return to an earlier stage",
            ha="center", fontsize=8, color=RED)
    arrow(ax, (positions[7][0] + 0.095, positions[7][1] + 0.22),
          (positions[1][0] + 0.095, positions[1][1]), color=RED,
          style="--", connectionstyle="arc3,rad=-0.25")
    footer(ax, "At every stage, active service, queue delay, blocking, evidence state and accountable role remain separately recorded.")
    return save(fig, "figure_lifecycle_roles", "Lifecycle and accountable role-stage demand")


def simulation_figure() -> list[str]:
    fig, ax = canvas(10.8, 5.7)
    title(ax, "Developmental simulation and comparator isolation",
          "Only information available at commitment cutoff t₀ enters deployable forecasts")
    box(ax, 0.035, 0.57, 0.18, 0.20, "Development configuration\n+ declared development seed namespace", fill="#EAF2F8", edge=BLUE, weight="bold")
    box(ax, 0.275, 0.57, 0.18, 0.20, "Synthetic truth DES\ncalendars • queues • gates • dependencies • rework", fill="#FDEDEC", edge=RED, weight="bold")
    box(ax, 0.515, 0.66, 0.18, 0.16, "Immutable realized outcomes\n(events, service, gates, terminal state)", fill="#FCE4D6", edge=ORANGE)
    box(ax, 0.515, 0.39, 0.18, 0.16, "t₀ comparator packet\n(no realized outcomes)", fill="#E8F6F3", edge=GREEN)
    box(ax, 0.755, 0.50, 0.20, 0.25, "Forecast and evaluation\n\nStory Points\nHIE-compatible\nSimple role load\nProposed model\nDiagnostic oracle", fill=MID, edge=NAVY, weight="bold")
    box(ax, 0.275, 0.17, 0.42, 0.11, "Checksummed reports: Brier/calibration • run-cluster uncertainty • negative results • parameter provenance", fill=LIGHT, edge=MUTED)
    arrow(ax, (0.215, 0.67), (0.275, 0.67))
    arrow(ax, (0.455, 0.68), (0.515, 0.74))
    arrow(ax, (0.455, 0.62), (0.515, 0.47))
    arrow(ax, (0.695, 0.74), (0.755, 0.66))
    arrow(ax, (0.695, 0.47), (0.755, 0.58))
    arrow(ax, (0.855, 0.50), (0.65, 0.28))
    ax.text(0.60, 0.59, "isolation boundary", ha="center", fontsize=7.5, color=GREEN)
    box(ax, 0.035, 0.14, 0.18, 0.14,
        "Locked production seeds and outputs:\nnot accessed / outside paper route",
        fill="#FDEDEC", edge=RED, fontsize=7.2)
    footer(ax, "Developmental synthetic mechanism evidence only; not empirical, cognitive, organizational or causal validation.")
    return save(fig, "figure_simulation_flow", "Developmental simulation and comparator isolation")


def evidence_figure() -> list[str]:
    fig, ax = canvas(11.3, 6.1)
    title(ax, "Targeted open evidence-map workflow",
          "Developmental searches remain outside the systematic corpus until accountable-author approval and freeze")
    steps = [
        ("Approved protocol\n+ declared source–family pairs", "#EAF2F8", BLUE),
        ("Complete open-index exports\nraw pages + checksums", "#EAF2F8", BLUE),
        ("Normalize, deduplicate\n+ consolidate study families", "#E8F6F3", GREEN),
        ("Isolated Agent A and B\nsame checksummed packet", "#E8F6F3", GREEN),
        ("Separate adjudication\nagent concordance", "#FCF3CF", ORANGE),
        ("Lawful full text\nappraisal + exact locators", "#FCF3CF", ORANGE),
        ("Bidirectional citation chase\nto stopping rule", "#FCE4D6", RED),
        ("Accountable-author\nclaim confirmation", "#FDEDEC", RED),
        ("Evidence matrix + flow ledger\n+ bounded novelty conclusion", MID, NAVY),
    ]
    positions = []
    for index, (label, fill, edge) in enumerate(steps):
        row = 1 if index < 5 else 0
        # Snake layout continues down from adjudication and moves right-to-left.
        column = index if row else 8 - index
        x = 0.025 + column * (0.19 if row else 0.235)
        y = 0.58 if row else 0.20
        w = 0.16 if row else 0.195
        positions.append((x, y, w))
        box(ax, x, y, w, 0.18, label, fill=fill, edge=edge, fontsize=7.8,
            weight="bold" if index in (0, 8) else "normal")
    for index in range(4):
        x, y, w = positions[index]
        nx, ny, _ = positions[index + 1]
        arrow(ax, (x + w, y + 0.09), (nx, ny + 0.09))
    arrow(ax, (positions[4][0] + positions[4][2] / 2, positions[4][1]),
          (positions[5][0] + positions[5][2] / 2, positions[5][1] + 0.18))
    for index in range(5, 8):
        x, y, w = positions[index]
        nx, ny, _ = positions[index + 1]
        arrow(ax, (x, y + 0.09), (nx + positions[index + 1][2], ny + 0.09))
    arrow(ax, (positions[6][0] + positions[6][2] / 2, positions[6][1] + 0.18),
          (positions[2][0] + positions[2][2] / 2, positions[2][1]),
          style="--", color=RED, connectionstyle="arc3,rad=-0.35")
    ax.text(0.52, 0.49, "new citation-network records re-enter the same workflow", ha="center", fontsize=7.5, color=RED)
    box(ax, 0.025, 0.035, 0.28, 0.09,
        "Developmental query records: retained for engineering audit only; never counted as systematic inclusions",
        fill=LIGHT, edge=MUTED, fontsize=7.2)
    ax.text(0.98, 0.045,
            "Peer-reviewed • preprint • secondary • practitioner • method/reference strata remain distinct",
            ha="right", va="bottom", fontsize=7.2, color=MUTED)
    return save(fig, "figure_evidence_map_flow", "Targeted open evidence-map workflow")


def main() -> None:
    setup()
    outputs = []
    for generator in (
        framework_figure,
        causal_figure,
        lifecycle_figure,
        simulation_figure,
        evidence_figure,
    ):
        outputs.extend(generator())
    hashes = {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in outputs}
    manifest = {
        "manifest_version": "1.0.0-working",
        "status": "working_manuscript_figures",
        "implementation_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "outputs": outputs,
        "output_sha256": hashes,
        "interpretation_boundary": "Conceptual figures and developmental method diagrams; not empirical validation.",
    }
    (HERE / "figure_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": manifest["status"], "outputs": len(outputs)}, sort_keys=True))


if __name__ == "__main__":
    main()
