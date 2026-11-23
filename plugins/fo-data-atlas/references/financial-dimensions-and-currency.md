# Dimensions and currency conventions

## Financial dimensions

Use PascalCase output aliases ending in `Value` for financial dimension values. Preserve the business dimension name and remove the `Dim` prefix. This is the owner's naming convention for generated analytical SQL, independent of the physical source identifier:

| Physical field, when verified in the target | Output alias |
| --- | --- |
| departmentvalue | DepartmentValue |
| sectionvalue | SectionValue |
| subsectionvalue | SubsectionValue |
| unitvalue | UnitValue |
| unitgroupvalue | UnitGroupValue |
| costcentervalue | CostCenterValue |
| projectvalue | ProjectValue |

For example, use `dim.unitvalue AS UnitValue` instead of `dim.unitvalue AS DimUnit`. Apply this convention across datasets and any derived tables that expose these values. Distinguish a value/code from its description; a description is not a `Value` column. For additional dimensions, use the verified business name plus `Value`, confirming ambiguous word casing rather than inventing a field. The table above is an alias policy, not evidence that all these columns exist in every tenant.

For an alias-only change, preserve source fields, joins, filters, calculations, output order and unrelated aliases, including the existing dimension identity alias. Update dependent SQL/checks/mapping references when they use a renamed alias. Preserve original exported definitions unchanged; apply these aliases to authored analytical output only. Explicit user-required legacy output names override the default and should be recorded in the dataset mapping.

For purchase datasets include the stored DefaultDimension identity and requested dimension values. Use the line/document's own stored dimension reference; a posted receipt must not silently inherit today's PO dimensions. The reviewed target stores unitgroupvalue, unitvalue, departmentvalue, sectionvalue and projectvalue on dimensionattributevalueset; these tenant columns are not assumed universal.

Verify exact field presence and RecId/Partition join evidence. Use LEFT JOIN and keep the dimension IsDelete predicate in ON so a missing dimension does not remove a line. Report NULL/zero dimension identity separately from a nonzero identity with no matching row. For a different schema propose an evidenced alternative or label the gap; do not invent dimension columns.

## Transaction, posted and current-rate amounts

Keep original transaction currency/amounts. A stored posted accounting amount is separately sourced; multiplying by today's rate does not reproduce it. Preserve each source field's price quantity, discount meaning, quantity unit and currency. Repeated PO values across receipt rows may be non-additive.

The owner's reference policy uses exchangeratecurrencypair + exchangerate + exchangeratetype, joins their RecId/Partition, filters each available IsDelete column, chooses exchangeratetype.name = 'Default' and exchangerate.validto > GETDATE(), and divides exchangerate by 100.0 except SAR uses 1.0. Join the resulting factor by transaction fromcurrencycode. This is the owner's current SAR reporting convention, not a universal rate rule, historical posting rate or discovery of every company's local currency.

Retain the explicit owner-approved direct join, but check duplicate rate rows per currency before using it. Do not silently choose MAX, ROW_NUMBER, inverse or triangulated rates. The approved example falls back to 1.0 for missing/zero rates using COALESCE(NULLIF(rate, 0), 1.0); disclose and diagnose fallback use, since it can mask missing conversions. A shared view may replace repeated logic only when its target existence/output contract is verified.

PO example: NULL inputs become 0.0 in the derived current-rate calculation, as requested. Receipt example: NULL native receipt amounts remain NULL in derived LCY and have a diagnostic. Preserve these distinctions instead of applying one generic COALESCE to every amount.

The receipt example's lineamount_w/currencycode_w population was accepted by the owner on one sample; regional source metadata and broader company/configuration coverage remain unresolved. Stored valuemst is kept as an independent accounting amount. Do not treat the current receipt amount fields as universally validated for all F&O environments.

Future DWH design keeps stored transaction/posted amounts and can calculate current-rate values in a reporting view. This plugin release generates SQL and evidence only; it does not deploy incremental pipelines or rewrite historical facts.
