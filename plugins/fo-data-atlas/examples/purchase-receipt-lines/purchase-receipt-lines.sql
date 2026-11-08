-- Packaged 0.2.0 example: all companies/POs; target-specific draft; run checks before use.
-- purchase-receipt-lines | all-company current-position draft | 2026-11-05
-- Based on owner-accepted incremental tests for PO the owner-tested PO.
-- Native CurrencyCode_W / LineAmount_W accepted on that sample only.
-- Their wider country/configuration coverage still requires validation.
-- Keep zero/negative/service lines. NULL amounts and derived LCY stay NULL.
-- LCY uses the owner-selected current Default/SAR pattern, not posted historical FX.
-- All-company results are not yet validated. Run the accompanying checks.
WITH ExchRate AS (
    SELECT exch.fromcurrencycode AS FromCurrencyCode,
        CASE
            WHEN exch.fromcurrencycode = 'SAR' THEN 1.0
            ELSE x.exchangerate / 100.0
        END AS ExchangeRate
    FROM dbo.exchangeratecurrencypair AS exch
    INNER JOIN dbo.exchangerate AS x
        ON exch.recid = x.exchangeratecurrencypair
       AND exch.partition = x.partition
       AND x.IsDelete IS NULL
    INNER JOIN dbo.exchangeratetype AS exchrt
        ON exch.exchangeratetype = exchrt.recid
       AND exch.partition = exchrt.partition
       AND exchrt.IsDelete IS NULL
    WHERE x.validto > GETDATE()
      AND exchrt.name = 'Default'
      AND exch.IsDelete IS NULL
)
SELECT
    UPPER(r.dataareaid) AS Company,
    r.recid AS ReceiptLineRecId,
    r.vendpackingslipjour AS ReceiptHeaderRecId,
    r.packingslipid AS [Receipt No],
    r.deliverydate AS [Receipt Date],
    r.origpurchid AS [Purchase Order No],
    r.purchaselinelinenumber AS PurchaseOrderLineNumber,
    r.inventtransid AS InventTransId,
    r.itemid AS [Item No],
    r.name AS [Line Description],
    r.qty AS [Received Qty],
    r.purchunit AS Unit,
    r.valuemst AS [Stored Accounting Amount],
    r.currencycode_w AS [Stored Receipt Currency],
    r.lineamount_w AS [Stored Receipt Amount],
    CASE
        WHEN r.lineamount_w IS NULL THEN CAST(1 AS BIT)
        ELSE CAST(0 AS BIT)
    END AS IsReceiptAmountMissing,
    COALESCE(NULLIF(er.ExchangeRate, 0), 1.0) AS ExchangeRateToLCY,
    CAST(
        r.lineamount_w * COALESCE(NULLIF(er.ExchangeRate, 0), 1.0)
        AS DECIMAL(38, 6)
    ) AS [Stored Receipt Amount LCY],
    r.priceunit AS [Receipt Price Quantity],
    p.recid AS PurchaseLineRecId,
    p.purchqty AS [Current PO Ordered Qty],
    p.purchprice AS [Current PO Purchase Price],
    p.priceunit AS [Current PO Price Quantity],
    p.currencycode AS [Current PO Currency Code],
    CASE
        WHEN p.recid IS NULL THEN CAST(0 AS BIT)
        ELSE CAST(1 AS BIT)
    END AS HasMatchingPOLine,
    CASE
        WHEN p.recid IS NULL THEN CAST(NULL AS BIT)
        WHEN p.purchid = r.origpurchid
         AND p.linenumber = r.purchaselinelinenumber THEN CAST(1 AS BIT)
        ELSE CAST(0 AS BIT)
    END AS POLineReferenceMatches,
    idim.inventsiteid AS Site,
    idim.inventlocationid AS Warehouse,
    r.defaultdimension AS DefaultDimensionRecId,
    dim.unitgroupvalue AS UnitGroupValue,
    dim.unitvalue AS UnitValue,
    dim.departmentvalue AS DepartmentValue,
    dim.sectionvalue AS SectionValue,
    dim.projectvalue AS ProjectValue,
    h.orderaccount AS OrderVendorAccount,
    h.invoiceaccount AS InvoiceVendorAccount,
    CASE
        WHEN h.recid IS NULL THEN CAST(0 AS BIT)
        ELSE CAST(1 AS BIT)
    END AS HasMatchingHeader
FROM dbo.vendpackingsliptrans AS r
LEFT JOIN dbo.vendpackingslipjour AS h
    ON h.recid = r.vendpackingslipjour
   AND h.dataareaid = r.dataareaid
   AND h.partition = r.partition
   AND h.IsDelete IS NULL
LEFT JOIN dbo.dimensionattributevalueset AS dim
    ON dim.recid = r.defaultdimension
   AND dim.partition = r.partition
   AND dim.IsDelete IS NULL
LEFT JOIN dbo.inventdim AS idim
    ON idim.inventdimid = r.inventdimid
   AND idim.dataareaid = r.dataareaid
   AND idim.partition = r.partition
   AND idim.IsDelete IS NULL
LEFT JOIN dbo.purchline AS p
    ON p.inventtransid = r.inventtransid
   AND p.dataareaid = r.dataareaid
   AND p.partition = r.partition
   AND p.isdeleted = 0
   AND p.IsDelete IS NULL
   AND r.inventtransid IS NOT NULL
   AND r.inventtransid <> ''
LEFT JOIN ExchRate AS er
    ON r.currencycode_w = er.FromCurrencyCode
WHERE r.IsDelete IS NULL;
