<h1 align="center">Enterprise AI Value Assurance: From Token Consumption to Auditable Outcomes</h1>

<p align="center"><strong>An end-to-end research framework for linking AI resource use to verified outcomes, defensible ROI claims, and accountable stop–revise–continue–scale decisions</strong></p>

<p align="center">AI economics · Outcome evidence · Fully loaded cost · Prospective governance</p>

<p align="center">
  <img alt="Node.js 20+" src="https://img.shields.io/badge/Node.js-20%2B-339933?logo=nodedotjs&logoColor=white">
  <img alt="JavaScript" src="https://img.shields.io/badge/JavaScript-ES%20Modules-F7DF1E?logo=javascript&logoColor=111111">
  <img alt="Python 3.11+" src="https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white">
  <img alt="JSON" src="https://img.shields.io/badge/Data-JSON-292929?logo=json&logoColor=white">
  <img alt="CSV" src="https://img.shields.io/badge/Data-CSV-217346">
  <img alt="Microsoft Excel" src="https://img.shields.io/badge/Review-Excel-217346?logo=microsoftexcel&logoColor=white">
  <img alt="SHA-256" src="https://img.shields.io/badge/Integrity-SHA--256-E67E22">
  <img alt="GitHub Actions" src="https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?logo=githubactions&logoColor=white">
  <img alt="Microsoft Word" src="https://img.shields.io/badge/Manuscript-Word-2B579A?logo=microsoftword&logoColor=white">
  <img alt="PDF" src="https://img.shields.io/badge/Publication-PDF-B30B00?logo=adobeacrobatreader&logoColor=white">
</p>

<p align="center">
  <a href="#the-problem-in-one-minute"><strong>Problem</strong></a> ·
  <a href="#method-overview"><strong>Method</strong></a> ·
  <a href="#benchmark-design"><strong>Benchmark</strong></a> ·
  <a href="#main-design-stage-results"><strong>Results</strong></a> ·
  <a href="#end-to-end-outcome-verification-workflow"><strong>Workflow</strong></a> ·
  <a href="#papers-and-submission-files"><strong>Papers &amp; Artifacts</strong></a> ·
  <a href="#public-technical-communication"><strong>Communication</strong></a> ·
  <a href="#reproducibility-expectations"><strong>Reproducibility</strong></a> ·
  <a href="#references"><strong>References</strong></a>
</p>

Research on whether enterprise AI investment decisions can be grounded in verified incremental outcomes rather than token volume, provider spend, technical quality, or self-reported value alone.

This repository is a research monorepo: each study has an isolated protocol, constructed benchmark, implementation, results, integrity record, and paper directory. The first study is **Outcome-Verified AI Resource Allocation (OVAR)**.

> **Double-blind review notice:** keep this repository **private** while an identified manuscript is under double-blind review. The `papers/thinkai-2026/` directory, Git history, citation metadata, and repository license identify the author. Do not publish the repository or create a public Zenodo deposit until the venue permits deanonymization.

## Author

Shaik Khaja Nayab Rasool.

---

## Research project dossier

### Project identity

**From AI Usage to Auditable Outcomes: Outcome-Verified AI Resource Allocation**<br>
*A prospective negative calibration of an outcome-evidence ledger for enterprise AI investment decisions.*

| Item | Description |
|---|---|
| Research area | AI economics, FinOps for AI, LLMOps, enterprise governance, causal measurement, and operations research |
| Study type | Methods research with constructed cases, blinded synthetic construct review, and a prospectively frozen calibration gate |
| Primary method | Outcome-Verified AI Resource Allocation (OVAR v1.0) |
| Unit of analysis | One AI-enabled workflow investment episode with consumption, cost, outcome, baseline, evidence, attribution, risk, and authorization records |
| Evaluation scope | 48 calibration cases across six domains; no held-out benchmark was created or accessed |
| Current conclusion | Outcome evidence reduced proxy-accounting errors, but OVAR v1.0 failed four of nine registered criteria |
| Publication framing | Transparent methods and prospective negative-calibration paper |

### Dossier coverage at a glance

| Research-project requirement | Where it is documented |
|---|---|
| Direct artifact links | [Papers and submission files](#papers-and-submission-files), [Tables, figures, and result artifacts](#tables-figures-and-result-artifacts), and [Reproducibility map](#reproducibility-map) |
| Explicit hypothesis and outcome | [Hypothesis and decision rule](#hypothesis-and-decision-rule) and [Main design-stage results](#main-design-stage-results) |
| Benchmark coverage | [Benchmark design](#benchmark-design) and the [48 reviewer-visible calibration cases](studies/ovar/calibration/candidate_v1.1/construct_review_cases.json) |
| Analytical methods | [Method overview](#method-overview) and [Analysis performed](#analysis-performed) |
| Technology boundaries | [Key technologies and libraries](#key-technologies-and-libraries) and [Technology boundaries](#technology-boundaries) |
| End-to-end operating model | [End-to-end outcome-verification workflow](#end-to-end-outcome-verification-workflow) and the [communication dossier](communications/linkedin/outcome-verified-allocation/README.md) |
| Reproducibility expectations | [Quick verification](#quick-verification), [Reproducibility map](#reproducibility-map), and [Reproducibility expectations](#reproducibility-expectations) |
| Research and source provenance | [References](#references), [novelty source register](studies/ovar/novelty/source_register.csv), and [claim-to-evidence ledger](studies/ovar/publication/CLAIM_TO_EVIDENCE_LEDGER_v1.0.csv) |

### Problem statement

Organizations can measure tokens, calls, latency, and provider charges, but those consumption records do not establish that an AI-assisted workflow caused a correct, accepted, incremental, or economically valuable outcome. The problem is amplified in agentic workflows, where retrieval, planning, model calls, tool calls, retries, evaluation, human review, integration, governance, and rework may all contribute to one business outcome.

The research problem is therefore:

> How can an organization prospectively convert an attributed AI-workflow trace into an independently reviewable incremental-value claim and use that claim for stop, revise, continue, scale, and resource-allocation decisions without treating token volume as productivity or overstating causal ROI?

OVAR addresses the evidence and decision-accounting layer. It is not a comparison of model vendors, observability platforms, agent frameworks, or commercial FinOps tools.

### Research questions

1. Can a predefined outcome contract and independently reviewable evidence reduce false-positive ROI classifications relative to usage-only and self-reported-value rules?
2. Does fully loaded cost—including review, integration, governance, and rework—change investment decisions compared with provider charges alone?
3. Can explicit counterfactual baselines and attribution confidence prevent technical quality or adoption from being mistaken for incremental value?
4. Can an authorization-sensitive policy protect invalid or out-of-scope projects without unnecessarily stopping valid in-scope work?
5. Can a prospectively frozen gate reveal when a more elaborate governance policy is dominated by a simpler evidence-based comparator?

## The problem in one minute

Enterprise AI programs often move from observable consumption to an assumed value claim without a reproducible causal bridge.

```text
AI resources consumed        Workflow output observed       Investment decision
tokens, calls, tools,  --->  draft, forecast, answer,  --->  stop / revise /
retrieval, review, rework     recommendation or action        continue / scale
          |                              |                            |
   directly measurable            may be technically good      requires incremental
                                                              value and current authority
```

The missing link is an **outcome-evidence ledger**. It must show what outcome was defined before measurement, what baseline represents the no-AI alternative, which evidence can be independently reproduced, what the fully loaded cost was, how much observed benefit is attributable to AI assistance, whether authority is current and in scope, and what decision rule produced the final receipt.

Without that link, several misleading substitutions become easy:

1. More tokens are treated as more work or innovation.
2. Lower model cost is treated as positive ROI.
3. High technical quality is treated as business value.
4. Self-reported time saved is treated as causal benefit.
5. A successful proof of concept is scaled without a credible baseline or complete cost boundary.
6. Unused internal AI budget is spent to avoid losing it, irrespective of verified marginal value.

OVAR studies whether a stricter evidence contract improves those decisions—and whether the added governance burden is itself justified.

## Why ordinary controls do not completely resolve it

Existing capabilities remain useful, but each addresses only part of the decision problem:

| Existing control | What it helps with | Remaining gap studied here |
|---|---|---|
| Token and cost dashboards | Attribute calls, tokens, latency, and provider charges | Consumption is not proof of incremental business value |
| LLM observability | Trace prompts, responses, tools, errors, and quality signals | Traceability alone does not establish a counterfactual or causal contribution |
| Model evaluation | Measure accuracy, groundedness, safety, or task quality | Technical quality may not yield adoption, time savings, revenue, or avoided loss |
| FinOps budgets and alerts | Limit or allocate expenditure | Historical spend and budget compliance are not marginal-value estimates |
| Self-reported benefits | Capture practitioner experience quickly | Estimates may be optimistic, inconsistent, non-incremental, or unauditable |
| ROI templates | Organize benefits and costs | They may be completed retrospectively without registered outcomes or evidence |
| A/B tests and causal designs | Estimate incremental effects when feasible | They do not by themselves define full cost, authority, portfolio allocation, or evidence receipts |
| Human investment committees | Add judgment and accountability | Committees still need consistent, reproducible evidence and comparable decision records |

The open problem is not the absence of telemetry, evaluation, budgeting, or causal methods individually. It is the lack of a prospectively tested control that links them into one auditable decision record while penalizing false ROI, unsafe scaling, false stopping, and measurement burden. OVAR v1.0 is an experimental formulation of that combined problem; the present result shows that its authorization mechanism is not adequate.

## Cross-industry examples

The following examples explain the decision problem. They are illustrative, not real incidents or additional experimental results.

### Healthcare and medical administration

A hospital pilots an AI scheduling assistant. Token use, response time, and appointment recommendations are easy to count, but the relevant outcome may be reduced avoidable no-shows without increasing staff rework or inequitable access.

- **Misleading proxy:** many recommendations and high user activity.
- **Evidence required:** a predefined no-show outcome, comparable baseline, acceptance criteria, staff-review cost, intervention maturity, and current approval for the studied use.
- **Decision risk:** scaling a popular tool that did not cause the claimed operational benefit—or stopping a valuable pilot because benefits mature slowly.

### Banking, payments, and finance

A lender uses AI to prioritize case review. A technically accurate model may coincide with policy changes, staffing shifts, or a macroeconomic recovery.

- **Misleading proxy:** faster cases or positive self-reported time savings.
- **Evidence required:** matched or time-series baseline, realized recovery outcomes, full review and compliance cost, confounder record, and current authorization scope.
- **Decision risk:** attributing shared or delayed value entirely to AI and scaling beyond the approved decision context.

### E-commerce and digital marketplaces

A retailer deploys an AI merchandising or customer-support workflow. High call volume can reflect adoption, retries, poor routing, or unresolved customer problems.

- **Misleading proxy:** tokens per active user, automated-resolution count, or generated revenue without substitution controls.
- **Evidence required:** margin-aware outcome, holdout or matched comparison, return and rework cost, campaign confounders, and mature observation window.
- **Decision risk:** rewarding high-consumption teams even when a simpler workflow produced equal or better value.

### Transportation and logistics

A logistics operator pilots AI for dispatch, forecasting, or maintenance. Weather, labor availability, terminal hours, vessel schedules, and fleet campaigns can move outcomes independently of the system.

- **Misleading proxy:** lower forecast error or fewer planner minutes in an uncontrolled period.
- **Evidence required:** operational outcome contract, comparable routes or assets, implementation and incident costs, concurrent-event register, and decision checkpoint.
- **Decision risk:** scaling after a favorable but confounded period or excluding a low-adoption workflow with high avoided-loss value.

### Cybersecurity and access operations

A security team uses AI to triage alerts or draft investigation steps. A reduction in analyst handling time is not valuable if escalation quality deteriorates or authority expires.

- **Misleading proxy:** automated alert count, latency reduction, or reviewer acceptance alone.
- **Evidence required:** security outcome, incident severity, corrected drafts, human-review burden, harm model, and structured authorization dates and scope.
- **Decision risk:** continuing an unauthorized deployment or stopping an in-scope workflow because text mentions a different excluded environment.

### Privacy and data governance

A governance team uses AI to classify records or prepare data-subject responses. Productivity estimates may exclude legal review, exception handling, remediation, and audit costs.

- **Misleading proxy:** documents processed or initial turnaround time.
- **Evidence required:** correctness and timeliness contract, independent audit sample, exception and rework cost, jurisdiction, purpose, and current approval.
- **Decision risk:** claiming savings while shifting work to downstream reviewers or operating outside the approved data scope.

### Human resources and workforce systems

A workforce team pilots AI for candidate communication or policy assistance. Adoption and quality can be high while fairness, escalation, or downstream correction costs remain unknown.

- **Misleading proxy:** messages generated, recruiter time reported, or satisfaction without a comparator.
- **Evidence required:** registered service outcome, subgroup review, baseline workflow, human correction time, authority boundary, and delayed hiring outcome.
- **Decision risk:** scaling a superficially productive workflow whose value or authorization cannot be independently defended.

## The desired safety behavior

OVAR separates five decisions that are often collapsed into “approve” or “reject”:

| Decision | Meaning |
|---|---|
| `STOP` | Evidence supports negative value, unacceptable harm, or materially absent/expired/out-of-scope authorization |
| `REVISE` | The value interval crosses the decision boundary or the design needs a specified correction before reassessment |
| `CONTINUE_PILOT` | Evidence supports continued limited use, but not organization-wide scaling |
| `SCALE` | Evidence supports positive value and a sufficient benefit-to-cost margin within current authority |
| `INDETERMINATE` | The outcome contract, baseline, evidence, maturity, or attribution record is insufficient for a defensible classification |

The objective is not minimum token usage or maximum deployment. It is a reproducible allocation decision based on verified outcomes and fully loaded cost, subject to evidence sufficiency, risk, authorization, and measurement burden.

## Current study

OVAR v1.0 compares five frozen accounting policies on 48 deliberately constructed cases:

- six domains with eight prespecified construction strata per domain;
- reviewer-visible case facts separated from reference decisions during construct review;
- two blinded synthetic reviewers used only as rubric, clarity, and leakage stress tests;
- 25 pre-execution tests passed before the one-time calibration run;
- OVAR passed five of nine mandatory criteria;
- outcome-flat dominated OVAR across all registered measurement-burden weights;
- no held-out benchmark was created or accessed.

The supported conclusion is methodological and negative: outcome evidence substantially reduced proxy-accounting errors, but unstructured lexical rules did not resolve authorization time and scope reliably.

See [`studies/ovar/README.md`](studies/ovar/README.md) for the scientific scope and reproducibility boundary.

## Repository layout

```text
.
├── studies/
│   └── ovar/                 # Protocols, cases, reviewers, policies, results, integrity records
├── papers/
│   ├── thinkai-2026/         # Identified manuscript and declarations
│   └── _template/            # Starting structure for later papers
├── communications/           # LinkedIn articles, posts, diagrams, and figure provenance
├── docs/                     # Governance and repository conventions
├── scripts/                  # Repository-level verification
├── .github/workflows/        # Continuous integration
├── CITATION.cff
├── LICENSE
└── pyproject.toml
```

## Quick verification

Node.js 20 or later is recommended for the deterministic policy tests. Python 3.11 or later is used for repository verification and manuscript generation.

```bash
node --test studies/ovar/calibration/tests/calibration_policies_v1.0.test.mjs
node --test studies/ovar/calibration/tests/reference_labels_v1.0.test.mjs
node --test studies/ovar/pilot/tests/pilot_v1.0.test.mjs
python3 scripts/verify_repository.py
```

Or run:

```bash
make verify
```

## Reuse and citation

Code is licensed under the MIT License. Repository-owned data and documentation are available under CC BY 4.0 as stated in [`LICENSE-DATA-DOCS.md`](LICENSE-DATA-DOCS.md). Citation metadata are provided in [`CITATION.cff`](CITATION.cff). Referenced publications remain subject to their respective rights.

### Hypothesis and decision rule

The binding OVAR v1.0 calibration hypothesis was composite: OVAR had to improve false ROI and scale decisions while satisfying **every** prespecified safety, completion, burden, domain, and non-dominance criterion.

The registered gate required:

- all pre-execution tests and artifact hashes to pass;
- zero authorization-related harmful actions by OVAR;
- a lower false-positive ROI rate than usage-only and self-reported-value policies;
- a false-scale rate no worse than outcome-flat;
- a false-stop rate within ten percentage points of the best comparator;
- an indeterminate rate no greater than 30%;
- no comparator with both lower weighted loss and lower measurement burden;
- no domain with more than one serious OVAR false-scale or false-stop error;
- no comparator dominating OVAR throughout the registered burden-weight sensitivity range.

**Decision:** the composite hypothesis was **not supported**. OVAR passed five of nine criteria. It missed two expired authorizations, falsely stopped two safe in-scope cases, and was dominated by outcome-flat on loss and burden. The held-out stage was therefore not authorized.

### Method overview

OVAR links five record classes:

```text
consumption record
      + work ownership record
      + prospective outcome contract and evidence record
      + fully loaded value/cost/attribution record
      + allocation decision and immutable receipt
      = auditable investment decision
```

The reference policy uses:

- an outcome contract and acceptance criteria defined before decision time;
- an explicit baseline design and implementation record;
- independently locatable evidence and a reproduction note;
- provider, infrastructure, tooling, human-review, integration, governance, rework, and evidence-review costs;
- attributed value discounted by confidence and expected harm;
- evidence-sufficiency and authorization safeguards;
- deterministic policy field whitelists, canonical input hashes, and decision-receipt hashes;
- `STOP`, `REVISE`, `CONTINUE_PILOT`, `SCALE`, and `INDETERMINATE` actions.

The formal constructs are documented in the [objective and estimands](studies/ovar/method/FORMAL_OBJECTIVE_AND_ESTIMANDS_v0.1.md), [causal model](studies/ovar/method/CAUSAL_MODEL_v0.1.md), and [construct dictionary](studies/ovar/method/CONSTRUCT_DICTIONARY_v0.1.csv). The frozen policy implementation is [calibration_policies_v1.0.mjs](studies/ovar/calibration/implementation/calibration_policies_v1.0.mjs).

### Benchmark design

The study contains a 24-case engineering pilot and a separate 48-case prospective calibration set.

| Dimension | Coverage |
|---|---|
| Domains | Healthcare, financial services, e-commerce, transportation and logistics, cybersecurity, customer operations |
| Calibration cases | 48 constructed cases; eight per domain |
| Construction strata | High-value/moderate-usage, high-usage/low-value, hidden full cost, weak counterfactual, delayed/shared attribution, authorization/compliance, low-adoption/high-value, and revise/indeterminate boundary |
| Policies | Usage only, self-reported value, cost and quality, outcome flat, OVAR ledger |
| Reference actions | Stop, revise, continue pilot, scale, indeterminate |
| Construct review | Two isolated synthetic reviewers; one clarity-only packaging revision; synthetic agreement explicitly not human validation |
| Leakage controls | Reviewer-visible/reference separation, forbidden-key rejection, field whitelists, no case-ID branching, hash locks |
| Confirmatory status | Calibration/design evidence only; no held-out benchmark was created or opened |

Start with the [reviewer-visible calibration cases](studies/ovar/calibration/candidate_v1.1/construct_review_cases.json), [construct schema](studies/ovar/calibration/schema/construct_review_case_schema_v1.0.json), [prospective analysis plan](studies/ovar/calibration/PROSPECTIVE_ANALYSIS_PLAN_v1.0.md), and [pre-execution lock](studies/ovar/calibration/CALIBRATION_PRE_EXECUTION_LOCK_v1.2.json).

### Analysis performed

The completed analysis includes:

- a 39-source novelty and overlap audit with explicit narrowing of the contribution;
- a 24-case engineering dry run and deterministic policy-receipt validation;
- blinded synthetic construct scoring for outcome clarity, baseline credibility, evidence auditability, cost completeness, attribution defensibility, and decision realism;
- identification and one-time removal of visible stratum/order shortcuts without changing substantive cases;
- 25 pre-execution tests covering leakage, ranges, cost reconciliation, canonical hashing, authorization behavior, and identifier independence;
- one prospective execution of five frozen policies on 48 cases;
- false-positive ROI, false-scale, false-stop, authorization-violation, exact-action, indeterminate, burden, and weighted-loss measurements;
- measurement-burden sensitivity at weights 0.25, 0.50, 0.75, and 1.00;
- domain-level serious-error checks and case-level failure tracing;
- immutable pre-execution and closure manifests preserving the negative result.

### Main design-stage results

| Measure | OVAR v1.0 | Outcome-flat | Usage only | Interpretation |
|---|---:|---:|---:|---|
| False-positive ROI | 2/35 (5.7%) | 2/35 (5.7%) | 35/35 (100.0%) | Outcome evidence sharply outperformed consumption-only classification |
| False scale | 0/35 (0.0%) | 2/35 (5.7%) | 15/35 (42.9%) | OVAR was conservative on scale decisions |
| False stop | 2/13 (15.4%) | 0/13 (0.0%) | 0/13 (0.0%) | OVAR over-blocked two safe in-scope cases |
| Authorization violations | 2/48 (4.2%) | 2/48 (4.2%) | 5/48 (10.4%) | Lexical rules missed two expired approvals |
| Exact action | 25/48 (52.1%) | 32/48 (66.7%) | 2/48 (4.2%) | Outcome-flat matched more reference actions |
| Indeterminate | 12/48 (25.0%) | 12/48 (25.0%) | 0/48 (0.0%) | Both evidence-led policies stayed within the 30% gate |
| Measurement burden | 0.800 | 0.650 | 0.050 | OVAR required the most measurement effort |
| Weighted loss | 1.155 | 1.001 | 4.573 | Outcome-flat dominated OVAR at the registered central weight |
| Prospective criteria passed | 5/9 | Not applicable | Not applicable | Overall decision: stop v1.0; do not proceed to held out |

The authoritative machine-readable result is [calibration_gate.json](studies/ovar/calibration/results/calibration_v1.0/calibration_gate.json). Case-level outputs are in [policy_decisions.json](studies/ovar/calibration/results/calibration_v1.0/policy_decisions.json), and the interpretation is frozen in the [calibration decision memorandum](studies/ovar/calibration/results/calibration_v1.0/CALIBRATION_DECISION_MEMORANDUM_v1.0.md).

### Research history and work completed

1. **Problem formulation:** separated enterprise AI consumption telemetry from independently verified incremental value.
2. **Novelty audit:** screened 39 sources and narrowed the claim away from generic token optimization, FinOps, observability, routing, and ROI frameworks.
3. **Formalization:** defined the ledger, causal model, constructs, estimands, full-cost boundary, evidence confidence, and decision actions.
4. **Engineering pilot:** implemented five deterministic policies on 24 cases and validated receipts, whitelists, arithmetic, and leakage controls.
5. **Construct review:** used two isolated synthetic reviewers as a rubric stress test; their outputs are not represented as human validation.
6. **Clarity revision:** removed visible stratum names and repeating identifier order after a blocking shortcut was found; substantive case facts remained unchanged.
7. **Prospective calibration:** locked 48 cases, policies, reference labels, tests, thresholds, and hashes before one execution.
8. **Negative gate:** retained all four failed criteria, the dominating comparator, and the four binding authorization/scope cases.
9. **Publication preparation:** produced a 14-page ThinkAI manuscript in editable Word and PDF with eight tables, five equations, three figures, declarations, and a claim ledger.

### Key technologies and libraries

| Technology | Use in this project |
|---|---|
| Node.js 20+ | Deterministic policy execution, native test runner, schema processing, and cryptographic receipts |
| JavaScript ES modules | Policy implementation, case preparation, review consolidation, locking, and one-time calibration |
| Node.js standard library | `assert`, `crypto`, `fs`, `path`, `test`, `url`; no runtime package dependency |
| Python 3.11+ | Reproducible Word manuscript and PNG figure generation plus repository verification |
| `python-docx`, Matplotlib, Pillow | Manuscript construction and publication figures; analytical policy execution does not depend on them |
| JSON and CSV | Versionable cases, schemas, scores, decisions, manifests, claims, constructs, and novelty records |
| Microsoft Excel | Editable reviewer workbook with documented sheet and formula layout |
| SHA-256 | Pre-execution locks, review locks, decision receipts, and closure manifests |
| Git and GitHub Actions | Version control and automated boundary/test checks |
| Microsoft Word and PDF | Editable manuscript source and visually reviewed 14-page submission rendering |

The core calibration runtime deliberately uses Node.js built-ins only. It does not call an LLM, model provider, observability product, cloud billing API, or agent framework.

### Technology boundaries

The repository separates the **research construct**, **reference evaluator**, and **possible enterprise implementation**:

- OVAR is an outcome-evidence ledger and decision policy, not a token meter, model router, FinOps platform, observability SDK, accounting standard, or vendor-credit mechanism.
- Tokens are not treated as interchangeable across models, providers, modalities, cached/reasoning classes, or tokenizers.
- The evaluator consumes constructed records; it does not ingest live billing, ERP, CRM, HR, clinical, security, or workflow telemetry.
- “Carry-forward” refers to an internal allocation rule unless a vendor contract explicitly supports transferable or expiring credits; it is not evaluated in v1.0.
- Synthetic reviewers supported clarity and leakage stress testing only. They are not organizational stakeholders, independent human experts, or runtime agents.
- The frozen lexical authorization parser is a documented failure mechanism, not a deployable compliance control.
- A production implementation would need signed outcome contracts, trace-to-work identifiers, structured authorization, causal design support, accounting reconciliation, access control, privacy protection, monitoring, audit logging, and independent validation.
- No result establishes field ROI, portfolio optimization, legal compliance, fairness, security, production readiness, or generalization.

### Papers and submission files

| Artifact | Format | Purpose |
|---|---|---|
| [Camera-ready manuscript](papers/thinkai-2026/manuscript/OVAR_ThinkAI2026_CAMERA_READY_v1.0.docx) | Word (`.docx`) | Editable identified manuscript |
| [Camera-ready manuscript](papers/thinkai-2026/manuscript/OVAR_ThinkAI2026_CAMERA_READY_v1.0.pdf) | PDF | 14-page Microsoft Word export used for visual verification |
| [Author and declarations](papers/thinkai-2026/declarations/author_and_declarations.md) | Markdown | Authorship, interests, funding, ethics, CRediT, AI-use, and availability declarations |
| [ThinkAI submission notes](papers/thinkai-2026/README.md) | Markdown | Venue status, formatting, confidentiality, and pending actions |

The manuscript title is *From AI Usage to Auditable Outcomes: A Prospective Negative Calibration of Outcome-Verified AI Resource Allocation*. Tables 1–8, Equations 1–5, Figures 1–3, references, and page breaks were visually checked in the Word-exported PDF. The institution-approved similarity check remains pending; no similarity percentage is stated or inferred.

### Public technical communication

The communication package translates the study into an engineering narrative while preserving the negative-result boundary.

| Artifact | Purpose |
|---|---|
| [Consolidated technical article](communications/linkedin/outcome-verified-allocation/LINKEDIN_CONSOLIDATED_ARTICLE.md) | Full problem statement, architecture, equations, observed gate result, failure mechanism, precautions, enterprise adoption path, and research agenda |
| [LinkedIn article draft](communications/linkedin/outcome-verified-allocation/drafts/LINKEDIN_ARTICLE.md) | Compact editorial version for publication channels with tighter length constraints |
| [LinkedIn post](communications/linkedin/outcome-verified-allocation/drafts/LINKEDIN_POST.md) | Standalone professional post with technical result, practitioner sequence, and claim boundary |
| [Visual and provenance package](communications/linkedin/outcome-verified-allocation/README.md) | Six publication-ready figures, source classification, rebuild instructions, and interpretation boundary |
| [Deterministic figure renderer](communications/linkedin/outcome-verified-allocation/scripts/build_visuals.py) | Rebuilds Figures 01–05 and checks title spacing, alignment, and text containment |

Figures 01–03 and 05 are explanatory architectural diagrams. Figure 04 is generated from the committed calibration gate. Figure 06 is an AI-assisted conceptual workflow and is explicitly labeled as non-empirical. Communication assets are not study inputs, do not alter the frozen calibration, and must not be cited as additional evidence.

### End-to-end outcome-verification workflow

![From AI Usage to an Auditable Allocation Decision](communications/linkedin/outcome-verified-allocation/assets/06-end-to-end-ovar-workflow.png)

The workflow makes the evidence-to-action bridge operational:

1. **Define the decision:** identify the investment unit, accountable owner, action set, decision deadline, and resources that may change.
2. **Register the outcome:** prospectively specify the metric, threshold, evidence source, measurement window, practical-equivalence margin, and baseline design.
3. **Capture the trace:** bind model, token, retrieval, tool, retry, infrastructure, evaluation, and human events to stable work and episode identifiers.
4. **Reconcile fully loaded cost:** preserve provider, infrastructure, tooling, integration, evaluation, review, governance, rework, and remediation components.
5. **Verify evidence:** confirm that evidence is independently locatable, measured in the registered window, and supported by a reproduction note.
6. **Establish the baseline:** estimate the no-AI alternative with a registered comparison design and disclose concurrent events, spillovers, and limitations.
7. **Estimate net value:** combine attributable incremental benefit, complete cost, expected harm, maturity, and uncertainty rather than reporting point ROI alone.
8. **Validate authority:** evaluate subject, resource, action, purpose, scope, jurisdiction, valid dates, revocation, signer, and decision time as structured state.
9. **Issue the receipt:** select `STOP`, `REVISE`, `CONTINUE_PILOT`, `SCALE`, or `INDETERMINATE` and bind action, reasons, evidence state, authority, rule version, and hashes.
10. **Monitor and reassess:** invalidate or reopen the receipt when outcomes mature, costs change, authority expires, risk changes, or the operating context drifts.

The image is a conceptual implementation map, not an empirical result. The governing principle is that **consumption is an input to cost; verified incremental outcome, complete cost, uncertainty, risk, and current authority determine action**. The [full workflow explanation](communications/linkedin/outcome-verified-allocation/LINKEDIN_CONSOLIDATED_ARTICLE.md#end-to-end-workflow-from-investment-intent-to-a-verified-decision) includes implementation phases, precautions, and exit criteria.

### Tables, figures, and result artifacts

| Paper item | Content | Supporting artifact |
|---|---|---|
| Table 1 | Scope boundary and related research families | [Novelty decision memorandum](studies/ovar/novelty/NOVELTY_DECISION_MEMORANDUM_v1.0.md) and [comparison matrix](studies/ovar/novelty/comparison_matrix_v1.0.csv) |
| Table 2 | OVAR ledger fields and evidence contract | [Construct dictionary](studies/ovar/method/CONSTRUCT_DICTIONARY_v0.1.csv) |
| Table 3 | Five frozen comparison policies | [Calibration implementation](studies/ovar/calibration/implementation/calibration_policies_v1.0.mjs) |
| Table 4 | Construct-review dimensions and controls | [Construct-review metrics](studies/ovar/calibration/review/consolidated_v1.1/construct_recheck_metrics_v1.1.json) |
| Table 5 | Forty-eight-case benchmark coverage | [Reviewer-visible cases](studies/ovar/calibration/candidate_v1.1/construct_review_cases.json) |
| Table 6 | Prespecified calibration gate | [Prospective analysis plan](studies/ovar/calibration/PROSPECTIVE_ANALYSIS_PLAN_v1.0.md) |
| Table 7 | Policy-level calibration outcomes | [Calibration gate](studies/ovar/calibration/results/calibration_v1.0/calibration_gate.json) |
| Table 8 | Binding failure cases and mechanism | [Decision memorandum](studies/ovar/calibration/results/calibration_v1.0/CALIBRATION_DECISION_MEMORANDUM_v1.0.md) |
| Equations 1–5 | Full cost, attributed value, net value, policy loss, and allocation objective | [Formal objective and estimands](studies/ovar/method/FORMAL_OBJECTIVE_AND_ESTIMANDS_v0.1.md) |
| Figure 1 | OVAR outcome-evidence ledger workflow | [PNG](studies/ovar/publication/figures/ovar_ledger_workflow_v1.0.png) |
| Figure 2 | Policy error-rate comparison | [PNG](studies/ovar/publication/figures/policy_error_rates_v1.0.png) |
| Figure 3 | Measurement-burden sensitivity | [PNG](studies/ovar/publication/figures/burden_sensitivity_v1.0.png) |

Figures are generated by the versioned [manuscript builder](studies/ovar/publication/build_manuscript.py) from the committed results. They should not be edited manually and used as analytical evidence.

### Reproducibility map

| Need | Location |
|---|---|
| Scientific scope and limitations | [OVAR study README](studies/ovar/README.md) |
| Research concept and narrowed scope | [Research concept](studies/ovar/docs/RESEARCH_CONCEPT_v0.1.md) and [narrowed scope](studies/ovar/docs/NARROWED_RESEARCH_SCOPE_v0.2.md) |
| Causal and measurement model | [Causal model](studies/ovar/method/CAUSAL_MODEL_v0.1.md) and [formal objective](studies/ovar/method/FORMAL_OBJECTIVE_AND_ESTIMANDS_v0.1.md) |
| Calibration protocol and analysis plan | [Protocol](studies/ovar/calibration/CALIBRATION_DESIGN_PROTOCOL_v1.0.md) and [plan](studies/ovar/calibration/PROSPECTIVE_ANALYSIS_PLAN_v1.0.md) |
| Reviewer-visible cases | [candidate v1.1](studies/ovar/calibration/candidate_v1.1/construct_review_cases.json) |
| Policy implementation | [calibration_policies_v1.0.mjs](studies/ovar/calibration/implementation/calibration_policies_v1.0.mjs) |
| Tests | [calibration tests](studies/ovar/calibration/tests/calibration_policies_v1.0.test.mjs) and [pilot tests](studies/ovar/pilot/tests/pilot_v1.0.test.mjs) |
| Frozen result | [calibration gate](studies/ovar/calibration/results/calibration_v1.0/calibration_gate.json) |
| Decision interpretation | [calibration memorandum](studies/ovar/calibration/results/calibration_v1.0/CALIBRATION_DECISION_MEMORANDUM_v1.0.md) |
| Integrity closure | [calibration closure manifest](studies/ovar/calibration/CALIBRATION_CLOSURE_MANIFEST_v1.0.json) |
| Claim support | [claim-to-evidence ledger](studies/ovar/publication/CLAIM_TO_EVIDENCE_LEDGER_v1.0.csv) |
| Public technical interpretation | [consolidated article](communications/linkedin/outcome-verified-allocation/LINKEDIN_CONSOLIDATED_ARTICLE.md) and [visual provenance](communications/linkedin/outcome-verified-allocation/README.md) |
| Repository boundary check | [verify_repository.py](scripts/verify_repository.py) |

### Reproducibility expectations

A reproduction should satisfy all of the following conditions:

1. Use Node.js 20 or later and Python 3.11 or later from a clean checkout.
2. Treat the 24 pilot and 48 calibration cases as exposed engineering/design evidence, never as a new confirmatory test set.
3. Do not construct, reconstruct, or claim access to a held-out benchmark for OVAR v1.0.
4. Preserve the frozen policies, field whitelists, case/reference records, burden weights, loss coefficients, thresholds, and pre-execution hashes.
5. Run `make verify` before interpreting results; policy tests, reference arithmetic, and repository boundary checks must pass.
6. Treat committed JSON results as immutable historical outputs. Recomputed outputs belong in a separate directory and must be compared with the closure record.
7. Record Node.js/Python versions, operating system, commit hash, executed commands, and every deviation.
8. Report favorable and unfavorable results together, including two missed expired approvals, two false stops, and outcome-flat domination.
9. Do not describe synthetic-review agreement as human inter-rater reliability or design-case reproduction as field validation.

Minimum verification commands:

```bash
git rev-parse HEAD
node --version
python3 --version
make verify
```

A faithful reproduction should recover the frozen decision `REVISE_OR_STOP_PER_PROTOCOL` and the closure interpretation `STOP_OVAR_V1_NO_HELD_OUT`. A different result should be investigated as a code, input, environment, or protocol deviation rather than silently replacing the historical record.

### Research-integrity safeguards

- The broad novelty claim was narrowed after a logged 39-source audit; global uniqueness is not claimed.
- Reviewer-visible facts and reference actions were separated during construct review.
- Synthetic reviewers were isolated and blinded to reference labels and policy outcomes; their agreement is AI–AI consistency only.
- A blocking identifier/stratum shortcut was disclosed and corrected through the one permitted clarity-only revision.
- Policies receive only whitelisted fields; recursive forbidden-key checks reject adjudication-like data.
- Decisions do not branch on case identifiers, and distinct deterministic receipts are hashed.
- Pre-execution locks bind cases, labels, implementation, tests, and analysis rules before execution.
- The negative gate, dominating comparator, and failure cases are retained; thresholds were not relaxed.
- No held-out benchmark was created or accessed after the calibration failed.
- Public availability does not imply verified enterprise ROI, deployment readiness, external validity, or production authorization.

### Scope and limitations

The cases are deliberately constructed rather than drawn from live organizations. Reference outcomes are adjudicated design labels, not measured operational effects. The study has 48 calibration cases, only 13 safe continue/scale references, six represented domains, simplified costs, and a coarse fixed harm model. The authorization and risk layers rely on lexical rules, the central mechanism that failed. Synthetic review is not human-domain validation. There is no randomized field trial, external benchmark, portfolio allocation experiment, fairness evaluation, production telemetry, or confirmatory held-out result.

### Relationship to agentic systems

OVAR is relevant to agentic systems because one business outcome may consume resources across planning, retrieval, model inference, tools, retries, verification, and human escalation. A useful accounting unit must link those distributed traces to the responsible workflow, outcome contract, evidence, full cost, authorization, and decision receipt.

The repository is not a multi-agent orchestration framework. It neither deploys agents nor compares CrewAI, LangChain, model providers, gateways, or observability products. OVAR is a governance and measurement layer that could consume traces from single-agent, multi-agent, workflow, or conventional automation systems.

### Citation and responsible use

When referencing the project, distinguish between the repository, the OVAR method, and the ThinkAI manuscript. Use [`CITATION.cff`](CITATION.cff) for repository metadata and cite the final published paper once a DOI is assigned.

Do not state that OVAR v1.0 was validated, proven superior, or shown to improve organizational ROI. A faithful summary is:

> On a prospectively locked 48-case constructed calibration, outcome evidence reduced consumption-proxy errors, but OVAR v1.0 failed four of nine registered criteria because lexical authorization rules missed expired approvals, over-blocked valid in-scope work, and were dominated by a simpler outcome-flat policy.

## Research interpretation, limitations, and forward agenda

This section connects the registered hypothesis, observed outcome, defensible conclusion, and next research questions. It introduces no new experiment or effectiveness claim.

### Concrete hypothesis and observed outcome

The prospective OVAR v1.0 hypothesis was an **all-criteria calibration hypothesis**: the ledger policy had to improve decision errors over consumption and self-report proxies while remaining safe, completion-preserving, burden-conscious, stable across domains, and non-dominated. A favorable false-scale result could not compensate for an authorization or false-stop failure.

| Tested proposition | Observed calibration outcome | What the result supports |
|---|---|---|
| Reduce false-positive ROI relative to usage and self-report | 2/35 for OVAR versus 35/35 for each proxy policy | Outcome evidence is descriptively more discriminating than consumption or self-report on the constructed set |
| Avoid unsafe scaling | 0/35 false-scale decisions | The frozen OVAR policy was conservative about scale decisions represented in calibration |
| Preserve safe continue/scale work | 2/13 false stops, above the allowed tolerance | The completion proposition was not supported |
| Prevent authorization-related harmful decisions | Two expired approvals were missed | The lexical authorization safeguard failed its zero-violation criterion |
| Justify additional measurement burden | Weighted loss 1.155 at burden 0.800 versus outcome-flat 1.001 at 0.650 | The added OVAR mechanism did not justify its burden |
| Pass the complete prospective gate | Five of nine criteria passed | The composite OVAR v1.0 hypothesis was **not supported** |

The result is not “almost validated.” The gate is conjunctive, so each failed condition is binding. The research process succeeded in exposing a mechanism that favorable proxy comparisons might otherwise have hidden: unstructured text parsing cannot reliably distinguish an expired authorization from a current one or an excluded scope from the studied in-scope activity.

### Conclusions that can and cannot be drawn

The study supports three bounded methodological conclusions. First, enterprise AI consumption is not a defensible substitute for verified incremental value. Second, outcome contracts, baselines, evidence, full cost, and attribution confidence can be represented in a versioned decision ledger. Third, prospective multi-criterion gates can reject an elaborate method even when it improves selected metrics.

The study does **not** establish organizational ROI improvement, causal effectiveness, optimal budget allocation, production viability, globally novel tokenomics, authorization compliance, or superiority over all existing methods. It also does not show that outcome-flat is universally best; it shows only that outcome-flat dominated OVAR v1.0 under the constructed cases, frozen loss, and registered burden range.

### Limitations and what they convey

| Limitation | Consequence for interpretation |
|---|---|
| Constructed cases rather than organizational records | Results test method behavior under controlled patterns, not realized enterprise performance |
| Only 48 calibration cases and 13 safe references | Error rates are discrete and sensitive to a small number of cases |
| No held-out benchmark | The report is prospective calibration evidence, not confirmatory validation |
| Synthetic construct reviewers | Agreement reflects AI–AI rubric consistency, not independent human expertise |
| Reference decisions are constructed | They permit deterministic testing but do not replace measured causal outcomes or stakeholder adjudication |
| Fixed cost and harm abstractions | Financial and risk estimates do not capture every enterprise accounting, legal, or operational consequence |
| Lexical authorization and risk mapping | Temporal validity and scope semantics are too weak for operational control—the central negative finding |
| Six application domains | Transfer to other organizations, jurisdictions, workflows, and portfolio structures is unknown |
| No allocation simulation or field experiment | Hierarchical budgets, pooled reserves, carry-forward, access floors, and exploration policies remain future hypotheses |
| Similarity and final citation checks pending | Public release and submission still require institution-approved and author-controlled integrity checks |

These limitations define the study’s evidential boundary. They do not erase the negative result; they show why it belongs as a transparent methods and failure-analysis contribution rather than an effectiveness claim.

### Future research and testable next findings

A successor OVAR v2 should be separately registered and developed on newly constructed cases. Priority work is:

1. Replace lexical authorization parsing with structured records for subject, resource, action, purpose, jurisdiction, valid-from, valid-until, revocation state, required signer, scope, and decision timestamp.
2. Create new boundary cases that independently vary temporal expiry, revocation, nested scope, mixed in-scope/out-of-scope text, and conditional human approval.
3. Test whether structured authorization eliminates the four binding v1 errors without increasing measurement burden enough to remain dominated.
4. Obtain independent human review from finance, operations, governance, security/privacy, and domain stakeholders before field-facing claims.
5. Connect heterogeneous model, tool, retrieval, human-review, infrastructure, and rework traces to stable workflow and outcome identifiers.
6. Validate outcome contracts and fully loaded cost against operational records, with preregistered counterfactual designs and maturation windows.
7. Evaluate hierarchical portfolio allocation, access floors, exploration reserves, and internal carry-forward only after case-level value claims are reliable.
8. Stress-test Goodhart effects, gaming, delayed/shared value, uncertainty, fairness, strategic under-consumption, and incentive compatibility.
9. Freeze new code, cases, labels, weights, comparators, thresholds, and manifests before any successor held-out evaluation.

The next falsifiable hypothesis is therefore narrower and stronger: a prospectively frozen OVAR successor using structured temporal and scoped authorization records can preserve the false-scale benefit of outcome evidence, eliminate systematic authorization violations and false stops, and occupy a non-dominated error–burden position on new data. If it cannot, the correct outcome is another preserved negative result or a substantive pivot—not a relaxed gate.

## References

This reference map separates the author's research outputs from the external scholarship, standards, practice guidance, and implementation baselines that shaped the scope. The authoritative audit contains 39 records with overlap and disposition fields in the [novelty source register](studies/ovar/novelty/source_register.csv); the [search log](studies/ovar/novelty/search_log.csv), [comparison matrix](studies/ovar/novelty/comparison_matrix_v1.0.csv), and [novelty decision memorandum](studies/ovar/novelty/NOVELTY_DECISION_MEMORANDUM_v1.0.md) document how those sources narrowed the contribution.

### Author research outputs and communication

1. **Rasool, S. K. N. (2026). _From AI Usage to Auditable Outcomes: A Prospective Negative Calibration of Outcome-Verified AI Resource Allocation_.** ThinkAI 2026 camera-ready manuscript: [Word](papers/thinkai-2026/manuscript/OVAR_ThinkAI2026_CAMERA_READY_v1.0.docx), [PDF](papers/thinkai-2026/manuscript/OVAR_ThinkAI2026_CAMERA_READY_v1.0.pdf), and [declarations](papers/thinkai-2026/declarations/author_and_declarations.md).
2. **Rasool, S. K. N. (2026). _Outcome-Verified AI Resource Allocation research package_.** Protocols, cases, code, locks, calibration results, integrity records, and citation metadata in this [repository](https://github.com/khshaik/applied-ai-research-lab/tree/main/value-aware-enterprise-ai-tokenomics).
3. **Rasool, S. K. N. (2026). _From AI Usage to Auditable Outcomes: Engineering the Evidence Layer for Enterprise AI Allocation_.** Long-form technical communication connecting the problem statement, OVAR architecture, prospective negative gate, implementation precautions, and research-to-practice path. See the [consolidated article](communications/linkedin/outcome-verified-allocation/LINKEDIN_CONSOLIDATED_ARTICLE.md) and [visual dossier](communications/linkedin/outcome-verified-allocation/README.md).

### Token economics, agent resource allocation, and enterprise portfolio framing

- Zhu, Q. (2026), [AI Tokenomics: The Economics of Tokens, Computation, and Pricing in Foundation Models](https://arxiv.org/abs/2606.24616) — workflow production, pricing, allocation, and marginal productivity.
- Chen, Y., et al. (2026), [Token Economics for LLM Agents: A Dual-View Study from Computing and Economics](https://arxiv.org/abs/2605.09104) — token budgets across single-agent, multi-agent, ecosystem, and security levels.
- Zhu, S. (2026), [Agentic AI Systems Should Be Designed as Marginal Token Allocators](https://arxiv.org/abs/2605.01214) — marginal benefit, cost, latency, and risk allocation.
- Salim, M., et al. (2026), [Tokenomics: Quantifying Where Tokens Are Used in Agentic Software Engineering](https://arxiv.org/abs/2601.14470) — token distribution across agentic software-development work.
- Bai, L., et al. (2026), [How Do AI Agents Spend Your Money?](https://arxiv.org/abs/2604.22750) — agentic token variability, accuracy relationships, and cost prediction.
- Provost, F., and Ipeirotis, P. (2026), [AI Strategy: How to Choose What AI Product to Implement](https://arxiv.org/abs/2607.23733) — expected ROI and AI portfolio selection.
- Polamarasetty, V. K. (2026), [Measuring Enterprise AI Value in the Agentic AI Era](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6986058) — closed-loop adoption, decision intelligence, and enterprise ROI optimization.
- Krishnan, S., Hepp, A., and Gandhi, S. (2026), [A Multi-Layer Framework for Evaluating the Return on Investment of AI Projects](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6732598) — readiness, stage gates, risk adjustment, and decision scorecards.
- Lee, J., et al. (2026), [Transferability of Token Usage Rights](https://arxiv.org/abs/2604.26683) — carry-over, transfer, co-management, and conversion of usage rights.
- [Can LLM Agents Be CFOs?](https://arxiv.org/abs/2603.23638) (2026) — long-horizon resource allocation in dynamic enterprise environments.

### Cost, quality, routing, and token-efficiency methods

- Chen, L., Zaharia, M., and Zou, J. (2023), [FrugalGPT](https://arxiv.org/abs/2305.05176) — LLM cascades for lower inference cost with retained quality.
- Ong, I., et al. (2024), [RouteLLM](https://arxiv.org/abs/2406.18665) — preference-based model routing under cost-quality trade-offs.
- Aggarwal, P., et al. (2023), [AutoMix](https://arxiv.org/abs/2310.12963) — adaptive mixing of language models.
- Jiang, H., et al. (2023), [LLMLingua](https://arxiv.org/abs/2310.05736) — prompt compression for faster, lower-token inference.
- [Towards Optimizing the Costs of LLM Usage](https://arxiv.org/abs/2402.01742) (2024) — model selection, token reduction, and quality-cost-latency optimization.
- [Token-Budget-Aware LLM Reasoning](https://aclanthology.org/2025.findings-acl.1274/) (2025) — adaptive reasoning-token budgets.
- [Reasoning in Token Economies](https://aclanthology.org/2024.emnlp-main.1112/) (2024) — compute-matched evaluation of reasoning strategies.
- [Cut the Crap](https://arxiv.org/abs/2410.02506) (2024) — communication pruning in LLM-based multi-agent systems.
- [Budget-Aware Anytime Reasoning](https://aclanthology.org/2026.findings-acl.417/) (2026) — quality improvement under a fixed reasoning budget.

These works optimize or allocate compute under cost, quality, latency, or risk constraints. OVAR's retained boundary is downstream: whether outcome evidence and causal attribution justify a portfolio action after the workflow operates.

### Causal outcome and productivity evidence

- Noy, S., and Zhang, W. (2023), [Experimental Evidence on the Productivity Effects of Generative Artificial Intelligence](https://doi.org/10.1126/science.adh2586) — preregistered causal productivity and quality measurement.
- Brynjolfsson, E., Li, D., and Raymond, L. R. (2025), [Generative AI at Work](https://doi.org/10.1093/qje/qjae044) — field productivity effects, quality, and worker heterogeneity.
- Peng, S., et al. (2023), [The Impact of AI on Developer Productivity: Evidence from GitHub Copilot](https://arxiv.org/abs/2302.06590) — controlled developer-productivity experiment.
- [Does Generative AI Narrow Education-Based Productivity Gaps?](https://www.nber.org/papers/w34851) (2026) — randomized evidence on productivity and heterogeneous access effects.

These studies demonstrate why exposure, comparator design, outcome measurement, and heterogeneity are required before usage can become a causal value claim.

### Standards and practice guidance

- National Institute of Standards and Technology, [AI Risk Management Framework 1.0](https://www.nist.gov/itl/ai-risk-management-framework) — objectives, evidence, measurement, risk, and governance.
- International Organization for Standardization, [ISO/IEC 42001:2023](https://www.iso.org/standard/42001) — organizational AI management, risk, opportunity, and continual improvement.
- FinOps Foundation, [FinOps for AI](https://www.finops.org/framework/technology-categories/ai/) — AI cost allocation, forecasting, optimization, governance, and value alignment.
- FinOps Foundation, [How to Build a Generative AI Cost and Usage Tracker](https://www.finops.org/wg/how-to-build-a-generative-ai-cost-and-usage-tracker/) — token tracking, shared capacity, and cost attribution.
- FinOps Foundation, [Tokenomics: Managing AI Value in SaaS Model Token Costs](https://www.finops.org/wg/token-economics-saas/) — budgets, unit costs, and token-cost governance.
- OpenTelemetry, [Generative AI Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/) — normalized model and workflow trace attributes.
- FinOps Open Cost and Usage Specification, [FOCUS](https://focus.finops.org/) — normalized technology cost-and-usage schema.

### Telemetry and implementation baselines

- [LiteLLM](https://github.com/BerriAI/litellm) — model gateway, routing, virtual keys, spend tracking, and logging.
- [Langfuse](https://github.com/langfuse/langfuse) — LLM observability, traces, evaluation, and metrics.
- [OpenLIT](https://github.com/openlit/openlit) — OpenTelemetry-native AI observability, token cost, evaluation, and infrastructure monitoring.
- [Opik](https://github.com/comet-ml/opik) — tracing, evaluation, monitoring, and optimization.
- [OpenInference](https://github.com/Arize-ai/openinference) — semantic conventions for AI traces.

These tools are possible telemetry inputs. The repository does not claim to replace them and does not evaluate them as products.

### Patent and product-boundary records

The novelty audit also reviewed [pre-execution AI-model cost prediction](https://patents.google.com/patent/US20260119922A1/en), [hybrid inference for cost-of-goods reduction](https://patents.google.com/patent/US12524210B2/), [cloud-service resource allocation](https://patents.google.com/patent/US20250097163A1/en), and [management-rule enforcement for model routing](https://patents.google.com/patent/US20250363200A1). These records constrain novelty claims around cost prediction, routing, allocation, and enforcement; OVAR does not claim those mechanisms.

### Citation and interpretation note

Use [`CITATION.cff`](CITATION.cff) for repository metadata and cite the final paper once a DOI is assigned. External publications remain subject to their respective rights. Inclusion here indicates relevance or boundary-setting, not endorsement and not proof of global novelty. The study's supported claim remains limited to prospective behavior on the constructed calibration and the identified authorization failure mechanism.
