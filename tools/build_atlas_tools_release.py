"""Stage a small tools-only release bound to already built immutable metadata assets."""
import argparse
import json
from pathlib import Path
import shutil
from package_atlas_plugin import package

ROOT=Path(__file__).resolve().parents[1]


def build(source,catalog,output):
    source=source.resolve();output=output.resolve()
    if output.exists() or output.is_relative_to(source): raise ValueError('Choose a new output outside the plugin source.')
    output.mkdir(parents=True)
    staged=output/'fo-data-atlas';staged.mkdir()
    for path in source.rglob('*'):
        relative=path.relative_to(source)
        if (not path.is_file() or any(p in {'dist','__pycache__','.git'} for p in relative.parts)
                or path.suffix in {'.sqlite','.pyc'} or '.sqlite-' in path.name
                or path.name in {'package-manifest.json','reference-pack.json'}
                or relative.as_posix() in {'references/manifest.json','references/INDEX.md'}): continue
        target=staged/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target)
    shutil.copyfile(catalog,staged/'metadata-catalog.json')
    version=json.loads((staged/'.codex-plugin/plugin.json').read_text())['version']
    result=package(staged,output/f'fo-data-atlas-{version}.zip',tools=True)
    result['staged_tools']=str(staged)
    (output/'tools-build.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=ROOT/'plugins/fo-data-atlas')
    parser.add_argument('--metadata-catalog',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();build(args.source,args.metadata_catalog,args.output)
