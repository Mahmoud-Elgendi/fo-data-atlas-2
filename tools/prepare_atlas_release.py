"""Create a new, plugin-only source publication folder; never stage the app workspace."""
import argparse
from pathlib import Path
import shutil
import zipfile
import json

ROOT = Path(__file__).resolve().parents[1]


def prepare(pack, output, project=ROOT):
    pack, output = Path(pack).resolve(), Path(output).resolve()
    if output.is_relative_to(pack):
        raise ValueError('Source staging must be outside the plugin package.')
    if output.exists():
        raise ValueError('Choose a new source output; earlier candidates are preserved.')
    output.mkdir(parents=True)
    version=json.loads((pack/'.codex-plugin/plugin.json').read_text(encoding='utf-8'))['version']
    documentation=project/('docs/plugin-release-'+version)
    if not documentation.is_dir(): documentation=project/'docs/plugin-release-2026-11-08'
    for path in pack.rglob('*'):
        relative = path.relative_to(pack)
        if (not path.is_file() or any(p in {'dist','__pycache__','.git'} for p in relative.parts)
                or path.suffix in {'.sqlite','.pyc'} or '.sqlite-' in path.name
                or path.name == 'package-manifest.json' or '.build.sqlite' in path.name):
            continue
        target = output / 'plugins' / 'fo-data-atlas' / relative
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(path,target)
    for name in ('build_atlas_plugin.py','package_atlas_plugin.py','prepare_atlas_release.py','verify_atlas_plugin.py','build_atlas_metadata_packs.py','build_atlas_tools_release.py'):
        target = output/'tools'/name
        target.parent.mkdir(exist_ok=True)
        shutil.copyfile(project/'tools'/name,target)
    for name in ('test_atlas_plugin.py','test_atlas_github_release.py','test_atlas_sql_lineage.py','test_atlas_metadata_cache.py','test_atlas_cli.py','test_atlas_cli.cjs','test_atlas_workflow_templates.py'):
        target=output/'tests'/name
        target.parent.mkdir(exist_ok=True)
        shutil.copyfile(project/'tests'/name,target)
    shutil.copytree(documentation,output/('docs/release-'+version))
    launcher=json.loads((project/'tools/atlas-npx-package.json').read_text(encoding='utf-8'))
    if launcher['version'] != version: raise ValueError('npm launcher and plugin versions differ.')
    (output/'package.json').write_text(json.dumps(launcher,indent=2)+'\n',encoding='utf-8')
    shutil.copyfile(project/'tools/atlas-npx-package.json',output/'tools/atlas-npx-package.json')
    shutil.copyfile(pack/'RELEASE-NOTES.md',output/'release-notes.md')
    (output/'.gitignore').write_text('**/__pycache__/\n*.pyc\n*.sqlite*\n*.zip\n**/dist/\ntest-evidence/\n**/reference-pack*.json\n',encoding='utf-8')
    text='''# F&O Data Atlas

Private offline D365 F&O metadata and SQL assistant by Mahmoud Elgendi.

This repository contains the small plugin source, tests and release documentation.
The full offline database is distributed as a versioned GitHub Release asset.

## Install

Use Node.js 22+, Git, Python 3.10+ and authenticated GitHub CLI with read access.
One-time authentication: `gh auth login`, then `gh auth setup-git`.
After this version is published, run from your intended Fabric project:

```powershell
npx --yes --package="git+https://github.com/Mahmoud-Elgendi/fo-data-atlas-2.git#vVERSION" fo-data-atlas
```

This is a private Git-backed command, not an npm registry publication or skills-add installation.
For an extracted source package, Node.js/Git are optional; use the Python route:

```powershell
python plugins/fo-data-atlas/scripts/github_release.py install
```

It downloads/verifies the tools and selected Core/Full metadata, then opens the
AI-tool/global-or-project setup wizard. Follow native host activation instructions.
Installed evidence works offline; uncached originals require the Full profile.
Use the same command to update; existing project settings and previous versions stay.

See [plugin guide](plugins/fo-data-atlas/README.md),
[release notes](release-notes.md), [release plan](docs/release-0.2.0/PLAN.md)
and [terminal workflow](docs/release-0.2.0/TERMINAL.md).

## Test source

```powershell
python -m unittest discover -s tests -v
python plugins/fo-data-atlas/scripts/validate_package.py --source-only
```

The source checkout alone intentionally lacks references/atlas.sqlite; obtain the
complete release package before attempting metadata queries or offline setup.
Metadata baselines and plugin versions are separate. No new .49 collection is claimed.
'''
    text=text.replace('release-0.2.0','release-'+version).replace('vVERSION','v'+version)
    (output/'README.md').write_text(text,encoding='utf-8')
    (output/'.gitattributes').write_text('* -text\n',encoding='ascii')
    files=[p for p in output.rglob('*') if p.is_file()]
    if any('.sqlite' in p.name or p.suffix=='.zip' for p in files):
        raise ValueError('Generated source contains a payload that belongs in a release asset.')
    return {'source':str(output),'files':len(files),'bytes':sum(p.stat().st_size for p in files)}


if __name__=='__main__':
    import json
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pack',type=Path,default=ROOT/'plugins/fo-data-atlas')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--zip',type=Path)
    args=parser.parse_args()
    result=prepare(args.pack,args.output)
    if args.zip:
        with zipfile.ZipFile(args.zip,'x',compression=zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(args.output.rglob('*')):
                if path.is_file(): archive.write(path,'fo-data-atlas-source/'+path.relative_to(args.output).as_posix())
        with zipfile.ZipFile(args.zip) as archive:
            if archive.testzip(): raise ValueError('Source ZIP integrity failed.')
        result['archive']=str(args.zip)
    print(json.dumps(result,indent=2))
