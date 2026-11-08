"""Create the private, self-contained Atlas plugin ZIP without changing source exports."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

PROJECT = Path(__file__).resolve().parents[1]
DEFAULT = PROJECT / "plugins" / "fo-data-atlas"


def sha(path):
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""): value.update(chunk)
    return value.hexdigest()


def package(pack, output=None):
    pack = pack.resolve()
    reference = json.loads((pack / "references" / "manifest.json").read_text(encoding="utf-8"))
    if sha(pack / "references" / "atlas.sqlite") != reference["sqlite_sha256"]:
        raise ValueError("Reference database does not match its publication manifest.")
    version = json.loads((pack / ".codex-plugin" / "plugin.json").read_text())["version"]
    output = output or pack / "dist" / ("fo-data-atlas-" + version + ".zip")
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists(): raise ValueError("Archive already exists; preserve it and choose a new output path.")
    files = sorted(p for p in pack.rglob("*") if p.is_file() and
                   "dist" not in p.relative_to(pack).parts and "__pycache__" not in p.parts and
                   p.suffix != ".pyc" and ".build.sqlite" not in p.name and p.name != "package-manifest.json")
    manifest = {"name": "fo-data-atlas", "version": version, "private": True,
                "host_load_verified": False, "runtime_validated": False, "business_reconciled": False,
                "files": [{"path": p.relative_to(pack).as_posix(), "sha256": sha(p), "bytes": p.stat().st_size} for p in files]}
    identity = pack / "package-manifest.json"
    identity.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    with zipfile.ZipFile(output, "x", allowZip64=True) as archive:
        for path in files + [identity]:
            archive.write(path, "fo-data-atlas/" + path.relative_to(pack).as_posix(),
                          compress_type=zipfile.ZIP_STORED if path.suffix == ".sqlite" else zipfile.ZIP_DEFLATED)
    # CRC validation reads the actual archive, including the offline payload.
    with zipfile.ZipFile(output) as archive:
        bad = archive.testzip()
        if bad: raise ValueError("Archive CRC failed: " + bad)
    result = {"archive": str(output), "sha256": sha(output), "bytes": output.stat().st_size, "files": len(files) + 1}
    output.with_suffix(".sha256").write_text(result["sha256"] + "  " + output.name + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", type=Path, default=DEFAULT); parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    package(args.pack, args.output)
