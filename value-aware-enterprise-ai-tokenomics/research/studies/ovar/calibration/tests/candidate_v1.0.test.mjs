import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(here,"..");
const doc=JSON.parse(fs.readFileSync(path.join(root,"candidate_v1.0/construct_review_cases.json"),"utf8"));
const cases=doc.cases;
const domains=["HEALTHCARE","FINANCIAL_SERVICES","ECOMMERCE","TRANSPORT_LOGISTICS","CYBERSECURITY","CUSTOMER_OPERATIONS"];
const strata=["HIGH_VALUE_MODERATE_USAGE","HIGH_USAGE_LOW_VALUE","HIDDEN_FULLY_LOADED_COST","WEAK_OR_ABSENT_COUNTERFACTUAL","DELAYED_OR_SHARED_ATTRIBUTION","AUTHORIZATION_OR_COMPLIANCE_CONSTRAINT","LOW_ADOPTION_HIGH_VALUE","REVISE_INDETERMINATE_BOUNDARY"];
const costKeys=["provider_cost","infrastructure_cost","tooling_cost","human_review_cost","integration_amortized_cost","governance_cost","rework_cost"];
const forbiddenKeys=[/^true_/,/^reference_/,/policy_output/i,/ground.?truth/i];
const forbiddenText=[/\bprohibited\b/i,/\bmust stop\b/i,/\bmust scale\b/i,/\bpositive roi\b/i,/\bnegative roi\b/i,/cannot support a positive/i,/attribution (?:is )?therefore capped/i,/preferred policy/i,/reference decision/i];

test("48 unique consecutive IDs",()=>{
  assert.equal(cases.length,48);assert.equal(new Set(cases.map(x=>x.case_id)).size,48);
  assert.deepEqual(cases.map(x=>x.case_id),Array.from({length:48},(_,i)=>`OC-${String(i+1).padStart(3,"0")}`));
});
test("six domains and eight strata per domain",()=>{
  for(const d of domains){const rows=cases.filter(x=>x.domain===d);assert.equal(rows.length,8,d);for(const s of strata)assert.equal(rows.filter(x=>x.stratum===s).length,1,`${d}:${s}`);}
});
test("no hidden keys or forbidden decision cues",()=>{
  for(const c of cases){for(const k of Object.keys(c))assert.ok(!forbiddenKeys.some(x=>x.test(k)),`${c.case_id}:${k}`);for(const p of forbiddenText)assert.ok(!p.test(JSON.stringify(c)),`${c.case_id}:${p}`);}
});
test("cost components and ranges are valid",()=>{
  for(const c of cases){assert.deepEqual(Object.keys(c.cost_components).sort(),[...costKeys].sort(),c.case_id);for(const k of costKeys)assert.ok(Number.isFinite(c.cost_components[k])&&c.cost_components[k]>=0,`${c.case_id}:${k}`);for(const k of ["attribution_confidence","technical_quality","utilization_rate"])assert.ok(Number.isFinite(c[k])&&c[k]>=0&&c[k]<=1,`${c.case_id}:${k}`);assert.ok(Number.isInteger(c.active_users)&&c.active_users>0,c.case_id);}
});
test("required audit narratives are populated",()=>{
  for(const c of cases)for(const k of ["outcome_contract","acceptance_criteria","baseline_implementation","evidence_locator","evidence_reproduction_note","cost_allocation_method","attribution_rationale","risk_facts","authorization_evidence_facts","decision_checkpoint"])assert.ok(typeof c[k]==="string"&&c[k].trim().length>=8,`${c.case_id}:${k}`);
});
test("constructed provenance is explicit",()=>{for(const c of cases){assert.equal(c.provenance,"CONSTRUCTED");assert.equal(c.authoring_version,"calibration-1.0-draft");}});
