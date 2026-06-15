#!/usr/bin/env python3
"""Apply data/const_modern_text_corrections.json to an already-built DB.

Mirrors ingest_constitution.apply_text_corrections (which runs at build time) for
DBs that are already built (live constitution.db, the reconstruction scratch). Only
touches the provision's CURRENT (open) version text; FTS reindexed via the
external-content 'delete' command. Idempotent. Run after fix_amend* steps.

Usage: python scripts/apply_modern_text_corrections.py <db_path> [--apply]
"""
import argparse, json, sqlite3, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from ndcourts_mcp import corpus  # noqa: E402

CORR = ROOT / "data" / "const_modern_text_corrections.json"
BATCH = "modern-text-corrections-2026-06-15"


def norm(s):
    return " ".join((s or "").split())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("db", type=Path)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    con = sqlite3.connect(args.db)
    data = json.loads(CORR.read_text())
    n = 0
    for c in data["corrections"]:
        row = con.execute("SELECT p.id, p.current_version_id, p.heading, v.text_content "
                          "FROM provisions p JOIN provision_versions v ON v.id=p.current_version_id "
                          "WHERE p.citation=?", (c["citation"],)).fetchone()
        if not row:
            print(f"  SKIP {c['citation']}: not in DB"); continue
        pid, vid, head, old = row
        new = norm(c["text"]); head = head or ""
        if norm(old) == new:
            print(f"  ok   {c['citation']}: already correct"); continue
        print(f"  FIX  {c['citation']}: {len(old)}c -> {len(new)}c  ({c.get('applies_amendment') or 'source-defect'})")
        if args.apply:
            con.execute("INSERT INTO provisions_fts(provisions_fts, rowid, citation, heading, text_content) "
                        "VALUES('delete', ?, ?, ?, ?)", (vid, c["citation"], head, old))
            auth = (f"current text (ndconst.org, corrected for amend {c['applies_amendment']})"
                    if c.get("applies_amendment") else "current text (corrected — ndconst.org source defect)")
            con.execute("UPDATE provision_versions SET text_content=?, source_authority=? WHERE id=?",
                        (new, auth, vid))
            corpus.index_version_fts(con, vid, c["citation"], head, new)
            con.execute("INSERT INTO changelog (batch, provision_id, version_id, field, old_value, new_value, authority) "
                        "VALUES (?,?,?,?,?,?,?)", (BATCH, pid, vid, "current_text_corrected",
                        (old[:60] + "…") if old else None, "corrected from primary source",
                        c.get("reason", "")[:120]))
            n += 1
    if args.apply:
        con.commit(); print(f"applied {n} corrections to {args.db}")
    else:
        print("(dry run) re-run with --apply")
    con.close()


if __name__ == "__main__":
    main()
