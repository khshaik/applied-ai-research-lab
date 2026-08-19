# Locked Synthetic Evaluation Preregistration and Opening Checklist

**Document status:** Draft, preregistration-ready but not locked  
**Seed status:** the checked-in 24-seed manifest is prototype-only and must not be reused for production evaluation; a fresh independently sealed production set is required after all other contracts freeze  
**Interpretation boundary:** This is a synthetic mechanism evaluation. Passing it does not validate human cognition, organizational usefulness, or causal effects of AI-assisted development.

## Frozen research question

Under the prespecified synthetic worlds, does the proposed role- and readiness-aware model forecast completion within the planning interval and identify binding role constraints more accurately than the strongest deployable comparator, while remaining robust to plausible perturbations?

The primary endpoint is paired item-level Brier-score improvement for **strict verified completion** within the planning interval. Only terminal state `completed` is coded as an event. `completed_with_residual_risk`, `failed`, `dependency_failed`, and `censored` are coded as non-events because unresolved residual risk is not unconditional verification. The strongest deployable comparator is selected by aggregate Brier score from Story Points, HIE-compatible, and simple role-load models. The oracle is diagnostic and cannot be selected as the deployment reference.

A mandatory, non-adjudicating sensitivity analysis named `conditional_completion_inclusive` recodes both `completed` and `completed_with_residual_risk` as events, retains `failed`, `dependency_failed`, and `censored` as non-events, and repeats item-level Brier scoring, strongest-deployable selection, paired contrast, calibration, and threshold reporting. It must be published beside the primary result but cannot reverse or replace the primary adjudication.

## Hypotheses and adjudication

The proposed model advances only to prospective Route A testing when all preregistered synthetic conventions hold: relative Brier skill is at least 5%; absolute Brier improvement is at least 0.01; the paired 95% Monte Carlo interval excludes zero in the favorable direction; direction is retained in at least 80% of plausible configurations; and bottleneck top-one accuracy improves by at least 10 percentage points.

Prefer the simpler model when absolute Brier improvement is below 0.01, its interval includes zero, or performance is within one Monte Carlo standard error. Label the mechanism unstable when the central conclusion reverses in more than 20% of plausible configurations. Reaching the replication maximum without satisfying precision yields `precision_unresolved` and prohibits an advantage claim.

## Analysis and precision lock

- Use identical portfolios and common random numbers for every comparator within a replication.
- Use only declared `t0` fields for deployable comparators; realized truth is restricted to scoring and the oracle.
- Increase replications in fixed batches from the declared minimum to a maximum of 50,000.
- Require a 95% primary interval half-width no greater than 0.01 and a comparator-contrast half-width no greater than 10% of the smallest effect of interest.
- Freeze the interval estimator, clustering unit, calibration procedure, missing-output rule, and strongest-comparator selection implementation before opening seeds.
- Retain null, adverse, equivalence, abstention, and failed-hard-stop results.
- Report the prespecified conditional-completion-inclusive sensitivity even when no conditional completion occurs; label it sensitivity evidence, not the primary endpoint.

The machine-readable contract is `simulation/preregistration/locked_evaluation_protocol.json`. It fixes artifact hashes, decision rules, precision targets, and mandatory output tables. The current draft deliberately contains visible pending fields so the checker refuses authorization until the code release and independent review are frozen.

## Hard-stop opening checklist

Run these in order. Do not run the locked evaluation if any command or review item fails.

1. Run the complete test suite with `python3 -m simulation.test_runner`.
2. Freeze a clean, identifiable code release. Archive both the release artifact and a JSON release manifest that cross-references its SHA-256; declare and verify hashes for both files.
3. Recompute checksums for configuration, schema, and seed-manifest files; update the contract only through documented change control.
4. Complete an independent agent or human code/protocol review. Archive a real JSON review record and its SHA-256. The record must attest independence, cover code/protocol/hard stops, reference the same code-release artifact hash, and confirm that evaluation seed values were not accessed. An agent review is software/protocol evidence, not human construct validation.
5. Create a fresh production seed set through an independently controlled sealing process. The checked-in prototype manifest is explicitly ineligible because automated tests parse it. Confirm the fresh values have not been opened, logged, summarized, profiled, or used for tuning.
6. Replace the prototype seed policy with a sealed `production_locked_do_not_tune` policy whose declared capacity covers the maximum replication rule. Require a separately hash-locked external seal record created after both the release freeze and independent review; it must cross-reference the opaque seed artifact without disclosing its values. Do not inspect or print seed values while making this metadata change.
7. Freeze a dedicated production runner and a no-seed readiness record. The readiness record must hash the runner and cover exactly the locked worlds and every mandatory output ID.
8. Replace all pending fields, set `status` to `locked`, and record `locked_at_utc`.
9. Run `python3 -m simulation.prelock`; a zero exit status and `ready_to_open` are mandatory. The checker must independently verify real file hashes/content, locked-world consistency, production runner coverage, and clean root-contained output destinations.
10. Archive the preregistration protocol and its checksum outside the result directory before evaluation begins.
11. Execute the locked runner once. A hard-stop failure invalidates interpretation; it must not be selectively repaired and rerun under the same lock.
12. Verify that every file and field in the output contract exists, then publish null and adverse findings with successful findings.

## Production runner architecture

`simulation.locked_runner` is the sole production orchestration entry point. Its normal execution path calls the full prelock checker before accepting control from a seed-capable batch executor. It collects fixed replication batches, evaluates both preregistered Monte Carlo half-width rules, stops only at an eligible batch boundary or the replication maximum, and emits calibration, uncertainty, robustness, adjudication, provenance, and hard-stop records with the item/run outputs.

The runner validates all output payloads against the immutable contract before publication and refuses to overwrite any existing target. `python3 -m simulation.locked_runner --readiness-record` builds only public runner/world/output metadata; it has no seed-path parameter and does not open the sealed seed artifact. The checked-in CLI has no sealed executor installed and therefore cannot execute locked worlds accidentally.

Primary-endpoint precision and paired-contrast precision are separate rows and separate stopping conditions. Synthetic advancement requires every threshold—not merely a favorable interval—to pass: 5% relative Brier skill, 0.01 absolute improvement, favorable paired interval, 80% robustness, and a 10-percentage-point bottleneck-accuracy gain. Publication occurs only after cross-table key reconciliation and staged SHA-256 verification; a `publication_receipt` records all output hashes and reconciliation counts.

The runner maps terminal states rather than trusting a caller-supplied binary outcome. The primary event is strictly `completed`; residual-risk completion is a non-event. A mandatory `conditional_completion_inclusive` report repeats Brier scoring, reference selection, paired contrast, calibration and threshold reporting with residual-risk completion included as an event. It is a sensitivity only: the report must retain a verified hash and snapshot of the unchanged primary adjudication.

## Change control after lock

Any post-lock change to code, configuration, schema, seeds, comparator formulas, endpoint definitions, uncertainty method, thresholds, or output contract creates a new protocol version and hash. If evaluation values have been opened, the affected run becomes exploratory and a fresh, independently locked evaluation set is required. Defect corrections must preserve the failed run and its audit record.

## Deferred validation

Route A remains required for calibration, predictive validity, practitioner usability, human cognitive-load claims, fairness assessment, and organizational transfer. Synthetic success is only a warrant to conduct that future study.
