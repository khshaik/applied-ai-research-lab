# Developmental Simulation Reconciliation

**Version:** 1.0  
**Date:** 15 August 2026  
**Status:** Reproduced developmental synthetic evidence; not locked evaluation
or empirical validation.

## 1. Reproducibility decision

The checked-in manifest `0.1.0-development` did not reproduce after the engine,
calendar, dependency, evidence, gate, queue, and comparator implementation had
been hardened. Its four output hashes and several comparator winners differed
from a fresh run. Those outputs and any result summaries derived from them are
retired.

The current pipeline was run twice independently using:

```text
python3 -m simulation.development_pipeline --replications 24 --output <directory>
```

The two fresh output directories were byte-identical. The reconciled checked-in
artifact contains 11 scenarios, 24 replications per scenario, and 264 runs. Its
manifest `0.2.0-development` records:

- configuration SHA-256:
  `6b2fd67b3b62fa42a2c18dd285fd312c0308fb1c63a55e6ec9a87700de9db48b`;
- implementation SHA-256:
  `61625c6203f6c90820f3acec3e98a167c830fd19351b46a21dc2215047e421e4`;
- manifest content checksum:
  `e198d4ee0905c4c91a7383cd593fd95848d2bacbac6db915aa6b498098a7425d`.

The complete before/after audit is
`simulation/output/development/reproducibility_audit_20260815.json`.

## 2. Comparator reconciliation

The table reports the lowest Brier score among the four deployable comparator
families in each developmental scenario. The oracle is excluded. These are
descriptive development-set comparisons; the pipeline does not provide the
paired uncertainty needed for a superiority decision.

| Scenario | Items scored | Lowest-Brier deployable model | Brier score | Interpretation |
|---|---:|---|---:|---|
| baseline_sp | 288 | HIE-compatible | 0.145997 | The nominally SP-sufficient label does not make Story Points best under the current illustrative configuration |
| baseline_hie | 288 | HIE-compatible | 0.105476 | Consistent with the task/oversight world label, but development-only |
| baseline_bottleneck | 288 | Proposed model | 0.120608 | Advantage over HIE-compatible is only 0.000453 and is not adjudicated as material |
| review_capacity_low | 576 | Proposed model | 0.220344 | Proposed representation performs best descriptively under this constrained-review scenario |
| review_capacity_high | 576 | HIE-compatible | 0.287817 | Added review capacity does not guarantee advantage for the more detailed model |
| load_low | 144 | HIE-compatible | 0.110432 | Simpler task/oversight representation is adequate in this scenario |
| load_high | 864 | Simple role load | 0.249521 | Explicit readiness detail does not outperform the simple role-load comparator |
| recovery_service_low | 288 | Proposed model | 0.151579 | Developmental recovery fixture, not an outcome-validity test |
| recovery_service_high | 288 | Proposed model | 0.142288 | Developmental recovery fixture, not an outcome-validity test |
| edge_no_rework | 288 | Story Points | 0.001022 | A scalar baseline can remain competitive in a low-complexity boundary case |
| edge_severe_queue | 1,152 | Simple role load | 0.161438 | The proposed model is not universally best even in a severe-queue scenario |

Winner frequency is therefore: proposed model 4/11, HIE-compatible 4/11,
simple role load 2/11, and Story Points 1/11. Winner counts are descriptive and
must not be used as a statistical ranking.

## 3. Parameter-recovery reconciliation

| Fixture | Target multiplier | Recovered multiplier | Absolute error |
|---|---:|---:|---:|
| recovery_service_low | 0.75 | 0.785693 | 0.035693 |
| recovery_service_high | 1.75 | 1.825802 | 0.075802 |

Historical errors `0.00865` and `0.02014` are not supported by the current
reproducible artifact and must not appear in the manuscript. The recovery
metric also combines the implemented service-event mix; it is an engineering
diagnostic, not evidence that organization-level parameters can be recovered.

## 4. Mechanism-ablation reconciliation

The prior ablation artifact used only `world_sp` and two replications. It is
retained as historical development output but is superseded for reporting by
`g4b_mechanism_ablation_v2_20260815`, which uses:

- three declared development worlds;
- four one-at-a-time mechanism removals: dependencies, multi-role structure,
  queues, and readiness;
- 24 paired replications per world/mechanism;
- 576 baseline/ablated run records and 12 effect rows; and
- only the `development:g4b_ablation` seed namespace.

Two independent v2 generations were byte-identical. The receipt checksums all
published files.

### 4.1 Effect diagnostics

`primary_delta` is the ablated minus baseline non-completion proportion. A
positive value therefore means the ablated configuration had more
non-completion in that development run.

| World | Mechanism removed | Primary delta | Role-load concentration delta |
|---|---|---:|---:|
| world_bottleneck | dependencies | -0.062500 | -0.005407 |
| world_bottleneck | multi-role structure | 0.093750 | -0.630194 |
| world_bottleneck | queues | 0.121528 | -0.003937 |
| world_bottleneck | readiness | 0.000000 | 0.000000 |
| world_hie | dependencies | -0.062500 | -0.005003 |
| world_hie | multi-role structure | 0.017361 | -0.629879 |
| world_hie | queues | 0.055556 | -0.008878 |
| world_hie | readiness | 0.000000 | 0.000000 |
| world_sp | dependencies | -0.017361 | -0.001184 |
| world_sp | multi-role structure | 0.128472 | -0.627645 |
| world_sp | queues | 0.072917 | -0.001685 |
| world_sp | readiness | 0.000000 | 0.000000 |

### 4.2 Ablation interpretation limit

The ablations are executable mechanism diagnostics, not isolated causal
effects. Removing a mechanism changes event ordering and therefore which
pseudorandom draws are consumed by later events. The same initial seed does not
guarantee entity/event-level common random numbers after the paths diverge.
Multi-role removal also changes resource topology and aggregate concurrency,
not merely one scalar feature. Readiness removal is null in these worlds because
the configured evidence state is not a binding differentiator.

Consequently, the paper may report that all four removals execute,
reconcile, and expose expected structural differences. It must not interpret
the numerical deltas as causal estimates of queue, readiness, dependency, or
multi-role value. A future simulation revision would need keyed random streams
and mechanism-specific estimands before making that comparison.

## 5. Defensible developmental finding

The current artifact supports only the following result statement:

> Across 11 illustrative development scenarios, no deployable comparator was
> uniformly best. The proposed model, the HIE-compatible comparator, a simple
> role-load comparator, and Story Points each achieved the lowest descriptive
> Brier score in at least one scenario. This mixed pattern identifies scenario
> boundaries and motivates prospective validation; it does not establish
> organizational superiority.

## 6. Remaining work before manuscript result use

1. derive uncertainty and calibration tables from the current artifact;
2. produce publication-ready figures with explicit synthetic labels;
3. add a parameter-use table distinguishing literature-supported, design, and
   illustrative inputs;
4. link every reported number to the manifest and claim ledger; and
5. retain the ablation and parameter-recovery limitations in the manuscript.

