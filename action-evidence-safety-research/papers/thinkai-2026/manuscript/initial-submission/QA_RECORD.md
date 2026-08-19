# Initial-submission QA record

## Scope

This record documents the final checks applied to the anonymous review manuscript on 18 August 2026. It does not claim that the conference portal or organizer requirements were independently confirmed.

## Document and PDF validation

- PDF page count: 14.
- Visual inspection: every page inspected after Microsoft Word export and metadata-clean PDF rewriting.
- Layout corrections: Table 4 caption/table pagination repaired; Table 8 authorization-harms header shortened to prevent awkward wrapping.
- Accessibility audit: zero high-, medium-, or low-severity findings.
- Tracked changes: none detected.
- Comments parts: none detected.
- Placeholder scan: no `TODO`, `TBD`, `FIXME`, author placeholder, or affiliation placeholder detected.
- PII scan: no user path, organization path, email, author affiliation, or corresponding-author string detected in extracted manuscript text or document properties.
- DOCX core properties: anonymous creator and last-modified-by fields.
- PDF metadata: empty creator identity; descriptive anonymous title/subject only.

## Scientific consistency

- Design cases: 72 exposed cases across six domains.
- Held-out cases: 24; status `SEALED_NOT_RELEASED`.
- Safe completion: 25/27 = 0.9259.
- Harmful action: 14/45 = 0.3111.
- Mean normalized validation cost: 0.5472.
- False blocks: 2.
- FIXED_0.20 comparator: 27/27 safe completion, 18/45 harmful actions, mean cost 0.8000.
- Gate: seven criteria passed; safe completion failed.
- Decision: `FAIL_KEEP_HELD_OUT_SEALED`.

The authoritative sources are linked in [`../../ARTIFACT_TRACEABILITY.md`](../../ARTIFACT_TRACEABILITY.md).

