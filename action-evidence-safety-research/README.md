# Action Evidence Safety Research

Research on whether consequential automated actions should proceed when their authorization, policy, identity, scope, or operational prerequisites may have changed.

This repository is a research monorepo: each study has an isolated protocol, benchmark, implementation, results, integrity record, and paper directory. The first study is **Risk-Adaptive Evidence Revalidation (RAER)**.

> **Double-blind review notice:** keep this repository **private** while an identified manuscript is under double-blind review. The `papers/thinkai-2026/` directory and repository license identify the author. Do not publish the repository or create a public Zenodo deposit until the venue permits deanonymization.

## Current study

RAER asks which action-specific evidence should be revalidated under a limited budget and when a system should act, request renewed authority, refresh state, or abstain.

The current RAER v2 result is a prospective negative design-stage result:

- 72 exposed design cases across six domains;
- 24 held-out cases remain sealed and are not in this repository;
- harmful action: 14/45 invalid cases (31.1%);
- safe completion: 25/27 valid cases (92.6%);
- the registered 95% safe-completion requirement was not met;
- no confirmatory or deployment-effectiveness claim is made.

See [`studies/raer/README.md`](studies/raer/README.md) for the scientific scope and reproducibility boundary.

## Repository layout

```text
.
├── studies/
│   └── raer/                 # Benchmark, evaluators, results, integrity records
├── papers/
│   ├── thinkai-2026/         # Identified manuscript and declarations
│   └── _template/            # Starting structure for later papers
├── docs/                     # Governance and repository conventions
├── scripts/                  # Repository-level verification
├── .github/workflows/        # Continuous integration
├── CITATION.cff
├── LICENSE
└── pyproject.toml
```

## Quick verification

Python 3.11 or later is recommended. The research evaluators and tests use only the Python standard library.

```bash
python3 scripts/verify_repository.py
python3 studies/raer/evaluation/test_raer_benchmark.py
python3 studies/raer/evaluation/v2/test_raer_v2_design.py
```

Or run:

```bash
make verify
```

## Reuse and citation

Code and repository-owned data are licensed under the MIT License unless a file states otherwise. Citation metadata are provided in [`CITATION.cff`](CITATION.cff). Referenced publications remain subject to their respective rights.

## Author

Shaik Khaja Nayab Rasool.

