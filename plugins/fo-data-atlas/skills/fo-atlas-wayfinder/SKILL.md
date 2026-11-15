---
name: fo-atlas-wayfinder
description: Plan a large, unclear F&O analytics or Fabric initiative spanning several datasets or sessions when the user requests architecture planning or a decision roadmap.
---

Use for a broad initiative, such as a procurement Gold layer, not for a single well-scoped SELECT. This skill plans decisions; it does not deploy or execute ETL.

1. Read existing requirements, glossary, dataset notes and architecture decisions. Establish the destination and the most consequential unknown with one short question at a time. Reuse answers already given. Keep the user's discussion-only boundary when present.
2. Create `docs/atlas/<initiative>-plan.md` with the business outcome, known constraints, current decisions and open decisions. Separate decisions from implementation tasks. For each open decision identify what it blocks, evidence needed and a sensible recommendation. Keep the map local; no issue tracker or external account is required.
3. Resolve the next blocking decision using [discussion](../grill-me-with-docs/SKILL.md) and [research](../fo-atlas-research/SKILL.md). Record accepted choices and their reasons. If architecture depends on current Fabric features, verify the relevant official documentation or installed architecture skill; state evidence gaps explicitly.
4. When a milestone is clear, define a small deliverable, dependencies and acceptance checks. An example is one reconciled PO-line dataset before all procurement facts. Keep cost, incremental/deletion semantics, historical versus current-rate reporting and maintenance choices visible only where relevant. Planning does not establish their correctness.
5. Finish with the next agreed implementation task and the remaining map. For a transfer, use [handoff](../fo-atlas-handoff/SKILL.md). Begin actual implementation only within the user's requested scope; discussion-only work ends with the plan.

Save an ADR for a consequential durable architecture choice, with context, decision, alternatives, evidence and consequences. Use [glossary](../fo-atlas-glossary/SKILL.md) for resolved business terms. Avoid creating a full planning framework for an ordinary query request.
