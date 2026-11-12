# Unreleased review: workflow/timesheet analyst pilot

- Routes retrieval through the installed package first, with explicit missing-profile boundaries.
- Clarifies workflow grain, first-submission user/date pairing, target IDs, company-case evidence and polymorphic resource joins.
- Adds configurable event-history and timesheet-first-submission templates, with no tenant-specific IDs, live results or employee values.
- Adds synthetic logical fixtures and a planned 20-scenario manual analyst acceptance checklist. These do not certify native host loading, clean-PC installation or Fabric business correctness.

Version manifests remain on the published 0.4.0 baseline during review. Assign a new version before packaging this update; published assets and the metadata catalog are unchanged.

# F&O Data Atlas 0.4.0

Published 8 November 2026; publication and tools ZIP hash verified 12 November 2026. Native activation and clean-PC transfer remain separately tracked.

- Adds a buildless private Git-backed npx entrance for install, update and check. It delegates to the existing verified Python installer; no npm registry publication, dependencies or lifecycle scripts.
- Prints host-specific START HERE prompts after setup and includes them in JSON output.
- Documents another-PC prerequisites, authentication, host activation and first use.
- Reuses exact 0.3.0 metadata assets/hashes; earlier published files remain unchanged.

Remote private npx transfer and native host activation require separate verification.

## Retained from 0.3.0

- Separates the small tools package from independently versioned, shared metadata cache. Compatible tools-only updates do not redownload unchanged metadata.
- Adds Core (default) and Full offline selection. Both retain 447,389 object identities; Core has 204,438 readable document identities and Full has all originals. Missing evidence is explicit.
- Core includes both SQL catalogs, table/view/entity/EDT/enum XML and English labels. Full additionally supplies classes, forms, reports and all languages. Scope/source identities and original hashes are preserved.
- Fixes extended Windows paths in the download/extraction/verification path, not just installation copy. Adds regression and cache/upgrade tests.
- Keeps view SQL and dependency inspection, target-specific PO/receipt examples, exact schema naming and source/posted/current-rate distinctions. Vendor invoice remains a starter.
- Metadata downloads: Core 303.8 MiB; Full 1.21 GiB. Tools ZIP size is given by its build. Cache entries are retained across profiles/projects; metadata activation is atomic and verified.

All evidence comes from the existing exports. No new .49 baseline or business/runtime reconciliation is claimed. Original source SQL is not automatically Fabric-ready; native host loading and live private release transfer require separate verification. Published 0.2.0 files remain unchanged.
