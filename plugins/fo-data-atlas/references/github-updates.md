# GitHub install and offline updates — 0.5.2

The optional Git-backed npx entrance is described in [first use](first-use.md). It delegates to this same installer/cache. It is separate from skills-add installation, which does not prepare Atlas package-level helpers and metadata.

Repository: https://github.com/Mahmoud-Elgendi/fo-data-atlas-2. The 0.2.0 release remains immutable; version 0.3 separates small tools from Core/Full metadata and fixes long Windows download extraction paths.

## Install

Use Python 3.10+ and GitHub CLI authenticated for private-repository read access. Run `python scripts/github_release.py install` from the small source/bootstrap package. It verifies/downloads the tools ZIP and starts the branded AI-tool/global-project/profile wizard. Select Core (default) or Full offline, review size/settings and confirm [Y/n]. Metadata is separately verified and cached once per machine. Follow native host activation steps afterward.

The query skill checks once per conversation when invoked, offers a newer tools release, and continues locally if unavailable or declined. This is an agent instruction, not a native IDE startup hook. All installed metadata queries stay offline. Tool updates with unchanged metadata IDs/hashes reuse the cache; they do not download the baseline again.

Commands: `check` only reads release metadata; `download` verifies/cache-downloads tools; `install` also starts setup. `--tag v0.5.2` pins a stable tools version. `--destination PATH` selects its download cache. Existing same-version downloads are reverified before reuse. Tool copies are staged/promoted atomically. Profile cache behavior and missing-evidence rules are in [metadata profiles](metadata-profiles.md).

## Versions and preservation

The tools version and F&O metadata baseline are separate. metadata-catalog.json pins each Core/Full asset to its release tag and size/hash. Existing cache entries, project schemas/rules/queries and selected source IDs remain in place. Never silently switch a project's application baseline. An explicit project reference_pack override continues to take precedence.

## Owner release contract

Publish stable vMAJOR.MINOR.PATCH tags and a small `fo-data-atlas-MAJOR.MINOR.PATCH.zip` tools asset, its checksum and the bootstrap helper. For a new metadata baseline also attach the exact Core/Full ZIPs named in metadata-catalog.json. Subsequent tools-only releases reuse the same metadata catalog/release assets. Keep the repository private as agreed.

Metadata assets contain only references/atlas.sqlite and references/manifest.json. Verify ZIP size/SHA256 and database hash before cache promotion. Tools ZIPs contain a metadata catalog and package-manifest.json covering their files; original 0.2 complete archives remain readable by the helper for compatibility. A release must not be reported published while it is a draft or local artifact.

GitHub CLI is required only for online acquisition. A matching local metadata pack can seed cache with --local-pack. Native host loading, real private transfer and business/runtime correctness are separately recorded checks. See [GitHub login](https://cli.github.com/manual/gh_auth_login) and [release assets](https://docs.github.com/en/rest/releases/assets).
