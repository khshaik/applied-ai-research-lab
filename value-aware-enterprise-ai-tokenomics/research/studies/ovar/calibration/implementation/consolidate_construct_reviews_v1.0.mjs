import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(here,"..");
const aPath=path.join(root,"review/reviewer_a_synthetic_construct_v1.0.json");
const bPath=path.join(root,"review/reviewer_b_synthetic_construct_v1.0.json");
for(const p of [aPath,bPath])if(!fs.existsSync(p))throw Error(`Missing ${p}`);
const A=JSON.parse(fs.readFileSync(aPath,"utf8")),B=JSON.parse(fs.readFileSync(bPath,"utf8"));
const reviews=x=>x.reviews??x.cases??x.records??[];
const ar=reviews(A),br=reviews(B),bById=new Map(br.map(x=>[x.case_id,x]));
const dims=["outcome_contract_clarity","baseline_credibility","evidence_auditability","cost_boundary_completeness","attribution_defensibility","decision_realism"];
const sha=p=>crypto.createHash("sha256").update(fs.readFileSync(p)).digest("hex");
function validate(x,id){if(x.length!==48||new Set(x.map(r=>r.case_id)).size!==48)throw Error(`${id} coverage`);for(const r of x)for(const d of dims){if(!Number.isInteger(r[d])||r[d]<1||r[d]>5)throw Error(`${id}:${r.case_id}:${d}`);if((r[d]===1||r[d]===5)&&!(r.boundary_rationale??"").trim())throw Error(`${id}:${r.case_id}:rationale`);}}
validate(ar,"A");validate(br,"B");
const metrics={};
for(const d of dims){const p=ar.map(a=>[a[d],bById.get(a.case_id)[d]]);metrics[d]={exact_agreement:p.filter(([a,b])=>a===b).length/48,within_one:p.filter(([a,b])=>Math.abs(a-b)<=1).length/48,mean_absolute_difference:p.reduce((s,[a,b])=>s+Math.abs(a-b),0)/48,a_mean:p.reduce((s,[a])=>s+a,0)/48,b_mean:p.reduce((s,[,b])=>s+b,0)/48};}
const cases=ar.map(a=>{const b=bById.get(a.case_id);const reasons=[];if(a.leakage_flag!=="NO"||b.leakage_flag!=="NO")reasons.push("possible decision cue");if(a.ambiguity_flag==="YES"&&b.ambiguity_flag==="YES")reasons.push("both reviewers flag ambiguity");for(const d of dims)if(Math.abs(a[d]-b[d])>=2)reasons.push(`${d} differs by at least 2`);return {case_id:a.case_id,reasons,a,b};});
const blocking=cases.filter(x=>x.reasons.length);
const recommendation=blocking.length===0?"PASS_TO_REFERENCE_ADJUDICATION":"REVISE_BEFORE_REFERENCE_ADJUDICATION";
const report={metadata:{review_type:"SYNTHETIC_AI_AI_CONSTRUCT_STRESS_TEST",human_validation:false,version:"1.0",reviewer_a_sha256:sha(aPath),reviewer_b_sha256:sha(bPath)},metrics,flags:{a_leakage:ar.filter(x=>x.leakage_flag!=="NO").length,b_leakage:br.filter(x=>x.leakage_flag!=="NO").length,a_ambiguity:ar.filter(x=>x.ambiguity_flag==="YES").length,b_ambiguity:br.filter(x=>x.ambiguity_flag==="YES").length,blocking_cases:blocking.length},blocking_case_ids:blocking.map(x=>x.case_id),recommendation};
const outDir=path.join(root,"review/consolidated_v1.0");fs.mkdirSync(outDir,{recursive:true});
const metricsPath=path.join(outDir,"construct_review_metrics_v1.0.json"),registerPath=path.join(outDir,"construct_review_register_v1.0.json");
fs.writeFileSync(metricsPath,JSON.stringify(report,null,2)+"\n");fs.writeFileSync(registerPath,JSON.stringify({metadata:report.metadata,cases},null,2)+"\n");
const files=[aPath,bPath,metricsPath,registerPath];fs.writeFileSync(path.join(outDir,"CONSTRUCT_REVIEW_LOCK_v1.0.json"),JSON.stringify({status:"SYNTHETIC_CONSTRUCT_REVIEW_LOCK",human_validation:false,artifacts:files.map(p=>({relative_path:path.relative(root,p),sha256:sha(p),bytes:fs.statSync(p).size}))},null,2)+"\n");
console.log(JSON.stringify(report,null,2));
