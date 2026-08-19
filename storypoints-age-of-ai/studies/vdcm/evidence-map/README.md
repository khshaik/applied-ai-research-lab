# Evidence Map Workspace

## Current status

- Review route: access-constrained, AI-assisted systematic evidence map.
- Protocol: v1.3 draft reconciled; not frozen.
- Developmental records remain outside PRISMA.
- OpenAlex S3 v0.3: accepted at query-development level, 134/134 records.
- Semantic Scholar S3 v0.3: accepted at query-development level, 15/15 records.
- Crossref S3: over-broad; redesign around DOI and metadata verification.
- Semantic Scholar S4 v0.6: query-development controls passed, 279/279 records;
  50-record deterministic appraisal completed.
- OpenAlex S4 v0.6: query-development controls passed, 564/564 records;
  source-specific title-and-abstract search and 50-record appraisal completed.
- arXiv AX-S5R mapped to S4: query-development controls passed, 187/187 records;
  four sentinel checks and 50-record appraisal completed.
- S7 exact/close novelty controls passed developmentally for OpenAlex,
  Semantic Scholar, and arXiv; final novelty remains deferred to full text and
  study-family synthesis.
- S8 foundational comparison controls passed developmentally: OpenAlex
  1,097/1,097 with a 100-record appraisal (48.0% burden), and Semantic Scholar
  794/794 with a 50-record appraisal (42.0% burden).
- C08 bounded integration passed: S1 uses a complete 331-record Semantic
  Scholar control; S2 uses a complete 257-record OpenAlex discovery component
  plus a predeclared, checksum-bound known-item recovery from accepted S6.

## Canonical implementation

- Retrieval tooling: [`../../../gate2/`](../../../gate2/)
- Review workflow: [`../../../evidence_review/`](../../../evidence_review/)
- Systematic-review protocol: [`../../../02_systematic_review_protocol.md`](../../../02_systematic_review_protocol.md)
- Executable appendix: [`../../../02_executable_search_appendix.md`](../../../02_executable_search_appendix.md)
- Search log: [`../../../02_search_execution_log_pilot.md`](../../../02_search_execution_log_pilot.md)
- S3 v0.3 registry: [`../../../gate2/open_index_pilot_queries_v0.3.json`](../../../gate2/open_index_pilot_queries_v0.3.json)

## Current family-development records

- S4 plan: [`S4_QUERY_DEVELOPMENT.md`](S4_QUERY_DEVELOPMENT.md)
- S4 active registry: [`registries/s4_open_index_queries_v0.6.json`](registries/s4_open_index_queries_v0.6.json)
- S4 accepted Semantic Scholar baseline and superseded registry v0.5: [`registries/s4_open_index_queries_v0.5.json`](registries/s4_open_index_queries_v0.5.json)
- S4 superseded registry v0.4: [`registries/s4_open_index_queries_v0.4.json`](registries/s4_open_index_queries_v0.4.json)
- S4 superseded registry v0.3: [`registries/s4_open_index_queries_v0.3.json`](registries/s4_open_index_queries_v0.3.json)
- S4 superseded registry v0.2: [`registries/s4_open_index_queries_v0.2.json`](registries/s4_open_index_queries_v0.2.json)
- S4 superseded registry: [`registries/s4_open_index_queries_v0.1.json`](registries/s4_open_index_queries_v0.1.json)
- S7 development memo: [`S7_NOVELTY_DEVELOPMENT.md`](S7_NOVELTY_DEVELOPMENT.md)
- S8 development memo: [`S8_FOUNDATIONAL_DEVELOPMENT.md`](S8_FOUNDATIONAL_DEVELOPMENT.md)
- S8 active registry: [`registries/s8_foundational_queries_v0.6.json`](registries/s8_foundational_queries_v0.6.json)
- C08 development memo: [`C08_INTEGRATIVE_DEVELOPMENT.md`](C08_INTEGRATIVE_DEVELOPMENT.md)
- C08 active registry: [`registries/s1_s2_integrative_queries_v0.3.json`](registries/s1_s2_integrative_queries_v0.3.json)
- C09 final matrix: [`C09_SOURCE_FAMILY_ACCEPTANCE_MATRIX.md`](C09_SOURCE_FAMILY_ACCEPTANCE_MATRIX.md)
- C09 machine matrix: [`../../../gate2/final_source_family_acceptance_matrix.json`](../../../gate2/final_source_family_acceptance_matrix.json)

## Freeze sequence

1. register family-scoped positive and neutral/disconfirming sentinels;
2. validate source indexing and matching rules;
3. run bounded source-specific pilots;
4. complete deterministic precision appraisal;
5. obtain protocol-owner acceptance for every required source-family pair;
6. freeze and checksum the complete matrix;
7. rerun accepted searches into a new systematic corpus;
8. deduplicate, consolidate study families, and begin isolated screening.
