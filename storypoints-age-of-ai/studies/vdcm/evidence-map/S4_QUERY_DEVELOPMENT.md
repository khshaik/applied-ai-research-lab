# S4 query-development record

Status: development only  
Cutoff: 2026-08-15  
Family: AI-assisted code-review and verification burden

## Purpose

S4 tests whether the open evidence base captures both sides of the proposed
mechanism: AI-generated or AI-reviewed changes may increase human verification
demand, while AI review may also accelerate some decisions or improve parts of
the review workflow. It is not designed to prove that review burden always
increases.

## Prospective controls

The active development registry is
[`registries/s4_open_index_queries_v0.6.json`](registries/s4_open_index_queries_v0.6.json).
It contains two direct positive sentinels, one neutral/disconfirming sentinel,
one conventional-review boundary sentinel, and independent OpenAlex and
Semantic Scholar query translations.

The positive and neutral/disconfirming records must be recalled before a
source-family query can be considered for freeze. The negative-boundary record
is a precision warning, not a required absence claim.

## Acceptance sequence

1. Run a one-page development export for each source.
2. Confirm registry hash, stable identifiers, and known-item recall.
3. Refine only for documented recall or precision failures.
4. Complete pagination after a bounded pilot is acceptable.
5. Appraise the deterministic sample required by the population band.
6. Keep all results developmental until the overall evidence-map protocol is
   frozen and the accountable-author gate is complete.

No result from this file is an eligibility decision, included-study count, or
PRISMA flow value.

## Development history

- v0.1/OpenAlex retrieved 218 records in a complete developmental export but
  missed all three required known items. The failure was caused by implicit AND
  matching across every ungrouped term. It is retained as an immutable negative
  query-development result.
- v0.2 uses explicit Boolean synonym groups for the AI and review concepts.
  Its capped OpenAlex pilot reported 7,561 matches and found only one of three
  required sentinels in the first 100 ranked results. It is too broad for
  operational use and remains incomplete.
- v0.3 adds a third, explicitly disjunctive review-demand/outcome concept group.
  Its capped OpenAlex pilot still reported 7,127 matches and found only one of
  three required sentinels in the first 100 ranked results; it is too broad.
- v0.4 replaces the generic AI group with review-specific LLM/AI phrases while
  retaining outcome alternatives. Its capped OpenAlex pilot still reported
  2,808 matches and remained dominated by generation-quality studies.
- v0.5 requires the exact phrase `code review`, removes the broad `AI-assisted`
  and `pull request` alternatives, and retains the outcome alternatives. The
  peer-reviewed DOI is used for the industrial sentinel where available.
- v0.6 preserves the accepted Semantic Scholar translation and changes only
  OpenAlex execution: title-and-abstract field filtering replaces full-text
  search, and its sentinel set uses three records independently confirmed as
  indexed by OpenAlex. This source-specific mode is explicitly recorded in the
  export manifest.

## Current result

- Semantic Scholar S2-S4R5: complete developmental export, 279 records.
- Required sentinel recall: 2/2 positive and 1/1 neutral/disconfirming; pass.
- Deterministic appraisal: 50 records; 13 likely relevant, 12 uncertain, and
  25 likely irrelevant.
- Relevant-plus-uncertain burden: 50.0% (Wilson 95% interval 36.64%–63.36%).
- Mechanical source-family status: `freeze_ready=true` for query development.
- OpenAlex OA-S4R6: complete developmental export, 564 records. The
  title-and-abstract translation recalled all two positive and one
  neutral/disconfirming sentinels. Its deterministic 50-record appraisal found
  15 likely relevant, 5 uncertain, and 30 likely irrelevant records;
  relevant-plus-uncertain burden was 40.0% (Wilson 95% interval
  27.61%–53.82%). Mechanical query-development status is `freeze_ready=true`.
- Semantic Scholar S2-S4R5 remains accepted under registry v0.6. Its query,
  export, sample, and decisions were unchanged; a checksummed reuse record
  documents the recomputed source-qualified sentinel result.
- The existing complete arXiv AX-S5R export was mapped to S4 without renaming
  or rerunning it. All two positive and two neutral/disconfirming arXiv
  sentinels were present across 187 reconciled records. Mapping recall passes,
  and its deterministic 50-record appraisal is complete: 16 likely relevant,
  12 uncertain, and 22 likely irrelevant records. Relevant-plus-uncertain
  burden was 56.0% (Wilson 95% interval 42.31%–68.84%); mechanical mapped-query
  status is `freeze_ready=true`.

The Semantic Scholar result does not freeze the overall protocol, create an
included-study set, or establish evidence for any paper claim.
