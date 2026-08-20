# Hypothesis Registry

## Prospective Hypotheses (Frozen)

### H1: Rank Reversal Rate
**Hypothesis:** ≥20% of method-study combinations will show rank reversals between single-metric and multi-criteria evaluation.

**Estimand:** Count of (method, study) pairs where single-metric rank differs from multi-criteria rank by ≥2 positions, divided by total pairs.

**Decision Rule:** PASS if observed ≥ 0.20; FAIL otherwise.

**Status:** PENDING

---

### H2: Multi-Criteria Failure
**Hypothesis:** ≥1 method will pass single-metric threshold but fail ≥2 deployment criteria.

**Estimand:** Binary indicator of existence.

**Decision Rule:** PASS if ≥1 such method exists; FAIL otherwise.

**Status:** PENDING

---

### H3: Decision Instability
**Hypothesis:** ≥15% of cases will show decision changes under ±10% threshold perturbation.

**Estimand:** Cases with decision change under threshold sensitivity / total cases.

**Decision Rule:** PASS if observed ≥ 0.15; FAIL otherwise.

**Status:** PENDING

---

## Evidence Sources

### RAER v2 (Immutable)
- **Location**: `../../applied-ai-research-lab/action-evidence-safety-research/studies/raer/evaluation/v2/results_design_v1.0/`
- **Files**:
  - `oof_policy_outcomes.csv`
  - `oof_policy_summary.csv`
  - `v2_design_gate.json`
  - `bootstrap_intervals.json`

### OVAR v1.0 (Immutable)
- **Location**: `../../applied-ai-research-lab/value-aware-enterprise-ai-tokenomics/studies/ovar/calibration/`
- **Files**: TBD (to be located)

### VDCM (Immutable)
- **Location**: `../../applied-ai-research-lab/storypoints-age-of-ai/papers/thinkai-2026/results/`
- **Files**: TBD (to be located)

---

## Analysis Boundary

**Pre-execution Lock Date**: 2026-08-20  
**No retrospective hypothesis modification permitted**  
**Negative results are reportable outcomes**
