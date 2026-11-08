"""Build derived core/full metadata assets without changing the original evidence DB."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'plugins/fo-data-atlas/scripts'))
import atlas
import build_references


def digest(path):
    return build_references.digest(path)


def core_payload(row):
    kind=row['kind'].casefold(); path=row['path'].replace('\\','/').casefold()
    if kind in {'sql_object','reference','manifest'}: return True
    if kind.startswith(('axtable','axview','axdataentityview','axedt','axenum')): return True
    if kind=='axlabelfile':
        return path.endswith('.xml') or '/en-us/' in path or path.endswith('.en-us.label.txt')
    return False


def core_database(original, output):
    if output.exists(): raise ValueError('Derived database already exists.')
    source=sqlite3.connect(original.resolve().as_uri()+'?mode=ro',uri=True)
    source.row_factory=sqlite3.Row
    target=sqlite3.connect(output)
    try:
        build_references.initialize(target)
        target.executemany('INSERT INTO sources VALUES(?,?,?,?)',source.execute('SELECT * FROM sources'))
        selected=set(); count=0; available=0
        for row in source.execute('SELECT rowid,* FROM documents ORDER BY rowid'):
            keep=core_payload(row)
            if keep: selected.add(row['sha256']); available+=1
            target.execute('INSERT INTO documents(rowid,id,source,path,kind,name,sha256,search_text) VALUES(?,?,?,?,?,?,?,?)',
                (row['rowid'],row['id'],row['source'],row['path'],row['kind'],row['name'],row['sha256'],row['search_text'] if keep else ''))
            count+=1
            if count%10000==0: target.commit()
        target.commit()
        for sha in sorted(selected):
            raw=source.execute('SELECT content FROM blobs WHERE sha256=?',(sha,)).fetchone()
            if raw is None: raise ValueError('Missing selected original blob.')
            target.execute('INSERT INTO blobs VALUES(?,?)',(sha,raw[0]))
        target.execute("CREATE VIRTUAL TABLE search USING fts5(name,search_text,content='documents',content_rowid='rowid')")
        target.execute("INSERT INTO search(search) VALUES('rebuild')")
        target.commit()
        available=target.execute('SELECT COUNT(*) FROM documents d WHERE EXISTS(SELECT 1 FROM blobs b WHERE b.sha256=d.sha256)').fetchone()[0]
        if target.execute('PRAGMA quick_check').fetchone()[0]!='ok': raise ValueError('Core SQLite check failed.')
        target.execute('PRAGMA wal_checkpoint(TRUNCATE)');target.execute('PRAGMA journal_mode=DELETE')
        return {'documents':count,'payload_documents':available,'unique_contents':len(selected),
                'sources':source.execute('SELECT COUNT(*) FROM sources').fetchone()[0]}
    finally:
        source.close();target.close()


def build(pack,output,repo,tag):
    output=output.resolve()
    if output.exists(): raise ValueError('Use a new metadata build directory.')
    output.mkdir(parents=True)
    original=pack/'references/atlas.sqlite'
    old=json.loads((pack/'references/manifest.json').read_text(encoding='utf-8'))
    fullhash=digest(original)
    if fullhash!=old['sqlite_sha256']: raise ValueError('Original evidence hash mismatch.')
    identity='snapshot-'+fullhash[:16]
    catalog={'format':1,'metadata_id':identity,'repository':repo,'release_tag':tag,'profiles':{}}
    for profile in ('core','full'):
        folder=output/profile; refs=folder/'references';refs.mkdir(parents=True)
        db=refs/'atlas.sqlite'
        if profile=='core': summary=core_database(original,db)
        else:
            shutil.copyfile(original,db)
            summary={key:old[key] for key in ('documents','unique_contents','sources')}
            summary['payload_documents']=summary['documents']
        dbhash=digest(db)
        manifest={**summary,'metadata_id':identity,'profile':profile,'sqlite_sha256':dbhash,
            'original_sqlite_sha256':fullhash,'core_policy':1,'runtime_validated':False,'business_reconciled':False,
            'coverage':'All original document identities remain discoverable; core contains SQL catalogs, table/view/entity/EDT/enum XML and English labels. Other payloads require full.' if profile=='core' else 'All original current evidence payloads available offline.'}
        (refs/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
        name=f'fo-atlas-metadata-{identity}-{profile}-{dbhash[:12]}.zip'; archive=output/name
        with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as bundle:
            bundle.write(db,'references/atlas.sqlite')
            bundle.write(refs/'manifest.json','references/manifest.json')
        with zipfile.ZipFile(archive) as bundle:
            if bundle.testzip(): raise ValueError('Metadata ZIP CRC failed.')
        catalog['profiles'][profile]={'asset':name,'sha256':digest(archive),'bytes':archive.stat().st_size,
            'sqlite_sha256':dbhash,'database_bytes':db.stat().st_size,**summary}
        print(profile,json.dumps(catalog['profiles'][profile]),flush=True)
    (output/'metadata-catalog.json').write_text(json.dumps(catalog,indent=2)+'\n',encoding='utf-8')
    return catalog


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pack',type=Path,default=ROOT/'plugins/fo-data-atlas')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--repo',default='Mahmoud-Elgendi/fo-data-atlas-2')
    parser.add_argument('--tag',default='v0.3.0')
    args=parser.parse_args(); build(args.pack,args.output,args.repo,args.tag)
