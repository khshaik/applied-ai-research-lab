# Gate 3 Route B Simulation Protocol

**Version:** 0.1 for audit  
**Purpose:** Evaluate the internal behavior and decision consequences of a role-constrained verified-delivery-capacity model without claiming human or organizational validation.

## 1. Study design

Use a transparent discrete-event simulation (DES) of work items moving through lifecycle stages and requesting service from constrained role pools. Queueing approximations may be used as reasonableness checks, but the main model should not assume exponential arrivals/service or independent stages when those assumptions are implausible.

The simulation is a design-science evaluation of model coherence, sensitivity, and comparative decision behavior. It is not a substitute for a prospective field study.

## 2. Entities, resources, and stages

### Entities

Work items with:

- pre-commitment demand-driver profile IU/CPE/CPD/AO/CT;
- Story Point baseline;
- HIE-compatible pre-task fields where definable without outcome leakage;
- risk class and required gate evidence;
- AI mode/maturity by stage;
- due interval/priority;
- dependency links.

### Resource pools

- product/domain;
- architecture;
- development;
- peer review;
- security/privacy/compliance;
- QA/test;
- operations/release;
- UAT/business acceptance.

Resource pools can be combined in scenarios, but the mapping and effective capacity must remain explicit.

### Stages

1. Intent and acceptance definition
2. Architecture/risk resolution
3. Context preparation and generation planning
4. Implementation/refinement
5. Independent review and verification
6. Integration/system/quality evaluation
7. Release/operational validation
8. UAT/acceptance

## 3. State transitions

Each item moves through `Not Ready → Waiting → In Service → Evidence Check` for each applicable stage.

Gate evaluation consumes capacity from the accountable role. An evidence check results in:

- `Pass`: advance;
- `Conditional`: advance only if policy permits, while carrying a residual-risk record that can alter downstream failure/rework probability;
- `Fail`: return to the specified prior stage;
- `Not Applicable`: bypass with recorded rationale.

Rework transitions must be explicit. Items cannot silently acquire complete evidence or skip mandatory gates.

## 4. Stochastic inputs

For every distribution, record source class and uncertainty:

1. **Empirical:** estimated from genuine observations;
2. **Literature-informed:** bounded by relevant studies but not organization-calibrated;
3. **Expert-elicited:** unavailable in Route B unless genuine experts participate;
4. **Illustrative:** selected only to explore model behavior.

Current Route B runs will primarily be literature-informed or illustrative. Results must be labelled accordingly.

Inputs include arrival process, role capacity calendars, service-time distributions, correlations, gate applicability, initial readiness, transition probabilities, priority rules, interruption/context-switch penalties, and AI moderation effects.

## 5. Experimental factors

Use a factorial or space-filling scenario design across at least:

- implementation automation: low/medium/high;
- verification exposure: low/medium/high;
- context sufficiency: weak/moderate/strong;
- evidence maturity: weak/moderate/strong;
- specialist capacity pressure: low/medium/high;
- dependency/coordination load: low/medium/high;
- batch size: small/medium/large;
- risk class: routine/elevated/critical;
- service discipline: FIFO versus risk/age-aware;
- readiness enforcement: absent/advisory/mandatory.

Do not imply that these categories are validated 0–4 anchors.

## 6. Comparators

Compare decision performance under identical simulated portfolios:

1. **Story Points-only:** capacity allocated using historical point throughput assumptions;
2. **Task-effort/HIE-compatible:** task service demand incorporates context/interaction/oversight variables but has no explicit cross-role queues;
3. **Simple role-load ratio:** demand by role divided by capacity, without readiness or DES;
4. **VDCM:** role-stage demand, queues, evidence states, and rework transitions;
5. **Oracle bound:** uses simulated true parameters; diagnostic only, not a deployable method.

The oracle prevents overclaiming and helps quantify avoidable error. Comparators must also be tested in deliberately different data-generating worlds: Story-Point-sufficient, HIE/task-oversight, cross-role bottleneck, readiness/rework, mixed, and misspecified. A model must not be declared superior only in a world constructed from its own assumptions.

## 7. Outcomes

Primary simulation outcome:

> Error and calibration of predicted probability that a work item or committed portfolio completes within the planning interval.

Secondary outcomes:

- error in cycle-time quantiles;
- error in role-specific queue-delay quantiles;
- constrained-role identification accuracy;
- predicted versus realized touch-time distribution;
- rework-loop and gate-failure prediction;
- synthetic quality outcome prediction where transition rules are declared;
- overcommitment and undercommitment rates;
- estimation/measurement overhead proxy;
- fairness/risk by work class, never by individual.

## 8. Simulation procedure

1. publish model code, configuration, random seeds, and environment;
2. generate scenario portfolios before examining comparator results;
3. split scenarios/seeds into development and locked evaluation sets;
4. run sufficient replications to stabilize confidence intervals for primary outcomes;
5. use common random numbers across comparators where appropriate;
6. report Monte Carlo uncertainty;
7. retain null and adverse results;
8. run stress tests outside the nominal parameter region;
9. archive every configuration and checksum;
10. never tune on the locked evaluation set.

## 9. Sensitivity and robustness

Required analyses:

- global sensitivity analysis for high-leverage inputs;
- one-way threshold analyses around utilization pressure;
- alternative service-time shapes and correlations;
- alternative queue disciplines and priority policies;
- rework-probability perturbation;
- missing/misclassified readiness evidence;
- optimistic versus pessimistic AI moderation;
- no-context-switch-penalty versus plausible penalties;
- ablation of readiness, queues, multi-role structure, and each predictor family;
- comparison with the simpler role-load ratio.

If small plausible changes reverse the central conclusion, report the framework as unstable.

## 10. Verification and validation of the simulation

### Verification: did we build the model right?

- deterministic toy cases with hand-calculated results;
- conservation checks for entities and time;
- zero-arrival, infinite-capacity, single-role, no-rework, and mandatory-fail tests;
- event-trace inspection;
- independent code review;
- regression tests for fixed seeds.

### Validation: is the model adequate for the intended real system?

Route B can assess face plausibility against literature and internal consistency only. Empirical calibration, predictive validity, practitioner usability, and organizational transfer require Route A.

## 11. Route B propositions

These propositions concern model behavior under explicit assumptions:

- **SP1:** When a constrained non-development role approaches saturation, queue-aware forecasts have lower completion-probability error than Story Points-only forecasts in the simulated system.
- **SP2:** Increasing implementation automation does not monotonically reduce simulated cycle time when verification demand or specialist utilization increases.
- **SP3:** Readiness information improves forecast accuracy only when gate state predicts rework/transition behavior; otherwise its incremental contribution is null.
- **SP4:** Multi-role demand improves bottleneck identification relative to task-only effort when demand is materially imbalanced across roles.
- **SP5:** Under low utilization, low rework, and balanced role demand, a simple model performs similarly to VDCM; complexity is then not justified.
- **SP6:** VDCM should be rejected for decision use if its advantage disappears under plausible parameter uncertainty or its measurement-overhead proxy exceeds the simulated planning benefit.
- **SP7:** Reallocating capacity to the binding review/QA/security role can outperform further implementation acceleration under bottleneck scenarios.
- **SP8:** A Story Point scalar remains competitive when role demands are stable, correlated, and already reflected in team history.

## 12. Prohibited interpretation

Do not write that the simulation proves Story Points fail, measures human attention, validates VDCM, predicts a real team, or demonstrates causal effects of AI. State that it tests the internal consequences of a proposed mechanism and identifies conditions worth evaluating prospectively.
