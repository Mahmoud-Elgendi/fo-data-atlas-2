"""Release download integrity, offline fallback and preservation of installed data."""
import hashlib
from contextlib import redirect_stdout
import io
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile
import os
import shutil
import stat

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("atlas_github_release", ROOT / "plugins/fo-data-atlas/scripts/github_release.py")
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class GithubReleaseTests(unittest.TestCase):
    def setUp(self):
        parent = ROOT / 'test-evidence' / 'atlas-github'
        parent.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=parent)
        self.root = Path(self.temp.name)
        def cleanup():
            def remove_readonly(function,path,exc_info):
                os.chmod(path,stat.S_IWRITE);function(path)
            native=release.disk(self.root)
            if native.exists(): shutil.rmtree(native,onerror=remove_readonly)
            self.temp.cleanup()
        self.addCleanup(cleanup)

    def archive(self, name="fixture.zip", extra=None, corrupt=False):
        identity = json.dumps({"name": "fo-data-atlas", "version": "0.2.0"}).encode()
        db = b"small offline payload fixture"
        files = {".codex-plugin/plugin.json": identity, ".claude-plugin/plugin.json": identity,
                 "scripts/install.py": b"# installer fixture\n", "references/atlas.sqlite": db,
                 "examples/view-sql-custcustomerv3entity/source-CUSTDEFAULTDELIVERYLOCATIONVIEW--5f4dd73d7263.sql": b'SELECT 1;',
                 "references/manifest.json": json.dumps({"sqlite_sha256": hashlib.sha256(db).hexdigest()}).encode()}
        manifest = {"name": "fo-data-atlas", "version": "0.2.0", "files": [
            {"path": path, "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()}
            for path, content in files.items()]}
        if corrupt:
            files["references/atlas.sqlite"] = b"tampered database"
        output = self.root / name
        with zipfile.ZipFile(output, "w") as bundle:
            for path, content in files.items():
                bundle.writestr("fo-data-atlas/" + path, content)
            bundle.writestr("fo-data-atlas/package-manifest.json", json.dumps(manifest))
            if extra:
                bundle.writestr(extra, "unexpected")
        return output

    def info(self, archive):
        return {"repository": "owner/private-repo", "tag": "v0.2.0", "version": "0.2.0",
                "asset": "fo-data-atlas-0.2.0.zip", "bytes": archive.stat().st_size,
                "sha256": release.sha(archive)}

    def test_private_repo_url_and_reject_shell_or_path_input(self):
        self.assertEqual(release.repository("https://github.com/owner/private-repo.git"), "owner/private-repo")
        for value in ("--help", "owner/../repo", "https://evil.example/owner/repo", "owner/repo; echo token"):
            with self.assertRaises(ValueError):
                release.repository(value)

    @unittest.skipUnless(os.name=='nt','Windows CLI installation discovery')
    def test_installed_cli_is_found_when_terminal_path_is_stale(self):
        executable=self.root/'GitHub CLI/gh.exe';executable.parent.mkdir();executable.write_bytes(b'fixture - never executed')
        with patch.object(release.shutil,'which',return_value=None),patch.dict(os.environ,{'ProgramFiles':str(self.root)}):
            self.assertEqual(release.find_gh(),str(executable))

    def test_bootstrap_defaults_to_owner_repo_without_local_package(self):
        output = io.StringIO()
        with patch.object(release, 'read_json', return_value={}), patch.object(release, 'check', return_value={'status':'current'}) as check, redirect_stdout(output):
            self.assertEqual(release.main(['check']), 0)
        check.assert_called_once_with('Mahmoud-Elgendi/fo-data-atlas-2', '0.0.0', None)
        self.assertEqual(json.loads(output.getvalue())['status'], 'current')

    def test_explicit_repo_overrides_default(self):
        with patch.object(release, 'check', return_value={'status':'current'}) as check, redirect_stdout(io.StringIO()):
            self.assertEqual(release.main(['check','--repo','another/private-repo']), 0)
        self.assertEqual(check.call_args.args[0], 'another/private-repo')

    def test_unavailable_check_continues_offline_without_writes(self):
        with patch.object(release, "gh", side_effect=OSError("offline")):
            result = release.check("owner/repo", "0.1.1")
        self.assertEqual(result["status"], "unavailable")
        self.assertTrue(result["continue_offline"])
        self.assertEqual(list(self.root.iterdir()), [])

    def test_semantic_comparison_and_pinned_lookup(self):
        info = {"version": "0.10.0"}
        with patch.object(release, "release_info", return_value=info.copy()) as fetch:
            self.assertEqual(release.check("owner/repo", "0.9.0", "v0.10.0")["status"], "available")
            fetch.assert_called_once_with("owner/repo", "v0.10.0")
        with patch.object(release, "release_info", return_value=info.copy()):
            self.assertEqual(release.check("owner/repo", "0.10.0")["status"], "current")

    def test_release_requires_complete_asset_digest_and_stable_tag(self):
        archive = self.archive()
        info = self.info(archive)
        data = {"tag_name": info["tag"], "assets": [{"name": info["asset"], "size": info["bytes"],
                 "digest": "sha256:" + info["sha256"]}]}
        with patch.object(release, "gh", return_value=json.dumps(data)):
            self.assertEqual(release.release_info("owner/private-repo")["sha256"], info["sha256"])
        data["assets"][0].pop("digest")
        with patch.object(release, "gh", return_value=json.dumps(data)), self.assertRaisesRegex(ValueError, "digest"):
            release.release_info("owner/private-repo")
        data["prerelease"] = True
        with patch.object(release, "gh", return_value=json.dumps(data)), self.assertRaisesRegex(ValueError, "stable"):
            release.release_info("owner/private-repo")

    def test_download_verifies_before_promotion_and_keeps_previous_version(self):
        archive = self.archive()
        info = self.info(archive)
        destination = self.root / "downloads"
        old = destination / "fo-data-atlas-0.1.1"
        old.mkdir(parents=True)
        (old / "keep.txt").write_text("previous version")

        def download(arguments, timeout):
            target = Path(arguments[arguments.index("--dir") + 1]) / info["asset"]
            target.write_bytes(archive.read_bytes())
            return ""

        with patch.object(release, "gh", side_effect=download):
            pack = release.download(info, destination)
        self.assertTrue((pack / "references/atlas.sqlite").is_file())
        self.assertEqual(json.loads((pack / "release-origin.json").read_text())["repository"], "owner/private-repo")
        self.assertEqual((old / "keep.txt").read_text(), "previous version")
        self.assertFalse(list(destination.glob(".atlas-download-*")))
        with patch.object(release, 'gh', side_effect=AssertionError('Cached retry must not download again')):
            self.assertEqual(release.download(info, destination), pack)
        (pack / 'scripts/install.py').write_text('tampered')
        with self.assertRaisesRegex(ValueError, 'integrity'):
            release.download(info, destination)

    def test_wrong_outer_hash_never_promotes(self):
        archive = self.archive()
        info = self.info(archive)
        info["sha256"] = "0" * 64
        destination = self.root / "downloads"

        def download(arguments, timeout):
            (Path(arguments[-1]) / info["asset"]).write_bytes(archive.read_bytes())

        with patch.object(release, "gh", side_effect=download), self.assertRaisesRegex(ValueError, "ZIP failed"):
            release.download(info, destination)
        self.assertFalse((destination / "fo-data-atlas-0.2.0").exists())
        self.assertEqual(list(destination.iterdir()), [])

    def test_download_extracts_under_long_windows_cache_path(self):
        archive = self.archive()
        info = self.info(archive)
        destination = self.root / ('deep-project-' + 'x'*32) / 'github-download-test'
        def native(path):
            return Path('\\\\?\\'+str(path.resolve())) if os.name=='nt' and not str(path).startswith('\\\\?\\') else path
        def remove_readonly(function,path,exc_info):
            os.chmod(path,stat.S_IWRITE); function(path)
        self.addCleanup(lambda: shutil.rmtree(native(destination.parent),onerror=remove_readonly) if native(destination.parent).exists() else None)
        def download(arguments,timeout):
            path=Path(arguments[-1])/info['asset']
            native(path).write_bytes(archive.read_bytes())
        with patch.object(release,'gh',side_effect=download):
            pack=release.download(info,destination)
        self.assertTrue(native(pack/'references/atlas.sqlite').is_file())
        self.assertEqual(release.verify_pack(pack,'0.2.0',origin=info).name,'fo-data-atlas-0.2.0')

    def test_inner_tampering_and_unlisted_files_rejected(self):
        for name, extra, corrupt in (("corrupt.zip", None, True), ("unlisted.zip", "fo-data-atlas/extra.py", False)):
            archive = self.archive(name, extra, corrupt)
            with self.assertRaisesRegex(ValueError, "integrity|cover every"):
                release.extract_verified(archive, self.root / name.replace(".zip", ""), "0.2.0")

    def test_unsafe_paths_and_case_collisions_rejected(self):
        for index, extra in enumerate(("../escape.txt", "fo-data-atlas/../escape.txt", "fo-data-atlas/CON.txt",
                                       "fo-data-atlas/REFERENCES/atlas.sqlite")):
            archive = self.archive(f"bad{index}.zip", extra=extra)
            target = self.root / f"expanded{index}"
            with self.assertRaises(ValueError):
                release.extract_verified(archive, target, "0.2.0")
            self.assertFalse(target.exists())

    def test_release_version_mismatch_rejected(self):
        with self.assertRaisesRegex(ValueError, "identity"):
            release.extract_verified(self.archive(), self.root / "expanded", "0.3.0")


if __name__ == "__main__":
    unittest.main()
