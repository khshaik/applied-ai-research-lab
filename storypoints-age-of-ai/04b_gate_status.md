# Gate 4B Status — Minimum Production DES

**Date:** 14 August 2026  
**Decision:** Engineering conformance passed; production release not authorized  
**Production evaluation:** Not authorized

## Completed

- Scope baseline `G4B-MPS-001` freezes the minimum mechanism set and explicit exclusions.
- Executable UTC role-capacity calendars, effective-capacity reconciliation and blackout pause/resume are implemented.
- Finish-to-start template dependencies, predecessor release/failure handling, cycle rejection and deadlock detection are implemented.
- Required-evidence presence, same-run freshness, readiness, invalidation and supported regeneration behavior are enforced.
- FIFO, non-preemptive role queues preserve separate service, queue and dependency-blocking records.
- A fail-closed production runner implements fixed batching, dual precision stopping, calibration, comparator scoring, uncertainty, robustness, adjudication, provenance and immutable output publication.
- Primary-endpoint and paired-contrast Monte Carlo precision are calculated and stopped independently; neither can be hidden by a single minimum target.
- Gate 4B adjudication requires all six conditions: resolved precision, at least 5% relative Brier skill, at least 0.01 absolute Brier improvement, favorable confidence interval, at least 80% positive plausible configurations, and at least a 10-percentage-point bottleneck-accuracy gain.
- Outcome coding is executable and strict: only `completed` is a primary event. The mandatory `conditional_completion_inclusive` sensitivity additionally treats `completed_with_residual_risk` as an event and separately reports Brier scores, strongest reference, paired contrast, calibration and thresholds. Its output stores and reconciles the immutable primary-adjudication hash, so it cannot replace or alter the primary result.
- Queue-area verification includes unmatched queue entries through the finite horizon; a dedicated fixture confirms horizon-censored items remain explicitly included in the queue-length integral.
- Locked output publication reconciles run, item, model, score, calibration, robustness and uncertainty keys; stages the complete common output directory; verifies per-file SHA-256 hashes; and publishes a checksum receipt through one fail-clean directory rename.
- A separate development-only mechanism-ablation generator executes same-seed baseline/ablated pairs for queues, readiness, dependencies and multi-role structure. Each mutator records exact changed paths, accepts only a `development:*` namespace and declared development worlds, and emits an immutable four-file package (manifest, pair observations, effects and checksum receipt). These diagnostics cannot be interpreted as locked evidence.
- The pre-lock contract requires a real release artifact, independent review record, fresh externally sealed production seed artifact, seed-free runner-readiness record and initially absent output targets.
- Unified verification passes **136 tests**, including Gate 2 search-export, search-coverage, evidence-review and parameter-provenance controls.
- A machine-readable parameter registry uniquely covers 102 active execution, comparator and decision-rule paths. Illustrative development values remain usable, while prelock now hard-stops production calibration until active calibration/comparator records have verified E1/E2 provenance and reproducible transformations.
- Final independent agent audit passes all **19 engineering-testable Gate 4B controls**. `G4B-PRE-01` remains failed solely because the production release package is intentionally not locked or ready.
- No production seed was generated, opened, inspected or used, and no locked world was executed.

## Evidence work added

Focused primary-source discovery added three candidate evidence records:

- industrial LLM-assisted review evidence showing that elapsed pull-request closure may increase even when automated comments are useful;
- an 8,106-PR study identifying testing failures among common non-integration reasons;
- a 33,000-PR study connecting non-merge outcomes with larger changes, files touched, CI outcomes and review dynamics.

These are mechanism anchors only. None has been converted into an active-time distribution or universal multiplier.

Gate 2 now also has executable development-only infrastructure:

- a full-pagination arXiv Atom exporter with raw-page and normalized-export checksums, sentinel validation, duplicate/offset/total-volatility hard stops and atomic publication;
- split S5 review, testing/QA and security query families plus the revised S6R lifecycle family;
- a machine-validated two-agent screening, adjudication, study-family, extraction-verification and PRISMA reconciliation bundle;
- a machine-readable registry covering all 102 active simulation parameter paths.

Developmental arXiv retries are archived with verified checksums: AX-S6R 29/29, AX-S5R 187/187, AX-S5T 394/394 and AX-S5S 1,333/1,333. The S6R and S5R sentinels passed. These 1,943 records are volatile API query totals, not eligible-study, frozen-search or PRISMA counts. All active calibration and comparator inputs remain class-I illustrative values; production calibration fails closed through `parameter_provenance`.

## Current hard stop

`simulation.prelock` returns `hard_stop_not_ready`. The following remain deliberately unfulfilled:

- final placeholder-free locked protocol and timestamp;
- frozen release artifact and matching checksums;
- verified E1/E2 provenance for production calibration inputs;
- final independent review record;
- fresh externally sealed production seed artifact and capacity declaration;
- hash-matched production runner readiness record;
- initially absent, writable locked-output destinations.

The checked-in prototype seed manifest remains ineligible for production evaluation.

## Next actions

1. finish accessible systematic searches and source-level parameter extraction;
2. replace remaining illustrative production parameters or bound them as sensitivity ranges;
3. freeze the placeholder-free protocol and production configuration;
4. package a clean release and obtain an independent review of its exact hash;
5. externally register the locked protocol;
6. create a fresh independently sealed production seed set;
7. create the hash-matched runner/output-readiness records;
8. require `ready_to_open` before a single locked-world execution.

Route A human and organizational validation remains future work.
