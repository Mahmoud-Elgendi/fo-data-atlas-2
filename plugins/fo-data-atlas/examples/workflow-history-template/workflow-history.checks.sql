-- TEMPLATE checks: review against the recipient before running.
SELECT t.partition, t.recid, COUNT_BIG(*) AS [RowCount]
FROM dbo.workflowtrackingtable AS t
WHERE t.IsDelete IS NULL
GROUP BY t.partition, t.recid
HAVING COUNT_BIG(*) > 1;

SELECT h.partition, h.recid, COUNT_BIG(*) AS [RowCount]
FROM dbo.workflowtrackingstatustable AS h
WHERE h.IsDelete IS NULL
GROUP BY h.partition, h.recid
HAVING COUNT_BIG(*) > 1;

SELECT t.partition, t.recid, t.workflowtrackingstatustable
FROM dbo.workflowtrackingtable AS t
LEFT JOIN dbo.workflowtrackingstatustable AS h
    ON h.recid = t.workflowtrackingstatustable
   AND h.partition = t.partition AND h.IsDelete IS NULL
WHERE t.IsDelete IS NULL AND h.recid IS NULL;
