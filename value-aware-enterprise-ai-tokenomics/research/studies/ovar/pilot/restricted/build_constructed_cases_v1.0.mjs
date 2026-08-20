import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const pilotRoot = path.resolve(here, "..");
const publicDir = path.join(pilotRoot, "cases", "candidate_v1.0");
const restrictedDir = path.join(pilotRoot, "restricted");

const domains = [
  "HEALTHCARE", "FINANCIAL_SERVICES", "ECOMMERCE",
  "TRANSPORT_LOGISTICS", "CYBERSECURITY", "CUSTOMER_OPERATIONS",
];

const raw = [
  ["OV-P01","PF-A",domains[0],"PILOT","Emergency-discharge instruction drafting","A retrieval-grounded assistant drafts patient-specific discharge instructions for clinician approval.",60,18000,.82,46,13.2,4200,900,600,1600,2200,500,400,.91,31000,true,"Reduce clinician documentation time while maintaining medication-instruction accuracy above 98% during the 60-day window.",43000,17000,"VERIFIED","MATCHED_CONCURRENT",.82,3500,300,"PASS",900,"STANDARD",false,33000,10400,300,22300,18800,25800,true,true],
  ["OV-P02","PF-B",domains[0],"PILOT","Radiology report summarization","A language model produces patient-facing summaries that are reviewed before release.",45,14000,.88,31,18.4,5100,850,500,2500,1600,600,3900,.86,26000,true,"Decrease explanation time without increasing corrected clinical statements in released summaries.",30000,12000,"VERIFIED","INTERRUPTED_TIME_SERIES",.70,4500,600,"PASS",1200,"STANDARD",false,17500,15050,700,1750,-1500,5000,true,true],
  ["OV-P03","PF-C",domains[0],"PRE_PRODUCTION","Prior-authorization recommendation support","An agent recommends approval rationales from clinical and payer-policy records.",90,30000,.79,68,21.0,6800,1500,1000,4300,5200,1300,900,.89,52000,true,"Reduce authorization handling time while preserving policy compliance and clinician oversight.",60000,23000,"PARTIAL","STEPPED_WEDGE",.68,7000,2600,"PROHIBITED",1700,"MINIMUM_ACCESS",false,39000,21000,9000,9000,2000,16000,true,false],
  ["OV-P04","PF-D",domains[0],"POC","Outpatient appointment no-show prediction","A predictive assistant ranks appointments for reminder outreach.",30,9000,.66,14,5.8,1800,500,250,900,1300,300,200,.78,15000,false,"",19000,null,"UNVERIFIED","NONE",.32,6500,200,"CONDITIONAL",1600,"EXPLORATION",true,9000,5250,400,3350,-1000,7700,false,true],

  ["OV-P05","PF-A",domains[1],"PILOT","Know-your-customer document review","A multimodal assistant extracts identity evidence and flags inconsistencies for analyst review.",60,22000,.76,52,16.0,4800,1200,700,2100,3000,900,500,.90,42000,true,"Reduce analyst review minutes per completed KYC file without increasing missed mandatory checks.",51000,19000,"VERIFIED","RANDOMIZED",.86,4000,500,"PASS",1100,"STANDARD",false,36000,13200,500,22300,18300,26300,true,true],
  ["OV-P06","PF-B",domains[1],"PILOT","Fraud-alert narrative assistance","A model drafts alert narratives from transaction and case metadata for investigator review.",45,16000,.58,33,11.5,3300,800,450,1900,1800,450,700,.79,24000,true,"Lower narrative preparation time while maintaining investigator acceptance and escalation accuracy.",31500,13000,"VERIFIED","MATCHED_CONCURRENT",.72,5200,1000,"PASS",900,"STANDARD",false,11900,9400,900,1600,500,2700,true,true],
  ["OV-P07","PF-C",domains[1],"PRE_PRODUCTION","Consumer-credit underwriting explanation","An assistant generates adverse-action explanations from model and application features.",90,28000,.84,61,19.7,5900,1200,800,3500,4500,1200,2600,.88,57000,true,"Reduce explanation preparation time while meeting adverse-action and fairness requirements.",62000,21000,"PARTIAL","BEFORE_AFTER_UNCONTROLLED",.58,8000,6800,"PROHIBITED",2000,"MINIMUM_ACCESS",false,24000,19700,8500,-4200,-9000,600,true,false],
  ["OV-P08","PF-D",domains[1],"POC","Treasury variance commentary","A language model drafts monthly variance explanations from approved ledger extracts.",30,10000,.69,19,6.3,2100,450,300,1000,1400,400,350,.83,19000,true,"Reduce preparation time for accepted variance commentary without increasing factual corrections.",25500,11000,"PARTIAL","BEFORE_AFTER_UNCONTROLLED",.61,6000,200,"PASS",1000,"EXPLORATION",true,14500,6000,300,8200,-800,17200,true,true],

  ["OV-P09","PF-A",domains[2],"PILOT","Catalog product-description generation","A grounded generator drafts descriptions from verified product attributes for editor approval.",45,15000,.81,42,14.8,3900,600,550,1700,1900,450,600,.92,34000,true,"Increase accepted catalog entries per editor hour without increasing attribute-error returns.",41000,15000,"VERIFIED","RANDOMIZED",.88,3200,250,"PASS",800,"STANDARD",false,30000,9700,300,20000,16800,23200,true,true],
  ["OV-P10","PF-B",domains[2],"PILOT","Returns-resolution chat agent","An agent proposes return eligibility and resolution steps for service representatives.",60,17000,.90,75,20.5,5400,900,650,3200,2300,650,4100,.87,39000,true,"Reduce handling time while maintaining correct return-policy application and repeat-contact rate.",46000,17000,"VERIFIED","STEPPED_WEDGE",.76,5000,1100,"PASS",1300,"STANDARD",false,19000,17200,1300,500,-4500,5500,true,true],
  ["OV-P11","PF-C",domains[2],"PRE_PRODUCTION","Personalized offer recommendation","A recommendation service selects promotional offers using browsing and purchase signals.",90,26000,.77,120,24.0,6500,1500,1000,2500,3900,1100,700,.90,61000,true,"Increase incremental contribution margin per eligible visitor subject to consent and offer-fairness constraints.",69000,26000,"PARTIAL","MATCHED_CONCURRENT",.66,8000,7600,"PROHIBITED",1900,"MINIMUM_ACCESS",false,44000,17200,8500,18300,9000,27600,true,false],
  ["OV-P12","PF-D",domains[2],"POC","Natural-language storefront search","A retrieval system rewrites queries and reranks products for low-result searches.",30,11000,.52,18,7.0,2400,500,350,1100,1600,350,250,.81,17500,true,"Increase successful product discovery for low-result queries without increasing irrelevant clicks.",24500,10500,"VERIFIED","MATCHED_CONCURRENT",.74,3800,200,"PASS",900,"EXPLORATION",true,8000,6550,200,1250,250,2250,true,true],

  ["OV-P13","PF-A",domains[3],"PILOT","Last-mile dispatch optimization","An AI planner proposes route and stop assignments that dispatchers approve before release.",60,24000,.73,55,15.5,4600,1100,650,2300,3400,800,500,.88,47000,true,"Reduce fuel and late-delivery cost per route while preserving driver-hour and service constraints.",57000,21000,"VERIFIED","STEPPED_WEDGE",.84,4500,700,"PASS",1200,"STANDARD",false,40000,13350,700,25950,21450,30450,true,true],
  ["OV-P14","PF-B",domains[3],"PILOT","Shipment ETA explanation","A model generates customer ETA explanations from carrier events and route status.",45,13000,.64,28,9.5,3000,650,400,1600,1500,400,550,.82,21000,true,"Reduce manual ETA enquiries without increasing inaccurate promise-window statements.",29000,14000,"PARTIAL","INTERRUPTED_TIME_SERIES",.63,5200,800,"PASS",1000,"STANDARD",false,13000,8100,700,4200,-1000,9400,true,true],
  ["OV-P15","PF-C",domains[3],"POC","Warehouse replenishment suggestion","An assistant recommends replenishment quantities from demand and stock telemetry.",30,12000,.71,22,8.4,2700,700,450,1500,1800,500,350,.80,26000,false,"",32000,null,"UNVERIFIED","NONE",.40,7000,1200,"CONDITIONAL",1400,"EXPLORATION",true,18500,8000,1100,9400,2400,16400,false,true],
  ["OV-P16","PF-D",domains[3],"PILOT","Freight-document extraction","A multimodal model extracts shipment fields for operations staff to confirm.",60,15500,.83,39,17.2,4700,900,600,3100,2100,550,300,.84,30000,true,"Reduce manual data-entry cost while holding corrected extraction errors below the registered limit.",33000,14500,"VERIFIED","MATCHED_CONCURRENT",.77,4500,300,"PASS",850,"STANDARD",false,16000,12250,350,3400,-1100,7900,true,true],

  ["OV-P17","PF-A",domains[4],"PILOT","Security-alert triage","An analyst copilot clusters alerts, retrieves runbooks, and drafts triage summaries.",60,21000,.78,49,18.0,5200,1000,750,2600,2800,900,650,.91,46000,true,"Reduce analyst minutes per correctly resolved alert without increasing missed high-severity incidents.",56000,20000,"VERIFIED","RANDOMIZED",.87,4800,1000,"PASS",1500,"STANDARD",false,39000,13900,900,24200,19400,29000,true,true],
  ["OV-P18","PF-B",domains[4],"PILOT","Incident-response command suggestion","An agent proposes containment commands that require analyst approval before execution.",45,20000,.62,25,12.0,4100,850,650,2800,2500,1200,800,.80,37000,true,"Reduce time to approved containment while avoiding unsafe or unauthorized command proposals.",43000,18000,"PARTIAL","MATCHED_CONCURRENT",.60,8500,5200,"CONDITIONAL",2100,"STANDARD",false,21000,12900,4800,3300,-5200,11800,true,true],
  ["OV-P19","PF-C",domains[4],"POC","Vulnerability remediation prioritization","A model ranks vulnerabilities using asset and threat context for security-engineering review.",30,10000,.70,16,6.1,1900,500,300,1000,1300,400,250,.85,22000,false,"",28000,null,"UNVERIFIED","NONE",.35,7500,700,"CONDITIONAL",1700,"EXPLORATION",true,15000,5650,600,8750,1250,16250,false,true],
  ["OV-P20","PF-D",domains[4],"PILOT","Phishing-report classification","A classifier prioritizes employee-reported messages for analyst investigation.",60,14500,.86,81,16.8,4400,700,500,2300,1700,500,2900,.89,33000,true,"Reduce triage time while preserving detection of credential-theft messages and controlling analyst rework.",38000,15000,"VERIFIED","INTERRUPTED_TIME_SERIES",.73,5000,900,"PASS",1000,"STANDARD",false,15000,13000,900,1100,-3900,6100,true,true],

  ["OV-P21","PF-A",domains[5],"PILOT","Service-case response assistance","A grounded assistant drafts responses from policy and account records for representative approval.",60,19000,.80,92,22.0,5800,850,650,2500,2300,650,700,.93,48000,true,"Reduce handling time per accepted response without increasing repeat contact or policy error.",59000,22000,"VERIFIED","STEPPED_WEDGE",.85,4200,400,"PASS",1200,"STANDARD",false,41000,13450,450,27100,22900,31300,true,true],
  ["OV-P22","PF-B",domains[5],"POC","Account-manager email drafting","An assistant prepares follow-up drafts from CRM notes for account-manager editing.",30,9000,.38,12,4.2,1500,350,250,950,1200,250,150,.76,12000,true,"Reduce drafting time for accepted follow-up emails without increasing correction or opt-out rates.",16500,8500,"VERIFIED","MATCHED_CONCURRENT",.71,2600,100,"PASS",700,"EXPLORATION",true,5600,4650,100,850,200,1500,true,true],
  ["OV-P23","PF-C",domains[5],"PRE_PRODUCTION","Churn-retention outreach","An agent identifies accounts and drafts retention offers for representative review.",90,25000,.85,105,27.0,7200,1200,850,4300,3600,900,5200,.88,65000,true,"Increase incremental retained margin net of offer cost without increasing inappropriate-contact complaints.",71000,24000,"PARTIAL","BEFORE_AFTER_UNCONTROLLED",.56,9500,2600,"PASS",2200,"MINIMUM_ACCESS",false,20500,23250,2400,-5150,-14650,4350,true,true],
  ["OV-P24","PF-D",domains[5],"PILOT","Multilingual support translation","A language model translates service conversations, with sampled bilingual quality review.",45,12500,.67,37,10.4,3200,550,450,1900,1500,400,450,.84,25000,true,"Reduce interpreter and handling cost while meeting registered translation-accuracy and escalation thresholds.",31000,14000,"PARTIAL","INTERRUPTED_TIME_SERIES",.64,6100,700,"PASS",1100,"STANDARD",false,14500,8450,650,5400,-700,11500,true,true]
];

const visible = raw.map((r) => ({
  case_id:r[0], portfolio_id:r[1], domain:r[2], provenance:"CONSTRUCTED", project_stage:r[3], workflow:r[4], ai_intervention:r[5],
  measurement_window_days:r[6], approved_budget:r[7], utilization_rate:r[8], active_users:r[9], token_units_m:r[10],
  provider_cost:r[11], infrastructure_cost:r[12], tooling_cost:r[13], human_review_cost:r[14], integration_amortized_cost:r[15],
  governance_cost:r[16], rework_cost:r[17], technical_quality:r[18], owner_reported_gross_benefit:r[19], outcome_contract_present:r[20],
  outcome_contract:r[21], observed_outcome_value:r[22], baseline_estimated_outcome_value:r[23], evidence_status:r[24], baseline_design:r[25],
  attribution_confidence:r[26], uncertainty_half_width:r[27], expected_harm_cost:r[28], compliance_status:r[29], evidence_review_cost:r[30],
  access_class:r[31], exploration_protected:r[32], authoring_version:"1.0"
}));

function classifyReference(r) {
  const [trueValue,trueCost,trueHarm,net,lower,upper,sufficient,compliance] = r.slice(33,41);
  if (!sufficient) return ["INDETERMINATE","INDETERMINATE"];
  if (!compliance || upper < 0) return ["NEGATIVE","STOP"];
  if (lower > 0) return ["POSITIVE", (net / trueCost >= .20 ? "SCALE" : "CONTINUE_PILOT")];
  if (lower >= -.05 * trueCost && upper <= .05 * trueCost) return ["NEUTRAL","REVISE"];
  return ["NEUTRAL","REVISE"];
}

const reference = raw.map((r) => {
  const [roi, action] = classifyReference(r);
  return {
    case_id:r[0], true_incremental_value:r[33], true_fully_loaded_cost:r[34], true_expected_harm_cost:r[35],
    reference_net_value:r[36], reference_lower_bound:r[37], reference_upper_bound:r[38], reference_evidence_sufficient:r[39],
    reference_compliance_pass:r[40], reference_roi_state:roi, reference_action:action, label_version:"1.0"
  };
});

for (const r of raw) {
  const sum = r.slice(11,18).reduce((a,b) => a+b, 0);
  if (Math.abs(sum - r[34]) > 1e-9) throw new Error(`Cost reconciliation failed for ${r[0]}: ${sum} != ${r[34]}`);
  if (Math.abs((r[33] - r[34] - r[35]) - r[36]) > 1e-9) throw new Error(`Reference net failed for ${r[0]}`);
}

fs.mkdirSync(publicDir, {recursive:true});
fs.writeFileSync(path.join(publicDir, "reviewer_visible_cases.json"), JSON.stringify({metadata:{study:"OVAR constructed pilot",version:"1.0",case_count:visible.length,label_access:false},cases:visible}, null, 2) + "\n");
fs.writeFileSync(path.join(restrictedDir, "investigator_reference_RESTRICTED_v1.0.json"), JSON.stringify({metadata:{study:"OVAR constructed pilot",version:"1.0",restricted:true,case_count:reference.length},references:reference}, null, 2) + "\n");

console.log(JSON.stringify({visible_cases:visible.length, reference_records:reference.length, publicDir, restrictedDir}));
