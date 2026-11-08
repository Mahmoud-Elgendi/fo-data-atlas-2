# First-version verification — 4 November 2026

## 0.2.0 local release checks — 8 November 2026

- Complete project regression: 174 Python tests PASS (test-evidence/release-0.2.0-full-tests.log); eight formatter checks PASS. The focused Atlas suites contain 44 passing tests.
- Full offline database publication hash, both host manifests, skill/local links and nine real source-anchor checks PASS (test-evidence/release-0.2.0-verification.json). No original source folders or database connection are used for packed evidence reads.
- Real application-catalog CustCustomerV3Entity lineage: 50 objects and 14 original SQL definitions, with no unresolved blockers or truncation. Packaged as a source-engine example under examples/view-sql-custcustomerv3entity. Tables' catalog self-references are preserved without being mislabelled view cycles.
- PO/receipt sample-schema checks find only the known bounded-linter CTE review, explicitly recorded in each example's validation JSON. No physical-column/casing/deletion/Company issue remains in those samples. Runtime/business reconciliation remains false.
- New fixtures cover nested view SQL, snapshot isolation, source text preservation, missing/encrypted definitions, cycles, cross-database/ambiguous reference review, traversal bounds, case exceptions, cache retry, interrupted copy and Windows installation paths beyond 260 characters. A real ZIP/install smoke first exposed the long-path copy issue; the corrected installer uses extended paths and passed the new fixture. Native host loading remains separate.
- No new .49 VM baseline was imported. Live GitHub publication/download, native Codex/Claude loading and broad business correctness remain separate unperformed checks. Old verification sections below are historical, including earlier no-schema/scaffold statements that no longer describe the new examples.

## Unreleased GitHub update feature — 7 November 2026

159 Python regression tests passed, including nine new release tests; eight formatter checks passed. Package skill/manifests/local-link validation passed in source-only mode. New tests verify offline fallback, stable release/digest requirements, semantic version comparison, pinned lookup, full download integrity, old-version preservation, tampering, unlisted files, path traversal and case collisions. Network calls were mocked; GitHub CLI is not installed in the development session and no private-repository download or host activation was exercised.

The VM toolkit separately passed 17 Windows PowerShell 5.1 checks including long paths; this is fixture verification, not a real .49 VM collection. Existing 0.1.1 ZIPs remain unchanged. Configure the owner's repository and test the real release flow before publishing the next package.

After the owner supplied Mahmoud-Elgendi/fo-data-atlas-2, the origin/default bootstrap repository was configured and the complete 161-test Python suite passed, including eleven release tests. Source-only package validation also passed. The GitHub connector returned 404 for that repository; live access and release testing remain pending, and no upload was performed.

## Setup update 0.1.1

- User reported installing 0.1.0; activation of 0.1.1 has not been independently verified in the native hosts.
- 150 Python tests pass, including 20 plugin tests. New checks cover choice retries, Y/n defaults, cancellation without writes, accepted settings, unchanged scripted JSON output and managed upgrades retaining previous files.
- Actual `Setup.cmd --interactive` was exercised with both-tools/global selections and a final N. The branded screen and preview displayed correctly, exited successfully and made no installation changes. Preview: source checkout `test-evidence/atlas-setup-preview.txt`.
- Package manifests and local links pass validation. The reference payload is unchanged from 0.1.0; no VM export, database connection or SQL execution was needed.

## Passed locally

- 146 Python repository tests, including 16 plugin tests; 8 existing formatter checks.
- Both host manifests, skill frontmatter and package-local links passed the standard-library validator.
- The full application snapshot's 392,445 exported files were read and checked against their recorded SHA256 values. Windows long-path support was exercised on real mirrored source paths.
- Offline reference build: 447,389 documents, 395,819 unique contents, 11 separately identified sources. Counts include original exported files and derived per-object SQL references; they are not a count of unique F&O business objects.
- Real packed evidence checks: all six purchase tables; the PurchaseOrderNumber -> PurchTable.PurchId entity binding; @SYS15812 resolved to Purchase order from English label resources.
- Independent isolated skill trial used real purchase XML plus a simulated target schema. It retained an unsupported scope proposal as unverified and emitted a blocked scaffold rather than guessed executable SQL. Usability findings led to schema-path clarification and bounded named metadata reads.
- Behavioral tests cover descriptive filenames, source isolation, raw evidence portability, tamper detection, snapshot preservation, safe installation preparation, schema changes, label ambiguity and deletion-filter/casing checks.

The bundled skill-creator validator could not run because its PyYAML dependency is absent. The package's standard-library validator checked the actual simple frontmatter format, JSON identities and local reference links instead; this does not establish host loading.

An earlier full regression attempt hit sandbox loopback restrictions; allowing local test sockets resolved those. One later run encountered a transient busy-request connection abort during the large build. The final complete 146-test run passed. No application/server code was changed for this plugin.

## Still requires actual environment evidence

- Codex and Claude Code host activation/loading have not been performed. Installation preparation is tested in isolated folders; global/project setup must use the user's selected scope.
- No actual Fabric schema export or confirmed example field lists have been supplied. The three example SQL/check files are clearly blocked starting templates, with evidence-linked mappings.
- No dataset or validation SQL was executed. Runtime/business validation and reconciliation remain false.
- Whole-library XML interpretation, effective extension merging, tenant customization completeness and F&O build equivalence across snapshots are not established. Search and summaries have explicit bounds.

Read `INDEX.md` for source identities and the payload fingerprint. Use `scripts/validate_package.py` to recheck local package integrity and `scripts/atlas.py show` to verify individual packed evidence bytes.
