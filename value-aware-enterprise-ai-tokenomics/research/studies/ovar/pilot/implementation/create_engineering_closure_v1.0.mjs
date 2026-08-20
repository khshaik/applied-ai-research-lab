import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(here,"..");
const project=path.resolve(root,"..");
const relFiles=[
  "pilot/PILOT_PROTOCOL_v1.0.md",
  "pilot/DATA_GOVERNANCE_AND_ADJUDICATION_v1.0.md",
  "pilot/REVIEWER_INSTRUCTIONS_v1.0.md",
  "pilot/schema/outcome_evidence_ledger_schema_v1.0.json",
  "pilot/schema/investigator_reference_schema_v1.0.json",
  "pilot/schema/reviewer_response_schema_v1.0.json",
  "pilot/cases/candidate_v1.0/reviewer_visible_cases.json",
  "pilot/restricted/investigator_reference_RESTRICTED_v1.0.json",
  "pilot/implementation/ovar_pilot_v1.0.mjs",
  "pilot/implementation/run_pilot_v1.0.mjs",
  "pilot/tests/pilot_v1.0.test.mjs",
  "pilot/results/pilot_v1.0/policy_decisions.json",
  "pilot/results/pilot_v1.0/pilot_metrics_pretest.json"
];
const sha256=(p)=>crypto.createHash("sha256").update(fs.readFileSync(p)).digest("hex");
const artifacts=relFiles.map(relative_path=>{const absolute=path.join(project,relative_path);return {relative_path,sha256:sha256(absolute),bytes:fs.statSync(absolute).size};});
const manifest={
  manifest_version:"1.0",
  study:"OVAR constructed pilot",
  status:"ENGINEERING_DRY_RUN_CLOSURE",
  confirmatory:false,
  prospective:false,
  outcomes_observed_before_manifest:true,
  permissible_claim:"Implementation feasibility and constructed-case behavior only.",
  prohibited_claims:["prospective validation","organizational ROI improvement","field effectiveness","production readiness"],
  created_at:new Date().toISOString(),
  artifacts
};
fs.writeFileSync(path.join(root,"PILOT_ENGINEERING_DRY_RUN_CLOSURE_MANIFEST_v1.0.json"),JSON.stringify(manifest,null,2)+"\n");
console.log(JSON.stringify({artifacts:artifacts.length,manifest:path.join(root,"PILOT_ENGINEERING_DRY_RUN_CLOSURE_MANIFEST_v1.0.json")}));
