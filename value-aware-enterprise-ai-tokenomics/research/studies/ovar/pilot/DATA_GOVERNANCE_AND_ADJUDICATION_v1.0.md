# Pilot Data Governance and Adjudication v1.0

## Public and restricted layers

The public reviewer layer contains the outcome contract, measurement fields, costs, evidence descriptors, and policy inputs. The restricted investigator layer contains true incremental value, true cost, true expected harm, reference uncertainty, evidence sufficiency, reference ROI state, and reference action.

Restricted labels must never be given to reviewers scoring clarity, evidence sufficiency, or construct validity. A future public release may reveal labels only after every prospective gate and any held-out evaluation are complete.

## Minimum privacy rule

The pilot uses fictional organizations and constructed values. A later field study must exclude raw prompts, personal identifiers, individual employee surveillance fields, confidential text, credentials, and unrestricted evidence URIs from the minimum public ledger. Public records should use pseudonymous organizational and trace identifiers, aggregated costs, evidence hashes, access controls, and documented retention periods.

## Reviewer roles

Two independent reviewers should assess the reviewer-visible package:

- Reviewer A: finance, causal attribution, and accounting completeness;
- Reviewer B: operations, risk, and evidence auditability.

They should not see policy outputs, reference labels, the other review, aggregate results, or investigator adjudication. Synthetic reviewers may be used only as pre-review stress tests and must not be reported as human inter-rater reliability.

## Required reviewer fields

For every case, reviewers record 1–5 scores for outcome-contract clarity, baseline credibility, evidence auditability, cost-boundary completeness, attribution defensibility, and decision realism. They also provide a leakage flag, ambiguity flag, missing-information note, and concise rationale for scores of 1 or 5.

## Adjudication

Disagreements remain visible. The coordinator records the original values, disagreement reason, final adjudicated value, adjudicator identity, date, and rationale. Scores must not be averaged automatically. Any case content revision produces a new candidate version and invalidates prior hashes.

## Evidence and provenance

Each constructed case records its authoring version and `CONSTRUCTED` provenance. No number should be described as an observed market fact. Future empirical records require a source URI or controlled locator, source hash where permitted, collection time, evaluator, and evidence-access classification.
