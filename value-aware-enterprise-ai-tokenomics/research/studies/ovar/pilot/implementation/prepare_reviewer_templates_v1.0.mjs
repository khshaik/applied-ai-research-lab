import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(here,"..");
const sourcePath=path.join(root,"cases/candidate_v1.0/reviewer_visible_cases.json");
const source=JSON.parse(fs.readFileSync(sourcePath,"utf8"));
const sourceHash=crypto.createHash("sha256").update(fs.readFileSync(sourcePath)).digest("hex");
const reviewDir=path.join(root,"review");

for(const reviewer_id of ["REVIEWER_A","REVIEWER_B"]){
  const template={
    metadata:{study:"OVAR constructed pilot",version:"1.0",reviewer_id,blinded:true,source_sha256:sourceHash,ground_truth_accessed:false,policy_outputs_accessed:false,other_reviewer_scores_accessed:false},
    reviews:source.cases.map(c=>({case_id:c.case_id,outcome_contract_clarity:null,baseline_credibility:null,evidence_auditability:null,cost_boundary_completeness:null,attribution_defensibility:null,decision_realism:null,leakage_flag:"NO",ambiguity_flag:"NO",missing_information:"",boundary_rationale:""}))
  };
  fs.mkdirSync(reviewDir,{recursive:true});
  fs.writeFileSync(path.join(reviewDir,`${reviewer_id.toLowerCase()}_blank_v1.0.json`),JSON.stringify(template,null,2)+"\n");
}
console.log(JSON.stringify({templates:2,source_sha256:sourceHash,reviewDir}));
