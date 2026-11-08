# Offline reference snapshot

Original evidence is compressed losslessly in `atlas.sqlite`.
Use `scripts/atlas.py search` then `show` to read a hash-checked Markdown reference.
Use `show --raw --output <file>` to retrieve exact original bytes.

## Sources

- `application-20261019` — FO-Evidence-Snapshot-20261019-113929; manifest SHA256 `435c4e79b52b91d920c74db72f4513c31fb70601583dc1b1c498215e95ab01f9`. Declared application metadata; build/effective-extension/runtime completeness unconfirmed.
- `customer-analysis-references` — Customer-Analysis; manifest SHA256 `7927cbe9b6c721f81ac5eae215322f808ffb196ab4344f7185b37e59e0653e23`. Local exported/reference files. Snapshot compatibility and runtime correctness unconfirmed.
- `focused-application-20261018` — export; manifest SHA256 `e38dbdda1402163978bc76e7b0e37538786632bf8233bf1045a44120429de253`. Local exported/reference files. Snapshot compatibility and runtime correctness unconfirmed.
- `knowledge-20261020` — ms-learn-2026-10-20; manifest SHA256 `d745b8b4405b5cbca24f36da82553548087c2b567e805b7bfb0ba4376307a198`. Local exported/reference files. Snapshot compatibility and runtime correctness unconfirmed.
- `reviewed-knowledge-and-indexes` — Reviewed local knowledge and derived metadata; manifest SHA256 `593b38fefafeb5c258187d8fd6764da378e559667e5ab35f6549a0f4f03374fd`. Authored interpretations and derived indexes retain their source proofs; not independently runtime/business validated.
- `sql-application-capture-20261023` — live-sql-application-20261023-182402; manifest SHA256 `ddf18f0710d92109079b295d8c307d38ce43b6292e2e4c50ccb322bb4d7f8d8e`. Local exported/reference files. Snapshot compatibility and runtime correctness unconfirmed.
- `sql-application-catalog-20261023` — live49; manifest SHA256 `037bd4c1a64b0e2f2bc8a58b4c3d30e9bac7ce044cc7f0162dea97c2f483807b`. Derived SQL catalog snapshot. Original definitions retained; dependency edges are not joins. Target Fabric schema not established.
- `sql-edw-capture-20261023` — live-sql-20261023-edw; manifest SHA256 `fa9d6917961d95db1c14eaa96dad9716d6563846e275be525bc4ca156b690c70`. Local exported/reference files. Snapshot compatibility and runtime correctness unconfirmed.
- `sql-reference-catalog` — catalog; manifest SHA256 `5f10e66f433c246c68e282eb7e07ef28f4598e6c0f226e00ae7169d13ef3e107`. Derived SQL catalog snapshot. Original definitions retained; dependency edges are not joins. Target Fabric schema not established.
- `sql-reference-exports` — sql; manifest SHA256 `75a9e3ed1b5d2d29c52e67e85e44f844194869a731230f721b6d039ebd924134`. Local exported/reference files. Snapshot compatibility and runtime correctness unconfirmed.
- `sql-scope-capture-20261023` — live-sql-20261023-scope; manifest SHA256 `0f875871b87457adc7d309bfc9c1b54d980296b1d75f609a931e8a3d271ff4f8`. Local exported/reference files. Snapshot compatibility and runtime correctness unconfirmed.

## Coverage

```json
{
  "documents": 447389,
  "unique_contents": 395819,
  "sources": 11,
  "generated_utc": "2026-11-04T20:10:46.720929+00:00",
  "runtime_validated": false,
  "business_reconciled": false,
  "search_coverage": "Object names and bounded declared field/reference tokens, not exhaustive full-text or effective-extension merging.",
  "sqlite_sha256": "8a63169e90b0c2f76a95f08bcb726efbc1cfa8fbd48bf83cf6eba24e15c6ea18"
}
```
