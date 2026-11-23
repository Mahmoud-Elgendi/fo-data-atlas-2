# F&O Data Atlas 0.5.2 — 23 November 2026

Developed by Mahmoud Elgendi. Building D365 F&O, Microsoft Fabric and AI-assisted SQL solutions.
Mobile / WhatsApp: 00966542128150. Website: https://www.mahmoudelgendi.com.

- Makes the existing Fabric Link / Synapse Link active-row rule explicit: qualified `IsDelete IS NULL`, preserving exact casing.
- Rejects `isdeleted = 0`, `IsDelete = 0`, `IsDelete = FALSE` and `COALESCE(IsDelete, 0) = 0` as substitutes. A missing expected column is a schema gap, not permission to invent a deletion field.
- Reinforces the rule in SQL review. For a right-side LEFT JOIN, the filter stays in ON or a filtered subquery to preserve unmatched driving rows.
- Retains financial dimension Value aliases, all eleven skills and the existing installer. Reuses unchanged v0.3.0 metadata assets and cached profiles.

This tools-only documentation/skill patch does not change source exports, generated tenant queries or the SQL linter implementation. Static checks and packaging do not establish live SQL correctness, native host adherence or F&O business reconciliation. Previous releases remain immutable.
