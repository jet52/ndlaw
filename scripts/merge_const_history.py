#!/usr/bin/env python3
"""Merge the historical point-in-time layer (constitution_history.db) into the
served Constitution corpus (constitution.db) — Approach B.

The two DBs share the versioned-provision schema and are citation-disjoint:
constitution.db uses modern article numbering ("N.D. Const. art. V, § 2");
constitution_history.db uses the original 1889 numbering ("N.D. Const. § 82",
"N.D. Const. Schedule, § 5"). So the historical provisions can be inserted
alongside the modern ones with no cite_key collision, making historical text
SERVED and point-in-time queryable by its original citation:

    lookup_authority("N.D. Const. § 82", as_of_date="1945-01-01")

IDs are remapped (constitution.db already holds provisions 1..201). Each merged
version is FTS-indexed explicitly (citation/heading live on provisions, not the
FTS content table, so 'rebuild' can't reconstruct them). Run AFTER a fresh
`ingest_constitution --apply`; it refuses to run twice (guard on the 1889 scheme)
so re-runs don't duplicate — rebuild constitution.db, then re-merge.

    python scripts/merge_const_history.py            # dry run (report)
    python scripts/merge_const_history.py --apply
"""
import argparse, json, sqlite3, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BATCH = "const-history-merge-2026-06-08"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=Path, default=ROOT / "constitution.db")
    ap.add_argument("--source", type=Path, default=ROOT / "constitution_history.db")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    for p in (args.target, args.source):
        if not p.exists():
            sys.exit(f"ABORT: {p} not found")

    src = sqlite3.connect(f"file:{args.source}?mode=ro", uri=True)
    src.row_factory = sqlite3.Row
    provs = src.execute(
        "SELECT id, corpus, citation, cite_key, hierarchy, heading, status, current_version_id "
        "FROM provisions ORDER BY id"
    ).fetchall()
    vers = src.execute(
        "SELECT id, provision_id, effective_start, effective_end, text_content, "
        "source_authority, source_url, source_path, batch FROM provision_versions ORDER BY id"
    ).fetchall()
    amds = src.execute("SELECT * FROM amendments ORDER BY id").fetchall()
    cite_of = {p["id"]: (p["citation"], p["heading"]) for p in provs}
    print(f"source: {len(provs)} provisions, {len(vers)} versions, {len(amds)} amendment events")

    tgt = sqlite3.connect(args.target)
    tgt.row_factory = sqlite3.Row
    tgt.execute("PRAGMA foreign_keys=ON")

    # Idempotency guard: refuse if a prior merge (1889-scheme provisions) is present.
    dup = tgt.execute(
        "SELECT COUNT(*) FROM provisions WHERE hierarchy LIKE '%\"scheme\": \"1889%'"
    ).fetchone()[0]
    if dup:
        sys.exit(f"ABORT: target already has {dup} 1889-scheme provisions (already merged?). "
                 "Rebuild constitution.db (ingest_constitution --apply), then re-merge.")
    # cite_key collision check (should be zero — schemes are disjoint).
    src_keys = {p["cite_key"] for p in provs}
    clash = [k for (k,) in tgt.execute("SELECT cite_key FROM provisions").fetchall() if k in src_keys]
    if clash:
        sys.exit(f"ABORT: {len(clash)} cite_key collisions with modern provisions, e.g. {clash[:5]}")

    if not args.apply:
        print(f"dry run: would insert {len(provs)} provisions + {len(vers)} versions + "
              f"{len(amds)} amendments into {args.target.name} (no collisions). Re-run with --apply.")
        return

    pmap: dict[int, int] = {}   # old provision id -> new
    vmap: dict[int, int] = {}   # old version id   -> new
    try:
        for p in provs:
            cur = tgt.execute(
                "INSERT INTO provisions (corpus, citation, cite_key, hierarchy, heading, status, current_version_id) "
                "VALUES (?,?,?,?,?,?,NULL)",
                (p["corpus"], p["citation"], p["cite_key"], p["hierarchy"], p["heading"], p["status"]),
            )
            pmap[p["id"]] = cur.lastrowid
        for v in vers:
            cur = tgt.execute(
                "INSERT INTO provision_versions (provision_id, effective_start, effective_end, text_content, "
                "source_authority, source_url, source_path, batch) VALUES (?,?,?,?,?,?,?,?)",
                (pmap[v["provision_id"]], v["effective_start"], v["effective_end"], v["text_content"],
                 v["source_authority"], v["source_url"], v["source_path"], v["batch"] or BATCH),
            )
            vmap[v["id"]] = cur.lastrowid
            citation, heading = cite_of[v["provision_id"]]
            tgt.execute(
                "INSERT INTO provisions_fts(rowid, citation, heading, text_content) VALUES (?,?,?,?)",
                (cur.lastrowid, citation, heading or "", v["text_content"]),
            )
        for p in provs:  # now wire current_version_id with remapped ids
            if p["current_version_id"] is not None:
                tgt.execute("UPDATE provisions SET current_version_id=? WHERE id=?",
                            (vmap[p["current_version_id"]], pmap[p["id"]]))
        a_cols = [c[1] for c in src.execute("PRAGMA table_info(amendments)")]
        for a in amds:
            d = {c: a[c] for c in a_cols}
            d.pop("id", None)
            if d.get("provision_id") is not None:
                d["provision_id"] = pmap.get(d["provision_id"])
            if d.get("version_id") is not None:
                d["version_id"] = vmap.get(d["version_id"])
            cols = [c for c in d]
            tgt.execute(
                f"INSERT OR IGNORE INTO amendments ({','.join(cols)}) VALUES ({','.join('?'*len(cols))})",
                [d[c] for c in cols],
            )
        tgt.execute(
            "INSERT INTO provenance (operation, command, source_paths, rows_affected, notes) VALUES (?,?,?,?,?)",
            ("merge_const_history", BATCH, str(args.source),
             len(provs) + len(vers),
             f"Merged historical point-in-time layer (1889 numbering, {len(provs)} provisions / "
             f"{len(vers)} versions, eff. 1889-1980) into served constitution.db. "
             "Disjoint from modern art/§ provisions; no cross-era crosswalk yet (see TODO-primarylaw PL-CONST-CROSSWALK)."),
        )
        tgt.execute(
            "INSERT INTO changelog (batch, field, new_value, authority) VALUES (?,?,?,?)",
            (BATCH, "merge",
             f"+{len(provs)} provisions, +{len(vers)} versions (1889 scheme, 1889-1980)",
             "merge_const_history.py from constitution_history.db"),
        )
        tgt.commit()
    except Exception:
        tgt.rollback()
        raise

    tot_p = tgt.execute("SELECT COUNT(*) FROM provisions").fetchone()[0]
    tot_v = tgt.execute("SELECT COUNT(*) FROM provision_versions").fetchone()[0]
    print(f"APPLIED: constitution.db now has {tot_p} provisions, {tot_v} versions "
          f"(+{len(provs)}/+{len(vers)} historical).")


if __name__ == "__main__":
    main()
