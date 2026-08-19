"""Conservative D07 report-version consolidation over D06 canonical reports."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from difflib import SequenceMatcher
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
D06 = ROOT / "gate2/output/systematic/v1.3/20260816/d06"
OUTPUT = ROOT / "gate2/output/systematic/v1.3/20260816/d07"
VERSION = "d07-study-family-consolidation/1.0.0"
DECIDED_AT = "2026-08-16T09:15:11Z"


class ConsolidationError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _group(*ids: str, signals: list[str], rationale: str) -> dict[str, Any]:
    return {"members": list(ids), "linkage_signals": signals, "rationale": rationale}


APPROVED_MULTI_REPORT_GROUPS = [
    _group("CAN-09e12141a098f7bc9a41", "CAN-ff225bb14c94c05b7a58", "CAN-9abaddd48193dd43da85", "CAN-79b5056f22633e68c10d", "CAN-5fa4e64084d3879c2e9c", "CAN-32cef85026edc30a1e8c", signals=["explicit_version_statement", "shared_sample_project"], rationale="Main report and explicitly titled replication/data packages for the same Go Home Copilot study; identical supplied abstracts and study title."),
    _group("CAN-98a3fc547677995b9abc", "CAN-2f6414c31d8b09c9aa6b", signals=["title_author_year", "shared_sample_project"], rationale="Long and short CodeWars report titles share author/year and identical supplied abstract."),
    _group("CAN-638aef7ed5924b18400b", "CAN-fe8f718a490057fce143", signals=["manual_other"], rationale="Spanish and English metadata records describe the same Bogotá agile-effort study with identical supplied abstract."),
    _group("CAN-d4f1bb630411821aa797", "CAN-a55b9a233beb689839a5", "CAN-2b146f5c1b3e6374d482", signals=["correction_companion", "shared_sample_project"], rationale="Article and explicitly labelled peer-review reports for the same F1000Research version."),
    _group("CAN-e660e56caf7aaf125d3b", "CAN-ba5f1a1d922afc10177d", signals=["manual_other"], rationale="English and Ukrainian titles share author/year and identical supplied abstract for one effort-estimation report."),
    _group("CAN-3eb30db192b5bbddb26f", "CAN-c0aa43d9e6055e072e52", signals=["arxiv_related_doi", "explicit_version_statement"], rationale="Published ACM and arXiv versions of the modern-code-review roadmap."),
    _group("CAN-12e1efb46bf97050c0b3", "CAN-6e2d2c0970f6cd4f612e", signals=["title_author_year"], rationale="Near-identical CAMS-F title, author/year and chapter metadata; one record lacks DOI."),
    _group("CAN-6892277518a319b849f7", "CAN-f635f701d718b00937c6", signals=["shared_sample_project", "manual_other"], rationale="Poster and slides are companion artifacts for the consequences-of-unhappiness study."),
    _group("CAN-3d304ed2eb187474008f", "CAN-5eb95ff768d611d3f8e3", signals=["arxiv_related_doi", "explicit_version_statement"], rationale="Published and arXiv versions of the explanations-in-code-review study."),
    _group("CAN-21b349806bd68d59ba3b", "CAN-1cc64a6ec0126ee17c7f", signals=["explicit_version_statement", "shared_sample_project"], rationale="Main visual-aids study and explicitly labelled replication package."),
    _group("CAN-515e27a0f830002ed9c7", "CAN-ff9a821fc45915d69e26", signals=["shared_sample_project", "manual_other"], rationale="Report and preprint metadata share author lineage and essentially identical supplied abstract for the prompt-optimization framework/artifact."),
    _group("CAN-0756de76cc79ac54ec77", "CAN-8b65b2c77506241d723e", signals=["title_author_year", "explicit_version_statement"], rationale="THEX report title variants describe the same metapattern-mining work."),
    _group("CAN-5cd5e316cdfe3f7059a8", "CAN-f721247a0f24632a3abc", signals=["arxiv_related_doi", "explicit_version_statement"], rationale="ArXiv and published versions differ only by a title typo and share the study abstract."),
    _group("CAN-70e83d35cfe43943822d", "CAN-8518308ec397d53661fa", signals=["arxiv_related_doi", "explicit_version_statement"], rationale="ArXiv and ICSE-SEIP versions of the Xerox refactoring study."),
    _group("CAN-65c895148dae261d405d", "CAN-111abf1772d63d806fba", signals=["arxiv_related_doi", "explicit_version_statement"], rationale="ArXiv and IEEE versions of the requirements-interruption study."),
    _group("CAN-763c4f76104ded973517", "CAN-f272f35d15d0e5eb60af", "CAN-2f73260072efe2737f50", "CAN-66ed53a651c37948259e", "CAN-0cbde805a5987632c3e2", signals=["explicit_version_statement", "shared_sample_project"], rationale="Article and repository artifacts carry the same GitHub Copilot review abstract and author/year provenance."),
    _group("CAN-e8ade0480349870686ee", "CAN-fe83015cf4924b9d9ba9", signals=["explicit_version_statement", "shared_sample_project"], rationale="Ansible Lightspeed experience report and published service paper share the supplied study abstract."),
    _group("CAN-253754d57190a61c13ce", "CAN-ac1c06ebcf420918c681", "CAN-9e9bb70f5f51758ee056", signals=["arxiv_related_doi", "explicit_version_statement"], rationale="ArXiv, SSRN and journal versions of syntax-aware on-the-fly code completion."),
    _group("CAN-b4195c64e64cb7ec508b", "CAN-7e348a654ee7da95ae2c", signals=["title_author_year", "manual_other"], rationale="Expanded-title metadata variants for the same computational-chemistry work; retained as one family but outside-domain screening remains separate."),
    _group("CAN-b13bb772f65c0f0b02cd", "CAN-025a7adc4252d225fc7f", signals=["explicit_version_statement", "title_author_year"], rationale="Preprint and journal-title variants of the same generative-AI/DevOps review."),
    _group("CAN-091a78f5a8b0a931f6ca", "CAN-2e37c24e76e00226ff66", signals=["explicit_version_statement", "shared_sample_project"], rationale="MergeBERT working-title and published program-merge-conflict report."),
    _group("CAN-9fbca3f6fcdc48d6df25", "CAN-117ba5655c0f43a0b598", signals=["arxiv_related_doi", "explicit_version_statement"], rationale="ArXiv systematic-review title and published mapping-study title share the same supplied review evidence."),
    _group("CAN-3ed63397e99a3438183f", "CAN-8f55fc6742c14d7cedec", signals=["shared_sample_project", "manual_other"], rationale="Senatus and DeSkew-LSH report titles share author/year and highly similar supplied method abstract; preserved as one project family, not one report."),
]


KEEP_SEPARATE_PAIRS = {
    frozenset(("CAN-7478ece040e9ed80bff1", "CAN-db1e15fdb9ef3f6bbbc4")): "Different evaluated Claude model/version and no shared abstract evidence.",
    frozenset(("CAN-f84924a16e79f62a2fe5", "CAN-bf26855ef294caff989c")): "Thesis and conference report may be related but metadata does not establish the same study population or result.",
    frozenset(("CAN-e7927c1256d02233acc5", "CAN-0187aaf45fe1ebffb2c2")): "Distinct replication targets and materially different supplied abstracts.",
    frozenset(("CAN-fa441b5e00833c146c99", "CAN-1c04c3b6783dfe5a3826")): "Scrumban and Scrumbanfall are distinct proposed process integrations.",
    frozenset(("CAN-cabf128b05844e0a7959", "CAN-76a7921450b1e277f984")): "Research paper and later keynote have different titles, years and evidence targets; similarity is thematic only.",
}


def _read_reports() -> list[dict[str, str]]:
    with (D06 / "canonical_records.csv").open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _candidates(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    blocks: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        if row["normalized_first_author"] and row["publication_year"]:
            blocks[row["normalized_first_author"]].append(row)
    candidates = []
    for members in blocks.values():
        for index, left in enumerate(members):
            for right in members[index + 1:]:
                if abs(int(left["publication_year"]) - int(right["publication_year"])) > 2:
                    continue
                if left["normalized_title"] == right["normalized_title"]:
                    continue
                title_score = SequenceMatcher(None, left["normalized_title"], right["normalized_title"]).ratio()
                a = " ".join(left["abstract"].casefold().split())
                b = " ".join(right["abstract"].casefold().split())
                abstract_score = SequenceMatcher(None, a, b).ratio() if min(len(a), len(b)) >= 100 else 0.0
                if title_score < 0.88 and abstract_score < 0.85:
                    continue
                pair = frozenset((left["canonical_id"], right["canonical_id"]))
                accepted = any(pair <= set(group["members"]) for group in APPROVED_MULTI_REPORT_GROUPS)
                if accepted:
                    decision, rationale = "consolidate", "Both reports belong to an approved, explicitly reasoned multi-report group."
                elif pair in KEEP_SEPARATE_PAIRS:
                    decision, rationale = "keep_separate", KEEP_SEPARATE_PAIRS[pair]
                else:
                    decision, rationale = "keep_separate", "Similarity alone is insufficient; conservative singleton treatment retained pending later source evidence."
                candidates.append({
                    "candidate_id": "PAIR-" + hashlib.sha256("|".join(sorted(pair)).encode()).hexdigest()[:16],
                    "left_canonical_id": left["canonical_id"], "right_canonical_id": right["canonical_id"],
                    "title_similarity": f"{title_score:.6f}", "abstract_similarity": f"{abstract_score:.6f}",
                    "first_author_key": left["normalized_first_author"],
                    "year_delta": abs(int(left["publication_year"]) - int(right["publication_year"])),
                    "decision": decision, "rationale": rationale,
                    "reviewer_id": VERSION, "decided_at_utc": DECIDED_AT,
                })
    return sorted(candidates, key=lambda r: r["candidate_id"])


def _representative(members: list[dict[str, str]]) -> dict[str, str]:
    repository_prefixes = ("10.48550/", "10.5281/", "10.6084/", "10.2139/", "10.20944/")
    def score(row: dict[str, str]) -> tuple[Any, ...]:
        publisher_doi = bool(row["doi"]) and not row["doi"].startswith(repository_prefixes)
        artifact_penalty = any(word in row["title"].casefold() for word in ("replication package", "peer review report", "poster", "slides"))
        return (publisher_doi, not artifact_penalty, len(row["abstract"]), bool(row["doi"]), row["published"], row["canonical_id"])
    return max(members, key=score)


def consolidate(rows: list[dict[str, str]]) -> tuple[list[dict[str, Any]], list[dict[str, str]], list[dict[str, Any]]]:
    by_id = {row["canonical_id"]: row for row in rows}
    assigned: set[str] = set()
    groups = []
    for spec in APPROVED_MULTI_REPORT_GROUPS:
        members = spec["members"]
        if len(set(members)) != len(members) or not set(members) <= set(by_id):
            raise ConsolidationError(f"invalid approved group members: {members}")
        overlap = assigned & set(members)
        if overlap:
            raise ConsolidationError(f"report assigned to multiple approved groups: {sorted(overlap)}")
        assigned.update(members)
        groups.append(spec)
    for canonical_id in sorted(set(by_id) - assigned):
        groups.append({"members": [canonical_id], "linkage_signals": ["singleton"], "rationale": "No sufficiently supported cross-version relationship at D07 metadata review."})

    families, mapping = [], []
    for spec in groups:
        member_rows = [by_id[x] for x in spec["members"]]
        representative = _representative(member_rows)
        family_id = "FAM-" + hashlib.sha256("|".join(sorted(spec["members"])).encode()).hexdigest()[:20]
        families.append({
            "family_id": family_id,
            "member_canonical_ids": sorted(spec["members"]),
            "representative_canonical_id": representative["canonical_id"],
            "member_count": len(spec["members"]),
            "consolidation_basis": spec["rationale"],
            "linkage_signals": spec["linkage_signals"],
            "family_reviewer_agent_id": VERSION,
            "status": "candidate_for_title_abstract_screening",
            "accountable_author_confirmation_status": "pending",
        })
        for cid in spec["members"]:
            mapping.append({"canonical_id": cid, "family_id": family_id, "representative": str(cid == representative["canonical_id"]).lower()})
    if len(mapping) != len(rows) or len({m["canonical_id"] for m in mapping}) != len(rows):
        raise ConsolidationError("D07 report-to-family conservation failed")
    return sorted(families, key=lambda x: x["family_id"]), sorted(mapping, key=lambda x: x["canonical_id"]), _candidates(rows)


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def build(output_dir: Path = OUTPUT) -> dict[str, Any]:
    if output_dir.exists():
        raise ConsolidationError(f"immutable D07 output already exists: {output_dir}")
    rows = _read_reports()
    families, mapping, candidates = consolidate(rows)
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="d07-", dir=str(output_dir.parent)))
    try:
        family_path = staging / "study_families.jsonl"
        family_path.write_text("".join(json.dumps(x, sort_keys=True, ensure_ascii=False) + "\n" for x in families), encoding="utf-8")
        _write_csv(staging / "canonical_to_family.csv", mapping)
        _write_csv(staging / "version_candidate_decisions.csv", candidates)
        decision_counts = Counter(row["decision"] for row in candidates)
        manifest = {
            "status": "complete",
            "protocol_version": "1.3", "pipeline_version": VERSION,
            "decided_at_utc": DECIDED_AT,
            "input_d06_manifest_path": str((D06 / "d06_manifest.json").relative_to(ROOT)),
            "input_d06_manifest_sha256": sha256(D06 / "d06_manifest.json"),
            "canonical_report_count": len(rows), "study_family_count": len(families),
            "multi_report_family_count": sum(x["member_count"] > 1 for x in families),
            "singleton_family_count": sum(x["member_count"] == 1 for x in families),
            "reports_in_multi_report_families": sum(x["member_count"] for x in families if x["member_count"] > 1),
            "version_candidate_pair_count": len(candidates),
            "candidate_decision_counts": dict(sorted(decision_counts.items())),
            "unresolved_candidate_count": 0,
            "conservation_pass": sum(x["member_count"] for x in families) == len(rows),
            "interpretation_boundary": "Metadata-supported candidate study families for screening. Conservative keep-separate decisions may be revisited only with source-grounded evidence and logged change control; no eligibility, quality, novelty, or PRISMA inclusion decision is made.",
            "files": {},
        }
        for path in sorted(staging.iterdir()):
            manifest["files"][path.name] = {"sha256": sha256(path), "bytes": path.stat().st_size}
        manifest_path = staging / "d07_manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (staging / "d07_manifest.json.sha256").write_text(f"{sha256(manifest_path)}  d07_manifest.json\n", encoding="utf-8")
        staging.rename(output_dir)
        return manifest
    except Exception:
        shutil.rmtree(staging, ignore_errors=True); raise


def verify(output_dir: Path = OUTPUT) -> dict[str, Any]:
    manifest_path = output_dir / "d07_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for name, meta in manifest["files"].items():
        path = output_dir / name
        if sha256(path) != meta["sha256"] or path.stat().st_size != meta["bytes"]:
            raise ConsolidationError(f"D07 file mismatch: {name}")
    if (output_dir / "d07_manifest.json.sha256").read_text().split()[0] != sha256(manifest_path):
        raise ConsolidationError("D07 manifest sidecar mismatch")
    if not manifest["conservation_pass"] or manifest["unresolved_candidate_count"] != 0:
        raise ConsolidationError("D07 reconciliation failed")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=("run", "verify")); args = parser.parse_args()
    result = build() if args.command == "run" else verify()
    print(json.dumps({k: result[k] for k in ("status", "canonical_report_count", "study_family_count", "multi_report_family_count", "unresolved_candidate_count", "conservation_pass")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
