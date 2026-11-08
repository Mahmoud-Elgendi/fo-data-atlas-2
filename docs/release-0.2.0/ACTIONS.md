# Action log â€” F&O Data Atlas release

Date convention: Asia/Riyadh client date. Log what ran, its result and artifact; planned commands remain in TERMINAL.md until actually executed. Append entries as work proceeds, including failures and fixes. Keep package version and source-baseline claims separate.

## 2026-11-08 â€” planning and audit

- Owner: resume the plugin with current exports, deliver within hours, prefer IDE terminal authentication, and document code/actions. DWH remains on hold.
- Read grilling/domain-modeling skill instructions and existing package/readme/update workflow. Applied one-short-question interview preference; sent the release-scope question asynchronously.
- Read-only fresh-context audit delegated per grilling skill. Inspected package/manifests, examples, current dataset bundles, tests, helper and packaging script. No code or source export edits by that audit.
- Findings: reference database exists at 1,742,393,344 bytes; old full ZIP fits the existing <2 GiB downloader. Both host manifests remain 0.1.1. Old ZIP/manifest predate GitHub updater content. Corpus rebuild is not required for this release.
- Findings: reusable casing rules/linter and generic status example conflict with the approved target casing; example promotion, stale verification statements and version-sensitive tests need work. Source/business validation remains limited.
- Checked local command availability: Git and WinGet found; GitHub CLI not found in this session. No login, clone, push, source upload or release creation executed.
- Consulted official GitHub CLI documentation for login, repo access inspection and draft/upload workflow. Documented the terminal commands with links; the commands are for the owner's terminal and are not recorded as run.
- Created PLAN.md, TASKS.md, TERMINAL.md and this log. Updated glossary with package/source-baseline terms. These are planning/documentation changes; implementation starts after scope understanding is settled.
- Verification executed: Python standard-library check over docs/plugin-release-2026-11-08/*.md confirmed local Markdown targets exist and code fences are paired. Result: PASS. No product behavioral changes or new product test-pass claims in this planning step; the 161/8/17 counts in the plan are historical 7 November evidence.

## Pending owner input

- Scope is now accepted: ship first and iterate; preserve all metadata and add view SQL/dependency inspection. Invoice example completion remains next.
- IDE terminal repository-access readback after the documented authentication commands.

## Implementation log template

For each subsequent change record: task ID/description, files changed, exact test/build command, observed result, release artifact/hash where relevant, and remaining limitations. Mark checklist items complete only with matching evidence. Native host activation, GitHub publication and business reconciliation each require separate entries.

## 2026-11-08 — implementation

- User approved first-release scope and required complete current metadata plus view SQL, underlying views/tables and an offer to retrieve each underlying definition. No corpus narrowing or new-source relabelling.
- Added scripts/sql_lineage.py and references/sql-lineage.md. Uses hash-checked SQL_OBJECT payloads and same-snapshot target_key edges; exports original definitions, dependency outline/JSON and gaps. Tables' internal self-references are retained without falsely becoming view cycles. Missing/encrypted modules, ambiguous/qualified references, real module cycles and bounds are explicit.
- Factual audit found two distinct packed SQL catalogs and real nested CustCustomerV3Entity examples. No snapshot mixing; source dependency edges do not imply joins or Fabric deployability.
- Updated lint_sql.py for exact schema-checked GlobalOptionsetMetadata names and explicit project exceptions. Added dimension/currency guidance. Source SQL definitions are not reformatted.
- Added target-specific PO/receipt package copies, checks, evidence and sample schema. Removed the owner PO filter from packaged PO SQL/checks only; project dataset originals remain unchanged. Kept invoice starter and receipt amount coverage limitations explicit.
- New version 0.2.0 in both host manifests; fixture expectations now read package version. GitHub cached retries reverify the same release instead of blocking setup; interrupted installer copy stages/promotes only a checked payload.
- Focused command: bundled Python -m unittest discover -s tests -p test_atlas_*.py -v. Result: 43 tests PASS; saved at test-evidence/release-0.2.0-focused-tests.log. Includes snapshot isolation, cycles/gaps, tampering, casing, cache reuse and copy interruption.
- Real view command: scripts/sql_lineage.py 10b79974ade8da2f18d3ec0910b4c354 --output test-evidence/release-0.2.0-view-example --include-dependencies. 50 objects and 14 source definitions retrieved from the application catalog; initial table-self-reference warnings led to the focused fix/test. Final real-anchor verification is part of the release check below.
- Added tools/prepare_atlas_release.py to stage selected plugin source/tools/tests/docs only. Generated metadata database and ZIP files are excluded from source publication; the complete corpus remains in the offline release asset.

## 2026-11-08 — release verification

- Full regression: bundled Python -m unittest discover -s tests -v, with local fixture/temp/localhost permissions. 173 tests PASS in 22.177 seconds; test-evidence/release-0.2.0-full-tests.log. No operational F&O connection or upload.
- Full packed-evidence check: bundled Python tools/verify_atlas_plugin.py --output test-evidence/release-0.2.0-verification.json. PASS: payload hash, manifests/skills/links, six table anchors, entity alias, label and real nested-view graph. Recipient-schema/host/runtime/business flags remain false.
- Formatter: bundled Node tests/test_sql_format.cjs, eight tests PASS.
- PO/receipt example lint against the sample CSV: no schema/Company/IsDelete issue; only ExchRate CTE review remains and is manually documented in each validation JSON. Packaged PO filters removed; original dataset files unchanged.
- Real source-engine view bundle exported under examples/view-sql-custcustomerv3entity: 50 objects, 14 definitions, complete exported graph within bounds, deployment_ready false.
- Final terminal workflow names actual source/package/checksum/bootstrap paths and stages explicit source directories only. Login/push/upload commands remain unexecuted by the assistant.

## 2026-11-08 — long-path clean-install correction

- First full ZIP produced 70 files, 1,742,827,813 bytes, SHA256 ec9f12bc99a9b0f1d3f068148015df0d463691c1fce9fd5c998a343b10fb649b. Clean ZIP extraction passed, but full installation exposed Windows copy paths beyond 260 characters in temporary staging. Registration was not updated on that failure.
- Fixed install.py to use extended Windows paths for source copy, staging, promotion and JSON access. Added a long-project-path regression fixture. Fixture cleanup also handles readonly copied directories with extended paths.
- Reran focused Atlas suites: 44 PASS. Reran complete project suite: 174 PASS in 30.548 seconds. Logs retain these final results. Initial candidate ZIP/checksum were moved intact to dist/candidates/initial-0.2.0 before rebuilding; no old released version was overwritten.

## 2026-11-08 — final local artifact and recipient smoke

- Rebuilt complete offline package: plugins/fo-data-atlas/dist/fo-data-atlas-0.2.0.zip; 70 files; 1,742,828,069 bytes; SHA256 f4bd6861aef846ef26fdd0315232f535622eece8dd6494d717de7ae962a0c523. Checksum sidecar is fo-data-atlas-0.2.0.sha256. Original corpus hash remains unchanged.
- Verified the actual ZIP through github_release.extract_verified, then install.prepare into an isolated recipient-project-v2 folder for both host registrations. No global host configuration changed. Windows long-path copy succeeded.
- Executed installed atlas.py (not the source helper) to search CustCustomerV3Entity from the selected application SQL snapshot, then installed sql_lineage.py to export its root definition and lineage. PASS; full source closure complete within bounds. Original export folders are not required.
- Installed github_release.py check returned unavailable/continue_offline true because GitHub CLI is not installed in this session. Offline SQL search/export still passed. Evidence: test-evidence/release-0.2.0/recipient-smoke.json.
- Native host loading and live GitHub authenticated upload/download remain unperformed. The owner has the exact terminal commands; no chat connector access or operational database was used.
- Clean source staging and a separate small source ZIP are prepared by tools/prepare_atlas_release.py after this log update; its actual size/hash is recorded in the delivery manifest. Large DB/ZIP files are excluded from that source tree.

## 2026-11-08 — source handover

- Prepared the clean plugin-only source folder: 82 files, 3,128,975 bytes before final log synchronization; excludes the large offline database/ZIPs and unrelated metadata-app code.
- Ran the copied source checkout's own command: bundled Python -m unittest discover -s tests -v from test-evidence/release-0.2.0/source. All 44 plugin tests PASS in 1.775 seconds; source-tests.log retained outside the staged tree. Source-only manifest/skill/link validation also PASS.
- Final source ZIP is built from the reviewed source tree, excluding generated test-evidence and __pycache__. Earlier source candidate is preserved under dist/candidates/initial-source.
- Delivery manifest records exact final package/source asset paths, sizes and hashes. User terminal publication and native host loading remain pending; no remote upload or Git remote change was performed in this workspace.
