# Paper Outline: When Benchmark Winners Fail Deployment Gates

**Target**: ThinkAI 2026 (6 pages)  
**Deadline**: 25 August 2026

## Title
When Benchmark Winners Fail Deployment Gates: A Cross-Study Analysis of Single-Metric Success Versus Multi-Criteria Readiness

## Abstract (150-200 words)
- Problem: Single metrics can mislead deployment decisions
- Method: Cross-study analysis of RAER, OVAR, VDCM
- Finding: [X]% rank reversals, [Y] methods pass single metric but fail gates
- Contribution: Minimum Responsible Benchmark Report Checklist

## 1. Introduction (1 page)
- AI evaluation often optimizes single metrics
- Deployment requires safety, cost, authorization, stability, burden
- NIST AI 800-2 emphasizes transparent, complete reporting
- **RQ**: How often do single-metric winners fail deployment gates?

## 2. Background (0.5 pages)
- RAER: Evidence revalidation (8 criteria, 72 cases)
- OVAR: Outcome-verified allocation (9 criteria, 48 cases)
- VDCM: Verified delivery capacity (5 comparators, 11 scenarios)
- All three: prospective negative results

## 3. Method (1 page)
### 3.1 Data Sources
- Immutable result sets from three studies
- 165 total evaluation instances

### 3.2 Analysis
- Single-metric ranking extraction
- Multi-criteria gate evaluation
- Rank-reversal detection (≥2 position change)
- Threshold sensitivity (±10%, ±20%)

### 3.3 Metrics
- Rank reversal rate
- Criteria failure distribution
- Decision stability index

## 4. Results (2 pages)
### 4.1 Rank Reversals
- Table 1: Cross-study rank comparison
- Figure 1: Rank-reversal heatmap

### 4.2 Multi-Criteria Failures
- Table 2: Methods passing single metric, failing gates
- Figure 2: Criteria failure patterns

### 4.3 Threshold Sensitivity
- Figure 3: Decision stability across threshold perturbations

### 4.4 Cross-Study Patterns
- Common failure modes
- Study-specific vulnerabilities

## 5. Discussion (1 page)
- Implications for AI evaluation practice
- NIST AI 800-2 alignment
- Limitations: constructed cases, three studies only
- Generalizability boundaries

## 6. Minimum Responsible Benchmark Report Checklist (0.5 pages)
- Pre-registration requirements
- Multi-criteria reporting
- Threshold sensitivity disclosure
- Negative result preservation

## 7. Conclusion (0.25 pages)
- Single metrics insufficient for deployment
- Conjunctive gates reveal hidden failures
- Checklist enables responsible reporting

## References
- NIST AI 800-2
- RAER, OVAR, VDCM papers
- Benchmark evaluation literature

## Figures (3)
1. Rank-reversal heatmap
2. Criteria failure patterns
3. Threshold sensitivity

## Tables (2)
1. Cross-study rank comparison
2. Single-metric pass, multi-criteria fail
