# Review this update

Branch: codex/workflow-timesheet-pilot. Base: published-source commit 9e95d45. Status: prepared for review; not committed, pushed or released by the agent.

## Proposed change

Analyst requests can fail at the evidence boundary or use the wrong grain/key even when SQL looks plausible. This update routes retrieval through the installed package first, asks the short questions that affect row meaning, and makes target IDs, company casing and resource discriminators explicit. It supplies configurable examples rather than a recipient's literal working query.

- Workflow history template: next-event intervals, deterministic order and final NULL end.
- First-submission template: earliest event/user across instances, preserved timesheets, translated tracking type and worker identifiers.
- Reference guidance: target/schema/profile limits, output-name contracts and validation boundaries.
- Five synthetic logical fixtures plus 20 planned manual analyst acceptance scenarios.
- Publication wording corrected for the already-published v0.4.0 baseline.
- Source handover builder includes the new fixture file.

## Boundaries

No metadata payload/schema change; the metadata catalog and version manifests are unchanged. No live SQL outputs, actual employees/documents, endpoint configuration, credentials or local project settings are added. No main application workspace files are staged. The original exports and published release files are unchanged.

SQL templates contain required {{parameters}} and must be configured against the recipient's schema and evidence before use. They are authored examples with recipient runtime/business validation false. Normalized company expressions are conditional on evidence that casing is cosmetic. The raw wildcard follows the recipient Fabric table, not an unknown legacy view definition.

## Verification and remaining work

See [verification](VERIFICATION.md) and review-manifest.json. Current results: 63 plugin source tests passed, source-only package validation passed. The new SQLite fixtures execute template windows/join predicates with a narrow DATEADD adapter; they are not Fabric compilation tests.

After review, commit this branch as a focused development update. Before publishing, assign a new version and run clean-PC/private-download/native Codex and Claude activation checks. The manual 20-case plan is not recorded as passed. No broader self-service readiness or business reconciliation is asserted.
