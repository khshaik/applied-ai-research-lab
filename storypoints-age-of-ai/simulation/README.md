# Route B simulation prototype

This package operationalizes the Gate 3B design as a deterministic, auditable
prototype. It evaluates synthetic mechanisms; it does **not** validate human
cognitive load, a real organization, or causal effects of AI.

## Three layers

1. `engine.py` is the synthetic-truth layer. It realizes arrivals, explicit
   role queues, effective-capacity calendars and blackouts, template-level
   portfolio dependencies, stage service, gate evaluation, bounded rework,
   and terminal outcomes from a private data-generating world.
2. `comparators.py` consumes declared pre-commitment fields and must not use
   runtime event outcomes or private truth parameters.
3. `evaluation.py` scores comparator forecasts against realized records.

Frozen dataclass tuples are the authoritative in-memory output tables. The
plain-record adapter returns copies, preventing comparators from mutating truth.
No external system is read or written.

## Validate and test

The example is JSON-compatible YAML, so it loads with the Python standard
library when PyYAML is unavailable. The dependency-free validator implements
the JSON Schema keywords used in `research-design/03b_simulation_schema.json`, then checks
cross-document references and probability sums.

Run the complete suite through the unified runner. It discovers both project
test roots and fails if either root is missing:

```bash
python3 -m simulation.test_runner
```

Run the synthetic development suite (development seed namespace only):

```bash
python3 -m simulation.development_pipeline --replications 24
```

The runner writes a checksummed development manifest plus run, item-forecast,
comparator-score, and parameter-recovery CSV files under
`simulation/output/development`. It refuses scenarios that reference a world
outside `experimental_design.development_world_ids` and does not read the
locked evaluation seed manifest.

Manifest version `0.2.0-development` also records canonical configuration and
source-file implementation hashes. The 15 August 2026 reconciliation is
recorded in
`simulation/output/development/reproducibility_audit_20260815.json`; it retires
older, non-reproducing developmental output claims.

## Interpretation and prototype limits

- Values in `configs/example.yaml` are class `I` (illustrative).
- The engine currently accepts a fixed portfolio, sequential stages, FIFO
  queues, one primary role per stage, and the declared distribution families.
- Simulation time starts at the earliest capacity-interval timestamp. Each
  interval is an explicit open window whose timestamp duration must equal both
  `gross_hours` and `effective_hours`; absence and non-project hours must be
  zero. Closures must be explicit gaps or blackouts. Touch time remains
  one-for-one inside open windows and `calendar_pause` records closure time
  separately, preventing a second effective/gross multiplier. Role service
  slots are multiplied by calendar concurrency.
- A fixed portfolio may declare `parameters.template_ids`. A dependency edge
  `[A, B]` means every B-template item waits for all A-template items to
  complete successfully. This intentionally conservative template-level rule
  does not represent arbitrary item-to-item links. The model must explicitly
  freeze all-predecessors-successful release, block-successor failure handling,
  and template-all-to-all scope. Every cycle is a hard error; a failed
  predecessor produces a distinct blocked state.
- Priority queues, correlated draws, evidence expiry, item-level dependencies,
  split/preemptive staffing, daily shift reconstruction, and parallel stage
  service remain outside the implemented minimum scope and must not be implied
  by a locked evaluation claim.
- A locked run requires real commit and configuration checksums, independently
  reviewed parameters, and the completed preregistration.

## Locked-evaluation hard stop

The draft machine-readable protocol is
`simulation/preregistration/locked_evaluation_protocol.json`; the review and
opening procedure is in `research-design/04_locked_synthetic_preregistration.md`. Before any
evaluation seed is opened, run:

```bash
python3 -m simulation.prelock
```

The checked-in draft is expected to return `hard_stop_not_ready` until a clean
code release and independent review record have been frozen. Do not weaken or
bypass those failures to obtain results.

The production control plane is `simulation.locked_runner`. Generate its
seed-free readiness metadata with:

```bash
python3 -m simulation.locked_runner --readiness-record
```

Normal execution remains fail-closed until the protocol, release, independent
review, externally sealed production seed artifact, runner readiness record,
and clean output destinations all pass prelock. The checked-in runner does not
include a seed executor and cannot generate production seeds.
