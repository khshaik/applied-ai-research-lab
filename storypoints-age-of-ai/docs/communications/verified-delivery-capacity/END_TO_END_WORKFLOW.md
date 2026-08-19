# End-to-End Workflow: From AI-Assisted Work Item to Verified Delivery

![Verified Delivery Capacity end-to-end workflow](assets/06-end-to-end-verified-delivery-workflow.png)

## Why the workflow changes

AI assistance can reduce some implementation work without proportionally reducing the work needed to understand, integrate, review, secure, test, release, and accept a change. The planning question is therefore not simply “How hard is this item?” It is:

> Can the required roles produce and verify the evidence needed for this item by the commitment deadline?

VDCM represents that question as a role-stage resource and flow problem. It keeps active human service separate from waiting, dependency blocking, and calendar pauses. It also makes evidence readiness an explicit transition condition.

## Phase I — Frame and forecast

1. **Frame the item.** Define the intended outcome, acceptance conditions, risk tier, affected interfaces, data, policies, and operational boundaries.
2. **Freeze the `t0` inputs.** Archive the information available at commitment time. Realized prompt iterations, code churn, review comments, test failures, and later evidence cannot enter a prospective forecast.
3. **Profile pre-commitment demand drivers.** Rate intent uncertainty, change-propagation exposure, context-provisioning deficit, assurance obligation, and coordination topology using separate behavioral anchors and supporting evidence.
4. **Map role-stage human touch demand.** Forecast P50/P80 active service hours for each required role and lifecycle stage. This is a resource forecast—not a psychological measure of attention.

## Phase II — Flow and verify

5. **Load effective role capacity.** Represent schedulable hours after declared allocations, calendars, and blackouts, together with work already queued for each role pool.
6. **Simulate delivery flow.** Route items through dependencies, FIFO role queues, service, calendar pauses, gates, and bounded rework. Touch time, queue delay, dependency block time, and elapsed cycle time remain separate.
7. **Evaluate evidence readiness.** At each named gate, determine whether the risk-tier evidence is present, current, traceable, and independently checkable. Existence does not imply correctness.
8. **Decide at the gate.** Apply explicit `Pass`, `Conditional`, `Fail`, or `Not Applicable` semantics. Conditional progress retains a residual-risk record; failure routes to declared rework or a terminal stop; `N/A` requires a rationale.

## Phase III — Commit and learn

9. **Forecast verified delivery.** Report a distribution: completion probability by deadline, expected verified items per horizon, constrained role-stage, active service, waiting, blocking, rework, and assumptions. Do not collapse these into one universal score.
10. **Observe and recalibrate.** Compare forecasts with completed outcomes in a later validation wave. Preserve the original `t0` snapshot so observed execution data explains error without leaking into the forecast being evaluated.

## How organizations can start

Use the model in shadow mode beside current planning practice:

1. define evidence obligations and role pools for one risk tier;
2. select a narrow workflow with a known specialist constraint;
3. record current Story Points and a simple role-load baseline at the same `t0` cutoff;
4. forecast role-stage demand, readiness, and verified completion without changing commitments;
5. compare calibration, bottleneck information, decision value, and elicitation overhead;
6. expand only if the added structure is useful and reliably rated.

## Guardrails

- Do not use role demand for individual ranking, compensation, or surveillance.
- Do not interpret active service time as cognitive load.
- Do not infer causality or organizational return from developmental simulation.
- Retain Story Points or simpler role-load models where they perform adequately.
- Keep security, release, compliance, and acceptance decisions under accountable human authority.

The graphic is an explanatory artifact. The evidence map and developmental simulation provide the research context; they do not validate this workflow as an organizational standard.
