"""Explicit-oid promote for the 2 receive_westlaw AMBIGUOUS docs that the
auto-resolver couldn't disambiguate — Sletten/Moosbrugger share 536 N.W.2d 354
AND the same filing date, so the formulaic disciplinary captions don't resolve.
Each doc is hand-confirmed to its oid; reuses the tested receive_westlaw._promote
(jaccard safety gate still applies). Logs under the same batch as the main run.
"""
import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from ndcourts_mcp.db import DEFAULT_DB_PATH, get_connection  # noqa: E402
from ndcourts_mcp.ingest_westlaw import _doc_to_text  # noqa: E402
from ndcourts_mcp import receive_westlaw as rw  # noqa: E402

INC = REPO.parent  # unused
PAIRS = [
    (11968, "/Users/jerod/refs/nd/opin/westlaw-incoming/singlesource-2026-05-25/"
            "Westlaw Precision - 2 items from Find And Print/"
            "2 - Matter of Disciplinary Action Against Sletten.doc"),
    (11969, "/Users/jerod/refs/nd/opin/westlaw-incoming/singlesource-2026-05-25/"
            "Westlaw Precision - 81 items from Find And Print/"
            "81 - Matter of Disciplinary Action Against Moosbrugger.doc"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    conn = get_connection(DEFAULT_DB_PATH)
    for oid, path in PAIRS:
        p = Path(path)
        parsed = rw._parse(_doc_to_text(p))
        if not parsed:
            print(f"  oid {oid}: PARSE FAILED ({p.name})")
            continue
        archive = rw._archive_doc(p, parsed.get("primary_citation", ""),
                                  parsed.get("case_name", "")) if args.apply \
            else f"N.W.2d/(dry)/{p.name}"
        msg = rw._promote(conn, oid, parsed, archive, args.apply)
        print(f"  oid {oid} <- {p.name[:48]} : {msg}")
    if args.apply:
        conn.commit()
        print(f"\nAPPLIED (batch {rw.BATCH}).")
    else:
        print("\nDRY-RUN. Re-run with --apply.")


if __name__ == "__main__":
    raise SystemExit(main())
