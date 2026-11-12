-- TEMPLATE: resolve every {{parameter}} after recipient schema/evidence review.
-- Fixed-offset display policy must be confirmed; no universal timezone is assumed.
WITH WorkflowEvents AS (
    SELECT
        t.partition AS SourcePartition,
        t.recid AS WorkflowEventRecId,
        t.workflowtrackingstatustable AS WorkflowHistoryRecId,
        t.trackingtype AS TrackingTypeCode,
        ROW_NUMBER() OVER (
            PARTITION BY t.partition, t.workflowtrackingstatustable
            ORDER BY t.createddatetime, t.recid
        ) AS EventSequence,
        DATEADD(HOUR, {{utc_offset_hours}}, t.createddatetime) AS StartTime,
        LEAD(DATEADD(HOUR, {{utc_offset_hours}}, t.createddatetime)) OVER (
            PARTITION BY t.partition, t.workflowtrackingstatustable
            ORDER BY t.createddatetime, t.recid
        ) AS EndTime
    FROM dbo.workflowtrackingtable AS t
    WHERE t.IsDelete IS NULL
)
SELECT
    h.instancenumber AS [Instance Number],
    h.documenttype AS [Document Type],
    h.contextrecid AS [Document RecId],
    h.contexttableid AS [Context Table ID],
    e.WorkflowEventRecId,
    e.TrackingTypeCode,
    e.EventSequence,
    e.StartTime AS [Created Date Time],
    e.StartTime,
    e.EndTime,
    DATEDIFF_BIG(SECOND, e.StartTime, e.EndTime) AS DurationSeconds
FROM WorkflowEvents AS e
LEFT JOIN dbo.workflowtrackingstatustable AS h
    ON h.recid = e.WorkflowHistoryRecId
   AND h.partition = e.SourcePartition
   AND h.IsDelete IS NULL
WHERE h.contexttableid = {{timesheet_context_table_id}};
