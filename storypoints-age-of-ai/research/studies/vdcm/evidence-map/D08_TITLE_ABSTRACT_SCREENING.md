# D08 isolated title/abstract screening

Status: **complete**  
Controller: `d08-screening-controller/1.0.0`  
Input: 3,930 D07 candidate study families

The controller produced 40 immutable, checksum-bound shards containing the
same family-level metadata and frozen criteria for both screening passes.
Passes A and B ran in separate agent contexts, declared that the other pass was
not visible, used the versioned protocol-v1.3 prompts, and returned one decision
for every family.

Pass A classified 2,559 families `include`, 1,066 `exclude`, and 305 `unclear`.
Pass B classified 2,096 `include`, 1,647 `exclude`, and 187 `unclear`. Both
3,930-row artifacts pass exact family, representative-record, shard-checksum,
prompt-version, provenance, range, and completeness validation.

The agents agreed on 2,686 decisions (68.35% agent concordance): 1,821
include/include, 795 exclude/exclude, and 70 unclear/unclear. The remaining
decision pairs comprise 892 direct include/exclude disagreements and 352 cases
where at least one pass returned unclear. Under the frozen rule, all unclear
agreements also require adjudication, producing 1,314 D09 candidates and 2,616
unambiguous consensus decisions.

This percentage is an AI-agent reproducibility diagnostic, not human
inter-rater reliability. Title/abstract inclusion is only permission to seek
and assess lawful full text; it does not establish study quality, novelty, or
support for a manuscript claim.

Artifacts are under `gate2/output/systematic/v1.3/20260816/d08/`. Pass A is
bound by SHA-256
`68a72046082f81281086dee0e19a2a2d4ad36063aab8410c9ad2c2bfd1a086b1`;
pass B by
`56efe0460e716fc090a638eda8d8dd323e8b6012a13d4bad00bff9134762b2e4`;
and the D09 adjudication packet by
`1412c1f44a7676b975d719ef8f59a1b8aec21eb2cb71865fbe7c4fddb7ae4d70`.
