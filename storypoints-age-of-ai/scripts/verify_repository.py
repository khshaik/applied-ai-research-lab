#!/usr/bin/env python3
"""Fail closed on layout, restricted-material, and research-boundary mistakes."""

from __future__ import annotations

import json
import hashlib
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
REQUIRED = {
    "README.md", "LICENSE", "CITATION.cff", "CONTRIBUTING.md", "SECURITY.md",
    "Makefile", "pyproject.toml", "REPOSITORY_STRUCTURE_MANIFEST.json", "PROJECT_TODO.md",
    "research-design/02d_minimum_route_protocol_amendment_draft.md",
    "research-design/02e_b05_accountable_author_review.md",
    "docs/repository-layout.md", "docs/research-governance.md", "docs/status-and-roadmap.md",
    "docs/public-release-policy.md",
    "docs/traceability/README.md", "docs/traceability/evidence-preservation-map.md",
    "docs/traceability/research-status-and-release-path.md",
    "docs/traceability/STRUCTURE_ENHANCEMENT_RECORD_2026-08-19.json",
    "docs/traceability/RESEARCH_DESIGN_RELOCATION_2026-08-20.json",
    "research-design/README.md",
    "studies/vdcm/README.md", "studies/vdcm/protocol/README.md",
    "studies/vdcm/evidence-map/README.md", "studies/vdcm/simulation/README.md",
    "studies/vdcm/integrity/README.md", "studies/vdcm/restricted/README.md",
    "studies/vdcm/integrity/releases/D17_ACCOUNTABLE_AUTHOR_CONFIRMATION_2026-08-19.json",
    "studies/vdcm/integrity/releases/D17_ACCOUNTABLE_AUTHOR_CONFIRMATION_2026-08-19.json.sha256",
    "papers/thinkai-2026/README.md",
    "papers/thinkai-2026/ACCEPTANCE_RISK_ASSESSMENT.md",
    "papers/thinkai-2026/ARTIFACT_TRACEABILITY.md",
    "papers/thinkai-2026/HYPOTHESES_AND_RESULTS.md",
    "papers/thinkai-2026/MANUSCRIPT_SCIENTIFIC_FREEZE.md",
    "papers/thinkai-2026/SUBMISSION_GUIDE.md",
    "papers/thinkai-2026/venue/README.md",
    "papers/thinkai-2026/venue/SPRINGER_TEMPLATE_DISTILLATION.md",
    "papers/thinkai-2026/manuscript/initial-submission/README.md",
    "papers/thinkai-2026/manuscript/initial-submission/PRE_SUBMISSION_CHECKLIST.md",
    "papers/thinkai-2026/manuscript/initial-submission/QA_RECORD.md",
    "papers/thinkai-2026/manuscript/initial-submission/package_manifest_v0.2.json",
    "papers/thinkai-2026/manuscript/initial-submission/VDCM_ThinkAI2026_Anonymous_Full_Paper_v0.2_FINAL.docx",
    "papers/thinkai-2026/manuscript/initial-submission/VDCM_ThinkAI2026_Anonymous_Full_Paper_v0.2_FINAL.pdf",
    "papers/thinkai-2026/manuscript/identified-author/README.md",
    "papers/thinkai-2026/manuscript/identified-author/AUTHOR_METADATA_TEMPLATE.md",
    "papers/thinkai-2026/release/README.md",
    "papers/thinkai-2026/manuscript/README.md",
    "papers/thinkai-2026/manuscript/manuscript_working_draft.md",
    "papers/thinkai-2026/manuscript/claim_verification_ledger.md",
    "papers/thinkai-2026/declarations/AI_ASSISTANCE_DISCLOSURE.md",
    "papers/thinkai-2026/declarations/RESEARCH_ETHICS_AND_RESPONSIBLE_USE.md",
    "papers/thinkai-2026/declarations/DATA_CODE_AVAILABILITY.md",
    "communications/README.md",
    "communications/verified-delivery-capacity/README.md",
    "communications/verified-delivery-capacity/END_TO_END_WORKFLOW.md",
    "communications/verified-delivery-capacity/LONG_FORM_NARRATIVE.md",
    "communications/verified-delivery-capacity/SHORT_FORM_SUMMARY.md",
    "communications/verified-delivery-capacity/EDITORIAL_AND_RELEASE_GUIDE.md",
    "communications/verified-delivery-capacity/scripts/build_workflow.py",
    "communications/verified-delivery-capacity/assets/06-end-to-end-verified-delivery-workflow.png",
    "communications/verified-delivery-capacity/assets/06-end-to-end-verified-delivery-workflow.svg",
    "communications/verified-delivery-capacity/assets/asset_manifest.json",
    "scripts/verify_manuscript.py",
    "scripts/build_public_release.py", "scripts/verify_public_release.py",
    "gate2/minimum_route_scope.draft.json",
    "gate2/open_index_pilot_queries_v0.3.json",
    "studies/vdcm/evidence-map/registries/s4_open_index_queries_v0.6.json",
    "gate2/output/development/query_appraisals/OA-S4R6-20260815-query-appraisal-v1.json",
    "gate2/output/development/query_appraisals/S2-S4R5-20260815-query-appraisal-v2.json",
    "studies/vdcm/evidence-map/registries/arxiv_s4_mapping_v0.1.json",
    "studies/vdcm/evidence-map/registries/s5t_open_index_queries_v0.4.json",
    "studies/vdcm/evidence-map/registries/arxiv_s5t_mapping_v0.1.json",
    "gate2/output/development/query_appraisals/AX-S5R-to-S4-20260815-mapping-v1.json",
    "gate2/output/development/query_appraisals/AX-S5R-to-S4-20260815-query-appraisal-v1.json",
    "gate2/output/development/openalex/OA-S5TR4-20260816-pilot1/manifest.json",
    "gate2/output/development/query_appraisals/OA-S5TR4-20260816-query-decisions-v1.json",
    "gate2/output/development/query_appraisals/OA-S5TR4-20260816-query-appraisal-v1.json",
    "gate2/output/development/query_appraisals/AX-S5T-20260816-query-decisions-v1.json",
    "gate2/output/development/query_appraisals/AX-S5T-20260816-query-appraisal-v1.json",
    "studies/vdcm/evidence-map/registries/s5s_open_index_queries_v0.7.json",
    "studies/vdcm/evidence-map/registries/arxiv_s5s_mapping_v0.1.json",
    "gate2/output/development/openalex/OA-S5SR7-20260816-pilot1/manifest.json",
    "gate2/output/development/query_appraisals/OA-S5SR7-20260816-query-decisions-v1.json",
    "gate2/output/development/query_appraisals/OA-S5SR7-20260816-query-appraisal-v1.json",
    "gate2/output/development/query_appraisals/AX-S5S-20260816-query-decisions-v2.json",
    "gate2/output/development/query_appraisals/AX-S5S-20260816-query-appraisal-v2.json",
    "studies/vdcm/evidence-map/registries/arxiv_s6_mapping_v0.2.json",
    "gate2/output/development/query_appraisals/AX-S6R-20260816-query-decisions-v2.json",
    "gate2/output/development/query_appraisals/AX-S6R-20260816-query-appraisal-v2.json",
    "studies/vdcm/evidence-map/registries/s6_open_index_queries_v0.8.json",
    "gate2/output/development/openalex/OA-S6R8-20260816-pilot1/manifest.json",
    "gate2/output/development/query_appraisals/OA-S6R8-20260816-query-decisions-v1.json",
    "gate2/output/development/query_appraisals/OA-S6R8-20260816-query-appraisal-v1.json",
    "studies/vdcm/evidence-map/registries/s7_novelty_queries_v0.4.json",
    "studies/vdcm/evidence-map/registries/arxiv_s7_mapping_v0.4.json",
    "studies/vdcm/evidence-map/S7_NOVELTY_DEVELOPMENT.md",
    "gate2/output/development/openalex/OA-S7R4-20260816-pilot1/manifest.json",
    "gate2/output/development/semantic_scholar/S2-S7R4-20260816-pilot1/manifest.json",
    "gate2/output/development/arxiv/AX-S7R4-20260816-retry2/manifest.json",
    "gate2/output/development/arxiv/AX-S7R4-20260816-blocker.json",
    "gate2/output/development/query_appraisals/OA-S7R4-20260816-query-decisions-v1.json",
    "gate2/output/development/query_appraisals/OA-S7R4-20260816-query-appraisal-v1.json",
    "gate2/output/development/query_appraisals/S2-S7R4-20260816-query-decisions-v1.json",
    "gate2/output/development/query_appraisals/S2-S7R4-20260816-query-appraisal-v1.json",
    "gate2/output/development/query_appraisals/AX-S7R4-20260816-query-decisions-v1.json",
    "gate2/output/development/query_appraisals/AX-S7R4-20260816-query-appraisal-v1.json",
    "studies/vdcm/evidence-map/registries/s8_foundational_queries_v0.6.json",
    "studies/vdcm/evidence-map/S8_FOUNDATIONAL_DEVELOPMENT.md",
    "gate2/output/development/openalex/OA-S8R6-20260816-full1/manifest.json",
    "gate2/output/development/semantic_scholar/S2-S8R6-20260816-full1/manifest.json",
    "gate2/output/development/query_appraisals/OA-S8R6-20260816-query-decisions-v1.json",
    "gate2/output/development/query_appraisals/OA-S8R6-20260816-query-appraisal-v1.json",
    "gate2/output/development/query_appraisals/S2-S8R6-20260816-query-decisions-v1.json",
    "gate2/output/development/query_appraisals/S2-S8R6-20260816-query-appraisal-v1.json",
    "studies/vdcm/evidence-map/registries/s1_s2_integrative_queries_v0.3.json",
    "studies/vdcm/evidence-map/C08_INTEGRATIVE_DEVELOPMENT.md",
    "gate2/output/development/c08_bounded_union_acceptance_20260816.json",
    "gate2/output/development/semantic_scholar/S2-S1I3-20260816-full1/manifest.json",
    "gate2/output/development/openalex/OA-S2I2-20260816-full1/manifest.json",
    "gate2/output/development/query_appraisals/S2-S1I3-20260816-query-decisions-v1.json",
    "gate2/output/development/query_appraisals/S2-S1I3-20260816-query-appraisal-v1.json",
    "gate2/output/development/query_appraisals/OA-S2I2-20260816-query-decisions-v1.json",
    "gate2/output/development/query_appraisals/OA-S2I2-20260816-query-appraisal-v1.json",
    "gate2/final_source_family_acceptance_matrix.json",
    "studies/vdcm/evidence-map/C09_SOURCE_FAMILY_ACCEPTANCE_MATRIX.md",
    "simulation/preregistration/locked_evaluation_protocol.json",
    "simulation/output/development/development_manifest.json",
    "simulation/output/development/reproducibility_audit_20260815.json",
    "simulation/output/development/g4b_mechanism_ablation_v2_20260815/ablation_receipt.json",
    "research-design/05_developmental_simulation_reconciliation.md",
    "papers/thinkai-2026/results/developmental_simulation_v2/report_manifest.json",
    "papers/thinkai-2026/manuscript/tables/parameter_use_table.md",
    "papers/thinkai-2026/figures/figure_manifest.json",
    "papers/thinkai-2026/figures/ALT_TEXT.md",
    "papers/thinkai-2026/VENUE_REQUIREMENTS.md",
    "THINKAI_2026_Gate2_Research_Workbook.xlsx",
    "gate2/output/systematic/v1.3/20260816/d07/d07_manifest.json",
    "studies/vdcm/evidence-map/D07_STUDY_FAMILY_CONSOLIDATION.md",
    "gate2/output/systematic/v1.3/20260816/d08/d08_packet_manifest.json",
    "gate2/output/systematic/v1.3/20260816/d08/pass_a_decisions.jsonl",
    "gate2/output/systematic/v1.3/20260816/d08/pass_b_decisions.jsonl",
    "gate2/output/systematic/v1.3/20260816/d08/d09/d08_d09_manifest.json",
    "studies/vdcm/evidence-map/D08_TITLE_ABSTRACT_SCREENING.md",
    "gate2/output/systematic/v1.3/20260816/d08/d09/adjudicated_decisions.jsonl",
    "gate2/output/systematic/v1.3/20260816/d08/d09/final/d09_final_manifest.json",
    "gate2/output/systematic/v1.3/20260816/d08/d09/final/final_title_abstract_decisions.jsonl",
    "studies/vdcm/evidence-map/D09_ADJUDICATION.md",
    "gate2/output/systematic/v1.3/20260816/d10/final/d10_final_manifest.json",
    "gate2/output/systematic/v1.3/20260816/d10/final/fulltext_retrieval_ledger.jsonl",
    "gate2/output/systematic/v1.3/20260816/d10/timestamp_provenance_correction.json",
    "studies/vdcm/evidence-map/D10_LAWFUL_FULLTEXT_RETRIEVAL.md",
}
PROHIBITED_NAMES = {
    "production_seed_manifest.json", "sealed_seed_values.json",
    "held_out_test_labels.json", "participant_data.csv",
}
SECRET_PATTERNS = {
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
}
TEXT_SUFFIXES = {".csv", ".json", ".md", ".py", ".toml", ".txt", ".yml", ".yaml", ".cff"}


def main() -> None:
    errors: list[str] = []
    files = [path for path in ROOT.rglob("*") if path.is_file() and ".git" not in path.parts]
    missing = sorted(item for item in REQUIRED if not (ROOT / item).is_file())
    if missing:
        errors.append(f"required repository files missing: {missing}")
    leaked = sorted(path.relative_to(ROOT).as_posix() for path in files if path.name in PROHIBITED_NAMES)
    if leaked:
        errors.append(f"prohibited restricted files present: {leaked}")
    for path in files:
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {"LICENSE", "Makefile"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"{label} pattern in {path.relative_to(ROOT)}")

    restricted = ROOT / "studies/vdcm/restricted"
    unexpected = sorted(path.name for path in restricted.iterdir() if path.is_file() and path.name != "README.md")
    if unexpected:
        errors.append(f"unexpected restricted study files: {unexpected}")

    d17_approval_path = ROOT / "studies/vdcm/integrity/releases/D17_ACCOUNTABLE_AUTHOR_CONFIRMATION_2026-08-19.json"
    try:
        approval = json.loads(d17_approval_path.read_text(encoding="utf-8"))
        expected_claims = [f"CL-{number:03d}" for number in range(1, 11)]
        if approval.get("decision") != "approved" or approval.get("approved_claim_ids") != expected_claims:
            errors.append("D17 accountable-author approval is incomplete or out of order")
        for record in approval.get("source_artifacts", []):
            source = ROOT / record.get("path", "")
            actual = hashlib.sha256(source.read_bytes()).hexdigest() if source.is_file() else ""
            if actual != record.get("sha256"):
                errors.append(f"D17 approval source checksum mismatch: {record.get('path')}")
        sidecar = d17_approval_path.with_suffix(d17_approval_path.suffix + ".sha256")
        declared = sidecar.read_text(encoding="utf-8").split()[0]
        if declared != hashlib.sha256(d17_approval_path.read_bytes()).hexdigest():
            errors.append("D17 accountable-author approval sidecar mismatch")
    except (KeyError, TypeError, ValueError, OSError, json.JSONDecodeError, IndexError) as exc:
        errors.append(f"D17 accountable-author approval verification failed: {exc}")

    submission_dir = ROOT / "papers/thinkai-2026/manuscript/initial-submission"
    try:
        package = json.loads((submission_dir / "package_manifest_v0.2.json").read_text(encoding="utf-8"))
        if package.get("page_count") != 15 or package.get("qa", {}).get("visual_pages_inspected") != 15:
            errors.append("anonymous manuscript visual-QA page count is inconsistent")
        for record in package.get("files", []):
            artifact = submission_dir / record.get("path", "")
            actual = hashlib.sha256(artifact.read_bytes()).hexdigest() if artifact.is_file() else ""
            if actual != record.get("sha256"):
                errors.append(f"anonymous manuscript package checksum mismatch: {record.get('path')}")
    except (KeyError, TypeError, ValueError, OSError, json.JSONDecodeError) as exc:
        errors.append(f"anonymous manuscript package verification failed: {exc}")

    communication_dir = ROOT / "communications/verified-delivery-capacity/assets"
    try:
        communication_manifest = json.loads(
            (communication_dir / "asset_manifest.json").read_text(encoding="utf-8")
        )
        if communication_manifest.get("artifact_type") != "conceptual_communication_visual":
            errors.append("communication workflow must remain labeled conceptual")
        if communication_manifest.get("empirical_result") is not False:
            errors.append("communication workflow must not be labeled an empirical result")
        for record in communication_manifest.get("files", []):
            artifact = communication_dir / record.get("path", "")
            actual = hashlib.sha256(artifact.read_bytes()).hexdigest() if artifact.is_file() else ""
            if actual != record.get("sha256"):
                errors.append(f"communication asset checksum mismatch: {record.get('path')}")
    except (KeyError, TypeError, ValueError, OSError, json.JSONDecodeError) as exc:
        errors.append(f"communication asset verification failed: {exc}")

    d07_dir = ROOT / "gate2/output/systematic/v1.3/20260816/d07"
    try:
        from gate2.study_family_consolidation import verify as verify_d07
        d07 = verify_d07(d07_dir)
        if (
            d07.get("canonical_report_count") != 3962
            or d07.get("study_family_count") != 3930
            or d07.get("multi_report_family_count") != 23
            or d07.get("unresolved_candidate_count") != 0
        ):
            errors.append("D07 study-family reconciliation totals are inconsistent")
    except Exception as exc:
        errors.append(f"D07 study-family verification failed: {exc}")

    try:
        from gate2.title_abstract_screening import validate_pass, verify_packet
        packet = verify_packet()
        pass_a = validate_pass(ROOT / "gate2/output/systematic/v1.3/20260816/d08/pass_a_decisions.jsonl", "pass-a")
        pass_b = validate_pass(ROOT / "gate2/output/systematic/v1.3/20260816/d08/pass_b_decisions.jsonl", "pass-b")
        if packet.get("family_count") != 3930 or pass_a.get("family_count") != 3930 or pass_b.get("family_count") != 3930:
            errors.append("D08 packet/pass totals are inconsistent")
        from gate2.screening_reconcile import verify as verify_d09_packet
        d09 = verify_d09_packet()
        if d09.get("adjudication_candidate_count") != 1314 or d09.get("consensus_without_unclear_count") != 2616:
            errors.append("D08/D09 screening reconciliation totals are inconsistent")
    except Exception as exc:
        errors.append(f"D08 screening verification failed: {exc}")

    try:
        from gate2.adjudication_finalize import verify as verify_d09_final
        d09_final = verify_d09_final()
        if d09_final.get("family_count") != 3930 or d09_final.get("decision_counts") != {"exclude": 1854, "include": 2076}:
            errors.append("D09 final title/abstract totals are inconsistent")
    except Exception as exc:
        errors.append(f"D09 adjudication verification failed: {exc}")

    try:
        from gate2.fulltext_retrieval import verify_final as verify_d10_final
        d10 = verify_d10_final()
        if d10.get("family_count") != 2076 or d10.get("retrieved_pdf_count") != 1605 or sum(d10.get("status_counts", {}).values()) != 2076:
            errors.append("D10 lawful full-text retrieval totals are inconsistent")
    except Exception as exc:
        errors.append(f"D10 lawful full-text verification failed: {exc}")

    protocol = json.loads((ROOT / "simulation/preregistration/locked_evaluation_protocol.json").read_text())
    if protocol.get("status") != "draft_prelock" or protocol.get("locked_at_utc") is not None:
        errors.append("locked-evaluation protocol must remain draft and unopened during repository structuring")
    if (ROOT / "simulation/output/locked").exists():
        errors.append("locked simulation output exists before a ready-to-open release")

    development_dir = ROOT / "simulation/output/development"
    development_manifest = json.loads(
        (development_dir / "development_manifest.json").read_text()
    )
    if development_manifest.get("manifest_version") != "0.2.0-development":
        errors.append("development manifest lacks current code/config provenance")
    for name, expected in development_manifest.get("output_sha256", {}).items():
        output = development_dir / name
        actual = hashlib.sha256(output.read_bytes()).hexdigest() if output.is_file() else ""
        if actual != expected:
            errors.append(f"development output checksum mismatch: {name}")
    audit = json.loads(
        (development_dir / "reproducibility_audit_20260815.json").read_text()
    )
    current = audit.get("current_manifest", {})
    if current.get("content_checksum") != development_manifest.get("content_checksum"):
        errors.append("development audit does not reference the current manifest")
    if current.get("output_sha256") != development_manifest.get("output_sha256"):
        errors.append("development audit output hashes do not match the current manifest")
    ablation_dir = development_dir / "g4b_mechanism_ablation_v2_20260815"
    ablation_receipt = json.loads((ablation_dir / "ablation_receipt.json").read_text())
    if ablation_receipt.get("status") != "verified_developmental":
        errors.append("current developmental ablation receipt is not verified")
    for record in ablation_receipt.get("files", []):
        artifact = ablation_dir / record.get("path", "")
        actual = hashlib.sha256(artifact.read_bytes()).hexdigest() if artifact.is_file() else ""
        if actual != record.get("sha256"):
            errors.append(f"developmental ablation checksum mismatch: {artifact.name}")
    report_dir = ROOT / "papers/thinkai-2026/results/developmental_simulation_v2"
    report_manifest = json.loads((report_dir / "report_manifest.json").read_text())
    if report_manifest.get("status") != "developmental_synthetic_not_empirical_validation":
        errors.append("manuscript result package lacks the synthetic-evidence boundary")
    if report_manifest.get("bootstrap_replications") != 5000:
        errors.append("manuscript result package lacks the declared bootstrap precision")
    for name, expected in report_manifest.get("output_sha256", {}).items():
        artifact = report_dir / name
        actual = hashlib.sha256(artifact.read_bytes()).hexdigest() if artifact.is_file() else ""
        if actual != expected:
            errors.append(f"manuscript result checksum mismatch: {name}")
    figure_dir = ROOT / "papers/thinkai-2026/figures"
    figure_manifest = json.loads((figure_dir / "figure_manifest.json").read_text())
    if len(figure_manifest.get("outputs", [])) != 10:
        errors.append("working manuscript figure package is incomplete")
    for name, expected in figure_manifest.get("output_sha256", {}).items():
        artifact = figure_dir / name
        actual = hashlib.sha256(artifact.read_bytes()).hexdigest() if artifact.is_file() else ""
        if actual != expected:
            errors.append(f"working manuscript figure checksum mismatch: {name}")

    registry = json.loads((ROOT / "gate2/open_index_pilot_queries_v0.3.json").read_text())
    roles = {row.get("role") for row in registry.get("sentinels", []) if row.get("family_id") == "S3"}
    if not {"scope_positive", "neutral_disconfirming", "negative_boundary"}.issubset(roles):
        errors.append("S3 v0.3 registry lacks required family-scoped sentinel roles")

    s4_registry = json.loads((ROOT / "studies/vdcm/evidence-map/registries/s4_open_index_queries_v0.6.json").read_text())
    s4_roles = {row.get("role") for row in s4_registry.get("sentinels", []) if row.get("family_id") == "S4"}
    if not {"scope_positive", "neutral_disconfirming", "negative_boundary"}.issubset(s4_roles):
        errors.append("S4 v0.6 registry lacks required family-scoped sentinel roles")
    for source, result_path in (
        ("OpenAlex", "gate2/output/development/query_appraisals/OA-S4R6-20260815-query-appraisal-v1.json"),
        ("Semantic Scholar", "gate2/output/development/query_appraisals/S2-S4R5-20260815-query-appraisal-v2.json"),
    ):
        s4_result = json.loads((ROOT / result_path).read_text())
        if not (s4_result.get("freeze_ready") is True and s4_result.get("sample_size") == 50):
            errors.append(f"{source} S4 query-development acceptance is absent or inconsistent")
    for item in (
        "gate2/output/development/query_appraisals/S2-S4R5-20260815-decisions-v1",
        "gate2/output/development/query_appraisals/S2-S4R5-20260815-query-appraisal-v1",
        "gate2/output/development/query_appraisals/OA-S4R6-20260815-decisions-v1",
        "gate2/output/development/query_appraisals/OA-S4R6-20260815-query-appraisal-v1",
        "gate2/output/development/query_appraisals/S2-S4R5-20260815-query-appraisal-v2",
        "gate2/output/development/query_appraisals/S2-S4R5-20260815-decision-reuse-v2",
        "studies/vdcm/evidence-map/registries/s4_open_index_queries_v0.6",
        "studies/vdcm/evidence-map/registries/arxiv_s4_mapping_v0.1",
        "gate2/output/development/query_appraisals/AX-S5R-to-S4-20260815-mapping-v1",
        "gate2/output/development/query_appraisals/AX-S5R-to-S4-20260815-decisions-v1",
        "gate2/output/development/query_appraisals/AX-S5R-to-S4-20260815-query-appraisal-v1",
        "studies/vdcm/evidence-map/registries/s5t_open_index_queries_v0.4",
        "studies/vdcm/evidence-map/registries/arxiv_s5t_mapping_v0.1",
        "gate2/output/development/query_appraisals/OA-S5TR4-20260816-query-decisions-v1",
        "gate2/output/development/query_appraisals/OA-S5TR4-20260816-query-appraisal-v1",
        "gate2/output/development/query_appraisals/AX-S5T-20260816-query-decisions-v1",
        "gate2/output/development/query_appraisals/AX-S5T-20260816-query-appraisal-v1",
        "studies/vdcm/evidence-map/registries/s5s_open_index_queries_v0.7",
        "studies/vdcm/evidence-map/registries/arxiv_s5s_mapping_v0.1",
        "gate2/output/development/query_appraisals/OA-S5SR7-20260816-query-decisions-v1",
        "gate2/output/development/query_appraisals/OA-S5SR7-20260816-query-appraisal-v1",
        "gate2/output/development/query_appraisals/AX-S5S-20260816-query-decisions-v2",
        "gate2/output/development/query_appraisals/AX-S5S-20260816-query-appraisal-v2",
        "studies/vdcm/evidence-map/registries/arxiv_s6_mapping_v0.2",
        "gate2/output/development/query_appraisals/AX-S6R-20260816-query-decisions-v2",
        "gate2/output/development/query_appraisals/AX-S6R-20260816-query-appraisal-v2",
        "studies/vdcm/evidence-map/registries/s6_open_index_queries_v0.8",
        "gate2/output/development/query_appraisals/OA-S6R8-20260816-query-decisions-v1",
        "gate2/output/development/query_appraisals/OA-S6R8-20260816-query-appraisal-v1",
        "studies/vdcm/evidence-map/registries/s7_novelty_queries_v0.4",
        "studies/vdcm/evidence-map/registries/arxiv_s7_mapping_v0.4",
        "gate2/output/development/query_appraisals/OA-S7R4-20260816-query-decisions-v1",
        "gate2/output/development/query_appraisals/OA-S7R4-20260816-query-appraisal-v1",
        "gate2/output/development/query_appraisals/S2-S7R4-20260816-query-decisions-v1",
        "gate2/output/development/query_appraisals/S2-S7R4-20260816-query-appraisal-v1",
        "gate2/output/development/query_appraisals/AX-S7R4-20260816-query-decisions-v1",
        "gate2/output/development/query_appraisals/AX-S7R4-20260816-query-appraisal-v1",
        "studies/vdcm/evidence-map/registries/s8_foundational_queries_v0.6",
        "gate2/output/development/query_appraisals/OA-S8R6-20260816-query-decisions-v1",
        "gate2/output/development/query_appraisals/OA-S8R6-20260816-query-appraisal-v1",
        "gate2/output/development/query_appraisals/S2-S8R6-20260816-query-decisions-v1",
        "gate2/output/development/query_appraisals/S2-S8R6-20260816-query-appraisal-v1",
        "studies/vdcm/evidence-map/registries/s1_s2_integrative_queries_v0.3",
        "gate2/output/development/query_appraisals/S2-S1I3-20260816-query-decisions-v1",
        "gate2/output/development/query_appraisals/S2-S1I3-20260816-query-appraisal-v1",
        "gate2/output/development/query_appraisals/OA-S2I2-20260816-query-decisions-v1",
        "gate2/output/development/query_appraisals/OA-S2I2-20260816-query-appraisal-v1",
    ):
        payload = ROOT / f"{item}.json"
        sidecar = ROOT / f"{item}.sha256"
        expected = sidecar.read_text(encoding="utf-8").split()[0] if sidecar.is_file() else ""
        actual = hashlib.sha256(payload.read_bytes()).hexdigest()
        if expected != actual:
            errors.append(f"checksum mismatch or absent for {payload.relative_to(ROOT)}")

    s5t_export = ROOT / "gate2/output/development/openalex/OA-S5TR4-20260816-pilot1"
    s5t_manifest_path = s5t_export / "manifest.json"
    s5t_manifest = json.loads(s5t_manifest_path.read_text())
    s5t_registry = ROOT / "studies/vdcm/evidence-map/registries/s5t_open_index_queries_v0.4.json"
    if s5t_manifest.get("query_registry_sha256") != hashlib.sha256(s5t_registry.read_bytes()).hexdigest():
        errors.append("S5T OpenAlex export does not bind the accepted query registry")
    s5t_csv = s5t_export / s5t_manifest.get("records_csv", {}).get("file", "")
    if not s5t_csv.is_file() or hashlib.sha256(s5t_csv.read_bytes()).hexdigest() != s5t_manifest.get("records_csv", {}).get("sha256"):
        errors.append("S5T OpenAlex records CSV checksum mismatch")
    for page in s5t_manifest.get("pages", []):
        page_path = s5t_export / page.get("file", "")
        if not page_path.is_file() or hashlib.sha256(page_path.read_bytes()).hexdigest() != page.get("sha256"):
            errors.append(f"S5T OpenAlex raw-page checksum mismatch: {page.get('file')}")
    s5t_manifest_sidecar = (s5t_export / "manifest.sha256").read_text().split()[0]
    if s5t_manifest_sidecar != hashlib.sha256(s5t_manifest_path.read_bytes()).hexdigest():
        errors.append("S5T OpenAlex manifest sidecar checksum mismatch")

    s5s_export = ROOT / "gate2/output/development/openalex/OA-S5SR7-20260816-pilot1"
    s5s_manifest_path = s5s_export / "manifest.json"
    s5s_manifest = json.loads(s5s_manifest_path.read_text())
    s5s_registry = ROOT / "studies/vdcm/evidence-map/registries/s5s_open_index_queries_v0.7.json"
    if s5s_manifest.get("query_registry_sha256") != hashlib.sha256(s5s_registry.read_bytes()).hexdigest():
        errors.append("S5S OpenAlex export does not bind the accepted query registry")
    s5s_csv = s5s_export / s5s_manifest.get("records_csv", {}).get("file", "")
    if not s5s_csv.is_file() or hashlib.sha256(s5s_csv.read_bytes()).hexdigest() != s5s_manifest.get("records_csv", {}).get("sha256"):
        errors.append("S5S OpenAlex records CSV checksum mismatch")
    for page in s5s_manifest.get("pages", []):
        page_path = s5s_export / page.get("file", "")
        if not page_path.is_file() or hashlib.sha256(page_path.read_bytes()).hexdigest() != page.get("sha256"):
            errors.append(f"S5S OpenAlex raw-page checksum mismatch: {page.get('file')}")
    s5s_manifest_sidecar = (s5s_export / "manifest.sha256").read_text().split()[0]
    if s5s_manifest_sidecar != hashlib.sha256(s5s_manifest_path.read_bytes()).hexdigest():
        errors.append("S5S OpenAlex manifest sidecar checksum mismatch")

    s6_export = ROOT / "gate2/output/development/openalex/OA-S6R8-20260816-pilot1"
    s6_manifest_path = s6_export / "manifest.json"
    s6_manifest = json.loads(s6_manifest_path.read_text())
    s6_registry = ROOT / "studies/vdcm/evidence-map/registries/s6_open_index_queries_v0.8.json"
    if s6_manifest.get("query_registry_sha256") != hashlib.sha256(s6_registry.read_bytes()).hexdigest():
        errors.append("S6 OpenAlex export does not bind the accepted query registry")
    s6_csv = s6_export / s6_manifest.get("records_csv", {}).get("file", "")
    if not s6_csv.is_file() or hashlib.sha256(s6_csv.read_bytes()).hexdigest() != s6_manifest.get("records_csv", {}).get("sha256"):
        errors.append("S6 OpenAlex records CSV checksum mismatch")
    for page in s6_manifest.get("pages", []):
        page_path = s6_export / page.get("file", "")
        if not page_path.is_file() or hashlib.sha256(page_path.read_bytes()).hexdigest() != page.get("sha256"):
            errors.append(f"S6 OpenAlex raw-page checksum mismatch: {page.get('file')}")
    s6_manifest_sidecar = (s6_export / "manifest.sha256").read_text().split()[0]
    if s6_manifest_sidecar != hashlib.sha256(s6_manifest_path.read_bytes()).hexdigest():
        errors.append("S6 OpenAlex manifest sidecar checksum mismatch")

    s7_blocker = ROOT / "gate2/output/development/arxiv/AX-S7R4-20260816-blocker.json"
    s7_blocker_hash = ROOT / "gate2/output/development/arxiv/AX-S7R4-20260816-blocker.json.sha256"
    if s7_blocker_hash.read_text().split()[0] != hashlib.sha256(s7_blocker.read_bytes()).hexdigest():
        errors.append("S7 resolved blocker provenance checksum mismatch")
    s7_resolution = json.loads(s7_blocker.read_text())
    if s7_resolution.get("status") != "development_export_blocker_resolved":
        errors.append("S7 arXiv blocker is not explicitly resolved")
    resolved_export = ROOT / s7_resolution.get("resolution", {}).get("successful_export", "")
    if not resolved_export.is_dir():
        errors.append("S7 resolved arXiv export is absent")

    s8_registry = ROOT / "studies/vdcm/evidence-map/registries/s8_foundational_queries_v0.6.json"
    s8_registry_hash = hashlib.sha256(s8_registry.read_bytes()).hexdigest()
    for source, query_id, relative, expected_total in (
        ("openalex", "OA-S8R6", "gate2/output/development/openalex/OA-S8R6-20260816-full1", 1097),
        ("semantic_scholar", "S2-S8R6", "gate2/output/development/semantic_scholar/S2-S8R6-20260816-full1", 794),
    ):
        export = ROOT / relative
        manifest_path = export / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        if manifest.get("source") != source or manifest.get("query_id") != query_id:
            errors.append(f"S8 export identity mismatch: {query_id}")
        if manifest.get("query_registry_sha256") != s8_registry_hash:
            errors.append(f"S8 export registry binding mismatch: {query_id}")
        if manifest.get("complete_pagination") is not True or manifest.get("records_retrieved") != expected_total or manifest.get("total_reported") != expected_total:
            errors.append(f"S8 export completeness mismatch: {query_id}")
        csv_path = export / manifest.get("records_csv", {}).get("file", "")
        if not csv_path.is_file() or hashlib.sha256(csv_path.read_bytes()).hexdigest() != manifest.get("records_csv", {}).get("sha256"):
            errors.append(f"S8 records checksum mismatch: {query_id}")
        for page in manifest.get("pages", []):
            page_path = export / page.get("file", "")
            if not page_path.is_file() or hashlib.sha256(page_path.read_bytes()).hexdigest() != page.get("sha256"):
                errors.append(f"S8 raw-page checksum mismatch: {query_id}/{page.get('file')}")
        if (export / "manifest.sha256").read_text().split()[0] != hashlib.sha256(manifest_path.read_bytes()).hexdigest():
            errors.append(f"S8 manifest checksum mismatch: {query_id}")
        appraisal = json.loads((ROOT / f"gate2/output/development/query_appraisals/{query_id}-20260816-query-appraisal-v1.json").read_text())
        if appraisal.get("freeze_ready") is not True or appraisal.get("positive_sentinel_recall_pass") is not True or appraisal.get("neutral_disconfirming_recall_pass") is not True:
            errors.append(f"S8 appraisal acceptance mismatch: {query_id}")

    c08_path = ROOT / "gate2/output/development/c08_bounded_union_acceptance_20260816.json"
    c08_hash = ROOT / "gate2/output/development/c08_bounded_union_acceptance_20260816.sha256"
    if c08_hash.read_text().split()[0] != hashlib.sha256(c08_path.read_bytes()).hexdigest():
        errors.append("C08 bounded-union decision checksum mismatch")
    c08 = json.loads(c08_path.read_text())
    if c08.get("C08_disposition") != "complete_for_developmental_query_control":
        errors.append("C08 is not explicitly complete at developmental-control level")
    if c08.get("blocked_fresh_union_execution", {}).get("partial_records_used") is not False:
        errors.append("C08 improperly uses a partial OpenAlex rerun")

    c09_path = ROOT / "gate2/final_source_family_acceptance_matrix.json"
    c09_sidecar = ROOT / "gate2/final_source_family_acceptance_matrix.sha256"
    if c09_sidecar.read_text().split()[0] != hashlib.sha256(c09_path.read_bytes()).hexdigest():
        errors.append("C09 matrix checksum mismatch")
    c09 = json.loads(c09_path.read_text())
    if c09.get("approved_pair_count") != 18 or c09.get("C09_disposition") != "complete_for_protocol_reconciliation":
        errors.append("C09 matrix does not close the approved 18-pair allocation")
    if any(not row.get("complete") or not row.get("sentinel_acceptance") for row in c09.get("rows", [])):
        errors.append("C09 contains an incomplete or unaccepted source-family row")

    structure = json.loads((ROOT / "REPOSITORY_STRUCTURE_MANIFEST.json").read_text())
    if structure.get("production_seed_values_included") is not False:
        errors.append("structure manifest does not preserve the production-seed exclusion")
    if errors:
        raise SystemExit("REPOSITORY VERIFICATION FAILED\n" + "\n".join(errors))
    print(f"PASS: {len(files)} files checked; layout and research boundaries preserved")


if __name__ == "__main__":
    main()
