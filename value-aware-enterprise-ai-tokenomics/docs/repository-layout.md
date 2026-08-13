# Repository Layout

The repository is organized as a research monorepo so future papers can share governance without mixing experiments.

Each directory under `studies/` is an independent scientific unit. A mature study should contain:

```text
studies/<study-id>/
├── README.md
├── docs/              # Scope and scientific framing
├── method/            # Constructs, objectives, estimands, and causal model
├── novelty/           # Search protocol, source register, comparison, and decision
├── pilot/             # Engineering cases, implementation, review, tests, and results
├── calibration/       # Frozen design cases, policies, tests, results, and closure
├── publication/       # Figures, claim ledger, venue note, and package manifest
└── integrity/         # Study-wide research-integrity requirements
```

Each submission under `papers/` should contain its manuscript, declarations, venue notes, and—after the anonymity period—its repository/DOI record. Use `papers/_template/` for new submissions.

The OVAR `restricted/` directories contain only already exposed constructed design references needed to reproduce the pilot and calibration. They are not independent held-out data. Future truly restricted or held-out material must remain outside Git and is blocked by repository verification.
