"""Core/full coverage, verified shared cache and small tools upgrade behavior."""
from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import shutil
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch
import zlib

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'plugins/fo-data-atlas/scripts'))
import atlas
import build_references
import github_release
import install
import metadata_cache
from tools import build_atlas_metadata_packs as packs
from tools import package_atlas_plugin as packaging


class MetadataCacheTests(unittest.TestCase):
    def setUp(self):
        parent=ROOT/'test-evidence/metadata-cache';parent.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=parent);self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.original=self.root/'original';refs=self.original/'references';refs.mkdir(parents=True)
        db=sqlite3.connect(refs/'atlas.sqlite');build_references.initialize(db)
        db.execute('INSERT INTO sources VALUES(?,?,?,?)',('snapshot-a','Fixture','f'*64,'Fixture only'))
        self.ids={}
        records=[('SQL_OBJECT','AxDB:1.json','View',json.dumps({'object':{'id':'AxDB:1','name':'View','definition':'CREATE VIEW dbo.V AS SELECT 1;'},'dependencies':[]})),
                 ('AxTable','raw/AxTable/T.xml','T','<AxTable><Name>T</Name></AxTable>'),
                 ('AxLabelFile','raw/AxLabelFile/LabelResources/en-US/SYS.en-US.label.txt','SYS.en-US.label','@SYS1=Hello'),
                 ('AxClass','raw/AxClass/C.xml','C','<AxClass><Name>C</Name><Source>full original code</Source></AxClass>'),
                 ('AxLabelFile','raw/AxLabelFile/LabelResources/fr-FR/SYS.fr-FR.label.txt','SYS.fr-FR.label','@SYS1=Bonjour')]
        for kind,path,name,text in records:
            raw=text.encode();sha=hashlib.sha256(raw).hexdigest();identity=hashlib.sha256(path.encode()).hexdigest()[:32]
            self.ids[name]=identity
            db.execute('INSERT INTO blobs VALUES(?,?)',(sha,zlib.compress(raw)))
            db.execute('INSERT INTO documents VALUES(?,?,?,?,?,?,?)',(identity,'snapshot-a',path,kind,name,sha,name))
        db.execute("CREATE VIRTUAL TABLE search USING fts5(name,search_text,content='documents',content_rowid='rowid')")
        db.execute("INSERT INTO search(search) VALUES('rebuild')");db.commit();db.close()
        (refs/'manifest.json').write_text(json.dumps({'sqlite_sha256':github_release.sha(refs/'atlas.sqlite'),'documents':5,'unique_contents':5,'sources':1}))
        self.build=self.root/'assets'
        with redirect_stdout(io.StringIO()): self.catalog=packs.build(self.original,self.build,'owner/repo','v0.3.0')
        self.cache=self.root/'cache'

    def fake_download(self,args,timeout):
        asset=args[args.index('--pattern')+1]
        shutil.copyfile(self.build/asset,Path(args[-1])/asset)
        return ''

    def tools(self,name='tools',version='0.3.0'):
        folder=self.root/name;folder.mkdir()
        for host in ('.codex-plugin','.claude-plugin'):
            (folder/host).mkdir();(folder/host/'plugin.json').write_text(json.dumps({'name':'fo-data-atlas','version':version,'skills':'./skills/'}))
        (folder/'scripts').mkdir();(folder/'scripts/install.py').write_text('# fixture')
        (folder/'metadata-catalog.json').write_text(json.dumps(self.catalog))
        return folder

    def test_core_discovers_all_but_missing_payload_is_explicit(self):
        with atlas.connect(self.build/'core') as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM documents').fetchone()[0],5)
            hit=atlas.search(db,'C','snapshot-a')[0]
            self.assertEqual(hit['available_offline'],0)
            with self.assertRaisesRegex(ValueError,'Full offline'):
                atlas.document(db,self.ids['C'])
            self.assertIn(b'CREATE VIEW',atlas.document(db,self.ids['View'])[1])
            self.assertIn(b'Hello',atlas.document(db,self.ids['SYS.en-US.label'])[1])
        with atlas.connect(self.build/'full') as db:
            self.assertIn(b'full original code',atlas.document(db,self.ids['C'])[1])

    def test_cache_reused_offline_across_projects_and_tool_versions(self):
        with patch.object(github_release,'gh',side_effect=self.fake_download) as network:
            cached=metadata_cache.acquire(self.catalog,'core',self.cache)
            self.assertEqual(network.call_count,1)
        with patch.object(github_release,'gh',side_effect=AssertionError('No repeat metadata download')):
            self.assertEqual(metadata_cache.acquire(self.catalog,'core',self.cache),cached)
        a=self.tools();b=self.tools('new-tools','0.3.1')
        project=self.root/'project'
        first=install.prepare(a,project,'codex',metadata_pack=cached)
        second=install.prepare(b,project,'codex',allow_upgrade=True,metadata_pack=cached)
        for result in (first,second):
            target=Path(result['package']);self.assertFalse((target/'references/atlas.sqlite').exists())
            with atlas.connect(target) as db: self.assertIn(b'CREATE VIEW',atlas.document(db,self.ids['View'])[1])
            self.assertEqual(metadata_cache.resolve(target),cached)

    def test_local_seed_and_profile_switch_keep_previous_cache(self):
        with patch.object(github_release,'gh',side_effect=AssertionError('Local seed must stay offline')):
            core=metadata_cache.acquire(self.catalog,'core',self.cache,self.build/'core')
            full=metadata_cache.acquire(self.catalog,'full',self.cache,self.original)
        tools=self.tools();metadata_cache.activate(tools,core)
        with atlas.connect(tools) as db:
            with self.assertRaisesRegex(ValueError,'Full offline'): atlas.document(db,self.ids['C'])
        metadata_cache.activate(tools,full)
        with atlas.connect(tools) as db: self.assertIn(b'original code',atlas.document(db,self.ids['C'])[1])
        self.assertTrue((core/'references/atlas.sqlite').is_file())

    def test_corrupt_cache_or_wrong_snapshot_rejected(self):
        cached=metadata_cache.acquire(self.catalog,'core',self.cache,self.build/'core')
        (cached/'references/atlas.sqlite').write_bytes(b'corrupt')
        with self.assertRaisesRegex(ValueError,'checksum'): metadata_cache.acquire(self.catalog,'core',self.cache)
        tools=self.tools()
        with self.assertRaisesRegex(ValueError,'incompatible'):
            install.prepare(tools,self.root/'wrong','codex',metadata_pack=self.original)

    def test_modular_tools_archive_needs_no_embedded_db(self):
        tools=self.tools();archive=self.root/'tools.zip'
        with redirect_stdout(io.StringIO()): packaging.package(tools,archive,tools=True)
        expanded=github_release.extract_verified(archive,self.root/'expanded','0.3.0')
        self.assertTrue((expanded/'metadata-catalog.json').is_file())
        self.assertFalse((expanded/'references/atlas.sqlite').exists())

    def test_cancelled_setup_does_not_download_metadata(self):
        tools=self.tools()
        with patch.object(install,'ROOT',tools),patch('builtins.input',side_effect=['1','n']),patch.object(metadata_cache,'acquire') as network,redirect_stdout(io.StringIO()):
            self.assertEqual(install.main(['--host','codex','--scope','project','--project',str(self.root/'cancelled'),'--interactive']),0)
        network.assert_not_called()

    def test_existing_full_choice_is_default_for_same_baseline_upgrade(self):
        full=metadata_cache.acquire(self.catalog,'full',self.cache,self.original)
        project=self.root/'project';install.prepare(self.tools(),project,'codex',metadata_pack=full)
        updated=self.tools('updated-tools','0.3.1')
        output=io.StringIO()
        with patch.object(install,'ROOT',updated),patch('builtins.input',side_effect=['','n']),redirect_stdout(output):
            self.assertEqual(install.main(['--host','codex','--scope','project','--project',str(project),'--interactive']),0)
        self.assertIn('Full offline - all metadata, X++ and languages (default)',output.getvalue())

    def test_failed_metadata_download_does_not_replace_active_full_profile(self):
        full=metadata_cache.acquire(self.catalog,'full',self.cache,self.original)
        tools=self.tools();metadata_cache.activate(tools,full)
        def corrupt(args,timeout):
            (Path(args[-1])/args[args.index('--pattern')+1]).write_bytes(b'bad download')
        with patch.object(github_release,'gh',side_effect=corrupt),patch('builtins.input',return_value='y'),redirect_stdout(io.StringIO()):
            self.assertEqual(metadata_cache.main(['install','--pack',str(tools),'--profile','core','--cache-root',str(self.cache)]),2)
        self.assertEqual(metadata_cache.resolve(tools),full)

    def test_scripted_setup_is_json_only_and_uses_local_metadata(self):
        tools=self.tools();output=io.StringIO()
        with patch.object(install,'ROOT',tools),patch('builtins.input',side_effect=AssertionError('Unexpected prompt')),redirect_stdout(output):
            code=install.main(['--host','codex','--scope','project','--project',str(self.root/'scripted'),
                '--metadata-profile','core','--cache-root',str(self.cache),'--local-pack',str(self.build/'core')])
        self.assertEqual(code,0)
        result=json.loads(output.getvalue())
        self.assertEqual(result['metadata_profile'],'core')
        self.assertEqual(result['scope'],'project')


if __name__=='__main__': unittest.main()
