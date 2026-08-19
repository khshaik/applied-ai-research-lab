# Gate 2 executable evidence-review controls

This package operationalizes Sections 11–17 of
`research/design/02_systematic_review_protocol.md`. It is an audit and reconciliation layer,
not a search tool and not an autonomous evidence judge.

The approved discovery route is access constrained. Its scholarly discovery
sources are OpenAlex, Semantic Scholar Academic Graph, and arXiv under protocol
v1.3's declared non-Cartesian matrix. Crossref is DOI/bibliographic metadata
verification only. Scopus, Web of Science Core Collection, IEEE Xplore, ACM Digital
Library, SpringerLink, and ScienceDirect are documented authentication blocks;
the open sources are non-equivalent supplements and must never be relabelled as
searches of those platforms.

## Operating sequence

1. Copy `templates/review_bundle.template.json` and replace the accountable
   author placeholder. Do not populate it from the scoping seed matrix.
2. Register every approved systematic, update, and excluded pilot search run.
   Import records only from documented, approved search batches. Preserve every
   report even when it is later consolidated into a study family. Classify each
   record as peer-reviewed scholarly, preprint scholarly, grey/practitioner, or
   method/reference evidence.
3. Record every removed duplicate as a retained/removed pair with its DOI,
   arXiv-related DOI, normalized title/author/year, or documented manual basis.
   Study-family consolidation remains a later, report-preserving step.
4. Run two separately prompted agent passes in different context IDs. Both must
   receive the same checksum-identified input and record that the other pass's
   decision was not visible. Preserve agent and prompt/model IDs, decision,
   reason, confidence, and an inspectable source locator. Do not call this human
   double screening.
5. Use a different coordinating agent in a third context to adjudicate
   disagreements or `unclear` decisions. Full-text exclusions require one
   E1–E10 code.
6. Consolidate preprint, conference, journal, correction, and companion reports
   into a study family without deleting report-level records. State the basis,
   record explicit linkage signals, and select the most complete report.
7. Record whether full text is lawfully open, an author manuscript, a preprint
   version, available through authorized subscription access, paywalled, or
   otherwise unavailable. Assessed reports require an inspectable lawful
   locator; the workflow never treats a missing text as read.
8. Record one backward and one forward citation chase per finally included
   family, including seed, direction, provider, time, raw-export checksum,
   search run, and discovered record IDs. Preserve zero-result chases as empty
   discovered-record lists.
9. Appraise the family with the protocol-appropriate form. Extract claims at
   report level, preserving whether data are observed, self-reported, modeled,
   conceptual, or mixed and the exact table/page/section locator.
10. A second agent verifies outcome-bearing extractions. An accountable author
   then opens the cited source and confirms both the included source and each
   citation-bearing extraction. Agent agreement is never a substitute for this
   confirmation.
11. Append flow events as transitions occur, using a contiguous event index and
   predecessor link. Never reorder or replace earlier events; correct an error
   through a documented protocol-deviation record outside the bundle and a new
   event where the action model permits it. Never type aggregate counts into the
   bundle. The script derives them and, in final mode, applies four flow
   conservation equations. Version control or a write-once repository remains
   necessary for tamper evidence; a static JSON file cannot prove immutability.

## Commands

Development validation (allows incomplete searches and decisions):

```bash
python -m evidence_review.workflow path/to/review-bundle.json --prisma
```

Final reconciliation (hard-stops incomplete search/update status, incomplete
source/search-family coverage, incomplete agent passes, unresolved
disagreements, unconfirmed verified extractions, and non-conserving PRISMA
flow):

```bash
python -m evidence_review.workflow path/to/review-bundle.json --final --prisma
```

Add `--evidence-matrix` to derive the family-level evidence matrix from the same
bundle. It reports evidence stratum, publication and lawful-access state,
appraisal identifiers/bands, and verified/candidate extraction counts without
adding a synthesis judgment or a hand-entered count.

## Versioned agent calibration artifacts

The two isolated screening prompts and separate adjudicator prompt are under
`prompts/`. `fixtures/synthetic_calibration_manifest.json` locks their versions
and SHA-256 hashes together with one byte-identical input packet and a
synthetic-only calibration bundle. The fixture exercises disagreement and
adjudication mechanics but deliberately contains no real publication, evidence,
PRISMA observation, or publication-ready decision. Run
`python3 -m unittest tests.test_screening_prompt_artifacts` after any intentional
prompt revision, then version and re-hash the entire artifact set.

The command validates the JSON Schema before applying the cross-record
invariants JSON Schema cannot reliably express. The empty template
deliberately returns `no_observations` with `counts: null`; it is not a zero-
result literature review.

Final mode additionally applies a terminal state machine to every record. A
record follows exactly one path from its source-appropriate identification
event to duplicate removal, title/abstract exclusion, retrieval failure,
full-text exclusion, or inclusion. Aggregate totals cannot conceal an invalid
record path.

PRISMA output from this package documents the flow of records found through the
declared route. It does not certify exhaustive coverage. Peer-reviewed primary
reports, preprints, secondary studies, practitioner/grey records, and method
references must remain distinct destinations, with report counts distinguished
from consolidated study-family counts.

## Evidence and accountability boundary

Agents may propose decisions, codes, study-family links, appraisal entries, and
candidate extractions. Only an accountable author can confirm that a source was
opened and that a citation supports the manuscript claim. Until that explicit
confirmation is recorded, the claim is not publication-ready. The workflow
does not assert that agent passes are statistically or operationally
independent merely because two IDs are present; the recorded independence
attestation must describe session/context separation and limitations. Final
mode additionally checks distinct context IDs, identical input checksums,
blinded screening passes, and a distinct adjudicator/context.

## Claim boundary

The bundle is explicitly labelled an access-constrained, AI-assisted systematic
evidence map using open indexes. Final mode permits only this novelty wording:

> No substantively duplicative framework was identified within the predeclared
> open scholarly indexes, repositories, and citation networks searched through
> the stated cutoff date.

It prohibits “No prior research exists” and “All relevant literature was
searched.” An unavailable subscription source must record the access state,
attempt time, reason, deviation ID, and accountable-author approval; open-index
discovery is not represented as coverage-equivalent.
