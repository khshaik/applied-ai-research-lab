import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(here,"..");
const sourcePath=path.join(root,"candidate_v1.0/construct_review_cases.json");
const source=JSON.parse(fs.readFileSync(sourcePath,"utf8"));
const salt="OVAR-CALIBRATION-NEUTRAL-ID-MAP-v1.1";
const sha=x=>crypto.createHash("sha256").update(x).digest("hex");

const ranked=source.cases.map(c=>({old:c.case_id,key:sha(`${salt}:${c.case_id}`)})).sort((a,b)=>a.key.localeCompare(b.key));
const idMap=new Map(ranked.map((x,i)=>[x.old,`OC-R${String(i+1).padStart(3,"0")}`]));
const registry=source.cases.map(c=>({original_case_id:c.case_id,review_case_id:idMap.get(c.case_id),domain:c.domain,construction_stratum:c.stratum}));
const cases=source.cases.map(c=>{
  const {stratum,...rest}=c;
  return {...rest,case_id:idMap.get(c.case_id),authoring_version:"calibration-1.1-review"};
}).sort((a,b)=>a.case_id.localeCompare(b.case_id));

const oldById=new Map(source.cases.map(c=>[c.case_id,c]));
for(const r of registry){const revised=cases.find(c=>c.case_id===r.review_case_id),old=oldById.get(r.original_case_id);for(const k of Object.keys(old)){if(k==="case_id"||k==="stratum"||k==="authoring_version")continue;if(JSON.stringify(old[k])!==JSON.stringify(revised[k]))throw Error(`Unexpected content change ${r.original_case_id}:${k}`);}}

const outDir=path.join(root,"candidate_v1.1"),restrictedDir=path.join(root,"restricted");fs.mkdirSync(outDir,{recursive:true});fs.mkdirSync(restrictedDir,{recursive:true});
const outPath=path.join(outDir,"construct_review_cases.json"),registryPath=path.join(restrictedDir,"construction_registry_RESTRICTED_v1.1.json");
fs.writeFileSync(outPath,JSON.stringify({metadata:{study:"OVAR prospective calibration",version:"1.1-review",case_count:48,construction_strata_visible:false,reference_labels_present:false,policy_outputs_present:false,revision_reason:"Remove stratum disclosure and ID-order shortcut before reference adjudication.",source_v1_sha256:sha(fs.readFileSync(sourcePath))},cases},null,2)+"\n");
fs.writeFileSync(registryPath,JSON.stringify({metadata:{restricted:true,version:"1.1",mapping_method:"SHA-256 rank using fixed versioned salt",contains_reference_labels:false},registry},null,2)+"\n");
console.log(JSON.stringify({cases:cases.length,visible_sha256:sha(fs.readFileSync(outPath)),registry_sha256:sha(fs.readFileSync(registryPath)),unchanged_content_fields_verified:true}));
