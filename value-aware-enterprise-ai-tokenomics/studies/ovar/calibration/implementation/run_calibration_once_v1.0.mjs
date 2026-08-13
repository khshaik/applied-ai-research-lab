import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { evaluate, POLICIES, MEASUREMENT_BURDEN } from "./calibration_policies_v1.0.mjs";

const here=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(here,"..");
const lockPath=path.join(root,"CALIBRATION_PRE_EXECUTION_LOCK_v1.2.json");
const resultDir=path.join(root,"results/calibration_v1.0");
if(!fs.existsSync(lockPath))throw Error("Superseding pre-execution lock v1.1 is required");
if(fs.existsSync(resultDir))throw Error("Calibration result directory already exists; one-run rule prevents overwrite or rerun");
const lock=JSON.parse(fs.readFileSync(lockPath,"utf8"));
if(lock.status!=="CALIBRATION_PRE_EXECUTION_LOCK"||lock.execution_authorized!==true)throw Error("Execution lock is not active");
const sha=p=>crypto.createHash("sha256").update(fs.readFileSync(p)).digest("hex");
for(const a of lock.artifacts){const p=path.join(path.resolve(root,".."),a.relative_path);if(sha(p)!==a.sha256)throw Error(`Lock verification failed: ${a.relative_path}`);}

const cases=JSON.parse(fs.readFileSync(path.join(root,"candidate_v1.1/construct_review_cases.json"),"utf8")).cases;
const refDoc=JSON.parse(fs.readFileSync(path.join(root,"restricted/reference_labels_RESTRICTED_v1.0.json"),"utf8"));
const refs=refDoc.references??refDoc.records??refDoc.labels,byRef=new Map(refs.map(r=>[r.review_case_id,r]));
const decisions=[];
for(const c of cases)for(const policy of POLICIES){const d=evaluate(policy,c);const r=byRef.get(c.case_id);decisions.push({...d,domain:c.domain,reference_roi_state:r.reference_roi_state,reference_action:r.reference_action,reference_authorization_current:r.reference_authorization_current});}

const positive=x=>x==="POSITIVE",risky=x=>["SCALE","CONTINUE_PILOT"].includes(x),safeRef=x=>["SCALE","CONTINUE_PILOT"].includes(x),notScale=x=>["STOP","REVISE","INDETERMINATE"].includes(x);
function components(policy){const rows=decisions.filter(x=>x.policy===policy),roiNon=rows.filter(x=>x.reference_roi_state!=="POSITIVE"),shouldNot=rows.filter(x=>notScale(x.reference_action)),safe=rows.filter(x=>safeRef(x.reference_action));const fp=roiNon.filter(x=>positive(x.roi_state)),fsx=shouldNot.filter(x=>x.action==="SCALE"),fst=safe.filter(x=>x.action==="STOP"),viol=rows.filter(x=>!x.reference_authorization_current&&risky(x.action)),exact=rows.filter(x=>x.action===x.reference_action),ind=rows.filter(x=>x.action==="INDETERMINATE");return{policy,n:rows.length,denominators:{roi_nonpositive:roiNon.length,should_not_scale:shouldNot.length,safe_reference:safe.length},counts:{false_positive_roi:fp.length,false_scale:fsx.length,false_stop:fst.length,authorization_violation:viol.length,exact_action:exact.length,indeterminate:ind.length},rates:{false_positive_roi:fp.length/roiNon.length,false_scale:fsx.length/shouldNot.length,false_stop:fst.length/safe.length,authorization_violation:viol.length/rows.length,exact_action:exact.length/rows.length,indeterminate:ind.length/rows.length},measurement_burden:MEASUREMENT_BURDEN[policy],case_ids:{false_positive_roi:fp.map(x=>x.case_id),false_scale:fsx.map(x=>x.case_id),false_stop:fst.map(x=>x.case_id),authorization_violation:viol.map(x=>x.case_id)}};}
const summaries=POLICIES.map(components);
const loss=(s,beta=.5)=>2*s.rates.false_positive_roi+4*s.rates.false_scale+2*s.rates.false_stop+8*s.rates.authorization_violation+beta*s.measurement_burden;
for(const s of summaries)s.weighted_loss=loss(s,.5);
const ovar=summaries.find(x=>x.policy==="OVAR_LEDGER"),usage=summaries.find(x=>x.policy==="USAGE_ONLY"),self=summaries.find(x=>x.policy==="SELF_REPORTED_VALUE"),flat=summaries.find(x=>x.policy==="OUTCOME_FLAT");
const dominatedAtHalf=summaries.filter(x=>x.policy!=="OVAR_LEDGER"&&x.weighted_loss<ovar.weighted_loss&&x.measurement_burden<ovar.measurement_burden).map(x=>x.policy);
const betas=[.25,.5,.75,1];
const sensitivity=betas.map(beta=>({measurement_weight:beta,losses:Object.fromEntries(summaries.map(s=>[s.policy,loss(s,beta)])),ovar_dominated_by:summaries.filter(x=>x.policy!=="OVAR_LEDGER"&&loss(x,beta)<loss(ovar,beta)&&x.measurement_burden<ovar.measurement_burden).map(x=>x.policy)}));
const alwaysDominators=POLICIES.filter(p=>p!=="OVAR_LEDGER"&&sensitivity.every(x=>x.ovar_dominated_by.includes(p)));
const seriousByDomain={};for(const domain of [...new Set(cases.map(x=>x.domain))]){const rows=decisions.filter(x=>x.policy==="OVAR_LEDGER"&&x.domain===domain);seriousByDomain[domain]=rows.filter(x=>(x.action==="SCALE"&&notScale(x.reference_action))||(x.action==="STOP"&&safeRef(x.reference_action))).length;}
const criteria={all_preexecution_tests_and_hashes_passed:true,zero_ovar_authorization_harm:ovar.counts.authorization_violation===0,ovar_fpr_lower_than_usage_and_self:ovar.rates.false_positive_roi<usage.rates.false_positive_roi&&ovar.rates.false_positive_roi<self.rates.false_positive_roi,ovar_false_scale_no_worse_than_outcome_flat:ovar.rates.false_scale<=flat.rates.false_scale,ovar_false_stop_within_10pp_best:ovar.rates.false_stop<=Math.min(...summaries.map(x=>x.rates.false_stop))+.10,ovar_indeterminate_at_most_30pct:ovar.rates.indeterminate<=.30,ovar_not_loss_burden_dominated:dominatedAtHalf.length===0,max_one_serious_error_per_domain:Object.values(seriousByDomain).every(x=>x<=1),not_dominated_throughout_sensitivity:alwaysDominators.length===0};
const gate=Object.values(criteria).every(Boolean)?"GO_TO_HELD_OUT_DESIGN":"REVISE_OR_STOP_PER_PROTOCOL";
const report={metadata:{study:"OVAR prospective constructed calibration",version:"1.0",confirmatory:false,executed_at:new Date().toISOString(),lock_sha256:sha(lockPath),case_count:48},policy_summaries:summaries,domain_ovar_serious_errors:seriousByDomain,sensitivity,prospective_gate:{criteria,dominated_at_weight_0_5:dominatedAtHalf,always_dominating_policies:alwaysDominators,decision:gate}};
fs.mkdirSync(resultDir,{recursive:true});
fs.writeFileSync(path.join(resultDir,"policy_decisions.json"),JSON.stringify({metadata:report.metadata,decisions},null,2)+"\n");
fs.writeFileSync(path.join(resultDir,"calibration_gate.json"),JSON.stringify(report,null,2)+"\n");
console.log(JSON.stringify({gate,summaries:summaries.map(s=>({policy:s.policy,...s.rates,weighted_loss:s.weighted_loss})),criteria,seriousByDomain},null,2));
