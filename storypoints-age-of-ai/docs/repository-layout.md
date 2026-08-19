# Repository Layout

This repository follows the research-monorepo pattern used by the Action Evidence Safety project while preserving the path integrity of already checksummed artifacts.

## Canonical organization

```text
studies/vdcm/
├── README.md
├── protocol/          # Indexes for concept, constructs, causal model, and preregistration
├── evidence-map/      # Search-family registries, source procedures, screening workflow
├── simulation/        # Route B design, model and output map
├── integrity/         # Status, lock, claim and release boundaries
└── restricted/        # Exclusion notice only; real restricted material stays outside Git

papers/thinkai-2026/
├── README.md
├── venue/             # Authoritative venue records and unresolved requirements
├── manuscript/
│   ├── initial-submission/
│   └── identified-author/
├── declarations/
└── release/           # G06/G07 approvals, hashes and receipt

docs/
└── traceability/      # Evidence-preservation map and release path

communications/
└── verified-delivery-capacity/
    ├── README.md                       # Package index and interpretation boundary
    ├── END_TO_END_WORKFLOW.md          # Detailed operating-model explanation
    ├── LONG_FORM_NARRATIVE.md          # Platform-neutral article
    ├── SHORT_FORM_SUMMARY.md           # Concise publication copy
    ├── EDITORIAL_AND_RELEASE_GUIDE.md  # Claim, accessibility, and release controls
    ├── assets/                         # Editable SVG, high-resolution PNG, checksums
    └── scripts/                        # Deterministic local renderer
```

## Import-stable compatibility layer

The following paths remain canonical implementation paths until the protocol, code-release, and production-output contracts are jointly migrated and rehashed:

- `gate2/`
- `evidence_review/`
- `simulation/`
- `tests/`
- root `01_` through `04b_` research records
- root research workbooks

This is intentional, not unfinished housekeeping. These paths appear in test fixtures, manifests, SHA-256 records, simulation preregistration, and workbook links. A mechanical move would silently invalidate research provenance.

## Migration rule

A compatibility path may move only when all of the following are satisfied:

1. a versioned migration manifest lists old path, new path, and pre/post SHA-256;
2. every internal reference is updated in one change set;
3. the full test and repository-verification suites pass;
4. affected immutable artifacts are superseded, never overwritten;
5. preregistration or protocol deviations are recorded explicitly;
6. the Excel status ledger is synchronized after the migration.

Until then, the study directories act as the durable scientific navigation layer and the root packages remain the executable layer.

## Generated and restricted material

- Developmental outputs remain under `gate2/output/development/` and `simulation/output/development/`.
- Production outputs may appear only after the pre-lock checker returns `ready_to_open`.
- Real organizational data, production seeds, participant identifiers, and sealed evaluation values stay outside Git.
- `studies/vdcm/restricted/` contains only an exclusion notice.
- Communication assets are derived explanatory material. They do not modify
  frozen research artifacts and must preserve the D17 claim boundary.
