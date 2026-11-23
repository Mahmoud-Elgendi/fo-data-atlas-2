# Public one-script installation — 23 November 2026

The owner requested one script after npm refused Git package sources on another device and GitHub CLI was unavailable. tools/Install-Atlas.ps1 is an independent public-release bootstrap on main. It installs/updates the latest stable release (or an explicit stable tag) without npm, Git or gh. The published tools release remains v0.5.2 and its assets/tag are unchanged.

## Behavior

Finds a working Python 3.10+ (explicit path, FO_ATLAS_PYTHON, conda, Codex runtime, Python launcher or PATH); rejects a Store alias and incompatible interpreter. No runtime or administrative installation is attempted. It reads GitHub's public release API and downloads only the expected tools ZIP/helper HTTPS URLs. Both assets require matching release SHA256 and size. The verified helper then validates/extracts every package file.

An embedded Python setup adapter handles only the original metadata-cache release-download operation using public HTTPS. It restricts repository/tag/filename and HTTPS redirect destinations. The original metadata ZIP/database hashes and cache validation remain authoritative. Other gh actions are rejected by the adapter. It exists only in the setup process and does not alter installed package files. Existing cached profiles skip metadata transfer. The normal wizard chooses host, project/global scope and Core/Full with confirmation. Old versions/configuration are preserved. A local INSTALLATION.md records the run and readiness limits without credentials.

No execution-policy changes, TLS bypass, administrator command, npm policy override, global runtime install, live SQL or background job is used. If a corporate policy blocks the script or downloads, stop and use an approved method. Public downloads may require network/proxy access and are subject to GitHub's API rate limit. Native IDE activation remains a separate observed step.

## Verification

- All 71 source tests passed in 5.661 seconds, including four new public-transport boundary tests. Foreign repositories, unsafe filenames/tags, unsupported gh operations and non-HTTPS/foreign final download URLs are rejected. Downloads do not overwrite an existing file.
- A real v0.5.2 CheckOnly run fetched public tools/helper and passed archive/manifest checks in PowerShell 7 and Windows PowerShell 5.1. Execution policy was not changed.
- A real wizard run installed both host packages in a new isolated project using the existing Core cache after confirmation. Host activation instructions and the local run note were printed. No global host configuration changed.
- Cold Core/Full transfer is covered by transport boundary tests plus the existing metadata-cache ZIP/database validation tests; no fresh 304 MiB or 1.21 GiB metadata download was performed in this verification. The public transport also receives a small real-asset smoke check.
- Native Codex/Claude loading, the other PC's exact policy/proxy/Python environment and SQL sign-in remain unverified.

## Use

Run the README's single block from the intended project folder. It downloads the PS1 to TEMP and executes it normally. Or download and inspect the PS1, then run it. Repeat for future updates. Use -Tag for a reproducible release; main is the source of the bootstrap, not the selected release version. Downloaded work and evidence are kept in LOCALAPPDATA/fo-atlas/setup by default; -DownloadDirectory can choose another short path.

This script is authored for Atlas, not an npm package publication or skills-add adaptation. The plugin source exporter includes it and its tests in future source publications. The old packaged helper's CLI requirement persists outside this standalone setup process.
