# Gate 2 Review Logs Template

Use these logs only after Gate 2 protocol v1.3 is separately approved and
frozen. Pilot searches must remain labelled as pilot searches and must not be
merged into PRISMA counts without being rerun under the frozen protocol. The
discovery sources are OpenAlex, Semantic Scholar Academic Graph, and arXiv under
the approved non-Cartesian source-family matrix. Crossref is metadata
verification only; the six subscription sources documented below are coverage
limitations, not searched sources.

## 0. Source-access assessment log

An assessment date may document a user-confirmed lack of institutional authorization; it must not be represented as a platform search-attempt timestamp.

| Source | Assessment date | Access status | Assessment basis | Reason | Next action | Fallback role | Search coverage claimed? |
|---|---|---|---|---|---|---|---|
| Scopus | 2026-08-15 | `blocked_authentication` | User confirmed authorization unavailable | No authorized institutional session | Reassess only if lawful access changes | `non_equivalent_supplement` | No |
| Web of Science Core Collection | 2026-08-15 | `blocked_authentication` | User confirmed authorization unavailable | No authorized institutional session | Reassess only if lawful access changes | `non_equivalent_supplement` | No |
| IEEE Xplore | 2026-08-15 | `blocked_authentication` | User confirmed authorization unavailable | Authenticated/export access unavailable | Reassess only if lawful access changes | `non_equivalent_supplement` | No |
| ACM Digital Library | 2026-08-15 | `blocked_authentication` | User confirmed authorization unavailable | Authenticated/export access unavailable | Reassess only if lawful access changes | `non_equivalent_supplement` | No |
| SpringerLink | 2026-08-15 | `blocked_authentication` | User confirmed authorization unavailable | Authenticated/export access unavailable | Reassess only if lawful access changes | `non_equivalent_supplement` | No |
| ScienceDirect | 2026-08-15 | `blocked_authentication` | User confirmed authorization unavailable | Authenticated/export access unavailable | Reassess only if lawful access changes | `non_equivalent_supplement` | No |
| OpenAlex | 2026-08-16 | `accessible` | Complete developmental exports and checksum controls validated; current S2 fresh-union attempt rate-limited | 2026-08-16 | Rerun frozen queries at D05 with bounded retry | `none` | D03 approval pending |
| Semantic Scholar Academic Graph | 2026-08-16 | `accessible` | Complete developmental exports and checksum controls validated | 2026-08-16 | Rerun frozen queries at D05 | `none` | D03 approval pending |
| Crossref REST API | 2026-08-15 | `accessible` | Developmental metadata API retrieval succeeded |  | Verify candidate/included DOI metadata; no discovery role | `none` | No systematic coverage role |
| arXiv | 2026-08-15 | `accessible` | Developmental API exports only |  | Rerun approved families after freeze | `none` | No systematic coverage yet |

## A. Search execution log

| Search run ID | Date/time/timezone | Operator type/ID | Evidence stream | Database/source | Platform | Search family | Run status | Exact platform-accepted query | Fields searched | Date/language/type filters | Results returned | Complete export file/SHA-256 | PRISMA eligible? | Access-attempt/failure evidence | Fallback role | Notes/deviation ID |
|---|---|---|---|---|---|---|---|---|---|---|---:|---|---|---|---|---|
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

Allowed run statuses are `translation_draft`, `syntax_validated`,
`pilot_excluded`, `systematic_executed`, `export_verified`,
`refresh_executed`, and `failed_attempt`. A pilot or failed attempt must have
`PRISMA eligible? = false`. Do not use zero where a result count was not
obtained. Maintain the separate source-access fields defined in
`gate2/search_control_template.json`; a fallback must be labelled `none`,
`discovery_only`, or `non_equivalent_supplement`.

## B. Record and study-family log

| Record ID | Study-family ID | DOI | arXiv ID | Normalized title | First author | Year | Version/status | Evidence destination | Source database(s) | Duplicate of | Retained version | Deduplication rationale |
|---|---|---|---|---|---|---:|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |  |  |  |  |  |

Allowed evidence destinations are `scholarly_primary_peer_reviewed`, `scholarly_primary_preprint`, `scholarly_secondary`, `practitioner_grey`, and `method_reference`. Assign exactly one per retained report; related versions may share a study family but not duplicate a study-family inclusion count.

## C. Title/abstract screening log

Allowed decisions: `Include`, `Exclude`, `Unclear`.

| Record ID | Agent 1 decision/reason/confidence | Agent 1 ID + model/prompt version | Agent 2 decision/reason/confidence | Agent 2 ID + model/prompt version | Conflict? | Final research decision | Adjudicator/source-grounded notes | Author verification status |
|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |  |

## D. Full-text screening log

Use exactly one primary exclusion code for excluded full texts: E1–E10 from the protocol. Add a secondary note only when useful.

| Record ID | Full text obtained? | Agent 1 decision/code/confidence | Agent 2 decision/code/confidence | Final research decision | Primary exclusion code | Secondary explanation | Novelty-threatening exclusion? | Source-grounded audit complete? | Author verification status |
|---|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |  |  |

## E. Quality-appraisal log

| Study-family ID | Record/version used | Appraisal form | Reviewer/agent provenance | Applicable points | Points awarded | Percentage | Critical flaw? | Evidence band | Conflict disclosed? | Reproducibility materials? | Appraisal notes/source locators |
|---|---|---|---|---:|---:|---:|---|---|---|---|---|
|  |  |  |  |  |  |  |  |  |  |  |  |

## F. Extraction and accountable-author citation-confirmation log

| Extraction ID | Claim ID | Study-family ID | Record/version used | Extractor agent provenance | Verifier agent provenance | Full-text URL/checksum | Exact source locator | Data nature (observed/self-reported/modeled/conceptual/mixed) | Verification status | Citation key | Accountable author ID | Author source check (pending/confirmed/rejected) | Confirmation time | Corrections/notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

## G. Protocol-deviation log

| Deviation ID | Date | Original rule | Revised rule | Reason | Records affected | Before/after outcome-bearing review? | Bias impact assessment | Author/protocol-owner approver |
|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |  |

## G2. Citation-chasing and lawful full-text log

| Round ID | Seed study-family IDs | Direction (backward/forward) | Source | Date | Records inspected | New records before deduplication | New study families after deduplication | New eligible study families | Full-text route attempted/outcome | Stopping-rule status | Notes |
|---|---|---|---|---|---:|---:|---:|---:|---|---|---|
|  |  |  |  |  |  |  |  |  |  |  |  |

Lawful full-text outcomes are `open_publisher`, `repository`, `author_manuscript`, `preprint`, `legitimately_held_access`, or `retrieval_unavailable`. Do not bypass access controls or infer full-text content from metadata/abstracts.

## H. PRISMA count ledger

Generate from the append-only record-level event ledger after the final update
search. Do not enter aggregate counts manually. An empty ledger means “no
observations”, not zero search results. Final counts must satisfy identification,
screening, retrieval, and eligibility flow-conservation checks.

| Flow stage | Count | Derivation/query | Verified by | Date |
|---|---:|---|---|---|
| Records identified from scholarly databases |  |  |  |  |
| Records identified from other methods |  |  |  |  |
| Duplicate records removed |  |  |  |  |
| Records screened |  |  |  |  |
| Records excluded at title/abstract |  |  |  |  |
| Full texts sought |  |  |  |  |
| Full texts unavailable |  |  |  |  |
| Full texts assessed |  |  |  |  |
| Full texts excluded by E1–E10 |  |  |  |  |
| Scholarly primary studies included |  |  |  |  |
| Scholarly secondary studies included |  |  |  |  |
| Practitioner/grey records included |  |  |  |  |

PRISMA is used here as a transparent flow-reporting structure, not as evidence
that the access-constrained search was exhaustive. Keep peer-reviewed,
preprint, secondary-study, and practitioner/grey totals separate and identify
whether each displayed count refers to reports or study families.

The workbook-independent normative artifacts are
`evidence_review/schemas/review_bundle.schema.json`,
`evidence_review/templates/review_bundle.template.json`, and
`evidence_review/workflow.py`. This Markdown table is a viewing aid; the
validated bundle and derived output are authoritative.

## I. Novelty-adjudication log

Use `Yes`, `Partial`, `No`, or `Unclear` for criteria.

| Study-family ID | Prospective estimate | Multi-role capacity | Requirements-to-release/UAT | Readiness evidence | Actual Story Point comparison | Multi-team field study | Out-of-sample prediction/calibration | Overlap risk | Remaining distinction | Adjudicated research decision | Author verification status |
|---|---|---|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |  |  |  |  |
