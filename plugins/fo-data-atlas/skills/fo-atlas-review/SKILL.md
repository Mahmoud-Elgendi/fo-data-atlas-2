---
name: fo-atlas-review
description: Review new or changed Atlas analytical SQL before delivery, or review a supplied query against business requirements, F&O evidence and Fabric SQL conventions.
---

Use the supplied query and its existing mapping/checks. A static review can run offline; live execution is separate under [session startup](../../references/session-start.md). Read [SQL conventions](../../references/sql-rules.md), [deliverables](../../references/deliverables.md) and relevant source evidence. Use [research](../fo-atlas-research/SKILL.md) to resolve a specific evidence gap rather than filling it by intuition.

Review two distinct questions:

1. **Does the query meet the agreement?** Confirm purpose, row grain, selected fields/aliases and order when required, company/date scope, first/latest/current/posted semantics, filters and expected treatment of missing matches. Preserve previously agreed logic during naming-only work. Check the query against explicit requirements; do not invent a new business rule.
2. **Is its implementation supported?** Verify composite joins and partitions, company keys, polymorphic discriminators, join multiplicity and outer-join filters. Check Link deletion filters with exact `IsDelete` casing, enum entity/field/language scope and label uniqueness, currency direction/scaling/cardinality, dimension evidence, null/zero behavior, time-zone conversion, deterministic window order and numeric precision. Read [financial conventions](../../references/financial-dimensions-and-currency.md) or [workflow guidance](../../references/workflow-and-timesheets.md) only for those branches. Flag unsupported joins as unverified.

Run `python PACK/scripts/lint_sql.py <dataset>.sql --schema <csv>` when the project CSV exists, adding relevant company/Link flags from the SQL rules. Without a CSV, identify which target-column checks were not performed and use available live schema evidence if authorized. Static linter success is not SQL compilation or business validation.

Ensure `<dataset>.checks.sql` covers identity, fanout, missing matches, label/rate duplicates and material calculations as applicable. Execute bounded read-only checks only when the task authorizes live validation and the target is verified. Classify each check as passed, failed or not run; retain exact scope and evidence. If result mismatches need investigation, use [diagnosis](../fo-atlas-diagnose/SKILL.md) for that issue, then return here; avoid recursive reviews of the same unchanged SQL.

Write review findings in the existing mapping document with the affected field/join, consequence and concrete correction. Label delivery **ready for target testing**, **checks passed within the stated scope**, or **blocked by listed findings**. Never infer business reconciliation from successful compilation, and never hide unresolved findings behind an overall passed label. For review-only requests, report findings before changing SQL; if no material findings exist, say so and list validation limits briefly.
