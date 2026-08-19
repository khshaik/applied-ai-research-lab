# Gate 3B Decision Pack

**Date:** 13 August 2026  
**Recommendation:** Conditional approve for prototype implementation  
**Validation status:** Operationally specified, not empirically validated

## Decision summary

The Gate 3 framework is now executable in principle without claiming to measure human cognition. The proposed approach forecasts active human service demand by role and lifecycle stage, combines it with available capacity and existing queues, represents evidence readiness explicitly, and simulates completion and quality-risk behavior under declared assumptions.

Use descriptive terminology pending systematic and legal collision checks:

- **Role-Constrained Verified Delivery Model** — overall framework;
- **Role–Stage Demand Profile** — pre-commitment demand representation;
- **Evidence Readiness State** — gate/evidence representation;
- **Verified Delivery Capacity** — predicted verified items per horizon and completion probability.

Avoid VDCM/RSDRI in the paper title because both acronyms have unrelated established uses.

## Items proposed for approval

1. Five formative pre-commitment demand drivers:
   - Intent Uncertainty;
   - Change Propagation Exposure;
   - Context Provisioning Deficit;
   - Assurance Obligation;
   - Coordination Topology.
2. A five-element 0–4 profile with `U`/`NA`, raw evidence, rationale, confidence, timestamp, and version—not a summed score.
3. Four abstract risk tiers T1–T4 that organizations map to their own policies.
4. Six evidence gates with invariant `Pass`, `Conditional`, `Fail`, and `Not Applicable` semantics.
5. Separate treatment of assurance-production work, gate-assessment touch time, gate queue delay, remediation, and residual risk.
6. Strict separation of active touch demand, subjective workload, cognitive load, capacity, queue delay, readiness, and outcomes.
7. A three-layer simulation design: truth generator, equal-information comparator layer, and evaluation layer.
8. Six comparator worlds, including Story-Point-sufficient and deliberately misspecified worlds where the proposed model may show no advantage.
9. Provisional simulation-engineering thresholds for reproducibility, Monte Carlo precision, material forecast improvement, practical equivalence, and instability.
10. Explicit Route B limitation: conditional scenario behavior only; no claim of real predictive, cognitive, causal, usability, or organizational validity.

## Completed artifacts

- Gate 3 framework and construct dictionary;
- causal/mechanism model;
- Route B simulation protocol;
- future Route A propositions and leakage controls;
- driver anchors and raw-evidence rules;
- risk-tier readiness/evidence rules;
- parameter-provenance and rejection rules;
- valid JSON Schema for simulation configurations;
- independent audits by construct, readiness, simulation, causal, and proposition agents;
- preliminary naming-collision audit.

## Pending after approval

1. write a complete example YAML configuration and validate it against the schema;
2. implement the DES engine and immutable event/output tables;
3. implement hard-stop verification fixtures and deterministic checks;
4. create comparator information policies and locked seed manifests;
5. populate literature-informed parameter records through the systematic review;
6. run development scenarios, sensitivity analysis, and adversarial worlds;
7. preregister the locked evaluation configuration and thresholds;
8. update the live Excel research workbook with Gate 3 artifacts;
9. complete Gate 2 executable database searches and evidence synthesis;
10. retain Route A measurement and organizational validation as future work unless genuine data becomes available.

## Approval language

Suggested protocol-owner decision:

> Gate 3B is approved for prototype implementation using descriptive terminology, the five formative driver profile, four configurable risk tiers, evidence-readiness semantics, and the three-layer Route B simulation design. Approval authorizes schema/configuration and simulation implementation; it does not certify construct validity, empirical calibration, organizational usefulness, or superiority over Story Points/HIE.
