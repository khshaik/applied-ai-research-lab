# Research design and protocol artifacts

This directory contains the numbered research-development artifacts that were
previously stored at the repository root. Their filenames and bytes are
preserved; only their repository location changed on 20 August 2026.

The relocation reduces root-level clutter while keeping the research sequence
visible and auditable. Frozen protocol artifacts remain byte-identical. Legacy
paths recorded inside the frozen v1.3 package are resolved through the
checksum-bound relocation record in
[`../../docs/traceability/RESEARCH_DESIGN_RELOCATION_2026-08-20.json`](../../docs/traceability/RESEARCH_DESIGN_RELOCATION_2026-08-20.json).

## Phase map

| Phase | Purpose | Principal artifacts |
|---|---|---|
| 01 — Concept | Problem framing and research purpose | [`01_research_concept_brief.md`](01_research_concept_brief.md) |
| 02 — Evidence-map method | Protocol, executable searches, review controls, route decisions and freeze records | Files beginning with `02`, `02b`, `02d`, `02e`, and `02f` |
| 03 — Framework design | Constructs, causal model, propositions, operational anchors, readiness and simulation schema | Files beginning with `03` and `03b` |
| 04 — Simulation governance | Comparator specification, prototype status, preregistration and minimum production scope | Files beginning with `04` and `04b` |
| 05 — Reconciliation | Developmental simulation findings and interpretation boundary | [`05_developmental_simulation_reconciliation.md`](05_developmental_simulation_reconciliation.md) |

## Integrity boundary

- Relocation does not change a document's scientific content or approval state.
- The original frozen package remains unchanged as historical evidence.
- Consumers resolve legacy frozen paths through `gate2.frozen_paths`.
- Any future content amendment to a frozen artifact still requires the protocol's
  formal change-control process; relocation is not such an amendment.
- Public-release manifests must be regenerated after any structural change.
