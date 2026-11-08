---
name: fo-atlas-setup
description: Set up the private F&O Data Atlas plugin, choose global or project scope, and prepare a Fabric schema export or offline reference refresh.
---

Read [setup instructions](../../references/setup.md). Ask which host (Codex, Claude Code or both) and whether the user wants global or current-project installation; ask one short question at a time and reuse answers already provided. Run `scripts/install.py` only for the chosen scope. Preserve existing host configuration and project evidence.

For project setup, supply [the schema export SQL](../../templates/export-fabric-schema.sql) for the user to run in Fabric and save as CSV. Initialize `.fo-data-atlas/project.json` with `scripts/atlas.py init-project --project <project> --schema <csv>` after the result is available. Select the matching source IDs from `atlas.py sources`; leave source selection unresolved until known. Keep project schemas and customizations tied to their environment.

For reference refresh, use existing local export folders and the source-side builder described in setup. Choose a new snapshot output; retain the previous pack. No VM access, database connection, raw-source edits or live capture is required. Verify the refreshed reference identities before using it.

Finish by reporting which setup steps actually completed, whether the host loaded the skills, and any missing schema/source selection. A generated manifest or suggested install command alone is not a successful host installation.

For GitHub installation or package updates, follow [GitHub updates](../../references/github-updates.md). Use `scripts/github_release.py check` to discover updates and `install` for the verified download/setup after the user chooses to update. Reuse the repository origin, asking for its URL only if absent. Keep project settings intact and compare selected source IDs with the new pack before generating source-dependent SQL. An unavailable update check leaves local evidence usable.
