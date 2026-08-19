# Gate 3 Framework Specification

**Version:** 0.1 for agent audit and protocol-owner review  
**Date:** 13 August 2026  
**Route:** B — systematic evidence map, design-science artifact, and literature-informed/illustrative simulation  
**Validation status:** Proposed; not empirically validated

## 1. Gate 3 purpose

Gate 3 translates the Gate 2 novelty boundary into an explicit, falsifiable artifact. It does not claim to invent AI-era effort estimation, human approval gates, or lifecycle orchestration. It proposes a prospective extension that makes constrained role capacity and queueing visible before commitment.

The provisional framework name is **Verified Delivery Capacity Model (VDCM)**. Its pre-commitment elicitation artifact is the **Role–Stage Demand and Readiness Instrument (RSDRI)**. HADR is retained only as project history; “human attention” is not treated as a psychological quantity.

## 2. Unit, timing, and intended decision

- **Primary unit:** a work item moving through lifecycle stages, nested within a team/program and planning interval.
- **Prediction time:** before sprint/program commitment, using only information available then.
- **Decision supported:** whether the planned portfolio can pass required evidence gates within available cross-functional capacity and an acceptable quality-risk envelope.
- **Primary users:** delivery teams, product/program leads, architects, security, QA, operations, and UAT owners.
- **Not intended for:** individual ranking, surveillance, compensation, or automatic commitment decisions.

## 3. Framework architecture

VDCM contains four input layers, a delivery-system mechanism, and auditable outputs.

```text
Work-item predictor domains + stage-specific AI profile + risk/evidence requirements
                              │
                              ▼
             Pre-commitment role-stage service demand
                              │
               ┌──────────────┴──────────────┐
               ▼                             ▼
      Role capacity/availability      Gate evidence readiness
               │                             │
               └──────── queues, handoffs ───┘
                              │
                    rework/feedback loops
                              │
                              ▼
       touch time • queue delay • cycle time • completion • quality risk
```

### 3.1 Pre-commitment demand drivers

The Gate 1 I/C/A/V/Q/X dimensions mixed drivers, activities, and outcomes. They are replaced by five **formative pre-commitment demand drivers (PDD)**:

- **Intent Uncertainty:** unresolved business rules, scope, stakeholder decisions, acceptance examples, and domain interpretation.
- **Change Propagation Exposure:** affected boundaries, interfaces, data/contracts, dependencies, non-functional concerns, and risk-bearing technical change.
- **Context Provisioning Deficit:** trustworthy information required by humans or AI that is missing, stale, inaccessible, unapproved, or difficult to retrieve.
- **Assurance Obligation:** test, review, security, compliance, release, operational, and UAT evidence required by the applicable risk tier.
- **Coordination Topology:** external roles, teams, decisions, dependencies, handoffs, and synchronization constraints required for the work.

These are causes/inputs expected to shape role-stage demand, not reflective psychological constructs. They are not summed into a universal score. Raw counts and evidence should be retained where possible; provisional 0–4 anchors may support elicitation but cannot be mapped to hours without genuine calibration data.

### 3.2 Stage-specific automation profile

**Stage Automation Enablement (SAE)** records AI mode, context/instruction maturity, tool/domain experience, executable evidence, traceability, policy controls, and automated-test maturity by lifecycle stage. Automation is not assumed to reduce every service demand and is not a productivity score.

### 3.3 Risk-scaled evidence requirements

The six Gate 1 labels are retained as state-transition checks:

1. Intent Ready
2. Architecture Ready
3. Generation Ready
4. Verification Ready
5. Release Ready
6. Acceptance Ready

Each gate uses `Pass`, `Conditional`, `Fail`, or `Not Applicable`, plus evidence identifiers and an owning role. A gate state is an observed/configured property of the artifact and evidence, not a subjective workload rating.

### 3.4 Role-stage service-demand profile

For work item `w`, role pool `r`, and stage `s`, define **Role–Stage Human Touch Demand (RHTD)**:

`D(w,r,s) = ex-ante distribution of active human service requirement known at the commitment cutoff t0`.

Preferred unit is a bounded time distribution or range in hours. If reliable hours cannot be estimated, use behaviorally anchored ordinal bands and keep them separate; do not translate them to hours without calibration data.

Role pools may include product/domain, architecture, development, peer review, security/privacy/compliance, QA/test, operations/release, and business acceptance. Organizations may combine pools, but the mapping must be recorded.

### 3.5 Capacity and queue mechanism

For role pool `r` and planning interval `t`:

- `C(r,t)` is effective available service capacity after planned absence and non-project obligations;
- `L(r,t)` is offered load from the work-item portfolio;
- `U(r,t) = L(r,t) / C(r,t)` is forecast utilization pressure;
- `Wq(w,r,s)` is waiting time before role `r` supplies service at stage `s`.

Queue delay is expected to increase nonlinearly as utilization approaches capacity. This is a mechanism to test in simulation, not an empirical claim about a particular organization.

### 3.6 Rework and feedback loops

Failed/conditional evidence checks can send a work item to an earlier stage. Rework probability is conditioned on pre-task risk/context variables and the simulated evidence state. It must not be calibrated from unsupported assumptions and then presented as observed fact.

## 4. Outputs

VDCM produces a profile rather than one replacement point score. Its principal output, **Verified Delivery Capacity (VDC)**, is the distribution of items per horizon—and per-item probability—that satisfy defined release/acceptance evidence by the deadline under declared role capacities and routing assumptions.

1. active human touch-time distribution by role and stage;
2. queue-delay distribution by constrained role;
3. total gate-to-gate and end-to-end cycle-time distribution;
4. probability of completion within the planning interval;
5. probability and expected number of rework loops;
6. evidence-readiness status and unresolved evidence obligations;
7. quality-risk outcomes where a defensible transition model exists;
8. sensitivity ranking showing which assumptions drive the forecast.

## 5. Causal claims permitted under Route B

Route B may show that specified mechanisms produce particular outcomes **inside the model** under declared assumptions. It may compare model behavior and decision usefulness across synthetic scenarios.

Route B cannot establish that:

- VDCM/RSDRI measures actual human cognitive load;
- an AI tool causes productivity or quality improvement;
- a readiness gate reduces real defects;
- a simulated forecast is calibrated to an organization;
- VDCM predicts better than Story Points in practice.

Those require Route A data and appropriate empirical design.

## 6. Relationship to predecessors

| Prior work | VDCM relationship |
|---|---|
| Story Points | Retained as an organizational baseline; not portrayed as coding-time measurement |
| HIE | Theoretical/task-level foundation for context, interaction, transformation, and oversight demand |
| ACEM | Cost/HITL predecessor; VDCM focuses on constrained role capacity, queues, readiness, and delivery outcomes |
| SPACE and DevEx | Multi-dimensional productivity and developer-experience comparators; VDCM is a planning/flow artifact, not a productivity or wellbeing score |
| NASA-TLX and cognitive-load research | Possible future outcome/validation instruments; not used as pre-task capacity units |
| Agile V | Gate-workflow predecessor; VDCM couples risk-scaled evidence states to capacity and flow forecasting |
| DORA | Outcome and organizational-capability comparator; VDCM does not replace DORA performance measures |

## 7. Framework boundaries

Included:

- professional AI-assisted software delivery from intent through acceptance/release;
- cross-functional roles and constrained specialist pools;
- AI completion, chat, agentic, and mixed assistance;
- active service, waiting, blocking, handoff, rework, and evidence states.

Excluded from the initial Route B artifact:

- individual cognitive diagnosis;
- employee productivity rankings;
- monetary cost optimization;
- portfolio financial value;
- autonomous approval of security, compliance, release, or UAT;
- claims about all organizations, tools, or software domains.

## 8. Gate 3 falsification conditions

Revise or reject the framework if any of the following occurs:

1. predictor domains cannot be operationally separated from HIE or from each other;
2. role-stage demand adds no useful information beyond a task-level HIE-compatible baseline;
3. readiness state provides no incremental forecast information after risk and demand are represented;
4. queue-aware forecasts do not outperform simple capacity ratios under realistic scenarios;
5. model conclusions reverse under small plausible parameter changes;
6. measurement overhead is comparable to or greater than the delivery benefit it could support;
7. a simpler transparent model performs equivalently.

## 9. Gate 3 status

This specification is ready for independent construct, causal, and proposition audits. It is not frozen and must not be described as validated.
