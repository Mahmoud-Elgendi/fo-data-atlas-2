"""Prepare private Codex/Claude marketplaces; asks for global or project-only scope."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import os
import stat
import time

ROOT = Path(__file__).resolve().parents[1]
NAME = "fo-data-atlas"
MARKET = "fo-data-atlas-private"


def disk(path):
    path = Path(path).resolve()
    if os.name == 'nt' and not str(path).startswith('\\\\?\\'):
        value = str(path)
        return Path('\\\\?\\UNC\\' + value[2:]) if value.startswith('\\\\') else Path('\\\\?\\' + value)
    return path


def promote(staged,target):
    staged,target=disk(staged),disk(target)
    # A new local staging copy may inherit a cloud folder's readonly attribute.
    if os.name=='nt': os.chmod(staged,stat.S_IWRITE)
    for attempt in range(5):
        if target.exists(): raise ValueError('Installation appeared during copy; existing files were preserved.')
        try:
            staged.rename(target)
            return
        except PermissionError:
            if attempt==4: raise
            time.sleep(0.1*(2**attempt))


class Cancelled(Exception):
    pass


def banner():
    width = 70
    print("\n+" + "=" * width + "+")
    for line in ("F & O   D A T A   A T L A S", "", "Created by Mahmoud Elgendi",
                 "Offline D365 F&O knowledge for Fabric SQL"):
        print("|" + line.center(width) + "|")
    print("+" + "=" * width + "+")
    version = read_json(ROOT / ".codex-plugin" / "plugin.json", {})["version"]
    print(f"  Setup {version}  |  Codex + Claude Code  |  Private package")
    print("  Includes offline references, query skills and SQL checks.")
    print("  No VM or database connection is needed. Enter Q to cancel.\n")


def choose(title, options, default):
    """Required choices retry in place; Enter accepts the displayed default."""
    print(title)
    for number, (value, label) in enumerate(options, 1):
        print(f"  [{number}] {label}" + (" (default)" if value == default else ""))
    while True:
        answer = input("Select a number: ").strip().lower()
        if answer in {"q", "quit", "cancel"}: raise Cancelled()
        if not answer: return default
        for number, (value, _) in enumerate(options, 1):
            if answer in {str(number), value}: return value
        print("Please select one of the listed numbers, or Q to cancel.")


def confirm(question):
    while True:
        answer = input(question + " [Y/n]: ").strip().lower()
        if answer in {"q", "quit", "cancel"}: raise Cancelled()
        if answer in {"", "y", "yes"}: return True
        if answer in {"n", "no"}: return False
        print("Please enter Y or N. Enter accepts Yes.")


def project_folder(initial=None):
    while True:
        default = initial or Path.cwd()
        answer = input(f"Fabric project folder [{default}]: ").strip().strip('"')
        if answer.lower() in {"q", "quit", "cancel"}: raise Cancelled()
        try:
            path = Path(answer).expanduser().resolve() if answer else Path(default).resolve()
            if path.is_relative_to(ROOT.resolve()):
                print("Choose your Fabric project folder outside this plugin package.")
            elif path.exists() and not path.is_dir():
                print("That path is a file. Please choose a project folder.")
            else: return path
        except (OSError, ValueError) as exc:
            print("Please choose a valid folder: " + str(exc))
        initial = None


def progress(message):
    print("  > " + message, flush=True)


def read_json(path, default):
    path = disk(path)
    return json.loads(path.read_text(encoding="utf-8-sig")) if path.exists() else default


def write_json(path, value):
    path = disk(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def prepare(pack, base, host, allow_upgrade=False, notify=None, metadata_pack=None):
    """Local, inspectable setup; never replace an existing installation or unrelated entry."""
    pack, base = Path(pack).resolve(), Path(base).resolve()
    modular = (pack/'metadata-catalog.json').is_file()
    reference_pack = Path(metadata_pack).resolve() if metadata_pack else pack
    if modular and metadata_pack is None:
        from metadata_cache import resolve
        reference_pack = resolve(pack)
    if not disk(reference_pack / "references" / "atlas.sqlite").is_file():
        raise ValueError("Build/copy the complete offline reference pack before installation.")
    notify = notify or (lambda message: None)
    version = read_json(pack / ".codex-plugin" / "plugin.json", {})["version"]
    distribution = base / ".fo-data-atlas" / ("distribution-" + version)
    target = distribution / "plugins" / NAME
    if target.is_relative_to(pack):
        raise ValueError("Choose the intended Fabric project with --project; installation cannot be inside the source package.")
    codex_path = base / ".agents" / "plugins" / "marketplace.json"
    marketplace = read_json(codex_path, {"name": MARKET, "plugins": []})
    relative = "./" + target.relative_to(base).as_posix()
    entry = {"name": NAME, "source": {"source": "local", "path": relative},
             "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
             "category": "Productivity"}
    if host in {"codex", "both"}:
        existing = next((e for e in marketplace.get("plugins", []) if e.get("name") == NAME), None)
        if existing and existing.get("source") != entry["source"]:
            oldpath = existing.get("source", {}).get("path", "")
            managed = re.fullmatch(r"\./\.fo-data-atlas/distribution-\d+\.\d+\.\d+/plugins/fo-data-atlas", oldpath)
            old = read_json(base / oldpath / ".codex-plugin" / "plugin.json", {}) if managed else {}
            older = old.get("version", "")
            older_version = tuple(map(int, older.split("."))) if re.fullmatch(r"\d+\.\d+\.\d+", older) else ()
            if not allow_upgrade or not managed or old.get("name") != NAME or not older_version or older_version >= tuple(map(int, version.split("."))):
                raise ValueError("An Atlas marketplace entry points elsewhere; review it or use --upgrade for a managed earlier version.")
    notify("Verifying the offline reference checksum...")
    reference = read_json(reference_pack / "references" / "manifest.json", {})
    if modular:
        catalog=read_json(pack/'metadata-catalog.json',{})
        desc=catalog.get('profiles',{}).get(reference.get('profile'),{})
        if reference.get('metadata_id')!=catalog.get('metadata_id') or reference.get('sqlite_sha256')!=desc.get('sqlite_sha256'):
            raise ValueError('Selected metadata is incompatible with this tools catalog.')
    fingerprint = hashlib.sha256()
    with disk(reference_pack / "references" / "atlas.sqlite").open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""): fingerprint.update(chunk)
    if fingerprint.hexdigest() != reference.get("sqlite_sha256"):
        raise ValueError("Reference payload does not match its publication manifest; installation stopped.")
    if target.exists():
        notify("Checking the existing installation...")
        # An identical rerun is safe; do not silently keep an old/different reference snapshot.
        original = reference
        installed = read_json(target / "references" / "manifest.json", {})
        if not modular and (not original or original != installed):
            raise ValueError("This version is already installed with different references; use a new version or destination.")
        # Compare scripts and skill/rule content as well as reference identity.
        for path in pack.rglob("*"):
            if path.is_file() and path.suffix != ".pyc" and "__pycache__" not in path.parts and "dist" not in path.relative_to(pack).parts:
                destination = target / path.relative_to(pack)
                if path.name == "atlas.sqlite": continue
                if not destination.exists() or destination.read_bytes() != path.read_bytes():
                    raise ValueError("Installed package differs; preserve it and select a new package version.")
    else:
        notify("Copying the small tools package; metadata stays in the shared cache." if modular else "Copying the package. The offline reference file is large; please wait...")
        disk(target.parent).mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='.atlas-install-', dir=disk(target.parent)) as scratch:
            staged = Path(scratch) / NAME
            shutil.copytree(disk(pack), staged, ignore=shutil.ignore_patterns("__pycache__", "dist", "*.pyc", "*.build.sqlite*"))
            if not modular:
                copied = hashlib.sha256()
                with (staged / 'references' / 'atlas.sqlite').open('rb') as handle:
                    for chunk in iter(lambda: handle.read(1024 * 1024), b''): copied.update(chunk)
                if copied.hexdigest() != reference['sqlite_sha256']:
                    raise ValueError('Copied offline payload hash mismatch; registration was not changed.')
            promote(staged,target)
    if modular:
        from metadata_cache import activate
        activate(target,reference_pack)
    result = {"package": str(target), "completed": ["Package and offline metadata available and checked"], "next_steps": []}
    if host in {"codex", "both"}:
        notify("Preparing the Codex private marketplace...")
        if existing:
            existing.update(entry)
        else: marketplace["plugins"].append(entry)
        write_json(codex_path, marketplace)
        result["completed"].append("Registered Codex local marketplace entry")
        result["next_steps"].append("Refresh/restart Codex, open the local Plugins Directory, install F&O Data Atlas, and verify its skills in a new chat.")
    if host in {"claude", "both"}:
        notify("Preparing the Claude Code private marketplace...")
        write_json(distribution / ".claude-plugin" / "marketplace.json", {
            "name": MARKET, "owner": {"name": "365 Xperts"},
            "plugins": [{"name": NAME, "source": "./plugins/" + NAME, "description": "Offline F&O evidence and Fabric SQL skills."}]})
        result["claude_marketplace"] = str(distribution)
    result["host_load_verified"] = False
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", choices=("codex", "claude", "both"))
    parser.add_argument("--scope", choices=("global", "project"))
    parser.add_argument("--project", type=Path)
    parser.add_argument("--interactive", action="store_true", help="Show the setup wizard, preview and Y/n confirmation.")
    parser.add_argument("--upgrade", action="store_true", help="Allow updating an earlier Atlas-managed marketplace entry; keep its files.")
    parser.add_argument('--metadata-profile',choices=('core','full'))
    parser.add_argument('--cache-root',type=Path)
    parser.add_argument('--local-pack',type=Path,help='Seed cache from a matching local metadata pack; no metadata download.')
    args = parser.parse_args(argv)
    interactive = args.interactive or not (args.host and args.scope)
    installation_started = False
    try:
        if interactive: banner()
        host = args.host or choose("1. Choose your AI tool", (("codex", "Codex"), ("claude", "Claude Code"), ("both", "Both tools")), "both")
        scope = args.scope or choose("\n2. Choose where to install", (("project", "Current project only"), ("global", "Global - available across your projects")), "project")
        project = args.project
        if scope == "project" and project is None:
            if interactive: project = project_folder()
            else: project = Path.cwd()
        base = Path.home() if scope == "global" else project.resolve()
        catalog=read_json(ROOT/'metadata-catalog.json',None)
        profile=args.metadata_profile or 'core'
        if catalog and interactive and not args.metadata_profile:
            # Preserve an existing same-baseline profile when it is explicitly configured.
            previous=read_json(ROOT/'reference-pack.json',{})
            if not previous:
                candidates=list((base/'.fo-data-atlas').glob('distribution-*'))
                candidates=[p for p in candidates if re.fullmatch(r'distribution-\d+\.\d+\.\d+',p.name)]
                for folder in sorted(candidates,key=lambda p:tuple(map(int,p.name.removeprefix('distribution-').split('.'))),reverse=True):
                    choice=read_json(folder/'plugins'/NAME/'reference-pack.json',{})
                    if choice.get('metadata_id')==catalog['metadata_id']:
                        previous=choice;break
            if previous.get('metadata_id')==catalog['metadata_id']: profile=previous.get('profile','core')
            profile=choose('\n3. Offline metadata',(('core','Core - SQL, tables, enums and English labels'),('full','Full offline - all metadata, X++ and languages')),profile)
        if catalog and interactive:
            print(f"  Metadata: {profile}; download only if uncached: {catalog['profiles'][profile]['bytes']/1024**2:.1f} MiB.")
        if interactive:
            version = read_json(ROOT / ".codex-plugin" / "plugin.json", {})["version"]
            print("\n4. Review your setup" if catalog else "\n3. Review your setup")
            print("  Tool(s):  " + {"codex": "Codex", "claude": "Claude Code", "both": "Codex + Claude Code"}[host])
            print("  Scope:    " + ("Global" if scope == "global" else "Current project only"))
            print("  Folder:   " + str(base))
            print("  Version:  " + version)
            print("  Existing earlier Atlas copies will be kept.")
            print("  Atlas-managed registration may be updated to this version.")
            print("  Host activation steps will be shown after setup.\n")
            if not confirm("Continue with this setup?"): raise Cancelled()
            print("\n5. Prepare installation" if catalog else "\n4. Prepare installation", flush=True)
        installation_started = True
        options={'allow_upgrade':args.upgrade or interactive,'notify':progress if interactive else None}
        if catalog:
            from metadata_cache import acquire
            options['metadata_pack']=acquire(catalog,profile,args.cache_root,args.local_pack)
        result = prepare(ROOT, base, host, **options)
        if catalog: result['metadata_profile']=profile
        result["scope"] = scope
        result['start_here'] = {}
        if host in {'codex', 'both'}:
            result['start_here']['codex'] = {
                'setup': '$fo-atlas-setup\nSet up this Fabric project. Guide me one step at a time.',
                'view': '$fo-atlas-query\nShow the SQL behind CustCustomerV3Entity and list its underlying views and tables.',
                'query': '$fo-atlas-query\nCreate purchase-order-lines. Suggest the fields first.'}
        if host in {'claude', 'both'}:
            result['start_here']['claude'] = {
                'setup': '/fo-data-atlas:fo-atlas-setup\nSet up this Fabric project. Guide me one step at a time.',
                'view': '/fo-data-atlas:fo-atlas-query\nShow the SQL behind CustCustomerV3Entity and list its underlying views and tables.',
                'query': '/fo-data-atlas:fo-atlas-query\nCreate purchase-order-lines. Suggest the fields first.'}
        if "claude_marketplace" in result:
            result["claude_commands"] = [
                ["claude", "plugin", "marketplace", "add", result["claude_marketplace"]],
                ["claude", "plugin", "install", NAME + "@" + MARKET, "--scope", "user" if scope == "global" else "project"]]
            result["next_steps"].append("Run the listed Claude commands from the intended project, then verify /fo-data-atlas:fo-atlas-query is available.")
        if interactive:
            print("\n+----------------------------------------------------------------------+")
            print("  SETUP PREPARED - F&O Data Atlas")
            print("  Created by Mahmoud Elgendi")
            print("+----------------------------------------------------------------------+")
            print("\nInstalled files: " + result["package"])
            print("\nNext steps:")
            for number, step in enumerate(result["next_steps"], 1): print(f"  {number}. {step}")
            if result.get("claude_commands"):
                print("\nClaude Code commands (run from your Fabric project):")
                for command in result["claude_commands"]:
                    print("  " + " ".join('"' + value + '"' if any(c in value for c in ' &|<>^()%') else value for value in command))
                print("  If this private marketplace is already registered at an older path,")
                print("  remove that old registration before adding the new path.")
            print("\nSTART HERE - after activating the plugin, open your project and a new chat.")
            for tool, prompts in result['start_here'].items():
                print('\n  ' + {'codex': 'Codex', 'claude': 'Claude Code'}[tool] + ' - paste this to set up your Fabric project:')
                for line in prompts['setup'].splitlines(): print('    ' + line)
                print('  Or inspect an exported view immediately (no Fabric CSV needed):')
                for line in prompts['view'].splitlines(): print('    ' + line)
                print('  After project setup, request a dataset:')
                for line in prompts['query'].splitlines(): print('    ' + line)
            print("\nYour schema and reporting rules stay with each Fabric project.")
        else: print(json.dumps(result, indent=2))
        return 0
    except Cancelled:
        print("\nSetup cancelled. No installation changes were made.")
        return 0
    except KeyboardInterrupt:
        print("\nSetup interrupted. Some prepared files may remain; earlier installations were kept."
              if installation_started else "\nSetup cancelled. No installation changes were made.")
        return 130
    except (ValueError, OSError, EOFError) as exc:
        print("\nSetup could not finish: " + str(exc) if interactive else json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__": raise SystemExit(main())
