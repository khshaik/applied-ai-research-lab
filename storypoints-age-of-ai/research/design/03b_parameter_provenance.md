# Gate 3B Parameter Provenance and Rejection Rules

## Provenance classes

| Class | Meaning | Permitted interpretation |
|---|---|---|
| E1 Direct empirical | Estimate directly extracted from a compatible observed study | Literature estimate with stated context/uncertainty; not local calibration |
| E2 Transformed empirical | Published value transformed to the model unit with reproducible formula | Derived literature input with transformation uncertainty |
| L Literature bounded | Range informed by multiple heterogeneous sources | Plausible exploration range only |
| X Expert elicited | Structured elicitation from qualified people | Unavailable until genuine experts participate |
| I Illustrative | Deliberately hypothetical stress-test value | Mechanism exploration only |

Every parameter records source study-family/URL, exact locator, population/context, original measure/unit, transformation, distribution choice, bounds, uncertainty, applicability limits, extractor/verifier, and version/hash.

For `production_calibration`, an E1/E2 registry label is insufficient. Each
active empirical parameter must reference `evidence_extraction_id` in a frozen,
schema-valid, finally reconciled Gate 2 evidence bundle. That extraction must
be agent-verified, linked to an included study family, and explicitly confirmed
by an accountable author as supporting the cited claim at the exact locator.
The registry must also include a confirmed `transformation_audit` recording the
formula, input/output units, verifier agent, and accountable author. Prelock
loads the checksummed `evidence_review_bundle` artifact and fails closed if any
link or audit is absent. Class-I development values are not promoted.

## Route B acceptance/rejection criteria

These judge software/model credibility, not organizational validity:

1. all deterministic toy cases reproduce hand calculations within `1e-9` for exact arithmetic or the documented numerical tolerance;
2. entity/time conservation has zero unexplained loss or duplication;
3. fixed-seed runs reproduce identical event/output hashes in the declared environment;
4. simplified stable queues agree with applicable analytic checks within a prespecified Monte Carlo interval;
5. replication count is increased until the primary outcome Monte Carlo 95% interval half-width is at most 0.01 and the comparator-contrast half-width is no more than 10% of its preregistered smallest effect of interest, subject to a declared maximum such as 50,000 replications; unresolved precision is reported as unresolved;
6. capacity monotonicity holds in isolated tests unless a declared secondary bottleneck explains the result;
7. parameter-recovery intervals contain the generating value at their intended long-run rate in repeated synthetic experiments;
8. central conclusions must survive alternative plausible distribution families and global sensitivity analysis;
9. reject decision-use claims when a simpler comparator is practically equivalent, conclusions reverse under small plausible perturbations, or measurement-overhead assumptions exceed modeled benefit;
10. in Story-Point-sufficient and HIE-sufficient worlds, the proposed model must be allowed to show no advantage.

For the locked synthetic evaluation, provisional design conventions are: relative Brier skill of at least 5% versus the strongest deployable comparator; a 95% Monte Carlo interval excluding zero; direction retained in at least 80% of plausible configurations; and at least 10 percentage-point improvement for bottleneck identification. Prefer the simpler model when absolute Brier improvement is below 0.01, its interval includes zero, or performance lies within one Monte Carlo standard error. Treat the framework as unstable if the central conclusion reverses in more than 20% of plausible configurations. These are preregistered engineering conventions, not evidence of real organizational usefulness.
