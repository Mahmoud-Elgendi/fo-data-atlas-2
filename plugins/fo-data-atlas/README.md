# F&O Data Atlas — private AI plugin

Version 0.2.0. Offline F&O metadata exploration, exported view SQL/dependencies and Fabric query drafting for Codex and Claude Code. No VM, operational database or Atlas app connection is needed after the complete package is installed.

## Install

Online bootstrap requires Python 3.10+ and authenticated GitHub CLI with access to Mahmoud-Elgendi/fo-data-atlas-2. Download scripts/github_release.py from that repository or use its copy in this package, then run:

```powershell
python scripts/github_release.py install
```

This downloads and verifies the full offline package, then opens the branded setup wizard by Mahmoud Elgendi. Choose the AI tool and global/current-project scope; confirm with [Y/n]. Follow the displayed host activation steps. For an already downloaded complete ZIP, run Setup.cmd or python scripts/install.py entirely offline. Native host activation must be checked separately.

Source checkouts do not include the large offline database; the GitHub release asset supplies it. Version 0.2.0 is prepared locally until its release is actually published; live GitHub download/host activation are separate verification steps.

## Ask

- Show the SQL behind CustCustomerV3Entity and its underlying views.
- Explain which tables and fields this F&O form references, using exported metadata.
- Create purchase-order-lines. Suggest the fields first.
- Update F&O Data Atlas through GitHub.

For an existing view the skill shows original SQL, lists underlying views/tables and offers their SQL. All metadata in the current pack stays searchable; the view inspector follows the exported SQL dependency catalog. Original source SQL is not automatically Fabric-compatible.

For a new Fabric dataset, run templates/export-fabric-schema.sql manually in Fabric, save CSV and initialize each project with atlas.py init-project --project PROJECT --schema CSV. Select matching source IDs from atlas.py sources. The skill checks schema/evidence, confirms fields, and produces descriptively named SQL, mapping and checks files.

## Included

The unchanged full reference corpus contains 447,389 evidence documents from 11 separate sources. It retains original XML/X++, labels, SQL definitions, schema/dependencies and authored references. These counts describe the imported snapshots, not every object in every F&O build. No new .49 VM evidence has been substituted or relabelled.

Target-specific PO and receipt examples include SQL/mapping/checks, evidence and a sample schema. Compare them with your actual target; all-company financial reconciliation remains unverified. Vendor invoice is an explicit starter for a later iteration.

## References

- [Setup](references/setup.md)
- [GitHub/offline updates](references/github-updates.md)
- [View SQL and dependency inspection](references/sql-lineage.md)
- [SQL conventions](references/sql-rules.md)
- [Dimensions and currencies](references/financial-dimensions-and-currency.md)
- [Evidence use and coverage](references/reference-usage.md)
- [Named deliverables](references/deliverables.md)
- [Verification](references/verification.md)

## Maintainers

Build new evidence into a fresh output with scripts/build_references.py and an explicit source config; never overwrite original exports or an existing snapshot. tools/package_atlas_plugin.py in the source repository builds a complete ZIP and manifest after version/content changes. Updating scripts/examples does not require rebuilding the unchanged corpus. Retain old releases and explicit source selection.
