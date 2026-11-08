-- Packaged 0.2.0 example: all companies/POs; target-specific draft; run checks before use.
-- purchase-receipt-lines | all-company checks | NOT RUN
-- These inspect the promoted simple query, not the superseded complex draft.
-- Sample acceptance is owner-reported; all-company results remain pending.

-- 1. Source key/scope profile. Investigate missing identity and receipt numbers.
SELECT UPPER(r.dataareaid) AS Company, COUNT_BIG(*) AS ReceiptLines,
    COUNT_BIG(CASE WHEN r.recid IS NULL THEN 1 END) AS MissingLineIds,
    COUNT_BIG(CASE WHEN r.partition IS NULL THEN 1 END) AS MissingPartitions,
    COUNT_BIG(CASE WHEN r.dataareaid IS NULL OR r.dataareaid = '' THEN 1 END) AS MissingCompanyCodes,
    COUNT_BIG(CASE WHEN r.packingslipid IS NULL OR r.packingslipid = '' THEN 1 END) AS MissingReceiptNumbers
FROM dbo.vendpackingsliptrans AS r
WHERE r.IsDelete IS NULL
GROUP BY UPPER(r.dataareaid);

-- 2. Source identity duplicates. Expected: no rows.
SELECT r.partition AS PartitionKey, r.dataareaid AS SourceCompany,
    r.recid AS ReceiptLineRecId, COUNT_BIG(*) AS LineRows
FROM dbo.vendpackingsliptrans AS r
WHERE r.IsDelete IS NULL
GROUP BY r.partition, r.dataareaid, r.recid
HAVING COUNT_BIG(*) > 1;

-- 3. Header lookup duplicates. Expected: no rows.
SELECT h.partition AS PartitionKey, h.dataareaid AS SourceCompany,
    h.recid AS ReceiptHeaderRecId, COUNT_BIG(*) AS HeaderRows
FROM dbo.vendpackingslipjour AS h
WHERE h.IsDelete IS NULL
GROUP BY h.partition, h.dataareaid, h.recid
HAVING COUNT_BIG(*) > 1;

-- 4. Eligible current PO lookup duplicates. Expected: no rows.
SELECT p.partition AS PartitionKey, p.dataareaid AS SourceCompany,
    p.inventtransid AS InventTransId, COUNT_BIG(*) AS POLineRows
FROM dbo.purchline AS p
WHERE p.IsDelete IS NULL AND p.isdeleted = 0
  AND p.inventtransid IS NOT NULL AND p.inventtransid <> ''
GROUP BY p.partition, p.dataareaid, p.inventtransid
HAVING COUNT_BIG(*) > 1;

-- 5. Inventory dimension lookup duplicates. Expected: no rows.
SELECT idim.partition AS PartitionKey, idim.dataareaid AS SourceCompany,
    idim.inventdimid AS InventDimId, COUNT_BIG(*) AS DimensionRows
FROM dbo.inventdim AS idim
WHERE idim.IsDelete IS NULL
GROUP BY idim.partition, idim.dataareaid, idim.inventdimid
HAVING COUNT_BIG(*) > 1;

-- 6. Shared default-dimension lookup duplicates. Expected: no rows.
SELECT dim.partition AS PartitionKey, dim.recid AS DefaultDimensionRecId,
    COUNT_BIG(*) AS DimensionSetRows
FROM dbo.dimensionattributevalueset AS dim
WHERE dim.IsDelete IS NULL
GROUP BY dim.partition, dim.recid
HAVING COUNT_BIG(*) > 1;

-- 7. Simple FX lookup currencies must not multiply receipts.
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
SELECT er.FromCurrencyCode AS CurrencyCode, COUNT_BIG(*) AS RateRows
FROM ExchRate AS er
GROUP BY er.FromCurrencyCode
HAVING COUNT_BIG(*) > 1;

-- 8. Source vs exact output. Compare within Company, stored currency and unit.
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
),
Dataset AS (
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
    WHERE r.IsDelete IS NULL
)

SELECT 'BeforeEnrichment' AS Stage, UPPER(r.dataareaid) AS Company,
    r.currencycode_w AS StoredCurrency, r.purchunit AS Unit,
    COUNT_BIG(*) AS ReceiptLines, SUM(r.qty) AS ReceivedQty,
    SUM(r.lineamount_w) AS StoredReceiptAmount,
    SUM(r.valuemst) AS StoredAccountingAmount
FROM dbo.vendpackingsliptrans AS r
WHERE r.IsDelete IS NULL
GROUP BY UPPER(r.dataareaid), r.currencycode_w, r.purchunit
UNION ALL
SELECT 'AfterEnrichment' AS Stage, d.Company AS Company,
    d.[Stored Receipt Currency] AS StoredCurrency, d.Unit AS Unit,
    COUNT_BIG(*) AS ReceiptLines, SUM(d.[Received Qty]) AS ReceivedQty,
    SUM(d.[Stored Receipt Amount]) AS StoredReceiptAmount,
    SUM(d.[Stored Accounting Amount]) AS StoredAccountingAmount
FROM Dataset AS d
GROUP BY d.Company, d.[Stored Receipt Currency], d.Unit;

-- 9. Output identity duplicates, including possible Partition collisions.
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
),
Dataset AS (
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
    WHERE r.IsDelete IS NULL
)

SELECT d.Company AS Company, d.ReceiptLineRecId AS ReceiptLineRecId,
    COUNT_BIG(*) AS OutputRows
FROM Dataset AS d
GROUP BY d.Company, d.ReceiptLineRecId
HAVING COUNT_BIG(*) > 1;

-- 10. Output missing-value/reference profile. Blank native currency needs review.
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
),
Dataset AS (
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
    WHERE r.IsDelete IS NULL
)

SELECT d.Company AS Company, COUNT_BIG(*) AS ReceiptLines,
    COUNT_BIG(CASE WHEN d.HasMatchingHeader = 0 THEN 1 END) AS MissingHeaders,
    COUNT_BIG(CASE WHEN d.HasMatchingPOLine = 0 THEN 1 END) AS MissingPOLines,
    COUNT_BIG(CASE WHEN d.POLineReferenceMatches = 0 THEN 1 END) AS ConflictingPOReferences,
    COUNT_BIG(CASE WHEN d.IsReceiptAmountMissing = 1 THEN 1 END) AS NullReceiptAmounts,
    COUNT_BIG(CASE WHEN d.[Stored Receipt Currency] IS NULL
        OR d.[Stored Receipt Currency] = '' THEN 1 END) AS MissingStoredCurrencies,
    COUNT_BIG(CASE WHEN d.[Stored Receipt Amount] = 0
        AND d.[Received Qty] <> 0 THEN 1 END) AS ZeroAmountWithNonzeroQty
FROM Dataset AS d
GROUP BY d.Company;

-- 11. Native amount population by raw item classification and quantity sign.
-- Zero values are observations, not automatically missing. Compare with F&O.
SELECT UPPER(r.dataareaid) AS Company, r.stockedproduct AS StockedProductCode,
    r.currencycode_w AS StoredCurrency, r.purchunit AS Unit,
    CASE WHEN r.qty IS NULL THEN 'NULL' WHEN r.qty < 0 THEN 'Negative'
         WHEN r.qty = 0 THEN 'Zero' ELSE 'Positive' END AS QuantitySign,
    COUNT_BIG(*) AS ReceiptLines,
    COUNT_BIG(CASE WHEN r.lineamount_w IS NULL THEN 1 END) AS NullAmounts,
    COUNT_BIG(CASE WHEN r.lineamount_w = 0 THEN 1 END) AS ZeroAmounts,
    SUM(r.qty) AS ReceivedQty, SUM(r.lineamount_w) AS StoredReceiptAmount
FROM dbo.vendpackingsliptrans AS r
WHERE r.IsDelete IS NULL
GROUP BY UPPER(r.dataareaid), r.stockedproduct, r.currencycode_w, r.purchunit,
    CASE WHEN r.qty IS NULL THEN 'NULL' WHEN r.qty < 0 THEN 'Negative'
         WHEN r.qty = 0 THEN 'Zero' ELSE 'Positive' END;

-- 12. Rows using the owner-selected missing/zero FX fallback.
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
SELECT UPPER(r.dataareaid) AS Company, r.currencycode_w AS StoredCurrency,
    COUNT_BIG(*) AS LinesUsingRateOne
FROM dbo.vendpackingsliptrans AS r
LEFT JOIN ExchRate AS er
    ON r.currencycode_w = er.FromCurrencyCode
WHERE r.IsDelete IS NULL
  AND (er.ExchangeRate IS NULL OR er.ExchangeRate = 0)
GROUP BY UPPER(r.dataareaid), r.currencycode_w;
