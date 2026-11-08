# vendor-invoice-lines

Status: blocked draft. Runtime validated: false. Business reconciled: false.

## Purpose and grain

One row represents one captured VendInvoiceTrans record, with selected VendInvoiceJour attributes. Keep all nondeleted driving lines across all legal entities, including lines without a header. Do not combine this raw event family with the other purchase datasets.

## Blocking inputs

- Actual Fabric schema CSV has not been supplied for this example.
- The business field list and output aliases have not yet been confirmed.
- Complete header matching predicates and scope require evidence review and target checks. No unverified join is approved by this template.

## Available source evidence

Snapshot: `application-20261019`. These are original exported declarations, not runtime results or confirmed Fabric schema.

| Object | Packed evidence ID | Original XML SHA256 |
|---|---|---|
| VendInvoiceTrans | `e795329300de34326bf15a0480741393` | `0560884aec5361259ea465228950d55b950960f782089a228af8e66890559208` |
| VendInvoiceJour | `34c218304511e17ce258cd5453337aa8` | `d0530056a58ef3a93f633f638d02a4f5d6b07607245969872caceb4b6b23bb3b` |

Read each object with `atlas.py show <id> --relation <header-table>` or `--field <field>`; use raw local output when the bounded summary is insufficient. The package contains the original supporting XML. Keep extension candidates separate.

## Proposed output rules

- Confirm the line identity including applicable environment, company and Partition scope.
- Output `UPPER(line.dataareaid) AS Company` when the exact target field is available.
- LEFT JOIN the matching header; keep its deletion filter in ON or its own subquery.
- Apply exactly `IsDelete IS NULL` to each link source that has the column.
- Confirm and map business aliases; add status code/text only for selected, supported fields.
- Mark any repeated header amounts as non-additive at line grain.

## Unverified proposals and approvals

None approved. Record a complete proposed predicate, evidence gaps and the explicit user decision here before adding an unsupported join to SQL.

## Check plan

Not run: source line counts by Company; line-key duplicates; duplicate header keys; unmatched headers; before/after enrichment row counts; duplicate filtered enum options and unmatched status codes when selected; reconciliation by appropriate company/currency/unit/time scope.
