-- Packaged 0.2.0 example: all companies/POs; target-specific draft; run checks before use.
-- purchase-order-lines: validation queries | 2026-11-05 | NOT RUN
-- Run manually in the same Fabric Warehouse as the dataset query.
-- Resolve duplicate keys (checks 2-4) before using the dataset in ETL.
-- Counts/sums are observations, not proof of reconciliation with F&O.

-- 1. Required source identity fields. Null/blank-key counts should be zero.
SELECT
    UPPER(l.dataareaid) AS Company,
    COUNT_BIG(*) AS RetainedSourceLines,
    COUNT_BIG(CASE WHEN l.recid IS NULL THEN 1 END) AS NullLineRecIds,
    COUNT_BIG(CASE WHEN l.partition IS NULL THEN 1 END) AS NullPartitions,
    COUNT_BIG(CASE WHEN l.dataareaid IS NULL OR l.dataareaid = '' THEN 1 END) AS MissingCompanyCodes,
    COUNT_BIG(CASE WHEN l.purchid IS NULL OR l.purchid = '' THEN 1 END) AS MissingPurchaseOrderNumbers
FROM dbo.purchline AS l
WHERE l.IsDelete IS NULL

GROUP BY UPPER(l.dataareaid);

-- 2a. Retained line identity. Expected: zero rows.
SELECT
    l.partition AS PartitionKey,
    l.dataareaid AS SourceCompany,
    l.recid AS PurchaseLineRecId,
    COUNT_BIG(*) AS DuplicateRows
FROM dbo.purchline AS l
WHERE l.IsDelete IS NULL

GROUP BY l.partition, l.dataareaid, l.recid
HAVING COUNT_BIG(*) > 1;

-- 2b. Output identity omits Partition. Expected: zero rows.
-- A result may mean Partition must be added to the output identity.
SELECT
    UPPER(l.dataareaid) AS Company,
    l.recid AS PurchaseLineRecId,
    COUNT_BIG(*) AS DuplicateOutputKeys
FROM dbo.purchline AS l
WHERE l.IsDelete IS NULL

GROUP BY UPPER(l.dataareaid), l.recid
HAVING COUNT_BIG(*) > 1;

-- 3. Header join keys. Expected: zero rows. Never hide duplicates with DISTINCT.
SELECT
    h.partition AS PartitionKey,
    h.dataareaid AS SourceCompany,
    h.purchid AS PurchaseOrderNumber,
    COUNT_BIG(*) AS MatchingHeaderRows
FROM dbo.purchtable AS h
WHERE h.IsDelete IS NULL
GROUP BY h.partition, h.dataareaid, h.purchid
HAVING COUNT_BIG(*) > 1;

-- 4. Filtered status lookup keys. Expected: zero rows.
-- Multiple rows can multiply dataset lines even if their text is identical.
SELECT
    m.EntityName AS EntityName,
    m.OptionSetName AS OptionSetName,
    m.LocalizedLabelLanguageCode AS LanguageCode,
    m.[Option] AS StatusCode,
    COUNT_BIG(*) AS MatchingLabelRows
FROM dbo.GlobalOptionsetMetadata AS m
WHERE m.EntityName IN ('purchtable', 'purchline')
  AND m.OptionSetName = 'purchstatus'
  AND m.LocalizedLabelLanguageCode = 1033
GROUP BY m.EntityName, m.OptionSetName, m.LocalizedLabelLanguageCode, m.[Option]
HAVING COUNT_BIG(*) > 1;

-- 5. Missing/invalid header identity. Expected: zero invalid-key rows.
SELECT
    UPPER(h.dataareaid) AS Company,
    COUNT_BIG(*) AS InvalidHeaderKeyRows
FROM dbo.purchtable AS h
WHERE h.IsDelete IS NULL
  AND (h.recid IS NULL OR h.partition IS NULL OR h.dataareaid IS NULL
       OR h.dataareaid = '' OR h.purchid IS NULL OR h.purchid = '')
GROUP BY UPPER(h.dataareaid);

-- 6. Unmatched headers. Review every result; these lines remain in the dataset.
SELECT
    UPPER(l.dataareaid) AS Company,
    COUNT_BIG(*) AS LinesWithoutMatchingHeader
FROM dbo.purchline AS l
LEFT JOIN dbo.purchtable AS h
    ON h.purchid = l.purchid
   AND h.dataareaid = l.dataareaid
   AND h.partition = l.partition
   AND h.IsDelete IS NULL
WHERE l.IsDelete IS NULL

  AND h.recid IS NULL
GROUP BY UPPER(l.dataareaid);

-- 7. Status codes without a lookup row. Expected: zero rows.
-- The header section covers all retained headers, including unused headers.
SELECT
    'purchline' AS StatusSource,
    UPPER(l.dataareaid) AS Company,
    l.purchstatus AS StatusCode,
    COUNT_BIG(*) AS SourceRowsWithoutLookup
FROM dbo.purchline AS l
WHERE l.IsDelete IS NULL

  AND NOT EXISTS (
      SELECT 1
      FROM dbo.GlobalOptionsetMetadata AS ml
      WHERE ml.EntityName = 'purchline'
        AND ml.OptionSetName = 'purchstatus'
        AND ml.LocalizedLabelLanguageCode = 1033
        AND ml.[Option] = l.purchstatus
  )
GROUP BY UPPER(l.dataareaid), l.purchstatus
UNION ALL
SELECT
    'purchtable' AS StatusSource,
    UPPER(h.dataareaid) AS Company,
    h.purchstatus AS StatusCode,
    COUNT_BIG(*) AS SourceRowsWithoutLookup
FROM dbo.purchtable AS h
WHERE h.IsDelete IS NULL
  AND NOT EXISTS (
      SELECT 1
      FROM dbo.GlobalOptionsetMetadata AS mh
      WHERE mh.EntityName = 'purchtable'
        AND mh.OptionSetName = 'purchstatus'
        AND mh.LocalizedLabelLanguageCode = 1033
        AND mh.[Option] = h.purchstatus
  )
GROUP BY UPPER(h.dataareaid), h.purchstatus;

-- 8. Lookup rows without usable text. Expected: zero rows.
-- This diagnoses blank text without changing the approved COALESCE behavior.
SELECT
    m.EntityName AS EntityName,
    m.OptionSetName AS OptionSetName,
    m.[Option] AS StatusCode,
    m.LocalizedLabel AS LocalizedLabel,
    m.ExternalValue AS ExternalValue
FROM dbo.GlobalOptionsetMetadata AS m
WHERE m.EntityName IN ('purchtable', 'purchline')
  AND m.OptionSetName = 'purchstatus'
  AND m.LocalizedLabelLanguageCode = 1033
  AND (COALESCE(m.LocalizedLabel, m.ExternalValue) IS NULL
       OR COALESCE(m.LocalizedLabel, m.ExternalValue) = '');

-- 9. Informational scope profile. No extra business filters are assumed.
-- IsDelete is link deletion. isdeleted is a separate application field.
-- Review purchase types and application deletion flags before defining a gold slice.
SELECT
    UPPER(l.dataareaid) AS Company,
    l.purchasetype AS PurchaseTypeCode,
    l.isdeleted AS ApplicationIsDeleted,
    COUNT_BIG(*) AS RetainedSourceLines
FROM dbo.purchline AS l
WHERE l.IsDelete IS NULL

GROUP BY UPPER(l.dataareaid), l.purchasetype, l.isdeleted;


-- 10. Compare retained source rows with the exact full dataset.
-- Equal counts/totals require unique header, dimension, status and FX lookup keys.
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
),
Dataset AS (
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

)
SELECT 'BeforeEnrichment' AS Stage, UPPER(l.dataareaid) AS Company,
    l.currencycode AS CurrencyCode, l.purchunit AS PurchaseUnitSymbol,
    COUNT_BIG(*) AS DatasetRows, SUM(l.purchqty) AS OrderedPurchaseQuantityTotal,
    SUM(l.lineamount) AS LineAmountTotal
FROM dbo.purchline AS l
WHERE l.IsDelete IS NULL

GROUP BY UPPER(l.dataareaid), l.currencycode, l.purchunit
UNION ALL
SELECT 'AfterEnrichment' AS Stage, d.Company AS Company,
    d.[Currency Code] AS CurrencyCode, d.Unit AS PurchaseUnitSymbol,
    COUNT_BIG(*) AS DatasetRows, SUM(d.Qty) AS OrderedPurchaseQuantityTotal,
    SUM(d.[Net Amount]) AS LineAmountTotal
FROM Dataset AS d
GROUP BY d.Company, d.[Currency Code], d.Unit;

-- 11. Shared default-dimension set keys. Expected: zero rows.
SELECT dim.partition AS PartitionKey, dim.recid AS DefaultDimensionRecId,
    COUNT_BIG(*) AS DuplicateSetRows
FROM dbo.dimensionattributevalueset AS dim
WHERE dim.IsDelete IS NULL
GROUP BY dim.partition, dim.recid
HAVING COUNT_BIG(*) > 1;

-- 12. Missing referenced dimension sets. Zero/NULL means no default set, not a missing row.
SELECT UPPER(l.dataareaid) AS Company, COUNT_BIG(*) AS MissingDefaultDimensionSets
FROM dbo.purchline AS l
LEFT JOIN dbo.dimensionattributevalueset AS dim
    ON dim.recid = l.defaultdimension
   AND dim.partition = l.partition
   AND dim.IsDelete IS NULL
WHERE l.IsDelete IS NULL

  AND l.defaultdimension IS NOT NULL
  AND l.defaultdimension <> 0
  AND dim.recid IS NULL
GROUP BY UPPER(l.dataareaid);

-- 13. Dimension coverage is informational. Blank dimensions are not invented or filled.
SELECT
    UPPER(l.dataareaid) AS Company,
    COUNT_BIG(*) AS RetainedLines,
    COUNT_BIG(CASE WHEN l.defaultdimension IS NULL OR l.defaultdimension = 0 THEN 1 END) AS LinesWithNoDefaultSet,
    COUNT_BIG(CASE WHEN dim.unitvalue IS NOT NULL AND dim.unitvalue <> '' THEN 1 END) AS LinesWithUnit,
    COUNT_BIG(CASE WHEN dim.departmentvalue IS NOT NULL AND dim.departmentvalue <> '' THEN 1 END) AS LinesWithDepartment,
    COUNT_BIG(CASE WHEN dim.costcentervalue IS NOT NULL AND dim.costcentervalue <> '' THEN 1 END) AS LinesWithCostCenter
FROM dbo.purchline AS l
LEFT JOIN dbo.dimensionattributevalueset AS dim
    ON dim.recid = l.defaultdimension
   AND dim.partition = l.partition
   AND dim.IsDelete IS NULL
WHERE l.IsDelete IS NULL

GROUP BY UPPER(l.dataareaid);

-- 14. Direct lookup assumes one result per FromCurrencyCode. Expected: zero rows.
-- Report duplicates separately instead of adding deduplication to the main query.
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
SELECT er.FromCurrencyCode AS FromCurrencyCode, COUNT_BIG(*) AS LookupRows
FROM ExchRate AS er
GROUP BY er.FromCurrencyCode
HAVING COUNT_BIG(*) > 1;

-- 15. Show where the user-selected missing/zero-rate fallback is used.
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
SELECT UPPER(l.dataareaid) AS Company, l.currencycode AS CurrencyCode,
    CASE WHEN er.ExchangeRate IS NULL THEN 'MissingRate' ELSE 'ZeroRate' END AS FallbackReason,
    COUNT_BIG(*) AS LinesUsingRateOne
FROM dbo.purchline AS l
LEFT JOIN ExchRate AS er
    ON l.currencycode = er.FromCurrencyCode
WHERE l.IsDelete IS NULL

  AND (er.ExchangeRate IS NULL OR er.ExchangeRate = 0)
GROUP BY UPPER(l.dataareaid), l.currencycode,
    CASE WHEN er.ExchangeRate IS NULL THEN 'MissingRate' ELSE 'ZeroRate' END;

-- 16. Local calculations replace NULL monetary inputs with zero, per the example.
-- Original transaction columns retain their original NULLs.
SELECT UPPER(l.dataareaid) AS Company,
    COUNT_BIG(CASE WHEN l.lineamount IS NULL THEN 1 END) AS NullLineAmounts,
    COUNT_BIG(CASE WHEN l.purchprice IS NULL THEN 1 END) AS NullPurchasePrices,
    COUNT_BIG(CASE WHEN l.linedisc IS NULL THEN 1 END) AS NullDiscountAmounts
FROM dbo.purchline AS l
WHERE l.IsDelete IS NULL

GROUP BY UPPER(l.dataareaid);

-- 17. Informational source review only. This does not change the requested rate CTE.
-- The simple FromCurrencyCode join assumes the returned rates are for SAR.
SELECT exch.fromcurrencycode AS FromCurrencyCode,
    exch.tocurrencycode AS ToCurrencyCode,
    x.validfrom AS RateValidFrom,
    x.validto AS RateValidTo,
    x.exchangerate / 100.0 AS StoredRatePerUnit
FROM dbo.exchangeratecurrencypair AS exch
INNER JOIN dbo.exchangerate AS x
    ON exch.recid = x.exchangeratecurrencypair
   AND exch.partition = x.partition
   AND x.IsDelete IS NULL
INNER JOIN dbo.exchangeratetype AS exchrt
    ON exch.exchangeratetype = exchrt.recid
   AND exch.partition = exchrt.partition
   AND exchrt.IsDelete IS NULL
WHERE exch.IsDelete IS NULL
  AND x.validto > GETDATE()
  AND exchrt.name = 'Default'
  AND (x.validfrom > GETDATE() OR exch.tocurrencycode <> 'SAR' OR x.exchangerate < 0);
