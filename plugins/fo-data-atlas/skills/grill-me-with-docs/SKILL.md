---
name: grill-me-with-docs
description: Discuss Atlas SQL requirements when the user accepts the discussion offer or explicitly requests an interview, asking one short question at a time and recording agreed decisions with evidence.
---

This is the portable Atlas discussion skill. It includes the interview and documentation workflow; no external grilling or domain-modeling skill is required.

1. Read the current request, prior answers and relevant project notes. Reuse established choices. State the intended result in one short sentence.
2. Ask one short question in simple English about the most consequential unresolved choice. Start with the business purpose and what one output row represents. Offer a recommendation with a short reason when useful. Wait for the answer before the next question.
3. Use installed Atlas metadata and, when connected and authorized, target schema evidence to investigate facts yourself. Distinguish verified evidence from proposals. Resolve fields, join scope, company, dates, amounts, enum text and deletion handling only as relevant to the task. Discuss concrete edge cases rather than sending a checklist of questions.
4. Record agreed requirements and evidence gaps in the dataset's `<name>.mapping.md`, or `docs/atlas/<task-name>.md` if no dataset exists. Separate decisions, assumptions and open questions. Update an existing note instead of creating duplicates. Use [the glossary skill](../fo-atlas-glossary/SKILL.md) when resolving a business term; add an ADR only for a consequential architecture decision. Keep credentials and live row values out of notes.
5. Once purpose, grain, requested fields and material calculation/join choices are clear, summarize the agreement briefly and continue the user's requested work. If the user requested discussion only, finish with the agreement and remaining questions. Respect a request to skip or stop the interview. Discussion alone does not authorize database changes.

This skill does not start the database connection interview again; the calling Atlas skill handles [session startup](../../references/session-start.md).
