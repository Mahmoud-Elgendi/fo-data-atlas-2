# IDE terminal commands

Run in PowerShell. Authentication stays in the owner's terminal/browser. These instructions are documented commands, not actions already executed by the assistant.

## 1. GitHub CLI

Check availability:

```powershell
gh --version
```

If missing, install GitHub CLI through its Windows installer or WinGet, then reopen the IDE terminal:

```powershell
winget install --id GitHub.cli --exact --source winget
```

Installation source: [official GitHub CLI repository](https://github.com/cli/cli#installation).

## 2. Sign in and verify this repository

```powershell
gh auth login --hostname github.com --git-protocol https --web
gh auth status --hostname github.com
gh auth setup-git --hostname github.com
gh repo view Mahmoud-Elgendi/fo-data-atlas-2 --json nameWithOwner,isPrivate,isEmpty,viewerPermission,defaultBranchRef
```

If already signed in to the intended account, run status/repository view first and skip login when it is unnecessary. The repository result should identify Mahmoud-Elgendi/fo-data-atlas-2; check isPrivate and write/admin permission before uploading. If access is missing, fix account/repository access before proceeding. Record the success/error summary in ACTIONS.md; login output itself need not be copied into a release artifact.

The chat GitHub connector's access and GitHub CLI authentication are separate. CLI access can complete the release workflow even if the chat connector still cannot see the repository.

Official command references: [login](https://cli.github.com/manual/gh_auth_login), [repository view](https://cli.github.com/manual/gh_repo_view), [Git authentication](https://cli.github.com/manual/gh_auth_setup-git).

## 3. Publish only the prepared plugin source

Run after the local build creates the source folder and package. Execute one line at a time and stop on a failed command. Confirm the repository is private and still empty using section 2 first. If it is no longer empty, inspect its existing branch/content before initializing a new publication; do not force-push.

```powershell
$AtlasProject = 'C:\Users\MahmoudElgendi\OneDrive - 365 Xperts\_Codex\D365 FO Data Model'
$AtlasSource = Join-Path $AtlasProject 'test-evidence\release-0.2.0\source'
$AtlasPackage = Join-Path $AtlasProject 'plugins\fo-data-atlas\dist\fo-data-atlas-0.2.0.zip'
$AtlasChecksum = Join-Path $AtlasProject 'plugins\fo-data-atlas\dist\fo-data-atlas-0.2.0.sha256'
$AtlasBootstrap = Join-Path $AtlasSource 'plugins\fo-data-atlas\scripts\github_release.py'
Set-Location -LiteralPath $AtlasSource
Start-Transcript -Path (Join-Path $AtlasProject ('test-evidence\release-0.2.0\publish-' + (Get-Date -Format yyyyMMdd-HHmmss) + '.log'))
git init -b codex/release-0.2.0
git remote add origin https://github.com/Mahmoud-Elgendi/fo-data-atlas-2.git
git add -- .gitignore README.md release-notes.md plugins tools tests docs
git diff --cached --stat
git diff --cached --name-only
```

Review that this is the clean plugin-only source: no raw export directories, business data, SQLite payload or ZIP file is staged. The generated offline database is distributed through the release asset. If Git asks for a commit name/email, configure your intended identity locally in this checkout, then continue.

```powershell
git commit -m 'Release F&O Data Atlas 0.2.0'
git push -u origin codex/release-0.2.0
git tag v0.2.0
git push origin v0.2.0
```

These commands initialize the separately prepared source folder, not the metadata-explorer workspace. For a previously completed source push, inspect git status and the remote tag instead of reinitializing or recreating the same tag.

## 4. Upload, review and publish the release

From the same PowerShell session and source folder:

```powershell
gh release create v0.2.0 $AtlasPackage $AtlasChecksum $AtlasBootstrap --repo Mahmoud-Elgendi/fo-data-atlas-2 --verify-tag --draft --title 'F&O Data Atlas 0.2.0' --notes-file release-notes.md
gh release view v0.2.0 --repo Mahmoud-Elgendi/fo-data-atlas-2 --web
```

Review the draft's three files and notes. Then publish:

```powershell
gh release edit v0.2.0 --draft=false --latest --repo Mahmoud-Elgendi/fo-data-atlas-2
gh release view v0.2.0 --repo Mahmoud-Elgendi/fo-data-atlas-2 --json url,tagName,isDraft,assets
Stop-Transcript
```

If upload stops after the draft exists, resume missing assets with `gh release upload v0.2.0 PATH --repo Mahmoud-Elgendi/fo-data-atlas-2`, using the exact missing asset path. Preserve already uploaded/released files; do not use --clobber. An uploaded draft is not reported as a published stable release. Source commands are documented here but remain unexecuted by the assistant until a real terminal run is recorded.

References: [create](https://cli.github.com/manual/gh_release_create), [upload](https://cli.github.com/manual/gh_release_upload), [edit](https://cli.github.com/manual/gh_release_edit).

## 5. Real recipient smoke test â€” after publication

With Python 3.10+ and GitHub CLI available, use the finalized bootstrap helper path:

```powershell
python scripts/github_release.py check --repo Mahmoud-Elgendi/fo-data-atlas-2
python scripts/github_release.py install --repo Mahmoud-Elgendi/fo-data-atlas-2
```

Use an actual clean download/install folder for the test. Follow host/global-project setup choices and host activation instructions. Check an offline metadata lookup afterward. Record output/installed version and gaps; a release that exists only as a draft cannot pass the helper's stable-release test.
