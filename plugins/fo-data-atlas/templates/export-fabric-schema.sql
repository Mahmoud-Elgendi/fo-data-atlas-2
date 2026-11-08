-- Run manually in the target Fabric Warehouse; save results as fabric-schema.csv.
-- Metadata only. No source data is read or changed.
-- Catalog reference: https://learn.microsoft.com/sql/relational-databases/system-catalog-views/sys-columns-transact-sql
-- Results reflect metadata visible to your Fabric identity; this script has not been run in your tenant.
SELECT
    s.name AS schema_name,
    t.name AS table_name,
    c.name AS column_name,
    ty.name AS data_type,
    c.column_id AS ordinal_position,
    c.max_length AS max_length,
    c.precision AS numeric_precision,
    c.scale AS numeric_scale,
    c.is_nullable AS is_nullable
FROM sys.tables AS t
INNER JOIN sys.schemas AS s
    ON s.schema_id = t.schema_id
INNER JOIN sys.columns AS c
    ON c.object_id = t.object_id
INNER JOIN sys.types AS ty
    ON ty.user_type_id = c.user_type_id
UNION ALL
SELECT
    s.name AS schema_name,
    v.name AS table_name,
    c.name AS column_name,
    ty.name AS data_type,
    c.column_id AS ordinal_position,
    c.max_length AS max_length,
    c.precision AS numeric_precision,
    c.scale AS numeric_scale,
    c.is_nullable AS is_nullable
FROM sys.views AS v
INNER JOIN sys.schemas AS s
    ON s.schema_id = v.schema_id
INNER JOIN sys.columns AS c
    ON c.object_id = v.object_id
INNER JOIN sys.types AS ty
    ON ty.user_type_id = c.user_type_id
ORDER BY schema_name, table_name, ordinal_position;
