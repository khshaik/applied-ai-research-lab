# Gate 1 Research Concept Brief

## Working research topic

**Beyond Story Points: A Human Attention and Delivery Readiness Framework for Estimating AI-Assisted Software Delivery**

Short name for the proposed framework: **HADR (Human Attention and Delivery Readiness)**.

Alternative title for later consideration:

**From Coding Effort to Verified Delivery: An Empirical Framework for Estimating Human Attention in AI-Assisted Agile Teams**

## Executive decision

The broad observation that AI-generated code creates human oversight, review, and cognitive-load costs is **not novel by itself**. Recent publications already discuss human oversight and overload, cognitively demanding AI-era code review, and the shift from implementation toward specification, architecture, and governance.

The defensible research contribution is narrower and more useful:

> Design and empirically validate an end-to-end estimation framework that models human attention demand, automation leverage, and delivery-readiness gates across requirements, solution design, AI interaction, implementation refinement, verification, security review, QA, and UAT—and test whether it predicts delivery outcomes better than teams' existing story-point practice.

This turns an industry concern into a falsifiable research contribution rather than another opinion that “story points are dead.”

## Important correction to the starting premise

Story points were not formally created to count code or coding time. They are normally described as a team's relative estimate of effort, complexity, uncertainty, and risk. In practice, however, many organizations operationalize them as developer-centric sprint capacity and velocity. The paper should critique that **implementation and loss of construct validity**, especially under AI-assisted delivery, rather than make the historically vulnerable claim that story points measure how difficult code is to type.

## Purpose

To provide Agile leaders, engineering managers, product managers, architects, security practitioners, QA leaders, and delivery teams with a research-backed way to:

1. estimate scarce human attention across the complete delivery lifecycle;
2. expose downstream verification and quality bottlenecks before sprint commitment;
3. distinguish fast code generation from production-ready delivery;
4. plan capacity by role and gate rather than by developer effort alone; and
5. preserve speed without hiding rework, technical debt, delivery instability, or cognitive overload.

## Problem statement

AI coding assistants can compress parts of implementation, but they do not uniformly compress requirements analysis, domain-context construction, architecture, integration reasoning, security validation, review, test design, UAT, accountability, or cross-functional coordination. A single relative score calibrated mainly through historical team experience may therefore become unstable when the proportion and maturity of AI assistance change. It also provides little visibility into which scarce human capability—product, architecture, review, security, QA, or acceptance—will constrain flow.

The research problem is the absence of a validated, practical estimation approach that represents this redistributed human work and links it to end-to-end delivery outcomes.

## Proposed research questions

**RQ1.** How does AI assistance redistribute human effort and perceived cognitive workload across the software delivery lifecycle?

**RQ2.** Which pre-delivery characteristics best predict human attention consumed in requirements, AI interaction, architecture, review, security, QA, and UAT?

**RQ3.** Does HADR predict end-to-end cycle time, sprint completion, review/rework effort, and quality outcomes more accurately than the participating teams' existing story-point estimates?

**RQ4.** How do automation maturity, change size, system coupling, risk criticality, and team experience moderate the relationship between AI use and human attention demand?

**RQ5.** Can explicit readiness gates reduce rework and escaped defects without eliminating the implementation-time benefit of AI assistance?

## Candidate hypotheses

- **H1:** HADR estimates explain more variance in end-to-end cycle time and human touch time than story points alone.
- **H2:** As AI-assisted generation intensity increases, implementation time falls as a proportion of total human touch time, while verification, QA, and coordination consume a larger proportion.
- **H3:** Change size, architectural coupling, security criticality, and weak automated-test coverage increase verification attention independently of code-generation time.
- **H4:** Higher readiness-gate conformance is associated with fewer refinement loops, UAT rejection cycles, and escaped defects for work items with comparable attention demand.
- **H5:** The benefit of AI assistance is moderated by context readiness and team/tool maturity; consequently, AI usage intensity alone is not a reliable predictor of delivery performance.

These hypotheses remain provisional until the literature review and available-data assessment are complete.

## HADR framework: proposed structure

HADR should not replace one opaque scalar with another. It should produce three linked views.

### 1. Human Attention Demand Profile

Each work item receives anchored ordinal ratings, initially 0–4, on six dimensions:

1. **Intent and requirements reasoning (I):** ambiguity, stakeholder alignment, acceptance-criteria discovery, and domain interpretation.
2. **Context and AI orchestration (C):** effort to assemble trustworthy context, constraints, examples, prompts, tool instructions, and iterative feedback.
3. **Architecture, integration, and risk reasoning (A):** system boundaries, coupling, data contracts, non-functional requirements, security, privacy, compliance, and operational risk.
4. **Verification and rework (V):** expected effort to comprehend generated changes, trace intent to implementation, review, debug, and conduct human–AI refinement loops.
5. **Quality and acceptance evidence (Q):** unit, integration, system, regression, performance, security, accessibility, manual QA, and UAT breadth.
6. **Coordination and context switching (X):** handoffs, dependencies, specialist availability, decision latency, and the number of distinct business/technical contexts involved.

Anchors must be behaviorally defined. Statistical weights, if a composite is eventually needed, must be learned from data; they must not be chosen for convenience or mapped prematurely to Fibonacci numbers.

### 2. Automation Leverage Profile

Record factors that can change how attention converts into elapsed time:

- AI assistance mode: completion, chat, agentic, or mixed;
- proportion of lifecycle stages materially assisted by AI;
- context/instruction maturity;
- automated-test and quality-gate maturity;
- developer/reviewer experience with the domain and tool;
- change batch size and AI-generated change proportion, where reliably measurable.

This is a moderator profile, not a productivity score.

### 3. Delivery Readiness Gates

Use evidence-based pass/conditional/fail gates:

1. **Intent Ready:** problem, scope, constraints, and acceptance evidence are defined.
2. **Architecture Ready:** boundaries, interfaces, risks, and non-functional constraints are resolved to the level appropriate for the change.
3. **Generation Ready:** approved context, repository guidance, examples, and prohibited actions are available to the AI workflow.
4. **Verification Ready:** the change is traceable to intent; automated evidence is present; the diff is reviewable and appropriately sized.
5. **Release Ready:** integration, regression, security, operational, and observability evidence meets policy.
6. **Acceptance Ready:** QA and business acceptance criteria have been demonstrated and residual risks are owned.

The gates should scale by risk; they must not become a heavyweight universal checklist.

## Legacy versus proposed measurement model

| Measurement concern | Typical story-point/velocity use | HADR proposal | Observed outcome used for validation |
|---|---|---|---|
| Unit of planning | One relative team score | Six-dimensional attention profile plus readiness state | Human touch time by role and lifecycle stage |
| Capacity assumption | Primarily delivery-team/developer capacity | Product, architecture, development, review, security, QA, operations, and UAT capacity | Queue time and utilization pressure by constrained role |
| AI effect | Absorbed implicitly by recalibration | Explicit automation/context maturity moderators | AI-assisted versus unassisted time distribution |
| Quality | Often implicit in Definition of Done | Explicit evidence and readiness gates | Rework loops, failed tests, UAT rejections, escaped defects, change-failure rate |
| Flow | Sprint velocity | Gate-to-gate flow and total cycle time | Lead time, review latency, blocked time, deployment frequency |
| Risk and coupling | Folded into one estimate | Separate architecture/integration/security dimension | Defect severity, rollback, incident, and review depth |
| Cognitive burden | Discussed during estimation but rarely retained | Anchored prospective score plus sampled workload survey | NASA-TLX or a validated short workload measure after sampled tasks |
| Forecast target | Points completed per sprint | Probability of completion and expected attention demand by role/gate | Sprint completion, cycle-time distribution, and outcome quality |

## Recommended empirical design

### Study type

A mixed-method, multi-team field study using design-science principles:

1. systematic mapping review;
2. practitioner interviews and a Delphi-style expert review to refine constructs and anchors;
3. shadow estimation, in which teams keep their normal story points while also recording HADR without using it for commitment;
4. prospective field validation; and
5. usability and decision-value evaluation with practitioners.

### Practical sample target

- 6–12 Agile teams from at least two organizational contexts;
- approximately 150–300 completed work items;
- 4–6 sprints of shadow measurement after a short calibration period;
- product, engineering, architecture/security, QA, and delivery roles represented;
- a range of low- and high-coupling work and different AI-assistance levels.

The final power analysis must be based on the chosen primary outcome and model structure. Sample sizes must not be justified only by convenience.

### Data to collect

- existing story-point estimate;
- HADR dimension ratings and gate states before commitment;
- AI tool/mode and lifecycle stages assisted;
- human active/touch time by phase and role, collected with a low-burden protocol;
- elapsed cycle time, queue/block time, review pickup time, and review duration;
- pull-request size and number of refinement/review iterations;
- unit/integration/system test evidence and CI failures;
- security findings where applicable;
- QA defects, UAT rejection cycles, escaped defects, rollback/change failure, and early-life support;
- sampled post-task cognitive workload rather than a burdensome survey on every item;
- team, domain, experience, risk, and automation-maturity controls.

No proprietary prompts, source code, personal data, or confidential manuscripts should be provided to public AI systems.

### Analysis plan

- establish content validity through expert review;
- assess inter-rater reliability of HADR anchors;
- examine construct structure and internal consistency where statistically appropriate;
- compare out-of-sample prediction of relevant outcomes using story points alone, HADR alone, and combined models;
- use hierarchical/mixed-effects models to account for work items nested within teams;
- report MAE and calibration for time/probability forecasts, not only R-squared;
- test moderator effects without implying causality from observational associations;
- pre-register the primary outcome, exclusions, and analysis before examining final results;
- publish a de-identified instrument, codebook, and analysis script when organizational policy permits.

## Novelty assessment as of 13 August 2026

### Closely adjacent work

1. Garousi explicitly identifies human oversight and cognitive overload as hidden costs of AI-assisted software engineering, but the paper is positioned as a discussion based on practitioner opinions rather than a validated end-to-end estimation instrument: [Human Oversight and Overload](https://arxiv.org/abs/2606.05770).
2. Kamalı et al. propose an AI-supported code-review workflow with human-controlled gates, but its scope is code review rather than estimation across requirements through UAT: [Rethinking Code Review in the Age of AI](https://arxiv.org/abs/2605.17548).
3. Gurgul et al. report that GenAI shifts value toward specification quality, architectural reasoning, and oversight, based on a literature review and survey of 65 developers; they do not validate a replacement planning model: [State of Generative AI in Software Development](https://arxiv.org/abs/2603.16975).
4. Story-point research is actively applying LLMs to predict the existing score rather than questioning its construct under AI-assisted delivery: [Story Point Estimation Using Large Language Models](https://arxiv.org/abs/2603.06276).
5. Prior empirical work directly measures cognitive load in code review and shows that its relationship with review performance is not simple or uniformly negative. This warns against treating “less cognitive load” as automatically better: [Do explicit review strategies improve code review performance?](https://link.springer.com/article/10.1007/s10664-022-10123-8).
6. Productivity experiments report heterogeneous and even contradictory results: a constrained Copilot experiment found 55.8% faster completion, whereas a later RCT with experienced maintainers working in mature repositories found AI increased completion time by 19%: [Peng et al.](https://arxiv.org/abs/2302.06590) and [Becker et al.](https://arxiv.org/abs/2507.09089).
7. DORA reports a distinction between individual/productivity benefits and delivery-system effects, including concern about larger changes, throughput, and stability: [Impact of Generative AI in Software Development](https://dora.dev/ai/gen-ai-report/report/).

### Preliminary conclusion

No exact duplicate was identified in the searches completed for this gate. However, the conceptual territory is crowded and changing rapidly. Novelty depends on all four of the following being present:

1. full lifecycle scope from requirements through UAT;
2. an operationalized, behaviorally anchored instrument rather than a slogan;
3. comparison against actual team story-point practice using prospective field data; and
4. simultaneous evaluation of flow, human attention, and quality/readiness outcomes.

A purely conceptual paper or another unvalidated weighted formula would carry a high duplication and acceptance risk.

## Conference fit and submission constraints

- The supplied poster identifies THINKAI 2026 as the 4th International Conference on Recent Trends in AI Enabled Technologies, includes Generative AI among its focus areas, and lists 25 August 2026 as the full-paper deadline.
- The currently indexed submission page still displays THINKAI 2025 information. It states a 12–15 page Springer one-column format and double-blind review, but these requirements should be treated as provisional until the organizers publish or confirm the 2026 author instructions: [THINKAI paper submission page](https://thinkai.klh.edu.in/paper-submission).
- The likely fit is Generative AI / AI-enabled software engineering / human–AI collaboration. The paper must make the AI contribution explicit rather than read as a general Agile-management opinion.
- Springer Computer Science proceedings provide Word and LaTeX templates and impose publication-ethics and accessibility requirements: [Springer proceedings guidelines](https://www.springer.com/fr/computer-science/lncs/conference-proceedings-guidelines).
- Because the review is expected to be double blind, author names, affiliations, acknowledgements that identify the organization, repository links that reveal identity, and self-citations must be anonymized in the review version.

## Responsible AI-use rules for this project

Springer Nature requires human accountability, factual and citation verification, and transparent declaration of substantive generative-AI use. AI tools cannot be authors. Pure copy editing does not normally require declaration. Generative-AI images are generally prohibited, with limited exceptions; data-based graphs, tables, and simple flowcharts are not treated the same as generated illustrations. See [Springer Nature's AI guidance](https://group.springernature.com/gp/group/ai/ai-guidance-for-our-researchers-and-communities) and [book publishing policies](https://www.springernature.com/in/policies/book-publishing-policies).

For this paper:

- all claims and references must be human-verified against the source;
- no citation may be invented or included solely from an AI summary;
- AI-generated prose must be substantively reviewed and rewritten/approved by the human authors;
- statistical analysis decisions and interpretations remain with the researchers;
- no confidential organizational data may be pasted into an external AI tool;
- figures should be generated from verified data or created as conventional diagrams, not as generative-AI artwork;
- the final version should include an accurate AI-use disclosure if AI assists beyond copy editing.

## Proposed paper contribution statement

> This study contributes (1) an empirically grounded model of human attention demand across the AI-assisted software delivery lifecycle; (2) a behaviorally anchored estimation instrument and risk-scaled readiness gates; (3) a field comparison with existing story-point practice; and (4) evidence on when AI-enabled implementation speed translates—or fails to translate—into reliable end-to-end delivery.

## Scope boundaries

Included:

- professional Agile software/product teams using Copilot-like completion, conversational, or agentic coding assistance;
- work from requirements clarification through production/release readiness and UAT;
- human attention, delivery flow, review, testing, risk, and quality outcomes.

Excluded from the initial paper:

- claiming that story points are universally invalid;
- measuring employee performance or ranking individuals;
- estimating customer/business value with the same instrument;
- fully autonomous development with no accountable human delivery team;
- no-code content generation unrelated to software delivery;
- physiological/eye-tracking measurement unless resources and ethics approval make it feasible.

## Risks and mitigations

| Risk | Consequence | Mitigation |
|---|---|---|
| Topic framed only as “story points are obsolete” | Low novelty and easy reviewer rebuttal | Frame construct-validity and predictive-validity questions; compare models empirically |
| A new arbitrary score replaces Fibonacci | Same opacity as the criticized method | Preserve the dimension profile; learn weights only if evidence supports aggregation |
| Self-reported AI productivity | Perception bias | Combine surveys with workflow, timing, review, test, and quality data |
| Heavy data collection | Participant attrition and behavior change | Automate metadata collection; sample workload surveys; use a short study protocol |
| Confidential enterprise data | Ethics and policy exposure | De-identify, minimize data, obtain consent/approval, and keep code/prompts out of public AI systems |
| Correlation presented as causation | Invalid conclusions | Use cautious language, controls, longitudinal design, and causal design only where feasible |
| Framework becomes bureaucracy | Low practitioner adoption | Risk-scale gates and measure estimation overhead/usability |
| Fast-moving literature duplicates the contribution | Novelty erosion before submission | Refresh searches immediately before title lock and again before submission |

## Gated work plan

1. **Gate 1 — Concept and novelty:** approve/revise this brief, research questions, scope, and master prompt.
2. **Gate 2 — Evidence protocol:** approve databases, search strings, inclusion/exclusion criteria, quality appraisal, and evidence matrix.
3. **Gate 3 — Framework specification:** approve HADR constructs, behavioral anchors, readiness gates, survey/interview instruments, and data dictionary.
4. **Gate 4 — Study feasibility and ethics:** confirm data access, organizations/teams, consent, anonymization, sample/power plan, and analysis protocol.
5. **Gate 5 — Literature synthesis and related work:** review the evidence map, duplicate-topic audit, and claimed research gap.
6. **Gate 6 — Data collection/analysis:** run the approved study; review descriptive results before inferential analysis; freeze results before narrative drafting.
7. **Gate 7 — Manuscript outline:** approve the argument, section budget, tables, and figures in Springer format.
8. **Gate 8 — Section drafting:** review Methods and Results first, then Introduction/Related Work/Discussion, and Abstract last.
9. **Gate 9 — Integrity review:** verify every citation, claim, table, calculation, limitation, anonymization decision, and AI-use declaration.
10. **Gate 10 — Submission package:** double-blind audit, Springer format/accessibility checks, plagiarism/originality review, final human author approval, and submission.

## Master research prompt for subsequent gates

```text
You are supporting a human-led, publication-quality software-engineering research project intended for THINKAI 2026 and likely Springer Computer Science proceedings. Work only on the research gate explicitly authorized by the human authors. Do not advance to later gates or draft unsupported manuscript sections.

PROJECT OBJECTIVE
Develop and empirically validate a Human Attention and Delivery Readiness (HADR) framework for estimating AI-assisted Agile software delivery. The framework must cover requirements/problem framing, context and prompt construction, solution architecture, integration and security reasoning, AI-assisted implementation and refinement, unit/integration/system testing, code review, manual and automated QA, release validation, and UAT. It must be compared with participating teams' existing story-point practice and evaluated against observable end-to-end flow, human-attention, and quality outcomes.

CORE RESEARCH POSITION
Do not claim that story points historically measured lines of code or typing time. Treat them as relative estimates commonly intended to include effort, complexity, uncertainty, and risk, while testing whether their developer-centric single-number operationalization loses predictive and decision validity when AI redistributes work across lifecycle stages and roles. Do not assume HADR is superior; formulate falsifiable research questions and allow null or contrary findings.

EXPECTED CONTRIBUTION
1. A lifecycle-wide model of human attention demand in AI-assisted software delivery.
2. A behaviorally anchored estimation instrument with separate dimensions rather than an arbitrary replacement scalar.
3. Risk-scaled delivery-readiness gates based on auditable evidence.
4. A prospective field comparison of story points, HADR, and combined models.
5. Practical guidance for organizations without turning the framework into individual performance measurement.

RESEARCH QUESTIONS
Use or critically refine these only with human approval:
- How does AI redistribute human effort and perceived workload across the delivery lifecycle?
- Which pre-delivery characteristics predict human attention by role and stage?
- Does HADR improve out-of-sample prediction of cycle time, sprint completion, review/rework, and quality outcomes compared with story points?
- Which factors moderate AI's effect, including context readiness, change size, system coupling, risk, automation maturity, and experience?
- Do readiness gates reduce rework and escaped defects while retaining AI's implementation benefit?

HADR CANDIDATE CONSTRUCTS
Maintain separate 0–4 behaviorally anchored dimensions until evidence justifies aggregation:
I — Intent and requirements reasoning
C — Context and AI orchestration
A — Architecture, integration, security, and operational risk
V — Verification, comprehension, review, and rework
Q — Quality and acceptance evidence
X — Coordination, dependencies, and context switching
Also retain an Automation Leverage Profile and six risk-scaled readiness gates: Intent Ready, Architecture Ready, Generation Ready, Verification Ready, Release Ready, and Acceptance Ready.

EVIDENCE AND NOVELTY RULES
- Search current primary scholarly sources in software engineering, human–computer interaction, human factors, Agile estimation, developer productivity, code review, testing, and AI-assisted development.
- Search at minimum arXiv, ACM Digital Library, IEEE Xplore, SpringerLink, Scopus/Web of Science if accessible, Google Scholar for discovery, and backward/forward citations.
- Record full search strings, dates, databases, screening decisions, and duplicate removal.
- Give priority to peer-reviewed papers, registered reports, systematic reviews, standards, and official research reports. Label preprints and practitioner evidence clearly.
- Treat the topic as fast-moving; refresh the search before title lock and submission.
- Never fabricate a citation, DOI, quotation, statistic, participant count, result, or bibliographic field.
- Open and verify every cited source. If a source cannot be verified, mark it unresolved and exclude it from evidentiary claims.
- Distinguish source findings, author interpretation, and our inference.

METHOD REQUIREMENTS
- Prefer a mixed-method, multi-team prospective field study with shadow estimation.
- Preserve teams' normal story points during observation; do not disrupt sprint commitment until validation supports change.
- Define one primary outcome and conduct an appropriate power analysis.
- Use hierarchical models for work items nested in teams where appropriate.
- Compare out-of-sample predictive performance and calibration, not only in-sample association.
- Assess content validity, inter-rater reliability, construct validity, usability, and estimation overhead.
- Combine self-report with workflow metadata, human touch time, review/rework, test, UAT, and quality outcomes.
- Pre-register hypotheses, exclusions, primary outcome, and analysis before final-data inspection.
- Do not infer causation from observational data.
- Document threats to construct, internal, external, and conclusion validity.

ETHICS, PRIVACY, AND PUBLICATION RULES
- Keep humans accountable for all research decisions, interpretations, and final prose.
- Never place confidential code, prompts, tickets, personal data, manuscripts under review, or organization-identifying material into public AI systems.
- Obtain the required institutional/organizational ethics, consent, and data approvals before participant research.
- Do not use the framework to rank individuals or automate employment decisions.
- Follow the current THINKAI author instructions and Springer proceedings template; verify rather than assume the 2025 requirements apply to 2026.
- Prepare a double-blind review version with identities and identifying acknowledgements removed.
- Follow Springer Nature AI policy: AI is not an author; substantive AI use is transparently declared; authors verify accuracy, originality, and citations; generative-AI artwork is avoided; conventional diagrams and data-based plots remain traceable and accessible.

WRITING STANDARD
Use precise academic English. Avoid hype, false dichotomies, universal claims, marketing language, and claims that AI makes coding “free.” Define all constructs operationally. Report negative and null findings. Keep organizational recommendations proportional to evidence. Use tables and simple data/flow diagrams only when they improve comprehension. Draft the abstract last.

HUMAN-IN-THE-LOOP GATE PROTOCOL
For the authorized gate:
1. State the decision to be made.
2. Present evidence, assumptions, uncertainties, and alternatives.
3. Identify conflicts or duplication with prior work.
4. Produce the requested artifact and a concise change log.
5. Run an integrity check for unsupported claims and unverified citations.
6. Stop and request explicit human approval before moving to the next gate.

CURRENT AUTHORIZED GATE
[INSERT GATE NUMBER, PURPOSE, INPUTS, AND REQUIRED OUTPUT]

AUTHOR-PROVIDED DATA/CONSTRAINTS
[INSERT ONLY APPROVED, NON-CONFIDENTIAL INFORMATION]
```

## Gate 1 approval decisions

Before Gate 2 begins, the human authors should approve or revise:

1. the working title and HADR name;
2. the corrected problem framing (insufficiency/construct shift, not “story points only measured coding”);
3. the full-lifecycle scope and exclusions;
4. the five research questions and candidate hypotheses;
5. the three-part HADR structure;
6. the commitment to prospective empirical validation rather than a purely conceptual paper; and
7. the master prompt and gated workflow.

