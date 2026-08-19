# Gate 3 Causal and Mechanism Model

**Status:** Conceptual ordering for Route B; arrows are hypothesized mechanisms, not estimated causal effects.

## 1. Commitment cutoff

Define `t0` as the planning/commitment cutoff. Every prospective predictor must be observable, timestamped, and frozen at `t0`.

Prohibited prospective inputs include realized prompt counts, corrections, generated LOC, code churn, review comments, test failures, cycle-state transitions, actual rework, and gate evidence added after `t0`.

## 2. Mechanism ordering

```text
Pre-commitment demand drivers (IU, CPE, CPD, AO, CT) + risk tier
                                  │
                 Stage Automation Enablement moderates
                                  │
                                  ▼
                 Forecast Role–Stage Human Touch Demand
                                  │
             ┌────────────────────┴───────────────────┐
             ▼                                        ▼
Available Role Capacity + existing queue       Evidence Readiness State
             │                                        │
             ▼                                        ▼
 Role Capacity Pressure → Queue Delay       gate decision/rework probability
             │                                        │
             └───────────────┬────────────────────────┘
                             ▼
       touch + waiting + blocking + rework transitions
                             │
                             ▼
 Verified Delivery Capacity / completion / cycle time
                             │
                             ▼
       external quality, UAT, change-failure and DORA criteria
```

Context Provisioning Deficit is a missing-input driver at `t0`. Evidence Readiness State is the status of risk-tier-required evidence at a named gate/time. They must not be encoded as duplicate measures.

## 3. Important confounding and selection risks for Route A

- AI adoption is confounded by team maturity, task selection, organizational investment, and codebase condition.
- Gate use is risk-selected, creating confounding by indication.
- Team/tool/process maturity influences estimates, AI use, and outcomes.
- Analysis of completed work only creates survivor bias.
- Story Points are team-relative and must not be pooled raw across teams.
- Readiness and review demand can be mediators, measurements, or consequences depending on timestamp.

Consequently, Route B uses “the model implies under stated assumptions.” A later observational Route A study uses predictive-association language unless an intervention design justifies causal inference.

## 4. Switchable mechanisms for simulation

1. implementation service-time compression from AI assistance;
2. generated batch-size amplification;
3. verification-demand change;
4. context-defect-driven refinement loops;
5. risk/coupling-driven specialist demand;
6. nonlinear queue growth near role saturation;
7. gate assessment overhead versus avoided downstream rework;
8. residual-risk transfer after conditional pass;
9. context-switch/setup penalty reducing effective capacity;
10. parallel work where dependencies permit.

Every mechanism must be individually enabled/disabled. If AI changes only implementation time in a scenario, the model must not invent verification burden.

## 5. Causal-claim boundary

Route B can assess internal coherence, parameter recovery, scenario differences, mechanism sensitivity, and policy trade-offs. It cannot estimate actual effects of AI, gates, staffing, or VDCM use. Any real gate-effect study should follow predictive validation and, where feasible, use a randomized or stepped-wedge planning rollout.
