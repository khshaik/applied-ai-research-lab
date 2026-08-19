# Gate 3 Construct and Variable Dictionary

**Status:** Provisional Route B dictionary; definitions precede instrument anchors  
**Rule:** Do not use `attention`, `cognitive load`, `effort`, `touch time`, and `capacity` as interchangeable terms.

## 1. Core distinctions

| Term | Operational meaning in this study | Unit/type | Explicitly not |
|---|---|---|---|
| Active human service requirement | Human work time needed to complete a defined role-stage activity | Hours or bounded distribution | Elapsed time or cognitive-load score |
| Human touch time | Observed active time spent by accountable humans in Route A | Minutes/hours | Queue or blocked time |
| Queue delay | Time waiting for a required role/resource after the work is ready | Elapsed time | Active work |
| Blocked time | Time progression is impossible because a prerequisite/evidence/dependency is unresolved | Elapsed time + reason | All queue time |
| Subjective workload | A participant's reported task demand using a defined instrument | Instrument score | Objective attention capacity |
| Cognitive load | Theory/instrument-specific cognitive demand | Instrument-dependent | Generic synonym for effort |
| Effective capacity | Available service time of a role pool for the planning interval | Role-hours/interval | Nominal headcount |
| Utilization pressure | Offered role demand divided by effective capacity | Ratio | Individual performance metric |
| Readiness | Evidence-backed ability to advance through a defined transition | Categorical state | General confidence or completion percentage |
| Quality risk | Probability/severity of an adverse outcome under an explicit model | Probability × severity or categories | Observed defect count unless real data exists |

## 2. Pre-commitment demand drivers

These are formative inputs, not items expected to correlate as a reflective psychological scale. Cronbach's alpha is therefore not an appropriate validation criterion.

| Code | Driver | Definition | Candidate observable indicators available at t0 | Principal overlap/control |
|---|---|---|---|---|
| IU | Intent Uncertainty | Unresolved interpretation/agreement about problem, scope, rules, constraints, and acceptance evidence | unresolved decisions; stakeholder groups; acceptance examples; domain novelty; scope-volatility class | Distinguish from context deficit: IU concerns the problem/decision itself |
| CPE | Change Propagation Exposure | Breadth and criticality of affected boundaries, interfaces, data/contracts, dependencies, and non-functional concerns | components/services; interface/data changes; privilege change; risk class; rollback complexity | Separates technical exposure from service time and assurance policy |
| CPD | Context Provisioning Deficit | Trustworthy information needed by humans/AI that is unavailable, stale, inaccessible, unapproved, or hard to retrieve | repository guidance; decisions; examples; contracts; prohibited actions; freshness; retrieval gaps | HIE context completeness is the foundation; this is an ex-ante deficit and lifecycle extension |
| AO | Assurance Obligation | Evidence that policy/risk tier requires before release and acceptance | review independence; test levels; regression; security/compliance scans; performance/accessibility; QA/UAT class | Requirement/input, not actual test time, evidence state, or quality outcome |
| CT | Coordination Topology | External roles, teams, decisions, dependencies, handoffs, and synchronization constraints required for the work | role pools; external teams; approval/decision count; dependency graph; handoffs; time zones | Structural predictor, not observed context switching or queue delay |

## 3. Moderators and controls

| Variable | Definition | Measurement | Role in model |
|---|---|---|---|
| AI assistance mode | Completion, conversational, agentic, or mixed mode by stage | Categorical by stage | Moderator; never a universal treatment |
| Stage Automation Enablement | Stage-specific, observable AI/tool/evidence capability: none, ad hoc, repeatable, or controlled | Evidence-backed profile by stage | Moderator; not productivity and not mechanically subtracted from demand |
| Domain/tool experience | Relevant experience of the role pool, not personal performance | Aggregated/role-level band | Control/moderator; privacy-sensitive |
| Change batch size | Planned technical breadth at commitment | Files/components/interfaces or behaviorally anchored band | Exposure/control |
| Risk class | Organization-defined impact/criticality category | Ordered category with policy source | Determines evidence requirements and priority |
| Arrival pattern | Timing and volume of items requesting role service | Scenario distribution | Queue input |
| Role concurrency | Number of items a role pool can service without assumed loss | Integer/scenario | Queue resource rule |
| Service discipline | FIFO, priority, class-based, appointment, or other rule | Scenario policy | Queue behavior |

## 4. Derived variables and outcomes

| Variable | Formula/definition | Route B status | Route A observation source |
|---|---|---|---|
| Role–Stage Human Touch Demand `D(w,r,s)` | Pre-commitment P50/P80 distribution of active human service requirement | Scenario input/predicted distribution | Work sampling/workflow events plus validated sampling |
| Offered load `L(r,t)` | Sum of expected demand arriving for role `r` in interval `t` | Derived | Portfolio + observed demand |
| Effective capacity `C(r,t)` | Available role-hours net of declared obligations | Scenario input | Team capacity records |
| Utilization pressure `U(r,t)` | `L(r,t)/C(r,t)` | Derived | Derived from observed inputs |
| Queue delay `Wq(w,r,s)` | Ready-for-service timestamp to service-start timestamp | Simulated outcome | Workflow timestamps |
| Touch time | Sum of active role service intervals | Simulated outcome | Time sampling/tool telemetry with privacy controls |
| Rework count | Number of backward stage transitions | Simulated outcome | Workflow/test/review/UAT history |
| Cycle time | Commitment/start milestone to accepted/released milestone | Simulated outcome | Delivery-system timestamps |
| Verified Delivery Capacity | Expected verified items/horizon and probability each item reaches defined acceptance/release evidence by deadline | Monte Carlo result | Binary/time-to-event outcome with calibrated model |
| Quality outcome | Defect/rejection/incident state under explicit transition rules | Synthetic outcome only | Defects, UAT rejection, rollback, incident, severity |

## 5. Readiness evidence schema

Every gate record contains:

- work-item and gate identifier;
- applicable risk class;
- required evidence identifiers;
- current state: `Pass`, `Conditional`, `Fail`, or `Not Applicable`;
- missing/expired evidence;
- accountable owner role;
- decision timestamp and rationale;
- next permitted transition;
- simulated or observed provenance.

The framework must not compute an overall readiness percentage that hides a failed mandatory gate.

## 6. Aggregation rules

1. Do not sum IU/CPE/CPD/AO/CT into a Fibonacci-like scalar.
2. Keep role-stage demand as a vector or matrix.
3. Aggregate time only after roles/stages and uncertainty distributions remain inspectable.
4. A mandatory failed gate cannot be averaged away.
5. Learn weights only from genuine outcome data; Route B scenario weights are assumptions.
6. Report sensitivity to every high-leverage assumption.
7. Keep Story Points and HIE-compatible fields as separate comparison variables.

## 7. Instrument work still required

- behaviorally anchored 0–4 rubrics for each formative demand driver;
- content-validity assessment by qualified practitioners in Route A;
- inter-rater agreement and usability/overhead study;
- indicator redundancy/VIF checks and incremental-validity tests against HIE-compatible variables;
- mapping from ordinal anchors to time distributions, learned only from data;
- privacy, gaming, and individual-measurement safeguards.
