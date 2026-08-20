import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(here,"..");
const sourcePath=path.join(root,"cases/candidate_v1.0/reviewer_visible_cases.json");
const source=JSON.parse(fs.readFileSync(sourcePath,"utf8"));
const outDir=path.join(root,"cases","candidate_v1.1");
const sha256=b=>crypto.createHash("sha256").update(b).digest("hex");

const acceptance={
  "OV-P01":"Median documentation minutes decrease by at least 20%, medication-instruction accuracy is at least 98%, and no severe medication omission occurs.",
  "OV-P02":"Median explanation time decreases by at least 15%, corrected clinical-statement rate does not exceed the 3% non-inferiority limit, and sampled readability improves by at least one rubric point.",
  "OV-P03":"Median authorization handling time decreases by at least 20%, mandatory-check completion remains at 100%, and no recommendation bypasses clinician approval.",
  "OV-P04":"Completed reminder contacts per coordinator hour increase by at least 15% and the no-show rate decreases by at least 5% relative to the registered comparison.",
  "OV-P05":"Median analyst minutes per completed KYC file decrease by at least 25%, missed mandatory checks remain below 1%, and false escalations do not rise by more than 2 percentage points.",
  "OV-P06":"Median narrative-preparation time decreases by at least 20%, investigator acceptance is at least 85%, and escalation accuracy remains within a 2-point non-inferiority margin.",
  "OV-P07":"Median preparation time decreases by at least 20%, required adverse-action factors appear in 100% of released explanations, and group-level error-rate disparity does not worsen by more than 2 points.",
  "OV-P08":"Accepted commentary hours decrease by at least 15% while factual-correction frequency remains below 5% and every cited variance reconciles to the approved ledger extract.",
  "OV-P09":"Accepted catalog entries per editor hour increase by at least 25%, attribute-error rate remains below 1%, and attribute-related return rate does not increase by more than 0.5 points.",
  "OV-P10":"Median handling time decreases by at least 15%, incorrect eligibility decisions remain below 2%, and repeat-contact rate does not increase by more than 2 points.",
  "OV-P11":"Incremental contribution margin per eligible visitor is positive with a lower bound above zero, consent eligibility is 100%, and offer-rate disparity remains within the approved 3-point limit.",
  "OV-P12":"Successful discovery among low-result queries increases by at least 10%, irrelevant-click rate does not increase by more than 2 points, and zero-result rate falls by at least 5%.",
  "OV-P13":"Fuel plus late-delivery cost per completed route decreases by at least 8%, on-time delivery does not worsen, and driver-hour limits have zero violations.",
  "OV-P14":"Manual ETA enquiries decrease by at least 15%, inaccurate promise-window statements remain below 2%, and repeat ETA contacts do not increase by more than 2 points.",
  "OV-P15":"Stockout cost falls by at least 8%, excess-inventory cost does not increase by more than 3%, and no replenishment breaches storage or safety constraints.",
  "OV-P16":"Manual entry minutes per shipment decrease by at least 20%, corrected extraction fields remain below 2%, and no mandatory customs field is omitted.",
  "OV-P17":"Median analyst minutes per correctly resolved alert decrease by at least 20%, missed high-severity incidents remain at zero, and false escalation does not increase by more than 2 points.",
  "OV-P18":"Median time to approved containment decreases by at least 15%, no unauthorized command reaches execution, and unsafe-command proposal rate remains below 1%.",
  "OV-P19":"Median time to an accepted remediation queue decreases by at least 15%, critical-asset recall remains at least 98%, and no protected exploration asset is excluded solely for missing history.",
  "OV-P20":"Median triage time decreases by at least 20%, credential-theft recall remains at least 99%, and analyst rework does not exceed the registered 5% ceiling.",
  "OV-P21":"Median handling time per accepted response decreases by at least 20%, policy-error rate remains below 1%, and repeat-contact rate does not increase by more than 2 points.",
  "OV-P22":"Median drafting time decreases by at least 15%, manager acceptance reaches at least 75%, and correction and opt-out rates do not rise by more than 2 and 0.5 points respectively.",
  "OV-P23":"Incremental retained margin net of offer cost has a lower bound above zero, inappropriate-contact complaints do not increase, and all contacted accounts satisfy eligibility rules.",
  "OV-P24":"Interpreter plus handling cost decreases by at least 15%, sampled translation accuracy is at least 95%, and missed mandatory escalation cues remain at zero."
};

const partialGaps={
  "OV-P03":"Only 70% of sampled policy-rule paths have completed independent review; rare exception paths remain unaudited.",
  "OV-P07":"Fairness assessment covers major groups but lacks sufficient observations for two smaller eligibility groups.",
  "OV-P08":"Accepted-commentary records are available, but correction reasons were not coded consistently in the first week.",
  "OV-P11":"Contribution-margin evidence is available, but cross-device consent linkage remains incomplete for part of the cohort.",
  "OV-P14":"Contact and promise-window logs are complete; carrier-caused exception attribution is incomplete.",
  "OV-P18":"Approval and execution logs are complete, but rejected unsafe-command proposals lack a uniform severity code.",
  "OV-P23":"Retention and offer-cost records are complete, but some delayed cancellations remain outside the current measurement window.",
  "OV-P24":"Operational samples are complete for four languages; two low-volume languages have fewer than the registered review count."
};

const baselineDetail={
  RANDOMIZED:"Eligible episodes are assigned 1:1 within site and complexity strata; analysis follows assigned group and records crossover.",
  STEPPED_WEDGE:"Operational units cross over on a prespecified schedule; the model includes unit and calendar-period effects and records concurrent interventions.",
  MATCHED_CONCURRENT:"AI-assisted episodes are matched to concurrent non-AI episodes on workflow type, complexity band, site, and operator-experience band before outcomes are inspected.",
  INTERRUPTED_TIME_SERIES:"Weekly outcome series includes at least eight pre-period and eight post-period observations with level, slope, seasonality, and concurrent-shock annotations.",
  BEFORE_AFTER_UNCONTROLLED:"The comparison uses the immediately preceding operating window without a concurrent control; attribution is therefore capped and alternative explanations must be listed.",
  NONE:"No defensible incremental comparator has been registered; the case cannot support a positive causal ROI classification."
};

const valuationByDomain={
  HEALTHCARE:"Value uses recorded staff minutes at loaded labor cost; clinical quality and safety outcomes remain separate non-monetary constraints.",
  FINANCIAL_SERVICES:"Value uses recorded analyst minutes and verified avoided processing cost; regulatory and fairness outcomes remain separate constraints.",
  ECOMMERCE:"Value uses experimentally or concurrently estimated contribution margin and recorded operating cost, net of discounts, returns, and review effort.",
  TRANSPORT_LOGISTICS:"Value uses reconciled fuel, labor, delay, inventory, or document-processing cost; service and safety outcomes remain separate constraints.",
  CYBERSECURITY:"Value uses recorded analyst time and approved incident-loss proxies; security severity is reported separately and is not monetized without an approved model.",
  CUSTOMER_OPERATIONS:"Value uses recorded handling or interpreter time and verified retained margin where applicable, net of review, offer, correction, and repeat-contact cost."
};

const harmByDomain={
  HEALTHCARE:"Expected harm is calculated from prespecified error categories, reviewed severity weights, and observed or bounded event probabilities; clinical harm is not collapsed into revenue.",
  FINANCIAL_SERVICES:"Expected harm combines prespecified compliance/fairness event probabilities with approved remediation-cost ranges; legal prohibitions remain hard constraints.",
  ECOMMERCE:"Expected harm covers consent, policy, customer-remediation, and fairness events using registered probability and cost ranges.",
  TRANSPORT_LOGISTICS:"Expected harm covers service, safety, labor-rule, inventory, and customs exceptions using registered operational severity bands.",
  CYBERSECURITY:"Expected harm uses registered incident-severity bands and bounded exposure probabilities; unauthorized execution is a hard constraint.",
  CUSTOMER_OPERATIONS:"Expected harm covers policy error, inappropriate contact, escalation, and customer-remediation events using registered severity bands."
};

const cases=source.cases.map(c=>({
  ...c,
  outcome_contract:`${c.outcome_contract_present?c.outcome_contract:"Outcome contract not yet registered."} Acceptance criteria: ${acceptance[c.case_id]}`,
  acceptance_criteria:acceptance[c.case_id],
  baseline_implementation:baselineDetail[c.baseline_design],
  evidence_locator:`CONSTRUCTED-EVIDENCE/${c.case_id}/v1.1`,
  evidence_reproduction_note:c.evidence_status==="UNVERIFIED"?"No eligible evidence package exists; the locator records the missing-evidence receipt only.":"The constructed evidence package identifies the measurement extract, evaluator rubric, reconciliation check, and content hash needed for replay.",
  evidence_gap:c.evidence_status==="PARTIAL"?partialGaps[c.case_id]:(c.evidence_status==="UNVERIFIED"?"Outcome evidence and comparator evidence have not passed independent review.":"No material evidence gap is registered for the constructed case."),
  valuation_method:valuationByDomain[c.domain],
  cost_allocation_method:"Provider, infrastructure, and tooling cost are assigned from workflow trace identifiers; human review and rework use recorded minutes at loaded rates; integration and governance are amortized over the measurement window using the registered allocation key.",
  harm_valuation_method:harmByDomain[c.domain],
  decision_checkpoint:`At day ${c.measurement_window_days}, the accountable portfolio committee chooses STOP, REVISE, CONTINUE_PILOT, SCALE, or INDETERMINATE and records a signed decision receipt.`,
  authoring_version:"1.1"
}));

fs.mkdirSync(outDir,{recursive:true});
const outPath=path.join(outDir,"reviewer_visible_cases.json");
const out={metadata:{...source.metadata,version:"1.1",clarity_revision_only:true,source_v1_sha256:sha256(fs.readFileSync(sourcePath)),decision_bearing_numeric_fields_changed:false,label_access:false},cases};
fs.writeFileSync(outPath,JSON.stringify(out,null,2)+"\n");

const preserved=["case_id","portfolio_id","domain","project_stage","measurement_window_days","approved_budget","utilization_rate","active_users","token_units_m","provider_cost","infrastructure_cost","tooling_cost","human_review_cost","integration_amortized_cost","governance_cost","rework_cost","technical_quality","owner_reported_gross_benefit","outcome_contract_present","observed_outcome_value","baseline_estimated_outcome_value","evidence_status","baseline_design","attribution_confidence","uncertainty_half_width","expected_harm_cost","compliance_status","evidence_review_cost","access_class","exploration_protected"];
for(let i=0;i<source.cases.length;i++)for(const key of preserved)if(source.cases[i][key]!==cases[i][key])throw new Error(`Decision-bearing field changed: ${cases[i].case_id}:${key}`);
console.log(JSON.stringify({cases:cases.length,outPath,source_sha256:out.metadata.source_v1_sha256,output_sha256:sha256(fs.readFileSync(outPath)),preserved_fields_verified:preserved.length}));
