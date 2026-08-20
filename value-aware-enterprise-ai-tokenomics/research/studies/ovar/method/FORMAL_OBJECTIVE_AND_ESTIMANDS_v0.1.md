# Formal Objective and Estimands v0.1

**Status:** prospective design draft; not frozen  
**Applies to:** narrowed outcome-evidence-ledger study

## 1. Decision problem

For project or episode `i`, a policy `p` observes only the information allowed by its accounting treatment and chooses:

```text
D_i(p) ∈ {STOP, REVISE, CONTINUE_PILOT, SCALE, INDETERMINATE}
```

The reference decision `D_i*` is derived from investigator-only ground truth in a constructed pilot or from a prospectively specified causal and evidence-adjudication procedure in a field study. No policy may access `D_i*` or hidden outcome validity when making its decision.

## 2. Comparator information sets

| Policy | Information available at decision time |
|---|---|
| `USAGE_ONLY` | token/call volume, active users, and budget utilization |
| `SELF_REPORTED_VALUE` | usage plus owner-reported time, quality, and benefit |
| `COST_QUALITY` | reconciled direct cost plus technical success/quality |
| `OUTCOME_FLAT` | outcome contract, evidence, baseline, attribution, and fully loaded cost without hierarchy |
| `OVAR_LEDGER` | full outcome-evidence ledger, uncertainty, risk, decision receipt, and applicable access/exploration constraints |

Model routing, prompt compression, and token minimization are optimization treatments rather than primary accounting-policy comparators. They may be embedded consistently across policies or evaluated in a secondary factorial analysis.

## 3. Reference classification

For monetary outcomes, define:

```text
N_i = A_i × (Y_i(1) - Y_i(0)) - C_i - H_i
```

where:

- `Y_i(1)` is the measured outcome with AI;
- `Y_i(0)` is the registered counterfactual outcome estimate;
- `A_i ∈ [0,1]` is attribution confidence;
- `C_i` is fully loaded AI cost;
- `H_i` is expected harm or risk cost under the registered model.

The reference ROI state is:

```text
POSITIVE      if the lower uncertainty bound of N_i exceeds 0
NEGATIVE      if the upper uncertainty bound of N_i is below 0
NEUTRAL       if the interval lies inside a frozen practical-equivalence margin
INDETERMINATE otherwise or if mandatory evidence is insufficient
```

Non-monetary outcomes remain separate. A project cannot be declared financially positive solely from a favorable non-monetary score.

## 4. Primary estimands

Let `P` be the target portfolio distribution and `p` a policy.

### E1: False-positive ROI rate

```text
FPR_ROI(p) = Pr(policy says POSITIVE | reference is NEGATIVE, NEUTRAL, or INDETERMINATE)
```

Primary contrast:

```text
ΔFPR(p) = FPR_ROI(OVAR_LEDGER) - FPR_ROI(p)
```

for `p ∈ {USAGE_ONLY, SELF_REPORTED_VALUE, COST_QUALITY}`.

### E2: False-scale rate

```text
FSR(p) = Pr(D_i(p) = SCALE | D_i* ∈ {STOP, REVISE, INDETERMINATE})
```

### E3: False-stop rate

```text
FSTOP(p) = Pr(D_i(p) = STOP | D_i* ∈ {CONTINUE_PILOT, SCALE})
```

### E4: Decision loss

```text
L(p) = w_FP × false_positive_ROI
     + w_FS × false_scale
     + w_FSTOP × false_stop
     + w_R × risk_or_compliance_violation
     + w_M × normalized_measurement_cost
```

Weights must be elicited and frozen before outcome-bearing evaluation. Report every component even when a composite is used.

## 5. Secondary estimands

- classification accuracy and macro-F1 across ROI states;
- Brier score or multiclass log loss for probabilistic classifications;
- calibration slope/intercept and reliability by attribution-confidence band;
- proportion of decisions changed when indirect, human-review, and rework costs are added;
- cost per correctly classified project;
- measurement time and monetary burden;
- verified portfolio value under matched resource budget;
- allocation regret versus an oracle in constructed simulation only;
- stranded internal budget and reserve utilization;
- minimum-access, exploration, and concentration violations;
- results stratified by domain, project maturity, evidence quality, and outcome delay.

## 6. Candidate hypotheses and provisional success conditions

These thresholds are design candidates, not registered criteria.

| Hypothesis | Candidate success condition |
|---|---|
| H1 | `OVAR_LEDGER` reduces false-positive ROI by at least 15 percentage points versus `USAGE_ONLY`, and the paired 95% interval excludes zero |
| H2 | `OVAR_LEDGER` reduces false-scale by at least 10 percentage points versus `SELF_REPORTED_VALUE` without increasing false-stop by more than 5 points |
| H3 | Fully loaded cost changes the reference ROI state in at least 15% of eligible cases relative to direct provider cost alone |
| H4 | Attribution-confidence calibration improves Brier score by at least 10% relative to an uncalibrated confidence baseline |
| H5 | Outcome-linked allocation is non-dominated on verified portfolio value, risk violations, and allocation/measurement cost under matched budget |

The pilot must assess whether these thresholds are identifiable and whether adequate sample size is feasible. Thresholds may be revised once using construct and pilot evidence only, with the reason logged before test-case generation.

## 7. Analysis principles

- Use paired comparisons because every policy evaluates the same eligible case.
- Report exact denominators and exclude no case silently.
- Use bootstrap intervals stratified by domain or exact/randomization inference when assumptions warrant.
- Separate design, calibration, and test partitions.
- Evaluate ledger completeness and outcome-reference reliability separately from decision-policy performance.
- Conduct sensitivity analyses over baseline validity, attribution confidence, cost boundaries, delayed outcomes, and uncertain monetary conversion.
- Preserve `INDETERMINATE` as an outcome; do not force missing evidence into positive or negative ROI.

## 8. Required pilot design checks

Before freezing the analysis plan, the pilot must demonstrate:

1. each policy can be executed using only its permitted fields;
2. reference labels are deterministically reproducible;
3. outcome evidence and hidden labels are leakage-separated;
4. all five decision outcomes occur;
5. both false-positive and false-negative cases are represented;
6. fully loaded cost changes some decisions but does not mechanically determine all decisions;
7. outcome verification has measurable cost;
8. access and exploration constraints bind in some allocation scenarios;
9. ties have deterministic rules;
10. every decision produces a versioned receipt.

## 9. Current claim boundary

This document defines proposed estimands only. It contains no evidence that the ledger improves decision quality, ROI, allocation, or production success.

