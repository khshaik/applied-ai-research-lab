import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { evaluate, permittedView, POLICIES, POLICY_FIELDS } from "../implementation/ovar_pilot_v1.0.mjs";

const here=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(here,"..");
const visible=JSON.parse(fs.readFileSync(path.join(root,"cases/candidate_v1.0/reviewer_visible_cases.json"),"utf8")).cases;
const refs=JSON.parse(fs.readFileSync(path.join(root,"restricted/investigator_reference_RESTRICTED_v1.0.json"),"utf8")).references;
const prohibited=[/^true_/,/^reference_/,/ground.?truth/i,/realized_result/i];

test("24 unique visible and reference IDs match",()=>{
  assert.equal(visible.length,24); assert.equal(refs.length,24);
  assert.equal(new Set(visible.map(x=>x.case_id)).size,24);
  assert.deepEqual(visible.map(x=>x.case_id).sort(),refs.map(x=>x.case_id).sort());
});

test("visible records contain no prohibited reference keys",()=>{
  for(const row of visible) for(const key of Object.keys(row)) assert.ok(!prohibited.some(p=>p.test(key)),`${row.case_id}:${key}`);
});

test("all six domains have four cases",()=>{
  const counts={}; for(const x of visible) counts[x.domain]=(counts[x.domain]||0)+1;
  assert.equal(Object.keys(counts).length,6); for(const n of Object.values(counts)) assert.equal(n,4);
});

test("visible cost components reconcile to restricted true cost",()=>{
  const byId=new Map(refs.map(x=>[x.case_id,x]));
  for(const x of visible){const sum=x.provider_cost+x.infrastructure_cost+x.tooling_cost+x.human_review_cost+x.integration_amortized_cost+x.governance_cost+x.rework_cost;assert.equal(sum,byId.get(x.case_id).true_fully_loaded_cost,x.case_id);}
});

test("reference net arithmetic is exact",()=>{
  for(const r of refs) assert.equal(r.true_incremental_value-r.true_fully_loaded_cost-r.true_expected_harm_cost,r.reference_net_value,r.case_id);
});

test("all decision actions are represented in the reference",()=>{
  for(const action of ["STOP","REVISE","CONTINUE_PILOT","SCALE","INDETERMINATE"]) assert.ok(refs.some(x=>x.reference_action===action),action);
});

test("policy views contain only whitelisted keys",()=>{
  for(const p of POLICIES) for(const x of visible) assert.deepEqual(Object.keys(permittedView(p,x)),POLICY_FIELDS[p]);
});

test("every policy returns a complete deterministic receipt",()=>{
  for(const p of POLICIES) for(const x of visible){const a=evaluate(p,x),b=evaluate(p,x);assert.deepEqual(a,b);assert.match(a.input_hash,/^[a-f0-9]{64}$/);assert.ok(a.reasons.length>0);}
});

test("mutating a forbidden field cannot affect a policy receipt",()=>{
  for(const p of POLICIES) for(const x of visible){const a=evaluate(p,x);const b=evaluate(p,{...x,true_incremental_value:999999,reference_action:"SCALE"});assert.deepEqual(a,b);}
});

test("OVAR applies mandatory compliance stop",()=>{
  for(const x of visible.filter(x=>x.compliance_status==="PROHIBITED")) assert.equal(evaluate("OVAR_LEDGER",x).action,"STOP");
});

test("OVAR applies mandatory evidence indeterminacy",()=>{
  for(const x of visible.filter(x=>!x.outcome_contract_present||x.evidence_status==="UNVERIFIED"||x.baseline_design==="NONE"||x.attribution_confidence<.55)) assert.equal(evaluate("OVAR_LEDGER",x).action,"INDETERMINATE");
});

test("input hashes differ for distinct cases",()=>{
  for(const p of POLICIES){const hashes=visible.map(x=>evaluate(p,x).input_hash);assert.equal(new Set(hashes).size,24,p);}
});
