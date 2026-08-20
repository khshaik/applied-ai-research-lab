# Data Extraction Protocol v1.0

## Objective
Extract immutable results from RAER, OVAR, and VDCM for cross-study rank-reversal analysis.

## Source Integrity
All source files are frozen and versioned. No modification permitted.

## Extraction Schema

### Per-Study Extraction

#### RAER v2
**Source**: `oof_policy_outcomes.csv`, `oof_policy_summary.csv`

**Fields to Extract**:
- Policy ID
- Safe completion rate (single metric)
- Harmful action rate
- Mean validation cost
- Authorization failures
- False blocks
- Overall gate decision (PASS/FAIL)
- Criteria passed count (0-8)

**Single Metric**: Safe completion rate  
**Multi-Criteria**: Conjunctive gate (all 8 criteria)

---

#### OVAR v1.0
**Source**: Calibration results (to be located)

**Fields to Extract**:
- Policy ID
- False-positive ROI rate (single metric)
- False-scale rate
- False-stop rate
- Authorization violations
- Indeterminate rate
- Overall gate decision
- Criteria passed count (0-9)

**Single Metric**: False-positive ROI reduction  
**Multi-Criteria**: Conjunctive gate (all 9 criteria)

---

#### VDCM
**Source**: Developmental simulation results

**Fields to Extract**:
- Comparator ID
- Brier score (single metric)
- Scenario-level wins
- Calibration quality
- Burden score
- Overall assessment

**Single Metric**: Mean Brier score  
**Multi-Criteria**: Scenario-level performance + burden

---

## Normalization Rules

1. **Rank Calculation**: Within each study, rank methods by single metric (best = 1)
2. **Multi-Criteria Rank**: Rank by criteria passed count, then by single metric
3. **Reversal Detection**: |single_rank - multi_rank| ≥ 2
4. **Threshold Sensitivity**: Perturb thresholds by ±10%, ±20%

## Output Schema

```json
{
  "study": "RAER|OVAR|VDCM",
  "method_id": "string",
  "single_metric_value": "float",
  "single_metric_rank": "int",
  "criteria_passed": "int",
  "criteria_total": "int",
  "multi_criteria_rank": "int",
  "rank_reversal": "boolean",
  "reversal_magnitude": "int",
  "gate_decision": "PASS|FAIL",
  "failed_criteria": ["list"]
}
```

## Verification
- SHA-256 hash of source files
- Row count validation
- Range checks on extracted values
