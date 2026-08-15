# Context Is Not a Snapshot: The Missing Safety Boundary in Agentic AI

An AI agent can reason correctly, choose the intended tool, produce a schema-valid request—and still take the wrong action.

The failure may have nothing to do with hallucination.

The world may simply have changed between **observation**, **planning**, and **execution**.

An approval was valid when retrieved but revoked before commit. Consent was narrowed. A policy was superseded. An identity-to-account binding changed. Inventory was consumed elsewhere. A legal hold was issued. A credential rotated. A downstream agent inherited an earlier agent's conclusion without inheriting its evidence conditions.

The model may be logically correct relative to its inputs while the action is operationally invalid relative to the present world.

That is the problem explored in the **Action Evidence Safety** research repository through **Risk-Adaptive Evidence Revalidation (RAER)**.

## The problem statement

Most agent architectures treat context as input: prompt history, retrieved documents, memory, tool responses, identity attributes, policies, approvals, and operational state.

For a consequential action, that model is incomplete.

Context is not merely information available to the model. It is a set of claims whose truth, authority, scope, and freshness determine whether a proposed side effect is permissible **now**.

Suppose an agent observes evidence \(E_{t0}\), constructs plan \(P_{t1}\), and attempts action \(A_{t2}\). If the world changes between \(t0\) and \(t2\), then:

> Correct reasoning over stale premises can produce an unsafe state transition.

The relevant boundary is therefore not only model inference. It is the **time-of-check to time-of-use boundary** surrounding the action.

The engineering question becomes:

> Which mutable prerequisites must still be true at the exact moment an agent is allowed to change the world—and how should the system establish that truth under finite cost, latency, and authority constraints?

## Why this matters

An assistant that generates text can often be corrected. An agent that transfers money, modifies access, sends regulated data, changes infrastructure, schedules treatment, updates an employee record, or places an order can create effects that are costly, propagating, or irreversible.

Longer context windows do not solve this problem. Better retrieval does not automatically solve it. Higher model confidence does not solve it. More agents may make it worse by reproducing stale claims across hand-offs.

Three properties are frequently—and dangerously—collapsed:

1. **Inference confidence:** how strongly a model supports a conclusion given its inputs.
2. **Evidence validity:** whether those inputs still correspond to an authoritative source of truth.
3. **Action authority:** whether the principal remains permitted to perform this particular action, for this purpose, at this time.

A system can have high confidence, low evidence validity, and no current authority simultaneously.

This is why architecture selection and execution safety must be treated as two independent design axes.

The familiar progression remains useful:

**Business objective → capability → deterministic software → LLM → workflow → agent → multi-agent system**

Use the least complex architecture that satisfies the capability. But regardless of the rung selected, place an evidence-validity gate before consequential state change.

## What the research is trying to solve

“Refresh everything” appears safe but may be infeasible. Authoritative checks consume latency, money, API capacity, rate limits, operational disruption, and scarce human attention. Conversely, “trust the context” is cheap but allows invalid prerequisites to survive until execution.

RAER studies the decision between these extremes:

- Which evidence should be revalidated for this proposed action?
- Which checks are mandatory rather than economically tradable?
- How should validation cost be balanced against expected action harm and abstention loss?
- When should the system act, refresh state, request renewed authority, or abstain?
- Can those decisions be made reproducibly rather than delegated to an LLM's self-reported confidence?

The research treats action-critical context as a collection of typed, mutable evidence prerequisites. For each prerequisite \(i\), the policy considers:

- estimated probability of invalidity \(q_i\);
- normalized criticality \(w_i\);
- authoritative validation cost \(c_i\);
- evidence age, source volatility, dependent changes, update frequency, source reliability, authorization age, and contradictions.

For the proposed action, it also considers consequence, irreversibility, authorization sensitivity, available validation budget, and the loss of unnecessarily refusing a valid action.

The selector evaluates feasible check subsets and chooses a deterministic decision path. The LLM may propose an action; it does not get to redefine the admission policy at runtime.

## The solution direction: revalidate evidence at the action boundary

The central abstraction is an **evidence envelope**, not an unstructured memory fragment.

Each material claim should carry:

- semantic type and value;
- authoritative source and record identifier;
- source version or ETag;
- observation timestamp and maximum valid age;
- permitted purpose, action, and scope;
- dependencies and invalidation triggers;
- contradiction state;
- validation function and expected cost.

Before execution, the system should create an **action manifest** containing the intended operation, parameters, actor, delegated principal, purpose, expected read/write set, reversibility, prerequisites, validation endpoints, budget, deadline, idempotency key, and compensation strategy.

The evidence policy then returns one of four semantically distinct outcomes:

- **ACT** — selected authoritative checks remain valid and modeled action loss is acceptable.
- **REFRESH** — checked policy, identity, scope, or operational state is invalid; rebuild the plan from current evidence.
- **ASK** — authorization is missing, expired, narrowed, or revoked; obtain accountable authority.
- **ABSTAIN** — residual risk is unacceptable, evidence is contradictory, or mandatory validation cannot be completed within budget.

This separation matters operationally. REFRESH is a state-recovery workflow. ASK is an authority-recovery workflow. ABSTAIN is a safety outcome. Treating all three as a generic “tool failure” destroys their audit meaning and invites unsafe retries.

## Authorization must be non-fungible

Some evidence can be optimized under a cost–risk objective. Some constraints must not be traded away.

RAER includes a mandatory authorization safeguard: when authorization sensitivity and invalidity-weighted criticality cross a threshold, the authorization prerequisite must be checked. If its check cannot fit within budget, the policy abstains. It does not omit the check because another evidence subset is faster or cheaper.

This principle generalizes beyond authorization to consent, legal holds, segregation-of-duties approval, safety interlocks, data-residency constraints, and regulated-purpose limitations.

In the fitted design-data ablation, removing the authorization safeguard increased harmful actions from **14/45 to 19/45** and produced **seven harmful actions involving unchecked, triggered authorization evidence**. The full fitted configuration produced zero in that category.

The implication is direct: a probabilistic optimizer needs hard admission constraints around non-negotiable rights and duties.

## What the experiment actually found

The RAER-B96 benchmark contains 96 constructed scenarios and 288 evidence prerequisites across commerce, cybersecurity, finance, healthcare administration, human resources, and privacy.

RAER v2 used leave-one-domain-out selection across an 80-configuration design grid. The exposed design set contained 72 cases; a separate 24-case partition remained sealed.

Out-of-fold results were:

- safe completion: **25/27 = 92.6%**;
- harmful actions: **14/45 = 31.1%**;
- mean validation cost: **0.547**;
- false blocks: **2**;
- harmful actions involving triggered authorization evidence: **0**.

The registered FIXED_0.20 comparator produced:

- safe completion: **27/27 = 100%**;
- harmful actions: **18/45 = 40.0%**;
- mean validation cost: **0.800**;
- false blocks: **0**.

RAER therefore showed a descriptive reduction of four harmful actions and a **31.6% lower mean validation cost**. But its safe-completion result was below the prospectively specified 95% requirement.

Seven of eight gates passed. The composite decision was still:

> **FAIL_KEEP_HELD_OUT_SEALED**

This negative result is scientifically important. Favorable averages must not override a failed operational constraint. A system that blocks legitimate actions can create its own safety, access, and business risks. The two false blocks were localized to cross-domain configuration transfer in finance and privacy—evidence that pooled performance does not guarantee worst-domain stability.

The work should therefore be read as a rigorous **design-stage method and falsifiable research direction**, not as a production-certified safety claim.

## Precautions for real systems

### 1. Never use model confidence as evidence freshness

Confidence describes an inference conditioned on supplied inputs. It does not establish that the inputs remain true.

### 2. Keep action-critical facts out of untyped prompt prose

Prompts and vector memories may carry useful narrative context, but authority, consent, policy version, identity binding, balances, inventory, and safety state should be represented as typed claims with provenance and validation semantics.

### 3. Minimize the check-to-commit gap

Where possible, validate prerequisites and mutate state within the same transaction. Otherwise use compare-and-set, version preconditions, conditional requests, leases, or a final critical recheck immediately before the side effect.

### 4. Design for correlated invalidity

Prerequisites are not always independent. A role change may invalidate identity, authorization, and scope together. A policy update may invalidate several downstream interpretations. Dependency graphs and correlation stress tests are necessary.

### 5. Make retries replay-safe

A timeout does not prove that an action failed. Use idempotency keys, operation identifiers, durable state machines, reconciliation, and explicit compensation. Never allow a conversational retry to become a duplicate business transaction.

### 6. Verify postconditions in the authoritative system

HTTP 200, a well-formed tool response, or an agent's success statement is not proof of the intended state transition. Read back authoritative state, reconcile partial effects, and invalidate dependent memory.

### 7. Bound multi-agent context and authority

Pass scoped evidence envelopes, not shared-memory soup. A downstream agent must receive provenance, freshness, purpose, and permitted actions—and must not inherit another agent's confidence as authority.

### 8. Preserve fail-closed outcomes without creating silent dead ends

ASK, REFRESH, and ABSTAIN need owners, escalation paths, service-level objectives, user explanations, and telemetry. Safety without recoverability becomes operational paralysis.

### 9. Evaluate domains separately

Track worst-domain completion, harmful-action rate, false blocks, authorization failures, cost, latency, and uncertainty. Aggregate averages can conceal unacceptable local behavior.

### 10. Do not treat a benchmark improvement as deployment readiness

Constructed scenarios support controlled comparison. They do not establish calibrated real-world invalidity probabilities, external validity, regulatory acceptance, or safety under novel distributions.

## Turning the research into engineering practice

The most useful way to apply this work is not to copy one threshold. It is to adopt the research discipline and architecture pattern.

### Phase 1 — Map consequential actions

Inventory every agent tool that can change external state. Classify consequence, reversibility, affected principal, regulatory sensitivity, financial exposure, and blast radius. Start with a narrow, high-value workflow—not the entire enterprise.

### Phase 2 — Define evidence contracts

For each action, enumerate the prerequisites that must be true at commit time. Assign authoritative sources, freshness requirements, version semantics, dependency links, mandatory constraints, and validation costs. Make undocumented assumptions visible.

### Phase 3 — Introduce a plan/commit boundary

Let the model produce a proposed action and rationale. Convert the proposal into a typed action manifest. Place a deterministic policy enforcement point between planning and tool execution. The execution credential should be issued only after the gate succeeds and should be scoped to the approved action.

### Phase 4 — Run in shadow mode

Compute ACT/REFRESH/ASK/ABSTAIN decisions without changing production behavior. Compare them with actual outcomes, human decisions, stale-evidence incidents, false blocks, latency, and validation cost. Calibrate using local data rather than importing research parameters.

### Phase 5 — Exercise temporal failure modes

Use fault injection and replay to simulate revocation, policy updates, identity rebinding, contradictory sources, delayed writes, tool timeouts, rate limits, budget exhaustion, dependency failure, and state changes after validation but before commit.

### Phase 6 — Establish prospective deployment gates

Define success criteria before inspecting final results. Include safe completion, harmful actions, mandatory-authorization violations, false blocks, cost, latency, worst-domain performance, and uncertainty intervals. Require all critical gates to pass; do not optimize the evaluation after seeing the answer.

### Phase 7 — Roll out progressively

Move from observe-only to human-confirmed actions, then to bounded autonomy for reversible low-consequence operations. Expand authority only when evidence supports the next level. Maintain kill switches, rate limits, least-privilege credentials, immutable audit records, and rollback or compensation procedures.

### Phase 8 — Learn from committed outcomes

Treat every action result as new evidence. Verify postconditions, measure drift, invalidate dependent caches, review ASK/REFRESH/ABSTAIN patterns, and update estimators under controlled governance. Version policies and preserve reproducibility.

## A practical reference architecture

A production implementation can be separated into five planes:

1. **Capability plane:** deterministic services, LLM functions, workflows, and agents chosen according to task requirements.
2. **Evidence plane:** typed claims, authoritative connectors, provenance, versions, validity windows, and dependency graphs.
3. **Decision plane:** action manifest, invalidity estimation, mandatory checks, risk–cost selection, and ACT/REFRESH/ASK/ABSTAIN policy.
4. **Execution plane:** least-privilege credentials, transactional adapters, conditional writes, idempotency, postcondition checks, and compensation.
5. **Assurance plane:** traces, immutable decision records, temporal fault injection, domain-stratified evaluation, prospective gates, and incident review.

This separation prevents the LLM from simultaneously becoming the reasoner, database, authorization server, policy engine, workflow coordinator, and safety monitor.

## The larger lesson

The next generation of reliable agentic systems will not be secured by larger context windows alone.

They will be secured by knowing:

- which claims are mutable;
- which sources are authoritative;
- which constraints are non-negotiable;
- how validity changes over time;
- what must be checked at commit;
- how to verify the resulting state;
- and when the correct action is to stop.

The first architecture question remains:

> **Does this capability actually require an agent?**

But every action-taking system needs a second question:

> **What must still be true at the exact moment this system is permitted to change the world?**

Repository: https://github.com/khshaik/applied-ai-research-lab/tree/main/action-evidence-safety-research

Related system-design perspective: https://medium.com/inspiredbrilliance/agentic-ai-building-the-right-mental-model-for-system-design-269d85c1689f

#AgenticAI #AISafety #ContextEngineering #LLMOps #AgentArchitecture #ResponsibleAI #AIResearch #ToolUse #EnterpriseAI
