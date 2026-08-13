import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import {
  AUTHORIZATION_STATUS,
  MEASUREMENT_BURDEN,
  POLICIES,
  POLICY_FIELDS,
  RISK_TIER,
  directCost,
  evaluate,
  expectedHarmCost,
  fullyLoadedCost,
  mapAuthorizationStatus,
  mapConstructReviewCase,
  mapRiskTier,
  outcomeFlat,
  ovarLedger,
  permittedView,
} from "../implementation/calibration_policies_v1.0.mjs";

const casesUrl = new URL("../candidate_v1.1/construct_review_cases.json", import.meta.url);
const implementationUrl = new URL("../implementation/calibration_policies_v1.0.mjs", import.meta.url);
const { cases } = JSON.parse(await readFile(casesUrl, "utf8"));

test("candidate fixture is the prospective 48-case set with unique IDs", () => {
  assert.equal(cases.length, 48);
  assert.equal(new Set(cases.map(({ case_id }) => case_id)).size, 48);
});

test("nested costs map and reconcile, including evidence review in loaded cost", () => {
  for (const record of cases) {
    const input = mapConstructReviewCase(record);
    const nested = Object.values(record.cost_components).reduce((a, b) => a + b, 0);
    assert.equal(fullyLoadedCost(input), nested + record.evidence_review_cost);
    assert.equal(input.approved_budget, directCost(input));
  }
});

test("strict whitelists hide every unregistered field", () => {
  const input = mapConstructReviewCase(cases[0]);
  for (const policy of POLICIES) assert.deepEqual(Object.keys(permittedView(policy, { ...input, unregistered_probe: 1 })), [...POLICY_FIELDS[policy]]);
  assert.ok(!POLICY_FIELDS.OUTCOME_FLAT.includes("authorization_evidence_facts"));
  assert.ok(!POLICY_FIELDS.OUTCOME_FLAT.includes("risk_facts"));
});

test("forbidden adjudication-like keys are rejected recursively", () => {
  assert.throws(() => mapConstructReviewCase({ ...cases[0], reference_probe: "x" }), /Forbidden key/);
  assert.throws(() => mapConstructReviewCase({ ...cases[0], nested: { true_probe: 1 } }), /Forbidden key/);
  assert.throws(() => permittedView("USAGE_ONLY", { ...mapConstructReviewCase(cases[0]), reference_probe: 1 }), /Forbidden key/);
});

test("implementation has no filesystem access or external data paths", async () => {
  const source = await readFile(implementationUrl, "utf8");
  assert.doesNotMatch(source, /node:fs|readFile|restricted|results|labels|manifest/i);
});

test("authorization mapping is factual, three-state, and identifier-independent", () => {
  assert.equal(mapAuthorizationStatus("Approval A permits advisory use."), AUTHORIZATION_STATUS.CLEAR);
  assert.equal(mapAuthorizationStatus("Approval A covers named teams and requires specialist review."), AUTHORIZATION_STATUS.CONDITIONAL);
  assert.equal(mapAuthorizationStatus("No completed assessment is recorded for this scope."), AUTHORIZATION_STATUS.ABSENT);
  assert.equal(mapAuthorizationStatus("The subsidiary environment is absent from its annex."), AUTHORIZATION_STATUS.ABSENT);
  assert.equal(mapAuthorizationStatus(""), AUTHORIZATION_STATUS.ABSENT);
});

test("risk mapping is frozen text-to-tier and conservative when missing", () => {
  assert.equal(mapRiskTier("A malicious message was initially classified as benign and escalation was delayed."), RISK_TIER.HIGH);
  assert.equal(mapRiskTier("Every draft was corrected before release."), RISK_TIER.LOW);
  assert.equal(mapRiskTier("Several recommendations were revised by reviewers."), RISK_TIER.MODERATE);
  assert.equal(mapRiskTier(""), RISK_TIER.HIGH);
  assert.deepEqual(expectedHarmCost("Every draft was corrected before release.", 100), { tier: RISK_TIER.LOW, rate: 0.02, amount: 2 });
});

test("all policies produce 48 unique deterministic receipts with frozen burdens", () => {
  for (const policy of POLICIES) {
    const first = cases.map((record) => evaluate(policy, record));
    const second = cases.map((record) => evaluate(policy, record));
    assert.deepEqual(first, second);
    assert.equal(new Set(first.map(({ receipt_hash }) => receipt_hash)).size, 48);
    assert.ok(first.every(({ measurement_cost }) => measurement_cost === MEASUREMENT_BURDEN[policy]));
  }
});

test("canonical hashing is insensitive to source field order", () => {
  const reversed = Object.fromEntries(Object.entries(cases[0]).reverse());
  for (const policy of POLICIES) assert.deepEqual(evaluate(policy, cases[0]), evaluate(policy, reversed));
});

test("OUTCOME_FLAT is invariant to authorization and risk facts", () => {
  const input = mapConstructReviewCase(cases[0]);
  assert.deepEqual(outcomeFlat(input), outcomeFlat({ ...input, authorization_evidence_facts: "No completed approval is recorded.", risk_facts: "A severe injury occurred." }));
});

test("OVAR applies material authorization stop and risk-adjusted harm", () => {
  const base = mapConstructReviewCase(cases.find((record) => record.evidence_status === "VERIFIED" && record.attribution_confidence >= 0.55));
  const stopped = ovarLedger({ ...base, authorization_evidence_facts: "No completed authorization is recorded for this scope." });
  assert.equal(stopped.action, "STOP");
  assert.equal(stopped.authorization_status, AUTHORIZATION_STATUS.ABSENT);
  const assessed = ovarLedger({ ...base, authorization_evidence_facts: "Approval permits advisory use.", risk_facts: "A malicious event caused delayed escalation." });
  assert.equal(assessed.risk_tier, RISK_TIER.HIGH);
  assert.equal(assessed.expected_harm_cost, fullyLoadedCost(base) * 0.20);
});

test("decisions never branch on case ID", async () => {
  const source = await readFile(implementationUrl, "utf8");
  assert.doesNotMatch(source, /case_id\s*(?:===|==|!==|!=)|switch\s*\(\s*[^)]*case_id|OC-R\d/i);
  const input = mapConstructReviewCase(cases[0]);
  for (const policy of POLICIES) {
    const a = evaluate(policy, input, { mapped: true });
    const b = evaluate(policy, { ...input, case_id: "SYNTHETIC-RENAMED" }, { mapped: true });
    const omitIdentity = ({ case_id, input_hash, receipt_hash, ...decision }) => decision;
    assert.deepEqual(omitIdentity(a), omitIdentity(b));
  }
});
