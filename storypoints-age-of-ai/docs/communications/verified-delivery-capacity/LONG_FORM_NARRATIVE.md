# When Code Is No Longer the Only Constraint: Planning Verified Delivery in the AI Era

AI-assisted programming has changed the economics of producing code. It has not removed the work required to turn that code into an accepted, secure, operable change.

A feature still has to be understood. Architectural boundaries still have to be respected. Generated changes still have to be reviewed, tested, integrated, secured, released, and accepted. When implementation accelerates faster than these downstream capabilities, the bottleneck moves. It does not disappear.

That is why a team can generate substantially more code without seeing a proportional increase in sprint completion. More artifacts may arrive at the same scarce reviewers, architects, security specialists, test environments, product owners, and acceptance gates. The delivery system becomes queue-bound even while coding looks faster.

## The representational gap

Story Points remain a useful team-relative planning convention in many environments. The issue is not that they were simply “hours to write code,” nor that they have universally stopped working. The narrower limitation is that a single value does not explicitly show:

- which role must act;
- at which lifecycle stage that role is needed;
- how much active human service is forecast;
- how long the item may wait for scarce capacity;
- which dependencies can block progress;
- which evidence is required before the item can advance; or
- whether faster implementation increases downstream arrival pressure.

The Verified Delivery Capacity Model (VDCM) is a proposed way to make those conditions inspectable before commitment.

## Forecast the work at the point of commitment

The model begins with a strict information boundary: `t0`, the planning or commitment cutoff. Only information available at that point may be used in the prospective forecast. Actual prompt counts, later code churn, review comments, test failures, and realized correction loops are useful for retrospective explanation, but including them in the original forecast would create outcome leakage.

At `t0`, a work item is described through five separate demand drivers:

1. intent uncertainty;
2. change-propagation exposure;
3. context-provisioning deficit;
4. assurance obligation; and
5. coordination topology.

These drivers inform a distribution of active human service demand by role and lifecycle stage. The unit is time—not a synthetic “attention score.” The model then combines that demand with schedulable role capacity, existing queues, calendars, dependencies, evidence readiness, and bounded rework.

## Separate service from delay

An item can require little active effort and still take a long time because it waits for a specialist, a decision, an environment, or prerequisite evidence. VDCM therefore keeps four quantities distinct:

- active human touch time;
- constrained-role queue delay;
- dependency-block time; and
- calendar pause or other elapsed non-service time.

That distinction changes the management conversation. Instead of asking only whether a sprint contains too many points, leaders can ask whether the planned portfolio overloads a particular role-stage function or arrives at a gate without checkable evidence.

## Delivery is verified, not merely finished

The target is not code completion. It is evidence-ready completion against a declared risk tier and deadline. Each gate applies explicit transition semantics:

- **Pass:** the required evidence is ready and the item advances;
- **Conditional:** the item advances with an explicit residual-risk record;
- **Fail:** the item enters declared rework or stops;
- **Not Applicable:** the requirement does not apply and the rationale is recorded.

The output is a distribution of verified completion, expected items per horizon, likely bottlenecks, service and delay components, and assumptions. It is not another universal scalar.

## What the research found—and did not find

The access-constrained evidence map reconciled 791 included study families and 2,343 exact-locator findings, including 769 quantitative findings. No family met all five predeclared overlap dimensions for the same pre-commitment planning use. The bounded conclusion is that no substantively duplicative framework was identified within the predeclared open sources and citation network through the stated cutoff and approved resource cap. This is not a claim that every relevant publication was searched.

The developmental simulation also produced an important negative result: no deployable comparator was uniformly best. Across 11 declared synthetic scenarios, the proposed and HIE-compatible models each had the lowest descriptive Brier score in four, simple role load in two, and Story Points in one. These are synthetic mechanism results using illustrative inputs, not evidence of organizational superiority.

That is the point of a falsifiable framework. Added detail should earn its place. If a simple role-load ratio or current team practice predicts adequately, readiness does not distinguish transitions, inputs cannot be rated reliably, or measurement overhead outweighs decision value, the richer model should be simplified or rejected.

## A pragmatic adoption path

Organizations should begin in shadow mode. Keep current planning practice, add VDCM forecasts at the same `t0` cutoff, and compare calibration, bottleneck information, decision value, and overhead. Start with one workflow where specialist capacity or evidence obligations plausibly constrain delivery. Keep all reporting at work-item and role-pool level.

Only genuine prospective organizational data can establish whether the model is usable, calibratable, transportable, and worth its cost. Until then, VDCM is best understood as a transparent planning representation and validation agenda—not a cognitive metric, a productivity score, or a universal replacement for Story Points.

![Verified Delivery Capacity end-to-end workflow](assets/06-end-to-end-verified-delivery-workflow.png)

## Research boundary

The workflow graphic is conceptual. Evidence coverage is limited to declared open scholarly sources, lawful open full text, and the approved citation-chasing cap. The simulation is developmental and synthetic. Human and organizational validation remains future Route A work.
