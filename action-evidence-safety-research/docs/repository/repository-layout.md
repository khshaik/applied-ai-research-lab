# Repository Layout

The repository is organized as a research monorepo so future papers can share governance without mixing experiments.

Each directory under `studies/` is an independent scientific unit. A mature study should contain:

```text
studies/<study-id>/
├── README.md
├── calibration/       # Reviewer-visible benchmark construction and scoring
├── evaluation/        # Frozen evaluators, protocols, tests, and results
├── integrity/         # Locks, closures, claim ledgers, and citation logs
└── restricted/        # README only; real restricted material stays outside Git
```

Each submission under `papers/` should contain its manuscript, declarations, venue notes, and—after the anonymity period—its repository/DOI record. Use `papers/_template/` for new submissions.

For submissions with double-blind review, separate lifecycle stages explicitly:

```text
papers/<venue>/manuscript/
├── initial-submission/       # Anonymous review source/PDF and pre-submission QA
└── camera-ready-submission/  # Identified post-acceptance starting package
```

Never place an identified file in the initial-submission folder. Repository-level traceability notes belong under `docs/traceability/`; venue-specific checklists and claim maps belong in the venue paper directory.

The historical `evaluation/restricted/` name within RAER contains only the already exposed development and validation labels. It is retained because frozen evaluator paths depend on it. Truly restricted files belong outside the repository and are blocked by `.gitignore` and repository verification.
