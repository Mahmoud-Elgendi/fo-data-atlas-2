"""Exercise the optional buildless npx entrance alongside the Python suite."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class AtlasCliTests(unittest.TestCase):
    def test_node_launcher_contracts(self):
        bundled = Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
        node = str(bundled) if bundled.is_file() else shutil.which('node')
        if not node: self.skipTest('Optional npx entrance needs Node.js')
        result = subprocess.run([node, '--test', str(ROOT/'tests/test_atlas_cli.cjs')],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_launcher_manifest_keeps_metadata_and_lifecycle_scripts_out(self):
        path = ROOT/'tools/atlas-npx-package.json'
        package = json.loads(path.read_text())
        self.assertTrue(package['private'])
        self.assertNotIn('scripts', package)
        self.assertNotIn('dependencies', package)
        identity = json.loads((ROOT/'plugins/fo-data-atlas/.codex-plugin/plugin.json').read_text())
        self.assertEqual(package['version'], identity['version'])
        for name in package['files']:
            self.assertTrue((ROOT/name).is_file(), name)
            self.assertNotIn('.sqlite', name)


if __name__ == '__main__': unittest.main()
