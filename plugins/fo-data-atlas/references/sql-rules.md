# Mandatory SQL rules

Apply these rules to proposed analytical SQL. Keep extracted source definitions byte-preserved; style rules never rewrite original evidence.

## Names and scope

- UPPERCASE SQL keywords and functions. Lowercase physical schemas, tables and columns, checking exact target spelling against the Fabric schema CSV.
- Exception: the column `IsDelete` retains exactly that casing. Use `IsDelete IS NULL` for every Fabric Link / Synapse Link source table that has it. Check presence; never add nonexistent columns.
- Never substitute `isdeleted = 0`, `IsDelete = 0`, `IsDelete = FALSE` or `COALESCE(IsDelete, 0) = 0` for `IsDelete IS NULL`. The active-row rule is NULL, not a Boolean zero test. If the expected column is absent, report the schema gap instead of inventing a replacement deletion field or predicate.
- Explicit schema-confirmed exception: dbo.GlobalOptionsetMetadata and its exported OptionSetName, Option, IsUserLocalizedLabel, LocalizedLabelLanguageCode, LocalizedLabel, GlobalOptionSetName, EntityName and ExternalValue retain their exact case. The linter permits these only when present exactly in the target CSV. Further exceptions must be explicit identifier_case_exceptions in project.json and passed with --project; they never permit nonexistent identifiers.
- If a target deletion column has another casing, pause to resolve the conflict instead of silently skipping deletion filtering or emitting an identifier that does not exist.
- Keep output aliases in business casing. Prefer suitable exported entity field names. If none fit the meaning, propose a name and identify it as authored. Preserve the alias-to-source mapping.
- Financial dimension values use PascalCase aliases ending in `Value`, such as `UnitValue`, rather than a `Dim` prefix. Follow the complete [dimension alias convention](financial-dimensions-and-currency.md); source field names stay unchanged and must exist in the target.
- Company output is `UPPER(dataareaid) AS Company`, qualifying the physical field when needed. All legal entities are included by default for the three initial purchase datasets; company filtering is optional.
- Shared tables may have no company column. Establish company, Partition, source/environment and other required key predicates from evidence and actual target columns. Formatting Company does not justify normalizing join keys.
- If actual key samples establish mixed-case spellings of the same company, document the evidence and normalize both the join and window-partition company expressions consistently. Check cardinality and independently selected results afterward. Case normalization is a target-specific decision, not a universal rule for every identifier.
- F&O table IDs, SQL Server object_id and document RecId are different identifiers. An index-name prefix is only an unverified table-ID lead. Confirm the recipient's context table ID from explicit target metadata or an authorized read-only check of the replicated tableid column before using a numeric filter.
- For exact output-name requests, preserve explicitly provided names/order. A legacy view's SELECT * does not reveal its expanded schema or computed key formats. Ask once for headers; if the owner chooses the Fabric raw wildcard instead, document that contract and avoid claiming legacy schema parity. Implement only the requested enrichments.

## Rows and joins

- Full-load SELECT queries only. Preserve the declared row grain and retained line identity. ETL pipelines, incrementals and deletion/change tracking are deferred.
- The three purchase datasets start with lines and LEFT JOIN the corresponding header. Headers without lines are excluded; unmatched lines survive and have a diagnostic.
- Put deletion filters for right-side LEFT JOIN sources inside their filtered subquery or ON condition. Apply driving-table deletion filters in its subquery or WHERE.
- Read complete declared constraints and code-supported predicates before proposing joins. Composite/fixed/date/company constraints must remain visible. Extensions are separate evidence until effective behavior is established.
- Record unverified joins in `<name>.mapping.md`. Include them in `<name>.sql` only after user approval, retaining their unverified label and checks.
- Check uniqueness on the joined side; a LEFT JOIN can still multiply rows. Classify repeated header amounts as non-additive at line grain.
- Preserve polymorphic discriminators such as RefTableId/TableId together with RefRecId/RecId and required partition/company scope. A coincidental RecId match does not establish the referenced object type.

## Status labels

Keep both code and text. Prefer GlobalOptionsetMetadata.LocalizedLabel in English (1033), with optional COALESCE(m.LocalizedLabel, m.ExternalValue), checking the actual target's spelling.

Use a filtered SELECT subquery with the correct `entityname`, `optionsetname` and `localizedlabellanguagecode`. Join its `[option]` to the actual stored code. Confirm table/column existence and spelling from the target export. Check uniqueness per filtered option and keep unmatched driving rows. Exported enum XML supplies supporting references; numeric values and translations are never guessed.

Illustrative lookup shape only, not a complete executable dataset:

```sql
LEFT JOIN (
    SELECT
        m.[Option] AS StatusCode,
        COALESCE(m.LocalizedLabel, m.ExternalValue) AS StatusLabel
    FROM dbo.GlobalOptionsetMetadata AS m
    WHERE m.EntityName = 'purchtable'
      AND m.OptionSetName = 'documentstatus'
      AND m.LocalizedLabelLanguageCode = 1033
    -- Add m.IsDelete IS NULL here if this source has that column.
) AS documentstatus
    ON documentstatus.StatusCode = header.documentstatus
```

`StatusCode` and `StatusLabel` above are output aliases of the derived table. The supplied documentstatus example proves no other field's lookup. COALESCE handles NULL, not empty text; handle empty text only when explicitly required.

## Validation and delivery

- Confirm fields before drafting SQL. Missing requested target fields require a user decision.
- Deliver descriptively named SQL, mapping and checks files. Label source-supported facts, authored proposals and actual validation results separately.
- The assistant generates SQL without executing it. Checks begin as not run; runtime/business validation remains false until results support it. Approval, metadata coverage and fixture tests do not establish reconciled business totals.
- A bounded linter may request manual CTE review even when physical references pass. Record the warning and its review; a linter flag is neither Fabric compilation nor a substitute for target validation. Quote keyword-like aliases, for example [RowCount].
