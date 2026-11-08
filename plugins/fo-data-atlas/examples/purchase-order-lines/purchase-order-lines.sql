-- Packaged 0.2.0 example: all companies/POs; target-specific draft; run checks before use.
-- purchase-order-lines | user-selected simple FX pattern | 2026-11-05
-- LCY is SAR by the supplied reporting convention, not derived from company Ledger.
-- Current Default rate joined by transaction currency only.
-- Missing or zero rate -> 1.0. NULL monetary input -> 0.0 for the local calculation.
-- Check FX currency uniqueness separately before ETL. No automatic deduplication.
-- Existing Fabric IsDelete/Partition rules are retained inside source-table joins.
-- Headers, statuses and line default dimensions are unchanged. SQL not executed.
WITH ExchRate AS (
    SELECT
        exch.fromcurrencycode AS FromCurrencyCode,
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
    UPPER(l.dataareaid) AS Company,
    l.purchid AS [Purchase Order No],
    l.linenumber AS LineNumber,
    l.recid AS PurchaseLineRecId,
    h.purchname AS [Vendor Name],
    h.orderaccount AS OrderVendorAccount,
    h.invoiceaccount AS InvoiceVendorAccount,
    l.itemid AS [Item No],
    l.name AS [Line Description],
    l.purchqty AS Qty,
    l.purchunit AS Unit,
    l.currencycode AS [Currency Code],
    l.purchprice AS [Purchase Price],
    l.priceunit AS PurchasePriceQuantity,
    l.lineamount AS [Net Amount],
    l.linedisc AS [Line Discount Amount],
    l.linepercent AS [Line Discount Percentage],
    l.deliverydate AS RequestedDeliveryDate,
    l.confirmeddlv AS ConfirmedDeliveryDate,
    h.purchstatus AS PurchaseOrderStatusCode,
    hs.StatusLabel AS [Purchase Order Status],
    l.purchstatus AS PurchaseOrderLineStatusCode,
    ls.StatusLabel AS [Purchase Order Line Status],
    h.recid AS PurchaseHeaderRecId,
    CASE
        WHEN h.recid IS NULL THEN CAST(0 AS BIT)
        ELSE CAST(1 AS BIT)
    END AS HasMatchingHeader,
    l.defaultdimension AS DefaultDimensionRecId,
    dim.unitgroupvalue AS UnitGroupValue,
    dim.unitvalue AS UnitValue,
    dim.departmentvalue AS DepartmentValue,
    dim.sectionvalue AS SectionValue,
    dim.projectvalue AS ProjectValue,
    CASE
        WHEN l.defaultdimension IS NULL OR l.defaultdimension = 0 THEN CAST(NULL AS BIT)
        WHEN dim.recid IS NULL THEN CAST(0 AS BIT)
        ELSE CAST(1 AS BIT)
    END AS HasMatchingDefaultDimension,
    COALESCE(NULLIF(er.ExchangeRate, 0), 1.0) AS ExchangeRateToLCY,
    CAST(COALESCE(l.purchprice, 0.0) * COALESCE(NULLIF(er.ExchangeRate, 0), 1.0) AS DECIMAL(38,6)) AS [Purchase Price LCY],
    CAST(COALESCE(l.lineamount, 0.0) * COALESCE(NULLIF(er.ExchangeRate, 0), 1.0) AS DECIMAL(38,6)) AS [Net Amount LCY],
    CAST(COALESCE(l.linedisc, 0.0) * COALESCE(NULLIF(er.ExchangeRate, 0), 1.0) AS DECIMAL(38,6)) AS [Line Discount Amount LCY]
FROM dbo.purchline AS l
LEFT JOIN dbo.purchtable AS h
    ON h.purchid = l.purchid
   AND h.dataareaid = l.dataareaid
   AND h.partition = l.partition
   AND h.IsDelete IS NULL
LEFT JOIN dbo.dimensionattributevalueset AS dim
    ON dim.recid = l.defaultdimension
   AND dim.partition = l.partition
   AND dim.IsDelete IS NULL
LEFT JOIN (
    SELECT
        mh.[Option] AS StatusCode,
        COALESCE(mh.LocalizedLabel, mh.ExternalValue) AS StatusLabel
    FROM dbo.GlobalOptionsetMetadata AS mh
    WHERE mh.EntityName = 'purchtable'
      AND mh.OptionSetName = 'purchstatus'
      AND mh.LocalizedLabelLanguageCode = 1033
) AS hs
    ON hs.StatusCode = h.purchstatus
LEFT JOIN (
    SELECT
        ml.[Option] AS StatusCode,
        COALESCE(ml.LocalizedLabel, ml.ExternalValue) AS StatusLabel
    FROM dbo.GlobalOptionsetMetadata AS ml
    WHERE ml.EntityName = 'purchline'
      AND ml.OptionSetName = 'purchstatus'
      AND ml.LocalizedLabelLanguageCode = 1033
) AS ls
    ON ls.StatusCode = l.purchstatus
LEFT JOIN ExchRate AS er
    ON l.currencycode = er.FromCurrencyCode
WHERE l.IsDelete IS NULL
;