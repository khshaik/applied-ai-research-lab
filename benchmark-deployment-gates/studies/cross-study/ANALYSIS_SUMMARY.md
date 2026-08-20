# Cross-Study Analysis Summary

**Date**: 2026-08-20  
**Studies**: RAER v2, OVAR v1.0, VDCM  
**Total Methods**: 19 (9 RAER + 5 OVAR + 5 VDCM)

---

## Hypothesis Test Results

### H1: Rank Reversal Rate ≥20%
**Result**: ❌ **FAIL**  
**Observed**: 10.5% (2/19 methods)  
**Threshold**: 20.0%

**Interpretation**: The hypothesis that ≥20% of methods would show rank reversals was **not supported**. Only 10.5% of method-study combinations showed reversals ≥2 positions between single-metric and multi-criteria rankings.

**Breakdown by Study**:
- **RAER**: 0/9 (0.0%) - No reversals
- **OVAR**: 0/5 (0.0%) - No reversals  
- **VDCM**: 2/5 (40.0%) - Two reversals detected

**Key Reversals**:
1. **Oracle** (VDCM): Ranked #1 on single metric → #4 on multi-criteria (magnitude: 3)
2. **HIE-Compatible** (VDCM): Ranked #4 on single metric → #2 on multi-criteria (magnitude: 2)

---

### H2: Multi-Criteria Failure ≥1 Method
**Result**: ✅ **PASS**  
**Observed**: 3 methods passed single metric but failed ≥2 deployment criteria

**Methods Identified**:

1. **OUTCOME_FLAT** (OVAR)
   - Single metric: 0.943 (94.3% ROI reduction)
   - Criteria passed: 4/9
   - Failed: Authorization violations

2. **OVAR_LEDGER** (OVAR)
   - Single metric: 0.943 (94.3% ROI reduction)
   - Criteria passed: 4/9
   - Failed: Authorization violations

3. **Story Points** (VDCM)
   - Single metric: 0.787
   - Criteria passed: 0/2
   - Failed: Scenario wins, Brier threshold

**Interpretation**: The hypothesis was **supported**. Multiple methods appeared successful on single metrics but failed when evaluated against comprehensive deployment gates.

---

### H3: Decision Instability ≥15%
**Result**: ❌ **FAIL**  
**Observed**: 0.0% (0/19 methods)  
**Threshold**: 15.0%

**Interpretation**: The hypothesis that ≥15% of cases would show decision changes under ±10% threshold perturbation was **not supported**. All methods showed stable decisions across threshold variations.

**Breakdown by Study**:
- **RAER**: 0/9 (0.0%) unstable
- **OVAR**: 0/5 (0.0%) unstable
- **VDCM**: 0/5 (0.0%) unstable

---

## Key Findings

### 1. Authorization Failures Across Studies
Both OVAR methods (OUTCOME_FLAT and OVAR_LEDGER) failed authorization criteria despite strong ROI reduction performance. This replicates the authorization failure pattern identified in the original OVAR study.

### 2. VDCM Shows Highest Reversal Rate
VDCM exhibited 40% rank reversals, driven by:
- Oracle method: Best single metric, poor multi-criteria (non-deployable)
- HIE-Compatible: Moderate single metric, strong multi-criteria

### 3. RAER Stability
RAER showed no rank reversals, suggesting alignment between single-metric (safe completion) and multi-criteria evaluation. However, RAER v2 failed its primary safe-completion gate (92.6% vs. required 95%).

### 4. Limited Evidence for Broad Instability
The low overall reversal rate (10.5%) and zero threshold instability suggest that:
- Single metrics may align with multi-criteria in some contexts
- The specific studies may have well-calibrated primary metrics
- Cross-study heterogeneity limits generalization

---

## Implications for Paper

### Strengths
1. ✅ H2 supported: Clear evidence of single-metric success masking deployment failures
2. ✅ Authorization failures replicated across OVAR methods
3. ✅ VDCM reversals demonstrate context-dependent metric alignment

### Challenges
1. ❌ H1 not supported: Lower reversal rate than hypothesized
2. ❌ H3 not supported: No threshold instability detected
3. ⚠️ Small sample size (19 methods across 3 studies)

### Recommended Framing
**Title Revision**: Consider softening from "When Benchmark Winners Fail" to "Multi-Criteria Deployment Gates Reveal Hidden Failures in AI Evaluation"

**Key Message**: While not all methods show rank reversals, **critical deployment failures (especially authorization) can be masked by favorable single-metric performance**. The OVAR authorization failures and VDCM oracle reversal provide concrete evidence.

**Contribution**: The **Minimum Responsible Benchmark Report Checklist** remains valuable regardless of hypothesis outcomes, as it codifies transparent multi-criteria reporting.

---

## Next Steps

1. **Generate Visualizations**
   - Rank reversal heatmap (emphasize VDCM)
   - Multi-criteria failure patterns (highlight authorization)
   - Study-level comparison

2. **Refine Paper Narrative**
   - Lead with H2 (supported) and authorization failures
   - Report H1 and H3 transparently as negative results
   - Emphasize checklist as primary contribution

3. **Create Result Tables**
   - Table 1: Cross-study method comparison
   - Table 2: Authorization failure details
   - Table 3: Hypothesis test summary

4. **Draft Discussion**
   - Limitations: Small sample, constructed cases, three studies
   - Generalizability: Context-dependent metric alignment
   - Future work: Larger cross-study analysis, real-world benchmarks

---

## Data Integrity

- ✅ All source data immutable and versioned
- ✅ Extraction scripts deterministic
- ✅ Analysis reproducible
- ✅ Hypothesis tests pre-registered
- ✅ Negative results preserved

**SHA-256 Hashes**: (To be computed for final submission)
