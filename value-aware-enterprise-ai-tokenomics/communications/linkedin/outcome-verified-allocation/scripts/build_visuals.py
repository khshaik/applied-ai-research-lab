from __future__ import annotations

import json
from pathlib import Path
from textwrap import fill

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


OUT = Path(__file__).resolve().parents[1] / "assets"
PROJECT = Path(__file__).resolve().parents[4]
RESULTS = PROJECT / "studies/ovar/calibration/results/calibration_v1.0/calibration_gate.json"

WHITE = "#FFFFFF"
INK = "#000000"
PANEL = "#F5F5F5"
LIGHT = "#E8E8E8"
MID = "#8A8A8A"
CONTENT_LEFT = 0.055


def setup(title: str, subtitle: str, *, figsize=(14, 9)):
    fig, ax = plt.subplots(figsize=figsize, dpi=180)
    fig.patch.set_facecolor(WHITE)
    ax.set_facecolor(WHITE)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    title_artist = ax.text(
        CONTENT_LEFT, 0.965, title, ha="left", va="top", fontsize=26,
        weight="bold", color=INK,
    )
    subtitle_artist = ax.text(
        CONTENT_LEFT, 0.875, subtitle, ha="left", va="top", fontsize=12.5,
        color=INK,
    )
    ax.plot([CONTENT_LEFT, 0.16], [0.835, 0.835], color=INK, lw=2.2)
    ax._title_pair = (title_artist, subtitle_artist)
    ax._boxes = []
    ax._aligned = [title_artist, subtitle_artist]
    return fig, ax


def box(
    ax, x, y, w, h, title, body="", *, fill_color=WHITE,
    title_size=12, body_size=8.5, pad=0.018,
):
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.010,rounding_size=0.015",
        linewidth=1.7, edgecolor=INK, facecolor=fill_color,
    )
    ax.add_patch(patch)
    title_artist = ax.text(
        x + pad, y + h - 0.03, title, ha="left", va="top",
        fontsize=title_size, weight="bold", color=INK, linespacing=1.2,
    )
    artists = [title_artist]
    if body:
        body_artist = ax.text(
            x + pad, y + h - 0.088, body, ha="left", va="top",
            fontsize=body_size, color=INK, linespacing=1.45,
        )
        artists.append(body_artist)
    ax._boxes.append((title.replace("\n", " "), patch, artists))
    return patch


def arrow(ax, start, end, *, dashed=False, width=1.7):
    ax.add_patch(FancyArrowPatch(
        start, end, arrowstyle="-|>", mutation_scale=13, linewidth=width,
        color=INK, linestyle="--" if dashed else "-",
    ))


def footer(ax, text="Source: OVAR v1.0 repository artifacts; constructed calibration, not field validation"):
    artist = ax.text(
        CONTENT_LEFT, 0.025, text, ha="left", va="bottom",
        fontsize=8.2, color=INK,
    )
    ax._aligned.append(artist)


def statement(ax, y, text, *, fontsize=13.5):
    artist = ax.text(
        CONTENT_LEFT, y, text, ha="left", va="top", fontsize=fontsize,
        weight="bold", color=INK, linespacing=1.25,
    )
    ax._aligned.append(artist)


def save(fig, name: str):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for ax in fig.axes:
        title, subtitle = ax._title_pair
        if title.get_window_extent(renderer).y0 - subtitle.get_window_extent(renderer).y1 < 12:
            raise ValueError(f"{name}: insufficient title/subtitle spacing")
        lefts = [a.get_window_extent(renderer).x0 for a in ax._aligned]
        if max(lefts) - min(lefts) > 1.2:
            raise ValueError(f"{name}: misaligned title/footer/statement")
        for label, patch, artists in ax._boxes:
            pb = patch.get_window_extent(renderer)
            for artist in artists:
                tb = artist.get_window_extent(renderer)
                if not (
                    tb.x0 >= pb.x0 + 5 and tb.x1 <= pb.x1 - 5
                    and tb.y0 >= pb.y0 + 5 and tb.y1 <= pb.y1 - 5
                ):
                    raise ValueError(f"{name}: text exceeds box '{label}'")
            if len(artists) == 2 and artists[0].get_window_extent(renderer).overlaps(artists[1].get_window_extent(renderer)):
                raise ValueError(f"{name}: title/body overlap in '{label}'")
    fig.savefig(OUT / name, facecolor=WHITE, bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)


def problem_and_lifecycle():
    fig, ax = setup(
        "The accounting gap: usage is observable; incremental value is not",
        "A resource trace becomes decision evidence only after outcome, counterfactual, cost, attribution, and authority checks.",
    )
    stages = [
        (0.045, "1  CONSUME", "Models · tokens\ntools · retries\nlatency · provider cost"),
        (0.245, "2  PRODUCE", "Draft · forecast\nrecommendation\naction · escalation"),
        (0.445, "3  VERIFY", "Outcome contract\nevidence · baseline\nmeasurement window"),
        (0.645, "4  VALUE", "Attributed benefit\nfull cost · harm\nuncertainty interval"),
        (0.845, "5  DECIDE", "STOP · REVISE\nCONTINUE_PILOT\nSCALE · INDETERMINATE"),
    ]
    width = 0.145
    for x, title, body in stages:
        box(ax, x, 0.56, width, 0.22, title, body, fill_color=PANEL, title_size=10.2, body_size=7.5, pad=0.014)
    for idx in range(len(stages) - 1):
        x1 = stages[idx][0] + width + 0.012
        x2 = stages[idx + 1][0] - 0.012
        arrow(ax, (x1, 0.67), (x2, 0.67))
    ax.text(0.11, 0.49, "DIRECTLY METERED", ha="center", fontsize=9, weight="bold", color=INK)
    ax.text(0.70, 0.49, "MUST BE ESTABLISHED", ha="center", fontsize=9, weight="bold", color=INK)
    ax.plot([0.045, 0.37], [0.465, 0.465], color=INK, lw=1.2)
    ax.plot([0.445, 0.965], [0.465, 0.465], color=INK, lw=1.2)
    box(
        ax, 0.18, 0.22, 0.64, 0.16,
        "THE PROBLEM IS AN INFERENCE GAP",
        "Telemetry can prove consumption and provenance. It cannot, by itself, prove the no-AI counterfactual,\n"
        "incremental benefit, complete cost, current authorization, or a justified portfolio action.",
        title_size=12.5, body_size=9.5,
    )
    statement(ax, 0.145, "Do not optimize the meter before proving what the meter is economically connected to.")
    footer(ax)
    save(fig, "01-problem-and-lifecycle.png")


def ledger_architecture():
    fig, ax = setup(
        "OVAR is an evidence architecture, not a token-price dashboard",
        "Five linked records turn distributed AI activity into a reproducible allocation receipt.",
    )
    records = [
        (0.05, "CONSUMPTION", "Provider/model\nCalls + token classes\nTools + latency + charge"),
        (0.235, "WORK", "Organization + team\nProject + workflow + episode\nAccountable owner"),
        (0.42, "OUTCOME", "Predefined metric + window\nThreshold + evidence\nCounterfactual baseline"),
        (0.605, "VALUE", "Attributed benefit\nFully loaded cost + harm\nUncertainty interval"),
        (0.79, "ALLOCATION", "Constraints + authority\nAction + reasons\nInput/rule/receipt hashes"),
    ]
    w = 0.15
    for x, title, body in records:
        box(ax, x, 0.58, w, 0.22, title, body, fill_color=PANEL, title_size=10.1, body_size=7.1, pad=0.012)
    for idx in range(4):
        arrow(ax, (records[idx][0] + w + 0.01, 0.69), (records[idx + 1][0] - 0.01, 0.69))
    box(ax, 0.05, 0.29, 0.27, 0.16, "SYSTEMS OF RECORD", "Telemetry · finance · workflow\nquality · risk · authorization", title_size=11, body_size=8.7)
    box(ax, 0.37, 0.29, 0.27, 0.16, "POLICY ENGINE", "Whitelisted information set\nregistered rules · deterministic receipt", title_size=11, body_size=8.7)
    box(ax, 0.69, 0.29, 0.26, 0.16, "GOVERNANCE OUTPUT", "Decision + evidence status\nreason codes · next checkpoint", title_size=11, body_size=8.7)
    arrow(ax, (0.33, 0.37), (0.36, 0.37))
    arrow(ax, (0.65, 0.37), (0.68, 0.37))
    arrow(ax, (0.505, 0.46), (0.505, 0.555), dashed=True)
    statement(ax, 0.18, "Traceability explains where resources went. OVAR asks whether the resulting claim deserves action.")
    footer(ax)
    save(fig, "02-value-ledger-and-governance.png")


def decision_protocol():
    fig, ax = setup(
        "The decision protocol must preserve uncertainty",
        "A missing baseline or expired authority is not a low score; it changes which actions are admissible.",
    )
    box(ax, 0.05, 0.66, 0.18, 0.14, "REGISTER", "Outcome · threshold\nwindow · baseline · owner", fill_color=PANEL, title_size=11, body_size=8)
    box(ax, 0.29, 0.66, 0.18, 0.14, "RECONCILE", "Trace-to-work linkage\nfully loaded cost", fill_color=PANEL, title_size=11, body_size=8)
    box(ax, 0.53, 0.66, 0.18, 0.14, "ESTIMATE", "Attribution · harm\nnet-value interval", fill_color=PANEL, title_size=11, body_size=8)
    box(ax, 0.77, 0.66, 0.18, 0.14, "CONSTRAIN", "Evidence sufficiency\nrisk · authorization", fill_color=PANEL, title_size=11, body_size=8)
    for a, b in [((0.24, 0.73), (0.28, 0.73)), ((0.48, 0.73), (0.52, 0.73)), ((0.72, 0.73), (0.76, 0.73))]:
        arrow(ax, a, b)
    box(ax, 0.33, 0.46, 0.34, 0.11, "ADMISSIBLE-ACTION GATE", "Evaluate evidence, interval, current scope, and authority", title_size=10.2, body_size=7.7)
    arrow(ax, (0.86, 0.645), (0.65, 0.53))
    outcomes = [
        (0.035, "STOP", "Negative value, harm, or\nmaterially invalid authority"),
        (0.225, "REVISE", "Correct design, evidence,\nscope, or cost boundary"),
        (0.415, "CONTINUE\nPILOT", "Positive signal; limited\nevidence or maturity"),
        (0.605, "SCALE", "Positive margin within\ncurrent authorization"),
        (0.795, "INDETERMINATE", "Evidence cannot support\na defensible classification"),
    ]
    starts = [0.40, 0.45, 0.50, 0.55, 0.60]
    for (x, title, body), start in zip(outcomes, starts):
        box(ax, x, 0.20, 0.15, 0.15, title, body, title_size=9.5, body_size=7.1)
        arrow(ax, (start, 0.445), (x + 0.075, 0.365))
    statement(ax, 0.12, "The policy must be able to say “not yet knowable” without laundering uncertainty into ROI.")
    footer(ax)
    save(fig, "03-ovar-decision-protocol.png")


def calibration_result():
    data = json.loads(RESULTS.read_text())
    rows = {row["policy"]: row for row in data["policy_summaries"]}
    policies = ["USAGE_ONLY", "SELF_REPORTED_VALUE", "COST_QUALITY", "OUTCOME_FLAT", "OVAR_LEDGER"]
    labels = ["Usage only", "Self-report", "Cost-quality", "Outcome-flat", "OVAR"]
    metrics = ["false_positive_roi", "false_scale", "false_stop", "authorization_violation"]
    metric_labels = ["False-positive ROI", "False scale", "False stop", "Authorization violation"]
    fig, ax = plt.subplots(figsize=(14, 9), dpi=180)
    fig.patch.set_facecolor(WHITE)
    ax.set_facecolor(WHITE)
    x = list(range(len(policies)))
    width = 0.18
    hatches = ["", "///", "\\\\", "xx"]
    for j, (metric, label) in enumerate(zip(metrics, metric_labels)):
        values = [100 * rows[p]["rates"][metric] for p in policies]
        positions = [i + (j - 1.5) * width for i in x]
        ax.bar(positions, values, width, label=label, facecolor=WHITE, edgecolor=INK, linewidth=1.4, hatch=hatches[j])
    ax.set_title("OVAR reduced proxy errors—but failed its complete prospective gate", loc="left", fontsize=25, weight="bold", color=INK, pad=42)
    ax.text(0, 1.045, "Forty-eight constructed calibration cases; rates use registered denominators.", transform=ax.transAxes, fontsize=12.5, color=INK, va="bottom")
    ax.set_xticks(x, labels, fontsize=10)
    ax.set_ylabel("Error rate (%)", fontsize=11)
    ax.set_ylim(0, 108)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(INK)
    ax.tick_params(colors=INK)
    ax.grid(axis="y", color=LIGHT, linewidth=0.8)
    ax.legend(frameon=False, ncols=2, loc="upper right", fontsize=9)
    fig.text(
        0.125, 0.075,
        "OVAR: 5/9 criteria passed · STOP v1.0 · no held-out construction · "
        "outcome-flat dominated across every registered burden weight",
        fontsize=10.2, weight="bold", color=INK,
    )
    fig.text(0.125, 0.025, "Source: calibration_gate.json · prospective negative result · not a field-effect estimate", fontsize=8.2, color=INK)
    fig.subplots_adjust(left=0.10, right=0.97, top=0.80, bottom=0.20)
    fig.savefig(OUT / "04-calibration-gate-result.png", facecolor=WHITE, bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)


def assumptions_and_controls():
    fig, ax = setup(
        "Replace convenient assumptions with explicit controls",
        "Each inference shortcut has a corresponding evidence or governance requirement.",
    )
    headers = ["ASSUMPTION TO AVOID", "WHY IT FAILS", "CONTROL TO REQUIRE"]
    xs = [0.055, 0.365, 0.68]
    widths = [0.25, 0.255, 0.265]
    for x, w, header in zip(xs, widths, headers):
        ax.text(x, 0.79, header, ha="left", va="top", fontsize=10.5, weight="bold", color=INK)
        ax.plot([x, x + w], [0.765, 0.765], color=INK, lw=1.5)
    rows = [
        ("More tokens mean more value", "Consumption measures activity,\nnot the counterfactual outcome", "Predefined outcome contract\n+ credible baseline"),
        ("Provider bill is full cost", "Review, integration, governance,\nand rework may dominate", "Visible fully loaded\ncost components"),
        ("Quality or adoption proves ROI", "A good output may not change\na business outcome", "Independent evidence\n+ attribution interval"),
        ("Approval text is current authority", "Time, revocation, jurisdiction,\nand scope are stateful", "Structured authorization\n+ deterministic date/scope checks"),
        ("A favorable metric passes the method", "Safety and burden failures can be\nhidden by selective reporting", "Conjunctive prospective gate\n+ immutable decision receipt"),
    ]
    y = 0.67
    for left, middle, right in rows:
        box(ax, xs[0], y, widths[0], 0.085, fill(left, 33), title_size=9.5, pad=0.014)
        box(ax, xs[1], y, widths[1], 0.085, middle, title_size=8.7, pad=0.014)
        box(ax, xs[2], y, widths[2], 0.085, right, fill_color=PANEL, title_size=8.7, pad=0.014)
        arrow(ax, (xs[0] + widths[0] + 0.011, y + 0.043), (xs[1] - 0.011, y + 0.043), width=1.2)
        arrow(ax, (xs[1] + widths[1] + 0.011, y + 0.043), (xs[2] - 0.011, y + 0.043), width=1.2)
        y -= 0.115
    statement(ax, 0.09, "Governance is valuable only when it reduces decision error enough to justify its own burden.", fontsize=13)
    footer(ax)
    save(fig, "05-assumptions-and-controls.png")


def main():
    problem_and_lifecycle()
    ledger_architecture()
    decision_protocol()
    calibration_result()
    assumptions_and_controls()
    print(f"Rendered 5 figures to {OUT}")


if __name__ == "__main__":
    main()
