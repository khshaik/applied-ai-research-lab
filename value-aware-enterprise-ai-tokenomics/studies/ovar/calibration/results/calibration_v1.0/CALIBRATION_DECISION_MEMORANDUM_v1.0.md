# OVAR Prospective Calibration Decision Memorandum v1.0

## Decision

**STOP OVAR calibration v1.0; do not construct or open a held-out benchmark for this version.**

The calibration passed five of nine mandatory criteria and failed four. The result is a prospective negative calibration result on constructed cases, not a field-effect estimate.

## Results

| Policy | False-positive ROI | False scale | False stop | Authorization violation | Exact action | Indeterminate | Weighted loss |
|---|---:|---:|---:|---:|---:|---:|---:|
| Usage only | 100.0% | 42.9% | 0.0% | 10.4% | 4.2% | 0.0% | 4.573 |
| Self-reported value | 100.0% | 97.1% | 0.0% | 10.4% | 12.5% | 0.0% | 6.769 |
| Cost and quality | 100.0% | 65.7% | 0.0% | 10.4% | 25.0% | 0.0% | 5.562 |
| Outcome flat | 5.7% | 5.7% | 0.0% | 4.2% | 66.7% | 25.0% | 1.001 |
| OVAR ledger | 5.7% | 0.0% | 15.4% | 4.2% | 52.1% | 25.0% | 1.155 |

Denominators were 35 non-positive ROI references, 35 references that should not scale, and 13 safe continue/scale references.

## Criteria passed

- all pre-execution tests and hashes passed;
- OVAR false-positive ROI was lower than usage-only and self-report;
- OVAR false-scale was no worse than outcome-flat;
- indeterminate rate was within 30%;
- no domain had more than one OVAR false-scale or false-stop error.

## Criteria failed

1. OVAR produced two authorization-related harmful actions (`OC-R032`, `OC-R037`).
2. OVAR false-stop was 2/13 (15.4%), above the allowed best-comparator-plus-10-point limit (`OC-R004`, `OC-R011`).
3. Outcome-flat had lower weighted loss and lower measurement burden.
4. Outcome-flat dominated OVAR at every registered burden weight from 0.25 through 1.00.

## Failure mechanism

The frozen text classifier did not reason about authorization scope and time precisely enough.

- `OC-R032` and `OC-R037` contained approvals with explicit 2026 expiry dates. At the August 2026 decision date, the records were expired. The text classifier detected conditional wording but did not compare dates, allowing continued action.
- `OC-R004` and `OC-R011` described an authorized studied scope plus a different excluded scope. The classifier treated any absent/out-of-scope phrase as applying to the whole project and stopped otherwise valid in-scope work.

The risk tier also used coarse lexical rules and estimated harm as a fixed fraction of cost. This did not generate the four binding errors directly, but it is too crude for a strong operational claim.

## Interpretation

The hypothesis that OVAR v1.0 would achieve a non-dominated authorization-sensitive calibration position was **not supported**. OVAR eliminated false-scale decisions compared with outcome-flat, but did so by introducing false stops, without resolving expired authorization records. The additional governance burden therefore did not produce a superior composite decision policy.

This does not show that outcome-evidence accounting is useless. Outcome-flat substantially outperformed usage, self-report, and cost-quality proxies on the constructed set. The negative finding is narrower: unstructured text heuristics are inadequate for authorization-sensitive decision control.

## Research direction

The defensible paper framing is a methods and prospective negative-results study:

> Outcome evidence sharply reduced proxy-accounting errors, but adding authorization safeguards through unstructured lexical rules failed to produce a non-dominated policy because temporal and scoped authorization semantics were not reliably resolved.

A future OVAR v2 should use structured authorization records containing subject, resource, action, jurisdiction, valid-from, valid-until, revocation status, required signer, and decision timestamp. It must be designed against newly constructed cases and preregistered before evaluation; the current 48 cases are permanently design-exposed.

## Claim boundary

Do not state that OVAR was validated, superior, deployable, or proven to improve enterprise ROI. Permissible statements are limited to prospective constructed-calibration behavior and the identified authorization failure mechanism.
