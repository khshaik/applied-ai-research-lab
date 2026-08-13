import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
const here=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(here,".."),project=path.resolve(root,"..");
const rel=[
 "calibration/CALIBRATION_DESIGN_PROTOCOL_v1.0.md",
 "calibration/REFERENCE_ADJUDICATION_PROTOCOL_v1.0.md",
 "calibration/PROSPECTIVE_ANALYSIS_PLAN_v1.0.md",
 "calibration/CALIBRATION_IMPLEMENTATION_REVISION_LOG_v1.0.md",
 "calibration/schema/construct_review_case_schema_v1.0.json",
 "calibration/schema/reference_record_schema_v1.0.json",
 "calibration/candidate_v1.1/construct_review_cases.json",
 "calibration/restricted/construction_registry_RESTRICTED_v1.1.json",
 "calibration/restricted/reference_labels_RESTRICTED_v1.0.json",
 "calibration/review/consolidated_v1.1/construct_recheck_metrics_v1.1.json",
 "calibration/review/consolidated_v1.1/CONSTRUCT_RECHECK_LOCK_v1.1.json",
 "calibration/tests/candidate_v1.0.test.mjs",
 "calibration/tests/reference_labels_v1.0.test.mjs",
 "calibration/implementation/calibration_policies_v1.0.mjs",
 "calibration/tests/calibration_policies_v1.0.test.mjs",
 "calibration/implementation/run_calibration_once_v1.0.mjs"
];
const sha=p=>crypto.createHash("sha256").update(fs.readFileSync(p)).digest("hex");
const artifacts=rel.map(relative_path=>{const p=path.join(project,relative_path);return{relative_path,sha256:sha(p),bytes:fs.statSync(p).size};});
const lock={lock_version:"1.2",status:"CALIBRATION_PRE_EXECUTION_LOCK",created_at:new Date().toISOString(),execution_authorized:true,policy_results_absent:!fs.existsSync(path.join(root,"results/calibration_v1.0")),reference_labels_constructed:true,human_validation:false,case_count:48,revision_reason:"Minimal mkdir recursive-parent fix after pre-output ENOENT; no scientific input, policy, threshold, label, or metric changed.",artifacts};
if(!lock.policy_results_absent)throw Error("Result directory exists; refusing to create a prospective lock");
const out=path.join(root,"CALIBRATION_PRE_EXECUTION_LOCK_v1.2.json");fs.writeFileSync(out,JSON.stringify(lock,null,2)+"\n");console.log(JSON.stringify({out,artifacts:artifacts.length,sha256:sha(out)}));
