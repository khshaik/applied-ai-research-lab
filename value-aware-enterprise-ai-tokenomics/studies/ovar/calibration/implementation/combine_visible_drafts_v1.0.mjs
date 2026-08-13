import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(here,"..");
const drafts=[path.join(root,"drafts/constructor_a_visible_24_v1.0.json"),path.join(root,"drafts/constructor_b_visible_24_v1.0.json")];
for(const p of drafts)if(!fs.existsSync(p))throw Error(`Missing ${p}`);
const unpack=x=>Array.isArray(x)?x:(x.cases??x.records??x.construct_review_cases??[]);
const stratumMap={
  HIGH_VERIFIED_VALUE_MODERATE_USAGE:"HIGH_VALUE_MODERATE_USAGE",
  HIGH_USAGE_NEGATIVE_OR_NEUTRAL_INCREMENTAL_VALUE:"HIGH_USAGE_LOW_VALUE",
  POSITIVE_TECHNICAL_QUALITY_HIDDEN_FULLY_LOADED_COST:"HIDDEN_FULLY_LOADED_COST",
  WEAK_OR_ABSENT_COUNTERFACTUAL_EVIDENCE:"WEAK_OR_ABSENT_COUNTERFACTUAL",
  DELAYED_OR_SHARED_OUTCOME_ATTRIBUTION:"DELAYED_OR_SHARED_ATTRIBUTION",
  GENUINE_COMPLIANCE_OR_AUTHORIZATION_CONSTRAINT:"AUTHORIZATION_OR_COMPLIANCE_CONSTRAINT",
  LOW_ADOPTION_CREDIBLE_HIGH_VALUE:"LOW_ADOPTION_HIGH_VALUE",
  DIFFICULT_REVISE_VERSUS_INDETERMINATE_BOUNDARY:"REVISE_INDETERMINATE_BOUNDARY",
  S01_VERIFIED_VALUE_MODERATE_USAGE:"HIGH_VALUE_MODERATE_USAGE",
  S02_HIGH_USAGE_LIMITED_INCREMENT:"HIGH_USAGE_LOW_VALUE",
  S03_TECHNICAL_QUALITY_COST_BOUNDARY:"HIDDEN_FULLY_LOADED_COST",
  S04_COUNTERFACTUAL_GAP:"WEAK_OR_ABSENT_COUNTERFACTUAL",
  S05_SHARED_OR_DELAYED_ATTRIBUTION:"DELAYED_OR_SHARED_ATTRIBUTION",
  S06_AUTHORIZATION_CONSTRAINT:"AUTHORIZATION_OR_COMPLIANCE_CONSTRAINT",
  S07_LOW_ADOPTION_CREDIBLE_VALUE:"LOW_ADOPTION_HIGH_VALUE",
  S08_EVIDENCE_BOUNDARY:"REVISE_INDETERMINATE_BOUNDARY"
};
const cases=drafts.flatMap(p=>unpack(JSON.parse(fs.readFileSync(p,"utf8")))).map(c=>({...c,stratum:stratumMap[c.stratum]??c.stratum}));
const domains=["HEALTHCARE","FINANCIAL_SERVICES","ECOMMERCE","TRANSPORT_LOGISTICS","CYBERSECURITY","CUSTOMER_OPERATIONS"];
const strata=["HIGH_VALUE_MODERATE_USAGE","HIGH_USAGE_LOW_VALUE","HIDDEN_FULLY_LOADED_COST","WEAK_OR_ABSENT_COUNTERFACTUAL","DELAYED_OR_SHARED_ATTRIBUTION","AUTHORIZATION_OR_COMPLIANCE_CONSTRAINT","LOW_ADOPTION_HIGH_VALUE","REVISE_INDETERMINATE_BOUNDARY"];
const forbidden=[/\bprohibited\b/i,/\bmust stop\b/i,/\bmust scale\b/i,/\bpositive roi\b/i,/\bnegative roi\b/i,/cannot support a positive/i,/attribution (?:is )?therefore capped/i,/preferred policy/i,/reference decision/i,/\btrue_[a-z_]+\b/i,/\breference_[a-z_]+\b/i];
if(cases.length!==48||new Set(cases.map(x=>x.case_id)).size!==48)throw Error("48 unique IDs required");
for(const d of domains){const rows=cases.filter(x=>x.domain===d);if(rows.length!==8)throw Error(`${d} count`);for(const s of strata)if(rows.filter(x=>x.stratum===s).length!==1)throw Error(`${d}:${s}`);}
for(const c of cases){
  if(c.provenance!=="CONSTRUCTED"||c.authoring_version!=="calibration-1.0-draft")throw Error(`${c.case_id}: provenance/version`);
  if(c.attribution_confidence<0||c.attribution_confidence>1||c.technical_quality<0||c.technical_quality>1||c.utilization_rate<0||c.utilization_rate>1)throw Error(`${c.case_id}: range`);
  if(Object.values(c.cost_components).some(x=>typeof x!=="number"||x<0))throw Error(`${c.case_id}: cost`);
  const text=JSON.stringify(c);for(const f of forbidden)if(f.test(text))throw Error(`${c.case_id}: forbidden ${f}`);
}
const ordered=cases.sort((a,b)=>a.case_id.localeCompare(b.case_id));
const outDir=path.join(root,"candidate_v1.0");fs.mkdirSync(outDir,{recursive:true});
const outPath=path.join(outDir,"construct_review_cases.json");
const sha=p=>crypto.createHash("sha256").update(fs.readFileSync(p)).digest("hex");
fs.writeFileSync(outPath,JSON.stringify({metadata:{study:"OVAR prospective calibration",version:"1.0-draft",case_count:48,reference_labels_present:false,policy_outputs_present:false,constructors:drafts.map(p=>({file:path.basename(p),sha256:sha(p)}))},cases:ordered},null,2)+"\n");
console.log(JSON.stringify({cases:48,domains:domains.length,strata_per_domain:8,output:outPath,sha256:sha(outPath)}));
