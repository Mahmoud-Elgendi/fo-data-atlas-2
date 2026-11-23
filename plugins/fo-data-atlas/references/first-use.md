# First installation and first use

## Single command (0.5.1)

This command installs directly from our private GitHub repository, without npm registry publication. Clean-PC transfer and native activation still need recorded acceptance testing. It uses npm's [Git package support](https://docs.npmjs.com/cli/v11/commands/npm-install/) and [executable support](https://docs.npmjs.com/cli/v11/commands/npm-exec/).

On another Windows PC, install your AI tool, Node.js 22+, Git, Python 3.10+ and GitHub CLI. Your GitHub account needs read access to the private repository. Once per PC, run `gh auth login`, then `gh auth setup-git`. Reopen the terminal after installing prerequisites. Git-backed npx acquisition uses Git authentication; release downloads use GitHub CLI authentication. Keep credentials out of command lines and project files.

Open PowerShell in the intended Fabric project:

```powershell
npx --yes --package="git+https://github.com/Mahmoud-Elgendi/fo-data-atlas-2.git#v0.5.1" fo-data-atlas
```

`--yes` accepts npm's temporary launcher download. Atlas still requests download consent and the wizard's final `[Y/n]` confirmation. The launcher has no dependencies, build step or lifecycle hooks. It finds Python 3.10+ and runs the existing helper with the caller's terminal/project directory. Set `FO_ATLAS_PYTHON` to an interpreter executable if discovery fails.

The wizard shows Mahmoud Elgendi's banner, AI tool choice, project/global choice, Core/Full choice and size, then review/confirmation. Core downloads about 304 MiB once; Full about 1.21 GiB. Compatible updates reuse the verified shared cache. Installed helpers continue using Python standard library; Node.js is the optional installer entrance.

The Git tag pins the launcher. The release helper selects latest published stable tools; append `--tag v0.5.1` after `fo-data-atlas` to pin tools too. Metadata remains pinned to its original 0.3.0 assets/hashes. Append `check` for release status or `update` for the reviewed upgrade wizard. npm can cache unchanged Git references; future launcher changes require a new release tag.

Local source handover: `node plugins/fo-data-atlas/scripts/atlas-cli.cjs --help`. Extracted tools: use `Setup.cmd` or `python scripts/install.py --interactive`, with no Node.js/Git requirement. Offline installation needs matching cached or local metadata as described in [setup](setup.md).

## Activate and start

After activation, [the analyst workflow](analyst-workflow.md) lists the available research, diagnosis, SQL review, glossary, handoff, guided setup, Wayfinder and skill discovery skills. For example, ask `$fo-atlas-diagnose` to investigate doubled PO totals, `$fo-atlas-review` to check a saved query, or `$fo-atlas-handoff` to save a task for another device. In Claude Code use `/fo-data-atlas:<skill-name>`. These capabilities require version 0.5.0 or later and host activation; installing an earlier release does not add them.

When you start project work, Atlas asks whether to connect to a database or use offline metadata. If you choose a connection, it asks for the SQL endpoint and database separately, then checks access using an available connector or an existing sqlcmd (Go). Complete Microsoft sign-in if prompted. It next asks whether you want to discuss requirements before work begins. Accepting uses the bundled `grill-me-with-docs` skill, with one short question at a time and written decisions. Choices are reused within the conversation. See [session startup](session-start.md) for connection scope, missing-client handling and validation limits.

Setup prepares files/marketplace entries and prints host activation instructions. Follow them, open your intended project and start a new chat. File preparation alone does not prove the host loaded the skills. Resolve missing skills before asking for Atlas SQL.

In Codex, paste:

```text
$fo-atlas-setup
Set up this Fabric project. Guide me one step at a time.
```

In Claude Code, use `/fo-data-atlas:fo-atlas-setup` with the same request. Project setup guides the user to run the Fabric schema export, save CSV and select matching evidence sources. Each project retains its schema and reporting rules.

An exported view can be inspected immediately without a Fabric CSV:

```text
$fo-atlas-query
Show the SQL behind CustCustomerV3Entity and list its underlying views and tables.
```

Atlas retrieves original SQL, lists dependencies and offers underlying view SQL. Missing Core originals require Full; coverage limits remain explicit. In Claude Code use `/fo-data-atlas:fo-atlas-query`.

After project setup:

```text
$fo-atlas-query
Create purchase-order-lines. Suggest the fields first.
```

Atlas confirms fields, checks available evidence/schema and writes named SQL, mapping and checks files. Live read-only validation is available when requested and a connection is verified; database changes require their own task authorization. Metadata reads work offline; AI inference still needs the selected host's connection. The once-per-chat release check may use network but its failure does not block local evidence.
