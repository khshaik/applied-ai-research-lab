# D07 study-family consolidation

Status: **complete**  
Pipeline: `d07-study-family-consolidation/1.0.0`  
Input: 3,962 canonical D06 report records

D07 produced 3,930 candidate study families. Twenty-three families contain
multiple reports, covering 55 canonical reports; 3,907 families are
singletons. The conservation identity passes: every one of the 3,962 reports
maps to exactly one family and every family has exactly one deterministic
representative.

The version-candidate audit generated 39 candidate report pairs. Thirty-four
pairs were consolidated within the 23 explicitly reasoned groups. Five pairs
were retained as separate studies because similarity alone did not establish a
shared population, experiment, result, or publication lineage. No unresolved
candidate remains.

Consolidation used source-visible linkage signals such as related DOI/arXiv
identity, explicit version or companion-artifact wording, shared study/project
evidence, and closely corresponding multilingual metadata. Similar title,
author, year, or abstract text generated candidates but never independently
authorized a merge. This conservative rule prevents thematic neighbors from
being collapsed into a single study.

The families are metadata-supported screening units. They are not eligibility,
quality, inclusion, novelty, or PRISMA decisions. A keep-separate decision may
be changed only when later lawful full text supplies explicit linkage evidence,
with the change recorded in the review audit trail.

Canonical artifacts are under
`gate2/output/systematic/v1.3/20260816/d07/`. The manifest SHA-256 is
`154871436630f723b59a827d6d1e977129cc70d1e4bfe8c926adb8b28fa0b8f1`;
it binds the family file, report-to-family map, candidate decisions, and the
D06 input manifest.
