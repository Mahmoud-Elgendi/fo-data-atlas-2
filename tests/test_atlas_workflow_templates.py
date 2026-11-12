"""Portable template logic on synthetic SQLite fixtures, not Fabric compilation.

Only DATEADD's HOUR token is quoted for SQLite and implemented as a fixture UDF.
The workflow windows and resource join predicates are read from the shipped SQL.
"""
import datetime as dt
from pathlib import Path
import sqlite3
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / 'plugins/fo-data-atlas/examples'


def template(folder, name):
    text = (EXAMPLES / folder / name).read_text(encoding='utf-8')
    for key, value in {'timesheet_context_table_id': 900, 'submission_tracking_type_code': 23,
                       'utc_offset_hours': 3, 'label_language_code': 1033}.items():
        text = text.replace('{{' + key + '}}', str(value))
    return text.replace('DATEADD(HOUR,', "DATEADD('HOUR',")


class WorkflowTemplateTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        self.addCleanup(self.db.close)
        self.db.execute("ATTACH DATABASE ':memory:' AS dbo")
        def dateadd(unit, hours, value):
            self.assertEqual(unit, 'HOUR')
            return None if value is None else (dt.datetime.fromisoformat(value) + dt.timedelta(hours=hours)).isoformat(sep=' ')
        self.db.create_function('DATEADD', 3, dateadd)
        self.db.executescript('''
            CREATE TABLE dbo.workflowtrackingstatustable (
                partition INTEGER, recid INTEGER, contextcompanyid TEXT,
                contexttableid INTEGER, contextrecid INTEGER, IsDelete INTEGER);
            CREATE TABLE dbo.workflowtrackingtable (
                partition INTEGER, recid INTEGER, workflowtrackingstatustable INTEGER,
                trackingtype INTEGER, createddatetime TEXT, user TEXT, IsDelete INTEGER);
            CREATE TABLE dbo.tstimesheettable (
                partition INTEGER, recid INTEGER, dataareaid TEXT, tableid INTEGER,
                resource INTEGER, IsDelete INTEGER);
            INSERT INTO dbo.workflowtrackingstatustable VALUES
                (1,10,'ABC',900,101,NULL), (1,11,'abc',900,101,NULL),
                (1,12,'abc',901,101,NULL), (1,13,'abc',900,101,1),
                (2,10,'abc',900,101,NULL);
            INSERT INTO dbo.workflowtrackingtable VALUES
                (1,1,10,23,'2030-01-02 08:00:00','first-user',NULL),
                (1,2,11,23,'2030-01-03 08:00:00','later-user',NULL),
                (1,3,10,21,'2030-01-01 08:00:00','other-type',NULL),
                (1,4,12,23,'2030-01-01 08:00:00','other-table',NULL),
                (1,5,13,23,'2030-01-01 08:00:00','deleted-header',NULL),
                (1,6,10,23,'2030-01-01 08:00:00','deleted-event',1),
                (2,7,10,23,'2030-01-01 08:00:00','other-partition',NULL);
            INSERT INTO dbo.tstimesheettable VALUES
                (1,101,'abc',900,NULL,NULL), (1,202,'abc',900,NULL,NULL);
        ''')
        self.sql = template('timesheet-first-submission-template', 'timesheet-first-submission.sql')
        self.cte = self.sql.split('\nSELECT\n    UPPER(tst.dataareaid)', 1)[0]

    def test_first_submission_across_instances_pairs_original_user_and_normalizes_company(self):
        rows = self.db.execute(self.cte + '''
            SELECT SourcePartition, DocumentRecId, StartTime, [User]
            FROM WorkflowSubmission WHERE SubmissionRank=1 ORDER BY SourcePartition
        ''').fetchall()
        self.assertEqual(rows, [(1,101,'2030-01-02 11:00:00','first-user'),
                                (2,101,'2030-01-01 11:00:00','other-partition')])

    def test_missing_submission_preserves_timesheet(self):
        join = self.sql.split('FROM dbo.tstimesheettable AS tst', 1)[1].split('LEFT JOIN (', 1)[0]
        rows = self.db.execute(self.cte + '\nSELECT tst.recid, w.StartTime, w.[User]\n'
                               + 'FROM dbo.tstimesheettable AS tst' + join
                               + 'WHERE tst.IsDelete IS NULL ORDER BY tst.recid').fetchall()
        self.assertEqual(rows, [(101,'2030-01-02 11:00:00','first-user'), (202,None,None)])

    def test_tied_submissions_use_event_recid(self):
        self.db.execute("INSERT INTO dbo.workflowtrackingtable VALUES (1,0,11,23,'2030-01-02 08:00:00','tie-winner',NULL)")
        row = self.db.execute(self.cte + '''
            SELECT [User] FROM WorkflowSubmission WHERE SourcePartition=1 AND SubmissionRank=1
        ''').fetchone()
        self.assertEqual(row, ('tie-winner',))

    def test_next_event_uses_all_retained_types_and_never_crosses_instance_partition(self):
        sql = template('workflow-history-template', 'workflow-history.sql')
        cte = sql.split('\nSELECT\n    h.instancenumber', 1)[0]
        rows = self.db.execute(cte + '''
            SELECT WorkflowEventRecId, EventSequence, EndTime
            FROM WorkflowEvents WHERE SourcePartition=1 AND WorkflowHistoryRecId=10
            ORDER BY EventSequence
        ''').fetchall()
        self.assertEqual(rows, [(3,1,'2030-01-02 11:00:00'), (1,2,None)])

    def test_resource_polymorphic_company_partition_and_deletion_constraints(self):
        self.db.executescript('''
            DELETE FROM dbo.tstimesheettable;
            CREATE TABLE dbo.resresourceidentifier (recid INTEGER, partition INTEGER,
                refrecid INTEGER, reftableid INTEGER, IsDelete INTEGER);
            CREATE TABLE dbo.wrkctrtable (recid INTEGER, tableid INTEGER, partition INTEGER,
                dataareaid TEXT, worker INTEGER, IsDelete INTEGER);
            CREATE TABLE dbo.hcmworker (recid INTEGER, partition INTEGER, personnelnumber TEXT, IsDelete INTEGER);
            INSERT INTO dbo.tstimesheettable VALUES
                (1,101,'abc',900,11,NULL), (1,102,'abc',900,12,NULL),
                (1,103,'abc',900,13,NULL), (1,104,'abc',900,14,NULL),
                (1,105,'abc',900,15,NULL), (2,106,'abc',900,11,NULL);
            INSERT INTO dbo.resresourceidentifier VALUES
                (11,1,21,700,NULL), (12,1,21,999,NULL), (13,1,22,700,NULL),
                (14,1,23,700,NULL), (15,1,24,700,NULL), (11,2,21,700,NULL);
            INSERT INTO dbo.wrkctrtable VALUES
                (21,700,1,'ABC',31,NULL), (22,700,1,'OTHER',31,NULL),
                (23,700,1,'abc',31,1), (24,700,1,'abc',32,NULL),
                (21,700,2,'abc',31,NULL);
            INSERT INTO dbo.hcmworker VALUES
                (31,1,'EMP-A',NULL), (31,2,'EMP-B',NULL), (32,1,'DELETED',1);
        ''')
        joins = self.sql[self.sql.index('LEFT JOIN dbo.resresourceidentifier'):].rstrip().removesuffix(';')
        query = 'SELECT tst.recid, hw.recid, hw.personnelnumber FROM dbo.tstimesheettable AS tst\n' + joins + ' ORDER BY tst.recid'
        self.assertEqual(self.db.execute(query).fetchall(), [
            (101,31,'EMP-A'), (102,None,None), (103,None,None),
            (104,None,None), (105,None,None), (106,31,'EMP-B')])


if __name__ == '__main__': unittest.main()
