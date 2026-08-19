# Gate 2 Executable Evidence-Review Audit

**Audit date:** 14 August 2026  
**Scope:** Workbook-independent review governance only  
**Evidence status:** No subscription search was run; no study decision or
systematic-review count was created by this audit.

## Audit result

The frozen-method draft already specified two agent passes, adjudication,
study-family handling, quality appraisal, extraction, author accountability,
and PRISMA reporting. Before this remediation, those requirements existed only
as prose and blank table columns. The workflow therefore could not hard-stop an
unknown record reference, a record placed in two study families, a same-agent
extraction verification, an unconfirmed citation, or a non-reconciling PRISMA
flow.

| Control | Previous state | Executable state |
|---|---|---|
| Search provenance | Blank log table | Search-run IDs, exact queries, status, export checksums; pilot imports rejected |
| Agent screening | Prose/table | Two-pass provenance, decision vocabulary, confidence and source-locator checks |
| Adjudication | Prose/table | Required for disagreement/unclear; adjudicator must differ; full-text exclusion uses E1–E10 |
| Study families | Table | One-family-per-report, representative-member and consolidation-basis invariants |
| Appraisal | Table | Form, points, band, critical-flaw and source-locator record |
| Extraction | Table | Claim-level field/value, data-nature label, exact locator, distinct agent verification |
| Citation accountability | General author statement | Explicit source and claim confirmation by a registered accountable author |
| PRISMA | Blank aggregate table | Record-event ledger, predecessor chain, derived counts, four conservation equations |

## Artifacts and execution

- `evidence_review/schemas/review_bundle.schema.json` — interchange schema.
- `evidence_review/templates/review_bundle.template.json` — deliberately empty;
  it contains no inferred decisions or counts.
- `evidence_review/workflow.py` — dependency-free semantic validator and PRISMA
  reconciler.
- `evidence_review/README.md` — operating and accountability rules.
- `tests/test_evidence_review_workflow.py` — synthetic-only hard-stop tests.

Development validation allows an incomplete review. `--final` additionally
requires completed systematic and update searches, a non-placeholder
accountable author, frozen status, exactly two distinct agent passes for every
ledger-recorded screening stage, adjudication of disagreement/uncertainty,
author confirmation of verified citation-bearing extractions, study-family
assignment for included reports, and reconciling PRISMA flow.

## Deliberate boundaries and remaining blockers

- A static JSON predecessor chain detects accidental reorder/breakage but cannot
  itself prove immutability. Store production bundles in version control or a
  write-once evidence repository and checksum frozen exports.
- “Distinct agent IDs” does not establish statistical independence. Preserve the
  prompt-session separation and shared-model/context limitations in each pass.
- The executable layer does not retrieve paywalled content, search subscription
  databases, infer missing metadata, decide eligibility, or confirm citations.
- Final review readiness remains blocked until the approved searches and update
  search are actually executed, exported/checksummed, screened, adjudicated,
  consolidated, appraised, extracted, and explicitly confirmed by an
  accountable author.
