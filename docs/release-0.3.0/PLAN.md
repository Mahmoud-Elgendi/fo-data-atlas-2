# F&O Data Atlas 0.3.0 — small tools and shared metadata

Date: 2026-11-08. Owner accepted the smaller Core default and Full offline choice. The published 0.2.0 release is immutable and has not been replaced.

## Delivered design

- Small tools ZIP contains skills/helpers/examples and a metadata catalog, not the evidence database.
- Core is the setup default: both SQL catalogs, structural XML and English labels. All 447,389 object identities remain discoverable; 204,438 document identities have cached payloads. Uncached originals are explicitly marked and Full is offered when needed.
- Full offline contains every original current document/payload. No source export or original SQLite evidence was modified.
- Metadata is pinned by baseline/profile/hash in a shared cache and referenced by installed tools. Projects retain their schema and source selection. Matching cache entries are reused across installations and compatible tool updates.
- Metadata ZIPs and tools ZIPs are separate immutable GitHub assets. Future tools-only releases reuse this metadata catalog/release tag instead of rebuilding or downloading the baseline again.
- Extended Windows paths cover tools/metadata download, extraction, verification, installation and promotion.

## Measurements

| Component | Download | Local database |
|---|---:|---:|
| Core | 318,513,889 bytes (303.8 MiB) | 611,340,288 bytes |
| Full offline | 1,301,733,130 bytes (1.21 GiB) | 1,742,393,344 bytes |
| Tools | Recorded in final build/delivery manifest | No evidence database per installation |

Both profiles retain original source IDs and hashes. Full uses the exact old SQLite content SHA256 8a63169e90b0c2f76a95f08bcb726efbc1cfa8fbd48bf83cf6eba24e15c6ea18. Profile switching is explicit, not an incremental overlay; retaining both keeps both immutable databases. Discovery does not equal original-text availability.

## Migration and limits

The 0.2 bootstrap expects a monolithic archive. Use the new source/bootstrap helper for the one-time 0.3 migration. After publication, make the new source branch the repository default so new clones receive the new helper. Installed 0.2 users should use the new release helper rather than the old extractor.

The setup wizard still chooses Codex/Claude and global/current-project scope. Native host activation is a separate step. Private GitHub transfer after publication remains a live check; local cache/ZIP tests do not establish it. Current sources are not a newly collected .49 baseline. DWH work remains on hold.

See [TASKS.md](TASKS.md), [ACTIONS.md](ACTIONS.md), [TERMINAL.md](TERMINAL.md) and ADR 0005. This release is not published until the owner completes the recorded terminal steps.
