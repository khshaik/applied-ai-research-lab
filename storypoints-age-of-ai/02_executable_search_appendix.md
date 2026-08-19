# Gate 2 Executable Search Appendix

**Version:** 0.3 minimum-route reconciliation, 16 August 2026 IST  
**Status:** Query engineering appendix. The runs below are pilots and are **not** the final systematic search or PRISMA corpus.

## 1. Reproducibility boundary

The literal arXiv queries in this appendix were executed through the public Atom API. Result totals are volatile and describe the API response at the recorded time; they are not eligible-study counts. Early query-engineering pilots retrieved only shallow samples; later controlled developmental exports fully paginated AX-S5R, AX-S5T, AX-S5S, and AX-S6R, yielding 1,943 query records in total. No deduplication, eligibility screening, study-family consolidation, or frozen systematic execution has yet occurred, so 1,943 must not be presented as a PRISMA or included-study count.

The approved discovery sources are OpenAlex, Semantic Scholar Academic Graph,
and arXiv, allocated through protocol v1.3's non-Cartesian 21-pair matrix.
Crossref is DOI/bibliographic verification only and has no discovery-family or
PRISMA role. No systematic run has occurred; all existing outputs remain
developmental pilots.

Scopus, Web of Science, IEEE Xplore, ACM Digital Library, SpringerLink, and ScienceDirect were assessed on 15 August 2026 as unavailable because the project has no institutional authentication/authorization. They were not systematically executed. Their legacy candidate strings below are retained for auditability or possible future access only; they are not completed searches and the open indexes are not coverage-equivalent substitutes.

## 2. Tested arXiv pilot queries

Use the arXiv API endpoint `https://export.arxiv.org/api/query` with `start=0`, a documented `max_results`, `sortBy=submittedDate`, and `sortOrder=descending`. For the final run, paginate until `start >= totalResults`, retain the raw Atom pages, and calculate SHA-256 checksums.

### AX-P0 — deliberately over-broad precision test

```text
all:"large language model" AND all:"software engineering" AND
(all:effort OR all:estimation OR all:oversight)
```

Observed API total: **643**. Disposition: failed precision validation; preserve as pilot evidence but do not use as the final S1 search.

### AX-S3 — AI-era effort and Story Points

```text
(all:"story point" OR all:"software effort estimation") AND
(all:"large language model" OR all:"generative AI" OR all:"AI-assisted")
```

Observed API total: **4**. The returned set included ACEM (`2608.02582v2`) and *Story Point Estimation Using Large Language Models* (`2603.06276v2`). This family is sufficiently precise for full export, subject to sentinel recall testing.

### AX-S4 — AI-assisted review burden

```text
(all:"AI-assisted coding" OR all:"AI coding assistant") AND
(all:"code review" OR all:"pull request") AND
(all:workload OR all:attention OR all:effort OR all:verification)
```

Observed API total: **4**. The returned set included `2607.05677v1`, `2605.23108v1`, `2603.25773v1`, and `2512.23982v1`. This is precise but must be paired with the broader assurance query because literal assistant terminology may miss relevant review experiments.

### AX-S6 — team/lifecycle delivery

```text
(all:"large language model" OR all:"generative AI") AND
all:"software delivery" AND
(all:capacity OR all:coordination OR all:readiness OR all:orchestration)
```

Observed API total: **2**. The query is precise but failed to demonstrate recall of the known Armesto–Kolb sentinel; revise before freezing. It cannot be the sole S6 query.

### AX-S6R — revised team/lifecycle delivery pilot

```text
(all:"human-AI" OR all:"AI-assisted" OR all:"AI-augmented" OR
 all:"large language model" OR all:"coding agent") AND
(all:"software delivery" OR all:"software development lifecycle" OR
 all:"software modernization") AND
(all:orchestration OR all:workflow OR all:team OR all:validation)
```

Observed API total on 14 August 2026: **29**. Retrieval depth: first **10** records. The result set retrieved the Armesto–Kolb sentinel (`2603.20028v1`) and also surfaced relevant lifecycle/architecture/validation candidates, but included pipeline-operation noise. Disposition: sentinel-recall success and manageable full-export candidate; retain as the revised high-recall S6 family, with eligibility screening rather than post hoc query narrowing. It is not a frozen systematic result until all 29 records are paginated and archived under a frozen protocol.

### AX-S5 — assurance and verification

```text
(all:"large language model" OR all:"AI-assisted") AND
(all:"software testing" OR all:"code review" OR all:"software security") AND
(all:human OR all:oversight OR all:verification)
```

Observed API total: **142**. The first page included *Same Scrutiny, More Time: Eye Tracking Insights into Reviewing LLM-Labelled Code* (`2606.26505v1`). Disposition: retain as a high-recall family and divide it into testing, review, and security subqueries for the frozen search.

### AX-S5R — human review subfamily (developmental candidate)

```text
(all:"large language model" OR all:"AI-assisted" OR
 all:"AI coding assistant" OR all:"coding agent") AND
(all:"code review" OR all:"pull request") AND
(all:human OR all:oversight OR all:workload OR all:attention OR
 all:effort OR all:verification)
```

Sentinel diagnostic: `2606.26505` (*Same Scrutiny, More Time*) must be retrieved if indexed and available in the API at execution. The controlled retry fully retrieved **187/187** API records across two raw pages and retrieved the sentinel. This is a developmental query total, not an eligible-study or PRISMA count.

### AX-S5T — human testing/QA subfamily (developmental candidate)

```text
(all:"large language model" OR all:"AI-assisted" OR
 all:"AI coding assistant" OR all:"coding agent") AND
(all:"software testing" OR all:"test generation" OR all:"unit testing" OR
 all:"integration testing" OR all:"quality assurance") AND
(all:human OR all:oversight OR all:verification OR all:validation OR all:effort)
```

This separates test generation and test execution/validation from review. The controlled retry fully retrieved **394/394** API records across four raw pages. No sentinel is registered for this subfamily, so `sentinel_recall_pass=true` in the manifest is vacuous and must not be described as known-item validation.

### AX-S5S — human security assurance subfamily (developmental candidate)

```text
(all:"large language model" OR all:"AI-assisted" OR
 all:"AI coding assistant" OR all:"coding agent") AND
(all:"software security" OR all:"secure coding" OR all:vulnerability OR
 all:"security review") AND
(all:human OR all:oversight OR all:verification OR all:validation OR all:review)
```

This isolates security assurance from generic quality language. The controlled retry fully retrieved **1,333/1,333** API records across fourteen raw pages. The volume signals a likely precision burden requiring screening/query appraisal; it is not evidence of 1,333 eligible studies. No sentinel is registered for this subfamily.

### AX-S6R sentinel checks

For a complete AX-S6R development export, match version-insensitive arXiv base identifiers. The positive sentinel is Armesto–Kolb `2603.20028`. The controlled retry fully retrieved **29/29** API records in one raw page and retrieved the sentinel. A sentinel pass demonstrates only known-item recall; it does not establish sensitivity, precision, eligibility, or completeness. Record a missed sentinel as a query-validation failure without manually injecting the paper into the API export.

The machine-readable developmental queries and expected sentinels are stored in `gate2/arxiv_pilot_queries.json`.

## 2.1 Reproducible public arXiv export tooling

`python3 -m gate2.arxiv_export QUERY_ID 'LITERAL_QUERY' OUTPUT_DIRECTORY --sentinel BASE_ARXIV_ID` performs full Atom pagination by default. Repeat `--sentinel` when a family has multiple known-item checks. It:

1. refuses any status other than `development_pilot`;
2. preserves each raw Atom page;
3. checks stable `totalResults`, requested/returned page offsets, empty premature pages, duplicate versioned identifiers, and version-insensitive sentinel presence;
4. writes a normalized CSV plus query, page, CSV, and manifest SHA-256 values; and
5. publishes atomically to a previously nonexistent output directory.

The tool does not deduplicate study families, screen records, produce eligibility decisions, or create PRISMA counts. Public API rate limits remain an external execution constraint; a failed request must be logged and retried later without relabelling an incomplete export as complete.

## 3. Canonical-family control and source translations

The complete required family set is S1, S2, S3, S4, S5R, S5T, S5S, S6, S7,
and S8. `gate2/search_control_template.json` contains every literal term and a
canonical expression for every family; `python3 -c 'from pathlib import Path;
from gate2.search_control import load_control,render_families; print(render_families(load_control(Path("gate2/search_control_template.json"))))'`
expands them without `A_TERMS`-style placeholders. This is a canonical Boolean
render, not evidence that any database accepted or executed it.

All 18 source-family pairs in the approved non-Cartesian allocation have a
complete accepted developmental control or, for S2, the explicitly documented
bounded-union disposition. The reconciled matrix is
`gate2/final_source_family_acceptance_matrix.json`. These are not systematic
corpus runs; each accepted control must be rerun after D03/D04. No additional
Cartesian pairs are required, and a translation cannot be inferred from another
platform's syntax.

Run each family separately with publication window 2019 through the final search date and English language, where filters are supported. Apply the pre-2019 foundational rule to S8. Do not paste placeholders; expand the registered literal terms.

### Open source translation status

| Source | Role | Translation/export status | Query-quality status | Freeze implication |
|---|---|---|---|---|
| OpenAlex | Declared-pair discovery; citation relationships | All 10 allocated OpenAlex pair controls reconciled; S2 is a bounded-union control requiring fresh D05 rerun | Developmental controls accepted | Await D03 approval; no pilot enters PRISMA |
| Semantic Scholar Academic Graph | Declared-pair discovery and citation relationships | All 5 allocated Semantic Scholar pair controls reconciled | Developmental controls accepted | Await D03 approval; fresh D05 rerun required |
| Crossref REST API | DOI/bibliographic verification only | Prior CR-S3/CR-S3R broad diagnostics retired from discovery; API access demonstrated | No family-query acceptance required | Metadata-verification procedure must be tested before freeze; no PRISMA count |
| arXiv | Declared-pair preprint discovery | All 3 allocated mapped/novelty controls reconciled | Developmental controls accepted | Await D03 approval; fresh D05 rerun required |

For every open source, preserve exact request parameters, documentation/access date, pagination/cursor trail, raw responses, normalized export, and SHA-256 manifest. A rate-limited, capped, or incomplete response is a failed/incomplete run, not a complete export.

### OA-S3R — completed developmental query acceptance

On 15 August 2026, the registry-driven OpenAlex refinement retrieved **134/134**
records with complete cursor pagination. The manifest embeds the exact query
registry SHA-256
`6a90831f08ea139bb7a043ac5281262c464a3830eafccb2bf2cef6223571dd9a`.
Both scope-positive HIE sentinels were present and the registered
negative-boundary sentinel was absent. The prespecified 50-record boundary
sample contained **13 likely relevant**, **37 likely irrelevant**, and **0
uncertain** records, for a relevant-plus-uncertain burden of **26.0%** (Wilson
95% interval **15.87%–39.55%**). The v0.2 validator derives
`freeze_ready=true` for completeness, boundary, and precision controls.
Registry v0.2 is superseded for freeze preparation by the family-scoped v0.3
rerun described below.

This is acceptance of one source–family translation only. It is not an
eligibility decision, PRISMA identification count, protocol freeze, systematic
corpus, or evidence that the remaining source–family pairs are acceptable.

### S2-S3R and CR-S3R — complementary-source diagnostics

The Semantic Scholar S3 refinement retrieved **15/15** records. Appraisal of
the full result set found **14 likely relevant** and **1 likely irrelevant**
record (**93.3%**, Wilson 95% interval **70.18%–98.81%**); both positive HIE
sentinels were present and the negative-boundary sentinel was absent. Its
v0.2 validator result is `freeze_ready=true`, subject to the same missing
neutral/disconfirming-class control and non-corpus boundary as OA-S3R.

The Crossref S3 refinement reported **263,416** records. Retrieval was
intentionally stopped after the first 100 records. Amendment 0.1 subsequently
removed Crossref from systematic discovery and limited it to candidate-level
metadata verification. The diagnostic is therefore retired rather than a
freeze blocker; its reported total is not an exported-record or PRISMA count.

### S3 v0.3 — family-scoped sentinel acceptance

Registry v0.3 is checksummed as
`5f82bc8519fe6c64a5c78abef9b252229c12d2f8036e45848f43a5e5f1972e23`.
It separates scope-positive sentinels from an in-scope neutral/disconfirming
sentinel that retains Story Points as an LLM forecast target. A conventional
estimator remains a negative-boundary precision warning and cannot substitute
for the neutral/disconfirming class.

OA-S3R3 retrieved **134/134** records. Its Appendix 4.2 sample used the first
10, last 10, and 30 hash-selected middle positions with seed SHA-256
`7883b0af362a1123d731e5a91480789428a2d241a96af3efdc0ea071099c474f`.
The sample contained **9 likely relevant**, **39 likely irrelevant**, and **2
uncertain** records; relevant-plus-uncertain burden was **22.0%** (Wilson 95%
interval **12.75%–35.24%**). Both required sentinel classes were retrieved.
The negative-boundary paper was also retrieved and is retained as a precision
warning rather than treated as a recall failure. Query-level
`freeze_ready=true`.

S2-S3R3 retrieved **15/15** records and reused its prior 15 judgments only
after confirming the normalized CSV was byte-identical. It retrieved both
required sentinel classes and retained **14 likely relevant** records;
query-level `freeze_ready=true`.

These two source–family translations are now eligible for protocol-owner
freeze review. Their records remain developmental and must be rerun after the
full protocol and source–family matrix are frozen.

### S5T — testing and quality-assurance query acceptance

The complete developmental arXiv `AX-S5T` export contains **394** query
records. Registry `arxiv_s5t_mapping_v0.1` adds two scope-positive and two
neutral/disconfirming sentinels; all four are present. The prespecified
50-record deterministic sample contains **23 likely relevant**, **26 likely
irrelevant**, and **1 uncertain** record. Relevant-plus-uncertain burden is
**48.0%** (Wilson 95% interval **34.80%–61.49%**), and the mapped query records
`freeze_ready=true`. These are query-appraisal judgments, not eligibility
decisions.

OpenAlex refinement v0.1 returned 3,193 records and was rejected as too broad.
Refinement v0.2 returned 955 records, but two complete-export attempts correctly
hard-stopped on duplicate identifiers returned across live cursor pages; no
partial complete export was published. The prospectively refined v0.4 query
retains human-interaction terms and adverse bug-detection/reliability evidence.
It retrieved **137/137** records in a complete, registry-hashed export and
recalled two scope-positive sentinels plus the registered adverse sentinel. The
negative-boundary GenAI-system-testing record was absent. Its deterministic
50-record sample contains **39 likely relevant**, **5 likely irrelevant**, and
**6 uncertain** records; relevant-plus-uncertain burden is **90.0%** (Wilson
95% interval **78.64%–95.65%**), and `freeze_ready=true`.

Thus both declared S5T discovery pairs have accepted developmental controls.
They must still be rerun after D03/D04 into the systematic corpus.

### S5S — security-assurance query acceptance

The accepted OpenAlex developmental control retrieved **19/19** records and
recalled two scope-positive and two neutral/disconfirming sentinels while
excluding the general LLM-security boundary record. Full-population appraisal
found **8 likely relevant**, **2 uncertain**, and **9 likely irrelevant**
records, for a relevant-plus-uncertain burden of **52.6%**.

The complete developmental arXiv `AX-S5S` export contains **1,333** records and
recalls two scope-positive and two neutral/disconfirming sentinels. Its canonical
100-record sample was generated from registry version `0.1` with seed
`0ae355d66d28adf43c83ae3b95b60cadfb1a281bbe7b1c6dcab29c660122d003`.
Under the strict human security-assurance burden rule, it contains **6 likely
relevant**, **7 uncertain**, and **87 likely irrelevant** records. The
relevant-plus-uncertain burden is **13.0%** (Wilson 95% interval
**7.76%–20.98%**). Exact positions, ordered IDs, mechanical rederivation, and
checksums passed independent audit; `freeze_ready=true`.

Both S5S controls remain developmental query appraisals, not eligibility,
included-study, or PRISMA results. They must be rerun after D03/D04.

### S6 — lifecycle and team-delivery query acceptance

The accepted arXiv `AX-S6R` control appraised its complete **29/29** population
under the narrow S6 rule: evidence must span lifecycle orchestration, gates or
dependencies, or report team/organizational coordination, capacity, flow, or
delivery outcomes. It found **10 likely relevant** and **19 likely irrelevant**
records (34.48% burden). An earlier overbroad classification is explicitly
rejected and fail-closed. Two positive and two neutral/disconfirming sentinels
were recalled.

The accepted OpenAlex `OA-S6R8` export contains **231/231** records. Its
deterministic 50-record appraisal contains **20 likely relevant**, **6
uncertain**, and **24 likely irrelevant** records, for a 52.0%
relevant-plus-uncertain burden. Four required positive/neutral sentinels were
recalled. The registered negative-boundary item was also retrieved and is
reported as a precision warning, so this control must not be described as
passing every individual sentinel check. Exact export binding, sample
positions, ordered IDs, rederivation, and checksums passed independent audit.

Both S6 controls remain developmental and must be rerun after D03/D04; their
counts are not screening, inclusion, or PRISMA results.

### S7 — exact and close novelty-control acceptance

The v0.4 developmental controls are complete for all declared sources:
OpenAlex **49/49** (18 likely relevant, 11 uncertain), Semantic Scholar
**19/19** (12 likely relevant, 3 uncertain), and arXiv **7/7** (5 likely
relevant, 2 uncertain). All required closest-predecessor and
neutral/disconfirming controls were recalled. The OpenAlex and Semantic Scholar
negative-boundary record was absent. Exact registry binding, raw exports,
seeds, positions, ordered IDs, appraisals, and checksums passed.

The developmental overlap matrix does not show, from metadata alone, one
framework line satisfying all five indispensable dimensions for the same
pre-commitment planning use. This is not a final novelty finding. Full-text
appraisal, study-family consolidation, and citation chasing can still trigger
the protocol's stop/pivot rule. The earlier arXiv DNS failure is preserved as
resolved provenance; the successful retry is the accepted 7/7 export.

### S8 — foundational comparison acceptance

The accepted v0.6 developmental control is pre-2019-inclusive and covers
Story Point/relative-estimate validity, developer-productivity measurement,
human modern-code-review work, mental-workload measurement boundaries, and
software-delivery flow. OpenAlex completed **1,097/1,097** records using
explicit publication-date ordering; its deterministic 100-record appraisal
contains **39 likely relevant**, **9 uncertain**, and **52 likely irrelevant**
records (48.0% relevant-plus-uncertain burden). Semantic Scholar completed
**794/794** records; its deterministic 50-record appraisal contains **18 likely
relevant**, **3 uncertain**, and **29 likely irrelevant** records (42.0%
burden).

Both sources recalled all five positive and two neutral/disconfirming
sentinels; the non-software workload boundary record was absent. Little's
original queueing identity is retained as a separately verified
method/reference anchor and will enter through DOI verification and citation
chasing, not as a broad-query recall requirement. Counts overlap and remain
query-development totals, not deduplicated, screened, included, or PRISMA
counts. The development trail and strict appraisal boundary are recorded in
`studies/vdcm/evidence-map/S8_FOUNDATIONAL_DEVELOPMENT.md`.

### Inaccessible-source audit record

| Source | Assessment date | Status | Reason | Fallback role |
|---|---|---|---|---|
| Scopus | 15 August 2026 | `blocked_authentication` | No authorized institutional session | `non_equivalent_supplement` |
| Web of Science Core Collection | 15 August 2026 | `blocked_authentication` | No authorized institutional session | `non_equivalent_supplement` |
| IEEE Xplore | 15 August 2026 | `blocked_authentication` | Authenticated/export access unavailable | `non_equivalent_supplement` |
| ACM Digital Library | 15 August 2026 | `blocked_authentication` | Authenticated/export access unavailable | `non_equivalent_supplement` |
| SpringerLink | 15 August 2026 | `blocked_authentication` | Authenticated/export access unavailable | `non_equivalent_supplement` |
| ScienceDirect | 15 August 2026 | `blocked_authentication` | Authenticated/export access unavailable | `non_equivalent_supplement` |

These rows record an access assessment, not a successful platform search or a fabricated access attempt time.

### DB-S3 — Scopus

```text
TITLE-ABS-KEY(
  ("story point*" OR "agile effort estimation" OR "software effort estimation")
  AND
  ("large language model*" OR LLM OR LLMs OR "generative AI" OR
   "AI-assisted" OR "AI coding assistant*" OR "coding agent*")
)
AND PUBYEAR > 2018
AND LIMIT-TO(LANGUAGE,"English")
```

### DB-S3 — Web of Science Core Collection

```text
TS=(("story point*" OR "agile effort estimation" OR "software effort estimation")
AND ("large language model*" OR LLM OR LLMs OR "generative AI" OR
"AI-assisted" OR "AI coding assistant*" OR "coding agent*"))
```

### DB-S4 — IEEE Xplore

```text
(("All Metadata":"AI-assisted coding" OR "All Metadata":"AI coding assistant" OR
  "All Metadata":"GitHub Copilot" OR "All Metadata":"coding agent")
 AND
 ("All Metadata":"code review" OR "All Metadata":"pull request")
 AND
 ("All Metadata":"cognitive load" OR "All Metadata":workload OR
  "All Metadata":attention OR "All Metadata":effort OR "All Metadata":verification))
```

### DB-S4 — ACM Digital Library advanced search

```text
[[Abstract:"AI-assisted coding"] OR [Abstract:"AI coding assistant"] OR
 [Abstract:"GitHub Copilot"] OR [Abstract:"coding agent"] OR
 [Title:"AI-assisted coding"] OR [Title:"AI coding assistant"]]
AND
[[Abstract:"code review"] OR [Abstract:"pull request"] OR
 [Title:"code review"] OR [Title:"pull request"]]
AND
[[Abstract:"cognitive load"] OR [Abstract:workload] OR [Abstract:attention] OR
 [Abstract:effort] OR [Abstract:verification]]
```

### DB-S6 — Scopus lifecycle/team coverage

```text
TITLE-ABS-KEY(
  ("large language model*" OR LLM OR LLMs OR "generative AI" OR
   "AI-assisted software" OR "AI-augmented software" OR "coding agent*")
  AND
  ("software delivery" OR SDLC OR DevOps)
  AND
  (team OR organisation* OR organization* OR enterprise)
  AND
  (capacity OR coordination OR readiness OR orchestrat* OR flow)
)
AND PUBYEAR > 2018
AND LIMIT-TO(LANGUAGE,"English")
```

SpringerLink and ScienceDirect interfaces can change query parsing. At execution, copy the exact accepted query shown by the platform, filters, returned count, export format, and timestamp rather than claiming these Scopus/WoS strings were portable.

## 4. Query-development acceptance protocol

These criteria govern **source-specific development pilots**, not study
eligibility or final corpus inclusion. A pilot that passes is eligible for
protocol-owner review and query freeze; it does not become PRISMA eligible and
its records must still be rerun after freeze. Acceptance is evaluated for each
source–family pair, or for the explicitly logged union of prespecified split
queries needed to represent that pair.

### 4.1 Prospective known-item register

Before executing a development pilot, freeze a known-item register containing,
for each applicable source–family pair:

- stable identifier, title, family assignment, and sentinel class;
- why the item is within the intended conceptual scope;
- independent evidence that the source indexes or exposes the item on the pilot date;
- the exact identifier-matching rule, including DOI/arXiv normalization; and
- who approved the register and its SHA-256.

Use two sentinel classes:

1. **scope-positive sentinels** exercise the central constructs and close-overlap
   studies for that family;
2. **neutral/disconfirming sentinels** exercise evidence that preserves partial
   value for Story Points, finds null/mixed AI effects, reports increased human
   work, or otherwise constrains the motivating thesis.

Sentinels must be selected from prior scoping knowledge before viewing the
pilot result. Do not add a missed paper retrospectively to make recall appear
successful. A paper can be a sentinel only where its source availability is
independently confirmed; an absent or unindexed item is recorded as
`not_testable_on_source`, not counted as a hit or miss.

**Known-item acceptance:** the source–family query or prespecified query union
must retrieve 100% of testable scope-positive and neutral/disconfirming
sentinels. A miss is a hard query-development failure. Revise or split the query
and rerun the entire acceptance procedure. A narrower component query that
misses a sentinel may remain only as a labelled supplementary component when
the complete prespecified union retrieves it. Sentinel recall is a known-item
diagnostic, not an estimate of population recall and not evidence of eligibility.

No source–family pair may pass with an empty applicable sentinel class merely by
recording a vacuous `true`. If no defensible neutral/disconfirming item is known,
record `class_not_available` with a rationale and require an independent query
review focused on symmetric terminology before protocol-owner acceptance.

### 4.2 Deterministic sampled-precision appraisal

After preserving the pilot output, estimate title/abstract screening burden on
a deterministic sample. Use all records when the deduplicated pilot contains
50 or fewer. Otherwise screen at least 50 records selected across the complete
ordered result range: the first 10, last 10, and 30 positions generated from a
published hash seed based on `source + family + query_version`. For outputs over
1,000 records, increase the minimum sample to 100 while retaining first, middle,
last, and hash-selected coverage. Deduplicate exact record identifiers before
sampling but preserve the raw duplicate count.

Two isolated agent passes apply only the broad title/abstract categories
`likely_eligible`, `unclear`, and `likely_ineligible`; conflicts are adjudicated
under the review protocol. For the burden estimate, count `unclear` with
`likely_eligible`. Report the observed proportion and a 95% Wilson interval,
the sample rule/seed, category counts, and the most common noise mechanisms.
This is query-development triage, not final screening, and sampled records do
not enter the corpus unless retrieved again after freeze.

The following pragmatic thresholds are declared in advance; they are
feasibility controls, not universal measures of search quality:

- **operational pass:** estimated likely-eligible-plus-unclear proportion is at
  least 10%, with all known-item and completeness controls passing;
- **conditional pass:** 5% to below 10%, allowed only when the full projected
  screening load is within the documented review capacity and the source adds
  a distinct coverage role or unique sentinel retrieval;
- **revise/split:** below 5%, unless the entire deduplicated result set is 100
  records or fewer and the protocol owner prospectively accepts full screening;
- **hard failure:** zero likely-eligible/unclear sampled records together with no
  retrieved applicable sentinel, regardless of result count.

Low precision must not be improved by deleting terms solely because retrieved
records contradict the thesis. Any revision is justified by recorded noise
mechanisms and reruns the full known-item, sample, and completeness checks.

### 4.3 Completeness, caps, and source-role boundaries

For every pilot, preserve the exact accepted request, filters, requested fields,
sort/order behavior, raw pages, normalized records, response metadata,
pagination trace, retry log, and checksums. A result-count field is diagnostic;
completeness is established only by traversing the source's documented
termination condition without an unexplained gap, premature empty page,
unstable cursor/offset, or unhandled rate-limit response.

Source-specific requirements are:

- **OpenAlex:** traverse the documented cursor until its terminal value;
  preserve every cursor transition and reconcile unique OpenAlex work IDs.
- **Semantic Scholar Academic Graph:** traverse the documented bulk-search
  pagination to termination. If the service exposes fewer records than its
  reported total or imposes a result cap, the query must be prospectively split
  into disjoint, reproducible partitions (normally year plus a registered
  secondary key) and the union deduplicated. An overlapping or non-exhaustive
  partition scheme fails completeness.
- **Crossref REST API:** traverse the documented cursor to termination, retain
  deposited DOI/record identifiers, and treat reported totals as diagnostics.
  Because Crossref's role is DOI metadata verification and complementary
  discovery, sparse abstracts may pass the source-role check but must be logged;
  Crossref alone cannot establish full-text eligibility or absence of a study.
- **arXiv:** require stable `totalResults`, contiguous requested/returned page
  offsets, no premature empty page, version-aware identifier handling, and full
  reconciliation to the reported total, as enforced by the developmental
  exporter.

If a source cap cannot be resolved with a logged, disjoint partition strategy,
the source–family pair is `capped_incomplete` and cannot be frozen. If source
semantics make a canonical family impossible, record `translation_not_viable`,
retain the failure evidence, and obtain a prospective protocol amendment; do
not silently narrow the family or borrow another source's coverage.

### 4.4 Acceptance record and failure rules

Each source–family acceptance record must contain query/version hashes,
sentinel outcomes by class, precision sample and interval, projected full
screening volume, completeness/cap outcome, source-role limitations, reviewer
provenance, and one status: `pass`, `conditional_pass`, `revise_and_retest`, or
`hard_fail`.

`pass` or `conditional_pass` requires all of the following:

1. every testable positive and neutral/disconfirming sentinel is retrieved;
2. the deterministic sample and burden decision satisfy Section 4.2;
3. pagination/export is complete or a disjoint capped-source partition union is proven complete;
4. raw output and acceptance artifacts have verified SHA-256 values;
5. source-role limitations are explicit and no cross-source equivalence is claimed; and
6. the exact accepted query is unchanged after the evaluated pilot.

Any sentinel miss, unresolved truncation, unverified export, post-pilot query or
filter change, unexplained result-count instability, missing acceptance field,
or thesis-favouring removal of disconfirming terminology forces
`revise_and_retest` or `hard_fail`. Network/rate-limit interruption is an
execution failure, not a zero-result search. Zero results are valid only after a
complete, error-free response is archived; a zero-result family still cannot
pass where testable sentinels exist.

## 5. Frozen-run requirements

1. Freeze the protocol and append query version/hash before outcome-bearing screening.
2. Run every executable open source on the same day where practical.
3. Export complete records with abstracts, identifiers, and cited references when licensed.
4. Preserve native export plus SHA-256 checksum; never infer counts from result-page estimates.
5. Retain the six dated authentication blocks and do not silently substitute an open index or general web search as equivalent coverage.
6. Deduplicate only after all completed exports are preserved.
7. Repeat the final update search within seven days of submission.

## 6. Status and access decision tree

For each source in the control record and each required family where applicable:

1. If access has not been tested, record `not_assessed`; do not create a run.
2. If access succeeds, translate the canonical query and record
   `translation_draft`, then `syntax_validated`. Pilot output is
   `pilot_excluded` and is never PRISMA-eligible.
3. A final protocol-approved run is `systematic_executed`; it becomes
   `export_verified` only after complete export and SHA-256 verification.
4. If execution fails, record `failed_attempt`, the exact accepted query when
   available, the failure evidence, and `prisma_eligible=false`. Do not enter a
   result count that was not obtained.
5. If source access is blocked, record the specific blocked-access status,
   attempt time, reason, next action, and fallback role. A fallback may support
   discovery or non-equivalent supplementation; it does not replace the source.
6. Final reconciliation fails while any executable open source lacks any
required family, any source remains `not_assessed`, the refresh is incomplete,
or a blocked source is paired with a comprehensive/full-access coverage claim.

The maximum final coverage label is `access_constrained`. PRISMA flow reporting
describes records found and processed under this route; it does not establish
exhaustive retrieval. The maximum permitted absence claim is the protocol's
qualified statement that no substantively duplicative framework was identified
within the predeclared open sources and citation networks through the stated
cutoff date.

The executable validator is `gate2/search_control.py`; its empty template makes
no execution or result claim.
