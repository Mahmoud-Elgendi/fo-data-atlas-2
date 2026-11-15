---
name: fo-atlas-setup
description: Set up the private F&O Data Atlas plugin, choose global or project scope, and prepare a Fabric schema export or offline reference refresh.
---

For project/database work, first follow [session startup](../../references/session-start.md): offer a database connection, ask for the endpoint and database one at a time, verify it, then offer the bundled [grill-me-with-docs](../grill-me-with-docs/SKILL.md) discussion. Reuse the current conversation's choices. Installation, update and cache-repair requests stay on the installation path below; defer the database/discussion flow until the user starts project work.

Read [setup instructions](../../references/setup.md). Ask which host (Codex, Claude Code or both) and whether the user wants global or current-project installation; ask one short question at a time and reuse answers already provided. Run `scripts/install.py` only for the chosen scope. Preserve existing host configuration and project evidence.

When setup, sign-in or host activation is blocked or the user wants step-by-step help, use [the Atlas wizard](../fo-atlas-wizard/SKILL.md). It follows these setup instructions without restarting them or assuming access to a different device. Use [workflow routing](../../references/analyst-workflow.md) for other supporting skills.

For version 0.3 follow [metadata profiles](../../references/metadata-profiles.md): Core is the smaller default; Full offline includes every original. Let the wizard show sizes and choose the profile. Shared verified cache entries are reused across projects/tool versions. An existing selection for the same baseline should be retained unless the owner chooses to change it. Explicit local matching metadata can seed the cache without another download.

For project setup, use [the schema export SQL](../../templates/export-fabric-schema.sql). When connected for this task, run the read-only export through the verified target and save its result as the project CSV; otherwise supply it for the user to run in Fabric. Initialize `.fo-data-atlas/project.json` with `scripts/atlas.py init-project --project <project> --schema <csv>` after the result is available. Select the matching source IDs from `atlas.py sources`; leave source selection unresolved until known. Keep project schemas and customizations tied to their environment.

For reference refresh, use existing local export folders and the source-side builder described in setup. Choose a new snapshot output; retain the previous pack. No VM access, database connection, raw-source edits or live capture is required. Verify the refreshed reference identities before using it.

Finish by reporting which setup steps actually completed, whether the host loaded the skills, and any missing schema/source selection. A generated manifest or suggested install command alone is not a successful host installation.

For GitHub installation or package updates, follow [GitHub updates](../../references/github-updates.md). Use `scripts/github_release.py check` to discover updates and `install` for the verified download/setup after the user chooses to update. Reuse the repository origin, asking for its URL only if absent. Keep project settings intact and compare selected source IDs with the new pack before generating source-dependent SQL. An unavailable update check leaves local evidence usable.
