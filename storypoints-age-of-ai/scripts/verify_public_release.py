#!/usr/bin/env python3
"""Fail closed on release integrity, secret patterns, and GitHub size limits."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path


SECRET_PATTERNS = {
    "private_key": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "github_token": re.compile(rb"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    "aws_access_key": re.compile(rb"\bAKIA[0-9A-Z]{16}\b"),
    "openai_secret": re.compile(rb"\bsk-[A-Za-z0-9_-]{32,}\b"),
    "credential_url": re.compile(
        rb"[a-zA-Z][a-zA-Z0-9+.-]{0,20}://[^\s/@:]{1,128}:[^\s/@]{1,128}@"
    ),
}
PROHIBITED_NAMES = {
    ".env", "production_seed_manifest.json", "sealed_seed_values.json",
    "context.txt", "temp.txt",
}
PROHIBITED_PARTS = {".git", ".pdf-venv", ".venv", "__pycache__", "restricted"}
ARCHIVES = {".docx", ".xlsx", ".pptx"}
MAX_GITHUB_FILE = 100 * 1024 * 1024
RUNTIME_GENERATED_PARTS = {
    ".pytest_cache", "__pycache__", ".mypy_cache", ".ruff_cache",
    ".approval_tests_temp",
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def scan_bytes(data: bytes) -> list[str]:
    return [name for name, pattern in SECRET_PATTERNS.items() if pattern.search(data)]


def scan_stream(handle, *, with_digest: bool) -> tuple[str | None, list[str]]:
    """Scan bounded windows so large one-line JSON never enters one regex call."""
    digest_state = hashlib.sha256() if with_digest else None
    hits: set[str] = set()
    tail = b""
    while True:
        chunk = handle.read(1024 * 1024)
        if not chunk:
            break
        if digest_state is not None:
            digest_state.update(chunk)
        window = tail + chunk
        for name, pattern in SECRET_PATTERNS.items():
            if name not in hits and pattern.search(window):
                hits.add(name)
        tail = window[-512:]
    return (
        digest_state.hexdigest() if digest_state is not None else None,
        sorted(hits),
    )


def scan_file(path: Path) -> tuple[str, list[str]]:
    with path.open("rb") as handle:
        actual_digest, hits = scan_stream(handle, with_digest=True)
    assert actual_digest is not None
    return actual_digest, hits


def verify(root: Path, *, progress_every: int = 500) -> dict:
    errors: list[str] = []
    findings: list[dict] = []
    manifest_path = root / "PUBLIC_RELEASE_MANIFEST.json"
    exclusions_path = root / "PUBLIC_RELEASE_EXCLUSIONS.json"
    if not manifest_path.is_file() or not exclusions_path.is_file():
        raise SystemExit("release manifests are missing")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = {item["path"]: item for item in manifest["included_files"]}
    actual_files = [
        path for path in root.rglob("*")
        if path.is_file()
        and path.name not in {manifest_path.name, exclusions_path.name}
        and not any(part in RUNTIME_GENERATED_PARTS for part in path.relative_to(root).parts)
        and path.suffix not in {".pyc", ".pyo"}
    ]
    actual_rel = {path.relative_to(root).as_posix() for path in actual_files}
    if actual_rel != set(expected):
        errors.append("export population does not match PUBLIC_RELEASE_MANIFEST.json")
    total = len(actual_files)
    print(f"[verify] scanning {total} manifested files", file=sys.stderr, flush=True)
    for index, path in enumerate(actual_files, start=1):
        relative = path.relative_to(root)
        posix = relative.as_posix()
        if path.stat().st_size >= MAX_GITHUB_FILE:
            errors.append(f"GitHub file-size limit reached: {posix}")
        restricted_notice = "restricted" in relative.parts and path.name == "README.md"
        if path.name in PROHIBITED_NAMES or (
            any(part in PROHIBITED_PARTS for part in relative.parts[:-1]) and not restricted_notice
        ):
            errors.append(f"prohibited release path: {posix}")
        record = expected.get(posix)
        actual_digest, hits = scan_file(path)
        if record and (path.stat().st_size != record["size_bytes"] or actual_digest != record["sha256"]):
            errors.append(f"manifest mismatch: {posix}")
        if hits:
            findings.append({"path": posix, "categories": hits})
        if path.suffix.lower() in ARCHIVES and zipfile.is_zipfile(path):
            with zipfile.ZipFile(path) as archive:
                for member in archive.infolist():
                    if member.file_size > 20 * 1024 * 1024:
                        continue
                    with archive.open(member) as member_handle:
                        _, member_hits = scan_stream(member_handle, with_digest=False)
                    if member_hits:
                        findings.append({"path": f"{posix}!{member.filename}", "categories": member_hits})
        if progress_every > 0 and (index % progress_every == 0 or index == total):
            print(f"[verify] {index}/{total} files", file=sys.stderr, flush=True)
    if findings:
        errors.append("potential secret material detected; see finding paths/categories")
    result = {
        "status": "PASS" if not errors else "FAIL",
        "file_count": len(actual_files),
        "size_bytes": sum(path.stat().st_size for path in actual_files),
        "maximum_file_bytes": max((path.stat().st_size for path in actual_files), default=0),
        "secret_findings": findings,
        "errors": errors,
    }
    if errors:
        print(json.dumps(result, indent=2))
        raise SystemExit(2)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("release_directory", type=Path)
    parser.add_argument("--progress-every", type=int, default=500)
    args = parser.parse_args()
    print(json.dumps(verify(args.release_directory.resolve(), progress_every=args.progress_every), indent=2))


if __name__ == "__main__":
    main()
