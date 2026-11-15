# Analyst supporting skills

Date: 15 November 2026. Status: implemented in the plugin-only checkout on main; not committed, pushed, published or activated. This work includes the earlier unpublished database/discussion flow. Previously published v0.4.1 and installed copies remain unchanged. Assign a new version before release; local smoke archives carrying the current source version are candidates only.

## Delivered

Eight authored Atlas skills: fo-atlas-research, fo-atlas-diagnose, fo-atlas-review, fo-atlas-glossary, fo-atlas-handoff, fo-atlas-wizard, fo-atlas-wayfinder and fo-atlas-find-skills. They accompany fo-atlas-query, fo-atlas-setup and grill-me-with-docs, giving eleven packaged skills. No third-party skill installation or new runtime dependency was added.

The shared routing reference is plugins/fo-data-atlas/references/analyst-workflow.md. Query work uses diagnosis for reported mismatches, research for conflicting/complex evidence and review before analytical SQL delivery. Discussion uses the glossary for resolved terms. Setup uses the wizard when guidance is needed. Handoff, Wayfinder and external discovery are optional. Skills reuse known target/requirements and keep explicit read-only/offline/installation boundaries.

Research retains source identities and evidence gaps. Diagnosis compares row grain and joins before changing SQL. Review separates requirements from implementation evidence and static checks from live validation. Handoff avoids credentials and raw business values. The wizard distinguishes the user's other device from the executing host. Discovery checks existing capabilities first and requests a choice before installing external code. Wayfinder saves local decisions without requiring an issue tracker.

## Verification

- Python source regression: 67 tests passed in 4.995 seconds. These cover existing package/helpers, including the earlier connection probe boundaries; they are not an evaluation of LLM adherence to the new prose skills.
- Source-only package validation passed with eleven skill identities and valid local links.
- Whitespace check passed with the repository's CR-at-EOL convention.
- Tools archive smoke build and inventory check are recorded in the main workspace's local test-evidence/aw1. An initial staging attempt beneath the deeply nested checkout hit Windows path length limits on an existing long example filename; staging under the shorter workspace path succeeded. No offline metadata corpus was rebuilt or copied into the tools archive.
- Native Codex/Claude discovery, invocation, routing and interview behavior remain untested. No live SQL or F&O reconciliation was run in this change.

## Manual acceptance to run through the installed candidate

| Request/scenario | Expected behavior | Observed status |
| --- | --- | --- |
| Show original exported view SQL offline | Retrieve original and dependencies; no full analytical review | Not run |
| Create PO lines with already agreed fields | Reuse fields; evidence, build, focused review, named outputs | Not run |
| PO amounts doubled after a join | Establish reproducer and grain; inspect join multiplicity before a fix | Not run |
| Research an unknown workflow table ID | Distinguish snapshot inference from target observation | Not run |
| Review SQL without live access | Static findings and not-run live checks; no fabricated pass | Not run |
| Define local currency | Resolve project meaning, update glossary and evidence reference | Not run |
| Continue on another PC | Handoff with relative file paths and actual check status; no secrets | Not run |
| Install on a restricted device | Supported offline/per-user path; no package-policy bypass | Not run |
| Plan all procurement Gold datasets | Decision map and small milestone; no unrequested deployment | Not run |
| Suggest a missing capability | Installed-first shortlist; no automatic third-party install | Not run |
| Follow up on the same target | Reuse connection/discussion choices | Not run |
| Change database or fail sign-in | Verify new target or retain unverified state | Not run |

## Reproduce

```powershell
python -m unittest discover -s tests -v
python plugins/fo-data-atlas/scripts/validate_package.py --source-only
git -c core.whitespace=cr-at-eol diff --check
```

The workflow guide links the upstream pattern references. These implementations are Atlas-specific, do not copy upstream skill bodies, and do not claim upstream compatibility or licensing approval for future redistribution of third-party skills.
