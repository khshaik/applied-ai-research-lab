# D05 frozen systematic-search execution

Status: **complete**  
Protocol: v1.3 frozen package  
Search cutoff: 2026-08-16  
Execution date: 2026-08-16

All 18 source-family searches in the frozen non-Cartesian matrix completed with
full pagination. The corpus contains 5,879 raw retrieval records: 2,490 from
eight OpenAlex runs, 1,439 from five Semantic Scholar runs, and 1,950 from five
arXiv runs. These are source-query retrieval counts, not unique studies,
eligible reports, or PRISMA inclusion counts.

The mandatory fresh OpenAlex S2 union (`OA-S2I3`) completed with 259 records;
no developmental S2 records were promoted. Earlier unauthenticated OpenAlex
HTTP-429 attempts are retained in the execution-status history and produced no
partial output. Authenticated execution read the key from the environment; the
credential was not written to request manifests or raw archives, and an
exact-value archive scan found zero matches.

The machine reconciliation verifies, for every run: systematic status,
complete pagination, frozen date bounds, literal query hash, registry hash,
acceptance-matrix-row hash, freeze-package hash, manifest sidecar, and immutable
output path. D06 may now normalize and deduplicate records. No eligibility,
screening, appraisal, study-family, novelty, or PRISMA claim is made at D05.

Canonical controls:

- `gate2/d05_execution_manifest_v1.3.json`
- `gate2/output/systematic/v1.3/20260816/d05_execution_status.json`
- `gate2/output/systematic/v1.3/20260816/d05_reconciliation.json`
