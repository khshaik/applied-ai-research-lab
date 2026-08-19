# C08 bounded S1/S2 integrative controls

Status: **complete for developmental query control; not a systematic corpus**

The approved minimum route assigns S1 only to Semantic Scholar and S2 only to
OpenAlex. These searches bridge the focused S3–S8 families and do not recreate
an exhaustive source-by-family matrix.

## S1 — human effort and work redistribution

The accepted v0.3 Semantic Scholar export is complete at **331/331** records.
Its deterministic 50-record metadata appraisal found **16 likely relevant**,
**3 uncertain**, and **31 likely irrelevant** records (38.0%
relevant-plus-uncertain). Both positive and both neutral/disconfirming controls
were recalled; `freeze_ready=true` at developmental query-control level.

## S2 — lifecycle validation and readiness

The v0.2 OpenAlex discovery component is complete at **257/257** records. Its
deterministic 50-record appraisal found **38 likely relevant**, **6 uncertain**,
and **6 likely irrelevant** records (88.0%). It recalled Agile V and the
lifecycle-error counterexample but missed the predeclared orchestration study
because that title lacks the assurance term required by the discovery clause.

Before the final rerun, v0.3 prospectively added one exact-title recovery
clause. OpenAlex then returned HTTP 429 through the bounded retry policy and no
partial artifact was published. The recovery clause is nevertheless verified
against two immutable OpenAlex records already archived in the complete,
checksum-bound S6 developmental export. C08 therefore accepts a **bounded
integrative union**: the 257-record discovery component supplies the burden
appraisal; the predeclared exact-title component supplies known-item recovery
only and adds no claimed discovery yield.

This is not described as a fresh OA-S2I3 execution. D05 must rerun the frozen
union into the systematic corpus when the public API is reachable. The
machine-readable decision and exact hashes are in
`gate2/output/development/c08_bounded_union_acceptance_20260816.json`.
