# OVAR Calibration Reference-Adjudication Protocol v1.0

**Status:** frozen before reference creation  
**Reference creator access:** calibration candidate v1.1 and this protocol only  
**Prohibited access:** policy code, pilot cases/labels/results, comparator outputs, construct-review scores, other reference work

## 1. Purpose

Create deterministic investigator-only reference records for the 48 constructed calibration cases. Reference decisions must represent the constructed case facts and this rule, not the expected behavior of OVAR or any comparator.

## 2. Hidden reference fields

For every case, record:

- `review_case_id`;
- `reference_incremental_value`;
- `reference_fully_loaded_cost`;
- `reference_expected_harm_cost`;
- `reference_net_value`;
- `reference_lower_bound` and `reference_upper_bound`;
- `reference_evidence_sufficient`;
- `reference_authorization_current`;
- `reference_roi_state`;
- `reference_action`;
- concise evidence, authorization, arithmetic, and action rationales;
- `label_version = 1.0`.

## 3. Arithmetic

```text
reference_fully_loaded_cost
  = provider + infrastructure + tooling + human review
  + integration amortization + governance + rework
  + evidence-review cost

reference_net_value
  = reference_incremental_value
  - reference_fully_loaded_cost
  - reference_expected_harm_cost

reference_lower_bound = reference_net_value - reference_uncertainty_half_width
reference_upper_bound = reference_net_value + reference_uncertainty_half_width
```

The reference incremental value is a constructed latent value informed by the scenario but is not copied mechanically from owner-reported benefit or the visible attribution estimate. Fully loaded cost is mechanically reconciled from visible cost fields; no cost may be omitted.

## 4. Evidence sufficiency

Set `reference_evidence_sufficient = false` when any applies:

- no baseline estimate and no defensible comparator;
- evidence is unverified;
- a partial-evidence gap prevents reproduction of the primary outcome;
- outcome measurement has not matured enough to determine the contracted endpoint;
- shared or concurrent effects cannot be bounded sufficiently for the decision.

Partial evidence may still be sufficient when the primary outcome, comparator, and full cost can be reproduced and the remaining gap is represented in uncertainty.

## 5. Authorization

Set `reference_authorization_current = false` only when the factual authorization record is absent, expired, revoked, outside scope, or lacks a required signer at the decision checkpoint. Do not infer authorization failure merely because a case concerns regulated or sensitive work.

## 6. Expected harm

Assign a nonnegative constructed expected-harm cost using the documented risk facts, event count/exposure, severity, interception controls, and residual exposure. Use zero only when the case facts support negligible monetary harm; non-monetary safety/compliance conditions remain in the action rationale.

## 7. ROI state and action

- `INDETERMINATE` ROI and action when reference evidence is insufficient.
- `NEGATIVE` ROI and `STOP` when authorization is not current or the upper bound is below zero.
- `POSITIVE` ROI when the lower bound is above zero.
- `NEUTRAL` ROI when the interval includes zero.
- `SCALE` for positive ROI when `reference_net_value / reference_fully_loaded_cost >= 0.20` and authorization is current.
- `CONTINUE_PILOT` for positive ROI below that ratio.
- `REVISE` for neutral ROI with sufficient evidence and current authorization.

## 8. Distribution and integrity

Do not force a predetermined result distribution. All five actions must nevertheless be present for a useful calibration set; absence of an action triggers a design review, not relabeling. Record exact arithmetic and retain all labels, including inconvenient or unbalanced outcomes.

## 9. Claim boundary

These references are constructed ground truth for method calibration. They are not observed organizational ROI, actual harm estimates, or expert validation.
