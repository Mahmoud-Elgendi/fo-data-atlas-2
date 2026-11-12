# 0.4.1 release checks

- Source base: merged workflow/timesheet pilot PR #4.
- Version identities: package.json, tools launcher manifest and both host manifests set to 0.4.1.
- Metadata: reuse v0.3.0 catalog/assets; compare unchanged bytes before publication.
- Run source tests and package source-only validation.
- Build and verify actual tools ZIP; smoke-test package executable.
- Push versioned source/tag, upload/verify draft assets, publish and read back.
- Verify actual private download and npx command; record observed limits.

Execution evidence is recorded in the local delivery manifest, not assumed from this checklist. Native Codex/Claude loading and a clean second PC remain manual acceptance scenarios until observed. No new recipient runtime/business validation is implied by this release.
