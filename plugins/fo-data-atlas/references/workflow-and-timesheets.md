# Workflow history and timesheet submissions

Read this for workflow-event intervals, first-submission dates, timesheet worker identifiers or legacy output-name matching. Retrieve evidence using the installed atlas.py and the project's selected sources. Source leads are WorkflowTrackingTable, WorkflowTrackingStatusTable, WorkflowTrackingType, ResResourceIdentifier, WrkCtrTable and HcmWorker. Read their actual fields/relations; the leads are not a new target's validation.

## Choose the row meaning

- Event history: one retained tracking event per row. Its start is that event timestamp; its end is the next retained event in the same workflow instance. Keep all intended events before applying LEAD. Filter a display preview after window evaluation. The final event has NULL end/duration, including completed instances. This measures time between log events, not necessarily an approver's processing time.
- First submission: one timesheet per row. Rank only the confirmed Submission event type across all workflow instances of the same document. Partition by source partition, company, context table and document RecId. Pick the first timestamp, break ties by event RecId and retain the user from that selected event. Creation, Resubmission and SubmitOnBehalf are distinct event types; include them only if the agreed definition calls for them.

Submission/event timestamps are not SinkModifiedOn replication watermarks. Apply an owner-selected timezone policy to display timestamps; the templates take an explicit UTC offset. An offset is suitable for a fixed-offset policy; seasonal timezones require a separately designed conversion. DATEDIFF_BIG(SECOND) counts second boundaries, not fractional seconds. Calendar-day lateness and elapsed seconds are different measures.

## Configure before generating SQL

Templates live in [workflow history](../examples/workflow-history-template/workflow-history.sql) and [first submission](../examples/timesheet-first-submission-template/timesheet-first-submission.sql), each with mapping/checks. Copy them into a descriptively named recipient dataset, resolve every {{parameter}} using verified target evidence and the owner's decisions, and run the ordinary schema/lint/manual review. Unresolved tokens mean a template is not ready to run. Do not execute the packaged templates directly.

Resolve timesheet_context_table_id in the recipient environment. A SQL Server object_id or an index prefix from another snapshot is not proof. Confirm submission_tracking_type_code against exported enum evidence and target GlobalOptionsetMetadata where available. Use filtered English label subqueries and optional ExternalValue fallback; check uniqueness before enrichment.

The first-submission template demonstrates normalized company matching, conditional on evidence that casing is cosmetic. Apply the same normalization to ranking and joining; normalizing output alone leaves a case-sensitive join unresolved. If the target uses meaningful case distinctions, replace all corresponding expressions with its verified key policy.

The worker path follows timesheet.resource -> resource identifier -> work centre -> worker. Preserve both RefRecId/RecId and RefTableId/TableId, partition scope and the relevant legal entity. Use the matched HcmWorker for WorkerRecId/Personnelnumber; the timesheet's own worker field may have different coverage. Keep missing enrichments visible and count them. Employee names and dimension descriptions are separate mappings with temporal semantics, not mere aliases for worker identifiers.

## Preserve the requested output contract

For a naming-only change, keep established row selection, filters and calculations. Freeze the actual output headers after target validation. A Fabric tst.* projection includes that Fabric table's fields and may differ from an old Jet view's wildcard. Do not invent an old DocumentId concatenation format or claim exact column/type parity without its definition/headers. Add only requested worker/description fields; preserve numeric codes when translating labels unless the owner explicitly chooses another contract.

## Validation scope

Compare base/enriched row counts, duplicate keys, unmatched labels/headers/workers and first-submission choices against an independently grouped MIN. Test a document with multiple submissions and mixed company casing, not only a single-event happy path. For event intervals, compare separately selected raw UTC timestamps, ordering, next-event boundaries, timezone conversion and final NULLs. Keep tenant credentials, endpoint details, actual users, document identifiers and live query output in the recipient project, outside reusable package examples.

Package fixtures establish selected logical invariants only. Native host loading, recipient SQL compilation, live data checks and F&O business reconciliation are separate outcomes. See [analyst acceptance scenarios](analyst-acceptance.md) for the private pilot checklist.
