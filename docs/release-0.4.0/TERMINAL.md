# Owner terminal workflow

Publication-dependent example; v0.4.0 is initially a local candidate. Copy the prepared source into the plugin-only checkout, inspect changes, commit/push a codex/release-0.4.0 branch, tag and publish tools. The assistant provides each concrete command separately after checks. Metadata stays in v0.3.0 and is not uploaded again.

On another PC, install prerequisites, then `gh auth login` and `gh auth setup-git` once. From the intended Fabric project:

```powershell
npx --yes --package="git+https://github.com/Mahmoud-Elgendi/fo-data-atlas-2.git#v0.4.0" fo-data-atlas
```

Select tool, scope and metadata; confirm download/setup. Activate in your host and paste its START HERE prompt. Append `check` for status or `update` for the reviewed upgrade wizard. Python-only source fallback: `python plugins/fo-data-atlas/scripts/github_release.py install`.
