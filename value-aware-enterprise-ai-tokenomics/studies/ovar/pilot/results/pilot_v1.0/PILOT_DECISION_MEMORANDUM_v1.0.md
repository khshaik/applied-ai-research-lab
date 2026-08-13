# OVAR Pilot Decision Memorandum v1.0

## Decision

**DRY-RUN GO TO BLINDED CONSTRUCT REVIEW; NOT A PROSPECTIVE PERFORMANCE PASS.**

## What passed

- 24 unique constructed cases cover six domains, with four cases per domain.
- All five reference actions are represented: 3 stop, 9 revise, 3 continue-pilot, 6 scale, and 3 indeterminate.
- All 12 schema, leakage, cost-reconciliation, whitelist, determinism, and decision-receipt tests passed.
- On this authored case set, OVAR produced zero false-positive ROI classifications, zero false-scale decisions, zero false-stop decisions, and zero compliance violations under the frozen metric definitions.
- OVAR exact action agreement was 19/24 (79.2%); its five remaining disagreements were conservative revise/indeterminate distinctions rather than false scale or false stop under the registered definitions.
- OVAR's normalized measurement burden was 0.80, higher than every comparator, but no comparator combined lower weighted decision loss with lower burden.

## Comparator results

| Policy | False-positive ROI | False scale | False stop | Exact action agreement | Indeterminate | Weighted loss |
|---|---:|---:|---:|---:|---:|---:|
| Usage only | 100.0% | 53.3% | 0.0% | 29.2% | 0.0% | 5.158 |
| Self-reported value | 100.0% | 100.0% | 0.0% | 29.2% | 0.0% | 7.050 |
| Cost and quality | 100.0% | 53.3% | 0.0% | 37.5% | 0.0% | 5.233 |
| Outcome flat | 6.7% | 6.7% | 0.0% | 66.7% | 25.0% | 1.058 |
| OVAR ledger | 0.0% | 0.0% | 0.0% | 79.2% | 20.8% | 0.400 |

## Why this is not confirmatory evidence

The investigator authored the cases, reference states, and policy rules, and the first execution occurred before an immutable pre-execution manifest was created. The favorable ranking may therefore reflect case-design alignment with the proposed method. The result is evidence that the implementation behaves as intended, not evidence that OVAR improves real enterprise decisions.

## Required next gate

1. Obtain two blinded, independent construct reviews of the reviewer-visible cases.
2. Retain every original score and adjudicate disagreements transparently.
3. Permit at most one documented case/rubric revision based only on clarity and construct feedback, not policy outputs.
4. Construct a new calibration set whose reference labels are not reused from this dry run.
5. Freeze the calibration protocol, cases, reference labels, policy code, dependencies, tests, and hashes before executing policy comparisons.

The manuscript must continue to describe novelty and effectiveness as provisional.
