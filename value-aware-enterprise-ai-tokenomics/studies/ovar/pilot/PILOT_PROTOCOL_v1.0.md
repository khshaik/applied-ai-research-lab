# OVAR Constructed Pilot Protocol v1.0

**Protocol status:** frozen before pilot execution  
**Study type:** deterministic constructed-case method pilot  
**Framework:** Outcome-Verified AI Resource Allocation (OVAR)  
**Confirmatory status:** exploratory and non-confirmatory  

## 1. Purpose

This pilot tests whether the proposed outcome-evidence ledger can be implemented, replayed, audited, and compared with simpler enterprise AI accounting rules. It does not estimate real organizational ROI and cannot validate deployment effectiveness.

## 2. Primary research question

Can a prospective outcome-evidence ledger reduce false positive ROI classifications and incorrect stop/scale decisions relative to usage-only, self-reported-value, and direct-cost/technical-quality accounting on leakage-separated constructed cases?

## 3. Unit of analysis and scope

The unit is one proposed enterprise AI project decision at a defined measurement checkpoint. The pilot contains 24 cases: four cases in each of healthcare, financial services, e-commerce, transportation and logistics, cybersecurity, and customer operations.

Every case contains one reviewer-visible record and one investigator-only reference record. Cases are constructed for method testing and are not presented as records from real organizations.

## 4. Policies

Each policy receives only its permitted information set.

| Policy | Permitted information | Purpose |
|---|---|---|
| `USAGE_ONLY` | utilization, active users, token volume, provider cost, approved budget | represents consumption-led governance |
| `SELF_REPORTED_VALUE` | usage fields plus owner-reported benefit | represents benefit claims without independent outcome evidence |
| `COST_QUALITY` | direct model/infrastructure/tool cost plus technical quality | represents conventional cost-quality accounting |
| `OUTCOME_FLAT` | outcome contract, observed outcome, baseline, attribution confidence, evidence status, and fully loaded cost | isolates the value of outcome accounting without OVAR risk safeguards |
| `OVAR_LEDGER` | all reviewer-visible fields, including uncertainty, risk, compliance, and missing-evidence gates | proposed method |

## 5. Decision outputs

Each policy must return:

- ROI state: `POSITIVE`, `NEGATIVE`, `NEUTRAL`, or `INDETERMINATE`;
- action: `STOP`, `REVISE`, `CONTINUE_PILOT`, `SCALE`, or `INDETERMINATE`;
- reasons containing only permitted fields;
- a deterministic decision receipt with policy version and input-case hash.

## 6. Leakage controls

1. Reviewer-visible cases do not contain `true_*`, `reference_*`, hidden sufficiency, or realized-result fields.
2. Investigator reference labels are stored in a separate restricted file.
3. Policy functions accept a whitelisted view rather than the combined record.
4. Automated tests reject prohibited keys in reviewer-visible material and detect policy access outside its whitelist.
5. Reference labels are not used to tune thresholds after execution.

## 7. Reference decision

The investigator-only record contains deterministic ground truth for incremental outcome value, fully loaded cost, expected harm, uncertainty interval, evidence sufficiency, and compliance. The reference decision is assigned independently of any policy output:

- `STOP` for a compliance prohibition or an upper net-value bound below zero;
- `INDETERMINATE` when the reference evidence is insufficient;
- `SCALE` when the lower net-value bound is positive and the net-value-to-cost ratio is at least 0.20;
- `CONTINUE_PILOT` when the lower bound is positive but the ratio is below 0.20;
- `REVISE` when the interval crosses zero and evidence is sufficient.

## 8. Frozen policy thresholds

- Usage high threshold: 0.75; moderate threshold: 0.45.
- Self-reported positive margin: reported benefit exceeds provider cost; scale margin: at least 25% of provider cost.
- Technical-quality thresholds: 0.85 for scale and 0.70 for continued pilot.
- Minimum OVAR attribution confidence: 0.55.
- Practical-equivalence margin: ±5% of fully loaded cost.
- OVAR scale threshold: lower risk-adjusted net-value bound above zero and expected net-value-to-cost ratio at least 0.20.
- Mandatory OVAR stop: compliance status `PROHIBITED`.
- Mandatory OVAR indeterminate: absent outcome contract, unverified evidence, absent credible baseline, or attribution below 0.55.

## 9. Metrics

Primary:

1. false-positive ROI rate;
2. false-scale rate;
3. false-stop rate;
4. exact action agreement;
5. weighted decision loss.

Secondary:

- ROI-state accuracy;
- indeterminate rate;
- risk/compliance violations;
- mean normalized measurement burden;
- domain-level error counts;
- decision changes caused by fully loaded rather than direct cost.

The frozen decision-loss weights are: false-positive ROI 2, false-scale 4, false-stop 2, risk/compliance violation 8, and normalized measurement burden 0.5. All components will be reported separately.

## 10. Pilot gate

The pilot receives `GO_TO_CALIBRATION` only if all conditions pass:

1. all schema, leakage, determinism, and receipt tests pass;
2. every reference action category is represented;
3. `OVAR_LEDGER` has no compliance violation;
4. its false-positive ROI rate is lower than both `USAGE_ONLY` and `SELF_REPORTED_VALUE`;
5. no comparator has both lower weighted decision loss and lower measurement burden;
6. OVAR indeterminate rate is at most 25%;
7. no domain contains more than one OVAR false-scale or false-stop error.

`REVISE` applies when a traceable construct, schema, or implementation defect is identified without changing a threshold in response to a favorable or unfavorable result. `STOP_OR_PIVOT` applies if the method remains dominated after one documented revision.

## 11. Analysis

All cases are paired across policies. Counts and exact denominators will be reported. Because 24 deliberately stratified constructed cases are not a probability sample, confidence intervals will be descriptive only and will not be used to claim population effects. No post-result case replacement, threshold change, exclusion, or relabeling is permitted.

## 12. Known limitations

- constructed cases may encode investigator assumptions;
- case coverage is broad but shallow within each domain;
- deterministic labels simplify delayed, shared, and contested value;
- reviewer burden is estimated rather than observed until independent review occurs;
- this pilot does not test hierarchical allocation, carry-forward, organizational behavior, or field ROI.

## 13. Claim boundary

A passing pilot supports only implementation feasibility and progression to calibration. It does not establish originality beyond the completed novelty audit, causal organizational benefit, superiority in practice, or production readiness.
