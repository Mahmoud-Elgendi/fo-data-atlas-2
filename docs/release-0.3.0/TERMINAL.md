# 0.3.0 terminal handover

The owner requested one command at a time. These are a reference sequence, not commands already executed. We will guide each live step separately. GitHub CLI path on this machine: C:\Program Files\GitHub CLI\gh.exe. Authentication is already confirmed by owner terminal evidence; retain it.

## Source update

1. In the existing plugin-only source repository, create codex/release-0.3.0 from the published 0.2 source branch.
2. Copy the prepared 0.3 source overlay into that checkout, excluding .git and generated test files. Remove the obsolete tracked references/INDEX.md and references/manifest.json summaries from the old monolithic source (the old tag retains them). Preserve old docs/history and .gitattributes '* -text'. The exact overlay path is recorded in delivery.json after build.
3. Review git diff/status. Stage only .gitattributes/.gitignore, README/release notes, plugins, tools, tests and docs. Metadata database/ZIP assets stay outside Git.
4. Commit/push the source branch; tag/push v0.3.0. Once source is reviewed, set the new source branch as repository default so new clones use the metadata-aware bootstrap. Existing 0.2 tags/assets remain unchanged.

## Draft and assets

Create v0.3.0 as a draft using --verify-tag and --notes-file release-notes.md. Upload the small fo-data-atlas-0.3.0.zip, its .sha256 file, github_release.py, and both exact metadata ZIP filenames from metadata-catalog.json. Asset paths/sizes/hashes are in the final delivery manifest. Do not upload a database directly or use --clobber.

Review the complete draft and SHA256 digests, then publish with --draft=false --latest. Read back tagName/isDraft/assets/url. A published tools release must have every uncached metadata asset referenced by its catalog available at the pinned metadata release tag.

## Local use without downloading metadata again

For this owner's machine the built Core already exists. The staged tools Setup.cmd/scripts/install.py can take --metadata-profile core --local-pack <built-core-root> so no metadata network download is necessary. Choose AI tool and registration scope in the wizard. This is a local seed of the same verified baseline, not a special reduced corpus.

For a clean recipient, the new github_release.py install downloads tools, then the selected uncached metadata profile. Verify Core first. Metadata_cache.py status reports the active profile; install --profile full explicitly acquires/activates Full. Record native host activation separately.

Do not retry the old 0.2 bootstrap against 0.3's tools-only format. Use the new release helper/source branch. The 0.3 helper also searches standard Windows GitHub CLI installation folders when an IDE terminal has an old PATH. Native Git/gh commands can still use their known absolute path.
