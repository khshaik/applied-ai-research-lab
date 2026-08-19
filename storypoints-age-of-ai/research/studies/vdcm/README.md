# VDCM Study

**Verified Delivery Capacity Model (VDCM)** is a prospective role-stage resource and flow model for AI-assisted software delivery. Its elicitation artifact is the proposed **Role–Stage Demand and Readiness Instrument (RSDRI)**.

## Research question

Can pre-commitment role-stage demand, capacity, readiness, and queue information improve forecasts of verified completion, constrained-role delay, and quality-aware delivery outcomes beyond Story Points and HIE-compatible baselines?

## Current route

- **Route B now:** access-constrained evidence map, design-science artifact, and developmental discrete-event simulation.
- **Route A later:** prospective multi-team shadow-mode validation using genuine practitioners and organizational event data.

## Scientific boundaries

- Human touch demand is active work time, not a psychological measure of attention.
- Queue delay is modeled separately from active touch time.
- Story Points and HIE remain comparators, not strawman baselines.
- Synthetic results are conditional mechanism evidence only.
- Production evaluation remains blocked until all pre-lock controls pass.

## Navigation

- [`protocol/README.md`](protocol/README.md): concept, constructs, causal model and propositions.
- [`evidence-map/README.md`](evidence-map/README.md): Gate 2 protocol, source matrix and screening status.
- [`simulation/README.md`](simulation/README.md): DES, comparators and preregistration status.
- [`integrity/README.md`](integrity/README.md): current hard stops, claims and release boundary.
- [`restricted/README.md`](restricted/README.md): excluded-material policy.

## Verification

```bash
python3 -m simulation.test_runner --quiet
python3 scripts/verify_repository.py
```

