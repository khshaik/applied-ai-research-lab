<h1 align="center">Action Evidence Safety: From Stale Evidence to Safe Execution</h1>

<p align="center"><strong>An end-to-end research framework for deciding what to revalidate, when to abstain, and how to protect authorization before consequential automated actions</strong></p>

<p align="center">Evidence revalidation · Authorization safety · Budgeted validation · Prospective evaluation</p>

<p align="center">
  <img alt="Python 3.11+" src="https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white">
  <img alt="Standard library" src="https://img.shields.io/badge/Runtime-Standard%20Library-4B8BBE">
  <img alt="JSON" src="https://img.shields.io/badge/Data-JSON-292929?logo=json&logoColor=white">
  <img alt="CSV" src="https://img.shields.io/badge/Data-CSV-217346">
  <img alt="unittest" src="https://img.shields.io/badge/Testing-unittest-6C4FBB">
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
  <a href="#papers-and-submission-files"><strong>Papers &amp; Artifacts</strong></a> ·
  <a href="#reproducibility-expectations"><strong>Reproducibility</strong></a>
</p>

Research on whether consequential automated actions should proceed when their authorization, policy, identity, scope, or operational prerequisites may have changed.

This repository is a research monorepo: each study has an isolated protocol, benchmark, implementation, results, integrity record, and paper directory. The first study is **Risk-Adaptive Evidence Revalidation (RAER)**.

> **Double-blind review notice:** keep this repository **private** while an identified manuscript is under double-blind review. The `papers/thinkai-2026/` directory and repository license identify the author. Do not publish the repository or create a public Zenodo deposit until the venue permits deanonymization.

## Author

Shaik Khaja Nayab Rasool.

---

## Research project dossier

### Project identity

**Risk-Adaptive Evidence Revalidation for Consequential Tool Actions**<br>
*A prospective failure analysis of budgeted, authorization-sensitive evidence checking before an automated action.*

| Item | Description |
|---|---|
| Research area | AI safety, agentic systems, decision-making under uncertainty, evidence validity, authorization governance |
| Study type | Methods research with a constructed benchmark and prospectively specified design gate |
| Primary method | Risk-Adaptive Evidence Revalidation (RAER v2) |
| Unit of analysis | A proposed consequential action with three mutable evidence prerequisites |
| Evaluation scope | 72 exposed design cases across six domains; 24 held-out cases remain sealed |
| Current conclusion | Promising descriptive safety-cost trade-off, but the prespecified design hypothesis was not supported |
| Publication framing | Transparent methods and prospective negative-results paper |

### Dossier coverage at a glance

| Research-project requirement | Where it is documented |
|---|---|
| Direct artifact links | [Papers and submission files](#papers-and-submission-files), [Tables, figures, and result artifacts](#tables-figures-and-result-artifacts), and [Reproducibility map](#reproducibility-map) |
| Explicit hypothesis and outcome | [Hypothesis and decision rule](#hypothesis-and-decision-rule) and [Main design-stage results](#main-design-stage-results) |
| Benchmark coverage | [Benchmark design](#benchmark-design) and the [reviewer-visible benchmark](studies/raer/calibration/benchmark/release_v1.1/reviewer_visible_cases.json) |
| Analytical methods | [Method overview](#method-overview) and [Analysis performed](#analysis-performed) |
| Technology boundaries | [Key technologies and libraries](#key-technologies-and-libraries) and [Technology boundaries](#technology-boundaries) |
| Reproducibility expectations | [Quick verification](#quick-verification), [Reproducibility map](#reproducibility-map), and [Reproducibility expectations](#reproducibility-expectations) |

### Problem statement

Automated systems may prepare an action using evidence that was correct when observed but no longer valid when the action is executed. Authorization may be revoked, a policy may change, an identity binding may expire, or operational state may drift. Rechecking every prerequisite can consume latency, money, rate limits, or human attention, while reusing every stored observation can permit an unsafe or unauthorized action.

The research problem is therefore:

> How should an automated system select which action-specific prerequisites to revalidate under a limited validation budget, while balancing harmful action, unnecessary abstention, validation cost, authorization safety, and safe task completion?

RAER addresses the decision before execution. It does not evaluate which commercial tool or agent framework performs best.

### Research questions

1. Can action-specific prerequisite revalidation reduce harmful actions without requiring exhaustive evidence refresh?
2. Can harmful-action loss, abstention loss, and validation cost be combined in an interpretable constrained objective?
3. Does a prespecified authorization safeguard prevent harmful actions caused by unchecked, invalid authorization evidence?
4. Can a configuration selected on five domains transfer to a sixth domain without materially degrading safe completion?
5. Can prospective gates and sealed test data prevent favorable descriptive results from being overstated as validation?

## The problem in one minute

Many automated actions are safe only while several supporting facts remain valid. A system may verify those facts when planning an action, but the world can change before execution.

```text
Evidence collected            State changes                 Action executes
        t0                         t1                              t2
        |                          |                               |
 "Approved and valid"    authorization revoked,        system still relies on
                         policy updated, identity         the evidence from t0
                         changed, resource moved
```

The central risk is a **time-of-check to time-of-action evidence gap**. The system may reason correctly from its stored evidence and still perform the wrong action because one prerequisite became invalid after it was observed.

Checking everything again is not always practical. Authoritative validation may require a human approval, a slow system of record, a paid service, a rate-limited API, or an operational interruption. The system must decide:

1. Which evidence is important enough to revalidate now?
2. Which checks fit within the available cost or latency budget?
3. Should the action proceed if all selected checks remain valid?
4. Should the system refresh state, request renewed authority, or abstain?
5. How can safety improve without blocking too many valid actions?

RAER studies this decision boundary before execution.

## Why ordinary controls do not completely resolve it

Existing controls remain necessary, but each usually addresses only part of the problem:

| Existing control | What it helps with | Remaining gap studied here |
|---|---|---|
| Authentication | Confirms who or what is making a request | Does not prove that a previously granted action-specific authorization is still active |
| Access control | Checks a permission against a policy | May not cover changed purpose, scope, consent, state, or dependent prerequisites |
| Input validation | Checks syntax, type, and allowed values | Cannot establish that an externally observed fact is still current |
| Transaction checks | Protect consistency at commit time | May not identify which upstream evidence should be refreshed before commitment |
| Confidence scoring | Estimates model or prediction confidence | Is not the same as validity of authorization, identity, policy, inventory, or operational state |
| Refresh everything | Minimizes stale-evidence reuse | Can be too costly, slow, disruptive, or impossible under a validation budget |
| Fixed refresh threshold | Rechecks evidence above one cutoff | Can ignore action consequence, evidence criticality, correlation, and authorization sensitivity |
| Human approval | Adds accountable oversight | Human attention is limited and still depends on current, correctly scoped evidence |

The open engineering and research challenge is not the absence of authentication, policy enforcement, or validation tools. It is the absence of a generally validated decision mechanism that jointly handles **mutable action prerequisites, limited validation resources, authorization safeguards, abstention cost, and safe completion across domains**. RAER is an experimental method for that combined problem; the present results do not establish that it has solved it.

## Cross-industry examples

The following are illustrative problem scenarios, not reports of real incidents and not additional benchmark results.

### Healthcare and medical administration

A system prepares to schedule or authorize a high-cost procedure using a referral, patient identity match, payer authorization, and current clinical order. Before execution, the authorization expires or the clinical order changes.

- **If it acts:** the patient may receive an incorrectly scheduled service, experience a billing dispute, or bypass a required clinical review.
- **If it always abstains:** valid and time-sensitive care may be delayed.
- **Evidence-selection problem:** determine whether to recheck authorization, patient-order binding, eligibility, or all prerequisites within the available time.

RAER does not provide medical advice or clinical validation. It studies the pre-action evidence-control problem around an administrative action.

### Banking, payments, and finance

A payment workflow prepares a beneficiary change or fund transfer using identity verification, account status, transaction authority, and fraud-screening state. Authority is revoked or the destination account changes after the evidence was collected.

- **If it acts:** funds may be sent without current authority or to an invalid destination.
- **If it refreshes everything:** the transaction may miss a legitimate settlement deadline and incur unnecessary cost.
- **Evidence-selection problem:** prioritize high-consequence authorization and destination-binding checks without treating every transaction as equally risky.

### E-commerce and digital marketplaces

An order service prepares a refund, cancellation, address change, price correction, or inventory commitment. Customer authorization, catalogue price, fulfillment state, or available inventory changes before commitment.

- **If it acts:** the service may refund the wrong party, ship to an outdated address, apply an invalid price, or promise unavailable inventory.
- **If it blocks too often:** legitimate purchases and customer-service requests fail.
- **Evidence-selection problem:** balance customer authorization, order state, fulfilment state, and validation cost for the proposed action.

### Transportation and logistics

A dispatch system prepares to reroute a vehicle, release a shipment, assign a driver, or change a delivery destination. Driver eligibility, cargo restrictions, route conditions, customer authority, or vehicle availability changes after planning.

- **If it acts:** a shipment may be released to the wrong destination, a route may violate a new restriction, or an unavailable resource may be assigned.
- **If it revalidates every dependency:** time-critical dispatch can become too slow.
- **Evidence-selection problem:** identify the minimum sufficient checks while treating safety-critical and authorization evidence conservatively.

Transportation is an illustrative extension domain; it is not one of the six domains in the current RAER-B96 benchmark.

### Cybersecurity and access operations

A security workflow prepares to release quarantined content, rotate credentials, isolate a host, or change access using a ticket, asset state, policy, incident severity, and approver authority. The incident classification or approval changes before execution.

- **If it acts:** it may restore malicious content, revoke legitimate access, or execute a privileged change without current authority.
- **If it abstains indiscriminately:** incident response may be delayed.
- **Evidence-selection problem:** revalidate the prerequisites whose invalidity would make the specific action unsafe or impermissible.

### Privacy and data governance

A workflow prepares to send a campaign, export records, apply a retention action, or satisfy a data-subject request. Consent, identity binding, legal hold, jurisdiction, or requested scope changes before execution.

- **If it acts:** data may be disclosed, retained, deleted, or processed outside the current authorized scope.
- **If it blocks every uncertain case:** legitimate rights requests and operational obligations may not be completed on time.
- **Evidence-selection problem:** give authorization and scope evidence special treatment while controlling unnecessary abstention.

### Human resources and workforce systems

A workforce workflow prepares an offer, compensation update, access change, schedule adjustment, or offboarding action. Manager approval, employment state, labor constraint, or effective date changes before execution.

- **If it acts:** the wrong access, payment, employment, or scheduling state may be committed.
- **If it delays every action:** onboarding, payroll, staffing, and offboarding workflows may be disrupted.
- **Evidence-selection problem:** recheck the most consequential and irreversible prerequisites within the operational budget.

## The desired safety behavior

RAER separates four outcomes that are often collapsed into a single proceed/deny response:

| Decision | Meaning |
|---|---|
| `ACT` | Selected checks remain valid and modeled action loss is acceptable |
| `REFRESH` | A checked state, policy, identity, or scope prerequisite is invalid and updated evidence is required |
| `ASK` | A checked authorization prerequisite is invalid and renewed human or institutional authority is required |
| `ABSTAIN` | Available checks and modeled risk do not justify executing the action within the allowed budget |

The goal is not maximum automation. It is a defensible balance among safety, completion, authority, and validation cost—with every trade-off recorded and evaluated prospectively.

## Current study

RAER asks which action-specific evidence should be revalidated under a limited budget and when a system should act, request renewed authority, refresh state, or abstain.

The current RAER v2 result is a prospective negative design-stage result:

- 72 exposed design cases across six domains;
- 24 held-out cases remain sealed and are not in this repository;
- harmful action: 14/45 invalid cases (31.1%);
- safe completion: 25/27 valid cases (92.6%);
- the registered 95% safe-completion requirement was not met;
- no confirmatory or deployment-effectiveness claim is made.

See [`studies/raer/README.md`](studies/raer/README.md) for the scientific scope and reproducibility boundary.

## Repository layout

```text
.
├── studies/
│   └── raer/                 # Benchmark, evaluators, results, integrity records
├── papers/
│   ├── thinkai-2026/         # Identified manuscript and declarations
│   └── _template/            # Starting structure for later papers
├── docs/                     # Governance and repository conventions
├── scripts/                  # Repository-level verification
├── .github/workflows/        # Continuous integration
├── CITATION.cff
├── LICENSE
└── pyproject.toml
```

## Quick verification

Python 3.11 or later is recommended. The research evaluators and tests use only the Python standard library.

```bash
python3 scripts/verify_repository.py
python3 studies/raer/evaluation/test_raer_benchmark.py
python3 studies/raer/evaluation/v2/test_raer_v2_design.py
```

Or run:

```bash
make verify
```

## Reuse and citation

Code and repository-owned data are licensed under the MIT License unless a file states otherwise. Citation metadata are provided in [`CITATION.cff`](CITATION.cff). Referenced publications remain subject to their respective rights.

### Hypothesis and decision rule

The binding RAER v2 design hypothesis was composite: the method had to occupy a useful safety-cost position **and pass every prespecified operational criterion** on leave-one-domain-out design evaluation.

The registered gate required:

- safe completion within five percentage points of the best registered comparator;
- harmful-action rate no worse than `FIXED_0.20`;
- zero harmful actions caused by unchecked triggered authorization evidence;
- no comparable-safe policy dominating RAER v2 on both harm and cost;
- positive budget-slack use in no more than 25% of cases;
- mean slack no greater than 0.025 and maximum slack no greater than 0.05;
- an eligible configuration in at least five of six outer-domain folds.

**Decision:** the composite hypothesis was **not supported**. RAER v2 passed seven of eight criteria but achieved 25/27 safe completions (92.6%), below the required 95%. The correct interpretation is not that the research process failed; the prespecified v2 design hypothesis failed, and the held-out set was preserved.

### Method overview

For a candidate subset of evidence checks, RAER v2 combines:

```text
expected loss
= harmful-action loss
+ unnecessary-abstention loss
+ validation cost
+ controlled budget-slack penalty
```

The method uses:

- a frozen monotone evidence-invalidity estimator based only on pre-action observable features;
- consequence, irreversibility, authorization sensitivity, criticality, and validation-cost rubric scores;
- exact enumeration of feasible evidence subsets;
- deterministic tie-breaking by cost, residual harm, check count, and evidence identifier;
- an authorization safeguard for sufficiently sensitive and risky authorization prerequisites;
- a maximum boundary slack of 0.05 with an explicit penalty;
- `ACT`, `ABSTAIN`, `ASK`, and `REFRESH` outcomes determined by selected checks and their observed validity.

The complete mathematical definition is in the [RAER v2 method specification](studies/raer/evaluation/v2/RAER_V2_METHOD_SPECIFICATION_v1.0.json). The frozen design rules are in the [prospective design plan](studies/raer/evaluation/v2/RAER_V2_PROSPECTIVE_DESIGN_PLAN_v1.0.json).

### Benchmark design

RAER-B96 contains 96 constructed scenarios and 288 evidence prerequisites.

| Dimension | Coverage |
|---|---|
| Domains | Commerce, cybersecurity, finance, healthcare administration, human resources, privacy |
| Cases per domain | 16 |
| Evidence prerequisites per case | 3 |
| Original partitions | 48 development, 24 validation, 24 held-out |
| Exposed design set used by v2 | 72 cases: 27 all-valid and 45 containing at least one invalid prerequisite |
| State patterns | All-valid, single invalidity, correlated failures, independent dual failures, authorization revocation, policy change, contradiction, budget insufficiency |
| Reviewer separation | Reviewer-visible operational facts were separated from investigator-only validity labels |

Start with the [reviewer-visible benchmark](studies/raer/calibration/benchmark/release_v1.1/reviewer_visible_cases.json), its [schema](studies/raer/calibration/benchmark/release_v1.1/reviewer_visible_schema.json), and the [scenario provenance register](studies/raer/calibration/benchmark/release_v1.1/scenario_provenance.json).

### Analysis performed

The completed analysis includes:

- exact evaluation against eight registered comparators;
- an 80-configuration prospective RAER v2 grid;
- six-fold leave-one-domain-out configuration selection;
- deterministic policy execution and recorded tie-breaking;
- domain-stratified bootstrap uncertainty with a fixed seed and 10,000 replicates;
- non-dominance and budget-slack checks;
- authorization-specific harmful-action analysis;
- ablations for abstention loss, authorization safeguard, slack, and correlation uplift;
- failure-category analysis of the two out-of-fold false blocks;
- v1-to-v2 methodological history without relabelling v1 outcomes as v2 evidence;
- frozen manifests and SHA-256 integrity checks before and after evaluation.

### Main design-stage results

| Measure | RAER v2 OOF | `FIXED_0.20` | Interpretation |
|---|---:|---:|---|
| Safe completion on valid cases | 25/27 (92.6%) | 27/27 (100.0%) | RAER v2 failed the registered ≥95% requirement |
| Harmful actions on invalid cases | 14/45 (31.1%) | 18/45 (40.0%) | Favorable descriptive difference; not confirmatory |
| Mean validation cost | 0.547 | 0.800 | Lower descriptive cost for RAER v2 |
| False blocks | 2 | 0 | Cross-domain completion instability |
| Triggered-authorization harmful actions | 0 | 0 | RAER v2 passed its authorization criterion |
| Prospective criteria passed | 7/8 | Not applicable | Overall gate decision remained failure |

The authoritative machine-readable decision is [v2_design_gate.json](studies/raer/evaluation/v2/results_design_v1.0/v2_design_gate.json). Detailed outcomes are available in [oof_policy_outcomes.csv](studies/raer/evaluation/v2/results_design_v1.0/oof_policy_outcomes.csv), [oof_policy_summary.csv](studies/raer/evaluation/v2/results_design_v1.0/oof_policy_summary.csv), and [bootstrap_intervals.json](studies/raer/evaluation/v2/results_design_v1.0/bootstrap_intervals.json).

### Research history and work completed

1. **Feasibility pilot:** established deterministic scenario execution, evidence selection, diagnostics, and immutable pilot records.
2. **Novelty audit:** screened close research and narrowed the contribution after identifying prior work combining budgeted evidence acquisition and abstention.
3. **Calibration protocol:** defined leakage-safe evidence-invalidity estimation and scoring rubrics for consequence, irreversibility, authorization sensitivity, criticality, and cost.
4. **Benchmark construction:** created 96 cases across six domains, separated reviewer-visible facts from investigator labels, and performed blinded clarity and anti-shortcut checks.
5. **RAER v1 evaluation:** preserved a negative validation result and stopped before consuming held-out labels.
6. **RAER v2 formulation:** prospectively froze an abstention-aware expected-loss objective, authorization safeguard, controlled slack rule, comparators, metrics, and decision gate.
7. **Design-only evaluation:** performed leave-one-domain-out selection, bootstrap analysis, ablations, and failure analysis on the 72 exposed cases.
8. **Research closure:** recorded the failed safe-completion criterion, retained all favorable and unfavorable outcomes, and kept the 24-case test partition sealed.
9. **Manuscript preparation:** produced editable Word and matching PDF versions with declarations, citation verification, and a claim-to-evidence ledger.

### Key technologies and libraries

| Technology | Use in this project |
|---|---|
| Python 3.11+ | Reference evaluators, exact subset enumeration, analysis, tests, and verification |
| Python standard library | `argparse`, `csv`, `hashlib`, `itertools`, `json`, `math`, `pathlib`, `random`, `unittest`, and collection utilities |
| JSON and CSV | Versionable benchmark, protocol, manifest, score, outcome, and summary formats |
| SHA-256 | Immutable release locks, artifact manifests, and integrity verification |
| `unittest` | Determinism, boundary, authorization, outcome, and summary-denominator tests |
| Git and GitHub Actions | Version control and automated research-integrity/test checks |
| Microsoft Word and PDF | Editable manuscript source and visually verified submission rendering |

The evaluation runtime deliberately has no mandatory NumPy, pandas, scikit-learn, orchestration-framework, model-provider, or external API dependency. This keeps the reference computation inspectable and reproducible with the Python standard library.

### Technology boundaries

The repository separates the **research method**, **reference implementation**, and **possible deployment context**:

- RAER is a deterministic evidence-selection and action-control method, not a language model, agent framework, tool router, or workflow orchestrator.
- The committed evaluator does not call an LLM, external API, database, vector store, browser, or live operational system.
- The constructed benchmark does not contain production telemetry or claim to simulate every behavior of a deployed agent.
- Synthetic model review supported rubric and scenario stress testing, but it is not part of runtime inference and is not treated as independent human validation.
- Word and PDF applications were used for manuscript preparation and visual verification; they are not dependencies of the analytical evaluator.
- A production integration would require separate work on authoritative data connectors, identity and access control, policy enforcement, latency, monitoring, audit logging, fault handling, security testing, and external validation.
- Any future implementation using an agentic or multi-agent architecture must preserve the same evidence/label separation and may not infer hidden validity labels from benchmark construction patterns.

### Papers and submission files

| Artifact | Format | Purpose |
|---|---|---|
| [Camera-ready manuscript](papers/thinkai-2026/manuscript/RAER_v2_ThinkAI2026_CAMERA_READY_v1.0.docx) | Word (`.docx`) | Editable identified manuscript |
| [Camera-ready manuscript](papers/thinkai-2026/manuscript/RAER_v2_ThinkAI2026_CAMERA_READY_v1.0.pdf) | PDF | 14-page Word-exported version used for visual verification |
| [Author and declarations](papers/thinkai-2026/declarations/author_and_declarations.md) | Markdown | Authorship, interests, funding, ethics, CRediT, AI-use, and availability declarations |
| [ThinkAI submission notes](papers/thinkai-2026/README.md) | Markdown | Venue status, formatting, confidentiality, and pending actions |

The Word and PDF manuscripts contain the same research narrative. The PDF was visually checked page by page; Tables 1–8 and Equations 1–5 render without clipping or broken table pagination.

### Tables, figures, and result artifacts

The current paper is table- and equation-led; no standalone generated figure is required to interpret the reported result.

| Paper item | Content | Supporting artifact |
|---|---|---|
| Table 1 | Closest research families and bounded novelty claim | Manuscript and citation log |
| Table 2 | Reviewer scoring dimensions | [Adjudicated scores](studies/raer/calibration/benchmark/release_v1.1/adjudicated_master_scores.json) |
| Table 3 | Prospective RAER v2 configuration grid | [Method specification](studies/raer/evaluation/v2/RAER_V2_METHOD_SPECIFICATION_v1.0.json) |
| Table 4 | Prospective v2 gate | [Design plan](studies/raer/evaluation/v2/RAER_V2_PROSPECTIVE_DESIGN_PLAN_v1.0.json) |
| Table 5 | Main design-stage results | [OOF policy summary](studies/raer/evaluation/v2/results_design_v1.0/oof_policy_summary.csv) |
| Table 6 | Registered gate outcome | [Gate decision](studies/raer/evaluation/v2/results_design_v1.0/v2_design_gate.json) |
| Table 7 | Out-of-fold false blocks | [OOF policy outcomes](studies/raer/evaluation/v2/results_design_v1.0/oof_policy_outcomes.csv) |
| Table 8 | Design-data ablations | [Ablation results](studies/raer/evaluation/v2/results_design_v1.0/ablations.csv) |
| Equations 1–5 | Invalidity estimate, harm, residual risk, safe-probability proxy, and expected-loss objective | [Method specification](studies/raer/evaluation/v2/RAER_V2_METHOD_SPECIFICATION_v1.0.json) |

Future figures should be generated from immutable CSV/JSON results by a versioned script and committed with a caption, source-data path, and generation command. Manually edited result graphics should not be used as analytical evidence.

### Reproducibility map

| Need | Location |
|---|---|
| Scientific scope and limitations | [RAER study README](studies/raer/README.md) |
| Statistical analysis plan | [STATISTICAL_ANALYSIS_PLAN_v1.0.json](studies/raer/evaluation/STATISTICAL_ANALYSIS_PLAN_v1.0.json) |
| v1 implementation | [raer_benchmark.py](studies/raer/evaluation/raer_benchmark.py) |
| v2 implementation | [raer_v2_design.py](studies/raer/evaluation/v2/raer_v2_design.py) |
| v1 tests | [test_raer_benchmark.py](studies/raer/evaluation/test_raer_benchmark.py) |
| v2 tests | [test_raer_v2_design.py](studies/raer/evaluation/v2/test_raer_v2_design.py) |
| Design closure | [V2_DESIGN_CLOSURE_MANIFEST_v1.0.json](studies/raer/integrity/V2_DESIGN_CLOSURE_MANIFEST_v1.0.json) |
| Claim support | [Claim-to-evidence ledger](studies/raer/integrity/RAER_Claim_to_Evidence_Ledger_v0.2.csv) |
| Citation checks | [Citation-verification log](studies/raer/integrity/RAER_Citation_Verification_Log_v0.2.csv) |
| Repository boundary check | [verify_repository.py](scripts/verify_repository.py) |

### Reproducibility expectations

A reproduction should satisfy all of the following conditions:

1. Use Python 3.11 or later and run the repository from a clean checkout.
2. Do not add, reconstruct, or inspect the sealed 24-case held-out label partition.
3. Preserve the frozen benchmark text, partitions, scoring records, estimator coefficients, candidate grid, comparator definitions, bootstrap seed, and gate thresholds.
4. Run `make verify` before interpreting results; all 15 unit tests and the restricted-artifact boundary check must pass.
5. Treat the committed CSV and JSON outputs as immutable historical results. Recomputed outputs should be written to a separate directory and compared against the recorded manifests.
6. Record the operating system, Python version, commit hash, commands executed, and any deviation from the frozen protocol.
7. Report both favorable and unfavorable metrics, including the two false blocks and the failed safe-completion criterion.
8. Do not describe design-data reproduction as an independent held-out replication or effectiveness validation.

Minimum verification commands:

```bash
git rev-parse HEAD
python3 --version
make verify
```

A scientifically faithful reproduction should recover the registered decision `FAIL_KEEP_HELD_OUT_SEALED`. A different result should be investigated as a code, input, environment, or protocol deviation rather than silently replacing the historical record.

### Research-integrity safeguards

- The invalidity estimator uses only pre-action features; actual validity is not used to calculate its estimate.
- Reviewer-visible facts and investigator validity labels were structurally separated.
- Synthetic model reviewers were used for methodological stress testing and are not represented as human inter-rater validation.
- Development and validation cases are explicitly labelled design evidence.
- The held-out label file is absent and prohibited by repository checks.
- Frozen protocols, code, inputs, and results are bound by hashes and additive closure manifests.
- Negative outcomes are retained; thresholds are not relaxed after seeing results.
- Novelty is bounded to the screened literature and is not described as proof of global uniqueness.
- Public availability does not imply production readiness, clinical validity, legal compliance, or external effectiveness.

### Scope and limitations

The benchmark is constructed rather than operational. The design analysis contains only 27 all-valid cases, making safe-completion estimates discrete and uncertain. Rubric values and the frozen invalidity estimator are interpretable proxies rather than calibrated deployment probabilities. The benchmark has no external dataset, production latency measurement, field deployment, independent human-domain validation, or confirmatory held-out result. Generalization beyond the benchmark is unsupported.

### Relationship to agentic systems

This work is relevant to tool-using and agentic systems because such systems may execute state-changing actions based on mutable observations. RAER contributes a pre-action safety and governance layer: it reasons about prerequisite evidence, validation cost, authorization, state drift, and abstention before an action is allowed to proceed.

The repository is not an implementation of a multi-agent orchestration or content-generation framework. Its focus is the evidence-validity decision boundary that could be integrated into single-agent, multi-agent, workflow, or conventional automation architectures.

### Citation and responsible use

When referencing the project, distinguish between the repository, the RAER method, and the ThinkAI manuscript. Use [`CITATION.cff`](CITATION.cff) for repository metadata and cite the final published paper once its bibliographic record is available.

Do not state that RAER v2 was validated, proven superior, or shown to be deployment-ready. A faithful summary is:

> RAER v2 showed a promising descriptive harm-cost trade-off on exposed design data but did not satisfy its prospectively registered safe-completion criterion; the held-out test partition remained sealed.
