# Route B Comparator, Seed-Locking, and Evaluation Specification

**Status:** Prototype implementation; agent-reviewed software evidence only  
**Interpretation boundary:** Nothing in this document demonstrates predictive validity for a real person, team, organization, or AI-assisted delivery process.

## Comparator contract

All deployable comparators receive only information available at the pre-commitment time point (`t0`) and are evaluated on identical generated portfolios using common random numbers.

| Comparator | Permitted information | Explicit exclusion |
|---|---|---|
| Story Points | Story Points and frozen historical point allowance | Role queues, readiness, realized outcomes |
| HIE-compatible | Story Points plus pre-task context, interaction, and oversight demand | Cross-role queues and runtime outcomes |
| Simple role load | Pre-commitment demand/capacity by role | Gates, readiness, rework transitions |
| Proposed model | Role loads plus pre-commitment readiness and rework risk | Realized service, gate, and completion outcomes |
| Oracle | Synthetic truth parameters | Not deployable and never a reference for a deployment claim |

The prototype formulas are deliberately transparent and frozen in `ComparatorParameters`. They are mechanism probes, not fitted empirical models. Any coefficient tuning must use development worlds only and produce a new version/hash before locked evaluation.

Task-only models abstain from bottleneck identification because assigning them a role prediction would manufacture unavailable information. Abstention counts are reported beside accuracy.

## Primary and secondary evaluation

The primary outcome is the Brier score for completion within the planning interval. Report absolute paired Brier improvement, relative Brier skill, Monte Carlo uncertainty, calibration tables, and expected calibration error. The current dependency-free interval is a normal interval over independent replication-level paired differences; portfolio clustering requires cluster-aware analysis before a formal evaluation.

Secondary metrics implemented at this gate are:

- bottleneck top-one accuracy with abstentions;
- cycle-time or queue-delay quantile absolute error;
- logarithmic loss as a diagnostic, not a replacement primary endpoint.

The provisional adjudicator retains the model only for future field testing when all preregistered synthetic conventions pass: relative skill at least 5%, absolute Brier improvement at least 0.01, interval excluding zero, positive direction in at least 80% of configurations, and bottleneck accuracy improvement of at least 10 percentage points. Failure produces `do_not_claim_advantage`; success does not establish organizational usefulness.

## Seed locking

`simulation/configs/locked_seed_manifest.json` commits to eight development and 24 evaluation seeds derived by SHA-256 namespaced streams from master seed `20260813`. Development and evaluation streams are disjoint and the canonical core payload is checksum-protected. Common random numbers are used across comparators.

The 24 locked evaluation seeds are sufficient to verify pipeline behavior, not the Gate 3B precision target. A preregistered production manifest must increase replications until the primary probability interval half-width is at most 0.01 and comparator-contrast precision meets the declared rule, or report precision as unresolved at the maximum.

## Hard-stop verification

Automated tests currently cover:

- configuration/schema loading and engine execution;
- fixed-seed event-hash identity;
- zero arrivals;
- effectively infinite capacity with zero queue waiting;
- no-failure/no-rework behavior;
- mandatory failure after the rework-loop limit;
- entity reconciliation;
- completed-item time conservation;
- probability bounds;
- seed checksum, uniqueness, and development/evaluation separation;
- comparator input isolation and oracle truth requirements;
- hand-calculated Brier, calibration, bottleneck, quantile, and adjudication examples.

Any failed hard stop invalidates the run. The results must not be interpreted or selectively repaired after evaluation seeds are opened.

## Remaining limitations and required work

- The comparator coefficients and synthetic truth parameters are illustrative.
- Calibration slope/intercept and cluster-aware uncertainty are not yet implemented.
- The engine still needs formal blackout, dependency, deadlock, Little's Law, capacity-monotonicity, and analytic stable-queue fixtures.
- Measurement overhead and fairness-by-work-class outcomes remain to be operationalized.
- Literature values require source-level extraction and transformations before they may replace illustrative inputs.
- Route A prospective organizational validation remains indispensable.
