"""Versioned shared metadata cache. Network access occurs only on explicit acquisition."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile
import zipfile

import github_release as github


def default_cache():
    return Path.home()/'.fo-data-atlas'/'metadata'


def resolve(pack):
    pack=Path(pack).resolve()
    pointer=github.read_json(pack/'reference-pack.json',{})
    if pointer:
        target=Path(pointer['pack_root'])
        manifest=github.read_json(target/'references/manifest.json',{})
        if any(manifest.get(k)!=pointer.get(k) for k in ('metadata_id','profile','sqlite_sha256')):
            raise ValueError('Metadata cache identity changed; rerun setup before querying.')
        if not github.disk(target/'references/atlas.sqlite').is_file():
            raise ValueError('Selected metadata cache is missing; rerun setup.')
        return target
    if github.disk(pack/'references/atlas.sqlite').is_file(): return pack
    raise ValueError('Metadata not configured. Run setup and choose Core or Full offline.')


def validate(root,catalog,profile):
    expected=catalog['profiles'][profile]
    manifest=github.read_json(root/'references/manifest.json',{})
    if (manifest.get('metadata_id')!=catalog['metadata_id'] or manifest.get('profile')!=profile
            or manifest.get('sqlite_sha256')!=expected['sqlite_sha256']):
        raise ValueError('Metadata manifest does not match the selected snapshot/profile.')
    db=github.disk(root/'references/atlas.sqlite')
    if not db.is_file() or github.sha(db)!=expected['sqlite_sha256']:
        raise ValueError('Metadata database checksum mismatch.')
    return root


def acquire(catalog,profile,cache_root=None,local_pack=None):
    if profile not in {'core','full'} or profile not in catalog.get('profiles',{}):
        raise ValueError('Select an available core/full metadata profile.')
    identity=catalog['metadata_id']; desc=catalog['profiles'][profile]
    if not re.fullmatch(r'[A-Za-z0-9_-]+',identity) or not re.fullmatch(r'[a-f0-9]{64}',desc['sqlite_sha256']):
        raise ValueError('Invalid metadata identity.')
    root=Path(cache_root or default_cache()).resolve()
    final=root/identity/(profile+'-'+desc['sqlite_sha256'][:16])
    if github.disk(final).exists():
        validate(final,catalog,profile)
        return final
    github.disk(final.parent).mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.metadata-',dir=github.disk(final.parent)) as scratch:
        scratch=Path(scratch); staged=scratch/'pack'
        if local_pack:
            source=Path(local_pack)
            # Reuse an existing full 0.2.0 pack when its exact DB matches this profile.
            db=github.disk(source/'references/atlas.sqlite')
            if not db.is_file() or github.sha(db)!=desc['sqlite_sha256']:
                raise ValueError('Local metadata does not match the selected profile hash.')
            (staged/'references').mkdir(parents=True)
            shutil.copyfile(db,staged/'references/atlas.sqlite')
            source_manifest=github.read_json(source/'references/manifest.json',{})
            source_manifest.update({'metadata_id':identity,'profile':profile,'sqlite_sha256':desc['sqlite_sha256']})
            (staged/'references/manifest.json').write_text(json.dumps(source_manifest,indent=2)+'\n',encoding='utf-8')
        else:
            asset=desc['asset']
            github.version_tuple(catalog['release_tag'])
            if github.safe_relative(asset).name!=asset: raise ValueError('Metadata asset must be a filename.')
            github.gh(['release','download',catalog['release_tag'],'--repo','github.com/'+github.repository(catalog['repository']),
                       '--pattern',asset,'--dir',str(scratch)],timeout=3600)
            archive=scratch/asset
            if archive.stat().st_size!=desc['bytes'] or github.sha(archive)!=desc['sha256']:
                raise ValueError('Metadata ZIP size/hash mismatch.')
            with zipfile.ZipFile(archive) as bundle:
                entries=bundle.infolist()
                if sorted(e.filename for e in entries)!=['references/atlas.sqlite','references/manifest.json']:
                    raise ValueError('Unexpected metadata archive contents.')
                if sum(e.file_size for e in entries)>16*1024**3: raise ValueError('Metadata archive too large.')
                for entry in entries:
                    target=staged/github.safe_relative(entry.filename)
                    target.parent.mkdir(parents=True,exist_ok=True)
                    with bundle.open(entry) as inp,target.open('xb') as out: shutil.copyfileobj(inp,out,1024*1024)
        validate(staged,catalog,profile)
        if github.disk(final).exists(): validate(final,catalog,profile)
        else: staged.rename(github.disk(final))
    return final


def activate(pack,metadata_root):
    root=Path(metadata_root).resolve()
    manifest=github.read_json(root/'references/manifest.json',{})
    pointer={key:manifest[key] for key in ('metadata_id','profile','sqlite_sha256')}
    pointer['pack_root']=str(root)
    path=github.disk(Path(pack)/'reference-pack.json'); pending=path.with_suffix('.pending.json')
    pending.write_text(json.dumps(pointer,indent=2)+'\n',encoding='utf-8')
    pending.replace(path)
    return pointer


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('status','install'))
    parser.add_argument('--pack',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--profile',choices=('core','full'),default='core')
    parser.add_argument('--cache-root',type=Path)
    parser.add_argument('--local-pack',type=Path,help='Reuse verified local metadata without a network download.')
    args=parser.parse_args(argv)
    try:
        if args.command=='status':
            root=resolve(args.pack);print(json.dumps(github.read_json(root/'references/manifest.json',{}),indent=2));return 0
        catalog=github.read_json(args.pack/'metadata-catalog.json',{})
        desc=catalog['profiles'][args.profile]
        print(f"Metadata profile: {args.profile}; download if uncached: {desc['bytes']/1024**2:.1f} MiB.")
        if input('Install/activate this metadata profile? [Y/n]: ').strip().lower() not in {'','y','yes'}: return 0
        root=acquire(catalog,args.profile,args.cache_root,args.local_pack)
        print(json.dumps(activate(args.pack,root),indent=2));return 0
    except (OSError,ValueError,KeyError,zipfile.BadZipFile) as exc:
        print(json.dumps({'error':str(exc),'existing_metadata_preserved':True}));return 2


if __name__=='__main__': raise SystemExit(main())
