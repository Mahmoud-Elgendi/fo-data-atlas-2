# Configurable timesheet first submission

One retained timesheet per row. Required parameters: timesheet_context_table_id, submission_tracking_type_code, utc_offset_hours and label_language_code. Resolve these from recipient schema/metadata and owner decisions before generating executable SQL. Index prefixes and another tenant's table IDs are insufficient. Company normalization assumes confirmed cosmetic case differences; adapt both ranking and joining if the actual key policy differs.

Rank confirmed Submission events across all retained workflow instances for the document. Select first timestamp, break ties by event RecId and retain the matching submitting user. Other tracking types are excluded. No submission means NULL DocId/StartTime/User/DurationDays; the timesheet survives. The resource path retains RefTableId/TableId and partition/company scope and preserves unmatched timesheets through LEFT JOINs. Output identifiers come from the matched worker, not an assumed timesheet worker value.

Output is Company, the actual Fabric tst.* expansion, then DocId, Tracking Type, StartTime, User, WorkerRecId, Personnelnumber, DurationDays, WeekFrom and WeekTo. This is not proof of a legacy view's hidden wildcard schema or DocumentId format. Retain the raw status codes in tst.*; the selected tracking code is translated using filtered target option metadata. Other status descriptions require a separately agreed output contract.

DurationDays follows calendar day boundaries, clamped at zero. Week columns deliberately retain YEAR/DATEPART(WEEK), not ISO week-year; session DATEFIRST affects week numbering. A fixed offset must match the owner's timezone policy. No employee names or dimension descriptions are included.

Portable authored template; no actual user, employee, document, endpoint or tenant-specific numeric ID is supplied. Runtime validated for recipient: false. Business reconciled: false. Checks: not run for recipient. Fixture tests cover selected logical invariants only.
