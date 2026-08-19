# Status and roadmap

> The controlling completion plan is now
> [`../PROJECT_TODO.md`](../PROJECT_TODO.md). This document remains a concise
> status narrative and must not be used to add work outside that checklist.

Last updated: 2026-08-19  
Research route: Open Evidence Route + Route B simulation  
Repository state: private during double-blind preparation; protocol v1.3 frozen

## Current status

- D05–D14 evidence-map execution, lawful full-text processing, appraisal,
  extraction, and bounded citation chasing are complete.
- D15 reconciled 791 included study families, 2,343 source-located findings,
  and 769 quantitative findings.
- D16 produced the normalized synthesis, evidence bands, overlap matrix, and
  bounded novelty conclusion.
- D17 material claims CL-001 through CL-010 were confirmed by the accountable
  author on 2026-08-19.
- Developmental Route B simulation, figures, and result tables are complete.
- Active work is manuscript integration, venue formatting, DOCX/PDF rendering,
  visual QA, G06 approval, and G07 submission authorization.

The detailed material below records the earlier development state and is
retained for provenance; it is superseded by this current-status block and
[`research-status-and-release-path.md`](traceability/research-status-and-release-path.md).

## Historical completed snapshot (superseded)

### Scientific framing

- Reframed the contribution as prospective, multi-role verified-delivery
  capacity forecasting rather than a universal replacement for Story Points.
- Defined VDCM, RSDRI, role-stage human touch demand, capacity pressure,
  readiness, queue delay, and verified completion.
- Separated active touch time, waiting time, psychological workload, and quality
  outcomes.
- Preserved Story Points and an ex-ante HIE-compatible model as comparators.

### Evidence map

- Converted Gate 2 to an access-constrained, AI-assisted open evidence map.
- Recorded six inaccessible subscription sources as coverage limitations.
- Implemented immutable OpenAlex, Semantic Scholar, Crossref, and arXiv
  developmental exporters with checksums and hard stops.
- Implemented isolated agent-screening/adjudication controls, study-family
  consolidation, evidence-matrix, citation-confirmation, and PRISMA-ledger
  validation.
- Accepted S3 query development for OpenAlex and Semantic Scholar.
- Accepted S4 query development for Semantic Scholar:
  - 279/279 records retrieved;
  - all required positive and neutral/disconfirming sentinels recalled;
  - 50-record deterministic query appraisal completed;
  - 13 likely relevant, 12 uncertain, 25 likely irrelevant;
  - relevant-plus-uncertain burden 50.0%.
- Rejected the former OpenAlex full-text S4 translation, then accepted the
  source-specific title-and-abstract redesign:
  - 564/564 records retrieved;
  - all required known-item classes recalled;
  - 50-record deterministic appraisal completed;
  - 15 likely relevant, 5 uncertain, 30 likely irrelevant;
  - relevant-plus-uncertain burden 40.0%.
- Completed C03–C07 query controls, including S5T, S5S, S6, S7, and the
  pre-2019-inclusive S8 foundational comparison family. S8 accepted complete
  OpenAlex (1,097) and Semantic Scholar (794) developmental exports with
  deterministic appraisal, balanced sentinels, registry binding, and hashes.

### Simulation

- Implemented the developmental DES, comparators, gate/evidence semantics,
  calendars, blackouts, dependencies, queues, ablations, and a fail-closed
  production-runner architecture.
- Passed the Gate 4B engineering contract.
- Kept locked evaluation unopened and production lock blocked.
- Retained genuine organizational validation as future Route A work.

### Repository engineering

- Added study, paper, documentation, governance, artifact, and communications
  workspaces modeled on the reference research laboratory.
- Preserved import-stable, checksum-bound compatibility paths.
- Added contribution, security, citation, licensing, CI, Makefile, and
  repository-integrity controls.
- Drafted the minimum-route protocol amendment and machine-readable
  source-family/claims boundary; accountable-author approval is pending.
- Current verification: 201 tests plus repository and working-manuscript boundary validation.

## Historical pending snapshot (superseded)

### Scope and Gate 2 query matrix

1. Complete C08 bounded S1/S2 integrative controls under the approved
   non-Cartesian source allocation.
2. Complete C09 source-family acceptance reconciliation.
3. Present reconciled protocol v1.3 for accountable-author approval at D03.
4. Freeze only after every declared source-family pair has an accepted export,
   sentinel result, precision appraisal, checksum, and accountable-owner gate.

### Evidence-map execution

5. Rerun accepted queries into a new systematic corpus.
6. Normalize and deduplicate by DOI, title, authors, year, and study family.
7. Run two isolated agent screening passes and separate adjudication.
8. Retrieve lawful open full text, appraise included reports, and extract exact
   claim locators.
9. Conduct recursive backward and forward citation chasing to the declared
    stopping rule.
10. Reconcile the record/report/study-family ledger and produce the final
    evidence matrix and bounded novelty conclusion.

### Developmental simulation and paper

11. Reproduce and reconcile the existing developmental simulation, comparator,
    parameter-recovery, ablation, and negative-result artifacts.
12. Produce manuscript-ready tables/figures with synthetic-evidence labels and
    a parameter-use/limitations table.
13. Draft stable manuscript sections while the evidence map proceeds; populate
    results only from the final evidence bundle and reproduced simulation.
14. Complete citation, claims-boundary, AI-disclosure, anonymous/identified
    variants, rendering, visual QA, accountable-author approval, and submission.

Production locked evaluation and real organizational validation are outside the
minimum completion route unless the accountable author explicitly upgrades the
scope.

## User support triggers

No user action is needed for the current developmental work. Support will be
requested only for:

- accountable-author approval at protocol/query freeze;
- confirmation of final paper title and author metadata;
- final claim and citation sign-off;
- venue submission actions; and
- future Route A access to genuine teams or organizational data.

Authentication to subscription databases is not required under the approved
Open Evidence Route and will not be requested again unless access conditions
change.
