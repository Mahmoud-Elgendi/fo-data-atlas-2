# 0.3.0 action log

2026-11-08, Asia/Riyadh client date. No 0.2.0 remote asset/tag was changed.

- Owner accepted smaller Core installation with Full offline choice after the 1.62 GiB download/path error.
- Read-only profile recorded in research/plugin-packaging-2026-11-08/size-options.md: original DB 1.623 GiB; non-DB files 2.93 MiB; most bytes are original evidence/labels. Vacuum cannot materially fix the size.
- User's actual extraction failure reproduced at target.open with a tiny view-SQL archive. Added regression before applying extended paths throughout github_release.py. 175-project-test patch baseline and actual long-path ZIP extraction passed before the new profile design.
- Added tools/build_atlas_metadata_packs.py: stream original rows read-only into a new Core database, retain all source/object identities, select SQL/structural/English payloads, rebuild search, and produce Core/Full archives with SHA256. Full SQLite hash remains original. Original DB/exports never rewritten.
- Corrected the Core availability count to count actual retrievable hashes, including deduplicated content shared by other paths. Final Core: 204,438 document identities/182,328 unique payloads; all 447,389 objects discoverable. Initial pre-correction archive retained under metadata build/initial-core.
- Added metadata_cache.py for verified immutable shared acquisition, local seeding and atomic reference-pack.json activation. Missing Core originals are explicit in atlas.py; cache resolution preserves explicit project overrides.
- Updated install.py to keep metadata external, add profile/size selection and cancellation before acquisition, reuse old same-baseline profile choices and retain previous versions. Legacy complete packs remain supported.
- Added tools-only bundle validation/packaging and build_atlas_tools_release.py. Version set to 0.3.0 in both host manifests. Updated skills/profile docs and ADR 0005.
- Added six cache/profile tests. Focused Atlas suites: 51 PASS. Complete project command: bundled Python -m unittest discover -s tests -v; 181 tests PASS in 23.146 seconds, test-evidence/release-0.3.0-full-tests.log. No operational F&O access or remote publication.
- Actual Core reads verified @SYS15812 resolves Purchase order and CustCustomerV3Entity's 50-object SQL closure is complete. Metadata source IDs/proofs remain unchanged.
- Core ZIP: 318,513,889 bytes, SHA256 34f30d94df208bb14594d812c975e895d5d969e9fa2593607bf6d00a8cd527f2. Full ZIP: 1,301,733,130 bytes, SHA256 22c422612da673557d0756754f3cea1bdff1850e42c0ae10396e872c03b426bb.
- Current artifacts are local/unpublished. Live GitHub transfer and native host loading are separate pending evidence; next terminal actions will be guided one command at a time as requested.

## Final validation

- Added coverage for preserving Full as the next setup default, failed metadata transfer retaining the active Full profile, and JSON-only unattended local-seeded setup. One sandbox rename restriction was isolated by rerunning with normal local file permissions; the tests passed without a product workaround.
- Final complete suite: 184 tests PASS in 21.892 seconds, test-evidence/release-0.3.0-full-tests.log. Eight formatter tests and source-only tool manifest/skill/link checks PASS.
- Actual Core ZIP acquisition exercised via a local file provider through the same verification/extraction/cache code (no network). Two isolated project installs reuse one cache; second acquisition had no provider/network call. Neither installed project contains the evidence SQLite file.
- Executed the installed atlas.py for offline SQL search. Missing Core class payload explicitly required Full. Seeded Full from the existing original local complete pack without any network, read that original class, and restored Core. Previous cache entries remained. Smoke evidence: test-evidence/release-0.3.0-smoke/smoke.json. No global host settings changed; native activation and live 0.3 GitHub transfer remain unperformed.
- The tools-only release and source handover are built after these checks. Final asset paths/sizes/hashes are in delivery.json; no 0.2.0 remote file/tag is replaced.

- Final Windows robustness checks added standard GitHub CLI discovery for an old IDE PATH (the owner's observed install situation). An intermittent Windows staging-directory permission/lock failure led to clearing the new staging copy's readonly attribute on Windows and bounded promotion retry; a simulated-lock test verifies only complete payload promotion and preservation of existing targets. No original directory permissions are changed.
- Final complete regression after these fixes: 186 tests PASS in 21.559 seconds; focused suites: 56 PASS. Tools progress displays a meaningful MiB size instead of 0.00 GiB for the small download.

## Ready artifact

- Tools ZIP: test-evidence/release-0.3.0-ready-tools/fo-data-atlas-0.3.0.zip, 438,919 bytes, SHA256 5db3781f88c0e992ba7c75bf82ef2658b2330dc1278f34526ad40ad97201ab11. Previous local candidates were retained; no published file was overwritten.
- The exact ready ZIP was re-extracted/verified under a deep Windows path, installed into an isolated project using the existing verified Core cache with all network calls forbidden, and executed via the installed metadata_cache.py/SQL-lineage helper. Core status reports 204,438 readable identities; SQL view export PASS. Evidence: test-evidence/release-0.3.0-ready-smoke/smoke.json.
- Global host settings were not changed. Native host loading and live 0.3 publication/transfer remain pending.

## Source handover verification

- Prepared plugin-only source includes the metadata catalog, profile/cache modules, builders and all four plugin test modules; no metadata DB or ZIP is committed as source.
- Source tests were rerun from the copied source directory. Deep-path fixture cleanup needed the same Windows extended-path handling as the tested extractor; corrected that test cleanup (no product behavior change) and reran. All 56 source plugin tests PASS in 2.988 seconds; test-evidence/release-0.3.0/source-tests.log.
- The final source ZIP excludes generated test artifacts/bytecode and preserves the previous source candidate. Tools/archive/reference hashes and publication paths are in delivery.json.
- New source branch and release assets remain for the owner's terminal commands. Existing 0.2 repository/tag/assets are intact.
