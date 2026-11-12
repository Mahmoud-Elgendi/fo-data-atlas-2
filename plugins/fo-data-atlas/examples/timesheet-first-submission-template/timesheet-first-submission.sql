-- TEMPLATE: resolve every {{parameter}} from recipient evidence/owner decisions.
-- Preconditions: company-case normalization is appropriate; referenced schema exists.
WITH WorkflowSubmission AS (
    SELECT
        h.partition AS SourcePartition,
        UPPER(h.contextcompanyid) AS ContextCompanyId,
        h.contexttableid AS ContextTableId,
        h.contextrecid AS DocumentRecId,
        t.recid AS SubmissionEventRecId,
        t.trackingtype AS TrackingTypeCode,
        DATEADD(HOUR, {{utc_offset_hours}}, t.createddatetime) AS StartTime,
        t.[user] AS [User],
        ROW_NUMBER() OVER (
            PARTITION BY h.partition, UPPER(h.contextcompanyid), h.contexttableid, h.contextrecid
            ORDER BY t.createddatetime, t.recid, h.recid
        ) AS SubmissionRank
    FROM dbo.workflowtrackingtable AS t
    INNER JOIN dbo.workflowtrackingstatustable AS h
        ON h.recid = t.workflowtrackingstatustable
       AND h.partition = t.partition AND h.IsDelete IS NULL
    WHERE t.IsDelete IS NULL
      AND h.contexttableid = {{timesheet_context_table_id}}
      AND t.trackingtype = {{submission_tracking_type_code}}
)
SELECT
    UPPER(tst.dataareaid) AS Company,
    tst.*,
    w.DocumentRecId AS DocId,
    tracking.TrackingTypeLabel AS [Tracking Type],
    w.StartTime,
    w.[User],
    hw.recid AS WorkerRecId,
    hw.personnelnumber AS Personnelnumber,
    CASE
        WHEN DATEDIFF(DAY, tst.periodto, w.StartTime) < 0 THEN 0
        ELSE DATEDIFF(DAY, tst.periodto, w.StartTime)
    END AS DurationDays,
    CAST(YEAR(tst.periodfrom) AS VARCHAR(4))
        + RIGHT('00' + CAST(DATEPART(WEEK, tst.periodfrom) AS VARCHAR(2)), 2) AS WeekFrom,
    CAST(YEAR(tst.periodto) AS VARCHAR(4))
        + RIGHT('00' + CAST(DATEPART(WEEK, tst.periodto) AS VARCHAR(2)), 2) AS WeekTo
FROM dbo.tstimesheettable AS tst
LEFT JOIN WorkflowSubmission AS w
    ON w.DocumentRecId = tst.recid
   AND w.SourcePartition = tst.partition
   AND w.ContextCompanyId = UPPER(tst.dataareaid)
   AND w.ContextTableId = tst.tableid
   AND w.SubmissionRank = 1
LEFT JOIN (
    SELECT m.[Option] AS TrackingTypeCode,
        COALESCE(m.LocalizedLabel, m.ExternalValue) AS TrackingTypeLabel
    FROM dbo.GlobalOptionsetMetadata AS m
    WHERE m.EntityName = 'workflowtrackingtable'
      AND m.OptionSetName = 'trackingtype'
      AND m.LocalizedLabelLanguageCode = {{label_language_code}}
) AS tracking
    ON tracking.TrackingTypeCode = w.TrackingTypeCode
LEFT JOIN dbo.resresourceidentifier AS rri
    ON rri.recid = tst.resource
   AND rri.partition = tst.partition AND rri.IsDelete IS NULL
LEFT JOIN dbo.wrkctrtable AS wct
    ON wct.recid = rri.refrecid
   AND wct.tableid = rri.reftableid
   AND wct.partition = rri.partition
   AND UPPER(wct.dataareaid) = UPPER(tst.dataareaid)
   AND wct.IsDelete IS NULL
LEFT JOIN dbo.hcmworker AS hw
    ON hw.recid = wct.worker
   AND hw.partition = wct.partition AND hw.IsDelete IS NULL
WHERE tst.IsDelete IS NULL;
