# D14 Citation-Chasing Resource-Cap Decision

Status: **Approved by accountable author**  
Protocol: frozen evidence-map protocol v1.3, Section 7.4  
Decision date: 2026-08-19

## Completed coverage

- The first backward/forward citation round started from all 570 D13-included study families.
- OpenAlex resolved 512 seeds and returned 5,090 backward plus 3,346 forward edges.
- Semantic Scholar resolved 26 additional seeds and returned 803 relationships.
- The rate-aware recovery resolved 16 further seeds and returned 588 relationships.
- A checksum-bound supplement resolved two additional seeds, completed both previously failed relationship calls, and returned 57 relationships from those two seeds.
- Two source-no-match studies were reconciled to frozen OpenAlex identities with zero indexed edges.
- Seven seeds ended as confirmed source no-match and five remain public-API failures after bounded retries.
- The round produced 6,017 initially unique citation candidates. Dual isolated screening plus adjudication retained 1,017 title/abstract candidates; 337 lawful static full texts were assessed and 212 were included.
- The supplement added 54 candidate records, consolidated to 33 unique records. Dual screening plus adjudication retained 11; nine lawful action-free full texts were retrieved and both isolated full-text passes included all nine.

## Proposed prospective cap

Close D14 after completing appraisal and extraction for the nine supplement reports, without recursively citation-chasing the 221 newly included D14 studies and without further retries of the five persistently throttled Semantic Scholar seeds.

The cap is proposed because:

1. one broad citation round was attempted across the complete 570-family seed set;
2. the open-index searches and citation round already produced a large, separately screened corpus;
3. recursive chasing from 221 new inclusions could expand without a predictable bound and would materially delay the evidence synthesis;
4. five repeated API failures are an external availability limitation, not evidence of no relationships;
5. the paper uses a bounded novelty statement and will disclose inaccessible subscription databases, unavailable full texts, source no-matches, API failures, and the absence of recursive saturation.

## Consequence if approved

The review must not claim exhaustive retrieval or citation-network saturation. The permitted conclusion remains:

> No substantively duplicative framework was identified within the predeclared open scholarly indexes, repositories, and citation networks searched through the stated cutoff date and reported resource cap.

The limitation section must state that seven source no-matches, five persistent API failures, 680 unavailable initial D14 full texts, two unavailable supplement reports, and the unexecuted recursive round may contain relevant evidence.

## Decision

- [x] Approved by accountable author on 2026-08-19
- [ ] Rejected; continue recursive citation chasing

Approval phrase: **Approve the D14 prospective resource cap as documented.**
