---
name: fo-atlas-find-skills
description: Find an installed or external skill for a missing Atlas capability when the user explicitly asks for skill discovery or recommendations; review dependencies before suggesting installation.
---

1. Clarify the missing capability only if it is not already clear. Check the bundled [Atlas workflow](../../references/analyst-workflow.md) and the host's installed skill inventory first. Prefer an existing skill that completes the task without another install.
2. For external discovery, use the available search tools and original publisher documentation. A published skills CLI can be an optional search route if already available and permitted. Verify the actual source, maintenance state, intended host, dependencies, license and installation instructions before recommending redistribution or installation. Label unknowns and untested compatibility.
3. Share a short shortlist with the job each skill performs, why it fits, required runtimes/network and whether it is already installed. External skills can carry scripts, network actions and host-specific assumptions; examine those before recommending one. Keep endpoint names, schemas, customer details and proprietary metadata out of external search terms.
4. Ask which candidate the user wants before installing third-party code. Discovery alone authorizes no package download/execution, new account connection or host configuration change. Respect offline choices and organization package-source restrictions. If no suitable option exists, propose a small Atlas-specific workflow with explicit limits.

Distinguish a recommendation, a downloaded skill, successful host activation and a verified end-to-end capability. Never describe arbitrary external skills as bundled, supported, secure or tested merely because a catalog lists them. This skill itself works from host tools and documentation; it does not require an extra discovery CLI or auto-install one.
