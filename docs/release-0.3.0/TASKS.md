# 0.3.0 checklist

- [x] Owner accepts Core default, shared cache and Full offline alternative.
- [x] Reproduce the actual 0.2 long-path extraction error before the fix; verify the real archive afterward.
- [x] Build immutable Core/Full assets from current evidence, preserving original IDs/hashes.
- [x] Keep all identities discoverable and mark unavailable payloads explicitly.
- [x] Implement verified cache reuse, local seeding, atomic profile activation and independent tools packaging.
- [x] Integrate setup/profile choices and installed metadata resolution; preserve project schemas/source selection.
- [x] Regression checks for core/full coverage, cache reuse across upgrades/projects, corrupt cache rejection, cancellation and small tools archives.
- [x] Initial full project regression: 181 tests PASS. Focused Atlas suites: 51 PASS.
- [x] Final tools ZIP and hashes; source handover verified separately (56 tests) and recorded in delivery manifest.
- [x] Real-sized Core ZIP -> shared cache -> two project installs -> installed offline SQL lookup, plus local Full/profile-switch smoke.
- [x] Final checks: 186 project tests, 56 focused plugin tests, 8 formatter checks; metadata/manifest/skill validation.
- [ ] Source commit/tag and new 0.3.0 draft/assets; preserve 0.2.0.
- [ ] Publish and verify real private download using the new bootstrap.
- [ ] Native Codex/Claude activation recorded separately.

Commands and outcomes belong in ACTIONS.md. A local build is not a published release; source metadata completeness is not runtime/business validation.
