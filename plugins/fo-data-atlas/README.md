# F&O Data Atlas — private AI plugin

Version 0.3.0. Offline F&O metadata exploration, exported view SQL/dependencies and Fabric query drafting for Codex and Claude Code. No VM, operational database or Atlas app connection is needed after the complete package is installed.

## Install

Online bootstrap requires Python 3.10+ and authenticated GitHub CLI with access to Mahmoud-Elgendi/fo-data-atlas-2. Download scripts/github_release.py from that repository or use its copy in this package, then run:

```powershell
python scripts/github_release.py install
```

This downloads and verifies the small tools package, then opens the branded setup wizard by Mahmoud Elgendi. Choose Core metadata (default) or Full offline; verified metadata is cached once per machine. Choose the AI tool and global/current-project scope; confirm with [Y/n]. Follow the displayed host activation steps. For offline installation, provide the matching local metadata pack with --local-pack; uncached profiles otherwise need a download. Native host activation must be checked separately.

Source checkouts do not include the large offline database; the GitHub release asset supplies it. Version 0.3.0 is prepared locally until its release is actually published; live GitHub download/host activation are separate verification steps.

## Ask

- Show the SQL behind CustCustomerV3Entity and its underlying views.
- Explain which tables and fields this F&O form references, using exported metadata.
- Create purchase-order-lines. Suggest the fields first.
- Update F&O Data Atlas through GitHub.

For an existing view the skill shows original SQL, lists underlying views/tables and offers their SQL. All metadata in the current pack stays searchable; the view inspector follows the exported SQL dependency catalog. Original source SQL is not automatically Fabric-compatible.

For a new Fabric dataset, run templates/export-fabric-schema.sql manually in Fabric, save CSV and initialize each project with atlas.py init-project --project PROJECT --schema CSV. Select matching source IDs from atlas.py sources. The skill checks schema/evidence, confirms fields, and produces descriptively named SQL, mapping and checks files.

## Included

The full reference corpus contains 447,389 evidence documents from 11 separate sources. Core keeps all object identities discoverable and 204,438 original document identities readable offline; Full includes all originals. It retains original XML/X++, labels, SQL definitions, schema/dependencies and authored references. These counts describe the imported snapshots, not every object in every F&O build. No new .49 VM evidence has been substituted or relabelled.

Target-specific PO and receipt examples include SQL/mapping/checks, evidence and a sample schema. Compare them with your actual target; all-company financial reconciliation remains unverified. Vendor invoice is an explicit starter for a later iteration.

## References

- [Setup](references/setup.md)
- [GitHub/offline updates](references/github-updates.md)
- [Core/Full profiles and shared cache](references/metadata-profiles.md)
- [View SQL and dependency inspection](references/sql-lineage.md)
- [SQL conventions](references/sql-rules.md)
- [Dimensions and currencies](references/financial-dimensions-and-currency.md)
- [Evidence use and coverage](references/reference-usage.md)
- [Named deliverables](references/deliverables.md)
- [Verification](references/verification.md)

## Maintainers

Build new evidence into a fresh output with scripts/build_references.py and an explicit source config; never overwrite original exports or an existing snapshot. tools/build_atlas_metadata_packs.py builds new immutable metadata assets; tools/package_atlas_plugin.py --tools builds the small tools ZIP and manifest. Reuse unchanged metadata catalogs for tools-only releases. Updating scripts/examples does not require rebuilding the unchanged corpus. Retain old releases and explicit source selection.
