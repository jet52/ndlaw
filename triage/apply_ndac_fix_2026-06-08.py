#!/usr/bin/env python3
"""Apply the NDAC extraction-bug fixes to admincode.db (TODO PL-3).

The admin code was extracted by the same buggy `scrape_nd_code.py` converter as
the NDCC statutes, so it carries the same two bugs:
  * dropped cross-reference lines (TOC filter ate wrapped body lines), and
  * phantom-duplicate headers (a wrapped body cross-reference mis-parsed as a
    section header, fragmenting the section; the phantom won first-wins dedup
    at ingest so some DB sections hold garbage).
Both are fixed in the converter (code-mirror ce5af93). This compares
admincode.db against a clean re-extraction (`--reextract`, default /tmp/ndac_fixed,
0 phantom dups) and, for every admin section whose DB heading or text differs,
replaces both with the clean re-extraction's. Parsing matches the ingest exactly
(ingest_admin.section_files + parse_sections, first-wins dedup).

    python triage/apply_ndac_fix_2026-06-08.py [--reextract /tmp/ndac_fixed]
        [--db admincode.db] [--apply] [--show N]
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ndcourts_mcp import corpus  # noqa: E402
from ndcourts_mcp.ingest_admin import section_files, parse_sections  # noqa: E402

BATCH = "ndac-extraction-fix-2026-06-08"
AUTHORITY = ("clean re-extraction of official ndlegis.gov NDAC chapter PDFs after fixing "
             "the dropped-line and phantom-duplicate-header bugs in scrape_nd_code.py "
             "(0 phantom dups corpus-wide); see TODO PL-3")


def reextract(root: Path):
    """sec_num -> (heading, text), first-wins, exactly as ingest_admin builds."""
    out = {}
    for f in section_files(root, None):
        for sec in parse_sections(f.read_text()):
            out.setdefault(sec["sec_num"], (sec["heading"], (sec["text"] or "").strip()))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reextract", type=Path, default=Path("/tmp/ndac_fixed"))
    ap.add_argument("--db", default=None)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--show", type=int, default=12)
    args = ap.parse_args()

    new = reextract(args.reextract)
    db_path = Path(args.db) if args.db else corpus.resolve_corpus_db_path("admin")
    conn = corpus.get_corpus_connection(db_path, must_exist=True)
    rows = conn.execute(
        """SELECT p.id, pv.id, p.citation, p.heading, pv.text_content
             FROM provisions p JOIN provision_versions pv ON pv.id = p.current_version_id
            WHERE p.corpus = 'admin'""").fetchall()
    db_secs = {r[2].replace("N.D.A.C. § ", "").strip() for r in rows}

    # A handful of sections live inside enormous embedded tables (hazardous-waste
    # treatment-standards chapters) where BOTH the old and new extraction misjudge
    # the section boundary and the re-extraction's heading comes out as a body
    # sentence. Don't auto-overwrite those — hold them for manual review against
    # the official text.
    _SENT = re.compile(r'^(the|this|that|these|those|all|a|an|if|where|when|it|no|'
                       r'each|any|there|upon|whenever|for purposes|notwithstanding|'
                       r'in the case|except)\b', re.I)
    def sentence_like(h):
        return bool(h) and (h[0].islower() or (_SENT.match(h) and len(h) > 45))

    changed, held, only_db = [], [], 0
    for pid, vid, citation, db_head, db_text in rows:
        sec = citation.replace("N.D.A.C. § ", "").strip()
        if sec not in new:
            only_db += 1
            continue
        nh, nt = new[sec]
        if (db_text or "").strip() != nt or (db_head or "") != (nh or ""):
            if sentence_like(nh):
                held.append(sec)
                continue
            changed.append((sec, pid, vid, citation, db_head, db_text or "", nh, nt))
    only_new = [s for s in new if s not in db_secs]
    print(f"HELD (re-extraction heading is a body sentence — manual review): "
          f"{len(held)} -> {sorted(held)}")

    text_diffs = sum(1 for c in changed if (c[5] or "").strip() != c[7])
    head_diffs = sum(1 for c in changed if (c[4] or "") != (c[6] or ""))
    grew = sum(1 for c in changed if len(c[7]) > len(c[5]))
    print(f"DB admin sections: {len(rows)}   re-extracted: {len(new)}")
    print(f"sections to update: {len(changed)}  (text diffs {text_diffs}, heading diffs {head_diffs}; "
          f"grew {grew}, shrank {len(changed)-grew})")
    print(f"only-in-DB: {only_db}   only-in-re-extract: {len(only_new)} {only_new[:8]}")
    print(f"\n--- sample (first {args.show}) ---")
    for sec, pid, vid, cit, dh, dt, nh, nt in changed[:args.show]:
        print(f"§ {sec}: DB {len(dt)}c -> new {len(nt)}c | head: {dh!r} -> {nh!r}")

    if not args.apply:
        print(f"\nDry run. {len(changed)} sections would be updated. Re-run with --apply.")
        return

    for sec, pid, vid, cit, dh, dt, nh, nt in changed:
        conn.execute(
            "INSERT INTO provisions_fts(provisions_fts, rowid, citation, heading, text_content) "
            "VALUES('delete', ?, ?, ?, ?)", (vid, cit, dh or "", dt))
        conn.execute("UPDATE provision_versions SET text_content=? WHERE id=?", (nt, vid))
        if (dh or "") != (nh or ""):
            conn.execute("UPDATE provisions SET heading=? WHERE id=?", (nh, pid))
        corpus.index_version_fts(conn, vid, cit, nh, nt)
        conn.execute(
            """INSERT INTO changelog (batch, provision_id, version_id, field,
                                      old_value, new_value, authority)
               VALUES (?,?,?,?,?,?,?)""",
            (BATCH, pid, vid, "heading+text_content",
             f"[extraction bug; head={dh!r}; {len(dt)} chars]",
             f"[clean re-extraction; head={nh!r}; {len(nt)} chars]", AUTHORITY))
    conn.execute(
        "INSERT INTO provenance (operation, command, source_paths, rows_affected, notes) "
        "VALUES (?,?,?,?,?)",
        ("apply_ndac_fix", BATCH, str(args.reextract), len(changed),
         f"corrected {len(changed)} NDAC sections (dropped-line + phantom-header bugs)"))
    conn.commit()
    print(f"\nAPPLIED: {len(changed)} sections updated, batch {BATCH}.")


if __name__ == "__main__":
    main()
