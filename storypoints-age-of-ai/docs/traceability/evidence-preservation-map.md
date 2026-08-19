# Evidence Preservation Map

## Principle

Canonical navigation is separated from immutable evidence. Root protocol files
and executable packages remain in their original locations because their paths
and bytes are referenced by frozen manifests and checksums.

| Scientific layer | Canonical navigation | Authoritative artifacts |
|---|---|---|
| Research framing | `research/studies/vdcm/protocol/` | Root `01_`–`04b_` records |
| Evidence-map method | `research/studies/vdcm/evidence-map/` | Frozen protocol package and `gate2/` controls |
| Systematic corpus | `research/studies/vdcm/evidence-map/` | `gate2/output/systematic/v1.3/20260816/` |
| Simulation | `research/studies/vdcm/simulation/` | `simulation/` and manuscript result package v2 |
| Claim confirmation | `research/studies/vdcm/integrity/releases/` | D17 pack plus accountable-author approval record |
| Manuscript | `papers/thinkai-2026/manuscript/` | Working source and versioned submission packages |
| Venue controls | `papers/thinkai-2026/venue/` | Conference-source notes and retained call image |
| Release | `papers/thinkai-2026/release/` | Approved hashes, QA record, and submission receipt |

## Preservation rules

1. Never overwrite a frozen evidence artifact; issue a superseding version.
2. Never move a checksum-bound artifact without a versioned migration manifest.
3. Keep developmental simulation evidence distinct from empirical validation.
4. Keep inaccessible reports as availability outcomes, not eligibility
   exclusions or negative evidence.
5. Keep anonymous and identified manuscripts in separate directories.
6. Record final release hashes before submission and archive the receipt after
   authorized submission.
