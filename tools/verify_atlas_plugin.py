"""Verify real offline source anchors and report package limits; no SQL execution."""
import argparse
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "plugins" / "fo-data-atlas" / "scripts"))
import atlas
import validate_package
import sql_lineage


def verify(pack):
    package = validate_package.validate(pack)
    if not package["passed"]: raise ValueError(str(package["issues"]))
    checks = []
    with atlas.connect(pack) as db:
        source = "application-20261019"
        for name in ("PurchLine", "PurchTable", "VendInvoiceTrans", "VendInvoiceJour", "VendPackingSlipTrans", "VendPackingSlipJour"):
            path = "raw/ApplicationSuite/Foundation/AxTable/" + name + ".xml"
            row = db.execute("SELECT id FROM documents WHERE source=? AND path=?", (source, path)).fetchone()
            if not row: raise ValueError("Missing source anchor: " + path)
            record, raw = atlas.document(db, row[0])
            if ET.fromstring(raw).findtext("Name") != name: raise ValueError("Unexpected table XML identity")
            checks.append({"name": name, "id": record["id"], "sha256": record["sha256"], "state": "packed_source_hash_verified"})
        entitypath = "raw/ApplicationSuite/Foundation/AxDataEntityView/PurchPurchaseOrderHeaderV2Entity.xml"
        row = db.execute("SELECT id FROM documents WHERE source=? AND path=?", (source, entitypath)).fetchone()
        record, raw = atlas.document(db, row[0])
        root = ET.fromstring(raw)
        fields = [node for node in root.find("Fields") if node.findtext("Name") == "PurchaseOrderNumber"]
        if len(fields) != 1 or fields[0].findtext("DataField") != "PurchId" or fields[0].findtext("DataSource") != "PurchTable":
            raise ValueError("Expected alias binding was not present")
        checks.append({"name": "PurchaseOrderNumber -> PurchTable.PurchId", "id": record["id"], "sha256": record["sha256"], "state": "declared_entity_binding"})
        labels = atlas.label_lookup(db, "@SYS15812", source)
        if labels["ambiguous"] or not labels["matches"] or {row["text"] for row in labels["matches"]} != {"Purchase order"}:
            raise ValueError("English caption source is missing or ambiguous")
        checks.append({"name": "@SYS15812", "state": "resolved_English_label", **labels})
        counts = [dict(row) for row in db.execute("SELECT source,count(*) AS documents FROM documents GROUP BY source ORDER BY source")]
        lineage = sql_lineage.inspect(db, '10b79974ade8da2f18d3ec0910b4c354')
        if lineage['truncated'] or len(lineage['nodes']) != 50 or lineage['blockers']:
            raise ValueError('Known nested-view lineage anchor changed or is incomplete')
        checks.append({'name':'CustCustomerV3Entity nested SQL lineage', 'source':lineage['source'],
                       'objects':len(lineage['nodes']), 'definitions':sum(bool(n['object'].get('definition')) for n in lineage['nodes']),
                       'state':'packed_catalog_edges_verified_not_runtime'})
    return {"package": package, "source_anchor_checks": checks, "source_counts": counts,
            "runtime_validated": False, "business_reconciled": False, "host_load_verified": False,
            "sample_target_schema_available": (pack / 'examples/fabric-schema-example.csv').is_file(),
            "recipient_schema_validated": False,
            "example_queries": "PO/receipt are target-specific drafts with checks and sample-level evidence; vendor invoice is a starter. No all-company/business validation claimed."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", type=Path, default=ROOT / "plugins" / "fo-data-atlas")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = verify(args.pack)
    text = json.dumps(result, indent=2) + "\n"
    if args.output: args.output.write_text(text, encoding="utf-8")
    else: print(text)
