# F&O Data Atlas: hours-scale release plan

Date: 2026-11-08, Asia/Riyadh. Proposed package version: 0.2.0. Repository: https://github.com/Mahmoud-Elgendi/fo-data-atlas-2. Scope accepted: ship the initial release, retain the complete current metadata corpus, and include view SQL/dependency inspection. Publication/native host checks are separate gates.

## Outcome

Deliver a privately downloadable offline plugin using the existing reference snapshot. A recipient authenticates to GitHub, downloads/verifies the complete package, selects Codex/Claude and global/project scope, exports their own Fabric schema, and drafts evidence-backed SQL with named mapping/check files. Local evidence remains usable if a later update check is unavailable or declined.

The owner explicitly resumed plugin work using current exports. New .49 VM collection is a future metadata update and is not a release prerequisite. DWH/ETL deployment remains on hold. Do not relabel current evidence as a freshly verified .49 baseline.

## Settled and open decisions

| Decision | State |
|---|---|
| Use current exports and finish within hours | Owner requested |
| Private repository and offline recipient use | Previously agreed; privacy must be read back before upload |
| Repository | Mahmoud-Elgendi/fo-data-atlas-2 |
| Authentication | Owner prefers commands in their IDE terminal; use that route |
| Update behavior | Check once per skill conversation, offer update, retain old files/settings; no native IDE startup-hook claim |
| SQL generation | Evidence-based, field-first, line grain, actual Fabric schema, named SQL/mapping/checks |
| Release examples | Accepted first-release scope: PO/receipt now; vendor invoice remains a starter; all current metadata and view inspection included |
| Package version | Proposed 0.2.0; distinct from F&O source versions |

The owner approved shipping this scope and iterating, requiring original view SQL plus underlying views/tables and an offer to retrieve their SQL. This is included in 0.2.0. The completed invoice example remains next; invoice metadata itself is retained in full.

## Working budget

These are estimates for active work, not a measured completion guarantee. Reuse the 1.623 GiB reference database; regenerate the package manifest/ZIP, not the corpus. Reserve approximately 3â€“4 hours including contingency; upload speed, authentication and native host availability can extend delivery.

| Order | Work | Budget | Completion evidence |
|---|---|---|---|
| 1 | Agree scope; terminal authentication in parallel | 10â€“15 min | Scope answer; repository access/privacy readback |
| 2 | Align rules/linter and package selected examples | 45â€“60 min | Exact schema casing checks; curated examples/limitations |
| 3 | Make release/install/update flow coherent | 30â€“45 min | Versioned manifests; bootstrap; retry/config preservation checks |
| 4 | Regression, integrity and clean offline smoke tests | 30â€“45 min | Test log; reference hashes; host evidence or explicit gaps |
| 5 | Package, publish and test real download | 30â€“60 min | ZIP/SHA256; release URL; real authenticated download verification |

Detailed checklist: [TASKS.md](TASKS.md). Terminal instructions: [TERMINAL.md](TERMINAL.md). Observations and commands: [ACTIONS.md](ACTIONS.md).

## Release contents

- Current full offline corpus: 447,389 documents from 11 separately identified sources, with original source identities/hashes and coverage limits retained.
- Query/setup skills, SQL view/dependency inspector, Python standard-library helpers, branded Windows setup and GitHub release helper.
- Reusable SQL rules: exact-case schema-approved exceptions, Company convention, IsDelete selection, filtered status subqueries, mandatory dimensions when applicable, and amount/FX distinctions.
- Curated PO and receipt example bundles, if scope accepted. State their target schema fingerprint and sample-level evidence; recipients adapt/validate against their own schema. Exclude test PO filters from general examples and exclude archived complex receipt drafts.
- Descriptive SQL, mapping and checks files; preserve unverified/runtime/business flags unless actual evidence supports a change.
- Quick start, installation/update commands, release notes, manifest, checksums and known limitations.

General query support extends beyond these examples through metadata/schema inspection. It does not mean every F&O table, custom join or business process is runtime verified.

## Priority technical corrections

The current reusable rules/linter conflict with approved exact dbo.GlobalOptionsetMetadata casing. Correct that through explicit target-validated exceptions while retaining uppercase SQL keywords and lowercase ordinary physical identifiers; do not broadly waive case checking. Update stale documentation claiming no actual project schema exists.

Both host manifests remain 0.1.1; old ZIPs lack the GitHub helper. Bump the new package identity and remove hardcoded 0.1.1 test expectations. Regenerate package-manifest.json after final content changes. Existing released archives stay immutable.

The prepared helper already verifies release ZIP size/hash, safe extraction and all manifest/reference hashes. Real private GitHub download is not verified. Test an accepted/declined/unavailable update, repeat update after an interrupted or already completed download, and preservation of project schema/source selection. Fix confirmed retry blockers before release.

## Publication boundary

Prepare a clean plugin-only checkout/staging directory. The current metadata-explorer workspace has many unrelated changes; never push its whole tree or attach the new remote to it as a shortcut. Keep generated SQLite/large ZIP files as release assets; commit the deliberately selected small source/docs/tests. Include build prerequisites or clearly document maintainer-only tools that are not shipped.

Create the source commit, attach the newly built full package and checksum to a draft release, inspect the files and source claims, then publish. The stable release must use the same package version as both host manifests and the required asset filename. A draft release is not downloadable through the helper's stable latest-release path.

## Done means

1. Scope and package identity recorded; existing source baseline accurately named.
2. Both host manifests/local links validate; required regression passes and payload/ZIP hashes verify.
3. A clean recipient download retrieves all evidence without original source folders, an Atlas server or VM access.
4. Setup/global-project choices, source configuration and offline evidence retrieval work. Native Codex/Claude activation is recorded separately; unavailable native checks remain gaps, not passed tests.
5. The real published GitHub asset satisfies downloader naming/digest requirements; local-only or draft-only output is not reported as a published release.
6. Source settings survive upgrade; offline/declined checks continue locally. Metadata versions are not silently switched.
7. Codes, commands, outcomes, failures and remaining limitations are captured in the action log/release notes. Source/runtime/business validation remain separate.

If a gate blocks delivery, document that exact blocker and deliver the verified local package/runbook while continuing unaffected work. Do not describe unexecuted publication or host activation as completed.
