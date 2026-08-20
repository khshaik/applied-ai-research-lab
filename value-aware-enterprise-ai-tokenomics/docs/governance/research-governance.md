# Research Governance

## Evidence classes

- **Exploratory:** may guide method development but cannot support confirmatory claims.
- **Engineering pilot:** verifies implementation behavior and instrumentation; not an effectiveness result.
- **Calibration/design:** exposed evidence used for method testing, diagnosis, or selection.
- **Held-out:** inaccessible before a frozen method and one-time release decision.
- **Restricted:** investigator-only or organization-sensitive material that is not committed to Git unless explicitly reclassified as exposed design evidence.

## Immutability

Frozen records are append-only. Corrections receive a new version and a manifest explaining what changed and why. A failed gate remains a failed gate; later tuning cannot replace it.

## Review provenance

Synthetic reviewers may stress-test clarity, leakage, and rubric consistency, but their agreement is AI–AI consistency rather than human inter-rater reliability. Publications and derivative work must preserve that distinction.

## Publication boundary

OVAR v1.0 is a prospective negative calibration on constructed cases. No held-out benchmark or field validation exists. Repository availability does not establish organizational ROI, causal effectiveness, production readiness, superiority, or global novelty.

## Double-blind submissions

Keep the repository private until the venue permits author identification. A public repository, Git history, license notice, DOI record, or manuscript directory can reveal authorship even if the submitted PDF is anonymous.
