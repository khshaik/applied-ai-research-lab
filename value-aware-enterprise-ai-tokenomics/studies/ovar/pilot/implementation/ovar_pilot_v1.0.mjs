import crypto from "node:crypto";

export const POLICY_VERSION = "1.0";

export const POLICY_FIELDS = Object.freeze({
  USAGE_ONLY: ["case_id","approved_budget","utilization_rate","active_users","token_units_m","provider_cost"],
  SELF_REPORTED_VALUE: ["case_id","approved_budget","utilization_rate","provider_cost","owner_reported_gross_benefit"],
  COST_QUALITY: ["case_id","approved_budget","provider_cost","infrastructure_cost","tooling_cost","technical_quality"],
  OUTCOME_FLAT: ["case_id","outcome_contract_present","observed_outcome_value","baseline_estimated_outcome_value","evidence_status","baseline_design","attribution_confidence","uncertainty_half_width","provider_cost","infrastructure_cost","tooling_cost","human_review_cost","integration_amortized_cost","governance_cost","rework_cost","evidence_review_cost"],
  OVAR_LEDGER: ["case_id","outcome_contract_present","observed_outcome_value","baseline_estimated_outcome_value","evidence_status","baseline_design","attribution_confidence","uncertainty_half_width","provider_cost","infrastructure_cost","tooling_cost","human_review_cost","integration_amortized_cost","governance_cost","rework_cost","expected_harm_cost","compliance_status","evidence_review_cost","access_class","exploration_protected"]
});

const stable = (value) => JSON.stringify(value, Object.keys(value).sort());
const hash = (value) => crypto.createHash("sha256").update(stable(value)).digest("hex");
const totalCost = (x) => x.provider_cost + x.infrastructure_cost + x.tooling_cost + x.human_review_cost + x.integration_amortized_cost + x.governance_cost + x.rework_cost;
const directCost = (x) => x.provider_cost + x.infrastructure_cost + x.tooling_cost;
const credibleBaseline = (x) => !["NONE","BEFORE_AFTER_UNCONTROLLED"].includes(x.baseline_design);

export function permittedView(policy, record) {
  if (!POLICY_FIELDS[policy]) throw new Error(`Unknown policy ${policy}`);
  return Object.fromEntries(POLICY_FIELDS[policy].map((k) => [k, record[k]]));
}

function receipt(policy, input, roi_state, action, reasons, measurement_cost) {
  return {policy, policy_version:POLICY_VERSION, case_id:input.case_id, input_hash:hash(input), roi_state, action, reasons, measurement_cost};
}

export function evaluate(policy, record) {
  const x = permittedView(policy, record);
  if (policy === "USAGE_ONLY") {
    if (x.provider_cost > 1.25 * x.approved_budget) return receipt(policy,x,"NEGATIVE","STOP",["provider cost materially exceeds budget"],0.05);
    if (x.utilization_rate >= .75) return receipt(policy,x,"POSITIVE","SCALE",["high utilization within budget"],0.05);
    if (x.utilization_rate >= .45) return receipt(policy,x,"POSITIVE","CONTINUE_PILOT",["moderate utilization within budget"],0.05);
    return receipt(policy,x,"NEUTRAL","REVISE",["low utilization"],0.05);
  }
  if (policy === "SELF_REPORTED_VALUE") {
    const margin = x.owner_reported_gross_benefit - x.provider_cost;
    if (margin >= .25*x.provider_cost && x.utilization_rate >= .50) return receipt(policy,x,"POSITIVE","SCALE",["reported benefit exceeds provider cost by scale margin"],0.10);
    if (margin > 0) return receipt(policy,x,"POSITIVE","CONTINUE_PILOT",["reported benefit exceeds provider cost"],0.10);
    if (margin < 0) return receipt(policy,x,"NEGATIVE","STOP",["reported benefit below provider cost"],0.10);
    return receipt(policy,x,"NEUTRAL","REVISE",["reported benefit equals provider cost"],0.10);
  }
  if (policy === "COST_QUALITY") {
    const cost = directCost(x);
    if (cost > 1.25*x.approved_budget || x.technical_quality < .60) return receipt(policy,x,"NEGATIVE","STOP",["direct cost or technical quality fails threshold"],0.20);
    if (x.technical_quality >= .85 && cost <= x.approved_budget) return receipt(policy,x,"POSITIVE","SCALE",["high technical quality within direct-cost budget"],0.20);
    if (x.technical_quality >= .70) return receipt(policy,x,"POSITIVE","CONTINUE_PILOT",["acceptable technical quality"],0.20);
    return receipt(policy,x,"NEUTRAL","REVISE",["borderline technical quality"],0.20);
  }
  if (policy === "OUTCOME_FLAT" || policy === "OVAR_LEDGER") {
    const burden = policy === "OUTCOME_FLAT" ? 0.65 : 0.80;
    if (policy === "OVAR_LEDGER" && x.compliance_status === "PROHIBITED") return receipt(policy,x,"NEGATIVE","STOP",["mandatory compliance prohibition"],burden);
    if (!x.outcome_contract_present || x.evidence_status === "UNVERIFIED" || !credibleBaseline(x) || x.attribution_confidence < .55) {
      return receipt(policy,x,"INDETERMINATE","INDETERMINATE",["mandatory outcome evidence, baseline, or attribution requirement not met"],burden);
    }
    const cost = totalCost(x);
    const incremental = x.attribution_confidence * (x.observed_outcome_value - x.baseline_estimated_outcome_value);
    const harm = policy === "OVAR_LEDGER" ? x.expected_harm_cost : 0;
    const net = incremental - cost - harm;
    const lower = net - x.uncertainty_half_width;
    const upper = net + x.uncertainty_half_width;
    const eq = .05 * cost;
    if (upper < 0) return receipt(policy,x,"NEGATIVE","STOP",["upper net-value bound below zero"],burden);
    if (lower > 0) return receipt(policy,x,"POSITIVE", net/cost >= .20 ? "SCALE" : "CONTINUE_PILOT",["lower net-value bound above zero"],burden);
    if (lower >= -eq && upper <= eq) return receipt(policy,x,"NEUTRAL","REVISE",["net-value interval inside practical-equivalence margin"],burden);
    return receipt(policy,x,"NEUTRAL","REVISE",["net-value interval crosses zero"],burden);
  }
  throw new Error(`Unhandled policy ${policy}`);
}

export const POLICIES = Object.freeze(Object.keys(POLICY_FIELDS));
