# Context Is Not a Snapshot: Engineering Agentic Systems Across State Change

## The overlooked failure boundary in agentic AI

An AI system can produce a perfectly coherent plan, call the correct tool, satisfy its local schema, and still perform the wrong action.

That failure does not require a hallucination, a jailbreak, or a defective model. It requires only time.

At observation time, a fact is true. At planning time, the fact is retrieved from memory or a database. At execution time, the world has changed. Approval was revoked. Consent was narrowed. A policy was superseded. The account-to-person binding changed. Inventory was consumed by another channel. A work order was amended. A credential rotated. The system reasons correctly over an obsolete premise and crosses a consequential side-effect boundary.

This is the engineering problem explored by the repository **Action Evidence Safety**, whose first study is **Risk-Adaptive Evidence Revalidation (RAER)**. Its most important contribution is not a claim that one policy has solved agent safety. In fact, its prospectively specified v2 method failed one of eight registered gates. Its value lies in making a frequently implicit problem precise: when an automated action depends on mutable evidence, what should be revalidated, at what cost, and when must the system refuse to act?

![Context lifecycle](../assets/01-context-lifecycle.png)

## Start with the right architecture question - then add the missing execution question

Karthika Vijayan's essay on the mental model for agentic system design makes a useful architectural argument: begin with the business objective, decompose it into capabilities, and use deterministic software, an LLM capability, a fixed workflow, a single agent, or multiple agents only as the problem requires. An LLM is appropriate where interpretation is needed; an agent is appropriate where some part of the workflow must be chosen dynamically; multiple agents are justified when responsibilities, tools, knowledge, or contexts require real separation.

That is a sound capability-to-architecture progression. It prevents “agent” from becoming the default answer to every software problem.

RAER exposes a second, orthogonal design axis. Even when the architecture is correctly scoped, the evidence supporting an action may lose validity before the action commits. Architecture answers **who or what selects the next step**. Evidence control answers **whether the premises authorizing that step are still fit for use**.

The two questions should be joined:

1. Does this capability require deterministic code, an LLM, a workflow, an agent, or a multi-agent system?
2. Before this capability changes external state, which prerequisites must still be true, and how will the system establish that they are true now?

![Architecture and gate](../assets/02-architecture-and-evidence-gate.png)

## Context has at least three temporal forms

For action-taking systems, “context” should not be treated as a single prompt payload. It evolves through an action lifecycle.

### 1. Before: observed context

The system assembles evidence: identity, authorization, policy, purpose, scope, resource state, operational constraints, and dependent records. Every material claim should carry provenance and time semantics:

- authoritative source;
- source record and version;
- observation timestamp;
- validity window or freshness requirement;
- known dependencies and invalidation triggers;
- contradiction state;
- permitted purpose and action scope.

The right abstraction is an evidence envelope, not a free-form memory fragment.

### 2. Now: pre-commit context

The system has a proposed action with concrete parameters and an anticipated read/write set. The question is no longer “What did the agent know?” but “Which prerequisites remain sufficiently valid for this exact action?”

This is where authoritative revalidation belongs. Some checks may be cheap; others may consume latency, money, rate limits, operational interruption, or human attention. Therefore “refresh everything” and “trust memory” are both incomplete policies. The system needs a selection rule and a refusal path.

### 3. After: committed context

The action itself changes the environment. Its result becomes new evidence for later decisions. The system must verify postconditions in the authoritative system of record, emit a durable audit event, invalidate dependent memories, reconcile partial failure, and trigger compensation or escalation where required.

Without this phase, yesterday's tool output becomes tomorrow's stale premise.

This temporal view also clarifies what a context switch means. It is not merely a conversational topic change. It is a change in the truth conditions, authority, purpose, scope, identity binding, or operational state on which an action depends.

## RAER: from context volume to action-specific evidence selection

RAER models a proposed consequential action with a validation budget \(B\), consequence score \(C\), irreversibility score \(I\), and a set of mutable evidence prerequisites. For prerequisite \(i\):

- \(q_i\) is a pre-action estimate of invalidity;
- \(w_i\) is normalized criticality;
- \(c_i\) is normalized authoritative-check cost.

The frozen estimator uses only observable pre-action features: evidence age, source volatility, dependent changes, update frequency, inverse source reliability, authorization age, and contradictory observations. Actual validity remains hidden from selection.

Action harm increases with consequence and irreversibility. For a candidate subset of checks \(S\), a valid authoritative check reduces modeled invalidity to a small verifier-error floor. Residual harm accounts for unchecked invalidity and a prespecified correlated-prerequisite uplift. A safe-probability proxy estimates how likely the prerequisites are to remain valid. RAER v2 then minimizes an interpretable objective:

> validation cost + bounded budget-slack penalty + min(expected action loss, expected abstention loss)

The method exactly enumerates feasible evidence subsets and uses deterministic tie-breaking. It does not ask an LLM to “feel confident.” It separates model reasoning from a reproducible action-control policy.

After selected checks run:

- **ACT** when checks are valid and modeled action loss does not exceed abstention loss;
- **REFRESH** when checked state, policy, identity, or scope evidence is invalid;
- **ASK** when a checked authorization prerequisite is invalid;
- **ABSTAIN** when residual risk remains too high or mandatory checks cannot fit within budget.

![RAER decision protocol](../assets/03-raer-decision-protocol.png)

## Authorization is not interchangeable with ordinary evidence

One of RAER's most important design choices is a mandatory authorization safeguard. If authorization sensitivity is high and invalidity-weighted criticality crosses a threshold, the authorization prerequisite must be checked. If the mandatory check cannot fit within the allowed budget, the policy abstains. It may not silently omit authority because another subset is cheaper.

This is not a cosmetic rule. In the fitted design-data ablation, removing the safeguard increased harmful actions from 14/45 to 19/45 and produced seven harmful actions involving unchecked triggered authorization evidence. The full fitted configuration produced zero in that category.

The broader principle is that certain constraints are non-fungible. A system should not “trade off” current authority against token cost, model confidence, or convenience. Authorization, legal hold, consent, segregation-of-duties approval, and safety interlocks may need hard admission semantics layered over a probabilistic objective.

## The negative result is the strongest part of the study

RAER-B96 contains 96 constructed scenarios and 288 evidence prerequisites across commerce, cybersecurity, finance, healthcare administration, human resources, and privacy. Each case has three prerequisites. The exposed design set contains 72 cases: 27 all-valid and 45 with at least one invalid prerequisite. A separate 24-case partition remained sealed.

RAER v2 was evaluated using leave-one-domain-out selection across an 80-configuration grid. The method was required to pass all eight prospective criteria, including safe completion, harmful-action rate, authorization safety, non-dominance, budget-slack limits, and fold eligibility.

Out of fold:

- safe completion: **25/27 (92.6%)**;
- harmful actions: **14/45 (31.1%)**;
- mean validation cost: **0.547**;
- false blocks: **2**;
- triggered-authorization harmful actions: **0**.

The registered comparator FIXED_0.20 achieved:

- safe completion: **27/27 (100.0%)**;
- harmful actions: **18/45 (40.0%)**;
- mean validation cost: **0.800**;
- false blocks: **0**.

RAER v2 therefore showed a descriptive reduction of four harmful actions and a 31.6% lower mean check cost. Yet its safe-completion rate was below the required 95%. Seven criteria passed; the composite gate failed. The correct decision was **FAIL_KEEP_HELD_OUT_SEALED**.

![Safety-cost trade-off](../assets/04-safety-cost-tradeoff.png)

This matters. A weak evaluation narrative could highlight lower harm and lower cost while hiding the two unnecessary blocks. A disciplined multi-objective gate prevents that form of result selection. It also preserves the held-out partition as a scientific resource rather than spending it on a method that did not clear its design threshold.

The failure analysis localized both false blocks to cross-domain configuration transfer. Inner-domain selection chose a lower abstention-loss weight in the omitted finance and privacy folds. All six inner configurations were eligible, yet each of those two unseen domains contributed one false block. The lesson is general: pooled eligibility does not guarantee worst-domain stability.

## What systems should do at the context switch

### Represent evidence as typed, versioned data

Do not let action-critical facts exist only as prose inside a prompt or opaque vector memory. Store each prerequisite as a typed claim with provenance, version, observation time, validity window, authority, scope, dependencies, and an authoritative validation function.

### Separate inference confidence from evidence validity

Model confidence concerns an inference given inputs. Evidence validity concerns whether those inputs still correspond to the world. A perfectly calibrated model can be perfectly confident about a stale fact.

### Make the action and its prerequisites explicit

Before tool execution, construct an action manifest:

- action type and parameters;
- actor and delegated principal;
- purpose and permitted scope;
- expected read/write set;
- reversible and irreversible effects;
- required prerequisites;
- authoritative validation endpoints;
- budget and deadline;
- idempotency and compensation plan.

The validation policy should operate over this manifest, not over undifferentiated conversation history.

### Use a plan/commit boundary

Reasoning should produce a proposal, not an immediate side effect. At commit time, use current versions, compare-and-set semantics, leases, or transactional preconditions to detect changes after planning. Where possible, bind checks and mutation in the same transaction. Where that is impossible, minimize the time-of-check to time-of-use window and re-check the most critical prerequisites immediately before effect.

### Budget revalidation by risk, not by token salience

Evidence selection should reflect consequence, irreversibility, authorization sensitivity, criticality, change likelihood, source reliability, correlation, and cost. Attention weight inside an LLM is not a safety policy. Neither is recency alone.

### Preserve distinct refusal outcomes

“Do nothing” is insufficiently expressive. Systems should distinguish:

- missing or revoked authority -> **ASK**;
- invalid operational evidence -> **REFRESH**;
- unresolved residual risk or unaffordable mandatory validation -> **ABSTAIN**;
- confirmed conditions -> **ACT**.

These outcomes drive different recovery workflows, owners, service-level objectives, and audit meanings.

### Verify after execution

A successful HTTP response is not proof that the intended business state was committed. Verify postconditions, record the authoritative result, reconcile partial effects, and invalidate dependent context. Use idempotency keys and replay-safe behavior because agentic systems retry.

### Scope context across agents

Multi-agent systems should not default to a shared memory soup. Hand off scoped evidence envelopes with explicit provenance, freshness, purpose, and allowed actions. Each agent should receive the minimum authority and context required for its responsibility. A downstream agent must not inherit upstream confidence as if it were current evidence.

### Observe the entire decision, not only the model call

Log the proposed action, candidate and selected evidence, estimated invalidity, cost, residual risk, authorization triggers, checks performed, versions returned, decision outcome, tool request, tool response, verified postcondition, and any compensation. This is the minimum substrate for incident analysis and policy evaluation.

### Test drift as a first-class fault model

Evaluation should inject authorization revocation, policy change, identity rebinding, delayed writes, contradictory sources, correlated failures, insufficient budgets, rate limits, tool timeouts, retries, and state changes between check and commit. Prompt benchmarks alone cannot exercise these failures.

## Assumptions to prohibit

![Assumptions and controls](../assets/05-assumptions-and-controls.png)

1. **“Memory is current.”** Memory is a cache unless the source contract proves otherwise.
2. **“More context is safer.”** Volume cannot compensate for missing provenance or freshness.
3. **“Latest timestamp wins.”** Authority and source precedence matter; the newest observation may be non-authoritative or adversarial.
4. **“High confidence means the premise is valid.”** Confidence and temporal validity are different variables.
5. **“Authorization is just another feature.”** Some constraints are admission requirements, not weighted preferences.
6. **“A successful tool call means success.”** Transport success, application acceptance, and intended state transition are distinct.
7. **“Retries are harmless.”** Consequential effects require idempotency and reconciliation.
8. **“One shared context improves collaboration.”** Shared context can amplify stale evidence, privilege, and scope leakage.
9. **“Refresh everything is always safest.”** Exhaustive checking may violate latency, availability, rate-limit, and human-attention constraints; it can also create denial-of-service behavior.
10. **“Average safety is enough.”** A pooled metric can hide domain-specific false blocks or harms.
11. **“An action is reversible because an API has an undo endpoint.”** Disclosure, customer impact, downstream propagation, and audit consequences may remain irreversible.
12. **“A benchmark improvement is deployment readiness.”** Constructed scenarios and descriptive intervals do not establish external effectiveness.

## How this connects to the wider research landscape

RAER sits at the intersection of several established lines of work and carefully limits its novelty claim.

- **Selective prediction and reject options** formalize the cost of abstention and risk-coverage trade-offs: Franc, Prusa, and Voracek (2023).
- **Active feature/evidence acquisition** studies which observations to purchase before prediction: Shim, Hwang, and Yang (2018); Li and Oliva (2025).
- **Budgeted acquire-or-abstain systems** already combine evidence acquisition and abstention: Xu et al.'s BCEA (2026). RAER's distinction is action-prerequisite semantics, authorization, deterministic state transitions, and explicit tool-action harm.
- **Stale and conflicting memory** benchmarks test whether agents recognize invalid memories: STALE (Chao et al., 2026) and MemConflict (Tao et al., 2026).
- **Agentic abstention** asks whether systems know when not to act or when to stop gathering information: AgentAbstain (Liu et al., 2026) and Luo, Wen, and Wang (2026).
- **Contract and solver-aided tool verification** checks formal preconditions, postconditions, and policy compliance: ToolGate (Liu et al., 2026) and Winston, Winston, and Just (2026). RAER adds the premise that the observations feeding those contracts may themselves be stale and costly to refresh.
- **Tool-agent safety benchmarks and runtime protection** cover stateful interaction and broader failure surfaces: ToolEmu, tau-bench, ToolSandbox, Agent-SafetyBench, ToolSafe, and SafeAgent.

The resulting research boundary is precise: RAER is not a generic agent framework, not a prompt-injection defense, not a calibrated production probability model, and not proof of general safety. It is a deterministic research method for selecting which mutable, action-specific prerequisites to revalidate under budget before committing a consequential action.

## A reference architecture for production

A robust implementation would separate five planes:

1. **Capability plane:** deterministic services, LLM functions, workflows, and agents selected according to problem complexity.
2. **Evidence plane:** typed claims, provenance, versioning, validity windows, dependency graphs, and authoritative connectors.
3. **Decision plane:** action manifest, invalidity estimator, risk/cost model, mandatory constraints, subset selection, and ACT/REFRESH/ASK/ABSTAIN policy.
4. **Execution plane:** transactional adapters, compare-and-set, idempotency, least privilege, postcondition checks, and compensation.
5. **Assurance plane:** traces, immutable ledgers, temporal fault injection, domain-stratified evaluation, prospective gates, and incident review.

This decomposition prevents the LLM from becoming the database, policy engine, authorization service, workflow coordinator, and safety monitor simultaneously.

## The engineering principle

The next generation of agentic systems will not be made reliable by context windows alone. Reliability will come from knowing which claims are mutable, which sources are authoritative, which constraints are non-negotiable, what must be checked at commit time, and when the only correct action is to stop.

The decisive system-design question is therefore not only:

> Does this problem need an agent?

It is also:

> What must still be true at the exact moment this agent is allowed to change the world?

## Source links

- RAER repository: https://github.com/khshaik/applied-ai-research-lab/tree/main/action-evidence-safety-research
- Karthika Vijayan, “Agentic AI: Building the Right Mental Model for System Design”: https://medium.com/inspiredbrilliance/agentic-ai-building-the-right-mental-model-for-system-design-269d85c1689f
- Franc et al. (2023): https://www.jmlr.org/papers/v24/21-0048.html
- Shim et al. (2018): https://proceedings.neurips.cc/paper/2018/hash/e5841df2166dd424a57127423d276bbe-Abstract.html
- Li and Oliva (2025): https://proceedings.mlr.press/v258/li25h.html
- Xu et al. (2026), BCEA: https://arxiv.org/abs/2606.16667
- Chao et al. (2026), STALE: https://arxiv.org/abs/2605.06527
- Tao et al. (2026), MemConflict: https://arxiv.org/abs/2605.20926
- Liu et al. (2026), AgentAbstain: https://arxiv.org/abs/2607.10059
- Luo et al. (2026), agentic abstention: https://arxiv.org/abs/2606.28733
- Liu et al. (2026), ToolGate: https://arxiv.org/abs/2601.04688
- Winston et al. (2026), solver-aided policy verification: https://arxiv.org/abs/2603.20449
- Ruan et al. (2024), ToolEmu: https://arxiv.org/abs/2309.15817
- Yao et al. (2024), tau-bench: https://arxiv.org/abs/2406.12045
- Lu et al. (2025), ToolSandbox: https://arxiv.org/abs/2408.04682
- Zhang et al. (2025), Agent-SafetyBench: https://arxiv.org/abs/2412.14470
- Mou et al. (2026), ToolSafe: https://arxiv.org/abs/2601.10156
- Liu et al. (2026), SafeAgent: https://arxiv.org/abs/2604.17562

#AgenticAI #ContextEngineering #AISafety #LLMOps #AgentArchitecture #ResponsibleAI #AIResearch #ToolUse
