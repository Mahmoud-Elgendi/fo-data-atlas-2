---
name: fo-atlas-research
description: Investigate D365 F&O tables, joins, enums, view lineage or business calculations when evidence is missing or conflicts, and record findings before SQL is built.
---

Use the installed Atlas package as `PACK`. Follow [workflow routing](../../references/analyst-workflow.md) and reuse its current target and answers. Stay offline when offline work was selected.

1. Define the question and the smallest evidence needed to answer it. Inspect existing project notes and `python PACK/scripts/atlas.py context --project <project>` before investigating. A missing target schema does not block reading original exported SQL.
2. Search the installed references using `atlas.py sources`, `search` and `show`; follow [reference usage](../../references/reference-usage.md) for source selection, cache resolution and coverage. Keep source snapshots separate. For view definitions and dependencies, use [SQL lineage](../../references/sql-lineage.md) and offer underlying view SQL. Retrieve available evidence yourself rather than asking the analyst to name tables or enum codes.
3. When live target inspection is needed, follow [session startup](../../references/session-start.md) if no target choice exists. Use read-only schema inspection in the verified database for facts such as available columns. For Microsoft product behavior, use official documentation when browsing is available and permitted. Keep proprietary identifiers, business values and connection details out of external searches. Without web access, state which current product facts remain unchecked.
4. Compare original definitions, explicit relations, enum mappings and target schema. Classify findings as source-evidenced, target-observed, proposed/unverified or unknown. A dependency is not a join, a target column is not business validation, and an index name is not proof of a runtime F&O table ID. If Core lacks the original payload, offer Full under the metadata rules; preserve the gap until evidence is available.
5. Put concise findings in the existing `<dataset>.mapping.md`, or `docs/atlas/<topic>-research.md` for a standalone investigation. Record the question, source IDs/hashes or official links, relevant predicates, contradictions, conclusion and remaining checks. Quote only the necessary evidence. Link large original SQL files rather than duplicating them across notes. Do not publish live result rows or credentials.

Finish when the question is supported by identifiable evidence or the precise missing evidence is documented. Return the conclusion and its practical limits, then resume the calling task. Do not turn a proposed answer into a verified fact because the user approved using it.
