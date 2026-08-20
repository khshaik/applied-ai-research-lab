import crypto from "node:crypto";

export const POLICY_VERSION = "calibration-1.0";

export const AUTHORIZATION_STATUS = Object.freeze({
  CLEAR: "CLEAR_CURRENT_IN_SCOPE",
  CONDITIONAL: "CONDITIONAL_OR_SCOPE_LIMITED",
  ABSENT: "MATERIALLY_ABSENT_EXPIRED_OR_OUT_OF_SCOPE",
});

export const RISK_TIER = Object.freeze({ LOW: "LOW", MODERATE: "MODERATE", HIGH: "HIGH" });

export const MEASUREMENT_BURDEN = Object.freeze({
  USAGE_ONLY: 0.05,
  SELF_REPORTED_VALUE: 0.10,
  COST_QUALITY: 0.20,
  OUTCOME_FLAT: 0.65,
  OVAR_LEDGER: 0.80,
});

const DIRECT_COST_FIELDS = Object.freeze(["provider_cost", "infrastructure_cost", "tooling_cost"]);
const LOADED_COST_FIELDS = Object.freeze([
  ...DIRECT_COST_FIELDS,
  "human_review_cost",
  "integration_amortized_cost",
  "governance_cost",
  "rework_cost",
  "evidence_review_cost",
]);

export const POLICY_FIELDS = Object.freeze({
  USAGE_ONLY: Object.freeze(["case_id", "approved_budget", "utilization_rate", "active_users", "token_units_m", "provider_cost"]),
  SELF_REPORTED_VALUE: Object.freeze(["case_id", "approved_budget", "utilization_rate", "provider_cost", "owner_reported_gross_benefit"]),
  COST_QUALITY: Object.freeze(["case_id", "approved_budget", ...DIRECT_COST_FIELDS, "technical_quality"]),
  OUTCOME_FLAT: Object.freeze(["case_id", "outcome_contract_present", "observed_outcome_value", "baseline_estimated_outcome_value", "evidence_status", "baseline_design", "attribution_confidence", "uncertainty_half_width", ...LOADED_COST_FIELDS]),
  OVAR_LEDGER: Object.freeze(["case_id", "outcome_contract_present", "observed_outcome_value", "baseline_estimated_outcome_value", "evidence_status", "baseline_design", "attribution_confidence", "uncertainty_half_width", ...LOADED_COST_FIELDS, "authorization_evidence_facts", "risk_facts"]),
});

export const POLICIES = Object.freeze(Object.keys(POLICY_FIELDS));

const FORBIDDEN_KEY = /^(?:true|reference)_/i;
const finite = (value, name) => {
  if (typeof value !== "number" || !Number.isFinite(value)) throw new TypeError(`${name} must be a finite number`);
  return value;
};
const money = (value, name) => {
  finite(value, name);
  if (value < 0) throw new RangeError(`${name} must be non-negative`);
  return value;
};

function rejectForbiddenKeys(value, path = "record") {
  if (!value || typeof value !== "object") return;
  for (const [key, child] of Object.entries(value)) {
    if (FORBIDDEN_KEY.test(key)) throw new Error(`Forbidden key at ${path}.${key}`);
    rejectForbiddenKeys(child, `${path}.${key}`);
  }
}

// Canonical JSON is recursive, so receipts do not depend on insertion order.
function canonical(value) {
  if (Array.isArray(value)) return `[${value.map(canonical).join(",")}]`;
  if (value && typeof value === "object") {
    return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canonical(value[key])}`).join(",")}}`;
  }
  return JSON.stringify(value);
}

export function sha256(value) {
  return crypto.createHash("sha256").update(canonical(value)).digest("hex");
}

export function directCost(input) {
  return DIRECT_COST_FIELDS.reduce((sum, key) => sum + money(input[key], key), 0);
}

export function fullyLoadedCost(input) {
  return LOADED_COST_FIELDS.reduce((sum, key) => sum + money(input[key], key), 0);
}

/*
 * Prospective authorization mapping. It deliberately receives only the factual
 * authorization narrative. Explicit lack of a recorded approval, an expired
 * record, or an out-of-scope statement is material. Scope/condition language is
 * conditional. A remaining affirmative record is clear for its recorded scope.
 */
export function mapAuthorizationStatus(authorizationEvidenceFacts) {
  const text = String(authorizationEvidenceFacts ?? "").trim().toLowerCase();
  if (!text) return AUTHORIZATION_STATUS.ABSENT;
  const materiallyAbsent = [
    /\b(?:no|without) (?:completed |current |recorded )?(?:approval|authorization|assessment|review|consent|record)\b/,
    /\b(?:approval|authorization|assessment|review|consent|record) (?:is |has )?(?:absent|expired|not recorded)\b/,
    /\bhas not been recorded\b/,
    /\bis absent from\b/,
    /\boutside (?:the )?(?:recorded |approved |authorized )?scope\b/,
    /\bcurrent (?:approval|authorization|assessment|review|consent|record) (?:has )?expired\b/,
  ];
  if (materiallyAbsent.some((pattern) => pattern.test(text))) return AUTHORIZATION_STATUS.ABSENT;
  const conditional = [
    /\b(?:except|exclude[sd]?|only|requires?|subject to|limited? to|through|until|named|listed|retention|oversight|sign-?off|final approval|verification|review before|retain(?:s|ed)? .* authority)\b/,
  ];
  return conditional.some((pattern) => pattern.test(text)) ? AUTHORIZATION_STATUS.CONDITIONAL : AUTHORIZATION_STATUS.CLEAR;
}

/*
 * No numeric expected-harm field exists in candidate v1.1. This frozen mapping
 * uses risk text only to select a conservative severity tier. Dollar exposure is
 * 2%, 8%, or 20% of fully loaded cost, a non-outcome accounting base. Patterns
 * describe consequence severity/control failure and never identifiers or value.
 */
export function mapRiskTier(riskFacts) {
  const text = String(riskFacts ?? "").trim().toLowerCase();
  if (!text) return RISK_TIER.HIGH;
  const high = [
    /\b(?:injur(?:y|ies)|breach|malicious|material control gap|clinically material|urgent response|roadside failure|safety event|local restriction|rollback|delayed escalation)\b/,
    /\b(?:missed|omitted?)\b.{0,45}\b(?:material|urgent|prescription|damage|failure|control)\b/,
  ];
  if (high.some((pattern) => pattern.test(text))) return RISK_TIER.HIGH;
  const low = [
    /\bno (?:documented |observed )?(?:injury|breach|harm|incident)\b/,
    /\b(?:all|each|every)\b.{0,55}\b(?:corrected|removed|identified|approved|reviewed)\b.{0,30}\bbefore\b/,
    /\bno unreviewed\b/,
  ];
  if (low.some((pattern) => pattern.test(text))) return RISK_TIER.LOW;
  return RISK_TIER.MODERATE;
}

export function expectedHarmCost(riskFacts, loadedCost) {
  money(loadedCost, "loadedCost");
  const tier = mapRiskTier(riskFacts);
  const rate = tier === RISK_TIER.LOW ? 0.02 : tier === RISK_TIER.MODERATE ? 0.08 : 0.20;
  return { tier, rate, amount: loadedCost * rate };
}

export function mapConstructReviewCase(record) {
  rejectForbiddenKeys(record);
  if (!record || typeof record !== "object" || Array.isArray(record)) throw new TypeError("record must be an object");
  if (!record.cost_components || typeof record.cost_components !== "object") throw new TypeError("cost_components is required");
  const costs = Object.fromEntries(DIRECT_COST_FIELDS.concat(LOADED_COST_FIELDS.slice(3, 7)).map((key) => [key, money(record.cost_components[key], `cost_components.${key}`)]));
  costs.evidence_review_cost = money(record.evidence_review_cost, "evidence_review_cost");
  // Candidate v1.1 has no approved_budget. Direct planned charges are the
  // prospective neutral proxy; no outcome, authorization, or risk fact enters it.
  const approvedBudget = directCost(costs);
  return Object.freeze({
    case_id: record.case_id,
    approved_budget: approvedBudget,
    utilization_rate: record.utilization_rate,
    active_users: record.active_users,
    token_units_m: record.token_units_m,
    owner_reported_gross_benefit: record.owner_reported_gross_benefit,
    technical_quality: record.technical_quality,
    outcome_contract_present: typeof record.outcome_contract === "string" && record.outcome_contract.trim().length > 0,
    observed_outcome_value: record.observed_outcome_value,
    baseline_estimated_outcome_value: record.baseline_estimated_outcome_value,
    evidence_status: record.evidence_status,
    baseline_design: record.baseline_design,
    attribution_confidence: record.attribution_confidence,
    uncertainty_half_width: record.uncertainty_half_width,
    authorization_evidence_facts: record.authorization_evidence_facts,
    risk_facts: record.risk_facts,
    ...costs,
  });
}

export function permittedView(policy, policyInput) {
  if (!POLICY_FIELDS[policy]) throw new Error(`Unknown policy ${policy}`);
  rejectForbiddenKeys(policyInput);
  return Object.freeze(Object.fromEntries(POLICY_FIELDS[policy].map((key) => [key, policyInput[key]])));
}

function receipt(policy, input, roiState, action, reasons, details = {}) {
  const core = {
    policy,
    policy_version: POLICY_VERSION,
    case_id: input.case_id,
    input_hash: sha256(input),
    roi_state: roiState,
    action,
    reasons,
    measurement_cost: MEASUREMENT_BURDEN[policy],
    ...details,
  };
  return Object.freeze({ ...core, receipt_hash: sha256(core) });
}

const credibleBaseline = (input) => input.baseline_estimated_outcome_value !== null && !["NONE", "BEFORE_AFTER_UNCONTROLLED"].includes(input.baseline_design);

export function usageOnly(input) {
  const x = permittedView("USAGE_ONLY", input);
  if (x.provider_cost > 1.25 * x.approved_budget) return receipt("USAGE_ONLY", x, "NEGATIVE", "STOP", ["provider cost materially exceeds budget"]);
  if (x.utilization_rate >= 0.75) return receipt("USAGE_ONLY", x, "POSITIVE", "SCALE", ["high utilization within budget"]);
  if (x.utilization_rate >= 0.45) return receipt("USAGE_ONLY", x, "POSITIVE", "CONTINUE_PILOT", ["moderate utilization within budget"]);
  return receipt("USAGE_ONLY", x, "NEUTRAL", "REVISE", ["low utilization"]);
}

export function selfReportedValue(input) {
  const x = permittedView("SELF_REPORTED_VALUE", input);
  const margin = x.owner_reported_gross_benefit - x.provider_cost;
  if (margin >= 0.25 * x.provider_cost && x.utilization_rate >= 0.50) return receipt("SELF_REPORTED_VALUE", x, "POSITIVE", "SCALE", ["reported benefit exceeds provider cost by scale margin"]);
  if (margin > 0) return receipt("SELF_REPORTED_VALUE", x, "POSITIVE", "CONTINUE_PILOT", ["reported benefit exceeds provider cost"]);
  if (margin < 0) return receipt("SELF_REPORTED_VALUE", x, "NEGATIVE", "STOP", ["reported benefit below provider cost"]);
  return receipt("SELF_REPORTED_VALUE", x, "NEUTRAL", "REVISE", ["reported benefit equals provider cost"]);
}

export function costQuality(input) {
  const x = permittedView("COST_QUALITY", input);
  const cost = directCost(x);
  if (cost > 1.25 * x.approved_budget || x.technical_quality < 0.60) return receipt("COST_QUALITY", x, "NEGATIVE", "STOP", ["direct cost or technical quality fails threshold"]);
  if (x.technical_quality >= 0.85 && cost <= x.approved_budget) return receipt("COST_QUALITY", x, "POSITIVE", "SCALE", ["high technical quality within direct-cost budget"]);
  if (x.technical_quality >= 0.70) return receipt("COST_QUALITY", x, "POSITIVE", "CONTINUE_PILOT", ["acceptable technical quality"]);
  return receipt("COST_QUALITY", x, "NEUTRAL", "REVISE", ["borderline technical quality"]);
}

function outcomeDecision(policy, x, harm = { tier: null, rate: 0, amount: 0 }, authorizationStatus = null) {
  if (!x.outcome_contract_present || x.evidence_status === "UNVERIFIED" || !credibleBaseline(x) || x.attribution_confidence < 0.55) {
    return receipt(policy, x, "INDETERMINATE", "INDETERMINATE", ["mandatory outcome evidence, baseline, or attribution requirement not met"], policy === "OVAR_LEDGER" ? { authorization_status: authorizationStatus, risk_tier: harm.tier, expected_harm_cost: harm.amount } : {});
  }
  const cost = fullyLoadedCost(x);
  const incremental = x.attribution_confidence * (x.observed_outcome_value - x.baseline_estimated_outcome_value);
  const net = incremental - cost - harm.amount;
  const lower = net - x.uncertainty_half_width;
  const upper = net + x.uncertainty_half_width;
  const equivalence = 0.05 * cost;
  const details = { fully_loaded_cost: cost, incremental_outcome_value: incremental, expected_harm_cost: harm.amount, net_value: net, lower_bound: lower, upper_bound: upper };
  if (policy === "OVAR_LEDGER") Object.assign(details, { authorization_status: authorizationStatus, risk_tier: harm.tier });
  if (upper < 0) return receipt(policy, x, "NEGATIVE", "STOP", ["upper net-value bound below zero"], details);
  if (lower > 0) {
    let action = net / cost >= 0.20 ? "SCALE" : "CONTINUE_PILOT";
    const reasons = ["lower net-value bound above zero"];
    if (policy === "OVAR_LEDGER" && authorizationStatus === AUTHORIZATION_STATUS.CONDITIONAL && action === "SCALE") {
      action = "CONTINUE_PILOT";
      reasons.push("authorization is conditional or scope-limited");
    }
    return receipt(policy, x, "POSITIVE", action, reasons, details);
  }
  if (lower >= -equivalence && upper <= equivalence) return receipt(policy, x, "NEUTRAL", "REVISE", ["net-value interval inside practical-equivalence margin"], details);
  return receipt(policy, x, "NEUTRAL", "REVISE", ["net-value interval crosses zero"], details);
}

export function outcomeFlat(input) {
  const x = permittedView("OUTCOME_FLAT", input);
  return outcomeDecision("OUTCOME_FLAT", x);
}

export function ovarLedger(input) {
  const x = permittedView("OVAR_LEDGER", input);
  const authorizationStatus = mapAuthorizationStatus(x.authorization_evidence_facts);
  const cost = fullyLoadedCost(x);
  const harm = expectedHarmCost(x.risk_facts, cost);
  if (authorizationStatus === AUTHORIZATION_STATUS.ABSENT) {
    return receipt("OVAR_LEDGER", x, "NEGATIVE", "STOP", ["material authorization evidence is absent, expired, or out of scope"], { authorization_status: authorizationStatus, risk_tier: harm.tier, expected_harm_cost: harm.amount, fully_loaded_cost: cost });
  }
  return outcomeDecision("OVAR_LEDGER", x, harm, authorizationStatus);
}

const EVALUATORS = Object.freeze({ USAGE_ONLY: usageOnly, SELF_REPORTED_VALUE: selfReportedValue, COST_QUALITY: costQuality, OUTCOME_FLAT: outcomeFlat, OVAR_LEDGER: ovarLedger });

export function evaluate(policy, record, { mapped = false } = {}) {
  const input = mapped ? record : mapConstructReviewCase(record);
  const evaluator = EVALUATORS[policy];
  if (!evaluator) throw new Error(`Unknown policy ${policy}`);
  return evaluator(input);
}
