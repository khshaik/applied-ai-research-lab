# Gate 2 Open Evidence Route Status

**Status date:** 16 August 2026  
**Route:** Targeted, access-constrained, AI-assisted open evidence map  
**Protocol state:** `draft_reconciled_unfrozen`; amendment 0.1 approved  
**Corpus state:** No systematic corpus has been frozen or screened

## 16 August 2026 checkpoint

- The accountable user approved minimum Route B through two consecutive
  `Continue` instructions after the explicit B05 approval request. The decision
  record is stored in `02e_b05_accountable_author_review.md`.
- S5T developmental controls are accepted for the two declared discovery
  sources: arXiv (394 records; 50-record appraisal burden 48.0%) and OpenAlex
  (137/137 records; 50-record appraisal burden 90.0%). These are query-control
  results only, not eligibility, PRISMA, or included-study counts.
- Repository verification passes 201 tests plus integrity and working-manuscript
  boundary checks.
- C04 is complete. Its OpenAlex control is accepted (19/19 complete; all four
  supporting/adverse sentinels recalled; all-record burden 52.6%). The
  1,333-record arXiv export recalls two positive and two neutral/disconfirming
  sentinels; its canonical 100-record appraisal found 6 likely relevant, 7
  uncertain, and 87 likely irrelevant records (13.0% burden). Exact seed,
  positions, ordered IDs, rederivation, and checksums passed independent audit.
- C05 is complete. The accepted arXiv control appraised all 29 records under
  the narrow S6 rule (10 likely relevant; 19 likely irrelevant); its rejected
  overbroad version is fail-closed. The accepted OpenAlex control retrieved
  231/231 records and its deterministic 50-record appraisal found 20 likely
  relevant, 6 uncertain, and 24 likely irrelevant records. The retrieved
  negative-boundary record is an explicit precision warning.
- C06 is complete across OpenAlex (49/49), Semantic Scholar (19/19), and arXiv
  (7/7). All records were appraised under the exact/close-overlap boundary and
  all required positive and disconfirming controls were recalled. The earlier
  arXiv DNS failure is retained as resolved provenance. Metadata-level overlap
  does not trigger the five-dimension stop rule, but final novelty remains
  deferred until systematic full-text and citation-network appraisal.
- The single active task is now C07: foundational comparison query controls.

## Decision and claims boundary

The discovery source set is OpenAlex, Semantic Scholar Academic Graph, and
arXiv under the approved 21-pair non-Cartesian matrix. Crossref is
DOI/bibliographic verification only. Scopus, Web of Science Core Collection,
IEEE Xplore, ACM Digital Library, SpringerLink, and ScienceDirect are recorded
as inaccessible because authorized institutional access is unavailable. Open
indexes are complementary sources and are not represented as coverage-equivalent
substitutes for those platforms.

The strongest permissible negative novelty statement, subject to completion of
the frozen review, is:

> No substantively duplicative framework was identified within the predeclared
> open scholarly indexes, repositories, and citation networks searched through
> the stated cutoff date.

The review must not claim that all relevant literature was searched, that its
coverage is exhaustive, or that no prior work exists.

## Completed controls

- Protocol, executable-search appendix, decision pack, logs, and source-access
  controls revised for the Open Evidence Route.
- Six inaccessible sources recorded with date, reason, and non-substitution
  treatment.
- Development-only exporters implemented for OpenAlex, Semantic Scholar, and
  Crossref, complementing the existing arXiv exporter.
- Raw-page preservation, normalized CSV output, atomic publication, pagination
  checks, retry limits, duplicate detection, stable-total checks, and SHA-256
  manifests implemented.
- Review workflow requires two isolated and blinded agent passes over identical
  inputs, a separate adjudicator, lawful full-text status, study-family
  consolidation, citation-chasing provenance, verified extraction, and final
  accountable-author citation confirmation.
- Peer-reviewed, preprint, secondary-study, and practitioner/grey evidence are
  maintained as distinct strata.
- Current integrated verification is reported by `make verify`; historical
  counts in this status file must not override the canonical `PROJECT_TODO.md`.

## Developmental discovery results

These figures are API query diagnostics only. They are not eligible-study,
deduplicated-study, systematic-review, or PRISMA counts.

| Source/query | Archived | API-reported total | Completeness | Decision |
|---|---:|---:|---|---|
| OpenAlex `OA-S3` | 100 | 1,491 | Intentionally capped | Too broad; refine and sentinel-test |
| Crossref `CR-S3` | 100 | 163,615 | Intentionally capped | Too broad; refine and sentinel-test |
| Semantic Scholar `S2-S3` | 0 | 0 | Complete response | Translation/recall failure; redesign query |
| Existing arXiv development families | 1,943 | 1,943 | Complete developmental exports | Deduplicate and screen only after approved rerun |

Refined S3 translations (`OA-S3R`, `S2-S3R`, and `CR-S3R`) and their
machine-readable appraisal controls are prepared. A capped OpenAlex diagnostic
retrieved 100 of an API-reported 134 records. Both positive HIE sentinels were
present and the negative-boundary sentinel was absent. A deterministic 20-record
query-precision appraisal classified 4 likely relevant, 15 likely irrelevant,
and 1 uncertain; relevant-plus-uncertain burden was 25.0% (Wilson 95% interval
11.19%-46.87%). The run remains diagnostic-only because its registry provenance
was not embedded, pagination was incomplete, and the required freeze sample is
50. The machine result correctly reports `freeze_ready=false`.

The refined Semantic Scholar S3 translation has since passed developmental
query controls. Crossref's broad S3 diagnostic was retired when amendment 0.1
limited Crossref to metadata verification; it is not a literature finding or a
discovery-search blocker.

## Next executable gate

1. Register positive, neutral, and disconfirming sentinel studies for each
   source/search-family translation.
2. Refine only the 21 declared source-family translations and measure sentinel
   recall plus sampled precision.
3. Approve and checksum literal queries only after every declared pair passes
   its predeclared query-quality threshold.
4. Freeze and archive the protocol, query registry, prompts, schemas, and
   approval record.
5. Rerun the approved open-source searches without developmental caps and
   archive complete exports.
6. Deduplicate records and consolidate report versions into study families.
7. Run two isolated agent screening passes and separate adjudication.
8. Retrieve lawful full text, perform appraisal and extraction, and complete
   backward/forward citation chasing until the stopping rule is met.
9. Reconcile the evidence-flow ledger and evidence matrix.
10. Request accountable-author confirmation only for the narrowed set of exact
    claims and citations intended for the manuscript.

## Support required

No database credentials or subscription access are required. No user action is
needed for the current query-engineering stage. Later support will be requested
only for:

- protocol-owner approval immediately before the systematic corpus is frozen;
- accountable-author verification of the final evidence claims and citations;
- reopening `THINKAI_2026_Gate2_Research_Workbook.xlsx` with the ChatGPT add-in
  if live workbook synchronization is desired.
