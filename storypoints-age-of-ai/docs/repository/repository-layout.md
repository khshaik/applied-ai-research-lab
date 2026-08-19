# Repository Layout

This repository follows the research-monorepo pattern used by the Action Evidence Safety project while preserving the path integrity of already checksummed artifacts.

## Canonical organization

```text
research/design/
├── README.md          # Phase index and relocation boundary
├── 01_*               # Concept framing
├── 02*                # Evidence-map protocol and governance
├── 03*                # Framework and construct design
├── 04*                # Simulation specification and governance
└── 05_*               # Developmental-result reconciliation

research/studies/vdcm/
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
├── governance/        # Research and public-release controls
├── repository/        # Structure and migration policy
├── status/            # Roadmap and completion checklist
├── traceability/      # Evidence-preservation map and release path
└── communications/
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
- `research/design/` numbered research records
- `artifacts/workbooks/` research workbooks

The numbered records were moved from the root to `research/design/` on
20 August 2026 under a checksum-preserving relocation. Frozen v1.3 package
bytes were not rewritten. Their legacy paths resolve through
`gate2.frozen_paths` and the versioned
[`RESEARCH_DESIGN_RELOCATION_2026-08-20.json`](../traceability/RESEARCH_DESIGN_RELOCATION_2026-08-20.json)
record.

## Migration rule

A compatibility path may move only when all of the following are satisfied:

1. a versioned migration manifest lists old path, new path, and pre/post SHA-256;
2. every internal reference is updated in one change set;
3. the full test and repository-verification suites pass;
4. affected immutable artifacts are superseded, never overwritten;
5. preregistration or protocol deviations are recorded explicitly;
6. the Excel status ledger is synchronized after the migration.

The completed relocation satisfies this rule through a versioned path map,
byte-level hashes, reference repair, and full repository verification. The
study directories remain the durable scientific navigation layer, while
`research/design/` is now the canonical home for the numbered design record.

## Generated and restricted material

- Developmental outputs remain under `gate2/output/development/` and `simulation/output/development/`.
- Production outputs may appear only after the pre-lock checker returns `ready_to_open`.
- Real organizational data, production seeds, participant identifiers, and sealed evaluation values stay outside Git.
- `research/studies/vdcm/restricted/` contains only an exclusion notice.
- Communication assets are derived explanatory material. They do not modify
  frozen research artifacts and must preserve the D17 claim boundary.
