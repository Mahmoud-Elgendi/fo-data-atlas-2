"""Validate this package's JSON manifests, simple skill frontmatter and local links."""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def validate(pack, source_only=False):
    issues = []
    manifests = [json.loads((pack / host / "plugin.json").read_text(encoding="utf-8"))
                 for host in (".codex-plugin", ".claude-plugin")]
    if len({(m.get("name"), m.get("version")) for m in manifests}) != 1:
        issues.append("Host package identities differ")
    for m in manifests:
        if m.get("skills") != "./skills/": issues.append("Unexpected skill directory")
    skills = sorted((pack / "skills").glob("*/SKILL.md"))
    if not skills: issues.append("No skills found")
    for skill in skills:
        text = skill.read_text(encoding="utf-8")
        match = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
        if not match:
            issues.append(str(skill.relative_to(pack)) + ": missing frontmatter")
            continue
        # These skills intentionally use only unquoted single-line name/description.
        data = dict(line.split(": ", 1) for line in match[1].splitlines() if ": " in line)
        if data.get("name") != skill.parent.name or not re.fullmatch(r"[a-z0-9-]{1,64}", data.get("name", "")):
            issues.append("Skill name mismatch: " + skill.parent.name)
        if not data.get("description") or len(data["description"]) > 1024:
            issues.append("Missing/oversized skill description: " + skill.parent.name)
        if re.search(r"\bTODO\b|\[TODO", text): issues.append("Unfinished skill scaffold: " + skill.parent.name)
    for md in list((pack / "skills").rglob("*.md")) + list((pack / "references").glob("*.md")) + [pack / "README.md"]:
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", md.read_text(encoding="utf-8")):
            if target.startswith(("https://", "#")): continue
            path = (md.parent / target.split("#", 1)[0]).resolve()
            if not path.is_relative_to(pack.resolve()) or not path.is_file():
                issues.append("Broken/escaping link in " + str(md.relative_to(pack)) + ": " + target)
    if not source_only:
        reference_pack=pack
        if (pack/'reference-pack.json').is_file() or (pack/'metadata-catalog.json').is_file():
            try:
                from metadata_cache import resolve
                reference_pack=resolve(pack)
            except ValueError as exc: issues.append(str(exc))
        manifest = reference_pack / "references" / "manifest.json"
        db = reference_pack / "references" / "atlas.sqlite"
        if not manifest.exists() or not db.exists(): issues.append("Offline payload is missing")
        else:
            digest = hashlib.sha256()
            with db.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""): digest.update(chunk)
            if digest.hexdigest() != json.loads(manifest.read_text())["sqlite_sha256"]:
                issues.append("Reference publication hash mismatch")
    return {"passed": not issues, "issues": issues, "skills": [p.parent.name for p in skills],
            "scope": "Local package validation only; actual host loading and SQL execution not verified."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", type=Path, default=ROOT); parser.add_argument("--source-only", action="store_true")
    args = parser.parse_args()
    result = validate(args.pack, args.source_only)
    print(json.dumps(result, indent=2)); raise SystemExit(0 if result["passed"] else 1)
