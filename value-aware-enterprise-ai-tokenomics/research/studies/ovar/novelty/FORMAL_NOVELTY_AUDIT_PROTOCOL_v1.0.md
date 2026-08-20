# Formal Novelty-Audit Protocol v1.0

**Protocol date:** 12 August 2026  
**Search cutoff:** 12 August 2026  
**Target:** 30–40 closest eligible sources  
**Decision:** `GO`, `NARROW`, or `PIVOT`

## 1. Purpose

Determine whether OVAR has a defensible research contribution beyond existing work on AI tokenomics, LLM cost optimization, AI ROI, FinOps allocation, observability, token-budgeted agents, marginal token allocation, resource transferability, and enterprise governance.

This audit reduces duplication risk; it cannot prove global uniqueness, patent freedom to operate, or absence of unpublished work.

## 2. Provisional claim under audit

The proposed contribution is a prospectively evaluated protocol that:

1. reconciles heterogeneous AI resource consumption into fully loaded cost;
2. binds consumption to a predefined workflow outcome;
3. requires independently reviewable outcome evidence and a counterfactual baseline;
4. records causal-attribution confidence and uncertainty;
5. estimates risk-adjusted marginal outcome value;
6. allocates internal budgets across a hierarchy with reserve/carry-forward, access, exploration, concentration, and anti-gaming constraints;
7. evaluates stop/revise/scale decisions against frozen baselines and gates.

Novelty is asserted, if at all, only for the validated combination and its empirical operationalization—not for any component in isolation.

## 3. Research questions for the audit

- **NA-RQ1:** Which proposed OVAR components already exist in scholarly frameworks, standards, practice guidance, patents, or software?
- **NA-RQ2:** Has prior work already linked request-level AI consumption to independently verified incremental business outcomes?
- **NA-RQ3:** Has prior work prospectively evaluated hierarchical, risk-adjusted marginal allocation with reserve and access constraints?
- **NA-RQ4:** What is the narrowest contribution that remains distinct and testable?
- **NA-RQ5:** Is that contribution large enough to justify an empirical conference paper?

## 4. Source classes

Include:

- peer-reviewed journal and conference papers;
- arXiv and other clearly identified preprints;
- dissertations and institutional working papers where directly relevant;
- official standards and framework publications;
- patents and published patent applications;
- official public repositories and technical documentation;
- high-quality practitioner guidance when it documents current operational capabilities.

Exclude:

- undated marketing summaries without inspectable methods or capabilities;
- secondary articles when a primary paper, standard, repository, or documentation page is available;
- cryptocurrency tokenomics unless it directly addresses transferable AI usage rights or allocation mechanisms;
- generic AI adoption or ROI commentary with no relevant construct;
- duplicate versions, retaining the latest authoritative version while recording version history;
- sources unavailable for sufficient inspection.

## 5. Search channels

- arXiv and cited/citing links;
- ACM Digital Library, IEEE Xplore, SpringerLink, AIS eLibrary, and SSRN;
- Google Scholar or Semantic Scholar for citation chaining;
- NIST, ISO/IEC public descriptions, FinOps Foundation, FOCUS, and OpenTelemetry;
- Google Patents, WIPO Patentscope, and USPTO search;
- GitHub repositories and official project documentation.

If a database is unavailable, record the limitation and do not infer absence.

## 6. Query families

Run combinations of:

1. `("LLM" OR "generative AI" OR "agentic AI") AND (token economics OR tokenomics) AND (value OR ROI)`
2. `("AI cost" OR "LLM cost") AND (business outcome OR productivity OR value attribution)`
3. `(token budget OR inference budget) AND (allocation OR routing OR optimization)`
4. `(enterprise AI OR AI portfolio) AND (ROI OR value realization OR stage gate)`
5. `(AI FinOps OR LLM FinOps) AND (allocation OR showback OR chargeback OR unit economics)`
6. `(AI usage OR LLM trace) AND (outcome evidence OR causal attribution OR counterfactual)`
7. `(token transferability OR token carry-over OR budget rollover) AND generative AI`
8. `(hierarchical budget allocation OR dynamic resource allocation) AND AI AND value`
9. `(LLM observability OR GenAI telemetry) AND (cost OR evaluation OR outcome)`
10. `(agent loop OR multi-agent) AND (token efficiency OR cost quality trade-off)`

Run title and exact-phrase searches for every included close work and backward/forward citation chaining for the ten closest sources.

## 7. Screening procedure

1. Record every query, channel, date, and result count where exposed.
2. Deduplicate by DOI, arXiv identifier, title, repository URL, or patent family.
3. Screen titles and abstracts/descriptions.
4. Retrieve the full text or authoritative documentation for likely close sources.
5. Exclude with a recorded reason.
6. Assess included sources using the comparison fields below.
7. Mark factual uncertainty explicitly; absence of a feature is `unclear` unless the inspected source supports `no`.

## 8. Comparison fields

- source and version;
- source/research level;
- telemetry;
- cost normalization;
- workflow attribution;
- outcome definition;
- independent outcome verification;
- counterfactual baseline;
- attribution confidence;
- fully loaded cost;
- ROI;
- risk adjustment;
- organizational hierarchy;
- dynamic allocation;
- reserve/carry-forward;
- access/fairness constraints;
- anti-gaming controls;
- evaluation method and evidence;
- open artifacts;
- direct overlap and remaining gap.

Use `yes`, `partial`, `no`, `unclear`, or a short bounded description. Do not convert unknowns to `no`.

## 9. Closeness assessment

Score each source from 0–2 on:

- outcome verification;
- incremental/counterfactual value;
- fully loaded AI cost;
- hierarchical allocation;
- marginal or dynamic allocation;
- risk/access/governance constraints;
- prospective empirical evaluation.

Total range: 0–14. The score prioritizes full-text review; it is not a novelty statistic.

## 10. Decision rule

- **GO:** no inspected source substantially implements and evaluates the same closed loop; at least one material, testable contribution remains after removing known components; and credible baselines and data can be constructed.
- **NARROW:** overlap is material, but a smaller testable contribution remains. Rewrite the title, problem, claims, questions, and experiment before method work.
- **PIVOT:** the combination is already substantially covered, cannot be empirically identified, or cannot be evaluated credibly within available constraints.

The memorandum must name the closest sources, prohibited claims, bounded surviving claim, evidence limitations, and immediate next research artifact.

## 11. Integrity and update rule

- Preserve the original audit and add versioned updates rather than silently rewriting decisions.
- One prespecified clarification round is permitted before the decision memorandum.
- New close work discovered later must be added and may force narrowing or pivoting.
- The manuscript literature search must be refreshed immediately before submission.

