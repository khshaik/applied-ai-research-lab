import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
const here=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(here,".."),project=path.resolve(root,"..");
const rel=[
 "calibration/CALIBRATION_PRE_EXECUTION_LOCK_v1.2.json",
 "calibration/CALIBRATION_IMPLEMENTATION_REVISION_LOG_v1.0.md",
 "calibration/results/calibration_v1.0/policy_decisions.json",
 "calibration/results/calibration_v1.0/calibration_gate.json",
 "calibration/results/calibration_v1.0/CALIBRATION_DECISION_MEMORANDUM_v1.0.md"
];
const sha=p=>crypto.createHash("sha256").update(fs.readFileSync(p)).digest("hex"),artifacts=rel.map(relative_path=>{const p=path.join(project,relative_path);return{relative_path,sha256:sha(p),bytes:fs.statSync(p).size};});
const closure={closure_version:"1.0",status:"CALIBRATION_CLOSED_NEGATIVE_GATE",gate_decision:"STOP_OVAR_V1_NO_HELD_OUT",confirmatory:false,field_validation:false,human_validation:false,held_out_created:false,rerun_permitted:false,created_at:new Date().toISOString(),artifacts};
const out=path.join(root,"CALIBRATION_CLOSURE_MANIFEST_v1.0.json");fs.writeFileSync(out,JSON.stringify(closure,null,2)+"\n");console.log(JSON.stringify({out,artifacts:artifacts.length,sha256:sha(out)}));
