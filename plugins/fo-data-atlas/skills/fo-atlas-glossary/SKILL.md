---
name: fo-atlas-glossary
description: Resolve ambiguous F&O business terms during Atlas discussion or SQL design and maintain a project glossary with evidence and agreed meanings.
---

1. Read the existing project `GLOSSARY.md`, agreed dataset notes and relevant installed evidence. Reuse established vocabulary. Identify only ambiguities that change interpretation: for example local currency versus reporting currency, receipt versus invoice, workflow instance versus event, or first versus latest submission.
2. Find factual definitions through [research](../fo-atlas-research/SKILL.md). Ask the analyst one short question when a project/business choice remains. Offer a concrete example that exposes the difference. Label a proposed definition until it is agreed.
3. Add or update only resolved terms in `GLOSSARY.md` with term, plain-English meaning, scope and evidence/decision reference. Distinguish standard F&O behavior from this organization's chosen meaning. Preserve the original F&O names alongside business terms; keep tenant-specific choices in the project, outside the plugin corpus.
4. Keep implementation details, SQL and temporary investigation notes in the dataset mapping or research note. If new evidence contradicts an established term, explain the consequence and resolve it before replacing the definition. Identify affected dataset notes rather than silently rewriting unrelated queries.

Finish with the terms changed and any consequential disagreement still open. A glossary is shared language, not permission to change database objects or a substitute for source evidence. Create it only when there is a resolved term to record.
