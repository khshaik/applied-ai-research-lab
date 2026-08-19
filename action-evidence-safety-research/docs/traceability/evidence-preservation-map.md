# Evidence preservation map

## Purpose

Documentation alone is not sufficient to preserve the research. The core scientific record is the combination of frozen protocols, executable implementations, raw outcomes, calculation summaries, integrity locks, closure decisions, and claim/citation ledgers.

## Preserve as immutable core findings

1. **Benchmark release:** the complete [`studies/raer/calibration/benchmark/release_v1.1/`](../../studies/raer/calibration/benchmark/release_v1.1/) folder.
2. **V1 evaluation record:** evaluator, tests, statistical plan, development/validation results, failure diagnosis, stop record, and closure manifest under [`studies/raer/evaluation/`](../../studies/raer/evaluation/) and [`studies/raer/integrity/`](../../studies/raer/integrity/).
3. **V2 prospective specification:** method specification, prospective plan, implementation, tests, and pre-execution lock under [`studies/raer/evaluation/v2/`](../../studies/raer/evaluation/v2/) and integrity.
4. **V2 calculations:** the complete [`results_design_v1.0/`](../../studies/raer/evaluation/v2/results_design_v1.0/) folder, especially row-level outcomes, fold selection, summaries, intervals, ablations, gate, and manifest.
5. **Research closure:** [`V2_DESIGN_CLOSURE_MANIFEST_v1.0.json`](../../studies/raer/integrity/V2_DESIGN_CLOSURE_MANIFEST_v1.0.json), including the explicit no-held-out-access boundary.
6. **Publication audit:** the claim-to-evidence ledger and citation verification log in [`studies/raer/integrity/`](../../studies/raer/integrity/).
7. **Submission lifecycle:** both manuscript-stage folders under [`papers/thinkai-2026/manuscript/`](../../papers/thinkai-2026/manuscript/), their hashes, checklists, QA record, declarations, and venue source notes.

## Preserve but do not publicly release

The investigator label vault, coordinator workbook, label-access log, and sealed held-out labels must remain outside Git. Their exclusion protects the registered boundary. Do not create empty or reconstructed substitutes that could be mistaken for released evidence.

## Interpretation safeguards

- Frozen raw results are append-only; corrections require a new version and explanation.
- A failed gate remains failed.
- Fitted all-design outcomes and ablations are descriptive and cannot replace out-of-fold endpoints.
- Synthetic reviewer agreement is AI-AI consistency, not human inter-rater reliability.
- Repository availability does not establish external validity, superiority, deployment readiness, or global novelty.
- Never access the held-out labels merely to improve a manuscript or acceptance probability.

For the claim-by-claim map, see [`papers/thinkai-2026/ARTIFACT_TRACEABILITY.md`](../../papers/thinkai-2026/ARTIFACT_TRACEABILITY.md).

