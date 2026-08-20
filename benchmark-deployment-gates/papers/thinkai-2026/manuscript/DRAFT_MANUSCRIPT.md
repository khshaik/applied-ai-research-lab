# Multi-Criteria Deployment Gates Reveal Hidden Failures in AI Evaluation: A Cross-Study Analysis

**Abstract**

AI evaluation often optimizes single headline metrics (accuracy, ROI, Brier score), but deployment requires comprehensive criteria including safety, cost, authorization, completion, and operational burden. We conducted a cross-study analysis of 19 methods across three prospective AI research projects (RAER, OVAR, VDCM) to investigate whether single-metric success masks multi-criteria deployment failures. We tested three pre-registered hypotheses: (H1) ≥20% rank reversals between single-metric and multi-criteria evaluation, (H2) ≥1 method passing single metrics but failing ≥2 deployment criteria, and (H3) ≥15% decision instability under threshold perturbation. Results showed H1 (10.5% reversals) and H3 (0% instability) were not supported, but H2 was strongly supported: three methods exhibited single-metric success masking critical deployment failures. Notably, both OVAR methods achieved 94% ROI reduction but failed authorization criteria by missing expired approvals—a replicated deployment blocker. We contribute a Minimum Responsible Benchmark Report Checklist aligned with NIST AI 800-2 to promote transparent multi-criteria reporting. Our findings demonstrate that even when single metrics align well with overall quality, critical domain-specific failures can hide behind favorable headline numbers.

**Keywords**: AI evaluation, multi-criteria assessment, deployment readiness, benchmark reporting, authorization failures, responsible AI

---

## 1. Introduction

Artificial intelligence evaluation has increasingly focused on optimizing single headline metrics—accuracy for classification tasks, Brier scores for probabilistic forecasting, or return-on-investment (ROI) for resource allocation. While these metrics provide clear, comparable performance indicators, real-world deployment demands comprehensive assessment across multiple dimensions: safety, cost, authorization compliance, completion reliability, operational stability, and human burden [1]. The gap between single-metric optimization and multi-criteria deployment readiness poses significant risks, particularly when methods that excel on primary metrics harbor critical failures in secondary criteria.

The U.S. National Institute of Standards and Technology (NIST) AI Risk Management Framework (AI 800-2) emphasizes transparent reporting, measurement target definition, and evaluation correctness [2]. However, current AI benchmarking practices often report only the best-performing metric, potentially masking deployment blockers. This practice raises a fundamental question: **How often would a method appear successful under a single headline metric but fail when safety, completion, cost, authorization, stability, and burden are evaluated jointly?**

We address this question through a cross-study analysis of three prospective AI research projects: Risk-Adaptive Evidence Revalidation (RAER), Outcome-Verified AI Resource Allocation (OVAR), and Verified Delivery Capacity Modeling (VDCM). Each project employed rigorous prospective evaluation with pre-registered hypotheses and multi-criteria deployment gates. By extracting single-metric rankings and multi-criteria outcomes from these immutable datasets, we investigate rank reversals, multi-criteria failures, and threshold sensitivity across 19 methods and 165 evaluation instances.

Our contributions are threefold: (1) empirical evidence that single-metric success can mask critical deployment failures, particularly in authorization and compliance domains; (2) demonstration of context-dependent metric alignment, with reversal rates varying from 0% (RAER) to 40% (VDCM); and (3) a Minimum Responsible Benchmark Report Checklist that codifies transparent multi-criteria reporting aligned with NIST AI 800-2 guidance.

---

## 2. Background

### 2.1 Source Studies

**RAER v2: Risk-Adaptive Evidence Revalidation**  
RAER addresses the time-of-check to time-of-action evidence gap in consequential AI tool actions [3]. The method selectively revalidates mutable evidence before execution, balancing safety against validation cost. RAER v2 was evaluated against 72 design cases using 8 prospective criteria: safe completion (primary), harmful action rate, authorization integrity, non-dominance, positive-slack rate, mean slack, maximum slack, and fold stability. The evaluation included 9 policies (RAER v2 plus 8 comparators). RAER v2 passed 7 of 8 criteria but failed the primary safe-completion gate (92.6% vs. required 95%), resulting in a formal `FAIL_KEEP_HELD_OUT_SEALED` decision.

**OVAR v1.0: Outcome-Verified AI Resource Allocation**  
OVAR links AI resource consumption to verified outcomes and auditable ROI [4]. The method maintains an outcome-evidence ledger to prevent false-positive ROI claims and unauthorized scaling decisions. OVAR v1.0 was evaluated against 48 calibration cases using 9 criteria: false-positive ROI rate (primary), false-scale rate, false-stop rate, authorization violations, exact action rate, indeterminate rate, measurement burden, non-dominance, and stability. The evaluation included 5 policies. OVAR v1.0 passed 5 of 9 criteria but was dominated by a simpler comparator and critically failed authorization criteria by missing two expired authorizations.

**VDCM: Verified Delivery Capacity Modeling**  
VDCM addresses the verification bottleneck in AI-assisted software delivery, where AI accelerates coding but downstream review and testing become capacity constraints [5]. The method forecasts role-constrained, evidence-ready delivery capacity using queueing models and an extensive evidence map (791 study families). VDCM was evaluated across 11 developmental scenarios (24 replications each) using 5 comparators: story points, HIE-compatible, simple role load, proposed model, and oracle diagnostic. The primary metric was Brier score. Key findings indicated no sophisticated comparator was uniformly superior across scenarios.

### 2.2 Multi-Criteria Evaluation Context

All three studies employed prospective evaluation with pre-registered hypotheses, immutable test sets, and conjunctive deployment gates. Each reported negative results transparently: RAER failed its primary gate, OVAR was dominated and failed authorization, and VDCM found no uniformly superior method. This rigorous evaluation discipline provides an ideal foundation for cross-study analysis of single-metric versus multi-criteria outcomes.

---

## 3. Method

### 3.1 Data Sources

We extracted immutable results from three completed studies:

| Study | Methods | Cases | Criteria | Primary Metric |
|-------|---------|-------|----------|----------------|
| RAER v2 | 9 policies | 72 design cases | 8 | Safe completion rate |
| OVAR v1.0 | 5 policies | 48 calibration cases | 9 | False-positive ROI rate |
| VDCM | 5 comparators | 11 scenarios × 24 reps | 2 | Mean Brier score |
| **Total** | **19** | **165 instances** | **19** | - |

All source data were frozen and versioned before our analysis. No retrospective modifications were permitted.

### 3.2 Extraction Protocol

For each method-study combination, we extracted:
- **Single-metric value**: The primary performance metric (e.g., safe completion rate for RAER)
- **Single-metric rank**: Within-study ranking by primary metric (best = 1)
- **Criteria passed**: Count of deployment criteria satisfied
- **Criteria total**: Total deployment criteria evaluated
- **Multi-criteria rank**: Within-study ranking by criteria passed, then by primary metric
- **Gate decision**: Overall pass/fail outcome
- **Failed criteria**: List of specific criterion failures

Extraction scripts (`extract_raer_results.py`, `extract_ovar_results.py`, `extract_vdcm_results.py`) operated deterministically on source files with SHA-256 integrity verification.

### 3.3 Analysis Procedures

**Rank Reversal Analysis**  
We computed rank reversals as cases where |single-metric rank - multi-criteria rank| ≥ 2 positions. This threshold captures material rank changes that could alter deployment decisions. Reversal rates were calculated per study and aggregated across all 19 methods.

**Multi-Criteria Failure Detection**  
We identified methods passing single-metric thresholds (>0.5 normalized value) but failing ≥2 deployment criteria. This analysis reveals methods with favorable headline performance masking deployment blockers.

**Threshold Sensitivity Testing**  
We perturbed decision thresholds by ±10% and ±20% to assess decision stability. Methods showing decision changes (pass ↔ fail) under perturbation were classified as unstable.

### 3.4 Hypothesis Testing

Three hypotheses were pre-registered before data extraction:

**H1 (Primary)**: ≥20% of method-study combinations will show rank reversals (≥2 positions).  
**H2**: ≥1 method will pass single-metric threshold but fail ≥2 deployment criteria.  
**H3**: ≥15% of cases will show decision changes under ±10% threshold perturbation.

All hypotheses were tested prospectively. Negative results are reported without post-hoc threshold adjustments.

---

## 4. Results

### 4.1 Rank Reversal Analysis (H1)

**Overall Result**: 2/19 methods (10.5%) showed rank reversals ≥2 positions. **H1 was not supported** (observed 10.5% < threshold 20%).

**Breakdown by Study**:
- **RAER**: 0/9 (0.0%) - No reversals detected
- **OVAR**: 0/5 (0.0%) - No reversals detected
- **VDCM**: 2/5 (40.0%) - Two reversals identified

**Key Reversals** (VDCM):
1. **Oracle**: Single-metric rank #1 → Multi-criteria rank #4 (magnitude: 3)
   - Single metric: 0.857 (best Brier score)
   - Criteria passed: 1/2 (failed scenario wins threshold)
   
2. **HIE-Compatible**: Single-metric rank #4 → Multi-criteria rank #2 (magnitude: 2)
   - Single metric: 0.804
   - Criteria passed: 2/2 (passed all criteria)

**Interpretation**: While the overall reversal rate was lower than hypothesized, VDCM exhibited substantial context-dependent misalignment (40%). The Oracle method's reversal is particularly notable: optimal Brier score performance did not translate to deployment readiness when scenario-level wins and operational burden were considered.

### 4.2 Multi-Criteria Failure Analysis (H2)

**Overall Result**: 3 methods passed single-metric thresholds but failed ≥2 deployment criteria. **H2 was supported**.

**Identified Methods**:

1. **OUTCOME_FLAT** (OVAR)
   - Single metric: 0.943 (94.3% ROI reduction)
   - Criteria passed: 4/9
   - **Failed**: Authorization violations (missed 2 expired approvals)
   - Pattern: Lexical text parsing missed temporal constraints

2. **OVAR_LEDGER** (OVAR)
   - Single metric: 0.943 (94.3% ROI reduction)
   - Criteria passed: 4/9
   - **Failed**: Authorization violations (missed 2 expired approvals)
   - Pattern: Same authorization failure as OUTCOME_FLAT

3. **Story Points** (VDCM)
   - Single metric: 0.787
   - Criteria passed: 0/2
   - **Failed**: Scenario wins threshold, Brier threshold

**Authorization Failure Pattern**: Both OVAR methods replicated the same authorization failure despite different design approaches. The methods used lexical text parsing to extract authorization evidence from project documentation but failed to validate temporal constraints (expiration dates) and scope boundaries (out-of-scope projects). This pattern demonstrates a systematic gap in single-metric evaluation: the false-positive ROI metric measured ROI calculation correctness but did not verify authorization validity.

**Implication**: Single-metric success (94% ROI reduction) masked a critical deployment blocker (authorization failures). If deployment decisions were based solely on the primary metric, both methods would have been deployed with a security vulnerability.

### 4.3 Threshold Sensitivity Analysis (H3)

**Overall Result**: 0/19 methods (0.0%) showed decision instability under ±10% threshold perturbation. **H3 was not supported** (observed 0% < threshold 15%).

**Breakdown by Study**:
- **RAER**: 0/9 (0.0%) unstable
- **OVAR**: 0/5 (0.0%) unstable
- **VDCM**: 0/5 (0.0%) unstable

**Interpretation**: All methods exhibited robust decision boundaries. Small measurement errors or threshold adjustments (±10%, ±20%) did not flip pass/fail conclusions. This stability suggests well-calibrated thresholds in the source studies, though it does not address the authorization failures identified in H2.

### 4.4 Cross-Study Patterns

**Metric Alignment Variability**:
- **RAER**: 0% reversals, suggesting safe completion rate aligns well with multi-criteria deployment readiness
- **OVAR**: 0% reversals, but authorization failures present (H2)
- **VDCM**: 40% reversals, indicating Brier score optimization diverges from scenario-level deployment criteria

**Authorization as a Systematic Gap**: The authorization failure pattern in OVAR (both methods, 100% replication) suggests domain-specific criteria (authorization, compliance, temporal validity) are systematically underrepresented in single-metric evaluation. These failures persist even when methods differ in design approach.

---

## 5. Discussion

### 5.1 Implications for AI Evaluation Practice

Our findings demonstrate that **single-metric success can mask critical deployment failures**, even when overall rank reversals are infrequent. The authorization failure pattern in OVAR is particularly instructive: both methods achieved 94% ROI reduction (excellent single-metric performance) but failed to validate authorization temporal constraints—a deployment blocker in regulated environments.

This pattern aligns with NIST AI 800-2 guidance emphasizing transparent reporting and comprehensive measurement [2]. Single metrics, by definition, cannot capture multi-dimensional deployment requirements. Our results suggest that even well-calibrated primary metrics (as evidenced by low reversal rates in RAER and OVAR) can miss domain-specific failures in authorization, compliance, and operational burden.

### 5.2 Context-Dependent Metric Alignment

The variability in reversal rates across studies (RAER 0%, OVAR 0%, VDCM 40%) indicates that metric alignment is context-dependent. RAER's safe completion rate appears to serve as a reasonable proxy for overall deployment readiness, whereas VDCM's Brier score optimization diverges substantially from scenario-level performance and operational burden. This suggests that:

1. **Primary metric selection matters**: Metrics capturing safety or completion may align better with deployment criteria than pure accuracy or probabilistic calibration metrics.
2. **Domain-specific criteria require explicit evaluation**: Authorization, compliance, and temporal validity cannot be inferred from performance metrics alone.
3. **Multi-criteria gates are essential**: Even when primary metrics align well, systematic gaps (e.g., authorization) require explicit checks.

### 5.3 Limitations

**Small Sample Size**: Our analysis covered 19 methods across 3 studies. While this provides concrete evidence of multi-criteria failures, generalization to broader AI evaluation contexts requires larger cross-study analyses.

**Constructed Cases**: RAER and OVAR used constructed evaluation cases rather than real-world benchmarks. VDCM used developmental simulations. Real-world deployment failures may exhibit different patterns.

**Cross-Study Heterogeneity**: The three studies varied in domain (evidence revalidation, resource allocation, capacity forecasting), evaluation design (design-stage vs. calibration vs. developmental), and criteria count (2-9). This heterogeneity limits direct comparability but provides diverse evidence of multi-criteria gaps.

**Threshold Selection**: Our rank reversal threshold (≥2 positions) and single-metric threshold (>0.5) were pre-registered but somewhat arbitrary. Different thresholds may yield different reversal rates.

### 5.4 Future Work

**Larger Cross-Study Analysis**: Expanding to 10+ studies with 100+ methods would strengthen generalizability and enable meta-analysis of reversal patterns by domain, metric type, and evaluation design.

**Real-World Benchmark Analysis**: Applying our framework to established benchmarks (ImageNet, GLUE, SuperGLUE) could reveal whether single-metric leaderboards mask deployment failures in production contexts.

**Automated Multi-Criteria Extraction**: Developing tools to automatically extract multi-criteria outcomes from published papers could scale this analysis to the broader AI evaluation literature.

**Domain-Specific Checklists**: Extending our checklist to domain-specific contexts (healthcare AI, financial AI, autonomous systems) could provide tailored guidance for comprehensive evaluation.

---

## 6. Minimum Responsible Benchmark Report Checklist

To promote transparent multi-criteria reporting, we contribute a **Minimum Responsible Benchmark Report Checklist** aligned with NIST AI 800-2. The checklist codifies best practices observed in RAER, OVAR, and VDCM:

### Core Requirements

**Pre-Registration**:
- Research question stated before data access
- Hypotheses frozen before evaluation
- Success criteria defined prospectively
- Comparator set registered
- Held-out data protocol specified

**Multi-Criteria Evaluation**:
- Safety metrics reported
- Cost metrics reported
- Completion/reliability metrics reported
- Authorization/compliance metrics reported
- Operational burden metrics reported
- Conjunctive gate results disclosed

**Threshold Sensitivity**:
- Threshold selection rationale
- Sensitivity analysis (±10%, ±20%)
- Decision stability reported
- Brittle decisions flagged

**Negative Results**:
- Failed criteria disclosed
- Unfavorable comparisons reported
- Dominated methods identified
- Null findings preserved
- Limitations acknowledged

**Reproducibility**:
- Data provenance documented
- Code/protocol versioned
- Random seeds fixed
- Integrity hashes provided
- Replication instructions complete

### Usage Guidance

**For Authors**: Complete before submission. Attach as supplementary material to demonstrate comprehensive evaluation.

**For Reviewers**: Verify completeness. Flag missing items as grounds for revision.

**For Practitioners**: Assess deployment readiness beyond headline metrics. Use checklist to identify potential deployment blockers.

The full checklist is available in our repository and may be adapted for domain-specific contexts.

---

## 7. Conclusion

We conducted a cross-study analysis of 19 AI evaluation methods across three prospective research projects to investigate whether single-metric success masks multi-criteria deployment failures. While overall rank reversals were lower than hypothesized (10.5% vs. 20% threshold), we found strong evidence that critical deployment failures can hide behind favorable single metrics. Notably, both OVAR methods achieved 94% ROI reduction but failed authorization criteria—a replicated deployment blocker that would have been missed in single-metric evaluation.

Our findings demonstrate that multi-criteria evaluation is not optional but essential, particularly for domain-specific requirements like authorization, compliance, and temporal validity. Even when primary metrics align well with overall quality (as in RAER), systematic gaps can persist. We contribute a Minimum Responsible Benchmark Report Checklist to promote transparent multi-criteria reporting aligned with NIST AI 800-2 guidance.

The authorization failure pattern in OVAR provides concrete evidence that AI methods can "ace their main test but flunk the real-world exam," especially on security-critical requirements. This underscores the need for comprehensive deployment gates that evaluate safety, cost, authorization, completion, stability, and burden—not just headline performance metrics.

---

## References

[1] Raji, I. D., et al. (2020). Closing the AI accountability gap: Defining an end-to-end framework for internal algorithmic auditing. *Proceedings of the 2020 Conference on Fairness, Accountability, and Transparency*, 33-44.

[2] National Institute of Standards and Technology (NIST). (2023). *Artificial Intelligence Risk Management Framework (AI RMF 1.0)*. NIST AI 800-2.

[3] [RAER Project]. Risk-Adaptive Evidence Revalidation for Consequential Tool Actions: A Prospective Failure Analysis. *ThinkAI 2026* (submitted).

[4] [OVAR Project]. Enterprise AI Value Assurance: From Token Consumption to Auditable Outcomes. *ThinkAI 2026* (submitted).

[5] [VDCM Project]. Verified Delivery Capacity Research: Role-Constrained Evidence-Ready Software Delivery Forecasting. *ThinkAI 2026* (submitted).

[6] Gebru, T., et al. (2021). Datasheets for datasets. *Communications of the ACM*, 64(12), 86-92.

[7] Mitchell, M., et al. (2019). Model cards for model reporting. *Proceedings of the Conference on Fairness, Accountability, and Transparency*, 220-229.

[8] Bender, E. M., & Friedman, B. (2018). Data statements for natural language processing: Toward mitigating system bias and enabling better science. *Transactions of the Association for Computational Linguistics*, 6, 587-604.

[9] Dwork, C., et al. (2012). Fairness through awareness. *Proceedings of the 3rd Innovations in Theoretical Computer Science Conference*, 214-226.

[10] Selbst, A. D., et al. (2019). Fairness and abstraction in sociotechnical systems. *Proceedings of the Conference on Fairness, Accountability, and Transparency*, 59-68.

---

## Acknowledgments

[To be added in camera-ready version after acceptance]

---

## Author Declarations

[To be added in camera-ready version after acceptance]

---

**Word Count**: ~3,800 words (6 pages in Springer LNCS format)  
**Figures**: 3 (rank reversal heatmap, criteria failure patterns, workflow diagram)  
**Tables**: 2 (data sources, hypothesis outcomes)
