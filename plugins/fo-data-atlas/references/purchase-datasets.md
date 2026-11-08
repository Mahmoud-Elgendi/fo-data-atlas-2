# Initial purchase datasets

These are separate line-grain datasets, not one combined order/receipt/invoice rowset.

Release 0.2.0 includes target-specific purchase-order-lines and purchase-receipt-lines bundles under examples/, with SQL/mapping/checks and the sample Fabric schema. The older product-receipt-lines name points to the receipt bundle. Vendor invoice remains an explicitly blocked starter for the next iteration. All metadata remains searchable regardless of which examples are finished. Compare sample fields with the recipient's actual schema; no sample proves all-company reconciliation.

| Dataset | Driving table lead | Header lead |
|---|---|---|
| purchase-order-lines | PurchLine | PurchTable |
| vendor-invoice-lines | VendInvoiceTrans | VendInvoiceJour |
| product-receipt-lines | VendPackingSlipTrans | VendPackingSlipJour |

Find the actual source documents through `atlas.py search` with the project's chosen source ID. All six table XML files are present in the recorded application snapshot. This establishes source availability, not complete analytical semantics or target availability.

For purchase orders, existing authored guides propose PurchId with company/Partition scope. For invoices, inspect the full composite relationship and the `vendInvoiceJour` / `findFromVendInvoiceTrans` code where needed. Document numbers alone are not assumed unique. Receipt joins likewise require the actual declared relationship. Each target field must exist in the Fabric schema export.

The exported `PurchPurchaseOrderHeaderV2Entity` declares `PurchaseOrderNumber` mapped to `PurchTable.PurchId`. The table field uses EDT PurchIdBase, whose label @SYS15812 resolves to Purchase order in the English SYS resource. Use this as an evidence-backed alias example, not as validation of all entity mappings.

The existing knowledge source contains `12 SQL Concepts - Header and Lines.md`, `11 Purchase to Pay - Process and Dataset Guide.md` and `p2p-guide.json`. Search the knowledge source and read these when planning field meanings, measures and checks. Their SQL is authored teaching material; semantic validation is explicitly false.

Never attach raw receipt and invoice line rowsets together to the same purchase line without an independently designed grain strategy: multiple events can create combinations. First-version outputs remain the three separate datasets. The initial example folders intentionally remain blocked until target schemas and field selections are confirmed.
