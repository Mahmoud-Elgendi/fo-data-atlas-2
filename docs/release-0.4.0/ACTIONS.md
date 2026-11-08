# 0.4.0 actions

## Owner terminal evidence

Owner published v0.3.0 (isDraft=false) from commit 974b219, downloaded/verified the 438,919-byte tools ZIP, then ran its installer with both tools/global/Core. SETUP PREPARED was reported at C:\Users\MahmoudElgendi\.fo-data-atlas\distribution-0.3.0\plugins\fo-data-atlas. This proves setup completed using available metadata; its output does not distinguish a new metadata download from cache reuse. Native loading was not confirmed.

## Implementation

Added an optional buildless npx entrance delegating to github_release.py and first-use prompts to installer output. Documented prerequisites, activation and project configuration separately. Version 0.4.0 retains the 0.3.0 metadata catalog. No remote publication or tagged source checkout modification performed.

## Verification

- Full suite: 188 tests PASS in 21.069 seconds; log: test-evidence/release-0.4.0/full-tests-final.log. Initial sandbox attempt hit temp/localhost restrictions. Outside-sandbox retry hit one transient Windows metadata directory rename lock; final complete rerun passed without changing the cache engine.
- Focused Atlas: 58 PASS; atlas-tests.log. This includes 6 Node launcher contracts and setup prompt checks. Formatter: 8 PASS. Package source-only validation passed.
- npm pack --ignore-scripts produced a 6,851-byte archive with six files: README, manifest, launcher, release helper, plugin identity and release origin. No database, npm dependencies or lifecycle scripts.
- Offline npx execution from that actual tarball printed launcher help and exited 0, testing npm bin wiring without remote acquisition or host writes. This is not a private Git authentication/transfer test.
- Tools ZIP: 443,441 bytes, SHA256 38522a4256d608165611861cf2ba1ed8448dc6ba9ef0886ab5ec5687a8d0c05c. Location: test-evidence/release-0.4.0/ready-tools/fo-data-atlas-0.4.0.zip.
- Metadata catalog SHA256 89506197a871f0bba4cec67b9a2ea2992716251c294fc01d1a9e1c256777ca66 matches the 0.3.0 catalog byte-for-byte. No Core/Full rebuild or extra upload required.

Final source: test-evidence/release-0.4.0/ready-source. Source ZIP: test-evidence/release-0.4.0/fo-data-atlas-0.4.0-source.zip. Source testing and delivery manifest are kept alongside it. Remote publication/private npx transfer and native host loading remain pending.
