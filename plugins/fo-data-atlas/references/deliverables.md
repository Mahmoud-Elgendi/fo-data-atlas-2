# Dataset files

Choose a meaningful lowercase kebab-case business name. Place the three files together:

```text
datasets/purchase-order-lines/
    purchase-order-lines.sql
    purchase-order-lines.mapping.md
    purchase-order-lines.checks.sql
```

Use `vendor-invoice-lines` and `product-receipt-lines` for the other initial datasets. Add a meaningful scope suffix for intentionally different variants. Avoid generic filenames such as query.sql and silent overwrites.

The mapping document records:

- Business purpose; one-row meaning; unique identity and required scope.
- Confirmed field list, business aliases, exact target columns/types and source evidence IDs/hashes.
- Selected metadata snapshot IDs and target schema export identity.
- Complete joins and row-retention rules; repeated header amounts/non-additive measures.
- Unverified proposals, user approvals, missing metadata/columns and unsupported behavior.
- Check definitions, execution state and returned results. Initially: not run, runtime validated false, business reconciled false.

Validation SQL should expose failures rather than hide them: duplicate line identities, nonunique header/lookup keys, unmatched headers/codes, and before/after enrichment row counts. Compare appropriate amounts/quantities by company/currency/unit/time with F&O when actual evidence becomes available. Avoid fabricated totals or fixed numeric business assertions based only on metadata.

If target evidence or requested fields are missing, deliver a mapping with blockers and an explicitly non-executable SQL scaffold. Never present a guessed target query as ready to run. SQL filenames remain descriptive even for blocked drafts.
