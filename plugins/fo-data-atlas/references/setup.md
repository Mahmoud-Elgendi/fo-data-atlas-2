# Setup — 0.5.2

For a new PC, see [first use](first-use.md) for the optional single-command route and ready-to-paste prompts. Confirm the 0.5.2 release is published before remote installation; clean-PC/native-host acceptance is still separate. Python-only setup remains supported.

## First installation

Use Python 3.10+ and GitHub CLI authenticated with read access to the private repository. Run the latest scripts/github_release.py install from the source/bootstrap package. It verifies the small tools ZIP and starts Setup.cmd/scripts/install.py. Version 0.2 bootstrap scripts expect a monolithic archive; use the new bootstrap for the one-time 0.3 migration.

The branded wizard by Mahmoud Elgendi asks for Codex, Claude Code or both, global/current-project scope, the project folder where needed, and Core (default) or Full offline metadata. It shows the profile size and confirms [Y/n]. Invalid choices retry; Enter accepts the labelled default; Q cancels. Cancellation before confirmation performs no metadata download. Native host activation steps follow preparation and must be checked in the host.

Core contains selected original evidence and all-object discovery; Full includes every original document. Read [metadata profiles](metadata-profiles.md) before assuming an uninstalled original was searched. Verified metadata is cached once per machine and shared by tool versions/projects. Compatible tools-only updates reuse it. [GitHub workflow](github-updates.md) describes release checking and downloads.

## Offline/local installation

An extracted tools ZIP can use a matching local metadata pack with scripts/install.py --local-pack PACK_ROOT --metadata-profile core (or full). The local pack root contains references/atlas.sqlite; its exact expected hash is checked. This can reuse the owner's built Core or an older complete 0.2 pack for Full, with no metadata network download. A previously cached profile also works offline. The small tools ZIP alone does not contain the evidence database.

The Windows Setup.cmd prefers the existing local Codex Python runtime, then the Python launcher, then Python from PATH. Existing Python 3.10+ and GitHub CLI are online prerequisites; no third-party Python packages are required. Global/project host settings are merged; unrelated entries and previous versions are retained. Managed upgrades require the wizard's confirmation or explicit --upgrade for unattended setup.

## Each Fabric project

1. Run templates/export-fabric-schema.sql manually in the intended Fabric SQL surface. Save its metadata result with column headings as CSV.
2. Run scripts/atlas.py init-project --project PROJECT --schema CSV. Existing project configuration is preserved.
3. Select matching metadata_sources from atlas.py sources in .fo-data-atlas/project.json. schema_file and relative reference_pack paths resolve from .fo-data-atlas. Never infer the user's application build from a source's nickname.
4. Run atlas.py context --project PROJECT to validate schema fingerprint and source selection. Schema changes require explicit review/update of schema_sha256.
5. Confirm dataset grain/fields and review the descriptively named SQL/mapping/check files. Run SQL/checks in Fabric separately. Exported view SQL inspection alone does not require a Fabric CSV.

An explicit project reference_pack overrides the installed shared-cache default and is never silently rewritten by setup. Native Codex/Claude loading and runtime/business validation are separate from package/cache checks.

## Maintenance

The existing lossless reference builder remains available as scripts/build_references.py, using explicit snapshot/folder/catalog/files source config and a fresh output. Original exports and prior snapshots are immutable. tools/build_atlas_metadata_packs.py builds Core/Full assets from a complete existing pack; tools/build_atlas_tools_release.py binds tools to their exact metadata catalog. A tools-only release should reuse the same catalog/assets.

Source metadata, source-version evidence, destination schema, runtime behavior and reconciled financial results remain separate validation levels. DWH deployment is outside this plugin setup.
