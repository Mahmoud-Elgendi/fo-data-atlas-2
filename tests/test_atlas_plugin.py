"""Offline plugin behavior: provenance isolation, portability and non-destructive setup."""
import csv
from contextlib import redirect_stdout
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "fo-data-atlas"
sys.path.insert(0, str(PACK / "scripts"))
import atlas
import install as atlas_install
import lint_sql
from tools import build_atlas_plugin as builder


class AtlasPluginTests(unittest.TestCase):
    def setUp(self):
        workspace_temp = ROOT / "test-evidence" / "atlas-plugin"
        workspace_temp.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=workspace_temp)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def build_fixture(self):
        folder = self.root / "originals"
        folder.mkdir()
        (folder / "PurchLine.xml").write_text("<AxTable><Name>PurchLine</Name><Fields><AxTableField><Name>PurchId</Name></AxTableField></Fields></AxTable>", encoding="utf-8")
        (folder / "notes.md").write_text("Business proposal: purchase order lines; not reconciled.", encoding="utf-8")
        pack = self.root / "portable"
        with redirect_stdout(io.StringIO()):
            builder.build({"sources": [{"type": "folder", "id": "environment-a", "path": str(folder)}]}, pack / "references")
        return folder, pack

    def test_search_show_portable_after_originals_disappear(self):
        original, pack = self.build_fixture()
        with atlas.connect(pack) as db:
            hits = atlas.search(db, "PurchId", "environment-a")
            self.assertEqual(len(hits), 1)
            record, raw = atlas.document(db, hits[0]["id"])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), record["sha256"])
            self.assertIn("PurchId", raw.decode())
        # Pack must not need source machine paths for reference retrieval.
        (original / "PurchLine.xml").unlink()
        with atlas.connect(pack) as db:
            self.assertIn("PurchId", atlas.document(db, hits[0]["id"])[1].decode())
            self.assertEqual(atlas.search(db, "PurchId", "other-environment"), [])

    def test_published_snapshot_is_never_overwritten(self):
        original, pack = self.build_fixture()
        before = (pack / "references" / "atlas.sqlite").read_bytes()
        with self.assertRaises(ValueError): builder.build({"sources": [{"type": "folder", "id": "a", "path": str(original)}]}, pack / "references")
        self.assertEqual(before, (pack / "references" / "atlas.sqlite").read_bytes())

    def test_tampered_manifest_content_blocks_publication(self):
        snapshot = self.root / "snapshot"
        (snapshot / "raw").mkdir(parents=True)
        (snapshot / "raw" / "PurchLine.xml").write_bytes(b"changed content")
        with (snapshot / "manifest.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, ["RelativePath", "Kind", "Name", "SHA256"])
            writer.writeheader()
            writer.writerow({"RelativePath": "PurchLine.xml", "Kind": "AxTable", "Name": "PurchLine", "SHA256": "0" * 64})
        output = self.root / "pack" / "references"
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            builder.build({"sources": [{"type": "snapshot", "id": "bad", "path": str(snapshot)}]}, output)
        self.assertFalse((output / "atlas.sqlite").exists())

    def test_snapshot_path_traversal_rejected(self):
        with self.assertRaises(ValueError): builder.contained(self.root, "../outside.xml")

    def test_resume_cannot_silently_retain_unselected_sources(self):
        output = self.root / "staged-pack" / "references"
        output.mkdir(parents=True)
        db = sqlite3.connect(output / "atlas.build.sqlite")
        builder.initialize(db)
        builder.register(db, "old-environment", "old", "hash", "not validated")
        db.commit(); db.close()
        folder = self.root / "new-environment"; folder.mkdir()
        with self.assertRaisesRegex(ValueError, "Staged sources were removed"):
            builder.build({"sources": [{"type": "folder", "id": "new-environment", "path": str(folder)}]}, output)
        self.assertFalse((output / "atlas.sqlite").exists())

    def test_corrupt_stored_evidence_is_not_returned(self):
        _, pack = self.build_fixture()
        path = pack / "references" / "atlas.sqlite"
        with sqlite3.connect(path) as db:
            doc = db.execute("SELECT id,sha256 FROM documents LIMIT 1").fetchone()
            import zlib
            db.execute("UPDATE blobs SET content=? WHERE sha256=?", (zlib.compress(b"tampered"), doc[1]))
        db.close()
        with atlas.connect(pack) as db, self.assertRaisesRegex(ValueError, "hash mismatch"):
            atlas.document(db, doc[0])

    def test_business_filenames_and_no_overwrite(self):
        output = Path(atlas.scaffold(self.root, "purchase-order-lines"))
        self.assertEqual({p.name for p in output.iterdir()}, {"purchase-order-lines.sql", "purchase-order-lines.mapping.md", "purchase-order-lines.checks.sql"})
        with self.assertRaises(ValueError): atlas.scaffold(self.root, "purchase-order-lines")
        for invalid in ("query", "../escape", "Purchase Order Lines"):
            with self.assertRaises(ValueError): atlas.slug_name(invalid)

    def test_schema_exact_casing_and_project_isolation(self):
        csvfile = self.root / "schema.csv"
        csvfile.write_text("schema_name,table_name,column_name,data_type\ndbo,purchline,IsDelete,bit\ndbo,purchline,dataareaid,nvarchar\n", encoding="utf-8")
        schema = atlas.load_schema(csvfile)
        self.assertIn("IsDelete", schema[("dbo", "purchline")])
        self.assertNotIn("isdelete", schema[("dbo", "purchline")])
        config = Path(atlas.project_init(self.root / "project-a", csvfile))
        data = json.loads(config.read_text())
        self.assertEqual(data["metadata_sources"], [])
        self.assertEqual(data["schema_sha256"], hashlib.sha256(csvfile.read_bytes()).hexdigest())
        self.assertFalse((self.root / "project-b" / ".fo-data-atlas").exists())
        with self.assertRaises(ValueError): atlas.project_init(self.root / "project-a", csvfile)

    def test_schema_duplicate_or_missing_columns_rejected(self):
        path = self.root / "bad.csv"
        path.write_text("schema_name,table_name\ndbo,purchline\n")
        with self.assertRaises(ValueError): atlas.load_schema(path)
        path.write_text("schema_name,table_name,column_name,data_type\ndbo,purchline,recid,bigint\ndbo,purchline,recid,bigint\n")
        with self.assertRaises(ValueError): atlas.load_schema(path)

    def test_project_context_detects_stale_schema_and_wrong_source(self):
        _, pack = self.build_fixture()
        csvfile = self.root / "actual.csv"
        csvfile.write_text("schema_name,table_name,column_name,data_type\ndbo,purchline,recid,bigint\n")
        project = self.root / "context-project"
        config = Path(atlas.project_init(project, csvfile))
        value = json.loads(config.read_text())
        value.update(reference_pack=str(pack), metadata_sources=["environment-a"])
        config.write_text(json.dumps(value))
        self.assertEqual(atlas.project_context(project)["reference_pack"], str(pack.resolve()))
        value["metadata_sources"] = ["other"]
        config.write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError, "sources are absent"): atlas.project_context(project)
        (config.parent / "fabric-schema.csv").write_text("changed")
        with self.assertRaisesRegex(ValueError, "schema changed"): atlas.project_context(project)

    def test_install_merges_marketplaces_without_changing_unrelated_entries(self):
        import shutil
        _, pack = self.build_fixture()
        for name in (".codex-plugin", ".claude-plugin", "skills", "scripts"):
            shutil.copytree(PACK / name, pack / name, ignore=shutil.ignore_patterns("__pycache__"))
        base = self.root / "install-project"
        existing = base / ".agents" / "plugins" / "marketplace.json"
        atlas_install.write_json(existing, {"name": "other-private", "plugins": [{"name": "other", "source": {"source": "local", "path": "./other"}}]})
        result = atlas_install.prepare(pack, base, "both")
        values = json.loads(existing.read_text())
        self.assertEqual(values["name"], "other-private")
        self.assertEqual(values["plugins"][0]["name"], "other")
        self.assertEqual(values["plugins"][1]["name"], "fo-data-atlas")
        self.assertFalse(result["host_load_verified"])
        self.assertTrue((Path(result["package"]) / "references" / "atlas.sqlite").exists())
        self.assertTrue((Path(result["claude_marketplace"]) / ".claude-plugin" / "marketplace.json").exists())
        with self.assertRaisesRegex(ValueError, "inside the source package"):
            atlas_install.prepare(pack, pack, "both")

    def test_xml_summary_keeps_composite_and_fixed_conditions(self):
        raw = b'<AxTable><Name>Lines</Name><Relations><AxTableRelation><Name>Header</Name><RelatedTable>Header</RelatedTable><Constraints><AxTableRelationConstraintField><Field>Id</Field><RelatedField>Id</RelatedField></AxTableRelationConstraintField><Fixed><Field>Type</Field><Value>3</Value></Fixed></Constraints></AxTableRelation></Relations></AxTable>'
        summary = atlas.xml_summary(raw)
        xml = summary["Relations"][0]["xml"]
        self.assertIn("RelatedField", xml)
        self.assertIn("<Value>3</Value>", xml)
        self.assertIn("not parsed", atlas.xml_summary(b'<!DOCTYPE x><x/>')["warning"])

    def test_sql_guard_preserves_case_exception_and_left_join_rows(self):
        schema = {("dbo", "purchline"): {c: {} for c in ("recid", "dataareaid", "purchid", "IsDelete")},
                  ("dbo", "purchtable"): {c: {} for c in ("recid", "dataareaid", "purchid", "IsDelete")}}
        sql = "SELECT l.recid AS PurchaseLineId, UPPER(l.dataareaid) AS Company FROM dbo.purchline AS l LEFT JOIN dbo.purchtable AS h ON h.purchid = l.purchid AND h.dataareaid = l.dataareaid AND h.IsDelete IS NULL WHERE l.IsDelete IS NULL;"
        result = lint_sql.check(sql, schema, True, True)
        self.assertEqual(result["issues"], [])
        bad = sql.replace("AND h.IsDelete IS NULL WHERE", "WHERE h.IsDelete IS NULL AND")
        self.assertTrue(any("LEFT JOIN deletion" in x for x in lint_sql.check(bad, schema, True, True)["issues"]))
        wrong_case = sql.replace("l.recid", "l.RECID").replace("h.IsDelete", "h.isdelete")
        issues = lint_sql.check(wrong_case, schema, True, True)["issues"]
        self.assertTrue(any("RECID" in x for x in issues))
        self.assertTrue(any("IsDelete" in x for x in issues))

    def test_sql_guard_rejects_mutation_but_ignores_comment_and_literal_keywords(self):
        schema = {("dbo", "t"): {"value": {}}}
        self.assertEqual(lint_sql.check("-- delete from\nSELECT 'delete' AS Label, t.value AS Value FROM dbo.t AS t", schema)["issues"], [])
        self.assertTrue(lint_sql.check("DELETE FROM dbo.t", schema)["issues"])

    def test_named_metadata_reads_are_bounded_and_preserve_selected_source(self):
        fields = "".join("<Field><Name>Field" + str(i) + "</Name></Field>" for i in range(40))
        raw = ("<AxTable><Name>T</Name><Fields>" + fields + "</Fields><SourceCode><Methods><Method><Name>findHeader</Name><Source>return Header::find(this.Id);</Source></Method></Methods></SourceCode></AxTable>").encode()
        summary = atlas.xml_summary(raw)
        self.assertEqual(len(summary["Fields"]), 30)
        self.assertTrue(summary["Fields_coverage"]["truncated"])
        selected = atlas.xml_summary(raw, "Fields", "Field39")
        self.assertEqual(len(selected["Fields"]), 1)
        self.assertEqual(selected["Fields"][0]["properties"]["Name"], "Field39")
        method = atlas.xml_summary(raw, "Methods", "findHeader")
        self.assertEqual(method["methods"][0]["source"], "return Header::find(this.Id);")
        self.assertNotIn("Fields", method)

    def test_label_conflicts_are_not_silently_resolved(self):
        folder = self.root / "labels"
        for model, value in (("A", "Purchase order"), ("B", "Different label")):
            target = folder / model / "AxLabelFile" / "LabelResources" / "en-US"
            target.mkdir(parents=True)
            (target / "SYS.en-us.label.txt").write_text("@SYS15812=" + value + "\n", encoding="utf-8")
        pack = self.root / "label-pack"
        with redirect_stdout(io.StringIO()):
            builder.build({"sources": [{"type": "folder", "id": "labels", "path": str(folder)}]}, pack / "references")
        with atlas.connect(pack) as db:
            result = atlas.label_lookup(db, "@SYS15812", "labels")
            self.assertEqual(len(result["matches"]), 2)
            self.assertTrue(result["ambiguous"])
            self.assertEqual(atlas.label_lookup(db, "@SYS15812", "other")["matches"], [])

    def test_setup_choice_retries_and_yes_no_defaults(self):
        with redirect_stdout(io.StringIO()), patch("builtins.input", side_effect=["invalid", "2"]):
            self.assertEqual(atlas_install.choose("Tool", (("codex", "Codex"), ("claude", "Claude")), "codex"), "claude")
        with patch("builtins.input", return_value=""):
            self.assertTrue(atlas_install.confirm("Continue?"))
        with redirect_stdout(io.StringIO()), patch("builtins.input", side_effect=["maybe", "N"]):
            self.assertFalse(atlas_install.confirm("Continue?"))

    def test_setup_cancel_does_not_copy_or_register(self):
        project = self.root / "not-created"
        with redirect_stdout(io.StringIO()) as output, patch("builtins.input", side_effect=["3", "1", str(project), "n"]), patch.object(atlas_install, "prepare") as prepare:
            self.assertEqual(atlas_install.main(['--metadata-profile','core']), 0)
        prepare.assert_not_called()
        self.assertFalse(project.exists())
        self.assertIn("Mahmoud Elgendi", output.getvalue())

    def test_setup_accepts_preview_and_keeps_scripted_json_mode(self):
        result = {"package": str(self.root / "package"), "next_steps": ["Activate the plugin."]}
        project = self.root / "project"
        with redirect_stdout(io.StringIO()), patch("builtins.input", side_effect=["3", "1", str(project), ""]), patch('metadata_cache.acquire',return_value=self.root/'fixture-metadata'), patch.object(atlas_install, "prepare", return_value=dict(result)) as prepare:
            self.assertEqual(atlas_install.main(['--metadata-profile','core']), 0)
        self.assertEqual(prepare.call_args.args[1:], (project.resolve(), "both"))
        self.assertTrue(prepare.call_args.kwargs["allow_upgrade"])
        with redirect_stdout(io.StringIO()) as output, patch("builtins.input", side_effect=AssertionError("Non-interactive setup prompted")), patch('metadata_cache.acquire',return_value=self.root/'fixture-metadata'), patch.object(atlas_install, "prepare", return_value=dict(result)):
            self.assertEqual(atlas_install.main(["--host", "codex", "--scope", "project", "--project", str(project)]), 0)
        self.assertEqual(json.loads(output.getvalue())["scope"], "project")

    def test_setup_managed_upgrade_keeps_previous_files(self):
        import shutil
        _, pack = self.build_fixture()
        shutil.copytree(PACK / ".codex-plugin", pack / ".codex-plugin")
        base = self.root / "upgrade-project"
        previous = base / ".fo-data-atlas" / "distribution-0.1.0" / "plugins" / "fo-data-atlas"
        atlas_install.write_json(previous / ".codex-plugin" / "plugin.json", {"name": "fo-data-atlas", "version": "0.1.0"})
        registry = base / ".agents" / "plugins" / "marketplace.json"
        atlas_install.write_json(registry, {"name": "private", "plugins": [{"name": "fo-data-atlas", "source": {"source": "local", "path": "./.fo-data-atlas/distribution-0.1.0/plugins/fo-data-atlas"}}, {"name": "other"}]})
        with self.assertRaises(ValueError): atlas_install.prepare(pack, base, "codex")
        result = atlas_install.prepare(pack, base, "codex", allow_upgrade=True)
        self.assertTrue(previous.exists())
        version = json.loads((PACK / '.codex-plugin/plugin.json').read_text())['version']
        self.assertIn("distribution-" + version, result["package"])
        entries = json.loads(registry.read_text())["plugins"]
        self.assertIn("distribution-" + version, entries[0]["source"]["path"])
        self.assertEqual(entries[1], {"name": "other"})

    def test_interrupted_copy_does_not_register_partial_install(self):
        import shutil
        _, pack = self.build_fixture()
        shutil.copytree(PACK / '.codex-plugin', pack / '.codex-plugin')
        base = self.root / 'failed-install'
        with patch.object(atlas_install.shutil, 'copytree', side_effect=OSError('simulated copy interruption')):
            with self.assertRaisesRegex(OSError, 'interruption'):
                atlas_install.prepare(pack, base, 'codex')
        self.assertFalse((base / '.agents/plugins/marketplace.json').exists())
        self.assertFalse(list(base.rglob('atlas.sqlite')))

    def test_temporary_directory_lock_does_not_publish_partial_copy(self):
        staged=self.root/'staged';staged.mkdir();(staged/'complete.txt').write_text('complete')
        target=self.root/'target'
        original=Path.rename;calls=[]
        def locked_once(path,destination):
            calls.append(path)
            if len(calls)==1: raise PermissionError('temporary cloud scan lock')
            return original(path,destination)
        with patch.object(Path,'rename',new=locked_once),patch.object(atlas_install.time,'sleep'):
            atlas_install.promote(staged,target)
        self.assertEqual((target/'complete.txt').read_text(),'complete')
        self.assertFalse(staged.exists())
        self.assertEqual(len(calls),2)

    def test_long_project_path_install(self):
        import shutil, os, stat
        _, pack = self.build_fixture()
        shutil.copytree(PACK / '.codex-plugin', pack / '.codex-plugin')
        longfile = pack / 'references' / ('metadata-' + 'x'*100 + '.md')
        atlas_install.disk(longfile).write_text('long path evidence',encoding='utf-8')
        self.addCleanup(lambda: atlas_install.disk(longfile).unlink(missing_ok=True))
        base = self.root / ('project-' + 'y'*90)
        def remove_readonly(function, path, exc_info):
            os.chmod(path,stat.S_IWRITE)
            function(path)
        self.addCleanup(lambda: shutil.rmtree(atlas_install.disk(base),onerror=remove_readonly) if atlas_install.disk(base).exists() else None)
        result = atlas_install.prepare(pack,base,'codex')
        installed = Path(result['package'])
        self.assertEqual(atlas_install.disk(installed/'references'/longfile.name).read_text(encoding='utf-8'),'long path evidence')
        self.assertTrue(atlas_install.disk(base/'.agents/plugins/marketplace.json').is_file())


if __name__ == "__main__": unittest.main()
