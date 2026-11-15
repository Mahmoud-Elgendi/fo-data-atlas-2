"""Probe boundary checks; these tests never connect to a real database."""
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

PACK = Path(__file__).resolve().parents[1] / "plugins" / "fo-data-atlas"
sys.path.insert(0, str(PACK / "scripts"))
import connect_database as connection


class AtlasConnectionTests(unittest.TestCase):
    def test_success_requires_requested_database_marker(self):
        for output, success in [("FO_ATLAS_CONNECTION_OK|DWH\n", True),
                                ("FO_ATLAS_CONNECTION_OK|Other\n", False), ("", False)]:
            with self.subTest(output=output), patch.object(connection.subprocess, "run", return_value=
                    subprocess.CompletedProcess([], 0, output, "")) as run:
                if success:
                    self.assertEqual(connection.probe("example.test", "DWH", "sqlcmd.exe"), "DWH")
                else:
                    with self.assertRaisesRegex(ValueError, "not confirmed"):
                        connection.probe("example.test", "DWH", "sqlcmd.exe")
                args = run.call_args.args[0]
                self.assertEqual(args[args.index("-Q") + 1], connection.QUERY)
                self.assertFalse(run.call_args.kwargs["shell"])
                self.assertEqual(args[args.index("-N") + 1], "true")
                self.assertNotIn("-C", args)

    def test_failure_and_missing_client_are_not_success(self):
        with patch.object(connection.shutil, "which", return_value=None):
            with self.assertRaisesRegex(ValueError, "unavailable"):
                connection.probe("example.test", "DWH")
        with patch.object(connection.subprocess, "run", return_value=
                          subprocess.CompletedProcess([], 1, "FO_ATLAS_CONNECTION_OK|DWH", "denied")):
            with self.assertRaisesRegex(ValueError, "failed"):
                connection.probe("example.test", "DWH", "sqlcmd.exe")
        with patch.object(connection.subprocess, "run", side_effect=subprocess.TimeoutExpired("sqlcmd", 180)):
            with self.assertRaises(subprocess.TimeoutExpired):
                connection.probe("example.test", "DWH", "sqlcmd.exe")

    def test_user_values_cannot_become_sql_or_shell_commands(self):
        name = "DWH'; DROP TABLE example;--"
        args = connection.command("tcp:example.test,1433", name, "C:/With Spaces/sqlcmd.exe")
        self.assertEqual(args[args.index("-d") + 1], name)
        self.assertNotIn(name, args[args.index("-Q") + 1])
        for endpoint in ("https://example.test", "server;Password=secret", "-Q", "x,65536"):
            with self.subTest(endpoint=endpoint), self.assertRaises(ValueError):
                connection.command(endpoint, "DWH", "sqlcmd")
        for database in ("", "-Q", "x\ny"):
            with self.subTest(database=database), self.assertRaises(ValueError):
                connection.command("example.test", database, "sqlcmd")

    def test_no_inherited_sqlcmd_password_or_startup_script(self):
        with patch.dict(connection.os.environ, {"SQLCMDPASSWORD": "secret", "SQLCMDINI": "startup.sql"}), \
                patch.object(connection.subprocess, "run", return_value=
                             subprocess.CompletedProcess([], 0, "FO_ATLAS_CONNECTION_OK|DWH", "")) as run:
            connection.probe("example.test", "DWH", "sqlcmd.exe")
        self.assertNotIn("SQLCMDPASSWORD", run.call_args.kwargs["env"])
        self.assertNotIn("SQLCMDINI", run.call_args.kwargs["env"])


if __name__ == "__main__":
    unittest.main()
