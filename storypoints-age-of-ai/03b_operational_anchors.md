# Gate 3B Operational Anchors

**Status:** Draft for audit; formative planning indicators, not validated scales  
**Cutoff:** Score only evidence observable at commitment time `t0`  
**Rule:** Preserve raw evidence/counts. Never convert an anchor directly to hours.

## Scoring controls

- Select the highest anchor whose observable conditions are materially present; record the evidence and uncertainty.
- Use `U = Unrateable` when evidence is insufficient and `NA` only when demonstrably inapplicable. Do not silently score missing information as zero or four.
- Record scorer, timestamp, instrument version, and confidence (`High`, `Moderate`, `Low`).
- Assign the lowest level whose complete description fits, except for an explicit level-4 critical trigger. For mixed cases, record the dominant level and highest material indicator; do not average indicators.
- Drivers are formative and remain separate. No total score, Fibonacci conversion, or Cronbach-alpha claim is permitted.

## IU — Intent Uncertainty

| Level | Observable anchor at t0 |
|---:|---|
| 0 | Scope, business rules, constraints, decision owner, and testable acceptance examples are explicit; no material unresolved decision. |
| 1 | One bounded clarification remains; owner and resolution path are known; no expected scope or acceptance change. |
| 2 | Multiple clarifications or one material rule/acceptance decision remains; affected stakeholders and decision date are known. |
| 3 | Competing interpretations, unresolved stakeholder alignment, or likely scope/acceptance change; decision ownership or timing is uncertain. |
| 4 | Problem/outcome is disputed or exploratory; critical business rules and acceptance basis are absent; commitment would require discovery. |

Required raw fields: unresolved decision count, stakeholder groups, acceptance examples present, domain novelty, declared scope-volatility class.

Control: domain novelty alone does not raise IU unless it creates an identifiable unresolved interpretation.

## CPE — Change Propagation Exposure

| Level | Observable anchor at t0 |
|---:|---|
| 0 | Localized change inside one well-understood component; no contract, data, privilege, or non-functional impact. |
| 1 | Small change within one bounded component with known tests and rollback; no externally consumed contract change. |
| 2 | Multiple modules or one internal interface/data change; dependencies and rollback are identified. |
| 3 | Cross-service/team propagation, externally consumed contract/data change, or material availability/performance/security impact. |
| 4 | Systemic or poorly bounded propagation involving critical data, privileges, regulation, migration, irreversible state, or uncertain rollback. |

Required raw fields: components/services, interfaces/contracts, data classifications, privilege changes, dependency count, rollback class, risk tier.

Control: risk tier does not itself determine CPE; CPE describes technical propagation, while AO describes policy-mandated evidence.

## CPD — Context Provisioning Deficit

| Level | Observable anchor at t0 |
|---:|---|
| 0 | Required repository/domain context is current, approved, retrievable, bounded, and demonstrably sufficient for the planned workflow. |
| 1 | Minor known gap with an authoritative source and low-cost retrieval; instructions and constraints otherwise current. |
| 2 | Several gaps or stale/conflicting material requiring assembly/validation before reliable AI or human use. |
| 3 | Critical context is fragmented, inaccessible, unowned, or unapproved; substantial reconstruction or expert interpretation is required. |
| 4 | No trustworthy basis exists for key domain/architecture constraints; proceeding would rely on unverified assumptions or prohibited disclosure. |

Required raw fields: required artifacts, present/current/approved/retrievable flags, source owner, freshness date, prohibited-data constraint, retrieval gap count.

Classification rule: if an agreed answer exists but is missing/stale/inaccessible/conflicting, use CPD; if the answer is undecided or disputed, use IU. Rate both only with distinct supporting evidence.

## AO — Assurance Obligation

| Level | Observable anchor at t0 |
|---:|---|
| 0 | Routine evidence only; existing automated unit/static checks cover the bounded change and no independent approval is required. |
| 1 | Standard peer review plus existing automated regression evidence; no specialist or business acceptance activity. |
| 2 | Integration/system evidence or targeted manual QA/UAT is required; one independent role contributes assurance. |
| 3 | Multiple independent assurance roles or material security, performance, privacy, accessibility, operational, or UAT evidence is mandatory. |
| 4 | Critical/regulatory change requiring independent specialist approval, traceable end-to-end evidence, resilience/recovery proof, and formal residual-risk ownership. |

Required raw fields: risk-policy ID/version, required evidence types, independent roles, mandatory approvals, retention/audit requirement.

Control: AO measures evidence required—not whether it exists, its duration, results, or subsequent defects. Unknown applicability is `U`.

## CT — Coordination Topology

| Level | Observable anchor at t0 |
|---:|---|
| 0 | One stable team/role group; no external dependency, handoff, or decision. |
| 1 | One planned handoff or consultation with a known owner and service expectation. |
| 2 | Two or more roles or one external team/dependency with explicit sequencing and owners. |
| 3 | Multiple teams/specialists, coupled decisions, asynchronous handoffs, or schedule/time-zone constraints on the critical path. |
| 4 | Networked dependencies with uncertain owners/order/availability, external vendors/regulators, or mutually blocking decisions. |

Required raw fields: role pools, teams, external parties, dependency edges, decisions, handoffs, time zones, owners, service expectations.

Control: CT records structure, not observed context switching, queue delay, blocking, or missed dates. AO captures evidence/independence; CT captures the organizational route used to obtain it.

## Reliability and validity work

Route B can test whether anchors are complete, executable, and sensitive in scenarios. Route A must evaluate content coverage, inter-rater weighted kappa/ICC, indicator redundancy/VIF, incremental criterion validity, overhead, gaming, and usability with qualified people and real work.
