# Release actions — 12 November 2026

User approved preparing, testing and publishing v0.4.1. Started from the merged source of PR #4 on codex/release-0.4.0 and created codex/release-0.4.1. Aligned version manifests and installation instructions, preserving the metadata catalog and prior release files. This is a tools-only update; no live queries or global host settings are required for packaging.

Verification commands and actual outputs are retained in local test-evidence for this release. The final delivery manifest records archive hashes, publication readback and private-transfer smoke results. A source commit/tag or this plan alone does not establish that a release has been published or that a host has loaded the plugin.

Prepublication verification passed: 63 source tests; source-only package validation; archive checksum/extraction; unchanged metadata catalog; cached Core installation with network disabled; installed offline metadata search; template presence; no metadata database copied into the project tools; local npm package launcher help. Tools ZIP: 455306 bytes, SHA256 97d8534698a0ce0ed58e11ce2ce5261896a62eeebab5879bea9bf4900e59c885. Native host loading, clean second-PC acceptance and F&O business reconciliation remain unverified.
