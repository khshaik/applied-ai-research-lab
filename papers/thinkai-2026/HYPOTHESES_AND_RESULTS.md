# Benchmark Deployment Gates: Prospective Hypotheses and Results

## Research Question

How often would a method appear successful under a single headline metric but fail when safety, completion, cost, authorization, stability, and burden are evaluated jointly?

The hypotheses below were frozen before data extraction and analysis. They must not be revised after observing the outcome.

---

## H1 - Rank Reversal Rate (Primary)

**Hypothesis:** ≥20% of method-study combinations will show rank reversals of ≥2 positions between single-metric and multi-criteria evaluation.

**Estimand:** Count of (method, study) pairs where single-metric rank differs from multi-criteria rank by ≥2 positions, divided by total method-study pairs.

**Observed:** 2/19 = 0.1053 (10.5%). The required value was ≥0.20.

**Decision:** **FAIL**. H1 was not supported. Do not describe this as a pass or replace the threshold with a post-hoc value.

**Breakdown:**
- RAER: 0/9 (0.0%)
- OVAR: 0/5 (0.0%)
- VDCM: 2/5 (40.0%)

---

## H2 - Multi-Criteria Failure

**Hypothesis:** ≥1 method will pass single-metric threshold (>0.5) but fail ≥2 deployment criteria.

**Observed:** 3 methods identified:
1. OUTCOME_FLAT (OVAR): 0.943 single metric, 4/9 criteria passed, authorization failures
2. OVAR_LEDGER (OVAR): 0.943 single metric, 4/9 criteria passed, authorization failures
3. Story Points (VDCM): 0.787 single metric, 0/2 criteria passed, scenario wins + Brier threshold failures

**Decision:** **PASS**. H2 was supported. Multiple methods showed single-metric success masking deployment failures.

---

## H3 - Decision Instability

**Hypothesis:** ≥15% of cases will show decision changes under ±10% threshold perturbation.

**Estimand:** Cases with decision change under threshold sensitivity / total cases.

**Observed:** 0/19 = 0.0000 (0.0%). The required value was ≥0.15.

**Decision:** **FAIL**. H3 was not supported. All methods showed stable decisions across threshold variations.

**Breakdown:**
- RAER: 0/9 (0.0%) unstable
- OVAR: 0/5 (0.0%) unstable
- VDCM: 0/5 (0.0%) unstable

---

## Registered Overall Decision

H1 and H3 failed; H2 passed. The composite hypothesis was **partially supported**. The study successfully identified methods with single-metric success masking deployment failures (H2), but did not observe the expected rate of rank reversals (H1) or threshold instability (H3).

---

## Plain-Language Explanation

This cross-study analysis examined whether AI evaluation methods that succeed on a single metric still succeed when evaluated against comprehensive deployment criteria. We found that while rank reversals were less common than expected (10.5% vs. 20% threshold), **critical deployment failures can hide behind favorable single metrics**. Notably, both OVAR methods showed 94% ROI reduction but failed authorization criteria—a deployment blocker. This demonstrates that multi-criteria evaluation is essential, even when single metrics appear well-calibrated.

---

## Authoritative Evidence

### Data Sources (Immutable)
- RAER v2: `../../applied-ai-research-lab/action-evidence-safety-research/studies/raer/evaluation/v2/results_design_v1.0/`
- OVAR v1.0: `../../applied-ai-research-lab/value-aware-enterprise-ai-tokenomics/research/studies/ovar/calibration/results/calibration_v1.0/`
- VDCM: `../../applied-ai-research-lab/storypoints-age-of-ai/papers/thinkai-2026/results/developmental_simulation_v2/`

### Analysis Outputs
- [`rank_reversal_analysis.json`](../../studies/cross-study/results/rank_reversal_analysis.json)
- [`threshold_sensitivity.json`](../../studies/cross-study/results/threshold_sensitivity.json)
- [`ANALYSIS_SUMMARY.md`](../../studies/cross-study/ANALYSIS_SUMMARY.md)

### Extracted Data
- [`raer_extracted.json`](../../studies/cross-study/data/raer_extracted.json)
- [`ovar_extracted.json`](../../studies/cross-study/data/ovar_extracted.json)
- [`vdcm_extracted.json`](../../studies/cross-study/data/vdcm_extracted.json)

---

## Hypothesis Test Summary Table

| Hypothesis | Threshold | Observed | Result | Key Finding |
|------------|-----------|----------|--------|-------------|
| H1: Rank Reversals | ≥20% | 10.5% | FAIL | Lower than expected, but VDCM showed 40% |
| H2: Multi-Criteria Failures | ≥1 method | 3 methods | **PASS** | **Authorization failures in OVAR, criteria failures in VDCM** |
| H3: Decision Instability | ≥15% | 0.0% | FAIL | All methods stable across thresholds |

---

## Scientific Interpretation

The partial support for the composite hypothesis indicates that:

1. **Single-metric success can mask critical failures** (H2 supported) - This is the primary contribution
2. **Rank reversals are context-dependent** (H1 not supported) - VDCM showed 40%, RAER/OVAR showed 0%
3. **Decision boundaries are robust** (H3 not supported) - Methods have stable thresholds

The **authorization failure pattern** in OVAR is particularly significant: both methods failed the same criterion despite different designs, suggesting a systematic gap in single-metric evaluation that multi-criteria gates can catch.

---

## Permitted Conclusions

✅ **Supported:**
- Multi-criteria evaluation reveals deployment failures masked by single metrics
- Authorization failures can persist across method variations
- Context-dependent metric alignment exists (VDCM vs. RAER/OVAR)

❌ **Not Supported:**
- Universal high rate of rank reversals (10.5% < 20% threshold)
- Widespread threshold instability (0% < 15% threshold)

⚠️ **Limitations:**
- Small sample size (19 methods across 3 studies)
- Constructed cases (not real-world benchmarks)
- Cross-study heterogeneity limits generalization
