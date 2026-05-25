"""Scoped Synopsis-editorial strip for the westlaw-receive-2026-05-25 batch only.

The receive_westlaw memorandum-fallback path (`_parse` when `_parse_westlaw_doc`
finds no body) takes the body between the filing date and "All Citations" WITHOUT
running the Synopsis stripper, so the Westlaw editorial Synopsis stub leaked into
some of the 178 promoted rows. This applies the tested `strip_synopsis_editorial`
(keeps court-authored narrative, drops the editorial stub) to ONLY those 178 rows
— not corpus-wide (the wider ~285-row synopsis residue is a separate pre-existing
item). Idempotent; drift-safe; dry-run default.
"""
import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from ndcourts_mcp.db import DEFAULT_DB_PATH, get_connection, log_change  # noqa: E402
from ndcourts_mcp.ingest_nwcite import _split_frontmatter  # noqa: E402
from ndcourts_mcp.strip_westlaw_synopsis import strip_synopsis_editorial  # noqa: E402

BATCH = "strip-westlaw-synopsis-singlesource-2026-05-25"
REPORT = REPO / "triage/westlaw-receive-2026-05-25.tsv"


def promoted_oids():
    oids = []
    for line in REPORT.read_text().splitlines():
        if line.startswith("MATCH"):
            m = re.search(r"oid=(\d+)", line)
            if m:
                oids.append(int(m.group(1)))
    return oids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    conn = get_connection(DEFAULT_DB_PATH)

    changed = unchanged = flagged = 0
    for oid in promoted_oids():
        tc = conn.execute("SELECT text_content FROM opinions WHERE id=?", (oid,)).fetchone()[0]
        fm, body = _split_frontmatter(tc)
        nb, modified, action = strip_synopsis_editorial(body)
        if not modified:
            unchanged += 1
            continue
        new_tc = (fm.rstrip() + "\n\n" + nb.strip()) if fm else nb.strip()
        if len(new_tc) < 0.4 * len(tc) or len(new_tc) < 300:
            flagged += 1
            print(f"  FLAG oid {oid}: strip collapses body {len(tc)}->{len(new_tc)} ({action}) — skipped")
            continue
        changed += 1
        print(f"  oid {oid:>6}: {len(tc)}->{len(new_tc)} (-{len(tc)-len(new_tc)}ch) {action}")
        if args.apply:
            log_change(conn, BATCH, oid, "text_content", tc,
                       f"synopsis-editorial-stripped (-{len(tc)-len(new_tc)}ch)",
                       authority="redistribution scope (NOTICE.md): Westlaw Synopsis stub is "
                                 "editorial; receive_westlaw memorandum-fallback bypassed the stripper")
            conn.execute("UPDATE opinions SET text_content=? WHERE id=?", (new_tc, oid))
    if args.apply:
        conn.commit()
    print(f"\n{'APPLIED' if args.apply else 'DRY-RUN'} batch {BATCH}: "
          f"stripped={changed} unchanged={unchanged} flagged={flagged}")


if __name__ == "__main__":
    raise SystemExit(main())
