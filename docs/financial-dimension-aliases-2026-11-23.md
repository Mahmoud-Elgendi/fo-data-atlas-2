# Financial dimension value aliases

On 23 November 2026 the owner requested UnitValue rather than DimUnit, and the equivalent convention for other financial dimensions. Updated the authoritative financial-dimensions-and-currency reference with the seven aliases supplied in the query, plus a pointer from the mandatory SQL rules. Lowercase physical columns remain unchanged. Existing PO/receipt example SQL already uses UnitValue, UnitGroupValue, DepartmentValue, SectionValue and ProjectValue and needed no rewrite.

The supplied query was copied to the main workspace's local test-evidence/financial-dimension-aliases/purchase-order-header.sql with only the seven Dim-prefixed aliases changed. The source attachment remains untouched; tenant-specific SQL was not added to the distributable plugin. Joins, fields, calculations, filters, column order and DefaultLedgerDimension are unchanged. Presence/meaning of the supplied tenant fields is not newly validated by this naming edit.

Checks: exact replacement comparison and source-only package validation. No live database connection, SQL execution, schema validation or F&O business reconciliation is claimed. This source convention change is not a new published plugin release; existing installations keep their installed rules until updated.
