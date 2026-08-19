# Gate 4B Minimum Production DES Scope Decision

**Decision ID:** G4B-MPS-001  
**Version:** 1.0  
**Decision date:** 14 August 2026  
**Status:** Approved scope baseline for implementation; not a production-evaluation lock  
**Route:** B — synthetic design-science evaluation  
**Authority:** Protocol-owner instruction to proceed; engineering and audit support may be agent-assisted

## 1. Decision

The production discrete-event simulation (DES) will implement the **smallest mechanism set needed to test whether pre-commitment role-stage demand, finite role availability, evidence readiness, explicit queues, and bounded rework improve synthetic forecasts of verified completion within a planning horizon**.

The selected route is to complete the missing core mechanisms rather than narrow the paper to the current two-role prototype. Production scope therefore adds only:

1. executable role-capacity calendars and blackouts;
2. executable acyclic finish-to-start work-item dependencies;
3. a closed evidence-readiness lifecycle, including declared production, invalidation, and regeneration of evidence; and
4. a single, auditable FIFO, non-preemptive queue policy with explicit waiting and blocking time.

No other mechanism from the broader Gate 3 research agenda enters the production lock. This decision does not authorize opening production seeds or running the locked evaluation.

## 2. Central estimand and decision supported

At the commitment cutoff `t0`, the deployable models forecast, for each work item and committed portfolio:

> the probability of reaching a terminal verified-completion state by the declared planning-horizon deadline, under declared role-stage service demand, role availability, dependency, gate, and rework assumptions.

The primary comparison remains paired item-level Brier-score improvement against the strongest deployable comparator. Bottleneck identification remains a required secondary outcome. The oracle remains diagnostic and cannot support a deployment claim.

`Verified completion` means that every applicable mandatory gate has reached an allowed terminal transition with current, artifact-matched synthetic evidence. A terminal failure, unresolved mandatory gate, unfinished dependency, or item still active at the horizon is not verified completion. A conditional terminal state must be reported separately as `completed_with_residual_risk`; it must not be silently pooled with unconditional completion. The preregistration must state before lock whether the primary binary endpoint treats this state as completed or not, and sensitivity analysis must report the alternative treatment.

## 3. Included production mechanisms

### 3.1 Portfolio, stages, and role pools

- A finite portfolio is frozen at `t0`; scheduled arrivals after `t0` may be represented only when their values are fixed in the locked configuration.
- Each work item follows a declared sequential stage route, with explicit backward transitions only through a rework rule.
- The locked worlds must exercise at least four distinct service functions: product/domain or context preparation; implementation; independent review/quality assurance; and release or business acceptance.
- Architecture and security/compliance may be separate role pools or risk-applicable service stages, but their mapping must be explicit and identical across comparators that are permitted to observe it.
- Each stage has one accountable service pool in the minimum implementation. Alternate-role routing, simultaneous multi-role service, and within-item stage parallelism are excluded.
- Service and gate-assessment durations use only frozen, provenance-labelled distributions supported by the sampler and schema.

### 3.2 Capacity calendars

- Role capacity is represented by an integer number of parallel servers and explicit UTC availability windows.
- Declared blackouts close the affected role pool. Service may start only while capacity is available; work crossing a closure pauses and resumes at the next availability window without resampling its remaining demand.
- Queue waiting continues during unavailable periods and is reported separately from active service.
- Aggregate fields such as gross, absence, non-project, and effective hours are validation/reporting totals, not a second capacity multiplier. The production configuration must reconcile them to executable availability windows to prevent double counting.
- Capacity outside declared windows is zero. No overtime or implicit capacity is invented.

### 3.3 Queue policy

- Each role pool has one FIFO, non-preemptive queue.
- Queue order is determined by queue-entry event sequence, with an immutable item-ID tie-breaker for exact time ties.
- Gate assessment consumes capacity from its declared accountable role and queues under the same rule.
- Initial backlog is permitted only when represented as explicit synthetic items with arrival/state records; a numeric backlog count without service demand is prohibited.
- Waiting, active service, gate-assessment service, dependency blocking, calendar unavailability, and rework service are recorded as distinct quantities.

### 3.4 Finish-to-start dependencies

- Cross-item dependencies form a directed acyclic graph frozen at `t0`.
- The only supported dependency rule is finish-to-start: a dependent item may arrive but cannot enter its first service queue until every declared predecessor reaches the configured release state.
- The production configuration must declare whether the release state is unconditional verified completion or whether `completed_with_residual_risk` also releases successors.
- A predecessor terminal failure propagates a declared `dependency_failed` terminal state to blocked successors, or leaves them censored at the horizon according to one rule frozen before lock; silent release is prohibited.
- Missing endpoints, self-dependencies, cycles, and an execution deadlock with no future release event are hard stops.

### 3.5 Evidence readiness, gates, and rework

- Applicable gates are determined by frozen risk class, gate applicability, and policy version.
- Evidence has explicit states at minimum: `absent`, `current`, and `invalid`.
- Every required evidence type declares the stage/event that produces or refreshes it and the events that invalidate it. Evidence is never created merely because a gate is reached.
- Gate assessment consumes separately recorded service demand. A mandatory gate cannot be bypassed or averaged into a readiness score.
- Supported decisions are `Pass`, `Conditional`, `Fail`, and `NotApplicable`, only where explicitly permitted. Conditional passage records residual risk and its downstream/terminal effect.
- A declared rework transition invalidates affected evidence, returns the item to a named prior stage, and permits evidence regeneration only at its declared producer stage/event.
- Rework loops are bounded. Exhaustion reaches a declared terminal failure; it never falls through to advancement.
- Stochastic gate outcomes may operate only after mandatory evidence is current. Their probabilities are frozen truth-generator parameters and are not interpreted as empirical defect rates.

### 3.6 Forecast and evaluation isolation

- Deployable comparators receive only fields available and frozen at `t0`; realized service, queue, gate, evidence, and outcome events remain truth/scoring data.
- Identical synthetic portfolios and common random numbers are used across comparators within each replication.
- Story Points, HIE-compatible, simple role load, proposed model, and oracle contracts remain as specified in `04_comparator_evaluation_spec.md`.
- The production runner must implement the locked precision-stopping rule, uncertainty method, strongest-comparator selection, immutable output contract, and no-post-opening-tuning rule.

## 4. Explicit exclusions

The following are outside the minimum production DES and must not be added before the locked evaluation:

- dynamic or endogenous arrivals, scope churn, cancellations, or reprioritization after `t0`;
- priority, shortest-processing-time, risk/age-aware, or learned queue disciplines;
- preemption, service interruption costs beyond calendar pause/resume, or skill-based alternate-role routing;
- within-item parallel branches, AND/OR joins, probabilistic dependencies, resource deadlocks, or cross-portfolio dependency discovery;
- generalized evidence rule languages, real artifact validation, cryptographic evidence verification, or human/agent identity assurance;
- time-varying gate policies, arbitrary evidence expiry, waiver workflows beyond the frozen conditional-pass rule, or residual-risk optimization;
- context-switch/setup penalties, batching economies, multitasking degradation, fatigue, learning curves, or cognitive-load measurement;
- correlated service-demand families unless a correlation implementation and recovery test are separately approved before scope freeze;
- AI-generated batch amplification, model/tool-specific causal effects, endogenous quality, defects avoided, or downstream incident simulation;
- monetary cost, portfolio value, staffing optimization, fairness by person, or individual productivity analysis;
- empirical calibration, practitioner usability testing, or organizational generalization.

Configuration fields for excluded mechanisms must either be absent or cause a validation hard stop. They must never be accepted and silently ignored.

## 5. Claims enabled by a conforming synthetic evaluation

Subject to the locked adjudication rules, this scope can support only statements of the following form:

1. Under specified synthetic worlds, the proposed role-, readiness-, dependency-, and queue-aware mechanism had lower, equivalent, or higher completion-probability error than named comparators.
2. Under specified capacity pressure, finite non-development-role availability produced queueing and constrained verified completion inside the model.
3. Under specified readiness/rework rules, evidence state did or did not add forecast information beyond pre-task effort/load variables.
4. Under specified dependency structures, blocked work changed completion forecasts and bottleneck attribution inside the model.
5. In low-utilization, balanced-demand, low-rework worlds, a simpler comparator was equivalent or preferable.
6. Synthetic capacity reallocation to a binding role changed model outcomes under the declared counterfactual scenario.
7. Results were stable, unstable, null, or adverse across the preregistered plausible region.

Every such statement must include or clearly inherit the qualifier **“in the prespecified synthetic model under declared assumptions.”** Synthetic success authorizes only a prospective Route A study.

## 6. Claims prohibited

This scope cannot support claims that:

- Story Points have stopped working, measure coding difficulty, or are inferior in real organizations;
- the framework measures human attention, cognitive load, mental effort, or prompt quality;
- AI causes higher productivity, lower implementation effort, more review burden, or different quality;
- readiness gates, dependencies, staffing changes, or the proposed model cause real delivery improvement;
- the model is calibrated, valid, useful, fair, or generalizable for a person, team, organization, tool, or industry;
- the proposed model is universally superior, replaces Agile estimation, prescribes optimal staffing, or justifies employee evaluation;
- results generalize to excluded queue disciplines, parallel workflows, dynamic portfolios, expiry rules, context switching, or correlated demand;
- agent review constitutes practitioner review, expert content validity, human-subject evidence, or organizational validation.

## 7. Production acceptance tests

All tests below are hard stops unless explicitly labelled an analysis check. The production release must map each test ID to executable test evidence and include the mapping in the independent review record.

| ID | Required acceptance test |
|---|---|
| G4B-CFG-01 | Schema plus cross-reference validation rejects unknown IDs, unsupported mechanism declarations, invalid durations/probabilities/timestamps, duplicate IDs, contradictory gate transitions, and excluded non-default policies. |
| G4B-DET-01 | The same release, configuration, world, and seed produce byte-stable canonical result content and identical event digest. |
| G4B-CAL-01 | A hand-calculated one-server availability fixture starts no service in a closed interval, pauses across a blackout, resumes with unchanged remaining demand, and matches expected wall-clock completion. |
| G4B-CAL-02 | Increasing executable availability cannot worsen completion time in a no-rework, otherwise identical fixture; aggregate calendar totals reconcile to executable windows. |
| G4B-QUE-01 | Simultaneous deterministic arrivals are served FIFO with the declared tie-breaker; no item receives service before queue entry or while all servers are busy/unavailable. |
| G4B-QUE-02 | Queue-area, item-wait, and resource-busy integrals reconcile on a hand-calculated stable finite fixture; censored work is accounted for explicitly. |
| G4B-DEP-01 | A two-item chain releases the successor only at the declared predecessor state and records dependency-blocked time separately from role-queue time. |
| G4B-DEP-02 | Missing endpoints, self-links, cycles, and event-queue deadlock each stop before interpretable results are emitted. |
| G4B-DEP-03 | Predecessor failure follows the one frozen propagation rule and can never silently release the successor. |
| G4B-RDY-01 | Missing/invalid mandatory evidence forces the declared non-passing outcome; reaching a gate cannot manufacture evidence. |
| G4B-RDY-02 | A deterministic rework fixture invalidates named evidence, regenerates it only at its declared producer event, and prevents stale evidence from passing a later gate. |
| G4B-GAT-01 | Gate assessment consumes the accountable role's calendar-constrained capacity and its service/wait is reported separately. |
| G4B-GAT-02 | Mandatory failure, conditional-policy restrictions, NotApplicable rationale, residual-risk recording, maximum-loop exhaustion, and terminal transitions follow the frozen policy without fall-through. |
| G4B-CON-01 | Entity conservation holds: every declared item is exactly one of completed, completed-with-residual-risk, failed, dependency-failed, or horizon-censored. |
| G4B-CON-02 | For completed deterministic fixtures, elapsed wall time reconciles to dependency blocking, queue/calendar waiting, active service, gate service, and rework without double counting. |
| G4B-ISO-01 | Comparator field-access tests prove that deployable models cannot read runtime truth or post-`t0` state; the oracle cannot be selected as deployable reference. |
| G4B-OUT-01 | Every locked output table and required field exists, row keys reconcile across tables, files are immutable/checksummed, and the run is regenerable from its manifest. |
| G4B-PRE-01 | Unified tests pass, code/config/schema/review/runner/readiness artifacts match their hashes, fresh sealed production seeds meet capacity, and `simulation.prelock` returns only `ready_to_open`. |
| G4B-PREC-01 | A development-seed fixture verifies fixed-batch precision stopping, maximum-replication behavior, paired uncertainty, and `precision_unresolved` without opening production values. |
| G4B-ABL-01 | Prespecified development-seed ablations remove queues, readiness, dependencies, and multi-role structure one at a time; each ablation changes only its declared mechanism. This is an analysis check but missing output is a hard stop. |

Existing fixed-seed, zero-arrival, infinite-capacity, no-rework, mandatory-fail, range, probability, configuration, seed-separation, comparator-isolation, and metric tests remain mandatory; the IDs above add to rather than replace them.

## 8. Scope-creep and overlap audit

| Mechanism or artifact | Existing status | Gate 4B treatment | Rationale |
|---|---|---|---|
| Fixed finite portfolio and sequential stages | Executable prototype | Retain and harden | Sufficient baseline for the estimand; dynamic arrivals are unnecessary. |
| Role pools and FIFO queues | Executable prototype | Retain one policy only | Central to role-constrained capacity; queue-policy comparison would expand the question. |
| Gate assessment demand and bounded rework | Executable prototype | Retain and close semantics | Necessary for verified completion and already substantially tested. |
| Evidence presence/freshness/invalidation | Limited executable prototype | Add declared production/regeneration lifecycle | Without regeneration, readiness/rework worlds can create structurally permanent failures and cannot test the intended mechanism cleanly. |
| Capacity calendars and blackouts | Validated configuration, not executed | Implement explicit availability/pause/resume | Finite role availability is part of the central causal mechanism; server count alone is inadequate. |
| Dependency models | Validated configuration, not executed | Implement acyclic finish-to-start only | Coordination/dependency blocking is a named pre-commitment mechanism; richer graphs are unnecessary. |
| Multiple lifecycle roles | Schema supports them; example uses two | Require at least four service functions in locked worlds | A two-role implementation/review toy cannot carry a cross-functional verified-delivery claim. |
| Priority/risk-aware queues | Mentioned in Gate 3 protocol, not executable | Exclude | Not required for the primary comparison and creates a policy-optimization study. |
| Context-switch/setup penalty | Conceptual/schema placeholder | Exclude | Parameterization is weak and it risks reintroducing an unvalidated cognitive proxy. |
| Parallel work and complex dependencies | Conceptual only | Exclude | High implementation/audit cost with no necessity for the primary claim. |
| General evidence expiry and waiver rules | Conceptual only | Exclude | Same-run freshness plus explicit invalidation is sufficient for the minimum readiness test. |
| AI moderation and batch amplification | Conceptual/scenario labels | Hold as exogenous frozen service parameters only | The paper cannot estimate a causal AI effect under Route B. |
| Comparator, precision, seed, prelock, and output contracts | Prototype/draft artifacts exist | Complete without changing the estimand | These are evaluation controls, not new delivery mechanisms. |
| Route A organizational validation | Future-work protocol | Remain deferred | Agents and synthetic data cannot establish construct, predictive, or organizational validity. |

This audit found no need to add priority scheduling, context switching, parallelism, cost optimization, fairness analysis, or endogenous AI behavior. Any such addition is scope creep for this production evaluation.

## 9. Implementation sequence and exit criteria

Implementation must proceed in this order:

1. align schema and configuration semantics with this decision, including hard rejection of excluded declarations;
2. implement and unit-test calendars;
3. implement and unit-test finish-to-start dependencies and failure propagation;
4. complete the evidence production/invalidation/regeneration lifecycle;
5. integrate the mechanisms and pass all conservation, isolation, output, and deterministic tests;
6. complete the production runner, precision stopping, uncertainty outputs, and immutable output contract;
7. run development-seed sensitivity, ablation, and adversarial checks only;
8. archive a clean code release and obtain an independent agent software/protocol review;
9. freeze configuration, schema, comparator formulas, endpoints, analysis, runner, outputs, and hashes;
10. create a fresh independently sealed production seed set, externally timestamp the preregistration, and run the pre-lock checker.

Gate 4B implementation exits only when every required test has executable evidence, no included configuration field is ignored at runtime, no excluded mechanism is active, the independent review has no unresolved hard stop, and `simulation.prelock` reports `ready_to_open`. Until then, all runs remain developmental.

## 10. Change control

### Before production lock

Every proposed change must have a decision-log entry stating the defect or research necessity, affected requirement/test IDs, claim impact, files/hashes changed, and whether prior development results must be regenerated. A change is accepted only if it is required to implement an included mechanism, satisfy an acceptance test, or remove ambiguity. New research questions and convenience features are rejected or deferred to a later protocol.

### After production lock

Any change to executable behavior, schema/configuration, parameter value or provenance, world, comparator formula, endpoint, conditional-completion treatment, uncertainty method, threshold, precision rule, runner, seed policy, or output contract creates a new protocol version and hashes. If any production evaluation value has been opened, the affected run is exploratory; it must be retained with its audit record, and a fresh independently sealed seed set is required for another confirmatory run.

Defect corrections never overwrite or selectively repair opened results. Documentation-only corrections may retain the lock only when an independent review confirms that no executable meaning, interpretation, or claim boundary changed and records that determination with a new document checksum.

## 11. Traceability and supersession

This decision specializes, but does not replace, `03_route_b_simulation_protocol.md`, `03_framework_specification.md`, `04_comparator_evaluation_spec.md`, and `04_locked_synthetic_preregistration.md`. Where those documents list a broader simulation mechanism, this Gate 4B decision governs what is executable in the minimum production evaluation. The preregistration, machine-readable protocol, schema, example/production configurations, runner-readiness record, and review checklist must be updated to cite `G4B-MPS-001` before lock.

The scope must be reopened rather than silently stretched if implementation shows that any included mechanism cannot be represented without adding an excluded mechanism. Reopening requires a new Gate 4B version and protocol-owner approval.
