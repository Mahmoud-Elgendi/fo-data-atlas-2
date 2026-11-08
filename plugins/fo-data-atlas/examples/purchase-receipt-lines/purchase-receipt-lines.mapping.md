# purchase-receipt-lines

Status: target-specific full-load example, not a universally validated production query. Runtime validated: false. Business reconciled: false. Checks not run by the assistant.

## Scope and grain

One retained VendPackingSlipTrans record, LEFT JOIN its journal by stored header RecId/company/partition; unmatched lines remain. Packaged SQL/checks contain no owner PO filter. These files are deliberately adapted copies; project dataset originals remain unchanged. Company is UPPER(dataareaid). Headerless lines remain and have diagnostics; headers without lines add no rows.

37 outputs. Receipt stored defaultdimension is used. Inventory location enrichment is optional; service lines remain. Current PO quantity/price repeats across receipts and is non-additive. lineamount_w/currencycode_w were accepted on one owner sample; regional metadata and all-company population remain unverified. valuemst is independently sourced accounting amount.

## Target schema and evidence

Sample schema: ../fabric-schema-example.csv, SHA256 734f53d2e2d4d8b58042a79ac544a452ac5cde7dbe4ca90c33a17c6a1b126cd9. Compare with the recipient's actual Fabric CSV; never auto-install this sample as their schema. Source IDs: sql-application-catalog-20261023 and application-20261019. Metadata/runtime target-build alignment remains unconfirmed. Each output alias and its exact expression is explicit in the named SQL file; original evidence IDs/hashes are in purchase-receipt-lines.review-evidence.json.

## Dimensions, currency and checks

Stored defaultdimension joins dimensionattributevalueset by RecId/Partition with its IsDelete selection in ON. The five dimension value columns are tenant/schema specific. Status labels use filtered English metadata subqueries where present, retaining code and text.

Current LCY follows the owner-approved Default/validto > GETDATE()/SAR reporting pattern, joined by source currency with a 1.0 missing/zero-rate fallback. Diagnose duplicate currencies and fallback use. This is not proof of historical posting FX or every company's accounting currency. PO NULL amounts become zero only for derived LCY; receipt NULL native amount remains NULL.

Run the accompanying checks manually, inspect fanout/unmatched rows and reconcile within company/currency/unit. Sample acceptance does not establish all-company amount or business correctness. Bounded lint may leave a manual CTE review; this does not waive real schema/casing issues. For a deployed DWH, current-rate presentation can be separated from stored fact amounts; no loader is deployed by this example.
