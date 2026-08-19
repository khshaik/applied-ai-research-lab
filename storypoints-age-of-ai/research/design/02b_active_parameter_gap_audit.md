# Gate 2 Active Parameter Provenance Gap Audit

**Date:** 14 August 2026  
**Configuration audited:** `simulation/configs/example.yaml`  
**Machine registry:** `simulation/configs/parameter_registry.json`  
**Result:** 102 active parameter paths are uniquely registered for illustrative development use; production calibration is a hard stop.

## Decision boundary

The literature registry contains useful mechanism and direction anchors, but no record currently supplies a compatible, locator-verified numerical calibration for active human touch demand, organizational capacity, gate outcomes, rework, UAT, arrivals or world multipliers. Accordingly, the checked-in numbers remain provenance class `I`. They may exercise mechanisms, comparators and failure boundaries in development simulations. They may not be described as empirical estimates, calibrated organizational parameters or production truth.

Preregistered evaluation thresholds are different: they are design controls rather than empirical calibration. Their class-I status is permitted for a locked synthetic decision rule only when preregistered; it does not make them evidence about organizations.

## Active parameter mapping

| Registry ID | Active input family | Concrete paths | Class / kind | Source basis | Permitted use | Production gap |
|---|---|---:|---|---|---|---|
| PR-TIME | Horizon and warm-up | 2 | I / calibration | Illustrative configuration | Development simulation | No empirical planning-horizon or warm-up calibration |
| PR-ROLE-CAPACITY | Role concurrency and initial backlog | 8 | I / calibration | Illustrative configuration | Development simulation | No observed effective capacity, absence, interruption or backlog data |
| PR-ARRIVALS | Portfolio count, start, spacing and template sequence | 4 | I / calibration | Fixed synthetic portfolio | Development load fixtures | No compatible arrival process, task-mix or correlation estimate |
| PR-DEMAND | Eight role-stage distribution families, parameters, truncations and independence declarations | 32 | I / calibration | Illustrative fixed/triangular active-time demand | Development mechanism tests | LP-008/009 concern review behavior or elapsed closure, not transferable touch-time distributions; context, implementation, QA and UAT demand remain uncalibrated |
| PR-CALENDAR | Availability window, blackout and concurrency | 9 | I / calibration | Explicit synthetic calendar | Calendar/queue verification | No observed team calendar or context-switch/setup-loss estimate |
| PR-REWORK | Route probability and loop ceiling | 2 | I / calibration | Bounded synthetic rework fixture | Rework safety tests | LP-010 supports failure mechanisms but supplies no transferable rework probability or loop distribution |
| PR-WORLD-TRUTH | Service multipliers and gate Fail/Conditional probabilities across six worlds | 18 | I / calibration | LP-001/002/008–011 are directional/structural anchors only | Development sensitivity worlds | No universal AI multiplier, active-review multiplier, gate probability or conditional-pass estimator; adverse/favorable findings cannot be copied as truth parameters |
| PR-TEMPLATE | Story Points, HIE-compatible fields and five PDD ratings for two templates | 20 | I / comparator input | LP-003/004/007 support comparator structure; LP-005/006 support future measurement work | Development comparator/mechanism tests | No validated pre-task PDD instrument, organizational calibration, or workload-to-hours conversion |
| PR-DECISION | Seven evaluation thresholds/conventions | 7 | I / design control | Protocol-owner engineering conventions | Development and preregistered synthetic decision rules | Not evidence of real usefulness; cannot be interpreted as empirical effect thresholds |

## Literature-to-parameter rejection decisions

- LP-001 and LP-002 justify favorable and adverse AI-moderation scenarios. Their reported task effects cannot become universal service multipliers.
- LP-003 supports information-instability research but not an AI readiness or gate-failure probability.
- LP-004 supports retaining Story Points and heterogeneity comparators, not downstream lifecycle distributions.
- LP-005 and LP-006 support future Route A instrument work; they cannot calibrate objective hours or capacity.
- LP-007 supports an SP-prediction comparator family, not Story Point validity.
- LP-008 remains extraction-pending and provides no executable numeric parameter.
- LP-009 reports elapsed pull-request closure, which cannot be substituted for active review touch time or causal delay.
- LP-010 and LP-011 support explicit testing, CI, review and change-propagation mechanisms, but not universal failure probabilities or causal weights.

## Requirements to lift the production hard stop

Each calibration record must be replaced or supplemented by an `E1` or `E2` record with `verified_executable` approval and all of the following: exact source locator and version/checksum; compatible population/task/tool context; original estimand and uncertainty; target unit; reproducible transformation; distribution-family rationale; bounds and truncation; correlation assumptions; extractor and independent verifier; applicability limits; and prespecified alternatives for sensitivity. Subscription-database retrieval alone does not satisfy this requirement.

Until those records exist, `simulation.parameter_registry.check_parameter_registry(..., use="production_calibration")` fails closed, and `simulation.prelock` reports `parameter_provenance` as failed. Development execution remains permitted and explicitly illustrative.
