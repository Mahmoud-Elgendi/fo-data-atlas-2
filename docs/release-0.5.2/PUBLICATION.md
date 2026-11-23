# Publication verified — 23 November 2026

[F&O Data Atlas v0.5.2](https://github.com/Mahmoud-Elgendi/fo-data-atlas-2/releases/tag/v0.5.2) is published as latest stable, not a draft or prerelease. Tagged source commit: `e734c8aeaa6312208135e632751129149c33c14d`. The approved rule is on main.

Checks: 67 source tests passed in 5.732 seconds; source-only package validation passed with eleven skills. A focused fixture confirmed the existing linter accepts IsDelete IS NULL and rejects isdeleted = 0, IsDelete = 0, IsDelete = FALSE and COALESCE(IsDelete, 0) = 0. No linter implementation change was made.

The actual archive was verified/extracted and installed to an isolated local project using the existing Core cache with network disabled. The mandatory SQL rule and review skill contained the new rejection guidance. Offline metadata search succeeded. The metadata catalog is unchanged; no metadata database was copied into project tools.

GitHub readback matched three assets and the tools ZIP: 476272 bytes; SHA256 `b320006c7f2e82533b84ea820af21d2073d6fff933d334200976d8016874b037`. Downloading the published release verified successfully. The short GitHub npx launcher completed its read-only check, reporting version 0.5.2/current with the same digest.

No global installation, live database, tenant query or source export was changed. Native host adherence and recipient/F&O result validation remain unverified. Existing Python/GitHub CLI and Git-package policy requirements remain unchanged. This documentation-only follow-up does not move the immutable tag or replace its release assets.
