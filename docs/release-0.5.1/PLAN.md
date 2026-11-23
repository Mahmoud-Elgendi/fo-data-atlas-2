# Release 0.5.1

On 23 November 2026 the owner approved publishing the financial dimension alias convention and integrating it into main. This is a tools-only patch, preserving metadata-catalog.json and original exports. Main remains the only remote branch; v0.5.0 and older release assets are immutable.

Scope: seven standard Value aliases in the authoritative financial-dimensions reference, a pointer in mandatory SQL rules, current version/install/update documentation and release evidence. The user's tenant-specific corrected query remains local to the application workspace and is not published. Existing purchase examples already use the established Value names and need no SQL rewrite.

Verify the source suite, package manifests/links, archive integrity and offline cache reuse. Commit only the plugin-only checkout, push main, tag v0.5.1, upload tools ZIP/checksum/helper to a draft, verify digests and publish. Confirm real private release download and the GitHub-backed npx release check. Record native host and recipient/F&O validation limits separately.
