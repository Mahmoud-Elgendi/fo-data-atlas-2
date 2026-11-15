"""Verify a SQL endpoint using an existing sqlcmd (Go) and Entra browser login.

Executes one fixed read-only statement. Does not persist targets or credentials.
"""
import argparse
import os
import re
import shutil
import subprocess

MARKER = "FO_ATLAS_CONNECTION_OK|"
QUERY = "SET NOCOUNT ON; SELECT 'FO_ATLAS_CONNECTION_OK|' + DB_NAME();"


def command(endpoint, database, executable):
    endpoint = endpoint.strip()
    database = database.strip()
    if not re.fullmatch(r"(?:tcp:)?[A-Za-z0-9][A-Za-z0-9.-]*(?:,[0-9]{1,5})?", endpoint):
        raise ValueError("Use a SQL server hostname, optionally tcp: and ,port; no URL or connection string.")
    if "," in endpoint and not 1 <= int(endpoint.rsplit(",", 1)[1]) <= 65535:
        raise ValueError("SQL port must be between 1 and 65535.")
    if not database or database.startswith("-") or len(database) > 128 or any(ord(c) < 32 for c in database):
        raise ValueError("Use a nonempty database name of at most 128 characters without control characters.")
    return [str(executable), "-S", endpoint, "-d", database,
            "--authentication-method", "ActiveDirectoryInteractive", "-N", "true",
            "-l", "30", "-t", "30", "-b", "-h", "-1", "-Q", QUERY]


def probe(endpoint, database, executable=None):
    executable = executable or shutil.which("sqlcmd")
    if not executable:
        raise ValueError("sqlcmd (Go) is unavailable. Use an available SQL connector or choose offline work.")
    args = command(endpoint, database, executable)
    # Sign-in uses the browser. Keep captured client output out of project files.
    env = {k: v for k, v in os.environ.items() if k.upper() not in
           {"SQLCMDPASSWORD", "SQLCMDUSER", "SQLCMDINI"}}
    result = subprocess.run(args, capture_output=True, text=True, timeout=180,
                            shell=False, env=env)
    if result.returncode != 0:
        raise ValueError("Connection check failed. Check sign-in, endpoint, database and SQL permissions; no connection verified.")
    expected = MARKER + database.strip()
    if expected not in [line.strip() for line in result.stdout.splitlines()]:
        raise ValueError("Requested database was not confirmed by the probe result.")
    return database.strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--database", required=True)
    parser.add_argument("--sqlcmd", help="Path to an existing Microsoft sqlcmd (Go) executable.")
    args = parser.parse_args()
    print("Complete Microsoft browser sign-in if prompted. Running a read-only connection check.", flush=True)
    try:
        database = probe(args.endpoint, args.database, args.sqlcmd)
    except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
        message = "Connection check timed out; no connection verified." if isinstance(exc, subprocess.TimeoutExpired) else str(exc)
        print(message)
        return 1
    print("Connection verified for " + database + ". Probe session closed; no project configuration written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
