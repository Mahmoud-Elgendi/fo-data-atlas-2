"""Check or download a complete Atlas GitHub release; installed SQL skills work offline.

Online operations use the authenticated GitHub CLI, without handling access tokens.
Run this file by itself for bootstrap, or from an installed plugin for updates.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPOSITORY = "Mahmoud-Elgendi/fo-data-atlas-2"
VERSION = re.compile(r"v?(\d+\.\d+\.\d+)\Z")


def disk(path):
    # Bootstrap is standalone, so it cannot import the installed package's helper.
    path = Path(path).resolve()
    if os.name == 'nt' and not str(path).startswith('\\\\?\\'):
        value = str(path)
        return Path('\\\\?\\UNC\\'+value[2:]) if value.startswith('\\\\') else Path('\\\\?\\'+value)
    return path


def read_json(path, default=None):
    path = disk(path)
    return json.loads(path.read_text(encoding="utf-8-sig")) if path.is_file() else default


def repository(value):
    value = value.removeprefix("https://github.com/").removesuffix(".git").rstrip("/")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*/[A-Za-z0-9][A-Za-z0-9_.-]*", value):
        raise ValueError("Use OWNER/REPOSITORY or its https://github.com URL.")
    return value


def version_tuple(value):
    match = VERSION.fullmatch(value)
    if not match:
        raise ValueError("Use a stable release tag vMAJOR.MINOR.PATCH.")
    return tuple(map(int, match[1].split(".")))


def find_gh():
    executable = shutil.which("gh")
    if not executable and os.name=='nt':
        for base in (os.environ.get('ProgramFiles',r'C:\Program Files'),os.environ.get('LOCALAPPDATA','')):
            if not base: continue
            for relative in ('GitHub CLI/gh.exe','Programs/GitHub CLI/gh.exe'):
                candidate=Path(base)/relative
                if candidate.is_file(): return str(candidate)
    return executable


def gh(arguments, timeout=30):
    executable = find_gh()
    if not executable:
        raise OSError("GitHub CLI was not found on PATH or in standard installation folders. Local/offline queries remain available.")
    result = subprocess.run([executable, *arguments], capture_output=True, text=True,
                            timeout=timeout, check=False)
    if result.returncode:
        # Avoid printing raw CLI responses or credentials supplied by a user's environment.
        raise OSError("GitHub request failed. Check connectivity, gh auth status and repository access.")
    return result.stdout


def release_info(repo, tag=None):
    endpoint = f"repos/{repository(repo)}/releases/"
    if tag:
        version_tuple(tag)
        endpoint += "tags/" + tag
    else:
        endpoint += "latest"
    data = json.loads(gh(["api", "--hostname", "github.com", endpoint]))
    if data.get("draft") or data.get("prerelease"):
        raise ValueError("Only published stable releases are supported.")
    tag = data["tag_name"]
    version_tuple(tag)
    version = VERSION.fullmatch(tag)[1]
    name = f"fo-data-atlas-{version}.zip"
    candidates = [asset for asset in data.get("assets", []) if asset.get("name") == name]
    if len(candidates) != 1:
        raise ValueError("Release must have one complete offline asset named " + name)
    asset = candidates[0]
    digest = asset.get("digest", "")
    if not re.fullmatch(r"sha256:[a-fA-F0-9]{64}", digest):
        raise ValueError("Release asset has no SHA256 digest; download is blocked.")
    size = asset.get("size")
    if not isinstance(size, int) or not 0 < size < 2 * 1024**3:
        raise ValueError("This downloader requires a single release ZIP smaller than 2 GiB.")
    return {"repository": repository(repo), "tag": tag, "version": version,
            "asset": name, "sha256": digest.split(":", 1)[1].lower(), "bytes": size}


def check(repo, current="0.0.0", tag=None):
    try:
        info = release_info(repo, tag)
        info["status"] = "available" if version_tuple(info["version"]) > version_tuple(current) else "current"
        return info
    except (OSError, ValueError, KeyError, subprocess.TimeoutExpired) as exc:
        return {"status": "unavailable", "continue_offline": True, "reason": str(exc)}


def sha(path):
    digest = hashlib.sha256()
    with disk(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_relative(value):
    # Reject Windows path aliases as well as POSIX traversal before writing anything.
    parts = PurePosixPath(value).parts
    if (not value or "\\" in value or value.startswith("/") or not parts
            or any(p in {".", ".."} or ":" in p or p.endswith((" ", "."))
                   or re.fullmatch(r"(?i)(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?", p)
                   for p in parts)):
        raise ValueError("Unsafe package path.")
    return Path(*parts)


def extract_verified(archive, destination, expected_version):
    """Validate the full immutable package before the caller promotes its directory."""
    destination = disk(destination)
    with zipfile.ZipFile(disk(archive)) as bundle:
        seen, entries, total = set(), [], 0
        for entry in bundle.infolist():
            relative = safe_relative(entry.filename.rstrip("/"))
            key = relative.as_posix().casefold()
            if key in seen:
                raise ValueError("Duplicate or case-colliding archive paths.")
            seen.add(key)
            if relative.parts[0] != "fo-data-atlas" or stat.S_ISLNK(entry.external_attr >> 16):
                raise ValueError("Unexpected archive root or symbolic link.")
            total += entry.file_size
            if total > 16 * 1024**3 or len(seen) > 100000:
                raise ValueError("Package exceeds extraction limits.")
            entries.append((entry, relative))
        for entry, relative in entries:
            target = destination / relative
            if entry.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with bundle.open(entry) as source, target.open("xb") as output:
                    shutil.copyfileobj(source, output, 1024 * 1024)

    return verify_pack(destination / 'fo-data-atlas', expected_version)


def verify_pack(pack, expected_version, origin=None):
    pack = disk(pack)
    if origin is not None and read_json(pack / 'release-origin.json', {}) != origin:
        raise ValueError('Cached download origin does not match the selected release.')
    manifest = read_json(pack / "package-manifest.json", {})
    if manifest.get("name") != "fo-data-atlas" or manifest.get("version") != expected_version:
        raise ValueError("Downloaded package identity does not match the release.")
    declared = set()
    for item in manifest.get("files", []):
        relative = safe_relative(item["path"])
        key = relative.as_posix().casefold()
        if key in declared or key == "package-manifest.json":
            raise ValueError("Duplicate/invalid package manifest entry.")
        declared.add(key)
        path = pack / relative
        if origin is not None and key == 'release-origin.json':
            continue
        if not path.is_file() or path.stat().st_size != item["bytes"] or sha(path) != item["sha256"]:
            raise ValueError("Package file integrity check failed: " + relative.as_posix())
    actual = {p.relative_to(pack).as_posix().casefold() for p in pack.rglob("*") if p.is_file()}
    generated = {'release-origin.json'} if origin is not None else set()
    if actual != declared | {"package-manifest.json"} | generated:
        raise ValueError("Package manifest does not cover every file.")
    for host in (".codex-plugin", ".claude-plugin"):
        identity = read_json(pack / host / "plugin.json", {})
        if identity.get("name") != "fo-data-atlas" or identity.get("version") != expected_version:
            raise ValueError("Host plugin identity mismatch.")
    if manifest.get('bundle_kind')=='tools':
        catalog=read_json(pack/'metadata-catalog.json',{})
        if catalog.get('format')!=1 or not {'core','full'}.issubset(catalog.get('profiles',{})):
            raise ValueError('Tools package has no valid core/full metadata catalog.')
    else:
        reference = read_json(pack / "references" / "manifest.json", {})
        db = pack / "references" / "atlas.sqlite"
        if not db.is_file() or sha(db) != reference.get("sqlite_sha256"):
            raise ValueError("Offline reference publication hash mismatch.")
    if not (pack / "scripts" / "install.py").is_file():
        raise ValueError("Release has no installer.")
    return pack


def download(info, destination):
    destination = Path(destination).resolve()
    disk(destination).mkdir(parents=True, exist_ok=True)
    final = destination / ("fo-data-atlas-" + info["version"])
    if disk(final).exists():
        verify_pack(final, info['version'], origin=info)
        return final
    with tempfile.TemporaryDirectory(prefix=".atlas-download-", dir=disk(destination)) as scratch:
        scratch = Path(scratch)
        gh(["release", "download", info["tag"], "--repo", "github.com/" + info["repository"],
            "--pattern", info["asset"], "--dir", str(scratch)], timeout=3600)
        archive = scratch / info["asset"]
        if not archive.is_file() or archive.stat().st_size != info["bytes"] or sha(archive) != info["sha256"]:
            raise ValueError("Release ZIP failed its GitHub size/SHA256 check.")
        pack = extract_verified(archive, scratch / "expanded", info["version"])
        # The repository identity is already validated; no credential is persisted.
        (pack / "release-origin.json").write_text(json.dumps(info, indent=2) + "\n", encoding="utf-8")
        pack.rename(disk(final))
    return final


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "download", "install"))
    parser.add_argument("--repo", help="OWNER/REPOSITORY; defaults to the package release origin.")
    parser.add_argument("--tag", help="Pin a specific stable package release instead of latest.")
    parser.add_argument("--destination", type=Path, default=Path.home() / ".fo-data-atlas" / "downloads")
    args = parser.parse_args(argv)
    origin = read_json(ROOT / "release-origin.json", {})
    identity = read_json(ROOT / ".codex-plugin" / "plugin.json", {})
    repo = args.repo or origin.get("repository") or DEFAULT_REPOSITORY
    if not repo:
        print(json.dumps({"status": "not_configured", "continue_offline": True,
                          "reason": "Supply --repo OWNER/REPOSITORY for the first download."}))
        return 0 if args.command == "check" else 2
    if args.command == "check":
        print(json.dumps(check(repo, identity.get("version", "0.0.0"), args.tag), indent=2))
        return 0
    try:
        info = release_info(repo, args.tag)
        size = f"{info['bytes']/1024**3:.2f} GiB" if info['bytes']>=1024**3 else f"{info['bytes']/1024**2:.2f} MiB"
        print(f"Download {info['version']} ({size}) from {info['repository']}.")
        if input("Download this complete offline package? [Y/n]: ").strip().lower() not in {"", "y", "yes"}:
            print("Cancelled; current installation remains available.")
            return 0
        pack = download(info, args.destination)
        print("Verified package: " + str(pack))
        if args.command == "install":
            # The downloaded installer supplies the existing host/scope/settings review.
            return subprocess.call([sys.executable, str(pack / "scripts" / "install.py"), "--interactive"])
        print("Run its Setup.cmd or scripts/install.py to choose host and global/project scope.")
        return 0
    except (OSError, ValueError, KeyError, zipfile.BadZipFile, EOFError, subprocess.TimeoutExpired) as exc:
        print("Update did not finish: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
