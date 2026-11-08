"""Build a self-contained, hash-verified offline Atlas reference pack from local exports."""
from __future__ import annotations

import argparse
import csv
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
from itertools import islice
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
import time
import zlib

PACK = Path(__file__).resolve().parents[1]
PROJECT = PACK.parents[1]
sys.path.insert(0, str(PACK / "scripts"))
import atlas


def disk(path):
    """Windows metadata mirrors exceed MAX_PATH; keep exported relative paths unchanged."""
    path = Path(path).resolve()
    if os.name == "nt" and not str(path).startswith("\\\\?\\"):
        return Path("\\\\?\\" + str(path))
    return path


def digest(path):
    value = hashlib.sha256()
    with disk(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""): value.update(block)
    return value.hexdigest()


def contained(root, relative):
    path = (root / relative.replace("\\", "/")).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Source path escapes its declared root: " + relative)
    return path


def initialize(db):
    db.executescript("""
        PRAGMA journal_mode=WAL;
        PRAGMA synchronous=NORMAL;
        PRAGMA cache_size=-131072;
        PRAGMA temp_store=MEMORY;
        CREATE TABLE IF NOT EXISTS sources(id TEXT PRIMARY KEY,label TEXT,manifest_sha256 TEXT,limitations TEXT);
        CREATE TABLE IF NOT EXISTS blobs(sha256 TEXT PRIMARY KEY,content BLOB NOT NULL);
        CREATE TABLE IF NOT EXISTS documents(id TEXT PRIMARY KEY,source TEXT,path TEXT,kind TEXT,name TEXT,
            sha256 TEXT,search_text TEXT,UNIQUE(source,path));
        CREATE INDEX IF NOT EXISTS doc_names ON documents(name COLLATE NOCASE);
        CREATE INDEX IF NOT EXISTS doc_sources ON documents(source,kind);
        CREATE INDEX IF NOT EXISTS doc_hashes ON documents(sha256);
    """)


def register(db, source, label, fingerprint, limitations):
    old = db.execute("SELECT manifest_sha256 FROM sources WHERE id=?", (source,)).fetchone()
    if old and old[0] != fingerprint:
        raise ValueError("Source changed during resume. Use a new --output for the new snapshot: " + source)
    db.execute("INSERT OR IGNORE INTO sources VALUES(?,?,?,?)", (source, label, fingerprint, limitations))


def search_words(path, kind, raw, extra=""):
    text = raw.decode("utf-8-sig", errors="replace")
    if path.lower().endswith(".xml"):
        return " ".join(re.findall(r"<(?:Name|DataField|DataSource|RelatedTable|RelatedField|Label|EnumType|ExtendedDataType)>([^<]+)</", text[:2000000]))[:60000]
    if kind == "SQL_OBJECT": return extra[:200000]
    if path.lower().endswith((".md", ".sql", ".json")): return text[:100000]
    return ""


def add(db, source, path, kind, name, raw=None, expected=None, loader=None, extra="", prepared=None):
    identity = hashlib.sha256((source + "/" + path).encode()).hexdigest()[:32]
    if db.execute("SELECT 1 FROM documents WHERE id=?", (identity,)).fetchone(): return False
    existing = expected and db.execute("SELECT 1 FROM blobs WHERE sha256=?", (expected,)).fetchone()
    if existing:
        sha = expected
        # Recover names from an already indexed representation of identical content.
        found = db.execute("SELECT search_text FROM documents WHERE sha256=? LIMIT 1", (sha,)).fetchone()
        words = found[0] if found else ""
    else:
        if prepared:
            sha, compressed, words = prepared
        else:
            raw = raw if raw is not None else loader()
            sha = hashlib.sha256(raw).hexdigest()
            compressed, words = zlib.compress(raw, 3), search_words(path, kind, raw, extra)
        if expected and expected.lower() != sha: raise ValueError("Source hash mismatch: " + source + "/" + path)
        db.execute("INSERT OR IGNORE INTO blobs VALUES(?,?)", (sha, compressed))
    db.execute("INSERT INTO documents VALUES(?,?,?,?,?,?,?)", (identity, source, path, kind, name, sha, words))
    return True


def snapshot(db, root, source):
    manifest = root / "manifest.csv"
    register(db, source, root.name, digest(manifest),
             "Declared application metadata; build/effective-extension/runtime completeness unconfirmed.")
    add(db, source, "manifest.csv", "MANIFEST", "manifest", raw=manifest.read_bytes())
    if (root / "snapshot.json").exists():
        add(db, source, "snapshot.json", "MANIFEST", "snapshot", raw=(root / "snapshot.json").read_bytes())
    completed = {r[0] for r in db.execute("SELECT path FROM documents WHERE source=?", (source,))}
    known = {r[0] for r in db.execute("SELECT sha256 FROM blobs")}
    def prepare(row):
        relative = "raw/" + row["RelativePath"].replace("\\", "/")
        if relative in completed: return row, relative, None
        raw = disk(contained(root, relative)).read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        if sha != row["SHA256"].lower(): raise ValueError("Source hash mismatch: " + relative)
        content = None if sha in known else (sha, zlib.compress(raw, 3), search_words(relative, row["Kind"], raw))
        return row, relative, content
    number = 0
    with manifest.open(encoding="utf-8-sig", newline="") as handle, ThreadPoolExecutor(max_workers=32) as pool:
        reader = csv.DictReader(handle)
        while batch := list(islice(reader, 512)):
            for row, relative, content in pool.map(prepare, batch):
                number += 1
                if relative not in completed:
                    sha = row["SHA256"].lower()
                    add(db, source, relative, row["Kind"], row["Name"], expected=sha, prepared=content)
                    known.add(sha)
            if number % 2048 == 0:
                db.commit(); print(f"{source}: {number:,} manifest files checked", flush=True)
    db.commit()


def folder(db, root, source, extensions=None):
    root = disk(root)
    allowed = extensions or {".xml", ".json", ".jsonl", ".csv", ".md", ".txt", ".sql", ".xpp"}
    paths = sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in allowed)
    signature = hashlib.sha256()
    # Fingerprint files, not mtimes, for immutable resumption and source identity.
    records = []
    for path in paths:
        rel, sha = path.relative_to(root).as_posix(), digest(path)
        records.append((path, rel, sha))
        signature.update((rel + ":" + sha + "\n").encode())
    register(db, source, root.name, signature.hexdigest(),
             "Local exported/reference files. Snapshot compatibility and runtime correctness unconfirmed.")
    for number, (path, rel, sha) in enumerate(records, 1):
        kind = next((part for part in path.parts if part.lower().startswith("ax")), "REFERENCE")
        add(db, source, rel, kind, path.stem, expected=sha, loader=path.read_bytes)
        if number % 2000 == 0:
            db.commit(); print(f"{source}: {number:,} reference files", flush=True)
    db.commit()


def files(db, root, source, selected):
    records = [(relative, contained(root, relative)) for relative in selected]
    fingerprint = hashlib.sha256("\n".join(relative + ":" + digest(path) for relative, path in records).encode()).hexdigest()
    register(db, source, "Reviewed local knowledge and derived metadata", fingerprint,
             "Authored interpretations and derived indexes retain their source proofs; not independently runtime/business validated.")
    for relative, path in records:
        add(db, source, relative, "REFERENCE", path.stem, expected=digest(path), loader=disk(path).read_bytes)
    db.commit()


def catalog(db, path, source):
    register(db, source, path.stem, digest(path),
             "Derived SQL catalog snapshot. Original definitions retained; dependency edges are not joins. Target Fabric schema not established.")
    conn = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    for number, obj in enumerate(conn.execute("SELECT * FROM objects ORDER BY id"), 1):
        obj = dict(obj)
        key = obj["id"]
        content = {"object": obj, "columns": [dict(r) for r in conn.execute("SELECT * FROM columns WHERE object_key=?", (key,))],
                   "dependencies": [dict(r) for r in conn.execute("SELECT * FROM dependencies WHERE source_key=?", (key,))],
                   "indexes": [dict(r) for r in conn.execute("SELECT * FROM indexes WHERE object_key=?", (key,))]}
        # Catalog provenance may contain absolute original paths; portable content uses basename only.
        for record in [obj] + content["dependencies"]:
            if record.get("source_file"):
                record["source_file"] = record["source_file"].replace("\\", "/").split("/")[-1]
        raw = json.dumps(content, ensure_ascii=False, indent=2).encode()
        words = " ".join([obj["name"], obj.get("display_name") or ""] + [c["name"] for c in content["columns"]])
        add(db, source, key + ".json", "SQL_OBJECT", obj["name"], raw=raw, extra=words)
        if number % 2000 == 0:
            db.commit(); print(f"{source}: {number:,} SQL objects", flush=True)
    conn.close(); db.commit()


def build(config, output):
    if not config.get("sources"):
        raise ValueError("No exported sources configured. Supply --config with existing local exports.")
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    final, pending = output / "atlas.sqlite", output / "atlas.build.sqlite"
    if final.exists(): raise ValueError("Published snapshot already exists. Choose a new --output directory.")
    db = sqlite3.connect(pending)
    try:
        return publish(config, output, db, pending, final)
    finally:
        db.close()


def publish(config, output, db, pending, final):
    initialize(db)
    configured = [item["id"] for item in config["sources"]]
    if len(set(configured)) != len(configured): raise ValueError("Duplicate source IDs in build config.")
    if any(item["type"] not in {"snapshot", "folder", "catalog", "files"} for item in config["sources"]):
        raise ValueError("Unsupported source type in build config.")
    staged = {row[0] for row in db.execute("SELECT id FROM sources")}
    if staged - set(configured):
        raise ValueError("Staged sources were removed from the config; use a new output instead of silently retaining them.")
    started = time.monotonic()
    for item in config["sources"]:
        root = Path(item["path"]).resolve()
        if not root.exists(): raise ValueError("Missing configured export: " + str(root))
        print("Reading " + item["id"], flush=True)
        if item["type"] == "snapshot": snapshot(db, root, item["id"])
        elif item["type"] == "catalog": catalog(db, root, item["id"])
        elif item["type"] == "files": files(db, root, item["id"], item["files"])
        else: folder(db, root, item["id"])
    print("Building search index", flush=True)
    db.execute("DROP TABLE IF EXISTS search")
    db.execute("CREATE VIRTUAL TABLE search USING fts5(name,search_text,content='documents',content_rowid='rowid')")
    db.execute("INSERT INTO search(search) VALUES('rebuild')")
    db.commit()
    counts = {"documents": db.execute("SELECT count(*) FROM documents").fetchone()[0],
              "unique_contents": db.execute("SELECT count(*) FROM blobs").fetchone()[0],
              "sources": db.execute("SELECT count(*) FROM sources").fetchone()[0]}
    # Verify DB consistency before atomic publication. WAL checkpoint removes sidecar dependency.
    if db.execute("PRAGMA quick_check").fetchone()[0] != "ok": raise ValueError("Reference integrity check failed")
    db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    db.execute("PRAGMA journal_mode=DELETE")
    db.close()
    pending.replace(final)
    summary = {**counts, "generated_utc": datetime.now(timezone.utc).isoformat(),
               "runtime_validated": False, "business_reconciled": False,
               "search_coverage": "Object names and bounded declared field/reference tokens, not exhaustive full-text or effective-extension merging.",
               "sqlite_sha256": digest(final)}
    (output / "manifest.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    with atlas.connect(output.parent) as read:
        lines = ["# Offline reference snapshot", "", "Original evidence is compressed losslessly in `atlas.sqlite`.",
                 "Use `scripts/atlas.py search` then `show` to read a hash-checked Markdown reference.",
                 "Use `show --raw --output <file>` to retrieve exact original bytes.", "", "## Sources", ""]
        for row in atlas.source_rows(read):
            lines.append(f'- `{row["id"]}` — {row["label"]}; manifest SHA256 `{row["manifest_sha256"]}`. {row["limitations"]}')
        lines += ["", "## Coverage", "", "```json", json.dumps(summary, indent=2), "```", ""]
        (output / "INDEX.md").write_text("\n".join(lines), encoding="utf-8")
        # Ready-to-read Markdown pages for the initial six core tables; all other evidence is available via show.
        ready = output / "tables"; ready.mkdir(exist_ok=True)
        for name in ("PurchLine", "PurchTable", "VendInvoiceTrans", "VendInvoiceJour", "VendPackingSlipTrans", "VendPackingSlipJour"):
            for row in read.execute("SELECT id FROM documents WHERE name=? AND kind='AxTable' AND path NOT LIKE '%/XppMetadata/%' ORDER BY source,path", (name,)):
                record, raw = atlas.document(read, row[0])
                (ready / (name + "--" + record["id"] + ".md")).write_text(atlas.markdown(record, raw), encoding="utf-8")
    print(json.dumps({**summary, "elapsed_seconds": round(time.monotonic() - started), "output": str(output)}, indent=2), flush=True)
    return summary


def defaults(project):
    adjacent = project.parent / "F&O DB"
    sources = [
        ("snapshot", "application-20261019", project / "FO-Evidence-Snapshot-20261019-113929"),
        ("folder", "focused-application-20261018", adjacent / "FO-Metadata-extraction" / "export"),
        ("folder", "sql-reference-exports", adjacent / "sql"),
        ("folder", "sql-application-capture-20261023", project / "evidence" / "live-sql-application-20261023-182402"),
        ("folder", "sql-edw-capture-20261023", project / "evidence" / "live-sql-20261023-edw"),
        ("folder", "sql-scope-capture-20261023", project / "evidence" / "live-sql-20261023-scope"),
        ("folder", "customer-analysis-references", adjacent / "Customer-Analysis"),
        ("folder", "knowledge-20261020", project / "research" / "ms-learn-2026-10-20"),
        ("catalog", "sql-reference-catalog", project / "data" / "catalog.sqlite"),
        ("catalog", "sql-application-catalog-20261023", project / "data" / "live49.sqlite"),
    ]
    result = [{"type": t, "id": i, "path": str(p)} for t, i, p in sources if p.exists()]
    selected = [p.name for p in sorted(project.glob("Reviewed Story*.md"))]
    selected += [str(p.relative_to(project)).replace("\\", "/") for p in
                 (project / "data" / name for name in ("application-reviews.json", "business-terms.json", "relationships.json", "navigation.json")) if p.exists()]
    if selected: result.append({"type": "files", "id": "reviewed-knowledge-and-indexes", "path": str(project), "files": selected})
    return {"sources": result}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, help="Local JSON: sources [{type,id,path}]; keep machine paths private.")
    parser.add_argument("--output", type=Path, default=PACK / "references")
    args = parser.parse_args()
    try:
        build(json.loads(args.config.read_text(encoding="utf-8-sig")) if args.config else defaults(PROJECT), args.output)
    except (OSError, ValueError, sqlite3.Error) as exc:
        print("Build stopped; prior published snapshots unchanged: " + str(exc), file=sys.stderr)
        raise SystemExit(2)
