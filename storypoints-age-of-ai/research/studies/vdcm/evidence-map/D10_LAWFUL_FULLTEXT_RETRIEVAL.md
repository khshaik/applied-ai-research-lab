# D10 lawful full-text retrieval

Status: **complete**  
Pipeline: `d10-lawful-fulltext/1.0.0`  
Input: 2,076 D09 title/abstract inclusions

D10 reconciled every retained study family to a terminal retrieval status:

- 1,605 lawfully open, PDF-signature-verified full texts;
- 34 access-blocked or paywalled reports;
- 436 reports for which a lawful full text was not retrieved after documented
  candidate and/or landing-page attempts;
- one report with no lawful full-text location identified.

Each retrieved PDF is bound to its family, source URL, lawful-location basis,
byte count, and SHA-256. The frozen package contains 2,764,178,471 bytes of
retrieved PDFs. Landing pages, HTML responses, login pages, DOI metadata and
non-PDF responses were never treated as full text. No authentication, paywall,
or technical control was bypassed.

The first retrieval batches mistakenly labelled a fixed batch-declaration time
as an HTTP-attempt time. Before D10 freeze, the field was transparently renamed
to `retrieval_batch_declared_at_utc`; URLs, responses, statuses, decisions and
PDFs were unchanged. Later fallback attempts carry request timestamps. The
correction record is checksum-bound into the final manifest.

Retrieval status is not full-text eligibility. The 1,605 retrieved reports now
enter D11; the 471 non-retrieved/paywalled reports remain visible in the study
flow and cannot support claims based on unread content.

Canonical artifacts are under
`gate2/output/systematic/v1.3/20260816/d10/final/`.
