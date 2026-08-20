import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(here,"..");
const reviewDir=path.join(root,"review");
const aPath=path.join(reviewDir,"reviewer_a_synthetic_completed_v1.0.json");
const bPath=path.join(reviewDir,"reviewer_b_synthetic_completed_v1.0.json");
const outDir=path.join(reviewDir,"consolidated_v1.0");
const dims=["outcome_contract_clarity","baseline_credibility","evidence_auditability","cost_boundary_completeness","attribution_defensibility","decision_realism"];
const sha256=(p)=>crypto.createHash("sha256").update(fs.readFileSync(p)).digest("hex");

for(const p of [aPath,bPath]) if(!fs.existsSync(p)) throw new Error(`Missing completed review: ${p}`);
const A=JSON.parse(fs.readFileSync(aPath,"utf8"));
const B=JSON.parse(fs.readFileSync(bPath,"utf8"));

function validate(doc,id){
  if(doc.metadata.reviewer_id!==id) throw new Error(`${id}: metadata mismatch`);
  if(doc.metadata.ground_truth_accessed!==false||doc.metadata.policy_outputs_accessed!==false||doc.metadata.other_reviewer_scores_accessed!==false) throw new Error(`${id}: blinding attestation failed`);
  if(doc.reviews.length!==24||new Set(doc.reviews.map(x=>x.case_id)).size!==24) throw new Error(`${id}: case coverage failed`);
  for(const r of doc.reviews) for(const d of dims){if(!Number.isInteger(r[d])||r[d]<1||r[d]>5) throw new Error(`${id}:${r.case_id}:${d}`);if((r[d]===1||r[d]===5)&&!r.boundary_rationale.trim())throw new Error(`${id}:${r.case_id}: missing boundary rationale`);}
}
validate(A,"REVIEWER_A"); validate(B,"REVIEWER_B");
if(A.metadata.source_sha256!==B.metadata.source_sha256) throw new Error("Source hashes differ");

const bById=new Map(B.reviews.map(x=>[x.case_id,x]));
function linearWeightedKappa(pairs){
  const n=pairs.length, k=5;
  const obs=Array.from({length:k},()=>Array(k).fill(0));
  const ar=Array(k).fill(0),br=Array(k).fill(0);
  for(const [a,b] of pairs){obs[a-1][b-1]++;ar[a-1]++;br[b-1]++;}
  let dobs=0,dexp=0;
  for(let i=0;i<k;i++)for(let j=0;j<k;j++){
    const w=Math.abs(i-j)/(k-1);
    dobs+=w*obs[i][j]/n;
    dexp+=w*(ar[i]/n)*(br[j]/n);
  }
  return dexp===0?1:1-dobs/dexp;
}

const metrics={};
for(const d of dims){
  const pairs=A.reviews.map(a=>[a[d],bById.get(a.case_id)[d]]);
  metrics[d]={
    exact_agreement:pairs.filter(([a,b])=>a===b).length/24,
    within_one_agreement:pairs.filter(([a,b])=>Math.abs(a-b)<=1).length/24,
    mean_absolute_difference:pairs.reduce((s,[a,b])=>s+Math.abs(a-b),0)/24,
    linear_weighted_kappa:linearWeightedKappa(pairs),
    reviewer_a_mean:pairs.reduce((s,[a])=>s+a,0)/24,
    reviewer_b_mean:pairs.reduce((s,[,b])=>s+b,0)/24
  };
}

const register=A.reviews.map(a=>{
  const b=bById.get(a.case_id);
  const score_disagreements=Object.fromEntries(dims.map(d=>[d,{reviewer_a:a[d],reviewer_b:b[d],absolute_difference:Math.abs(a[d]-b[d])}]));
  const large=dims.filter(d=>Math.abs(a[d]-b[d])>=2);
  const bothLow=dims.filter(d=>a[d]<=2&&b[d]<=2);
  const leakage=[a.leakage_flag,b.leakage_flag].some(x=>x!=="NO");
  const bothAmbiguous=a.ambiguity_flag==="YES"&&b.ambiguity_flag==="YES";
  return {
    case_id:a.case_id,score_disagreements:score_disagreements,
    reviewer_a_flags:{leakage:a.leakage_flag,ambiguity:a.ambiguity_flag,missing_information:a.missing_information,boundary_rationale:a.boundary_rationale},
    reviewer_b_flags:{leakage:b.leakage_flag,ambiguity:b.ambiguity_flag,missing_information:b.missing_information,boundary_rationale:b.boundary_rationale},
    escalation_reasons:[...(large.length?[`score difference >=2: ${large.join(", ")}`]:[]),...(bothLow.length?[`both reviewers scored <=2: ${bothLow.join(", ")}`]:[]),...(leakage?["possible leakage"]:[]),...(bothAmbiguous?["both reviewers flagged ambiguity"]:[])],
    adjudication_required:large.length>0||bothLow.length>0||leakage||bothAmbiguous,
    adjudicated_scores:Object.fromEntries(dims.map(d=>[d,null])),
    adjudication_action:null,adjudication_rationale:"",adjudicator:"",adjudication_date:null
  };
});

const escalated=register.filter(x=>x.adjudication_required);
const flagSummary={
  reviewer_a_leakage_non_no:A.reviews.filter(x=>x.leakage_flag!=="NO").length,
  reviewer_b_leakage_non_no:B.reviews.filter(x=>x.leakage_flag!=="NO").length,
  reviewer_a_ambiguity_yes:A.reviews.filter(x=>x.ambiguity_flag==="YES").length,
  reviewer_b_ambiguity_yes:B.reviews.filter(x=>x.ambiguity_flag==="YES").length,
  cases_requiring_adjudication:escalated.length
};
const result={metadata:{study:"OVAR constructed pilot",version:"1.0",review_type:"SYNTHETIC_AI_AI_CONSTRUCT_STRESS_TEST",human_inter_rater_reliability:false,source_sha256:A.metadata.source_sha256,reviewer_a_sha256:sha256(aPath),reviewer_b_sha256:sha256(bPath),created_at:new Date().toISOString()},dimensions:metrics,flags:flagSummary,case_ids_requiring_adjudication:escalated.map(x=>x.case_id)};

fs.mkdirSync(outDir,{recursive:true});
const metricsPath=path.join(outDir,"synthetic_agreement_metrics_v1.0.json");
const registerPath=path.join(outDir,"synthetic_adjudication_register_v1.0.json");
fs.writeFileSync(metricsPath,JSON.stringify(result,null,2)+"\n");
fs.writeFileSync(registerPath,JSON.stringify({metadata:result.metadata,cases:register},null,2)+"\n");

const rows=dims.map(d=>`| ${d.replaceAll("_"," ")} | ${(100*metrics[d].exact_agreement).toFixed(1)}% | ${(100*metrics[d].within_one_agreement).toFixed(1)}% | ${metrics[d].mean_absolute_difference.toFixed(3)} | ${metrics[d].linear_weighted_kappa.toFixed(3)} |`).join("\n");
const memo=`# Synthetic Construct Review Memorandum v1.0\n\n## Status\n\nThis is an AI–AI rubric stress test. It is not human inter-rater reliability, expert validation, or evidence of organizational effectiveness.\n\n## Agreement\n\n| Dimension | Exact | Within one | Mean absolute difference | Linear weighted kappa |\n|---|---:|---:|---:|---:|\n${rows}\n\n## Flags\n\n- Reviewer A non-NO leakage flags: ${flagSummary.reviewer_a_leakage_non_no}\n- Reviewer B non-NO leakage flags: ${flagSummary.reviewer_b_leakage_non_no}\n- Reviewer A ambiguity flags: ${flagSummary.reviewer_a_ambiguity_yes}\n- Reviewer B ambiguity flags: ${flagSummary.reviewer_b_ambiguity_yes}\n- Cases requiring adjudication under the frozen rule: ${flagSummary.cases_requiring_adjudication}\n\n## Decision rule\n\nNo score is automatically averaged. Every escalated case remains open in the adjudication register. A clarity-only revision may be authorized after reviewing those disagreements without consulting policy outputs or investigator reference labels.\n`;
const memoPath=path.join(outDir,"SYNTHETIC_CONSTRUCT_REVIEW_MEMORANDUM_v1.0.md");
fs.writeFileSync(memoPath,memo);
const outputs=[metricsPath,registerPath,memoPath];
const manifest={manifest_version:"1.0",status:"SYNTHETIC_REVIEW_OUTPUT_LOCK",human_validation:false,created_at:new Date().toISOString(),artifacts:[aPath,bPath,...outputs].map(p=>({relative_path:path.relative(root,p),sha256:sha256(p),bytes:fs.statSync(p).size}))};
fs.writeFileSync(path.join(outDir,"SYNTHETIC_REVIEW_LOCK_v1.0.json"),JSON.stringify(manifest,null,2)+"\n");
console.log(JSON.stringify({metrics,flags:flagSummary,case_ids_requiring_adjudication:escalated.map(x=>x.case_id),outDir},null,2));
