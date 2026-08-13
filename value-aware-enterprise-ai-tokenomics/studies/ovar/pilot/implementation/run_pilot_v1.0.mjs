import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { evaluate, POLICIES } from "./ovar_pilot_v1.0.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..");
const visible = JSON.parse(fs.readFileSync(path.join(root,"cases/candidate_v1.0/reviewer_visible_cases.json"),"utf8")).cases;
const references = JSON.parse(fs.readFileSync(path.join(root,"restricted/investigator_reference_RESTRICTED_v1.0.json"),"utf8")).references;
const refById = new Map(references.map(r => [r.case_id,r]));
const outDir = path.join(root,"results","pilot_v1.0");

const positive = (roi) => roi === "POSITIVE";
const riskyAction = (action) => ["SCALE","CONTINUE_PILOT"].includes(action);
const safeReference = (action) => ["SCALE","CONTINUE_PILOT"].includes(action);
const shouldNotScale = (action) => ["STOP","REVISE","INDETERMINATE"].includes(action);

const decisions = [];
for (const c of visible) {
  const ref = refById.get(c.case_id);
  if (!ref) throw new Error(`Missing reference ${c.case_id}`);
  for (const policy of POLICIES) decisions.push({...evaluate(policy,c), domain:c.domain, reference_roi_state:ref.reference_roi_state, reference_action:ref.reference_action, reference_compliance_pass:ref.reference_compliance_pass});
}

function summarize(policy) {
  const rows = decisions.filter(d => d.policy === policy);
  const roiNeg = rows.filter(d => d.reference_roi_state !== "POSITIVE");
  const nonScale = rows.filter(d => shouldNotScale(d.reference_action));
  const safe = rows.filter(d => safeReference(d.reference_action));
  const falsePositive = roiNeg.filter(d => positive(d.roi_state));
  const falseScale = nonScale.filter(d => d.action === "SCALE");
  const falseStop = safe.filter(d => d.action === "STOP");
  const violations = rows.filter(d => !d.reference_compliance_pass && riskyAction(d.action));
  const exact = rows.filter(d => d.action === d.reference_action);
  const indeterminate = rows.filter(d => d.action === "INDETERMINATE");
  const meanBurden = rows.reduce((a,b)=>a+b.measurement_cost,0)/rows.length;
  const rates = {
    false_positive_roi_rate:falsePositive.length/roiNeg.length,
    false_scale_rate:falseScale.length/nonScale.length,
    false_stop_rate:falseStop.length/safe.length,
    exact_action_agreement:exact.length/rows.length,
    indeterminate_rate:indeterminate.length/rows.length,
    risk_compliance_violation_rate:violations.length/rows.length,
    mean_normalized_measurement_burden:meanBurden
  };
  const weighted = 2*rates.false_positive_roi_rate + 4*rates.false_scale_rate + 2*rates.false_stop_rate + 8*rates.risk_compliance_violation_rate + .5*meanBurden;
  return {
    policy, n:rows.length,
    denominators:{roi_nonpositive:roiNeg.length, should_not_scale:nonScale.length, safe_reference:safe.length},
    counts:{false_positive_roi:falsePositive.length,false_scale:falseScale.length,false_stop:falseStop.length,risk_compliance_violation:violations.length,exact_action_agreement:exact.length,indeterminate:indeterminate.length},
    rates, weighted_decision_loss:weighted,
    error_case_ids:{false_positive_roi:falsePositive.map(x=>x.case_id),false_scale:falseScale.map(x=>x.case_id),false_stop:falseStop.map(x=>x.case_id),risk_compliance_violation:violations.map(x=>x.case_id)}
  };
}

const summaries = POLICIES.map(summarize);
const ovar = summaries.find(x=>x.policy === "OVAR_LEDGER");
const usage = summaries.find(x=>x.policy === "USAGE_ONLY");
const self = summaries.find(x=>x.policy === "SELF_REPORTED_VALUE");
const dominated = summaries.filter(x => x.policy !== "OVAR_LEDGER" && x.weighted_decision_loss < ovar.weighted_decision_loss && x.rates.mean_normalized_measurement_burden < ovar.rates.mean_normalized_measurement_burden);
const refCounts = Object.fromEntries(["STOP","REVISE","CONTINUE_PILOT","SCALE","INDETERMINATE"].map(a=>[a,references.filter(r=>r.reference_action===a).length]));
const domainSerious = {};
for (const domain of [...new Set(visible.map(x=>x.domain))]) {
  const rows=decisions.filter(x=>x.policy==="OVAR_LEDGER"&&x.domain===domain);
  domainSerious[domain]=rows.filter(x=>(x.action==="SCALE"&&shouldNotScale(x.reference_action))||(x.action==="STOP"&&safeReference(x.reference_action))).length;
}

const criteria = {
  implementation_tests_passed:null,
  every_reference_action_represented:Object.values(refCounts).every(n=>n>0),
  zero_ovar_compliance_violations:ovar.counts.risk_compliance_violation===0,
  lower_fpr_than_usage_and_self:ovar.rates.false_positive_roi_rate<usage.rates.false_positive_roi_rate&&ovar.rates.false_positive_roi_rate<self.rates.false_positive_roi_rate,
  ovar_not_loss_burden_dominated:dominated.length===0,
  ovar_indeterminate_at_most_25pct:ovar.rates.indeterminate_rate<=.25,
  max_one_serious_error_per_domain:Object.values(domainSerious).every(n=>n<=1)
};

const report = {metadata:{study:"OVAR constructed pilot",version:"1.0",confirmatory:false,case_count:visible.length,executed_at:new Date().toISOString()},reference_action_counts:refCounts,policy_summaries:summaries,domain_ovar_serious_error_counts:domainSerious,prospective_gate:{criteria,implementation_tests_in_separate_artifact:true,dominating_policies:dominated.map(x=>x.policy),decision:"PENDING_TEST_RESULT"}};

fs.mkdirSync(outDir,{recursive:true});
fs.writeFileSync(path.join(outDir,"policy_decisions.json"),JSON.stringify({metadata:report.metadata,decisions},null,2)+"\n");
fs.writeFileSync(path.join(outDir,"pilot_metrics_pretest.json"),JSON.stringify(report,null,2)+"\n");
console.log(JSON.stringify({outDir, reference_action_counts:refCounts, summaries:summaries.map(x=>({policy:x.policy,loss:x.weighted_decision_loss,fpr:x.rates.false_positive_roi_rate,false_scale:x.rates.false_scale_rate,false_stop:x.rates.false_stop_rate,agreement:x.rates.exact_action_agreement,indeterminate:x.rates.indeterminate_rate})),criteria},null,2));
