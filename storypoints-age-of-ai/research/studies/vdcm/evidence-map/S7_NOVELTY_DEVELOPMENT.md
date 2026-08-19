# S7 exact/close novelty-control development

**Status:** OpenAlex, Semantic Scholar, and arXiv v0.4 developmental controls complete. Developmental only.

## Purpose and boundary

S7 tests exact and close contribution vocabulary while deliberately retrieving the closest known framework families. It supports only the protocol's bounded novelty wording. The results below are query-engineering evidence, not screening, eligibility, study-family consolidation, full-text appraisal, PRISMA counts, or a final novelty conclusion.

The accepted registry is `registries/s7_novelty_queries_v0.4.json`. It uses contribution phrases plus broad predecessor classes rather than requiring complete predecessor titles. HIE and its conceptual predecessor, ACEM, Agile V, human-AI delivery orchestration, AI-assisted Story Point estimation, and conventional-effort estimation are registered as positive or disconfirming controls. Agentic pipeline self-healing is the negative boundary.

## Refinement ledger

- **v0.1 rejected:** ACEM was registered under an incorrect expanded title, and an early-adopter disconfirming sentinel was outside the narrow query.
- **v0.2 rejected as final control:** corrected ACEM's title and retrieved it in both sources, but did not document that Semantic Scholar exposes the record without DOI.
- **v0.3 superseded:** documented the stable Semantic Scholar paper ID and exact-title fallback; its first exports predated the final registry bytes. Hash-matched pilot-2 exports exist as developmental provenance but were superseded by a clean v0.4 run.
- **v0.4 accepted for completed sources:** immutable registry and manifests are hash-bound. OpenAlex retrieved 49/49 records and Semantic Scholar 19/19. Both appraised their complete populations.
- **arXiv v0.4 resolved:** the first bounded retry ended in DNS resolution failure and created no target directory. A later bounded retry succeeded at `gate2/output/development/arxiv/AX-S7R4-20260816-retry2` with 7/7 records and four registered sentinels. The blocker record is retained as resolved failure provenance.

## Completed-source control results

| Source | Complete records | Appraised | Likely relevant | Uncertain | Relevant + uncertain | Sentinel result | Development control |
|---|---:|---:|---:|---:|---:|---|---|
| OpenAlex | 49 | 49 | 18 | 11 | 29/49 (59.2%) | five positive and two disconfirming recalled; boundary absent | pass |
| Semantic Scholar | 19 | 19 | 12 | 3 | 15/19 (78.9%) | five positive and two disconfirming recalled; boundary absent | pass |
| arXiv | 7 | 7 | 5 | 2 | 7/7 (100%) | three positive and one disconfirming recalled | pass |

Semantic Scholar's ACEM record has no DOI. The control therefore matches its exact normalized indexed title; v0.4 also documents stable paper ID `f3e7ecd8f7c7c4d2d3aaacb8001c352dd5ddf10b` for audit. This is an explicit source-metadata limitation, not evidence that ACEM is absent.

## Section 15.5 developmental overlap assessment

This matrix is a conservative metadata-level check of the five indispensable dimensions. `Yes` means the exported abstract explicitly supports the dimension; `partial` means related constructs are present without the full requirement; `no/unclear` means the abstract does not establish it. Full text can change these judgments.

| Framework line | Pre-commitment predictors | Multi-role lifecycle through acceptance/release | Active touch separated from constrained-role queue | Capacity + readiness + dependencies/gates | Verified-completion/capacity forecast target | Developmental stop-rule result |
|---|---|---|---|---|---|---|
| HIE / LLM-aware effort | partial | no | no | no | no—task effort | not triggered |
| ACEM | partial | partial | no | no | no—cost | not triggered |
| Agile V | no/unclear | partial/yes | no | partial—approval gates, not explicit role capacity | partial—verified increments, not a capacity forecast | not triggered |
| Human-AI delivery orchestration | no—retrospective configurations | partial/yes | no | partial—workflow stages, not explicit readiness/capacity mechanics | no—observed/modeled delivery outcomes, not a pre-commitment forecast | not triggered |
| AI-assisted Story Point / conventional effort estimation | yes for task/project inputs | no | no | no | no—Story Points or effort | not triggered |

No inspected metadata record establishes all five dimensions in one study family or coherent framework line. This does **not** establish novelty. The stop-rule decision remains provisional because records have not been systematically screened or consolidated into study families, and full texts/citation networks have not been appraised. The rule must be re-run after those steps. If later evidence supplies all five dimensions for the same planning use, the paper must pivot to replication, integration, or extension.

## Permitted interpretation

At this stage the only defensible statement is: *the completed OpenAlex, Semantic Scholar, and arXiv developmental controls recalled the declared closest predecessors and did not identify, from metadata alone, one framework line that clearly satisfies all five stop-rule dimensions.* Do not substitute this for the protocol's final bounded novelty statement.
