# Gate 3 Future Empirical Propositions

**Status:** Preregisterable propositions for Route A; not claims tested by Route B.

## Information cutoff and comparators

At commitment cutoff `t0`, archive work/task controls, intended AI mode and stage automation enablement, evidence-readiness vector, forecast RHTD matrix, available capacity and existing queued work by role, actual team Story Points, and HIE-compatible **pre-task** variables.

Use identical outcomes, folds, time windows, and information cutoffs for:

- B0: historical/base-rate model with team/project/time controls;
- B1: Story Points;
- B2: pre-task HIE-compatible predictors;
- B3: Story Points + HIE-compatible predictors;
- C1: VDCM/RSDRI;
- C2: VDCM + Story Points/HIE, testing incremental rather than replacement value.

Execution-log HIE indicators may be used as a post-hoc explanatory/oracle benchmark, not as a fair prospective comparator.

## Propositions

**P1 — Incremental touch-demand validity.** At `t0`, the VDCM role-stage model improves held-out prediction of total and role-stage human touch time over B0–B3.

**P2 — Bottleneck and queue validity.** Conditional on role capacity and existing workload, the disaggregated RHTD profile predicts constrained-role queue delay and end-to-end cycle time better than an equal-information aggregate-effort score.

**P3 — Completion calibration.** Forecasts combining RHTD, capacity, existing queues, and readiness produce better calibrated completion probabilities than B0–B3.

**P4 — Readiness-risk association.** Pre-commitment readiness deficits predict subsequent rework, UAT rejection, and defined quality failures after adjustment for risk, coupling, change size, team/project, and AI mode. This is predictive association unless readiness is experimentally manipulated.

**P5 — Work-redistribution moderation.** As AI generation intensity rises, implementation touch time falls as a share of total touch time while verification/review/test share rises more strongly for high-coupling, high-risk, or context-deficient work. The proposition allows no change or reversal.

**P6 — Role-specific overload validity.** Role capacity pressure predicts queue growth, unfinished work, and quality degradation more accurately than aggregate sprint load.

**P7 — Transportability boundary.** Calibration and incremental benefit vary by team, tool maturity, and domain risk; temporal and leave-team/project-out evaluation will quantify degradation rather than assume universal transportability.

## Evaluation rules

- Touch prediction: paired out-of-sample MAE/WAPE or quantile/pinball loss with uncertainty.
- Completion: Brier score, log loss, calibration intercept/slope, and reliability plots.
- Cycle/queue time: distributional/quantile error, not only mean error.
- Validation: rolling-origin temporal validation plus leave-team/project-out evaluation; tuning nested inside training data.
- Uncertainty: cluster/bootstrap or hierarchical uncertainty appropriate to items nested in teams.
- Missingness and sparse quality events: rules defined before outcome inspection.
- Story Points: modeled within team or normalized through team-specific effects; never treated as directly comparable raw units across teams.

## Leakage controls

- archive the complete `t0` feature snapshot;
- fit preprocessing only on training folds;
- avoid random item splits across adjacent releases or dependent work;
- keep post-`t0` evidence out of readiness predictors;
- version anchors, tools, models, and process changes;
- do not train only on completed work.

## Future Route A sequence

1. prospective shadow-mode study: teams keep normal Story Points while RSDRI is recorded independently at `t0`;
2. low-burden multi-role touch sampling plus workflow timestamps for queues;
3. prespecified quality outcomes and observation windows;
4. simulation-based power/precision planning based on primary estimand;
5. temporal and external-team validation with null/negative result reporting;
6. only after predictive and measurement validity, evaluate planning use through a randomized or stepped-wedge rollout where feasible.
