# F&O Data Atlas 0.5.1 — 23 November 2026

Developed by Mahmoud Elgendi. Building D365 F&O, Microsoft Fabric and AI-assisted SQL solutions.
Mobile / WhatsApp: 00966542128150. Website: https://www.mahmoudelgendi.com.

- Standardizes authored financial dimension aliases: DepartmentValue, SectionValue, SubsectionValue, UnitValue, UnitGroupValue, CostCenterValue and ProjectValue, replacing the Dim prefix by default.
- Applies the convention through the mandatory SQL rules and the shared financial dimension reference. The alias list does not imply those fields exist in every tenant; target evidence is still required.
- Alias-only edits preserve joins, physical fields, filters, calculations, order and unrelated names. Original exports remain unchanged. Explicit required legacy names remain supported with a documented mapping.
- Retains the eleven analyst skills, optional connection/discussion flow, developer branding and offline installation route from 0.5.0.
- Reuses the unchanged v0.3.0 metadata catalog/assets and verified shared cache. No metadata rebuild or re-download is required for an already cached matching profile.

The user's tenant-specific query and attachment are excluded from the distributable package. No query execution, live connection or F&O business reconciliation is implied by this naming change. Earlier releases remain immutable.
