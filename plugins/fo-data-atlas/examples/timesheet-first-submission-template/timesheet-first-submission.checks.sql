-- TEMPLATE: replace {{parameters}} after recipient evidence review.
SELECT tst.partition, tst.dataareaid, tst.recid, COUNT_BIG(*) AS [RowCount]
FROM dbo.tstimesheettable AS tst
WHERE tst.IsDelete IS NULL
GROUP BY tst.partition, tst.dataareaid, tst.recid HAVING COUNT_BIG(*) > 1;

SELECT m.[Option], COUNT_BIG(*) AS LabelCount
FROM dbo.GlobalOptionsetMetadata AS m
WHERE m.EntityName = 'workflowtrackingtable' AND m.OptionSetName = 'trackingtype'
  AND m.LocalizedLabelLanguageCode = {{label_language_code}}
GROUP BY m.[Option] HAVING COUNT_BIG(*) > 1;

SELECT h.partition, UPPER(h.contextcompanyid) AS Company, h.contextrecid,
    COUNT_BIG(*) AS SubmissionCount, MIN(t.createddatetime) AS FirstSubmissionUTC
FROM dbo.workflowtrackingtable AS t
INNER JOIN dbo.workflowtrackingstatustable AS h
    ON h.recid = t.workflowtrackingstatustable
   AND h.partition = t.partition AND h.IsDelete IS NULL
WHERE t.IsDelete IS NULL
  AND h.contexttableid = {{timesheet_context_table_id}}
  AND t.trackingtype = {{submission_tracking_type_code}}
GROUP BY h.partition, UPPER(h.contextcompanyid), h.contextrecid
HAVING COUNT_BIG(*) > 1;
