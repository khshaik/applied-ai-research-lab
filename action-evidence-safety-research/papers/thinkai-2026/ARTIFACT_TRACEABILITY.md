# RAER artifact and claim traceability

This index identifies the core, non-documentary artifacts that make the reported calculations and research decisions independently traceable. These files should be preserved even if manuscript formats change.

## Frozen design and method

- [`RAER_V2_METHOD_SPECIFICATION_v1.0.json`](../../studies/raer/evaluation/v2/RAER_V2_METHOD_SPECIFICATION_v1.0.json): objective, candidate grid, policy behavior, and configuration space.
- [`RAER_V2_PROSPECTIVE_DESIGN_PLAN_v1.0.json`](../../studies/raer/evaluation/v2/RAER_V2_PROSPECTIVE_DESIGN_PLAN_v1.0.json): data boundary, six-fold procedure, metrics, thresholds, tie breaks, and all-required gate.
- [`RAER_V2_PRE_EXECUTION_LOCK_v1.0.json`](../../studies/raer/integrity/RAER_V2_PRE_EXECUTION_LOCK_v1.0.json): pre-execution artifact lock.

## Benchmark provenance and scoring

Preserve the entire [`release_v1.1/`](../../studies/raer/calibration/benchmark/release_v1.1/) folder. Its essential records are the reviewer-visible cases/schema, scenario provenance, label-blind split manifest, two reviewer score/finding files, disagreement register, adjudication register, adjudicated master scores, review agreement, independent quality audit, and post-review closure.

## Executable implementation and tests

- [`raer_v2_design.py`](../../studies/raer/evaluation/v2/raer_v2_design.py): v2 design evaluator.
- [`test_raer_v2_design.py`](../../studies/raer/evaluation/v2/test_raer_v2_design.py): deterministic v2 tests.
- [`verify_v2_design_closure.py`](../../studies/raer/evaluation/v2/verify_v2_design_closure.py): closure verification.
- [`raer_benchmark.py`](../../studies/raer/evaluation/raer_benchmark.py), [`evaluate_decision_gate.py`](../../studies/raer/evaluation/evaluate_decision_gate.py), and [`test_raer_benchmark.py`](../../studies/raer/evaluation/test_raer_benchmark.py): v1 benchmark/evaluation chain.

## Raw outcomes, calculations, and metrics

Preserve the entire [`results_design_v1.0/`](../../studies/raer/evaluation/v2/results_design_v1.0/) folder:

- `oof_policy_outcomes.csv`: row-level out-of-fold outcomes.
- `oof_policy_summary.csv`: policy-level out-of-fold metrics.
- `outer_fold_selection.csv`: fold-specific selected configurations and eligibility.
- `all_design_configuration_summary.csv`: full design-grid summaries.
- `final_design_fit_outcomes.csv`: fitted all-design descriptive outcomes.
- `bootstrap_intervals.json`: 10,000-replicate domain-stratified intervals.
- `ablations.csv`: descriptive component-removal results.
- `v2_design_gate.json`: authoritative criteria, metrics, final configuration, decision, and held-out status.
- `design_manifest.json`: result-package provenance.

## V1 failure and stopping evidence

- [`validation_v1.0/decision_gate.json`](../../studies/raer/evaluation/results/validation_v1.0/decision_gate.json): `STOP_BEFORE_HELD_OUT` and 8/11 safe completion.
- [`validation_v1.0/policy_summary.csv`](../../studies/raer/evaluation/results/validation_v1.0/policy_summary.csv): exact comparator counts and costs.
- [`VALIDATION_STOP_RECORD_v1.0.json`](../../studies/raer/integrity/VALIDATION_STOP_RECORD_v1.0.json): immutable stop record.
- [`V1_SUPPLEMENTARY_CLOSURE_MANIFEST_v1.0.json`](../../studies/raer/integrity/V1_SUPPLEMENTARY_CLOSURE_MANIFEST_v1.0.json): v1 supplementary closure.

## Publication integrity

- [`RAER_Claim_to_Evidence_Ledger_v0.2.csv`](../../studies/raer/integrity/RAER_Claim_to_Evidence_Ledger_v0.2.csv): claim, evidence locator, status, and permitted wording.
- [`RAER_Citation_Verification_Log_v0.2.csv`](../../studies/raer/integrity/RAER_Citation_Verification_Log_v0.2.csv): all 16 references and their primary URLs.
- [`V2_DESIGN_CLOSURE_MANIFEST_v1.0.json`](../../studies/raer/integrity/V2_DESIGN_CLOSURE_MANIFEST_v1.0.json): 15-artifact SHA-256 closure, no held-out access, and research boundary.

## Files that must remain excluded

Do not commit or publish the investigator label vault, restricted coordinator workbook, label-access log, or `held_out_test_labels_v1.1.json`. The held-out partition remains sealed; its absence is a negative control and a scientific integrity feature.

## Supported calculations

- RAER v2 safe completion: 25/27 = 92.6%.
- RAER v2 harmful action: 14/45 = 31.1%.
- RAER v2 mean normalized check cost: 0.547.
- `FIXED_0.20`: 27/27 safe completion, 18/45 harmful actions, mean cost 0.800.
- Positive-slack rate: 12/72 = 16.7%; mean slack 0.0083; maximum slack 0.05.
- Fold stability: 6/6 eligible outer folds.
- Authorization harms: 0 out of fold; removing the authorization safeguard produced 7 in the fitted-design ablation.
- Overall decision: 7/8 criteria passed, therefore `FAIL_KEEP_HELD_OUT_SEALED`.

