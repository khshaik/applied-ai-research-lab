# D11 — Full-Text Eligibility

Status: complete  
Protocol: frozen v1.3  
Completion date: 2026-08-17

## Security and access boundary

All assessment used local, checksum-bound, page-numbered extracted text. The
workflow did not use network access, credentials, environment secrets, Git
history, package installation, or executable PDF content. One AES-encrypted,
non-English dissertation could not be extracted with the already installed
libraries and was retained in the unavailable stratum; no new cryptography
package was installed.

## Flow

| D11 state | Families |
|---|---:|
| Full text assessed | 1,604 |
| Full text unavailable | 472 |
| Total entering D11 | 2,076 |

Two isolated AI-agent passes assessed the same 1,604 checksum-bound reports.
Their decision concordance was 1,247/1,604 (77.74%); this is agent concordance,
not human inter-rater reliability. A separate context adjudicated all 357
disagreements, including 83 and excluding 274.

Both passes identified an overly permissive shared interpretation risk around
the frozen I3 “quality consequences” wording. Before closure, a deterministic
SHA-256-ranked audit sampled 100 of the 1,096 consensus inclusions. It confirmed
43 and identified 57 false inclusions, exceeding the predeclared threshold of
five. D11 therefore hard-stopped and a separate strict re-review assessed all
1,096 consensus inclusions. The re-review retained 487 and excluded 609, and a
post-output consistency check agreed with the audit sample on 100/100 records.

## Final eligibility result

| Final state | Families |
|---|---:|
| Included full text | 570 |
| Excluded full text | 1,034 |
| Full text unavailable | 472 |
| Total | 2,076 |

Full-text exclusion reasons are E2 703, E1 202, E10 69, E8 20, E4 11, E3 10,
E5 7, E7 5, E9 5, and E6 2. The dominant correction removed benchmark-only or
technical-evaluation papers that did not substantively analyze eligible human,
process, delivery, oversight, flow, readiness, or quality consequences.

## Immutable artifacts

- Final ledger: `gate2/output/systematic/v1.3/20260816/d11/screening/final/fulltext_eligibility_decisions.jsonl`
- Final manifest: `gate2/output/systematic/v1.3/20260816/d11/screening/final/d11_final_manifest.json`
- Ledger SHA-256: `17d812d4c32d6f2a7d3342cd16f8b0f1271f16d6231e8388519f97dc1035f1c3`
- Separate adjudication SHA-256: `07c92b5c1e972ce6f6b241034043074dde4a81ba6c4fdca032b7613065439288`
- Consensus re-review SHA-256: `941b44afd74a914b911a9cf7b64f92e0f5c16b5462b87643d2a964010c58a3d0`
- Consensus audit SHA-256: `e54ba2f88e6c1f9204c1ee685c1dc276fc1460990a930645ce8f0ce3815cc95d`

## Interpretation boundary

D11 establishes eligibility, not evidence strength, cognitive-workload
validity, causal effect, or organizational generalizability. Those distinctions
are enforced in D12 appraisal and D13 extraction. The 472 unavailable reports
remain visible in the flow ledger but cannot contribute substantive claims.
