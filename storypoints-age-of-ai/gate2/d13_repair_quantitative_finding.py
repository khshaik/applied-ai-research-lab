"""One-record repair for a controller-identified D13 extraction defect."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


TARGET = "FAM-60c3404ce4f633d01f4f"
OUTPUT = Path("gate2/output/systematic/v1.3/20260816/d13/extraction_part_a.jsonl")


def main() -> None:
    original_lines = OUTPUT.read_text(encoding="utf-8").splitlines()
    rows = [json.loads(line) for line in original_lines]
    matches = [row for row in rows if row["family_id"] == TARGET]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one target row, found {len(matches)}")
    finding = matches[0]["measures_findings"][0]
    if finding["source_locator"] != "page 1" or not finding["quantitative"]:
        raise ValueError("target row no longer has the controller-reviewed shape")
    finding["reported_estimate"] = "sample size n=11; mean SUS=73; mean NASA-TLX=21"
    finding["reported_uncertainty"] = None
    new_lines = [json.dumps(row, sort_keys=True, ensure_ascii=False) for row in rows]
    changed = [i for i, (before, after) in enumerate(zip(original_lines, new_lines), 1) if before != after]
    if changed != [next(i for i, row in enumerate(rows, 1) if row["family_id"] == TARGET)]:
        raise ValueError(f"unexpected rows changed: {changed}")
    OUTPUT.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    digest = hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
    OUTPUT.with_suffix(OUTPUT.suffix + ".sha256").write_text(
        f"{digest}  {OUTPUT.name}\n", encoding="utf-8"
    )
    print(json.dumps({"family_id": TARGET, "changed_line": changed[0], "sha256": digest}))


if __name__ == "__main__":
    main()
