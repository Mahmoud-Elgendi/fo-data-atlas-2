# Start an Atlas task

Follow this flow when either Atlas skill starts a new conversation or the user changes the target database. Keep answers in conversation context; reuse choices already supplied. A follow-up in the same task does not restart the interview. Explicit requests to work offline, connect to a named target, or start immediately count as answers.

## 1. Choose the target

Ask: **Would you like to connect to a database for this task, or use offline metadata only?**

If offline, continue with the installed metadata and project CSV. If connecting, collect missing values one question at a time:

- **What is the SQL endpoint?** Ask for the server hostname, not a portal URL or a connection string containing credentials.
- **What is the database name?** For Fabric this is the Lakehouse SQL endpoint's database or Warehouse database, not the workspace name.

The connection offer is for the SQL endpoint, not an operational F&O database. If the user names another database engine or authentication scheme, determine whether an installed connector supports it before trying to connect.

## 2. Verify the connection

Prefer an available database connector that can target the supplied endpoint and database. Use its supported sign-in flow. Otherwise use the packaged [connection probe](../scripts/connect_database.py) with an existing Microsoft sqlcmd (Go):

```text
python PACK/scripts/connect_database.py --endpoint <hostname> --database <database>
```

Use structured tool arguments or shell-appropriate quoting for user values. `--sqlcmd <executable-path>` selects a known existing executable outside PATH. The probe uses Microsoft Entra interactive sign-in and runs only `SELECT DB_NAME()` with a result marker. It opens a connection for that check, then closes it; it does not create a persistent SQL session. Reuse the same target with the host's connector/client for subsequent authorized work.

Ask the user to complete Microsoft sign-in when prompted. Handle passwords, tokens and device authentication through the provider; never request secrets in chat or save them in project files. A Fabric CLI login alone is not proof of SQL access.

If no compatible connector/client is available, say **The endpoint is recorded for this conversation, but I cannot connect yet.** Offer client setup or offline work, one question at a time. An installation restriction, failed login, timeout or missing client leaves connection status unverified. Do not silently install software or claim success. Proceed to the discussion offer after the user chooses how to handle a failed connection.

Success requires a successful read-only check in the requested database. Report **Connection verified for <database>.** This proves access at that time, not permissions to every table, schema compatibility, business correctness, or that the account itself is read-only. Keep TLS certificate validation enabled. Collect no production rows in this probe.

## 3. Offer discussion

After the target choice and connection outcome, ask: **Would you like to discuss the requirements before I start?**

If yes, load the bundled [grill-me-with-docs skill](../skills/grill-me-with-docs/SKILL.md) and follow its interview. If no, continue the requested task using known requirements, clarifying only details needed for correctness. Never make an optional discussion block work after it was declined. This flow runs on skill use, not at IDE startup.

## Execution scope

Choosing a connection authorizes the small read-only connection check. Run further read-only schema checks or bounded query tests when required by the user's task; explain what is being checked. Creating datasets still defaults to writing SQL files. Connection permission alone does not authorize DDL, DML, ETL execution, deployment or changes to source data. Record which checks actually ran and their outcomes, without credentials or row data. Keep target details out of shared plugin examples and Git commits unless explicitly requested.

The offline snapshot and live target are distinct evidence sources. Continue verifying joins, fields and enums; a successful login does not validate them. Live schema evidence may replace a CSV for the fields actually inspected; export a project CSV when reusable schema evidence is needed. Reading original exported SQL remains available offline.

Microsoft documents the Go client's browser authentication in [sqlcmd Entra authentication](https://learn.microsoft.com/en-us/sql/tools/sqlcmd/sqlcmd-authentication?tabs=go&view=sql-server-ver16). The client is optional and is not bundled. The prompt flow and mocked probe tests do not certify native host behavior or a recipient's real SQL connection.
