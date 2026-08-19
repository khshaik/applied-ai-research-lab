# Simulation Workspace

The executable Route B package remains at [`../../../simulation/`](../../../simulation/) because its paths are embedded in tests, manifests, and the draft locked-evaluation protocol.

## Implemented

- role-stage touch demand and capacity;
- FIFO queues with separate service, waiting, blocking, and calendar-pause accounting;
- executable calendars and blackouts;
- finish-to-start dependencies and failure propagation;
- evidence production, freshness, invalidation, and regeneration;
- risk-applicable gates, bounded rework, and residual-risk outcomes;
- Story Points, HIE-compatible, simple role-load, proposed, and oracle comparators;
- development sensitivity and mechanism ablations;
- fail-closed pre-lock and locked-runner contracts.

## Boundary

All current parameter values remain developmental unless a machine-verifiable evidence record promotes them. Production seeds and locked worlds must not be opened until `python3 -m simulation.prelock --json` returns `ready_to_open`.

## Commands

```bash
python3 -m simulation.test_runner --quiet
python3 -m simulation.prelock --json
```

