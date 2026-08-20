# Adjudication and Revision Decision v1.0

## Decision

Authorize the single protocol-permitted **clarity-only revision**. Do not alter policy rules, decision thresholds, costs, usage, quality, observed outcomes, baseline estimates, evidence status, baseline class, attribution confidence, uncertainty, harm cost, compliance status, access class, hidden reference data, or case identifiers.

## Evidence supporting revision

The two isolated synthetic reviewers converged on five systemic issues:

1. outcome contracts often lacked numeric acceptance thresholds;
2. baseline labels lacked implementation details;
3. evidence statuses lacked locators and reproduction notes;
4. `PARTIAL` evidence did not identify the missing component;
5. valuation, harm, and cost-allocation provenance was insufficiently explicit.

Sixteen cases met the frozen adjudication rule. No reviewer score is averaged or silently replaced.

## Adjudication of possible leakage

`compliance_status = PROHIBITED` and `exploration_protected = true` are retained. They are intentional, prespecified decision inputs required to test compliance safeguards and protected exploration. They are not investigator reference labels. Their mechanical influence must nevertheless be disclosed, and future performance analyses must include ablations with these safeguards removed.

## Authorized additions

- numeric acceptance criteria;
- baseline implementation note;
- constructed evidence locator and reproduction note;
- explicit partial-evidence gap;
- value, cost-allocation, and harm-method notes;
- explicit decision checkpoint.

The revision produces candidate v1.1. It does not erase candidate v1.0 or the original reviews.
