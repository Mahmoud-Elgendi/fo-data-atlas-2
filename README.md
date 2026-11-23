# F&O Data Atlas

Private D365 F&O metadata and Fabric SQL assistant for Codex and Claude Code.

**Developed by Mahmoud Elgendi**

Building D365 F&O, Microsoft Fabric and AI-assisted SQL solutions.

**Mobile / WhatsApp:** 00966542128150 ([WhatsApp](https://wa.me/966542128150))

**Website:** [www.mahmoudelgendi.com](https://www.mahmoudelgendi.com)

## Install

Run PowerShell in your intended Fabric project. Requirements: Node.js 22+, Git, Python 3.10+, GitHub CLI and a GitHub account with read access to this private repository.

Authenticate once per device:

```powershell
gh auth login
gh auth setup-git
```

Install the reproducible 0.5.1 release:

```powershell
npx.cmd --yes --package="git+https://github.com/Mahmoud-Elgendi/fo-data-atlas-2.git#v0.5.1" fo-data-atlas install --tag v0.5.1
```

## Update

```powershell
npx.cmd --yes --package="git+https://github.com/Mahmoud-Elgendi/fo-data-atlas-2.git#v0.5.1" fo-data-atlas update --tag v0.5.1
```

For future updates using the launcher on `main` and the latest published stable tools:

```powershell
npx.cmd --yes --package="git+https://github.com/Mahmoud-Elgendi/fo-data-atlas-2.git#main" fo-data-atlas update
```

`main` is the only maintained branch. Tags retain reproducible releases; a source push does not change already installed tools. The commands use Git-backed npm acquisition, not a public npm package or `skills add`. npm may cache Git references; use a new release tag for reproducible launcher upgrades.

Setup asks for Codex/Claude/both, current-project/global scope and Core/Full metadata. Core downloads about 304 MiB once; Full about 1.21 GiB. Compatible updates reuse the checked shared cache. Follow the printed host activation instructions, restart the host and verify skills in a new chat.

If `npx.cmd` is missing on Windows, try its known installed path, such as `& 'C:\Program Files\nodejs\npx.cmd'`, or reopen your terminal after installing Node.js. Do not assume that path exists on every device.

## Restricted devices and offline setup

Admin access is not required for Atlas files, but prerequisites may need an approved per-user installation. If npm reports `EALLOWGIT`, this command is blocked on that device. Do not disable organization policy. Use the [release ZIP](https://github.com/Mahmoud-Elgendi/fo-data-atlas-2/releases/tag/v0.5.1) and matching metadata downloaded in the browser. Metadata remains on v0.3.0 because the snapshot has not changed; this is independent of the tools version.

Extract the tools and Core metadata into short user-owned paths. For example, if tools are in `C:\Users\you\Atlas` and metadata has `C:\Users\you\AtlasMetadata\references\atlas.sqlite`:

```powershell
python 'C:\Users\you\Atlas\scripts\install.py' --interactive --metadata-profile core --local-pack 'C:\Users\you\AtlasMetadata'
```

Replace the sample paths with the actual extracted roots. This local route uses Python 3.10+ and does not need Node.js, Git or GitHub CLI. The installer verifies the metadata hash. The small tools ZIP alone is not the offline evidence database. See [setup](plugins/fo-data-atlas/references/setup.md).

## Start using Atlas

In Codex, start a new chat after activation:

```text
$fo-atlas-query
Create purchase-order-lines. Suggest the fields first.
```

Atlas offers a database connection or offline metadata. If connecting, it asks for the SQL endpoint and database separately, verifies access through an available connector or existing sqlcmd (Go), and offers a short requirements discussion. Microsoft handles sign-in; no password is requested in chat. No client is silently installed. See [connection scope](plugins/fo-data-atlas/references/session-start.md).

There are eleven [bundled skills](plugins/fo-data-atlas/references/analyst-workflow.md): setup, query, discussion, research, diagnosis, SQL review, glossary, handoff, wizard, Wayfinder and skill discovery. For example, use `$fo-atlas-review` to review saved SQL. In Claude Code use `/fo-data-atlas:fo-atlas-query` or the corresponding skill name.

## Validation and evidence limits

Package/helper tests and archive verification are recorded in [release documentation](docs/release-0.5.1/PLAN.md). Native host routing, a clean recipient device, live SQL authentication and F&O business reconciliation remain separate checks. No new .49 VM baseline or all-IDE compatibility is claimed. Source exports and metadata hashes are preserved.

```powershell
python -m unittest discover -s tests -v
python plugins/fo-data-atlas/scripts/validate_package.py --source-only
```

See the [plugin guide](plugins/fo-data-atlas/README.md), [release notes](release-notes.md), [actions](docs/release-0.5.1/ACTIONS.md) and [terminal commands](docs/release-0.5.1/TERMINAL.md).
