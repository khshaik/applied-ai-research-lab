# D06 normalization and report-level deduplication

Status: **complete**  
Pipeline: `d06-normalize-deduplicate/1.0.0`  
Input: 5,879 frozen D05 retrieval occurrences

D06 produced 3,962 canonical report records and 1,917 duplicate-removal
decisions. The conservation identity `5,879 = 3,962 + 1,917` passes. There are
1,250 multi-record clusters and 2,712 singletons; the largest cluster contains
10 occurrences across repeated source-family retrievals.

Exact match bases were applied in the frozen hierarchy:

- DOI: 1,042 removals;
- arXiv identifier or arXiv-related DOI: 326;
- normalized title, first author and year: 500;
- exact repeated provider identity across query batches: 49.

The process preserves every occurrence, source ID, query family, retrieval
batch, normalized identifier, representative-selection basis and
removed-to-retained decision. Representatives are selected deterministically
by metadata completeness, abstract coverage, identifier availability, source
metadata richness and stable record ID.

No fuzzy title, semantic-similarity, shared-author-only, or inferred
preprint-to-published merge was permitted. Those relationships require D07
study-family review. D06 therefore establishes report-level uniqueness only;
it makes no eligibility, study-family, peer-review, quality, novelty or PRISMA
inclusion judgment.

Canonical artifacts are under
`gate2/output/systematic/v1.3/20260816/d06/`, with file-level SHA-256 hashes in
`d06_manifest.json`.
