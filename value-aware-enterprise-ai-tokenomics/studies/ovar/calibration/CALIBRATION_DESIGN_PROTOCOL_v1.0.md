# OVAR Prospective Calibration Design Protocol v1.0

**Status:** design protocol; policy execution prohibited until package lock  
**Relationship to pilot:** new design informed by, but not a revision of, the closed 24-case engineering pilot  

## 1. Purpose

Create 48 new constructed calibration cases to evaluate whether OVAR's evidence requirements and decision receipts remain useful outside the authored engineering cases. The 24 pilot cases and their labels are not reused.

## 2. Coverage

Eight cases are constructed in each domain: healthcare, financial services, e-commerce, transportation/logistics, cybersecurity, and customer operations. Each domain must include:

1. high verified value with moderate usage;
2. high usage with negative or neutral incremental value;
3. positive technical quality but hidden fully loaded cost;
4. weak or absent counterfactual evidence;
5. delayed or shared outcome attribution;
6. a genuine compliance/authorization constraint described as a factual record, not a decision label;
7. low adoption with credible high value;
8. a difficult revise-versus-indeterminate boundary.

## 3. Separation of roles

- Case constructors create reviewer-visible facts only and do not see policy code, pilot results, or investigator reference labels.
- An independent reference adjudicator receives the completed visible cases and this protocol, but not policy code or comparator outputs.
- Construct reviewers receive only the neutral construct-review view.
- Policy execution uses a separate policy-input view after construct review and package freeze.

## 4. Three-view architecture

1. **Construct-review view:** outcome, baseline implementation, evidence provenance, cost boundary/method, attribution rationale, risk facts, and decision setting. It excludes categorical fields named `PROHIBITED`, `exploration_protected`, `reference_*`, `true_*`, or language declaring a positive/negative decision.
2. **Policy-input view:** numeric and categorical inputs required by each registered policy. Factual authorization/compliance evidence is represented as scoped documents, dates, and conditions rather than preferred-action labels.
3. **Restricted reference view:** true incremental value, true fully loaded cost, true harm, sufficient-evidence determination, and reference decision.

The three views share only immutable case IDs and explicitly mapped source fields.

## 5. Neutral-language rule

Reviewer-visible text must not include: `prohibited`, `must stop`, `must scale`, `positive ROI`, `negative ROI`, `cannot support a positive`, `attribution capped`, `preferred policy`, `reference decision`, or synonymous outcome declarations. Missing and partial evidence may be described factually because evidence insufficiency is itself a construct under study.

## 6. Reference adjudication

Reference adjudication is independent of policy implementation. It uses hidden constructed ground truth and the frozen reference rule. Every label receives a concise rationale and arithmetic reconciliation. The target is balanced coverage, not an OVAR-favorable distribution.

## 7. Pre-execution gates

Before any policy comparison:

1. exactly 48 unique cases and eight per domain;
2. all eight strata represented in every domain;
3. decision-bearing costs reconcile;
4. no forbidden label keys or decision-cue phrases in construct-review text;
5. no case-ID or field-order shortcut predicts reference decisions above a prespecified chance-tolerance check;
6. two synthetic construct stress tests report no blocking issue; these are not human validation;
7. all policy field whitelists and decision receipts pass tests;
8. files, code, dependencies, and hashes are locked before execution.

## 8. Calibration gate

Thresholds will be registered in a separate prospective analysis plan before reference labels are joined to policy outputs. Passing calibration authorizes construction of a new held-out benchmark; it does not establish field effectiveness.
