---
name: fo-atlas-handoff
description: Save an Atlas task for another chat, agent, device or analyst with agreed requirements, evidence, files, validation status and next actions.
---

Read the current conversation and project notes. Create or update `docs/atlas/<task>-handoff.md` when the user asks to pause, transfer or summarize the work for continuation.

Include:

- The requested outcome, intended row grain and agreed fields, calculations, filters and naming.
- Completed work, relevant file paths relative to the project and the source revision if available. Check that referenced files exist; label proposed files explicitly. Identify the active plugin version and selected metadata source IDs/profile when known.
- Evidence-backed decisions, unresolved questions and assumptions. Link mapping/research/glossary notes instead of copying large definitions.
- Validation separately for static review/lint, target compilation, executed result checks and F&O business reconciliation. Record not-run checks as not run and limit claims to their actual sample/scope.
- The next concrete actions, missing tools or permissions, and how the next agent should locate this package and resume through [workflow routing](../../references/analyst-workflow.md).

Keep passwords, tokens, authentication codes, raw business rows, employee names and private connection strings out of the handoff. Refer to the target as a project alias by default; include an endpoint/database only in local project notes if the user explicitly wants those details carried. Authentication and connection verification must be repeated on a new device; an old successful probe is historical evidence, not a live session.

Show the handoff path and one short resume prompt. Saving a file does not send it to another person or prove that another device has the project/metadata. Never send messages or publish the handoff without an explicit request.
