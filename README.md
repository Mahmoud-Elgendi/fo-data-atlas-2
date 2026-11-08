# F&O Data Atlas

Private offline D365 F&O metadata and SQL assistant by Mahmoud Elgendi.

This repository contains the small plugin source, tests and release documentation.
The full offline database is distributed as a versioned GitHub Release asset.

## Install

Use Python 3.10+ and authenticated GitHub CLI with read access to this repository:

```powershell
python plugins/fo-data-atlas/scripts/github_release.py install
```

It downloads/verifies the tools and selected Core/Full metadata, then opens the
AI-tool/global-or-project setup wizard. Follow native host activation instructions.
Installed evidence works offline; uncached originals require the Full profile.
Use the same command to update; existing project settings and previous versions stay.

See [plugin guide](plugins/fo-data-atlas/README.md),
[release notes](release-notes.md), [release plan](docs/release-0.3.0/PLAN.md)
and [terminal workflow](docs/release-0.3.0/TERMINAL.md).

## Test source

```powershell
python -m unittest discover -s tests -v
python plugins/fo-data-atlas/scripts/validate_package.py --source-only
```

The source checkout alone intentionally lacks references/atlas.sqlite; obtain the
complete release package before attempting metadata queries or offline setup.
Metadata baselines and plugin versions are separate. No new .49 collection is claimed.
