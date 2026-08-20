# Narrowed Research Scope v0.2

## Working title

**From AI Usage to Auditable Outcomes: An Outcome-Evidence Ledger for Prospective AI Resource-Allocation Decisions**

## Primary problem statement

Enterprise AI telemetry can show who used a model, how many tokens or calls were consumed, and what the provider charged. It cannot by itself establish that the resulting work was correct, accepted, incremental to a credible baseline, causally attributable to AI assistance, or valuable enough to justify continued investment. Existing ROI frameworks organize investment reasoning, and existing observability systems instrument AI activity, but a measurement gap remains between the trace and an auditable outcome claim.

The research problem is:

> Organizations lack a prospectively tested evidence protocol for converting an attributed AI-workflow trace into a defensible incremental-value claim and using that claim in stop, revise, scale, and resource-allocation decisions under uncertainty.

## Primary research question

> Can an outcome-evidence ledger that requires a predefined outcome contract, independently reviewable evidence, a counterfactual baseline, fully loaded AI resource cost, and explicit attribution confidence reduce false ROI and incorrect scale/stop decisions compared with consumption-only, self-reported-value, and conventional cost-quality accounting?

## Secondary research questions

1. Which minimum evidence fields are necessary for reviewers to reproduce an AI value claim?
2. How often do token-, cost-, quality-, or self-report-based proxies disagree with verified incremental outcomes?
3. How sensitive are investment decisions to baseline choice, attribution confidence, delayed outcomes, rework, and human-review cost?
4. Does the ledger improve decision calibration without imposing unacceptable measurement cost or suppressing exploratory projects?
5. Can verified outcomes subsequently support hierarchical allocation better than raw usage while maintaining access and exploration floors?

## Candidate hypotheses

- **H1:** Consumption-only accounting produces a higher false-positive ROI classification rate than the outcome-evidence ledger.
- **H2:** Self-reported time/value accounting produces a higher false-scale rate than the outcome-evidence ledger.
- **H3:** Including rework, evaluation, and human-review cost materially changes net-value classification for a non-trivial share of episodes.
- **H4:** Explicit baseline and attribution-confidence requirements improve calibration of predicted versus realized value.
- **H5:** Outcome-linked allocation improves verified portfolio value over usage-proportional allocation subject to matched budget, risk, access, and exploration constraints.

These hypotheses are not frozen. Each requires a formal estimand, threshold, comparator, uncertainty method, sample justification, and decision consequence.

## Contribution boundary

The intended contribution is the design and prospective evaluation of the outcome-evidence ledger and its decision receipts. It is not a new observability platform, gateway, accounting standard, general ROI framework, token-routing algorithm, or vendor-credit policy.

## ThinkAI 2026 fit

The narrowed work remains aligned with Generative AI, Data Science & Analytics, and Optimization & Decision Making. A credible submission requires an implemented schema, a reproducible pilot or benchmark, prespecified baselines, and empirical decision-error results. A conceptual diagram alone is insufficient.

