# Initial Novelty Audit v0.1

**Search date:** 12 August 2026  
**Status:** provisional scoping audit; not a systematic review and not proof of global novelty

## Audit conclusion

The broad proposal—enterprise AI tokenomics, AI ROI, hierarchical cost allocation, dynamic budgets, or carry-forward—is not sufficiently novel as stated. Close 2026 papers and current FinOps practices already address token economics, enterprise allocation, marginal token allocation, ROI selection, and transferability. Open-source platforms already implement much of the telemetry and budget-control layer.

The concept should proceed only with this bounded contribution:

> A prospectively evaluated outcome-verification and allocation protocol that reconciles heterogeneous AI resource cost with independently evidenced incremental workflow value, then applies risk-adjusted marginal allocation across a hierarchical internal budget with explicit reserve, access, uncertainty, and anti-gaming constraints.

This is a proposed combination and evaluation design, not yet an established novelty claim.

## Closest scholarly work

| Work | Existing contribution | Boundary for OVAR |
|---|---|---|
| [AI Tokenomics: The Economics of Tokens, Computation, and Pricing in Foundation Models](https://arxiv.org/abs/2606.24616) | Connects token costs to workflow production, enterprise allocation, value, and marginal productivity | OVAR cannot claim this conceptual bridge; it must operationalize prospective outcome verification and evaluate a governance policy |
| [Token Economics for LLM Agents](https://arxiv.org/abs/2605.09104) | Unifies computing and economics across single-agent, multi-agent, ecosystem, and security levels | OVAR is not a new general theory of token economics |
| [Agentic AI Systems Should Be Designed as Marginal Token Allocators](https://arxiv.org/abs/2605.01214) | Frames agent layers through marginal benefit, cost, latency, and risk | OVAR cannot claim marginal allocation itself; it must test organization-level allocation using verified outcomes and hierarchy constraints |
| [Tokenomics: Quantifying Where Tokens Are Used in Agentic Software Engineering](https://arxiv.org/abs/2601.14470) | Measures token distribution across multi-agent software-development stages | OVAR shifts from consumption location to outcome evidence, portfolio allocation, and realized value |
| [How Do AI Agents Spend Your Money?](https://arxiv.org/abs/2604.22750) | Shows large token variability, weak prediction, and that more tokens need not improve accuracy | Supports the premise; OVAR must not present that premise as its discovery |
| [Towards Optimizing the Costs of LLM Usage](https://arxiv.org/abs/2402.01742) | Optimizes model selection and token reduction under quality, cost, and latency objectives | OVAR is not a routing or token-reduction method; comparison should include such a baseline |
| [AI Strategy: How to Choose What AI Product to Implement](https://arxiv.org/abs/2607.23733) | Expected-ROI decomposition into value if successful, likelihood, and investment | OVAR cannot claim AI project selection by expected ROI; it adds trace-to-outcome measurement and allocation feedback |
| [Transferability of Token Usage Rights](https://arxiv.org/abs/2604.26683) | Studies carry-over, co-management, transfer, conversion, and trade of token usage rights | Carry-forward and pooling are prior concepts; OVAR treats them as internal allocation mechanisms subject to contracts |
| [NIST AI RMF Core](https://airc.nist.gov/airmf-resources/airmf/5-sec-core/) | Requires defined business context, benefits, costs, benchmarks, risk tolerance, measurement, and governance | OVAR should align with these outcomes and avoid claiming general AI governance novelty |

## Closest practice and implementation work

| Source | Existing capability | Boundary for OVAR |
|---|---|---|
| [FinOps for AI](https://www.finops.org/framework/technology-categories/ai/) | Allocation, forecasting, optimization, governance, usage, cost, and business-value alignment | OVAR must provide an empirically testable method beyond general FinOps guidance |
| [GenAI cost and usage tracker](https://www.finops.org/wg/how-to-build-a-generative-ai-cost-and-usage-tracker/) | Token-based cost tracking and attribution across use cases | Tracking and attribution are inputs, not contributions |
| [Token Economics for SaaS model costs](https://www.finops.org/wg/token-economics-saas/) | Visibility, allocation, unit cost, optimization, budgets, and governance | OVAR must distinguish verified incremental value and policy evaluation |
| [LiteLLM](https://github.com/BerriAI/litellm) | Gateway, virtual keys, spend tracking, guardrails, routing, and logging | Potential telemetry adapter or comparator; do not rebuild or claim these capabilities |
| [Langfuse](https://github.com/langfuse/langfuse) | LLM observability, evaluation, metrics, traces, prompts, and datasets | Potential trace/evaluation source |
| [OpenLIT](https://github.com/openlit/openlit) | OpenTelemetry-native observability, GPU monitoring, guardrails, and evaluation | Potential interoperable instrumentation layer |
| [Opik](https://github.com/comet-ml/opik) | Tracing, evaluation, monitoring, and optimization | Potential interoperable instrumentation layer |
| [OpenInference](https://github.com/Arize-ai/openinference) | OpenTelemetry conventions and instrumentation for AI applications | Candidate common trace vocabulary |

## Claims prohibited at this stage

Do not claim that this project is the first to provide:

- AI tokenomics;
- value per token or value per dollar;
- marginal token allocation;
- enterprise AI ROI;
- hierarchical allocation, showback, or chargeback;
- dynamic budgets, pooling, transfer, or carry-forward;
- token/cost tracking or observability;
- quality-aware model routing;
- agent-loop or context optimization;
- POC stage gates.

## Formal audit still required

1. Define databases, date ranges, query strings, inclusion/exclusion criteria, and deduplication rules.
2. Review at least 30–40 closest sources, including cited and citing work.
3. Search patents, standards, working papers, dissertations, and active open-source implementations.
4. Compare constructs, inputs, objective functions, allocation levels, outcome verification, causality, risk, fairness, and evaluation evidence.
5. Maintain a claim-to-source ledger and quotation log.
6. Produce a one-page decision memorandum with `GO`, `NARROW`, or `PIVOT`.

