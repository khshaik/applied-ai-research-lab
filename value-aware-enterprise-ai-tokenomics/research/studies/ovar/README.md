# OVAR Study

**Outcome-Verified AI Resource Allocation (OVAR)** studies whether enterprise AI consumption can be linked prospectively to auditable incremental outcomes and defensible investment actions.

## Status

- The 24-case pilot supports implementation feasibility only because it was not immutably locked before execution.
- The separate 48-case calibration passed five of nine registered criteria and failed its prospective gate.
- Outcome-flat dominated OVAR v1.0 across the registered measurement-burden range.
- The held-out stage was not authorized; no held-out benchmark was created or accessed.
- The supported contribution is a method, benchmark protocol, and preserved failure mechanism—not validated enterprise ROI improvement.

## Contents

- `docs/`: research concept and narrowed scope.
- `method/`: causal model, constructs, objective, and estimands.
- `novelty/`: formal search protocol, 39-source audit, comparison matrix, and novelty decision.
- `pilot/`: engineering cases, policy implementation, review workbook, tests, results, and closure.
- `calibration/`: 48 cases, construct review, reference adjudication, policies, tests, results, locks, and closure.
- `publication/`: figures, manuscript builder, claim ledger, venue note, checklist, and manifest.
- `integrity/`: study-wide integrity rules and supplementary artifact manifest.

## Tests

From the repository root:

```bash
node --test studies/ovar/pilot/tests/pilot_v1.0.test.mjs
node --test studies/ovar/calibration/tests/candidate_v1.0.test.mjs
node --test studies/ovar/calibration/tests/reference_labels_v1.0.test.mjs
node --test studies/ovar/calibration/tests/calibration_policies_v1.0.test.mjs
```

The `restricted/` filenames are retained because frozen scripts depend on them. Their contents are constructed pilot/calibration reference records that became design-exposed when those stages were executed; they are not a held-out test set. Future restricted or held-out data must remain outside Git.

The included results are immutable historical outputs. Re-execution is for verification only and must not be reported as a new confirmatory study.
