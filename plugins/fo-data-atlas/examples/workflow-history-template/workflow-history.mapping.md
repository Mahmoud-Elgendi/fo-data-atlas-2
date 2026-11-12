# Configurable workflow event history

One retained event per row, scoped to linked timesheet instances. Required parameters: timesheet_context_table_id (recipient-confirmed F&O table ID) and utc_offset_hours (owner-confirmed fixed offset). Required physical columns and names must match the recipient schema CSV; preserve IsDelete casing.

Rows use all retained event types before LEAD. Ordering is createddatetime, recid within partition/workflow status reference. Last event end/duration is NULL. NULL/missing timestamps, purged events and replication lag need recipient review. The context filter excludes orphan events; diagnose those separately.

This is an authored portable template. The installed source catalog provides evidence leads, not universal target confirmation. No tenant ID, endpoint, actual employee or real document value is embedded. Runtime validated: false. Business reconciled: false. Checks: not run against the recipient. Static/fixture results do not change these flags.
