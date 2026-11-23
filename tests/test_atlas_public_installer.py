"""Public setup transport boundaries. Tests use no network or host installation."""
import io
from pathlib import Path
import re
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'plugins/fo-data-atlas/scripts'))
import github_release


def bootstrap_module():
    script = (ROOT / 'tools/Install-Atlas.ps1').read_text(encoding='utf-8')
    code = re.search(r"\$bootstrap = @'\n(.*?)\n'@", script, re.S).group(1)
    module = types.ModuleType('atlas_public_bootstrap')
    exec(compile(code, 'Install-Atlas embedded Python', 'exec'), module.__dict__)
    module.github = github_release
    return module


class PublicInstallerTests(unittest.TestCase):
    def test_transport_only_accepts_metadata_download_shape(self):
        module = bootstrap_module()
        with patch.object(module, 'download_public') as download:
            module.public_transport(['release', 'download', 'v0.3.0', '--repo',
                                     'github.com/Mahmoud-Elgendi/fo-data-atlas-2',
                                     '--pattern', 'core.zip', '--dir', 'C:/With Spaces'])
            download.assert_called_once_with('Mahmoud-Elgendi/fo-data-atlas-2', 'v0.3.0', 'core.zip', 'C:/With Spaces')
            for args in (['api', 'repos/example'], ['release', 'delete'], []):
                with self.assertRaisesRegex(ValueError, 'Unsupported'):
                    module.public_transport(args)

    def test_download_rejects_foreign_repo_unsafe_paths_and_unstable_tags(self):
        module = bootstrap_module()
        with patch.object(module.urllib.request, 'urlopen') as request:
            for repo, tag, asset in [('someone/else', 'v0.3.0', 'core.zip'),
                                     (module.REPOSITORY, 'main', 'core.zip'),
                                     (module.REPOSITORY, 'v0.3.0', '../core.zip'),
                                     (module.REPOSITORY, 'v0.3.0', 'folder/core.zip')]:
                with self.subTest(repo=repo, tag=tag, asset=asset), self.assertRaises(ValueError):
                    module.download_public(repo, tag, asset, '.')
            request.assert_not_called()

    def test_download_streams_public_asset_without_overwriting_existing_file(self):
        module = bootstrap_module()
        class Response(io.BytesIO):
            def geturl(self): return 'https://release-assets.githubusercontent.com/asset'
        scratch = ROOT / 'test-evidence/public-installer-tests'
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as directory:
            with patch.object(module.urllib.request, 'urlopen', return_value=Response(b'verified-later')) as request:
                module.download_public(module.REPOSITORY, 'v0.3.0', 'core.zip', directory)
            self.assertEqual((Path(directory)/'core.zip').read_bytes(), b'verified-later')
            self.assertEqual(request.call_args.args[0].full_url,
                             'https://github.com/Mahmoud-Elgendi/fo-data-atlas-2/releases/download/v0.3.0/core.zip')
            self.assertNotIn('Authorization', request.call_args.args[0].headers)
            with patch.object(module.urllib.request, 'urlopen', return_value=Response(b'changed')):
                with self.assertRaises(FileExistsError):
                    module.download_public(module.REPOSITORY, 'v0.3.0', 'core.zip', directory)
            self.assertEqual((Path(directory)/'core.zip').read_bytes(), b'verified-later')

    def test_non_https_or_foreign_redirect_is_rejected_before_write(self):
        module = bootstrap_module()
        class Response(io.BytesIO):
            def geturl(self): return 'http://example.test/asset'
        with patch.object(module.urllib.request, 'urlopen', return_value=Response(b'bad')):
            with self.assertRaisesRegex(ValueError, 'redirect'):
                module.download_public(module.REPOSITORY, 'v0.3.0', 'core.zip', '.')


if __name__ == '__main__': unittest.main()
