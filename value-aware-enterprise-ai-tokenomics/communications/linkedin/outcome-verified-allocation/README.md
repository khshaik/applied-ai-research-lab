# Outcome-Verified Allocation Communication Package

This package explains why enterprise AI resource accounting must progress from metered consumption to verified incremental outcomes, fully loaded cost, uncertainty, current authority, and auditable allocation decisions.

## Contents

- [`LINKEDIN_CONSOLIDATED_ARTICLE.md`](LINKEDIN_CONSOLIDATED_ARTICLE.md): primary long-form technical article.
- [`drafts/LINKEDIN_ARTICLE.md`](drafts/LINKEDIN_ARTICLE.md): compact editorial article for publication channels with tighter length constraints.
- [`drafts/LINKEDIN_POST.md`](drafts/LINKEDIN_POST.md): LinkedIn post with a technical narrative, result boundary, and practitioner checklist.
- [`assets/`](assets/): six publication-ready diagrams used by the articles.
- [`scripts/build_visuals.py`](scripts/build_visuals.py): deterministic renderer for Figures 01–05.

## Figure provenance

Figures 01–03 and 05 are explanatory architecture diagrams rendered by the committed Python script. Figure 04 is analytical: it reads the committed [`calibration_gate.json`](../../../studies/ovar/calibration/results/calibration_v1.0/calibration_gate.json) and reports registered error rates. None of these figures changes a study artifact.

Figure 06 is an original AI-assisted conceptual overview produced for communication. It is not an analytical result. It summarizes the proposed journey from defining an investment decision through registering an outcome, capturing traces, verifying evidence, validating authority, issuing a receipt, and reassessing the decision.

## Rebuild

From the project root:

```bash
MPLCONFIGDIR=/tmp/ovar-mpl \
XDG_CACHE_HOME=/tmp/ovar-fontconfig \
python3 communications/linkedin/outcome-verified-allocation/scripts/build_visuals.py
```

The renderer writes Figures 01–05 to `communications/linkedin/outcome-verified-allocation/assets/`. It validates title spacing, common left alignment, box containment, and title/body separation before saving.

## Interpretation boundary

The communication package does not modify or supersede the frozen study. OVAR v1.0 reduced false-positive ROI classifications to 2/35 and produced no false-scale decisions on the constructed calibration, but it also produced two false stops, missed two expired approvals, and was dominated by outcome-flat throughout the registered burden range. The correct decision remains **STOP OVAR v1.0; do not construct or open a held-out benchmark for this version**.
