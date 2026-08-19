# Public Monorepo Release Policy

This record defines the GitHub-ready export boundary for the
`storypoints-age-of-ai` project inside the `applied-ai-research-lab` monorepo.

## Preserve in the release

- research concepts, protocols, amendments, freeze records, and decision packs;
- executable search registries, raw scholarly metadata, query logs, and checksums;
- normalized records, deduplication and study-family ledgers;
- screening, adjudication, appraisal, extraction, citation-chasing, D15–D17,
  and claim-verification artifacts;
- simulation source, configurations, tests, developmental outputs, comparator
  results, ablations, manifests, and pre-lock controls;
- repository-owned spreadsheets, figures, communication assets, manuscripts,
  declarations, and render/QA records;
- integrity manifests and SHA-256 records needed to reconstruct provenance.

## Never publish from this workspace

- credentials, API keys, access tokens, private keys, environment files, or
  connection strings;
- sealed production seeds, participant data, organizational logs, or restricted
  material;
- virtual environments, caches, temporary files, render scratch space, or
  operating-system metadata;
- working-session transcripts such as `context.txt` and `temp.txt`;
- third-party PDF bodies, quarantined documents, sanitized copies, or bulk
  extracted full text.

The last category is excluded for copyright, repository-size, and document-
safety reasons. Reproducibility is preserved through lawful-location records,
source identifiers, bibliographic metadata, source checksums, exact locators,
short supporting snippets, decisions, and derived evidence ledgers.

## Double-blind boundary

The prepared project contains citation metadata, declarations, workbooks, and
other material that can identify the author. Do not push it to a public remote
while double-blind review applies. Push only to a private repository, or wait
until the venue permits deanonymization.

## Release procedure

1. Run `python3 scripts/build_public_release.py --destination <empty-directory>`.
2. Run `python3 scripts/verify_public_release.py <export-directory>`. The verifier
   streams large artifacts and prints progress every 500 files; on cloud-backed
   storage, allow the scan to reach its final JSON result rather than interrupting
   it while progress is advancing.
3. From the export, run `make verify`. Public-package mode runs the
   redistribution-safe test subset, release-integrity checks, and manuscript
   verification. The complete local archive continues to run the full suite.
4. Review `PUBLIC_RELEASE_MANIFEST.json` and
   `PUBLIC_RELEASE_EXCLUSIONS.json`.
5. Add the exported folder to the monorepo only after the checks pass.
6. Review the staged Git file list before committing.
7. Push only after confirming the double-blind boundary above.
