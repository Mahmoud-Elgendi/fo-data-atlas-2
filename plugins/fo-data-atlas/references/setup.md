# Setup and refresh

Use Python 3.10+ with its standard library. A portable distribution includes `references/atlas.sqlite`, `manifest.json`, `INDEX.md`, the skills and scripts. The source checkout also contains `tools/build_atlas_plugin.py` for rebuilding from local exports.

## Install

From your intended Fabric project, run `python <package>/scripts/install.py`, or specify `--project <project>`. It asks for Codex, Claude Code or both, then global or current-project scope. Supply `--host` / `--scope` for repeatable unattended setup after the user has chosen. Existing host files are merged without removing other plugins. The installer prepares local private marketplaces and reports the host steps still needed. Installation inside the source package is rejected to prevent recursive copies.

Codex requires refreshing/restarting the app and selecting the plugin in its local Plugins Directory. Claude Code can register the local marketplace and install with its CLI; the installer prints the exact commands for the chosen scope. Host loading must be verified in the actual application. A package/schema test is not a host smoke test.

### Interactive setup

`Setup.cmd` shows the F&O Data Atlas banner, creator Mahmoud Elgendi and a brief explanation. Numbered menus select Codex / Claude Code / both, then project-only / global scope. Invalid choices retry; Enter selects the labelled default. A project installation asks for its folder. A settings preview ends with `Continue with this setup? [Y/n]`; Enter accepts Yes, N cancels, and Q cancels at any prompt before installation. Progress and readable next steps follow. Double-click runs keep the window open for reading.

For unattended setup, pass `--host`, `--scope` and `--project` where applicable. Fully specified runs retain JSON output and no prompts. Add `--interactive` to show the preview/confirmation even when choices are supplied.

### Update an earlier installation

Version 0.1.1 keeps the same offline corpus. The interactive confirmation permits updating an earlier Atlas-managed Codex marketplace path to the new version; its old package directory is kept. Custom marketplace paths and newer-version registrations are not replaced. Unattended updates require `--upgrade` explicitly. Native host activation/refresh remains a separate step.

For Claude Code, the wizard prints its local marketplace commands. If the same private marketplace name is already registered at the old distribution path, remove that old registration before adding the new path. Setup does not execute those native host commands itself.

## Per project

1. Run `templates/export-fabric-schema.sql` manually in the intended Fabric Warehouse. Save the metadata result with its column headings as CSV.
2. Run `python scripts/atlas.py init-project --project <project> --schema <csv>`. It creates `.fo-data-atlas/project.json` and copies the validated CSV locally. Existing project config is not overwritten.
3. Inspect `atlas.py sources` and select matching `metadata_sources` in project.json. Record environment-specific reporting requirements there. Keep source snapshots separate and make cross-snapshot assumptions explicit.
   `schema_file` is resolved relative to the `.fo-data-atlas` configuration directory, not the project root.
4. Request a dataset, confirm its grain/fields, then review the three descriptively named output files. Run dataset/check SQL yourself in Fabric.

`atlas.py context --project <project>` verifies the schema fingerprint and selected source IDs before query work. If the schema CSV changes, review the change and explicitly update `schema_sha256`; it is never silently trusted as the previous schema.

## Rebuild references

In the source checkout, run `python tools/build_atlas_plugin.py --config <local-source-config.json> --output <new-pack>/references`. A config has `sources` entries with `type` (`snapshot`, `folder`, `catalog` or `files`), stable `id`, and local `path`. `snapshot` expects the existing manifest.csv/raw layout; `catalog` reads the existing Atlas SQL SQLite schema; `folder` preserves exported reference files; `files` takes an additional list of selected relative paths in `files`. The default configuration discovers the known local export roots.

The same builder is bundled as `scripts/build_references.py`; recipients can use it with an explicit local config and a new output directory without the original source checkout.

The builder checks original hashes for snapshot files, stores lossless compressed evidence, creates searchable references and writes ready-to-read Markdown for the six example tables. Every other document can be rendered as Markdown using `atlas.py show <id> --output <name>.md`. Restarting an interrupted build resumes its staging database with immutable source identities; changed inputs require a new output directory. Previously published reference databases are never overwritten.

Keep the old pack while using the new snapshot. The tool does not connect to the VM or Fabric and does not modify imported source exports. Local source config paths are maintenance inputs; they are not the project schema and are not required on the recipient's machine.

To use a newly built reference snapshot without reinstalling the skills, set project.json `reference_pack` to its pack root (the directory containing `references/atlas.sqlite`), select matching `metadata_sources`, and run `atlas.py context`. Relative reference-pack paths resolve from `.fo-data-atlas`; null uses the installed package. The skills use the validated effective pack path for evidence commands.

Official host documentation checked 4 November 2026:

- [Codex plugin packaging and local marketplaces](https://developers.openai.com/plugins/build/plugins)
- [Claude Code manifest](https://code.claude.com/docs/en/plugins-reference)
- [Claude Code installation scopes](https://code.claude.com/docs/en/discover-plugins)
