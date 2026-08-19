# Gate 3B Risk-Scaled Readiness Rules

**Status:** Configurable reference rules; not evidence that gates improve real quality

## Risk tiers

| Tier | Reference meaning | Gate depth |
|---|---|---|
| T1 Limited | Local, reversible, low external/data/security/operational impact | Artifact-linked evidence; automation or same-role verification may be permitted by policy |
| T2 Material | Meaningful user, service, dependency, or internal-business impact | Named peer review, broader verification, explicit rollback and acceptance evidence |
| T3 High | Sensitive data, material security/privacy, external customer, regulatory, or major operational exposure | Independent specialist evidence, formal risk owner, stronger traceability and separation of duties |
| T4 Critical | Safety-, mission-, legally critical, highly irreversible, or catastrophic-impact change | Policy-prescribed evidence, independent approval, strict segregation, and no conditional passage for designated critical obligations |

Organizations must map these reference tiers to their own policies. The research artifact must retain the policy identifier and version. Risk tier raises rigor; it does not automatically inflate every role-stage demand or make every evidence type applicable.

## Universal gate decision logic

- **Pass:** all applicable mandatory evidence for the risk tier is present, current, artifact-matched, attributable, traceable, independently checkable, satisfies configured acceptance rules, and is accepted by the accountable authority.
- **Conditional:** policy explicitly permits progression; every deficiency has an owner, deadline, downstream constraint, and residual-risk record. Conditional is prohibited for non-waivable evidence.
- **Fail:** mandatory evidence is absent, expired, contradictory, untraceable, rejected, or the residual risk exceeds delegated authority.
- **Not Applicable:** a documented applicability rule excludes the evidence/gate; N/A is never a substitute for missing evidence.

Gate evaluation consumes role capacity and time. Evidence existence does not prove correctness.

## Gate evidence catalogue

| Gate | Minimum T1 evidence | T2 additions | T3/T4 additions | Accountable role |
|---|---|---|---|---|
| Intent Ready | problem/outcome, bounded scope, constraints, acceptance examples, owner | stakeholders, impact/dependency assessment, material decisions resolved | formal risk/control interpretation, authorized acceptance basis, retained decision evidence | Product/domain owner |
| Architecture Ready | affected component/interfaces and rollback approach | architecture/data/security/operability assessment and decisions | independent risk/architecture approval; resilience, recovery, migration, threat and residual-risk evidence | Architecture authority |
| Generation Ready | implementation plan, approved context sources, repository instructions, constraints/prohibited actions | context freshness/traceability; sensitive-data/tool-use approval; verification plan | controlled environment, approved tool/model/configuration, auditable context package and provenance requirements | Engineering/technical lead |
| Verification Ready | traceable/reviewable change, build, unit/static evidence and findings | independent review; integration/regression, dependency/license and specialist evidence | separation of duties, formal security/privacy/compliance assurance, complete artifact-to-evidence chain | Engineering review owner |
| Release Ready | deploy/rollback instructions and required automated checks | operational readiness, observability, support, migration and change-risk evidence | formal release authority, recovery/business-continuity proof and non-waivable controls | Release/operations authority |
| Acceptance Ready | acceptance examples demonstrated and open issues classified | manual QA/UAT, handover and owned residual risks | formal business/control acceptance and auditable evidence retention | Business/product acceptance owner |

## Evidence record

Every evidence item records ID/type, work item, requirement/artifact/build/environment links, gate, risk tier, source URI/system, version/hash, created/verified time, maximum-age rule where applicable, invalidating events, producer, verifier, accountable authority, scope/result/limitations/coverage, traceability target, mandatory/waivable flag, exceptions, superseded evidence, provenance, and confidentiality class. A recent timestamp cannot make mismatched evidence valid.

Every decision records state, accountable role, timestamp, rationale, missing/expired evidence, residual-risk ID, next transition, and simulated/observed provenance.

## Safeguards

- A failed mandatory gate cannot be averaged into an overall percentage.
- Conditional passes carry residual risk downstream; they do not erase it.
- T4 evidence designated non-waivable cannot receive Conditional status.
- The same person/agent must not be assumed independent where policy requires separation.
- AI can assemble or check evidence but cannot own regulated/business acceptance unless policy lawfully delegates that authority.
- Compare no-gate, advisory, universal, and risk-scaled policies in simulation; retain scenarios where gates add delay without benefit.

## Residual-risk record

Every Conditional decision records a unique risk ID, source gate/evidence obligation, affected artifacts and downstream gates, exposure/consequence, organization-defined risk rating, compensating control, owner and accepting authority, remediation and due date, expiry/revalidation trigger, escalation path, closure evidence, and final disposition.

## Gate-overhead accounting

Separate assurance production work, gate-assessment touch time, gate queue delay, and remediation demand. Record assessment/retrieval/reconciliation minutes, approvers/handoffs, decision delay, reassessment count, conditional-risk carry duration, and gate overhead as a proportion of role-stage touch demand. No defects-avoided benefit is assumed.
