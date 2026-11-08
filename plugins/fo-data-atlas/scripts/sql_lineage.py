"""Read exported SQL and its catalog dependencies from one offline Atlas snapshot."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

import atlas


def inspect(db, identity, max_depth=25, max_nodes=300):
    if not 1 <= max_depth <= 100 or not 1 <= max_nodes <= 1000:
        raise ValueError("Use depth 1..100 and node limit 1..1000.")
    root, root_raw = atlas.document(db, identity)
    if root["kind"] != "SQL_OBJECT":
        raise ValueError("Select a SQL_OBJECT evidence ID, not application XML.")
    source = root["source"]
    database = json.loads(root_raw)['object'].get('database_name', '')
    nodes, edges, blockers, ordered, visiting = {}, [], [], [], set()
    truncated = False

    def visit(evidence_id, depth):
        nonlocal truncated
        if evidence_id in visiting:
            blockers.append({"reason": "cycle", "id": evidence_id})
            return
        if evidence_id in nodes:
            return
        if len(nodes) >= max_nodes:
            truncated = True
            return
        row, raw = atlas.document(db, evidence_id)
        if row["source"] != source or row["kind"] != "SQL_OBJECT":
            raise ValueError("Dependency escaped the selected SQL snapshot.")
        payload = json.loads(raw)
        obj = payload["object"]
        if obj.get('database_name', '').casefold() != database.casefold():
            blockers.append({'reason': 'different_database_requires_mapping', 'id': evidence_id})
            return
        node = {"evidence_id": evidence_id, "source": source, "sha256": row["sha256"],
                "object": obj, "depth": depth}
        nodes[evidence_id] = node
        visiting.add(evidence_id)
        kind = obj.get("kind", "")
        if kind != "USER_TABLE" and (not obj.get("definition") or str(obj.get("is_encrypted", "0")).lower() in {"1", "true"}):
            blockers.append({"reason": "definition_missing_or_encrypted", "id": evidence_id})
        for dependency in payload.get("dependencies", []):
            edge = {"source_id": evidence_id, "declared": dependency, "target_id": None}
            edges.append(edge)
            target_key = dependency.get("target_key")
            external = dependency.get("referenced_server") or (
                dependency.get("referenced_database") and
                dependency["referenced_database"].casefold() != obj.get("database_name", "").casefold())
            if dependency.get("is_ambiguous") not in (None, 0, "0", False):
                blockers.append({"reason": "ambiguous_reference", "edge": edge})
            if external:
                blockers.append({"reason": "qualified_reference_requires_review", "edge": edge})
                continue
            match = db.execute("SELECT id FROM documents WHERE source=? AND kind='SQL_OBJECT' AND path=?",
                               (source, str(target_key) + ".json")).fetchall() if target_key else []
            if len(match) != 1:
                blockers.append({"reason": "unresolved_reference", "edge": edge})
                continue
            edge["target_id"] = match[0][0]
            if edge['target_id'] == evidence_id and kind == 'USER_TABLE':
                edge['resolution_note'] = 'Table internal self-reference retained; not a view deployment cycle.'
                continue
            if depth >= max_depth:
                truncated = True
                continue
            visit(match[0][0], depth + 1)
        visiting.remove(evidence_id)
        ordered.append(evidence_id)

    visit(identity, 0)
    return {"root_id": identity, "source": source, "nodes": list(nodes.values()), "edges": edges,
            "ordered_ids": ordered, "blockers": blockers, "truncated": truncated,
            "source_definitions_complete": not blockers and not truncated,
            "deployment_ready": False, "fabric_validated": False, "runtime_validated": False,
            "business_reconciled": False,
            "limitations": ["Exported catalog dependencies only; dynamic SQL and runtime dependencies may be absent.",
                            "Dependency edges do not establish analytical joins.",
                            "Original SQL is for its exported source engine/database, not certified Fabric SQL.",
                            "Physical tables must exist; their CREATE TABLE definitions are not supplied by this catalog."]}


def heading(node):
    obj = node["object"]
    return ".".join(str(obj.get(key) or "?") for key in ("database_name", "schema_name", "name"))


def markdown(result):
    by_id = {node["evidence_id"]: node for node in result["nodes"]}
    root = by_id[result["root_id"]]
    lines = ["# " + heading(root), "", "Source snapshot: `" + result["source"] + "`.",
             "", "These are exported definitions and catalog edges. Fabric/runtime/business validation is false.",
             "", "## Objects", "", "| Object | Kind | Depth | Evidence ID |", "|---|---|---|---|"]
    for node in result["nodes"]:
        name = heading(node).replace("|", "\\|")
        lines.append(f"| {name} | {node['object'].get('kind')} | {node['depth']} | `{node['evidence_id']}` |")
    lines += ["", "## Declared dependencies", ""]
    for edge in result["edges"]:
        dep = edge["declared"]
        target = heading(by_id[edge["target_id"]]) if edge["target_id"] in by_id else str(dep.get("target_key") or dep)
        lines.append("- " + heading(by_id[edge["source_id"]]) + " → " + target)
    lines += ["", "## Gaps", "", "```json", json.dumps({"blockers": result["blockers"], "truncated": result["truncated"]}, indent=2), "```", ""]
    lines += ["- " + text for text in result["limitations"]]
    lines += ["", "Would you like the exported SQL for the underlying views too?", ""]
    return "\n".join(lines)


def export(result, folder, include_dependencies=False):
    folder = Path(folder)
    if folder.exists():
        raise ValueError("Choose a new output directory; existing SQL is preserved.")
    folder.mkdir(parents=True)
    (folder / "lineage.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    (folder / "lineage.md").write_text(markdown(result), encoding="utf-8")
    by_id = {node["evidence_id"]: node for node in result["nodes"]}
    selected = result["ordered_ids"] if include_dependencies else [result["root_id"]]
    written = []
    for identity in selected:
        node = by_id[identity]
        definition = node["object"].get("definition")
        if not definition or node["object"].get("kind") == "USER_TABLE":
            continue
        name = re.sub(r"[^A-Za-z0-9_.-]", "_", str(node["object"]["name"]))[:100]
        path = folder / ("source-" + name + "--" + identity[:12] + ".sql")
        path.write_bytes(definition.encode("utf-8"))
        written.append(path.name)
    (folder / "definitions-index.json").write_text(json.dumps({"files": written, "ordered_ids": selected,
        "dependency_sql_requested": include_dependencies, "deployment_ready": False}, indent=2) + "\n", encoding="utf-8")
    return {"folder": str(folder), "sql_files": written, "source_definitions_complete": result["source_definitions_complete"],
            "deployment_ready": False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("id", help="SQL_OBJECT evidence ID returned by atlas.py search")
    parser.add_argument("--pack", type=Path, default=atlas.ROOT)
    parser.add_argument("--depth", type=int, default=25)
    parser.add_argument("--max-nodes", type=int, default=300)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--include-dependencies", action="store_true")
    args = parser.parse_args(argv)
    try:
        with atlas.connect(args.pack) as db:
            result = inspect(db, args.id, args.depth, args.max_nodes)
        if args.output:
            print(json.dumps(export(result, args.output, args.include_dependencies), indent=2))
        else:
            print(json.dumps(result, indent=2))
        return 0
    except (OSError, ValueError, KeyError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
