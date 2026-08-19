# THINKAI 2026 Research Paper — Canonical Completion Checklist

Last cross-check: 2026-08-19  
Controlling route: minimum defensible Route B  
Status: active  
Protocol: v1.3 `frozen` by checksum-bound D03/D04 record  
Active task: F01/F04/F06 — finalize and package the manuscript  

Current scope-control artifacts:

- [`research/design/02d_minimum_route_protocol_amendment_draft.md`](../../research/design/02d_minimum_route_protocol_amendment_draft.md)
- [`gate2/minimum_route_scope.draft.json`](../../gate2/minimum_route_scope.draft.json)
- [`research/design/02e_b05_accountable_author_review.md`](../../research/design/02e_b05_accountable_author_review.md)

This is the single source of truth for work remaining before submission. If a
task is not listed here, it is not part of the current completion route unless
it is added through the change-control rule below.

## Fixed execution order

To prevent focus drift, complete the remaining work in this order. Do not start
a later phase when an earlier phase supplies its inputs, except for the
explicitly safe manuscript and venue preparation already underway.

1. **Approve scope:** B05.
2. **Finish query controls:** C01–C09.
3. **Freeze the evidence-map method:** D01–D04, including D03 approval.
4. **Execute and synthesize the evidence map:** D05–D16.
5. **Confirm material citations:** D17 and F07.
6. **Finalize scientific narrative:** F01, F04, and F06.
7. **Apply venue format and release QA:** G01–G05.
8. **Approve and submit:** G06–G07.

Simulation work E01–E06 is complete for the current Route B claims. Do not
restart production-lock or Route A work unless change control explicitly
upgrades the paper route.

## Status legend

- `[x]` completed and verified
- `[~]` in progress or partially complete
- `[ ]` not started
- `[H]` accountable-author/user approval required
- `[F]` future work; explicitly outside the current paper

## A. Foundations already completed

- [x] A01 — Research problem, purpose, scope, and novelty pivot.
- [x] A02 — VDCM and RSDRI construct architecture.
- [x] A03 — Causal model, boundaries, and testable propositions.
- [x] A04 — DES prototype, five comparator families, developmental scenarios,
  sensitivity, ablations, parameter recovery, and negative-result handling.
- [x] A05 — Gate, readiness, evidence, calendar, dependency, queue, and output
  engineering contract.
- [x] A06 — Open-evidence retrieval, checksum, review-workflow, screening,
  adjudication, extraction, and PRISMA-ledger tooling.
- [x] A07 — S3 estimation-family query development accepted for OpenAlex and
  Semantic Scholar.
- [x] A08 — S4/S5R review-burden query development accepted for OpenAlex,
  Semantic Scholar, and mapped arXiv.
- [x] A09 — Repository structure, governance, confidentiality controls, and CI.
- [x] A10 — Current automated verification: 244 tests passing, plus repository
  and working-manuscript boundary checks through `make verify`.

## B. Scope control — do before further broad searching

- [x] B01 — Draft a formal pre-freeze protocol amendment for the minimum
  defensible paper route.
- [x] B02 — In that amendment, freeze the evidence roles as follows, effective
  only after B05 approval:
  - S3: estimation/Story Point predecessor and comparator evidence;
  - S4/S5R: human review/cognitive-demand evidence;
  - S5T: testing and QA assurance evidence;
  - S5S: security-assurance evidence;
  - S6: lifecycle, coordination, and delivery-flow evidence;
  - S7: exact novelty/duplication search;
  - S8: foundational validity and comparator evidence;
  - S1/S2: bounded integrative searches, not a full source-by-family Cartesian
    matrix;
  - Crossref: DOI and metadata verification, not broad absence evidence.
- [x] B03 — Define the source allocation for each retained family using
  OpenAlex, Semantic Scholar, and/or arXiv according to actual source
  capability; do not require every family in every source.
- [x] B04 — Freeze the maximum claims, effective only after B05 approval:
  - design-science framework;
  - targeted AI-assisted open evidence map;
  - verified developmental simulation prototype and scenario evidence;
  - no empirical organizational superiority or validated cognitive-load claim.
- [x] B05 — Accountable author approved amendment 0.1 on 16 August 2026. The
  actual decision evidence (“Continue” twice after the explicit approval
  request), timestamp, matrix acceptance, and claims boundary are archived in
  [`research/design/02e_b05_accountable_author_review.md`](../../research/design/02e_b05_accountable_author_review.md).

Exit condition: approved, dated, versioned amendment with no unresolved scope
language. No systematic corpus is created before this exit condition.

## C. Finish developmental query controls

- [x] C01 — S3 controls are complete for OpenAlex and Semantic Scholar; the
  retained source allocation is recorded in amendment 0.1 and protocol v1.3.
- [x] C02 — S4/S5R controls are complete for OpenAlex, Semantic Scholar, and
  arXiv; the retained allocation is recorded in the approved matrix.
- [x] C03 — S5T testing/QA controls are accepted for both declared sources.
  arXiv: 394 records, all four positive/disconfirming sentinels recalled,
  50-record appraisal burden 48.0%. OpenAlex: 137/137 complete, all required
  positive/disconfirming sentinels recalled, 50-record burden 90.0%. Both are
  developmental `freeze_ready=true`, not systematic-corpus results.
- [x] C04 — S5S security assurance: OpenAlex control accepted (19/19 complete;
  four supporting/adverse sentinels recalled; all-record appraisal burden
  52.6%). The existing 1,333-record arXiv export recalls two positive and two
  neutral/disconfirming sentinels. Its canonical 100-record appraisal contains
  6 likely relevant, 7 uncertain, and 87 likely irrelevant records (13.0%
  relevant-plus-uncertain; Wilson 95% interval 7.76%–20.98%). Exact seed,
  positions, ordered IDs, rederivation, and checksums passed independent audit.
  These remain query controls, not screening or PRISMA counts.
- [x] C05 — S6 lifecycle/team delivery controls passed independent audit.
  arXiv: full 29/29 appraisal under the narrow S6 rule found 10 likely relevant
  and 19 likely irrelevant records (34.48% burden); the overbroad v1 is
  explicitly rejected. OpenAlex: 231/231 complete, four required
  positive/neutral sentinels recalled, and deterministic 50-record appraisal
  found 20 likely relevant, 6 uncertain, and 24 likely irrelevant records
  (52.0% burden). The retrieved negative-boundary record is retained as a
  precision warning. These are query controls, not screening or PRISMA counts.
- [x] C06 — S7 exact/close novelty controls completed across all three declared
  sources. OpenAlex: 49/49 appraised (18 likely relevant, 11 uncertain).
  Semantic Scholar: 19/19 appraised (12 likely relevant, 3 uncertain). arXiv:
  7/7 appraised (5 likely relevant, 2 uncertain). All required positive and
  neutral/disconfirming controls were recalled; the OpenAlex/Semantic Scholar
  negative boundary was absent. Exact seeds, positions, IDs, raw exports,
  checksums, and rederivations pass. Metadata does not show one framework line
  satisfying all five stop-rule dimensions, but final novelty remains deferred
  until systematic full-text, family consolidation, and citation chasing.
- [x] C07 — S8 foundational comparison controls accepted for both declared
  sources. OpenAlex: 1,097/1,097 complete with deterministic publication-date
  ordering; 100-record appraisal found 39 likely relevant, 9 uncertain, and 52
  likely irrelevant (48.0% burden). Semantic Scholar: 794/794 complete;
  50-record appraisal found 18 likely relevant, 3 uncertain, and 29 likely
  irrelevant (42.0% burden). Both recall all five positive and both
  neutral/disconfirming sentinels; the non-software workload boundary is
  absent. Little's original queueing identity is a targeted method/reference
  anchor, not a broad-discovery recall sentinel. Exact seeds, positions, raw
  pages, registry bindings, rederivations, and checksums pass.
- [x] C08 — Bounded integrative coverage completed under the approved minimal
  allocation. S1 Semantic Scholar: 331/331 complete; deterministic 50-record
  appraisal found 16 likely relevant, 3 uncertain, and 31 likely irrelevant
  records (38.0% burden), with all four positive/neutral controls recalled.
  S2 OpenAlex: the 257/257 discovery component produced 38 likely relevant, 6
  uncertain, and 6 likely irrelevant records (88.0% burden). A predeclared
  exact-title recovery for the sole missed orchestration sentinel was verified
  against two immutable OpenAlex records in the accepted S6 export after the
  fresh union rerun exhausted bounded HTTP-429 retries. This is explicitly an
  accepted bounded integrative union—not a fresh OA-S2I3 execution or
  systematic corpus—and D05 still requires a frozen rerun.
- [x] C09 — Final machine-readable and human-readable source-family acceptance
  matrix completed for all 18 pairs in the approved non-Cartesian allocation.
  Every row records query reference/hash, execution mode, cutoff, retrieved
  count, completeness, sentinel status, appraisal statistics, artifact hashes,
  disposition, and mandatory D05 rerun. All rows are complete and accepted;
  S2 alone is explicitly labeled `accepted_bounded_integrative_union`.

Exit condition: every family/source pair declared in the amended matrix has a
complete, checksummed, accepted developmental control or a documented exclusion.

## D. Freeze and execute the evidence map

- [x] D01 — Remove protocol placeholders and reconcile the protocol, query
  registries, screening prompts, schemas, and reporting boundary.
- [x] D02 — Record the initial cutoff (2026-08-16), mandatory pre-submission
  refresh, and the six inaccessible subscription-source limitations.
- [x] D03 — Accountable author explicitly approved protocol v1.3 on 16 August
  2026 using the requested approval phrase.
- [x] D04 — Exact approved bytes, approval record, freeze package, and SHA-256
  sidecars archived. Any change now requires formal deviation control.
- [x] D05 — All 18 frozen systematic searches completed and reconciled: eight
  OpenAlex runs (2,490 raw records), five Semantic Scholar runs (1,439), and
  five arXiv runs (1,950), totaling 5,879 raw retrieval records. The mandatory
  fresh S2 execution completed. Every run is fully paginated and bound to the
  frozen query, registry, matrix row, cutoff, and package hashes. Developmental
  outputs remain outside the corpus. The OpenAlex credential was supplied only
  through the environment and an exact-value archive scan found zero matches.
- [x] D06 — Normalized all 5,879 frozen retrieval occurrences and performed
  exact report-level deduplication in the frozen order: provider identity, DOI,
  arXiv/related DOI, and normalized title–first-author–year. The result contains
  3,962 canonical report records and 1,917 duplicate removals across 1,250
  multi-record clusters, with complete provenance and count conservation. No
  fuzzy or semantic-similarity merge was allowed; version relationships remain
  for D07.
- [x] D07 — Consolidated 3,962 canonical reports into 3,930 candidate study
  families. Twenty-three multi-report families link 55 reports; 3,907 are
  singletons. All 39 metadata-level version candidates have explicit decisions
  (34 consolidate, five keep separate), every report maps exactly once, no
  candidate is unresolved, and the immutable artifacts pass checksum and
  conservation verification. These are screening units, not eligibility or
  PRISMA inclusion decisions.
- [x] D08 — Ran isolated Agent A and Agent B title/abstract screening on the
  same 3,930-family, 40-shard checksum-bound packet. Both passes validate as
  complete and blinded. Agent concordance is 2,686/3,930 (68.35%); 2,616
  unambiguous consensus decisions are retained and 1,314 disagreements or
  unclear decisions are routed to D09. This is agent concordance, not human
  inter-rater reliability.
- [x] D09 — A distinct agent/context adjudicated all 1,314 disagreements or
  unclear cases without majority voting: 255 include and 1,059 exclude, with no
  unresolved decision. Combined with 2,616 unambiguous consensus decisions,
  2,076 families proceed to D10 and 1,854 are excluded at title/abstract. The
  3,930-family total and all checksums reconcile. D08 agreement remains labelled
  agent concordance, not human inter-rater reliability.
- [x] D10 — Reconciled all 2,076 title/abstract inclusions: 1,605 lawfully open,
  signature-verified PDFs; 34 access-blocked/paywalled; 436 lawful full texts
  not retrieved after documented attempts; and one with no lawful location
  identified. Every PDF has a source basis, byte count and SHA-256. No landing
  page, login response or metadata record was treated as full text, and no
  access control was bypassed. The pre-final timestamp-label correction is
  explicitly documented and checksum-bound.
- [x] D11 — Completed full-text eligibility for all 2,076 retained families:
  570 included, 1,034 excluded with E1–E10 reasons, and 472 unavailable.
  Two isolated agent passes were reconciled; 357 disagreements were separately
  adjudicated. A deterministic 100-item consensus-inclusion audit found 57
  false inclusions, triggering the predeclared full re-review of all 1,096
  consensus inclusions. That re-review retained 487 and excluded 609, agreed
  with the audit sample on 100/100 items, and is checksum-bound. Agent agreement
  is not reported as human inter-rater reliability. One AES-encrypted,
  non-English peripheral report remains unavailable; no package was installed.
- [x] D12 — Appraised all 570 eligible studies using the frozen §13 forms.
  Two partitioned primary appraisals were independently cross-audited; only 3
  matched on every criterion, so a separate source-grounded adjudicator resolved
  all 567 disputes rather than averaging scores. Final bands are 75 high, 272
  moderate, and 223 low/contextual; eight critical flaws remain included but are
  restricted to contextual evidentiary weight. Agent reproducibility is not
  human appraisal reliability, and technical-quality evidence is not treated as
  cognitive-workload validation.
- [x] D13 — Extracted and distinctly verified a 570-family evidence matrix with
  1,367 source-located findings, including 653 verified quantitative findings.
  A partition asymmetry exposed an exactly-one-finding completeness defect;
  the affected 285 studies were independently re-extracted, adding 679 material
  findings across 274 studies and removing 198 generic/non-result statements.
  No study currently satisfies all five novelty stop-rule dimensions for the
  same planning use. All findings remain pending D17 accountable-author citation
  confirmation before manuscript use.
- [x] D14 — Conduct backward and forward citation chasing until the declared
  stopping rule is met; pass new records through the same workflow.
  Round 1 OpenAlex is complete for 512/570 seeds. The immutable Semantic
  Scholar fallback resolved 26/58 OpenAlex-unresolved seeds and contributed
  803 relationships plus 567 new deduplicated candidates. The completed,
  checksum-bound rate-aware recovery over the 30 API-failure seeds resolved 16,
  confirmed seven exact-title no-matches, and left seven API failures. It
  retrieved 588 relationships across 533 unique related records; two
  relationship calls remain API failures. The two prior
  exact-title no-matches were
  reconciled to unique frozen D06 OpenAlex IDs (`W7164784501`, `W7132946893`);
  their checksum-bound OpenAlex supplement records zero indexed backward or
  forward edges at the 2026-08-16 cutoff. Frozen public identifiers preserve
  local identity reconciliation for all 570 families. Citation retrieval now
  remains pending for five unresolved recovery seeds; the two failed
  relationship calls were recovered in the checksum-bound supplement. A dedicated revalidation has confirmed all 13 formerly
  ambiguous empty relationship responses as valid empty
  relationship sets (zero recovered edges), with checksummed response
  envelopes; that ambiguity is closed. Do not close D14 or claim a complete
  round until the seven unresolved seed calls and two relationship calls are
  retrieved and validated, or the protocol's prospective resource-cap path is
  approved.
  The 5,530 OpenAlex and 567 Semantic Scholar new-candidate occurrences have
  been checksum-validated and conservatively consolidated into 6,017 candidate
  families (80 exact duplicate occurrences merged; no fuzzy matching). The
  immutable 61-shard screening packet is validated, and isolated title/abstract
  passes A and B completed over the byte-identical local population. Pass A:
  1,800 include / 2,319 exclude / 1,898 unclear; pass B: 1,060 include /
  3,978 exclude / 979 unclear. Both controller validations and checksum
  sidecars pass. Reconciliation produced 2,496 unambiguous consensus decisions
  and 3,521 disagreement-or-unclear cases; the separately isolated adjudication
  resolved all 3,521 cases (332 include / 3,189 exclude). The checksum-validated
  final ledger contains 1,017 title/abstract inclusions and 5,000 exclusions,
  with no unresolved decision. Concordance (44.7%) is reported only as AI-agent
  concordance, not human inter-rater reliability. Lawful full-text retrieval for
  the 1,017 inclusions is in progress. The local inventory contains 137 arXiv
  identifiers, 875 DOI routes, four record URLs, and one record without a
  retrieval identifier; frozen metadata supplied 322 families with lawful PDF
  locations. A checksum-bound OpenAlex DOI-only discovery pass matched 690/690
  records and identified 113 additional explicitly open-access PDF routes.
  That append-only v2 ledger covered 435 families. A subsequent checksum-bound
  Semantic Scholar batch-metadata pass queried 577 unresolved DOI identifiers
  and found 226 additional explicit HTTPS `openAccessPdf` routes. The immutable
  v3 ledger therefore covers 661 families; 356 have no explicit open route. A
  hardened 10-family pilot produced three incomplete/non-PDF
  responses, one clean static PDF, and six quarantined PDFs containing URI
  hyperlink actions but no exact JavaScript, launch, embedded-file, rich-media,
  or additional-action names. The approved project-local sanitizer uses the
  checksum-pinned pure-Python pypdf 6.16.1 wheel plus its checksum-pinned
  typing_extensions 4.16.0 runtime dependency. Its synthetic URI-removal test
  passes. All 661 lawful routes have now been attempted: 73 direct static PDFs,
  271 action-bearing quarantined PDFs, 269 invalid/non-PDF responses,
  thirty-nine HTTP failures, and nine network/policy failures. Three hundred
  and thirty-seven of the 344 actual PDFs have
  checksum-verified, action-free derivatives and page-numbered static text
  covering 6,799 pages / 27,114,693 characters. Seventy-two invalid lone-surrogate
  text code points were replaced with the explicit Unicode replacement
  character and counted. Seven malformed sources remain fail-closed after the
  isolated sanitization worker rejected them; they are not evidence.
  All originals remain unchanged. Source, derivative, text, and dependency
  checksums reconcile. CPU, output-size, file-descriptor, and wall limits are
  enforced per parser subprocess; macOS rejected lowering RLIMIT_AS, and that
  platform limitation is recorded. The dependency/sanitization blocker is
  closed. Retrieval controller v1.2 uses resumable 25-family checkpoints with
  concurrency capped at three unique-family public requests; original
  quarantined PDFs remain excluded from evidence use. The final checksum-bound
  disposition ledger conserves all 1,017 families: 337 screenable static full
  texts, seven sanitization failures, 269 invalid/non-PDF responses, 39 HTTP
  failures, nine network/policy failures, and 356 without a lawful route. The
  checksum-identical 337-family full-text eligibility packet is complete across
  seven shards. Isolated Agent A (250 include / 86 exclude / 1 unclear) and the
  accepted replacement Agent B pass (221 include / 116 exclude) are complete
  and checksum-valid. AI-agent decision concordance was 221/337 (65.6%): 178
  consensus includes and 43 consensus excludes. A separate adjudicator resolved
  all 116 disagreement-or-unclear cases (34 include / 82 exclude). The immutable
  final full-text ledger conserves all 1,017 families: 212 included, 125
  excluded after full-text assessment, and 680 unavailable/not assessed. The
  unavailable group remains an availability outcome, not an eligibility
  exclusion, quality judgment, or novelty finding. Final reconciliation,
  adjudication, ledger checksums, and targeted D14 tests pass. Quality appraisal
  and evidence extraction are complete for all 212 initial D14 inclusions: the
  final appraisal ledger contains 20 high, 121 moderate and 71 low/contextual
  studies; the final extraction ledger contains 931 exact-page findings and 90
  quantitative findings. A final literal-excerpt audit repaired 916 whitespace-
  only PDF extraction differences before freezing the ledger. The recovered
  relationship supplement produced 54 candidates, consolidated to 33 unique
  records; dual screening and adjudication retained 11. Nine lawful PDFs were
  sanitized into action-free static text (199 pages), and two isolated full-text
  passes included all nine. Separate quality adjudication classified four
  moderate and five low/contextual reports with no predefined critical flaw.
  Recovery extraction produced 45 page-supported findings, including 26
  independently verified owned-result quantitative findings; all 45 novelty
  dimensions remain not met and all nine same-planning-use judgments remain no.
  A final bounded retry attempted all five persistent Semantic Scholar failures;
  all five remain checksum-recorded API failures. The accountable author approved
  the prospective resource cap on 2026-08-19; D14 is checksum-closed with 221
  included citation-chasing families and no family satisfying the five-dimension
  same-planning-use duplication stop rule.
- [x] D15 — Reconciled records, reports, and study families into the final
  study-flow ledger: 791 included families, 2,343 findings and 769 quantitative
  findings across separately conserved systematic-search and citation streams.
- [x] D16 — Produced the normalized v2 evidence synthesis, overlap matrix,
  evidence bands, material-citation candidates, and bounded novelty conclusion.
  D16 is publication-eligible within the D17-confirmed claim boundaries.
- [x] D17 — Accountable author confirmed material claims CL-001 through CL-010
  on 2026-08-19 as bounded in the checksum-bound confirmation pack. The
  separate approval record preserves the original pack unchanged.

Exit condition: final checksummed evidence bundle validates with no unresolved
records, citations, flow counts, or extraction fields.

## E. Simulation evidence for this paper

- [x] E01 — Amend the simulation-method wording to classify current outputs as
  developmental/illustrative scenario evidence, not a locked empirical test.
- [x] E02 — Re-run the checked-in developmental pipeline from declared seeds and
  verify manifests/checksums reproduce. Two fresh current-code runs are
  byte-identical; the prior stale outputs were retired in
  [`simulation/output/development/reproducibility_audit_20260815.json`](../../simulation/output/development/reproducibility_audit_20260815.json).
- [x] E03 — Reconcile the 264-run scenario results, four mechanism ablations,
  comparator results, parameter-recovery results, and negative findings. See
  [`research/design/05_developmental_simulation_reconciliation.md`](../../research/design/05_developmental_simulation_reconciliation.md).
- [x] E04 — Produce manuscript-ready result tables and figures with explicit
  synthetic-data labels and uncertainty. Current package:
  [`papers/thinkai-2026/results/developmental_simulation_v2/`](../../papers/thinkai-2026/results/developmental_simulation_v2/).
- [x] E05 — Complete a parameter-use table distinguishing literature-supported,
  preregistered design, and illustrative Class-I values. See
  [`papers/thinkai-2026/manuscript/tables/parameter_use_table.md`](../../papers/thinkai-2026/manuscript/tables/parameter_use_table.md).
- [x] E06 — State prohibited interpretations: no human cognitive-load validity,
  causal gate effect, organizational ROI, or universal superiority.

Exit condition: every reported simulation number is reproducible and tied to a
manifest, while every limitation is stated in the manuscript.

## F. Manuscript — begin in parallel after B01

- [x] F01 — Froze the title, contribution statement, research questions, paper
  type, and scientific boundaries on 2026-08-19 in
  [`papers/thinkai-2026/MANUSCRIPT_SCIENTIFIC_FREEZE.md`](../../papers/thinkai-2026/MANUSCRIPT_SCIENTIFIC_FREEZE.md).
- [x] F02 — Draft stable sections immediately. A controlled working draft now
  exists at
  [`papers/thinkai-2026/manuscript/manuscript_working_draft.md`](../../papers/thinkai-2026/manuscript/manuscript_working_draft.md):
  - introduction and problem statement;
  - related-work positioning;
  - evidence-map method;
  - VDCM/RSDRI framework and constructs;
  - causal/queueing model;
  - simulation design and comparators;
  - threats, ethics, limitations, and Route A future work.
- [x] F03 — Create the framework, causal-model, lifecycle, simulation-flow, and
  evidence-flow figures. SVG and 300-DPI PNG assets are checksummed in
  [`papers/thinkai-2026/figures/`](../../papers/thinkai-2026/figures/README.md).
- [x] F04 — Populated the D15/D16 evidence-map flow, appraisal, coverage,
  overlap, and bounded novelty results after D17 confirmation.
- [x] F05 — Populate simulation results only after E03–E05. The working draft
  now uses only the reconciled manifest `0.2.0-development` and reporting
  package v2.
- [x] F06 — Completed discussion, organizational-use guidance, limitations,
  conclusion, abstract, and keywords from the frozen results.
- [x] F07 — Claim-to-evidence ledger and fail-closed manuscript verifier are in
  place; all ten material claims are accountable-author confirmed within their
  D17 wording and locator boundaries.
- [x] F08 — Working AI-assistance disclosure, research-ethics statement, and
  data/code availability statement are prepared under
  [`papers/thinkai-2026/declarations/`](../../papers/thinkai-2026/declarations/).

Exit condition: complete manuscript with no unsupported claims, unresolved
placeholders, or unverified references.

## G. Publication and submission quality gates

- [~] G01 — Confirm the current THINKAI/Springer template, page limit, required
  sections, anonymization rules, and submission deadline with an authoritative
  venue record. Dates, prior CCIS history, Springer author/AI/accessibility
  controls, and unresolved portal requirements are recorded in
  [`papers/thinkai-2026/VENUE_REQUIREMENTS.md`](../../papers/thinkai-2026/VENUE_REQUIREMENTS.md);
  the 2026 page limit and anonymization rule remain unavailable.
- [~] G02 — Anonymous references, equations, figures, tables, captions,
  keywords, and declarations are formatted; identified author metadata and
  final venue confirmation remain pending.
- [~] G03 — Anonymous-review DOCX/PDF v0.2 are generated and visually verified;
  the identified-author variant awaits accountable-author metadata.
- [~] G04 — Automated working/release manuscript hard stops are implemented in
  [`scripts/verify_manuscript.py`](../../scripts/verify_manuscript.py). Final
  citation/DOI, language, duplication-risk, and rendered-artifact checks remain
  after the evidence map and venue formatting are complete.
- [~] G05 — Anonymous DOCX/PDF were rendered and all 15 pages visually
  inspected with no clipping, overflow, unreadable figures, broken references,
  or pagination defects. Repeat after venue confirmation and for the identified
  package.
- [H] G06 — Accountable author performs final scientific, citation, authorship,
  disclosure, and submission approval.
- [H] G07 — Submit through the authorized venue account and archive the exact
  submitted package and receipt.

Exit condition: submission receipt archived and submitted files hash-match the
approved release package.

## H. Explicitly outside the current completion route

- [F] H01 — Prospective multi-team Route A validation with genuine practitioners.
- [F] H02 — Human construct/content/usability validation of RSDRI.
- [F] H03 — Claims of empirical superiority over Story Points or HIE.
- [F] H04 — Access to Scopus, Web of Science, IEEE Xplore, ACM DL,
  SpringerLink, or ScienceDirect.
- [F] H05 — Production locked simulation and its nine currently failing
  pre-lock controls, unless the paper route is deliberately upgraded before
  manuscript results are finalized.
- [F] H06 — Organizational ROI, causal readiness-gate, or validated cognitive
  workload claims.

## Change control — prevents drift

1. New tasks may be added only when they are necessary for an existing exit
   condition, required by the venue, or explicitly approved by the user.
2. Every added task must state the reason, affected gate, and whether it changes
   the paper's claims or schedule.
3. Optional improvements must not interrupt the next incomplete mandatory task.
4. At the start and end of each work cycle, report completed IDs, active ID,
   next IDs, and any `[H]` support required.
5. Do not mark the research goal complete until G07 is satisfied or the user
   explicitly changes the terminal condition.
