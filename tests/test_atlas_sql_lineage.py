"""Exported SQL lineage stays in its snapshot and preserves definitions/gaps."""
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'plugins/fo-data-atlas/scripts'))
import sql_lineage
import lint_sql


class SqlLineageTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        self.db.row_factory = sqlite3.Row
        self.addCleanup(self.db.close)
        self.db.executescript('CREATE TABLE documents(id TEXT,source TEXT,path TEXT,kind TEXT,name TEXT,sha256 TEXT); CREATE TABLE blobs(sha256 TEXT,content BLOB);')

    def add(self, key, name, definition=None, targets=(), kind='VIEW', source='snapshot-a', database='AxDB', extra=(), encrypted=0):
        dependencies = [{'source_key':key, 'target_key':target, 'referenced_name':target,
                         'referenced_schema':'dbo', 'referenced_database':None,
                         'referenced_server':None, 'is_ambiguous':0} for target in targets] + list(extra)
        payload = {'object': {'id':key, 'name':name, 'schema_name':'dbo', 'database_name':database,
                   'kind':kind, 'definition':definition, 'is_encrypted':encrypted}, 'dependencies':dependencies}
        raw = json.dumps(payload).encode()
        sha = hashlib.sha256(raw).hexdigest()
        identity = hashlib.sha256((source+key).encode()).hexdigest()[:32]
        self.db.execute('INSERT INTO documents VALUES (?,?,?,?,?,?)', (identity,source,key+'.json','SQL_OBJECT',name,sha))
        self.db.execute('INSERT INTO blobs VALUES (?,?)', (sha,zlib.compress(raw)))
        return identity

    def tree(self):
        table = self.add('AxDB:3','purchline',kind='USER_TABLE')
        child = self.add('AxDB:2','Child','CREATE VIEW dbo.Child AS SELECT * FROM dbo.purchline;\r\n', ['AxDB:3'])
        top = self.add('AxDB:1','Top','CREATE VIEW dbo.Top AS SELECT * FROM dbo.Child;\r\n',['AxDB:2'])
        self.add('AxDB:2','Child','WRONG SNAPSHOT',source='snapshot-b')
        return top,child,table

    def test_nested_chain_and_source_isolation(self):
        top, child, table = self.tree()
        result = sql_lineage.inspect(self.db,top)
        self.assertEqual(result['ordered_ids'], [table,child,top])
        self.assertTrue(result['source_definitions_complete'])
        self.assertFalse(result['deployment_ready'])
        self.assertEqual({n['source'] for n in result['nodes']},{'snapshot-a'})
        self.assertNotIn('WRONG SNAPSHOT',json.dumps(result))

    def test_export_defaults_to_root_then_optional_dependency_sql(self):
        top,child,table = self.tree()
        result = sql_lineage.inspect(self.db,top)
        parent = ROOT/'test-evidence'/'sql-lineage'
        parent.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=parent) as scratch:
            root = Path(scratch)
            first = sql_lineage.export(result,root/'single')
            self.assertEqual(len(first['sql_files']),1)
            expected = next(n['object']['definition'] for n in result['nodes'] if n['evidence_id']==top).encode()
            self.assertEqual((root/'single'/first['sql_files'][0]).read_bytes(),expected)
            full = sql_lineage.export(result,root/'full',True)
            self.assertEqual(len(full['sql_files']),2)
            self.assertTrue(full['sql_files'][0].startswith('source-Child'))
            with self.assertRaises(ValueError):
                sql_lineage.export(result,root/'full',True)

    def test_cycle_and_missing_definition_are_explicit(self):
        top = self.add('AxDB:1','Top','CREATE VIEW dbo.Top AS SELECT * FROM dbo.Child',['AxDB:2'])
        self.add('AxDB:2','Child',None,['AxDB:1'])
        result = sql_lineage.inspect(self.db,top)
        self.assertEqual({b['reason'] for b in result['blockers']},{'cycle','definition_missing_or_encrypted'})
        self.assertFalse(result['source_definitions_complete'])

    def test_table_internal_references_are_not_view_cycles(self):
        table = self.add('AxDB:3','purchline',targets=['AxDB:3'],kind='USER_TABLE')
        result = sql_lineage.inspect(self.db,table)
        self.assertTrue(result['source_definitions_complete'])
        self.assertIn('internal self-reference', result['edges'][0]['resolution_note'])

    def test_encrypted_and_different_database_require_review(self):
        encrypted = self.add('AxDB:4','Encrypted','encrypted-placeholder',encrypted=1)
        self.assertFalse(sql_lineage.inspect(self.db,encrypted)['source_definitions_complete'])
        top = self.add('AxDB:1','Top','SELECT 1',targets=['AxDW:2'])
        self.add('AxDW:2','Elsewhere','SELECT 2',database='AxDW')
        result = sql_lineage.inspect(self.db,top)
        self.assertEqual(result['blockers'][0]['reason'],'different_database_requires_mapping')
        self.assertEqual(len(result['nodes']),1)

    def test_unresolved_edges_never_resolve_from_other_snapshot(self):
        top = self.add('AxDB:1','Top','SELECT 1',['AxDB:999'])
        self.add('AxDB:999','Missing','SELECT 2',source='snapshot-b')
        result = sql_lineage.inspect(self.db,top)
        self.assertEqual(len(result['nodes']),1)
        self.assertEqual(result['blockers'][0]['reason'],'unresolved_reference')

    def test_qualified_ambiguous_reference_is_not_proven_external_access(self):
        top = self.add('AxDB:1','Top','SELECT 1',extra=[{'referenced_database':'doc','referenced_schema':'col',
            'referenced_name':'value','target_key':None,'is_ambiguous':1}])
        result = sql_lineage.inspect(self.db,top)
        self.assertEqual({b['reason'] for b in result['blockers']},{'ambiguous_reference','qualified_reference_requires_review'})

    def test_bounds_report_truncation(self):
        top,_,_=self.tree()
        for kwargs in ({'max_depth':1},{'max_nodes':1}):
            result=sql_lineage.inspect(self.db,top,**kwargs)
            self.assertTrue(result['truncated'])
            self.assertFalse(result['source_definitions_complete'])

    def test_tampered_evidence_rejected(self):
        top,_,_=self.tree()
        self.db.execute('UPDATE blobs SET content=?',(zlib.compress(b'tampered'),))
        with self.assertRaisesRegex(ValueError,'hash mismatch'):
            sql_lineage.inspect(self.db,top)


class CaseExceptionTests(unittest.TestCase):
    def test_exact_metadata_case_is_supported_without_waiving_other_identifiers(self):
        schema={('dbo','GlobalOptionsetMetadata'):{'LocalizedLabel':{},'EntityName':{},'Option':{}}}
        sql="SELECT m.LocalizedLabel FROM dbo.GlobalOptionsetMetadata AS m WHERE m.EntityName = 'purchtable'"
        self.assertTrue(lint_sql.check(sql,schema)['passed'])
        self.assertFalse(lint_sql.check(sql.replace('LocalizedLabel','localizedlabel'),schema)['passed'])
        self.assertFalse(lint_sql.check(sql.replace('SELECT','select'),schema)['passed'])

    def test_project_exception_requires_exact_schema_columns(self):
        schema={('ETL','Reference'):{'CurrencyCode':{}}}
        sql='SELECT r.CurrencyCode FROM ETL.Reference AS r'
        self.assertFalse(lint_sql.check(sql,schema)['passed'])
        self.assertTrue(lint_sql.check(sql,schema,case_exceptions=[{'schema':'ETL','table':'Reference','columns':['CurrencyCode']}])['passed'])
        with self.assertRaisesRegex(ValueError,'exact target'):
            lint_sql.check(sql,schema,case_exceptions=[{'schema':'ETL','table':'Reference','columns':['invented']}])


if __name__=='__main__': unittest.main()
