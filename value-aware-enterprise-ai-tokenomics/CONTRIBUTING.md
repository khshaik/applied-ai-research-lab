# Contributing

This repository preserves prospectively specified research records. Changes must not silently rewrite a frozen protocol, case set, reference label, result, or closure manifest.

## Change classes

- **Documentation correction:** clarify wording without changing a scientific claim or result.
- **Code maintenance:** improve maintainability while preserving behavior and tests.
- **New exploratory work:** add a new versioned directory and label it exploratory.
- **New registered study:** add a protocol and immutable design lock before examining evaluation labels.

## Requirements

1. Create a focused branch and describe the scientific effect of the change.
2. Keep future held-out material, credentials, private organizational records, and submission-system reports outside Git.
3. Run `make verify` before opening a pull request.
4. Add or update tests for code changes.
5. Record material protocol deviations explicitly; never overwrite the original record.
6. Update claim-to-evidence and citation records when manuscript claims change.
7. Do not reuse the 24 pilot or 48 calibration cases as confirmatory evidence for a successor method.

Generated-AI assistance must be disclosed according to the target venue's policy. Human contributors remain responsible for correctness, citations, licensing, confidentiality, originality review, and research integrity.
