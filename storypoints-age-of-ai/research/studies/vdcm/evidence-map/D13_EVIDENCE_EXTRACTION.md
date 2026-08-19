# D13 — Evidence Extraction

Status: complete  
Protocol: frozen v1.3  
Completion date: 2026-08-18

## Result

The final matrix contains 570 eligible study families, 1,367 exact-page-located
findings, and 653 source-verified quantitative findings. It records
bibliographic status, context and method, lifecycle coverage, VDCM/RSDRI
construct mappings, emergent constructs, measures/findings, limitations, and
the five novelty-adjudication dimensions.

| Evidence band | Families |
|---|---:|
| High | 75 |
| Moderate | 272 |
| Low/contextual | 223 |

No family currently satisfies all five indispensable novelty dimensions for
the same pre-commitment planning use, and no near-stop candidate met the frozen
mechanical rule. This is an extraction-stage diagnostic, not the final bounded
novelty conclusion; D14 citation chasing and D16 synthesis remain mandatory.

## Quality controls and remediation

The initial primary extraction contained 976 candidate findings and 666
quantitative candidates. Distinct verifiers checked every family, numerical
claim, page locator, and non-negative novelty mapping. They rejected contextual
or unsupported numbers and corrected malformed uncertainty fields.

A major completeness asymmetry remained: the first partition contained exactly
one finding per study, while the second contained one to three. D13 therefore
hard-stopped. A separate completeness re-extraction of the affected 285 studies
preserved only 87 baseline findings, removed 198 generic/non-result statements,
and added 679 material findings across 274 studies, including 89 newly located
quantitative findings. The superseded extraction remains preserved for audit
history.

## Interpretation and security boundaries

- Technical outcomes are not recoded as human cognitive workload without
  explicit source evidence.
- Quantitative values are not pooled across heterogeneous tasks or designs.
- Evidence bands control narrative strength; they are not certainty weights.
- Every manuscript-level material citation remains pending D17 accountable-
  author confirmation.
- Processing used local checksum-bound static text only. No network,
  credentials, Git history, package installation, links, or executable PDF
  content was used.

## Immutable artifacts

- Final matrix: `gate2/output/systematic/v1.3/20260816/d13/final/evidence_matrix.jsonl`
- Final manifest: `gate2/output/systematic/v1.3/20260816/d13/final/d13_final_manifest.json`
- Matrix SHA-256: `fe36a98598980c31ec0a660ffccb015df24eddc023d3bd0745e00ad4af66c417`
- Verified partition A v2 SHA-256: `e537123e77b344d5caddaee822f204bdff537f0399f07412b19d78730b1f4c2e`
- Verified partition B SHA-256: `136d782bf9dc97e3a7afc060d7f98be89e47dd33528821eb445f02eee4adffc8`
