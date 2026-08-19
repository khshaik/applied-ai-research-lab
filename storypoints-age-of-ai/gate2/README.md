# Gate 2 retrieval tooling

All exporters in this directory are restricted to `development_pilot`. Their
outputs support query engineering and discovery only. They do not represent a
frozen review corpus, eligible-study set, deduplicated study-family set, or
PRISMA count.

## Public open-index pilots

`open_index_pilot_queries.json` registers source-specific API translations for
OpenAlex, Semantic Scholar, and Crossref. The CLI requires this registry,
resolves the exact source/query-ID pair, and hashes the registry's exact bytes
into the export manifest. A supplied literal query is an assertion only and is
rejected if it differs from the registered query.

Example:

```text
python3 -m gate2.open_index_export openalex OA-S3R \
  gate2/output/development/openalex/OA-S3R-YYYYMMDD-pilot2 \
  --registry gate2/open_index_pilot_queries.json \
  --from-date 2019-01-01 --to-date 2026-08-15 --page-size 100 --max-pages 1
```

Use `--literal-query '...'` only to assert an expected registry value. It never
overrides the registry. The lower-level Python function remains available for
mocked tests and controlled library use, but only a non-empty registry hash
establishes registry provenance.

Each successful target is immutable and is published atomically only after it
contains raw JSON pages, a normalized CSV, a manifest, page and CSV hashes, and
a manifest checksum. Full retrieval hard-stops on volatile totals, empty
premature pages, duplicate source identifiers, missing/repeated continuation
tokens, invalid JSON, and malformed source responses. HTTP 429 and transient
server/network failures use bounded retry/backoff.

`--max-pages` is an explicit development safety cap. If it stops pagination,
the manifest records `complete_pagination=false` and
`retrieval_scope=truncated_development_pilot`; the API's reported total must not
be presented as an exported-record, eligible-study, or review-flow count.

The three indexes have different ranking, coverage, metadata, and query
semantics. A translation in this registry is not assumed equivalent to another
source's query and does not replace inaccessible subscription databases.

OpenAlex registry rows may explicitly select `query_mode=title_abstract_filter`
when full-text search causes documented precision failure. The exporter then
uses OpenAlex's field-specific `title_and_abstract.search` filter, records the
mode in the manifest, and rejects that mode for other sources. Missing mode
defaults to `fulltext_search` for backward compatibility.

## Query-appraisal hard stops

`query_appraisal.py` distinguishes `development_diagnostic_pass` from
`freeze_ready`. A bounded diagnostic may pass while an export remains
incomplete. Freeze readiness additionally requires complete pagination, the
Appendix 4.2 sample size (all records through 50, 50 for 51–1,000, and 100
above 1,000), passing known-item controls, and the operational
relevant-plus-uncertain burden band. The legacy `query_appraisal_pass` field is
a deprecated alias for `freeze_ready`; it cannot be true for an incomplete
export.

The completed OA-S3R development acceptance artifacts are under
`output/development/openalex/OA-S3R-20260815-pilot2-complete/` and
`output/development/query_appraisals/`. Its 50 decisions are query-precision
judgments only. Although the derived OA-S3R query result is
`freeze_ready=true` under registry v0.2, this is only a mechanical result. The
separate Section 4.1 neutral/disconfirming sentinel class is not yet registered,
so protocol acceptance remains pending alongside all other source–family
controls.

Registry v0.3 supersedes that v0.2 limitation for S3. It is stored in
`open_index_pilot_queries_v0.3.json` and requires family-scoped positive and
neutral/disconfirming sentinel classes. OA-S3R3 and S2-S3R3 pass these
developmental query controls; the systematic corpus remains unfrozen.
