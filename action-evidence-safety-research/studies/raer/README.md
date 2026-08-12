# RAER Study

**Risk-Adaptive Evidence Revalidation (RAER)** studies budgeted revalidation of mutable prerequisites before consequential tool actions.

## Status

- v1 stopped before held-out evaluation after failing its registered validation gate.
- v2 passed seven of eight prospective design criteria but missed safe completion: 25/27 (92.6%) against a required 95%.
- The 24-case held-out partition remains sealed and is absent from this repository.
- The supported contribution is methodological and negative-result evidence, not validated effectiveness.

## Contents

- `calibration/benchmark/release_v1.1/`: reviewer-visible benchmark, scoring, review, adjudication, and provenance.
- `evaluation/`: v1 evaluator, design labels, statistical plan, tests, and v1 results.
- `evaluation/v2/`: v2 objective, prospective plan, implementation, tests, and design results.
- `integrity/`: stop records, locks, closure manifests, and manuscript evidence ledgers.
- `restricted/`: exclusion notice only.

## Tests

From the repository root:

```bash
python3 studies/raer/evaluation/test_raer_benchmark.py
python3 studies/raer/evaluation/v2/test_raer_v2_design.py
```

The included raw results are immutable historical outputs. Some internal closure records refer to deliberately excluded restricted artifacts; they are retained for provenance, not as a claim that every internal hash can be reconstructed from the public repository.

