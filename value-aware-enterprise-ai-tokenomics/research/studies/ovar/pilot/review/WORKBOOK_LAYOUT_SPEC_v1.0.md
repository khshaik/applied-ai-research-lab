# Reviewer Workbook Layout Specification v1.0

The final workbook is a transport layer for the versioned JSON records. JSON remains the machine-readable source of truth.

## Sheets

1. `Read Me` — study status, blinding rules, scale anchors, return instructions, and reviewer attestation.
2. `Cases` — 24 reviewer-visible cases; no investigator-only fields or policy results.
3. `Scores` — one row per case with the six 1–5 dimensions, flags, missing-information note, and boundary rationale.
4. `Rubrics` — definitions and boundary examples for each dimension.
5. `Checks` — formula-driven completeness, integer-range, duplicate-ID, and attestation checks.

## Editable cells

Only the reviewer identity/attestation cells and score/flag/narrative columns are editable. Input-case fields and formulas should be protected where supported.

## Required formula checks

- completed score cells = 144;
- every score is an integer between 1 and 5;
- 24 unique case identifiers;
- every 1 or 5 has a non-empty boundary rationale;
- leakage and ambiguity flags use allowed values;
- reviewer attests that restricted labels, policy outputs, and the other review were not accessed.

## Visual rules

Use frozen headers, wrapped descriptive text, restrained color, hidden gridlines, explicit input coloring, and conditional formatting for incomplete or invalid entries. The workbook must be rendered and visually checked before release.
