---
name: fo-atlas-diagnose
description: Diagnose duplicate or missing rows, incorrect amounts, timestamps, enum labels or slow Fabric SQL with a small reproducible check before changing the query.
---

Reuse the target and agreed requirements under [workflow routing](../../references/analyst-workflow.md). Follow [session startup](../../references/session-start.md) only when its target choice is missing or changes. Read [SQL conventions](../../references/sql-rules.md).

1. Establish expected versus observed behavior with one short question if missing. Record the query revision, intended grain and a narrow sample filter. Preserve the original query. Without live access, work from supplied SQL and redacted results; mark proposed probes as not run.
2. Create the smallest read-only check that demonstrates the symptom. For duplicates or missing rows, compare base row identity/count with each join in sequence; check join-key uniqueness, company/partition scope, polymorphic table discriminators, deleted rows and WHERE predicates that remove LEFT JOIN rows. Use an agreed sample or time/company filter to bound scans.
3. For monetary discrepancies, check quantities, price units, signs, transaction/posted/local currency meanings, rate direction and duplicate rate matches before changing formulas. Read [financial conventions](../../references/financial-dimensions-and-currency.md). For dates or missing workflow events, check time zone, event grain, partition keys and ordering before applying filters. For labels, check entity, option set, language and duplicate matches. Treat these as relevant branches, not a questionnaire for every issue.
4. Form one evidence-backed hypothesis and test it with the next smallest probe. Keep changing one relevant factor at a time. For slow SQL, start with available plans/query diagnostics and filter/join behavior; do not launch an unbounded production benchmark or alter capacity, indexes or physical objects as part of diagnosis.
5. Fix the proven cause within the requested scope. Retain the failing scenario as a read-only check in `<dataset>.checks.sql`, or an appropriate automated test when a helper was wrong. Compare the same sample before and after; check the intended grain and important totals. A local fixture is not F&O business reconciliation.
6. Record cause, evidence, change, executed checks and remaining limitations in `<dataset>.mapping.md`. If blocked, identify the missing permission/data/tool and offer the next concrete check. Never report a guessed cause or an unexecuted fix as verified.

Before delivery, use [SQL review](../fo-atlas-review/SKILL.md). Do not mask fanout with DISTINCT, arbitrary TOP or aggregation unless the agreed dataset grain requires that operation.
