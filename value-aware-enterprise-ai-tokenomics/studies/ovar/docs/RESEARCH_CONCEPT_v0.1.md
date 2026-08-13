# OVAR Research Concept v0.1

## 1. Research objective

Design and prospectively evaluate an organization-level method for allocating AI resource budgets according to independently verified, risk-adjusted marginal outcome value rather than token volume, historical consumption, or unverified benefit claims.

## 2. Why a narrower formulation is necessary

The following are established or active areas and cannot independently support novelty:

- token and cost observability;
- per-user, project, or team spend attribution;
- model routing and quality-cost optimization;
- token-budgeted reasoning and agents;
- AI FinOps, showback, chargeback, and allocation hierarchies;
- AI ROI scorecards and portfolio selection;
- token carry-over or transferability;
- value-per-token or marginal-token language;
- LLM evaluation and production tracing.

The proposed gap is a prospective closed loop that binds consumption to a predefined outcome contract, verifies the outcome separately from the consuming system, estimates incremental rather than gross value, records attribution confidence, and uses realized portfolio evidence for constrained hierarchical reallocation.

## 3. Unit of analysis

The preferred unit is an **AI-assisted workflow episode**, not an individual token or chat message. An episode has:

- a registered task and accountable owner;
- a pre-AI comparator or counterfactual baseline;
- a trace containing all model, agent, retrieval, and tool activity;
- a predefined outcome and measurement window;
- quality, risk, and human-effort measurements;
- a verified outcome receipt;
- fully loaded cost and uncertainty fields.

This design prevents a long conversation, a successful model call, or a large token count from being treated as business value by default.

## 4. Core constructs

### 4.1 Normalized AI resource cost

For episode `e`:

```text
TotalCost(e) = ProviderCharges
             + InfrastructureCost
             + ToolAndRetrievalCost
             + EvaluationCost
             + HumanReviewCost
             + IntegrationAndReworkCost
```

Token classes remain in the ledger as explanatory quantities, but cross-provider allocation uses monetary cost or a versioned normalized AI Resource Unit derived from cost—not raw token totals.

### 4.2 Verified incremental value

```text
VerifiedIncrementalValue(e)
  = AttributionConfidence(e)
  × [MeasuredOutcomeWithAI(e) - CounterfactualBaseline(e)]
```

The value function may include monetary benefit, time, quality, risk, or service outcomes. Non-monetary components must remain separately visible unless a prespecified conversion is defensible.

### 4.3 Risk-adjusted net value

```text
RiskAdjustedNetValue(e)
  = VerifiedIncrementalValue(e)
  - TotalCost(e)
  - ExpectedHarmCost(e)
  - UncertaintyPenalty(e)
```

### 4.4 Marginal allocation

For organizational node `j`, allocate the next internal budget unit to the eligible proposal with the greatest expected marginal risk-adjusted value, subject to:

- portfolio budget;
- minimum-access or exploration floors;
- risk and compliance constraints;
- capacity and latency constraints;
- maximum concentration limits;
- outcome-evidence sufficiency;
- reserve and carry-forward rules.

## 5. Hierarchical budget model

```text
Enterprise
  └── Business unit
      └── Domain
          └── Team
              └── Project / product
                  └── Workflow / user
```

This is an internal ledger. It must distinguish:

- **committed vendor spend**, which follows contract terms;
- **available provider quota**, which may expire or be non-transferable;
- **internal notional budget**, which the organization can pool, reserve, carry forward, or reallocate;
- **realized spend**, which must reconcile to invoices and infrastructure records.

## 6. Candidate experimental design

### Policies

1. Equal fixed allocation.
2. Historical-usage proportional allocation.
3. Token-minimization allocation.
4. Cost-and-quality allocation.
5. Outcome-linked allocation without hierarchy.
6. OVAR hierarchical allocation without carry-forward.
7. OVAR hierarchical allocation with conditional reserve/carry-forward.

### Evaluation outcomes

- verified incremental value;
- risk-adjusted net value;
- successful outcome rate;
- fully loaded cost per verified outcome;
- time and quality change versus baseline;
- budget utilization and stranded balance;
- concentration and minimum-access violations;
- estimation calibration and regret;
- false scale, false stop, and POC-to-production decisions;
- gaming and metric-manipulation sensitivity.

### Recommended phases

1. Formal novelty audit and construct validation.
2. Interviews or Delphi-style review with finance, AI platform, product, risk, and domain experts.
3. Ledger schema and synthetic portfolio simulator.
4. Pilot using retrospective traces with prospectively defined outcome labels.
5. Frozen allocation rules and simulation experiments.
6. Prospective field or high-fidelity organizational study.
7. External replication.

## 7. Primary threats to validity

- value attribution without a credible counterfactual;
- monetizing time saved when time is not redeployed;
- self-reported quality or productivity;
- delayed, shared, or downstream outcomes;
- cross-model token non-comparability;
- changing prices and hidden reasoning tokens;
- selection bias in projects that provide telemetry;
- rubric subjectivity and evaluator dependence;
- strategic inflation of outcome estimates;
- starving exploration through historical ROI optimization;
- Goodhart effects once allocation follows the metric;
- privacy and workforce-surveillance risks from user-level attribution;
- constructed data that do not represent production behavior.

## 8. Prospective decision rule

Do not claim that OVAR improves ROI until a frozen evaluation demonstrates a non-dominated position on verified value, cost, risk, and access/fairness relative to prespecified baselines. Favorable consumption or quality metrics alone are insufficient.

