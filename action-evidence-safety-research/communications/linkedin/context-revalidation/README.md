# Context Revalidation Communication Package

This package explains why mutable evidence must be revalidated before a consequential automated action crosses its side-effect boundary.

## Contents

- [`LINKEDIN_CONSOLIDATED_ARTICLE.md`](LINKEDIN_CONSOLIDATED_ARTICLE.md): primary long-form article.
- [`drafts/`](drafts/): source article and post retained for editorial provenance.
- [`assets/`](assets/): publication-ready diagrams referenced by the Markdown articles.
- [`scripts/build_visuals.py`](scripts/build_visuals.py): deterministic renderer for Figures 01–05.

## Figure provenance

Figures 01–05 are architectural or analytical diagrams rendered by the committed Python script. Figure 04 reads the committed out-of-fold policy summary at `studies/raer/evaluation/v2/results_design_v1.0/oof_policy_summary.csv`.

Figure 06 is an original, AI-assisted conceptual overview created for communication. It is not an analytical result and must not be presented as empirical evidence. Its content summarizes the article's intent-to-evidence, pre-commit decision, execution, and reconciliation workflow.

## Rebuild

From the repository root:

```bash
python3 communications/linkedin/context-revalidation/scripts/build_visuals.py
```

The renderer writes Figures 01–05 to `communications/linkedin/context-revalidation/assets/` and performs text-containment and alignment checks before saving.

## Interpretation boundary

The communication package does not alter the frozen study. RAER v2 passed seven of eight prospective design gates but missed the safe-completion requirement; the held-out partition remains sealed.
