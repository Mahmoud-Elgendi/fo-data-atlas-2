# Core, Full offline and the shared metadata cache

Version 0.3 separates the small plugin tools from immutable metadata assets. Setup asks which AI tool, global/project scope, then Core (default) or Full offline. A matching verified cache is reused instead of downloading unchanged metadata. Skills and metadata have separate identities; an unchanged baseline can be used across compatible tool releases.

## Coverage

Both profiles retain all 447,389 current object identities, source IDs, original paths/hashes and all-object name discovery. Core includes the complete exported SQL_OBJECT catalogs (definitions, columns, dependencies), table/view/entity/EDT/enum XML and English label resources, plus small reference/manifest content. Original document IDs and hash checks remain unchanged.

The built Core contains 204,438 readable document identities (182,328 distinct payload hashes); identical content may make additional paths readable through global deduplication. Other objects remain discoverable with available_offline = 0. Core does not index the missing documents' field/method text. A missing Core search result does not establish absence from the full baseline.

Full contains all 447,389 original document identities and 395,819 unique payloads, including classes, forms, reports and other languages. Both preserve original evidence; neither establishes effective extension merging, runtime behavior or Fabric compatibility. No newly collected .49 evidence has replaced this baseline.

Measured initial downloads: Core 318,513,889 bytes (303.8 MiB), Full 1,301,733,130 bytes (1.21 GiB). Tool ZIP size is recorded by its release build. The Core database occupies 611,340,288 bytes locally; Full uses the unchanged 1,742,393,344-byte database. Profiles are alternative active views of the same baseline, not cumulative overlay databases. Keeping both profiles retains both cache files; no old evidence is deleted automatically.

## Using the installed profile

Run `python PACK/scripts/metadata_cache.py status` to inspect the active baseline/profile and coverage. `atlas.py search` marks each result's available_offline status. `atlas.py show` reports when the original payload needs Full; it does not invent a substitute definition.

When a question needs an uncached original, ask one short question before downloading Full. On acceptance use `python PACK/scripts/metadata_cache.py install --profile full`. This acquires/verifies Full if needed, atomically updates the installed plugin's reference-pack.json, and leaves old cache entries intact. It does not change a project's explicit reference_pack override; update such an override only at the owner's request.

Uncached evidence requires internet. Previously cached profiles work offline. Explicit local seed: add `--local-pack PACK_ROOT` when setup/acquisition can reuse a matching local database. The entire source DB hash must match the selected profile; an existing 0.2.0 full package can seed Full. Core can be seeded from its built/extracted pack. Wrong/partial/corrupt cache entries are rejected, not silently trusted.

## Storage and release contract

Cache default: USERPROFILE/.fo-data-atlas/metadata/<baseline>/<profile>-<hash>/. Each installed tools copy stores a small reference-pack.json pointer. Project/global registration scopes stay as selected; shared cache storage does not overwrite project schemas, rules, queries or selected source IDs. The pointer identifies the profile and exact metadata hash.

metadata-catalog.json records the metadata release tag, asset names, sizes and SHA256 values for both profiles. Metadata archives contain only references/atlas.sqlite and references/manifest.json. A new tools-only release must reuse the same catalog/tag/hashes to reuse unchanged metadata; do not rebuild/relabel metadata just for code changes. New baselines get new identities. If a cache folder is moved/deleted, setup must repair the missing path before querying.

Tools and metadata download staging use extended Windows paths. SHA256 is verified before promotion/activation. Old 0.2.0 releases remain unchanged; 0.3 contains the downloader extraction fix. Native host loading and real private GitHub transfer remain separately recorded checks.
