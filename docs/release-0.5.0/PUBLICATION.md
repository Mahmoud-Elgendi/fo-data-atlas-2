# Publication verified — 15 November 2026

[F&O Data Atlas v0.5.0](https://github.com/Mahmoud-Elgendi/fo-data-atlas-2/releases/tag/v0.5.0) is published as latest stable, not a draft or prerelease. Release source commit: `0ddec786a0d4acf73a5c08f635e010dbc03c625d`. All approved code is on main, the sole remote branch. The earlier implementation notes are prepublication records, superseded by this delivery state.

## Observed checks

- 67 source tests passed; source-only validator found eleven valid skills and valid local links.
- The actual tools ZIP was checksum/extraction-verified, installed to a separate local project using cached Core without network, and used to search installed offline metadata. No metadata database was copied into the project tools. No global installation was changed.
- Installer banner and launcher help include Developed by Mahmoud Elgendi, the one-line description, Mobile/WhatsApp 00966542128150 and www.mahmoudelgendi.com. The boxed banner's line widths were checked.
- GitHub's ZIP digest/size match the local candidate: 475487 bytes; SHA256 `86bdc6890d8a860887a76f2684aeb858804bdfaa6b7865efbe74fc74dc299f6d`. The checksum sidecar and bootstrap helper are attached. Unchanged metadata remains on its original v0.3.0 assets; no metadata payload was republished.
- Downloading the published private package with github_release.py succeeded and verified the archive.
- Acquiring the tagged private launcher through npx and running `fo-data-atlas check --tag v0.5.0` succeeded, reporting version 0.5.0/current and the same ZIP digest.

## Limits

These checks ran on the development device with working private GitHub access. They do not remove the other device's EALLOWGIT restriction or missing prerequisites. README documents the manual local-pack route. The npx check is not a fresh recipient's interactive installation or native Codex/Claude activation. Prompt routing, real SQL sign-in and F&O business reconciliation remain unverified for recipients. The new sqlcmd probe was boundary-tested with mocks; no live database connection was made during release work.

This publication record is a documentation-only follow-up on main; the release tag and tools bytes stay immutable. Install/update commands are maintained in the root README and TERMINAL.md.
