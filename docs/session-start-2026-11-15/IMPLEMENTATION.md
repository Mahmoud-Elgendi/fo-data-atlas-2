# Optional database connection and discussion

Date: 15 November 2026. Status: local source change; not committed, published or installed. Existing v0.4.1 release assets are unchanged. A new version is required before distributing these changed tools; the local packaging smoke archive is not a replacement v0.4.1 release.

## Agreed flow

Start project work with the optional database/offline question. If connecting, collect the endpoint then the database name, one question at a time. Verify access, then offer discussion. Accepting discussion uses the bundled grill-me-with-docs skill. Existing answers are reused throughout the conversation; installation/update requests stay on their own setup path. A changed target requires a new connection check.

The shared reference is plugins/fo-data-atlas/references/session-start.md. Both Atlas entry skills link to it. The bundled discussion skill includes its own one-question interview and decision-note workflow, without requiring Mahmoud's separately installed grill-with-docs/grilling/domain-modeling skills.

## Connection implementation

Prefer an available connector. The standard-library connect_database.py helper can use an existing Microsoft sqlcmd (Go) for Entra interactive browser authentication and a fixed DB_NAME() read-only probe. It requires a successful exit and the requested database marker. No arbitrary query flag, password argument, target persistence or credential storage is provided. SQL input is fixed, subprocess arguments are separated, TLS encryption is requested without certificate bypass, and inherited SQLCMD password/user/startup-file settings are removed. Missing clients, failed checks and timeouts do not establish access. Client setup is an explicit separate choice, including on devices without admin access.

The probe closes its session. Subsequent task-authorized schema checks use the same target through the host's connector/client. A connection choice does not authorize writes. The helper is not a database driver or persistent connection manager.

## Verification

- 67 Python suite tests passed, including four new connection boundary tests (success marker, wrong database, denied access, missing client, timeout, argument separation, TLS flags and inherited startup/credential exclusion). These are mocked tests, not a live SQL test.
- Source-only package validation passed; three skill manifests and local links are valid.
- Local tools archive build succeeded: 83 files, 461398 bytes. This is an unpublished packaging smoke artifact using the existing source version; do not upload it under v0.4.1.
- Actual Microsoft sqlcmd (Go) v1.10.0 local help lists the authentication-method and encrypt-connection flags. No connection/authentication was initiated.
- Installed host conversation behavior, recipient sign-in, actual target access and native skill loading remain unverified.

Manual acceptance: on a new chat choose offline then decline discussion; choose online and supply values sequentially; reuse an already named target; handle a missing client; complete Microsoft sign-in; reject a failed or wrong-database check; accept discussion and confirm one question at a time; follow up without repeating prompts; change target and verify again. Record observed results before claiming readiness.

## Reproduce source checks

From the plugin-only source checkout, with Python 3.10+:

```powershell
python -m unittest discover -s tests -v
python plugins/fo-data-atlas/scripts/validate_package.py --source-only
git -c core.whitespace=cr-at-eol diff --check
```

Reference checked: [Microsoft sqlcmd Entra authentication](https://learn.microsoft.com/en-us/sql/tools/sqlcmd/sqlcmd-authentication?tabs=go&view=sql-server-ver16), 15 November 2026. The discussion wording and portability workflow are authored for this package; no external skill dependency was added.
