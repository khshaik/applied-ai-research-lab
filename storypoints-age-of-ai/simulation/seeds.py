"""Deterministic, checksum-locked seed manifest generation."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Sequence


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def derive_seed(master_seed: int, namespace: str, index: int) -> int:
    if master_seed < 0 or index < 0 or not namespace:
        raise ValueError("master_seed/index must be non-negative and namespace non-empty")
    digest = sha256(f"{master_seed}:{namespace}:{index}".encode()).digest()
    return int.from_bytes(digest[:8], "big") & ((1 << 63) - 1)


@dataclass(frozen=True)
class SeedManifest:
    manifest_version: str
    master_seed: int
    development_seeds: tuple[int, ...]
    locked_evaluation_seeds: tuple[int, ...]
    common_random_numbers: bool
    checksum: str

    def verify(self) -> bool:
        payload = asdict(self)
        supplied = payload.pop("checksum")
        return supplied == sha256(_canonical(payload)).hexdigest()


def build_seed_manifest(
    master_seed: int,
    development_count: int,
    evaluation_count: int,
    *,
    common_random_numbers: bool = True,
) -> SeedManifest:
    if development_count <= 0 or evaluation_count <= 0:
        raise ValueError("development_count and evaluation_count must be > 0")
    payload = {
        "manifest_version": "1.0.0",
        "master_seed": master_seed,
        "development_seeds": tuple(
            derive_seed(master_seed, "development", i) for i in range(development_count)
        ),
        "locked_evaluation_seeds": tuple(
            derive_seed(master_seed, "locked_evaluation", i) for i in range(evaluation_count)
        ),
        "common_random_numbers": common_random_numbers,
    }
    checksum = sha256(_canonical(payload)).hexdigest()
    return SeedManifest(**payload, checksum=checksum)


def load_seed_manifest(path: str | Path) -> SeedManifest:
    """Load the locked core fields while permitting documentary metadata."""
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    required = {
        "manifest_version", "master_seed", "development_seeds",
        "locked_evaluation_seeds", "common_random_numbers", "checksum",
    }
    missing = required - value.keys()
    if missing:
        raise ValueError(f"seed manifest is missing: {sorted(missing)}")
    manifest = SeedManifest(
        manifest_version=value["manifest_version"],
        master_seed=int(value["master_seed"]),
        development_seeds=tuple(int(seed) for seed in value["development_seeds"]),
        locked_evaluation_seeds=tuple(int(seed) for seed in value["locked_evaluation_seeds"]),
        common_random_numbers=bool(value["common_random_numbers"]),
        checksum=value["checksum"],
    )
    if not manifest.verify():
        raise ValueError("seed manifest checksum does not match its locked fields")
    return manifest
