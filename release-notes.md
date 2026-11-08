# F&O Data Atlas 0.3.0

Prepared 8 November 2026; publication/native activation are separate checks.

- Separates the small tools package from independently versioned, shared metadata cache. Compatible tools-only updates do not redownload unchanged metadata.
- Adds Core (default) and Full offline selection. Both retain 447,389 object identities; Core has 204,438 readable document identities and Full has all originals. Missing evidence is explicit.
- Core includes both SQL catalogs, table/view/entity/EDT/enum XML and English labels. Full additionally supplies classes, forms, reports and all languages. Scope/source identities and original hashes are preserved.
- Fixes extended Windows paths in the download/extraction/verification path, not just installation copy. Adds regression and cache/upgrade tests.
- Keeps view SQL and dependency inspection, target-specific PO/receipt examples, exact schema naming and source/posted/current-rate distinctions. Vendor invoice remains a starter.
- Metadata downloads: Core 303.8 MiB; Full 1.21 GiB. Tools ZIP size is given by its build. Cache entries are retained across profiles/projects; metadata activation is atomic and verified.

All evidence comes from the existing exports. No new .49 baseline or business/runtime reconciliation is claimed. Original source SQL is not automatically Fabric-ready; native host loading and live private release transfer require separate verification. Published 0.2.0 files remain unchanged.
