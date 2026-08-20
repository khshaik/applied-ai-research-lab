import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(here,"..");
const reviewDir=path.join(root,"review");
const aPath=path.join(reviewDir,"reviewer_a_synthetic_recheck_v1.1.json");
const bPath=path.join(reviewDir,"reviewer_b_synthetic_recheck_v1.1.json");
const outDir=path.join(reviewDir,"consolidated_v1.1");
const dims=["outcome_contract_clarity","baseline_credibility","evidence_auditability","cost_boundary_completeness","attribution_defensibility","decision_realism"];
const A=JSON.parse(fs.readFileSync(aPath,"utf8")),B=JSON.parse(fs.readFileSync(bPath,"utf8"));
const byB=new Map(B.reviews.map(x=>[x.case_id,x]));
const sha=p=>crypto.createHash("sha256").update(fs.readFileSync(p)).digest("hex");
function validate(x,id){if(x.reviews.length!==24||new Set(x.reviews.map(r=>r.case_id)).size!==24)throw Error(`${id} coverage`);for(const r of x.reviews)for(const d of dims)if(!Number.isInteger(r[d])||r[d]<1||r[d]>5)throw Error(`${id}:${r.case_id}:${d}`);if(x.metadata.ground_truth_accessed!==false||x.metadata.policy_outputs_accessed!==false||x.metadata.other_reviewer_scores_accessed!==false)throw Error(`${id} blinding`);}
validate(A,"A");validate(B,"B");
const metrics={};
for(const d of dims){const p=A.reviews.map(a=>[a[d],byB.get(a.case_id)[d]]);metrics[d]={exact_agreement:p.filter(([a,b])=>a===b).length/24,within_one:p.filter(([a,b])=>Math.abs(a-b)<=1).length/24,mean_absolute_difference:p.reduce((s,[a,b])=>s+Math.abs(a-b),0)/24,reviewer_a_mean:p.reduce((s,[a])=>s+a,0)/24,reviewer_b_mean:p.reduce((s,[,b])=>s+b,0)/24};}
const cases=A.reviews.map(a=>{const b=byB.get(a.case_id);const leakage=a.leakage_flag!=="NO"||b.leakage_flag!=="NO";const ambiguity=a.ambiguity_flag==="YES"&&b.ambiguity_flag==="YES";const lowEvidence=a.evidence_auditability<=2&&b.evidence_auditability<=2;return {case_id:a.case_id,reviewer_a:{scores:Object.fromEntries(dims.map(d=>[d,a[d]])),leakage_flag:a.leakage_flag,ambiguity_flag:a.ambiguity_flag,missing_information:a.missing_information},reviewer_b:{scores:Object.fromEntries(dims.map(d=>[d,b[d]])),leakage_flag:b.leakage_flag,ambiguity_flag:b.ambiguity_flag,missing_information:b.missing_information},blocking_reasons:[...(leakage?["possible visible decision cue"]:[]),...(lowEvidence?["both evidence-auditability scores <=2"]:[]),...(ambiguity?["both reviewers flagged ambiguity"]:[])]};});
const summary={review_type:"SYNTHETIC_AI_AI_POST_REVISION_RECHECK",human_inter_rater_reliability:false,version:"1.1",reviewer_a_sha256:sha(aPath),reviewer_b_sha256:sha(bPath),metrics,flags:{a_leakage:A.reviews.filter(x=>x.leakage_flag!=="NO").length,b_leakage:B.reviews.filter(x=>x.leakage_flag!=="NO").length,a_ambiguity:A.reviews.filter(x=>x.ambiguity_flag==="YES").length,b_ambiguity:B.reviews.filter(x=>x.ambiguity_flag==="YES").length,blocking_cases:cases.filter(x=>x.blocking_reasons.length).length},gate_decision:"REVISE_OR_PIVOT_TO_NEW_CALIBRATION_DESIGN",reason:"The single permitted clarity revision improved scoreability but did not remove visible decision cues; three deliberately unverified/no-comparator cases remain non-reproducible by design."};
fs.mkdirSync(outDir,{recursive:true});
fs.writeFileSync(path.join(outDir,"synthetic_recheck_metrics_v1.1.json"),JSON.stringify(summary,null,2)+"\n");
fs.writeFileSync(path.join(outDir,"synthetic_recheck_case_register_v1.1.json"),JSON.stringify({metadata:summary,cases},null,2)+"\n");
const artifacts=[aPath,bPath,path.join(outDir,"synthetic_recheck_metrics_v1.1.json"),path.join(outDir,"synthetic_recheck_case_register_v1.1.json")];
fs.writeFileSync(path.join(outDir,"SYNTHETIC_RECHECK_LOCK_v1.1.json"),JSON.stringify({status:"POST_REVISION_RECHECK_LOCK",human_validation:false,artifacts:artifacts.map(p=>({relative_path:path.relative(root,p),sha256:sha(p),bytes:fs.statSync(p).size}))},null,2)+"\n");
console.log(JSON.stringify(summary,null,2));
