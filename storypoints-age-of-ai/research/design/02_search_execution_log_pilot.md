# Gate 2 Search Execution Log — Pilot Runs

**Timezone:** Asia/Kolkata  
**Operator:** coordinating Codex agent; public-source query execution  
**Status:** pilot/query validation only; excluded from PRISMA counts

| Run ID | Date | Source/platform | Family | Literal query reference | Returned | Retrieval depth | Disposition |
|---|---|---|---|---|---:|---:|---|
| AX-P0-20260813 | 13 Aug 2026 | arXiv public Atom API | broad S1 pilot | Appendix AX-P0 | 643 | 5 | Precision failure; narrow before freeze |
| AX-S3-20260814 | 14 Aug 2026 | arXiv public Atom API | S3 | Appendix AX-S3 | 4 | 4 | Precise; full-export candidate pending sentinel test |
| AX-S4-20260814 | 14 Aug 2026 | arXiv public Atom API | S4 | Appendix AX-S4 | 4 | 4 | Precise complementary family |
| AX-S6-20260814 | 14 Aug 2026 | arXiv public Atom API | S6 | Appendix AX-S6 | 2 | 2 | Recall failure against known sentinel; revise |
| AX-S6R-20260814 | 14 Aug 2026 | arXiv public Atom API | revised S6 | Appendix AX-S6R | 29 | 10 | Sentinel-recall success; full-export candidate with expected pipeline-operation noise |
| AX-S5-20260814 | 14 Aug 2026 | arXiv public Atom API | S5 | Appendix AX-S5 | 142 | 5 | High-recall pilot; split into three subfamilies |
| AX-S5R-ATTEMPT-20260814 | 14 Aug 2026 | arXiv public Atom API | S5 review | Appendix AX-S5R | Not obtained | 0 | Public API returned `Rate exceeded`; no result count/export claimed |
| AX-S5T-ATTEMPT-20260814 | 14 Aug 2026 | arXiv public Atom API | S5 testing | Appendix AX-S5T | Not obtained | 0 | Public API timed out; no result count/export claimed |
| AX-S5S-ATTEMPT-20260814 | 14 Aug 2026 | arXiv public Atom API | S5 security | Appendix AX-S5S | Not obtained | 0 | Public API timed out; no result count/export claimed |
| AX-S6R-RETRY1-20260814 | 14 Aug 2026 | arXiv public Atom API | revised S6 | Appendix AX-S6R | 29 | 29 | Complete developmental export; 1 raw page; sentinel `2603.20028` retrieved; manifest SHA-256 `5e2b8e9e0497ec41f8095c5cc54363948572f74808222705676644eed9761051` |
| AX-S5R-RETRY1-20260814 | 14 Aug 2026 | arXiv public Atom API | S5 review | Appendix AX-S5R | 187 | 187 | Complete developmental export; 2 raw pages; sentinel `2606.26505` retrieved; manifest SHA-256 `79bc0ff650a16d5acb27fb4331940080fcf5a9533dd48856e3d96a21b90d70a6` |
| AX-S5T-RETRY1-20260814 | 14 Aug 2026 | arXiv public Atom API | S5 testing | Appendix AX-S5T | 394 | 394 | Complete developmental export; 4 raw pages; no registered sentinel; manifest SHA-256 `16de14545695bf78deb8a64e5cb2d4f50ac2171cf5402ae3e5795b7c1a6f3e84` |
| AX-S5S-RETRY1-20260814 | 14 Aug 2026 | arXiv public Atom API | S5 security | Appendix AX-S5S | 1,333 | 1,333 | Complete developmental export; 14 raw pages; no registered sentinel; manifest SHA-256 `c7898ce9cfd57a3404a5b5b0009aa38017ccc8614120a87a2124110ccd18b58c` |
| WEB-EVIDENCE-20260814 | 14 Aug 2026 | Primary-source discovery search | review/testing/rework parameters | Focused empirical search | N/A | 4 primary records opened | Added LP-008 through LP-011 candidates; no PRISMA count and no numerical calibration |
| OA-S3-20260815-PILOT1 | 15 Aug 2026 | OpenAlex API | S3 v0.1 | Open-index registry v0.1 | 1,491 API total | 100 | Intentionally capped; too broad; archived developmental diagnostic only |
| S2-S3-20260815-PILOT1 | 15 Aug 2026 | Semantic Scholar Academic Graph API | S3 v0.1 | Open-index registry v0.1 | 0 API total | 0 | Valid response but translation/recall failure; never absence evidence |
| CR-S3-20260815-PILOT1 | 15 Aug 2026 | Crossref REST API | S3 v0.1 | Open-index registry v0.1 | 163,615 API total | 100 | Intentionally capped; too broad; archived developmental diagnostic only |
| OA-S3R-20260815-PILOT1 | 15 Aug 2026 | OpenAlex API | refined S3 | Open-index registry v0.2 query text, but registry hash absent from run manifest | 134 API total | 100 | Diagnostic-only and incomplete; both positive HIE sentinels present, negative-boundary sentinel absent; 20-record appraisal is not freeze-ready |
| OA-S3R-20260815-PILOT2 | 15 Aug 2026 | OpenAlex API | refined S3 | Open-index registry v0.2, SHA-256 `6a90831f08ea139bb7a043ac5281262c464a3830eafccb2bf2cef6223571dd9a` | 134 | 134 | Complete developmental export; both positive sentinels retrieved and negative-boundary sentinel absent; prespecified 50-record appraisal found 13 likely relevant and 37 likely irrelevant (`26.0%`, Wilson 95% CI `15.87%–39.55%`). The v0.2 validator returns `freeze_ready=true`, but the Section 4.1 neutral/disconfirming sentinel class is still missing, so protocol acceptance remains pending |
| S2-S3R-20260815-PILOT2 | 15 Aug 2026 | Semantic Scholar Academic Graph | refined S3 | Open-index registry v0.2 | 15 | 15 | Complete developmental export; all 15 records appraised, 14 likely relevant and 1 likely irrelevant (`93.3%`, Wilson 95% CI `70.18%–98.81%`). The v0.2 validator returns `freeze_ready=true`, but the Section 4.1 neutral/disconfirming sentinel class is still missing |
| CR-S3R-20260815-PILOT2 | 15 Aug 2026 | Crossref REST API | refined S3 | Open-index registry v0.2 | 263,416 API total | 100 | Intentionally capped after one page; refined translation remains severely over-broad and incomplete; revise or split before any complete export |
| OA-S3R3-20260815-PILOT1 | 15 Aug 2026 | OpenAlex API | S3 v0.3 | Family-scoped registry SHA-256 `5f82bc8519fe6c64a5c78abef9b252229c12d2f8036e45848f43a5e5f1972e23` | 134 | 134 | Complete export; positive and neutral/disconfirming sentinel recall passed. Hash-seeded 50-record sample: 9 likely relevant, 39 likely irrelevant, 2 uncertain; burden 22.0% (Wilson 95% CI 12.75%–35.24%); boundary paper retrieved as a precision warning; query-level `freeze_ready=true` |
| S2-S3R3-20260815-PILOT1 | 15 Aug 2026 | Semantic Scholar Academic Graph | S3 v0.3 | Same family-scoped registry | 15 | 15 | Complete export; all 15 appraised, 14 likely relevant and 1 likely irrelevant; positive and neutral/disconfirming sentinel recall passed; query-level `freeze_ready=true` |
| OA-S8R6-20260816-FULL1 | 16 Aug 2026 | OpenAlex API | S8 v0.6 foundational comparison | Registry `s8_foundational_queries_v0.6.json` | 1,097 | 1,097 | Complete developmental export with publication-date ordering; five positive and two neutral/disconfirming sentinels recalled; deterministic 100-record appraisal 39 likely relevant, 9 uncertain, 52 likely irrelevant; `freeze_ready=true` |
| S2-S8R6-20260816-FULL1 | 16 Aug 2026 | Semantic Scholar Academic Graph | S8 v0.6 foundational comparison | Registry `s8_foundational_queries_v0.6.json` | 794 | 794 | Complete developmental export; five positive and two neutral/disconfirming sentinels recalled; deterministic 50-record appraisal 18 likely relevant, 3 uncertain, 29 likely irrelevant; `freeze_ready=true` |

No raw export is claimed for these pilots: the API output was inspected during query engineering but not archived as a complete paginated corpus. Consequently the `Returned` field is a reproducibility diagnostic only.

## Access-status ledger

| Source | Systematic status | Reason/action |
|---|---|---|
| arXiv | S5R/S5T/S5S and S6R complete developmental exports archived | Raw Atom pages, normalized CSV, manifests and checksums are under `gate2/output/development/arxiv/`. These remain query-engineering pilots; protocol freeze, deduplication, screening and the final update search remain pending |
| OpenAlex | Declared developmental controls through S8 are partly accepted; systematic corpus not frozen | S8 v0.6 retrieved 1,097/1,097 and passed balanced sentinels, 100-record appraisal, completeness, registry binding, and checksums. S1/S2 bounded integration and the final matrix remain pending |
| Semantic Scholar Academic Graph | Declared developmental controls through S8 are partly accepted; systematic corpus not frozen | S8 v0.6 retrieved 794/794 and passed balanced sentinels, 50-record appraisal, completeness, registry binding, and checksums. S1/S2 bounded integration and the final matrix remain pending |
| Crossref REST API | Refined S3 translation failed bounded precision feasibility | `CR-S3R` reported 263,416 results; the first 100 were archived under an explicit development cap. Do not paginate or freeze this translation; revise or split it |
| Scopus | Not executed | Authenticated institutional access and verifiable export unavailable |
| Web of Science Core Collection | Not executed | Authenticated institutional access and verifiable export unavailable |
| IEEE Xplore | Not executed | Database search/export not executed in an authenticated review session |
| ACM Digital Library | Not executed | Database search/export not executed in an authenticated review session |
| SpringerLink | Seed pages inspected only | No complete systematic query/export run |
| ScienceDirect | Not executed | No complete systematic query/export run |
| Google Scholar | Discovery only | Non-reproducible rankings; not a substitute for the executable open-index set or inaccessible subscription databases |

These prose statuses predate the machine-control template and do not themselves
satisfy its final-access record. Before protocol freeze, migrate each source to
`gate2/search_control_template.json` with an explicit access status. In
particular, “not executed” is not interchangeable with a verified access block:
it remains `not_assessed` unless a timestamped access attempt and reason exist.

## Gate consequence

Gate 2 executable searching is **advanced but incomplete**. No PRISMA identification number, eligible-study count, saturation claim, or final novelty conclusion may be produced from this log.
