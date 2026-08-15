from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


OUT = Path(__file__).resolve().parents[1] / "assets"
REPOSITORY = Path(__file__).resolve().parents[4]
RESULTS = (
    REPOSITORY
    / "studies/raer/evaluation/v2/results_design_v1.0/oof_policy_summary.csv"
)

BG = "#FFFFFF"
PANEL = "#F7F7F7"
INK = "#000000"
MUTED = "#000000"
CYAN = "#000000"
GREEN = "#000000"
AMBER = "#000000"
RED = "#000000"
VIOLET = "#000000"
GRID = "#D8D8D8"
CONTENT_LEFT = 0.05


def setup_ax(title: str, subtitle: str):
    fig, ax = plt.subplots(figsize=(12, 9), dpi=150)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    title_artist = ax.text(CONTENT_LEFT, 0.965, title, color=INK, fontsize=27, weight="bold", va="top")
    subtitle_artist = ax.text(CONTENT_LEFT, 0.875, subtitle, color=INK, fontsize=13, va="top")
    ax.plot([CONTENT_LEFT, 0.14], [0.835, 0.835], color=INK, lw=2.2, solid_capstyle="round")
    ax._qa_title_pair = (title_artist, subtitle_artist)
    ax._qa_box_pairs = []
    ax._qa_left_aligned = [title_artist, subtitle_artist]
    return fig, ax


def box(ax, x, y, w, h, title, body="", edge=CYAN, fill=PANEL, title_size=14, body_size=10):
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.012,rounding_size=0.018",
        linewidth=1.8,
        edgecolor=edge,
        facecolor=fill,
    )
    ax.add_patch(patch)
    title_artist = ax.text(x + 0.02, y + h - 0.035, title, color=INK, fontsize=title_size, weight="bold", va="top")
    text_artists = [title_artist]
    if body:
        body_artist = ax.text(x + 0.02, y + h - 0.082, body, color=MUTED, fontsize=body_size, va="top", linespacing=1.5)
        text_artists.append(body_artist)
    if not hasattr(ax, "_qa_box_pairs"):
        ax._qa_box_pairs = []
    ax._qa_box_pairs.append((title.replace("\n", " "), patch, text_artists))
    return patch


def arrow(ax, start, end, color=MUTED, width=1.8, style="-|>"):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle=style, mutation_scale=13, linewidth=width, color=color))


def footer(ax, text="Source: RAER v2 public research artifact; design-stage evidence only"):
    artist = ax.text(CONTENT_LEFT, 0.025, text, color=MUTED, fontsize=8.5, va="bottom", ha="left")
    ax._qa_left_aligned.append(artist)


def bottom_statement(ax, y, text, fontsize=14):
    artist = ax.text(
        CONTENT_LEFT,
        y,
        text,
        color=INK,
        fontsize=fontsize,
        weight="bold",
        ha="left",
        va="top",
        linespacing=1.25,
    )
    ax._qa_left_aligned.append(artist)
    return artist


def save(fig, name):
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for ax in fig.axes:
        title_pair = getattr(ax, "_qa_title_pair", None)
        if title_pair:
            title_bbox = title_pair[0].get_window_extent(renderer)
            subtitle_bbox = title_pair[1].get_window_extent(renderer)
            if title_bbox.y0 - subtitle_bbox.y1 < 10:
                raise ValueError(f"{name}: insufficient main-title/subtitle spacing")
        aligned_artists = getattr(ax, "_qa_left_aligned", [])
        if aligned_artists:
            aligned_x = [artist.get_window_extent(renderer).x0 for artist in aligned_artists]
            if max(aligned_x) - min(aligned_x) > 1:
                raise ValueError(f"{name}: title, subtitle, bottom text, or footer left edges are misaligned")
        for label, patch, text_artists in getattr(ax, "_qa_box_pairs", []):
            patch_bbox = patch.get_window_extent(renderer)
            inset = 6
            text_bboxes = [artist.get_window_extent(renderer) for artist in text_artists]
            for text_bbox in text_bboxes:
                if not (
                    text_bbox.x0 >= patch_bbox.x0 + inset
                    and text_bbox.x1 <= patch_bbox.x1 - inset
                    and text_bbox.y0 >= patch_bbox.y0 + inset
                    and text_bbox.y1 <= patch_bbox.y1 - inset
                ):
                    raise ValueError(
                        f"{name}: text exceeds safe inset in box '{label}' "
                        f"text={tuple(round(v, 1) for v in text_bbox.extents)} "
                        f"box={tuple(round(v, 1) for v in patch_bbox.extents)}"
                    )
            if len(text_bboxes) == 2 and text_bboxes[0].overlaps(text_bboxes[1]):
                raise ValueError(f"{name}: title/body overlap in box '{label}'")
    fig.savefig(OUT / name, facecolor=BG, bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)


def context_lifecycle():
    fig, ax = setup_ax(
        "Context is a temporal contract, not a prompt snapshot",
        "A plan can be logically correct at t0 and operationally wrong at t2.",
    )
    cols = [
        (0.04, "BEFORE: OBSERVE", CYAN, "Evidence is collected\n\u2022 identity + authority\n\u2022 policy + scope\n\u2022 resource + operational state\n\u2022 provenance + version + time"),
        (0.37, "NOW: REVALIDATE", AMBER, "The system approaches commit\n\u2022 estimate invalidity q_i\n\u2022 weight criticality w_i\n\u2022 select checks under budget B\n\u2022 force sensitive authority checks"),
        (0.70, "AFTER: RECONCILE", GREEN, "The action changes the world\n\u2022 verify committed outcome\n\u2022 emit immutable evidence\n\u2022 invalidate dependent memory\n\u2022 monitor or compensate"),
    ]
    for x, title, color, body in cols:
        box(ax, x, 0.47, 0.24, 0.32, title, body, edge=color, title_size=12.5, body_size=8.6)
    arrow(ax, (0.294, 0.63), (0.346, 0.63), AMBER, 2.5)
    arrow(ax, (0.624, 0.63), (0.676, 0.63), GREEN, 2.5)
    ax.text(0.32, 0.668, "DRIFT", color=AMBER, fontsize=9, weight="bold", ha="center")
    ax.text(0.65, 0.668, "COMMIT", color=GREEN, fontsize=9, weight="bold", ha="center")
    box(
        ax, 0.03, 0.18, 0.90, 0.18,
        "The failure is semantic, not syntactic",
        "A model may faithfully reason over evidence that is stale, superseded, or contradictory,\n"
        "or no longer authorized. More context tokens do not repair missing freshness\n"
        "or authority guarantees.",
        edge=RED, body_size=10.5,
    )
    ax.text(0.04, 0.405, "t0", color=CYAN, fontsize=12, weight="bold")
    ax.text(0.37, 0.405, "t1 / pre-commit", color=AMBER, fontsize=12, weight="bold")
    ax.text(0.70, 0.405, "t2+", color=GREEN, fontsize=12, weight="bold")
    footer(ax)
    save(fig, "01-context-lifecycle.png")


def architecture_extension():
    fig, ax = setup_ax(
        "Architecture choice and evidence validity are orthogonal",
        "Use the least complex execution architecture that fits the capability - then gate every consequential commit.",
    )
    names = ["RULE-BASED\nSOFTWARE", "LLM\nCAPABILITY", "FIXED\nWORKFLOW", "SINGLE\nAGENT", "MULTI-AGENT\nSYSTEM"]
    colors = [MUTED, CYAN, VIOLET, AMBER, RED]
    x0 = 0.05
    top_pitch = 0.19
    top_width = 0.14
    for i, (name, color) in enumerate(zip(names, colors)):
        x = x0 + i * top_pitch
        box(ax, x, 0.66, top_width, 0.12, name, edge=color, title_size=10.3)
        if i < 4:
            next_x = x0 + (i + 1) * top_pitch
            arrow(ax, (x + top_width + 0.014, 0.72), (next_x - 0.014, 0.72), MUTED)
    ax.text(0.05, 0.61, "Increasing dynamic control, coordination, latency, and failure surface", color=MUTED, fontsize=10)
    ax.plot([0.08, 0.92], [0.53, 0.53], color=GRID, lw=2)
    ax.text(0.5, 0.555, "PRE-ACTION EVIDENCE GATE APPLIES ACROSS THE ENTIRE STACK", color=GREEN, fontsize=12, weight="bold", ha="center")
    gate_items = [
        (0.055, "1  TYPE", "Identify mutable\nclaims"),
        (0.245, "2  SCORE", "Consequence +\nauthority + criticality\n+ cost"),
        (0.435, "3  CHECK", "Select authoritative\nchecks under budget"),
        (0.625, "4  DECIDE", "ACT / REFRESH / ASK\n/ ABSTAIN"),
        (0.815, "5  PROVE", "Record evidence +\ncommitted outcome"),
    ]
    gate_width = 0.13
    for x, title, body in gate_items:
        box(ax, x, 0.25, gate_width, 0.17, title, body, edge=GREEN, title_size=9.8, body_size=6.8)
    for i in range(4):
        arrow(ax, (gate_items[i][0] + gate_width + 0.014, 0.335), (gate_items[i + 1][0] - 0.014, 0.335), GREEN)
    bottom_statement(
        ax,
        0.155,
        "Agency changes who chooses the next step.\nIt does not make old evidence current.",
        fontsize=14,
    )
    footer(ax, "Conceptual synthesis: capability-first agent design + RAER pre-action evidence control")
    save(fig, "02-architecture-and-evidence-gate.png")


def decision_loop():
    fig, ax = setup_ax(
        "A production context switch needs an explicit decision protocol",
        "RAER models evidence selection and abstention before a consequential tool action.",
    )
    box(ax, 0.04, 0.68, 0.17, 0.13, "PROPOSED\nACTION", "Intent + parameters\n+ read/write set", edge=CYAN, title_size=10.5, body_size=8)
    box(ax, 0.28, 0.68, 0.18, 0.13, "EVIDENCE LEDGER", "q_i, w_i, c_i, source\nversion + observed_at", edge=CYAN, title_size=10.2, body_size=7.7)
    box(ax, 0.53, 0.68, 0.17, 0.13, "SELECT S", "Exact subset search\nunder B + delta", edge=AMBER, title_size=10.5, body_size=8)
    box(ax, 0.77, 0.68, 0.17, 0.13, "AUTH GATE", "Mandatory if risk\nthreshold triggers", edge=RED, title_size=10.5, body_size=8)
    for a, b in [((0.224, 0.745), (0.266, 0.745)), ((0.474, 0.745), (0.516, 0.745)), ((0.714, 0.745), (0.756, 0.745))]:
        arrow(ax, a, b, MUTED)
    box(ax, 0.35, 0.48, 0.30, 0.12, "RUN AUTHORITATIVE CHECKS", "Query the system of record -\nnot model self-confidence", edge=VIOLET, title_size=11, body_size=8)
    ax.plot([0.855, 0.855], [0.666, 0.635], color=VIOLET, lw=1.8)
    ax.plot([0.855, 0.69], [0.635, 0.635], color=VIOLET, lw=1.8)
    arrow(ax, (0.69, 0.635), (0.642, 0.608), VIOLET)
    ax.text(0.772, 0.652, "MANDATORY SET INCLUDED", color=VIOLET, fontsize=7.6, weight="bold", ha="center")

    outcomes = [
        (0.03, "ACT", "Selected checks valid;\nmodeled action loss <=\nabstention loss", GREEN),
        (0.275, "REFRESH", "Invalid state, policy,\nidentity, or scope evidence", CYAN),
        (0.52, "ASK", "Invalid authorization;\nrenew accountable\nauthority", AMBER),
        (0.765, "ABSTAIN", "Residual risk or mandatory\nchecks cannot be justified\nwithin budget", RED),
    ]
    branch_starts = [0.405, 0.47, 0.53, 0.595]
    for (x, title, body, color), start_x in zip(outcomes, branch_starts):
        box(ax, x, 0.20, 0.18, 0.16, title, body, edge=color, title_size=12, body_size=7.8)
        arrow(ax, (start_x, 0.468), (x + 0.09, 0.382), color, 1.7)
    bottom_statement(
        ax,
        0.115,
        "Every outcome is observable. Only ACT crosses the side-effect boundary.",
        fontsize=14,
    )
    footer(ax)
    save(fig, "03-raer-decision-protocol.png")


def results_tradeoff():
    with RESULTS.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    wanted = {r["policy"]: r for r in rows}
    policies = ["STATIC", "FIXED_0.35", "RAER_V1", "RAER_V2_OUT_OF_FOLD", "FIXED_0.20", "CONTRACT_ONLY", "FIXED_0.10", "ALWAYS_REFRESH"]

    fig, ax = plt.subplots(figsize=(12, 9), dpi=150)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    fig.subplots_adjust(left=0.10, right=0.96, bottom=0.12, top=0.78)
    fig.text(0.075, 0.955, "RAER v2 found a useful trade-off - and still failed its gate", color=INK, fontsize=25, weight="bold", va="top")
    fig.text(0.075, 0.875, "72 exposed design cases; 24 held-out cases remained sealed", color=INK, fontsize=12, va="top")
    fig.add_artist(Line2D([0.075, 0.155], [0.845, 0.845], transform=fig.transFigure, color=INK, lw=2.2, solid_capstyle="round"))
    fills = {
        "STATIC": "#222222",
        "FIXED_0.35": "#666666",
        "RAER_V1": "#A0A0A0",
        "RAER_V2_OUT_OF_FOLD": "#FFFFFF",
        "FIXED_0.20": "#4A4A4A",
        "CONTRACT_ONLY": "#888888",
        "FIXED_0.10": "#B8B8B8",
        "ALWAYS_REFRESH": "#E0E0E0",
    }
    markers = {
        "STATIC": "s",
        "FIXED_0.35": "D",
        "RAER_V1": "^",
        "RAER_V2_OUT_OF_FOLD": "o",
        "FIXED_0.20": "P",
        "CONTRACT_ONLY": "h",
        "FIXED_0.10": "v",
        "ALWAYS_REFRESH": "X",
    }
    for policy in policies:
        r = wanted[policy]
        x = float(r["mean_check_cost"])
        y = float(r["harmful_action_rate_on_invalid"])
        safe = float(r["safe_completion_rate_on_valid"])
        c = fills[policy]
        size = 170 + safe * 280
        ax.scatter(x, y, s=size, c=c, marker=markers[policy], edgecolor=INK, linewidth=2.6 if policy == "RAER_V2_OUT_OF_FOLD" else 1.4, alpha=1.0, zorder=3)
        label = policy.replace("RAER_V2_OUT_OF_FOLD", "RAER v2 OOF").replace("_", " ")
        dx, dy = (0.025, 0.025)
        if policy == "CONTRACT_ONLY": dy = -0.055
        if policy == "FIXED_0.10": dx, dy = (-0.32, 0.025)
        if policy == "ALWAYS_REFRESH": dx, dy = (-0.31, 0.04)
        if policy == "STATIC": dy = -0.06
        ax.text(x + dx, y + dy, label, color=INK, fontsize=10, weight="bold" if policy == "RAER_V2_OUT_OF_FOLD" else "normal")
    ax.set_xlim(-0.05, 1.62)
    ax.set_ylim(-0.05, 1.08)
    ax.set_xlabel("Mean validation cost  ->", color=INK, fontsize=12)
    ax.set_ylabel("Harmful-action rate on invalid cases  ->", color=INK, fontsize=12)
    ax.tick_params(colors=MUTED)
    for spine in ax.spines.values():
        spine.set_color(GRID)
    ax.grid(color=GRID, alpha=0.6, linewidth=0.8)
    ax.axvline(0.547, color=GREEN, alpha=0.25, lw=1)
    ax.axhline(0.311, color=GREEN, alpha=0.25, lw=1)
    ax.text(0.58, 0.87, "Lower-left is better\nonly if safe completion is preserved.", transform=ax.transAxes, color=INK, fontsize=13, weight="bold", bbox=dict(boxstyle="round,pad=.5", facecolor=PANEL, edgecolor=GRID))
    ax.text(0.58, 0.55, "RAER v2: harm 31.1% vs 40.0%; cost 0.547 vs 0.800\nBut safe completion was 92.6% vs required >=95%.\nDecision: FAIL_KEEP_HELD_OUT_SEALED", transform=ax.transAxes, color=INK, fontsize=12, bbox=dict(boxstyle="round,pad=.6", facecolor=PANEL, edgecolor=RED, linewidth=1.8))
    fig.text(0.075, 0.025, "Bubble size encodes safe-completion rate. Results are descriptive, not confirmatory.", color=MUTED, fontsize=9)
    save(fig, "04-safety-cost-tradeoff.png")


def assumptions_controls():
    fig, ax = setup_ax(
        "Eight assumptions that make context-switching agents unsafe",
        "Convert each hidden assumption into a runtime invariant or an explicit refusal path.",
    )
    pairs = [
        ("Memory is current", "Record source, version, time, validity window; revalidate at commit"),
        ("More context means safer", "Prefer action-relevant evidence; freshness and authority outrank volume"),
        ("High confidence = valid evidence", "Separate inference confidence from world-state validity"),
        ("Authorization is another feature", "Make authority non-fungible; mandate checks and ASK if revoked"),
        ("Tool success = intended outcome", "Verify postconditions in the authoritative system of record"),
        ("Retries are harmless", "Use idempotency, compare-and-set versions, and replay-safe effects"),
        ("All agents can share one context", "Use scoped evidence, least privilege, and handoff contracts"),
        ("A good average is enough", "Gate worst-domain completion, uncertainty, harm, cost, and authority"),
    ]
    y = 0.79
    for i, (assumption, control) in enumerate(pairs, 1):
        color = RED if i in (1, 4, 5) else AMBER
        ax.text(0.055, y, f"{i:02d}", color=color, fontsize=12, weight="bold", va="center")
        ax.text(0.105, y, assumption, color=INK, fontsize=9.6, weight="bold", va="center")
        arrow(ax, (0.40, y), (0.455, y), GREEN, 1.5)
        ax.text(0.48, y, control, color=MUTED, fontsize=8.8, va="center")
        ax.plot([0.05, 0.95], [y - 0.042, y - 0.042], color=GRID, lw=0.8)
        y -= 0.08
    bottom_statement(
        ax,
        0.12,
        "The safest agent is not the one that knows the most.\nIt is the one that knows what must be checked again.",
        fontsize=13.5,
    )
    footer(ax, "Engineering synthesis based on RAER v2 mechanisms, ablations, limitations, and integrity gates")
    save(fig, "05-assumptions-and-controls.png")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    context_lifecycle()
    architecture_extension()
    decision_loop()
    results_tradeoff()
    assumptions_controls()
    print("Rendered 5 LinkedIn-ready PNG assets in", OUT)
