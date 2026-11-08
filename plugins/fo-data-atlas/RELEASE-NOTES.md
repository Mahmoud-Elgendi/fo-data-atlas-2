# F&O Data Atlas 0.2.0

Prepared 8 November 2026. Publication and native host activation are reported separately; a local package is not a published GitHub release.

- Keeps the complete existing offline metadata corpus: 447,389 documents, 11 source identities. The corpus hash and original definitions are unchanged; this is not a newly collected/verified .49 baseline.
- Adds exported SQL view inspection: original SQL, nested underlying views/tables/functions, explicit gaps, and optional named dependency SQL files with provenance. Same-named objects in different snapshots are never merged.
- Adds GitHub bootstrap/install/update and an update offer once per query-skill conversation. Unavailable checks continue locally; updates preserve source/project settings and previous files. Same-version cached downloads are verified before reuse.
- Retains branded setup, Codex/Claude choices and global/project scope. Installation copies are promoted only after offline payload integrity succeeds.
- Handles long Windows installation paths through extended-path copying/staging, with a regression fixture for deeply nested project paths.
- Packages target-specific PO and receipt examples with SQL/mapping/checks, evidence and a sample schema. Vendor invoice remains a starter.
- Fixes exact GlobalOptionsetMetadata casing support and allows explicit schema-validated project exceptions. Financial dimension and transaction/posted/current-rate amount rules are documented.

Limitations: original source SQL is not certified Fabric SQL; runtime X++, dynamic SQL and extension merging may add unseen dependencies. Native host loading, live private GitHub transfer and business reconciliation require separately recorded evidence. Receipt native currency/amount population remains sample-accepted only. The downloader currently supports one full ZIP below 2 GiB, not split assets or binary patches.
