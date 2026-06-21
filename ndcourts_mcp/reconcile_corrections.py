"""Reconcile logged corrections against the current DB — detect silent reversions.

The DB is the single source of truth, but ingest / merge_nd_metadata re-read the
``~/refs`` source and can silently overwrite a corrected field back to its
(often wrong) source value, without logging. The ``changelog`` table records the
intent of every correction; this module compares that intent to reality.

For each ``(opinion_id, field)`` where ``field`` is a real, literal-valued
``opinions`` column, the LATEST ``new_value`` in the changelog is the intended
current state. Compared to the actual DB value:

  * current == latest new_value   -> INTACT     (correction held)
  * current == earliest old_value -> REVERTED   (silently lost)
  * otherwise                     -> DIVERGED    (third value; review)

``text_content`` is excluded: its changelog rows store human descriptions
("dropped appended OCR copy"), not literal values, so they can't be reconciled
this way (text needs a content-hash method).

Two consumers:
  * ``invariants.py`` -> the ``corrections_not_reverted`` check (count REVERTED)
  * ``merge_nd_metadata`` / ``ingest`` -> ``corrected_values()`` as a write guard
    (never clobber a field whose corrected value differs from the source).
"""
from __future__ import annotations

import argparse
import sqlite3
from collections import defaultdict
from pathlib import Path

from .db import DEFAULT_DB_PATH, get_connection, log_change

# changelog fields whose new_value is NOT a literal column value
NON_LITERAL_FIELDS = {"text_content"}

# Content-correction fields safe to restore in isolation. source_reporter /
# source_path are deliberately excluded: they are provenance fields coupled to
# opinion_sources and the source_*_matches_primary invariants, so a blind
# restore could desync — they need the align_primary_source path instead.
SAFE_RESTORE_FIELDS = {
    "case_name", "case_name_full", "docket_number", "author", "date_filed",
    "judges", "opinion_url", "per_curiam", "court", "notes", "disposition",
}
RESTORE_BATCH = "restore-reverted-corrections-2026-06-21"


def _literal_corrected_fields(conn: sqlite3.Connection) -> set[str]:
    cols = {r[1] for r in conn.execute("PRAGMA table_info(opinions)")}
    return cols - NON_LITERAL_FIELDS


def _chains(conn: sqlite3.Connection):
    """{(opinion_id, field): [rows oldest..newest]} for reconcilable fields."""
    fields = _literal_corrected_fields(conn)
    chain: dict = defaultdict(list)
    for r in conn.execute(
        "SELECT opinion_id, field, old_value, new_value, batch, timestamp, id "
        "FROM changelog ORDER BY timestamp, id"
    ):
        if r["field"] in fields:
            chain[(r["opinion_id"], r["field"])].append(r)
    return chain


def corrected_values(conn: sqlite3.Connection,
                     only_fields: set[str] | None = None) -> dict[tuple[int, str], str | None]:
    """{(opinion_id, field): intended value} — the latest logged new_value.

    The write-guard interface: a writer about to set ``field`` on ``opinion_id``
    should keep this value instead of the incoming source value when the two
    differ. ``only_fields`` restricts to the columns a given writer touches.
    """
    out: dict = {}
    for (oid, field), rows in _chains(conn).items():
        if only_fields and field not in only_fields:
            continue
        out[(oid, field)] = rows[-1]["new_value"]
    return out


def _eq(a, b) -> bool:
    return ("" if a is None else str(a)) == ("" if b is None else str(b))


def reconcile(conn: sqlite3.Connection):
    """Return (reverted, diverged) lists of dicts."""
    reverted, diverged = [], []
    for (oid, field), rows in _chains(conn).items():
        cur = conn.execute(f"SELECT {field} AS v FROM opinions WHERE id=?", (oid,)).fetchone()
        if cur is None:
            continue  # opinion merged away — correction moot
        cur = cur["v"]
        latest_new = rows[-1]["new_value"]
        first_old = rows[0]["old_value"]
        if _eq(cur, latest_new):
            continue  # INTACT
        rec = dict(opinion_id=oid, field=field, current=cur,
                   intended=latest_new, original=first_old,
                   last_batch=rows[-1]["batch"])
        (reverted if _eq(cur, first_old) else diverged).append(rec)
    return reverted, diverged


def find_reverted(conn: sqlite3.Connection):
    return reconcile(conn)[0]


def restore_reverted(conn: sqlite3.Connection, fields: set[str] = SAFE_RESTORE_FIELDS,
                     apply: bool = False) -> list[dict]:
    """Rewrite each silently-reverted field back to its changelog-intended value.

    Only touches REVERTED entries in ``fields`` (a clean re-apply, not a guess);
    DIVERGED is left for human review. Each write is logged so the reconciliation
    sees it as INTACT afterward.
    """
    todo = [r for r in find_reverted(conn) if r["field"] in fields]
    if apply:
        for r in todo:
            conn.execute(f"UPDATE opinions SET {r['field']} = ? WHERE id = ?",
                         (r["intended"], r["opinion_id"]))
            log_change(conn, RESTORE_BATCH, r["opinion_id"], r["field"],
                       r["current"], r["intended"],
                       authority="surgical restore of silently-reverted correction")
        conn.commit()
    return todo


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    p.add_argument("--csv", type=Path, default=Path("triage") / "changelog-reconcile.csv")
    p.add_argument("--show", type=int, default=0, help="print first N reverted")
    p.add_argument("--restore", action="store_true",
                   help="re-apply silently-reverted content corrections (dry-run unless --apply)")
    p.add_argument("--apply", action="store_true", help="with --restore, write the restores")
    args = p.parse_args(argv)

    if args.restore:
        conn = get_connection(args.db)
        conn.row_factory = sqlite3.Row
        todo = restore_reverted(conn, apply=args.apply)
        from collections import Counter
        by = Counter(r["field"] for r in todo)
        excluded = [r for r in find_reverted(conn) if r["field"] not in SAFE_RESTORE_FIELDS]
        conn.close()
        verb = "RESTORED" if args.apply else "WOULD RESTORE"
        print(f"{verb} {len(todo)} reverted content corrections:")
        for f, n in by.most_common():
            print(f"    {f:<18} {n}")
        print(f"  ({len(excluded)} reverted left untouched — provenance fields "
              "source_reporter/source_path, restore via align_primary_source)")
        if not args.apply:
            print("\nRe-run with --restore --apply to write.")
        return

    conn = sqlite3.connect(str(args.db)); conn.row_factory = sqlite3.Row
    reverted, diverged = reconcile(conn)
    conn.close()

    from collections import Counter
    rc, dc = Counter(r["field"] for r in reverted), Counter(d["field"] for d in diverged)
    print(f"REVERTED (silently lost): {len(reverted)}")
    for f, n in rc.most_common():
        print(f"    {f:<18} {n}")
    print(f"DIVERGED (review):        {len(diverged)}")
    for f, n in dc.most_common():
        print(f"    {f:<18} {n}")

    import csv
    args.csv.parent.mkdir(parents=True, exist_ok=True)
    with args.csv.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["status", "opinion_id", "field", "current", "intended", "original", "last_batch"])
        for r in reverted:
            w.writerow(["REVERTED", r["opinion_id"], r["field"], r["current"],
                        r["intended"], r["original"], r["last_batch"]])
        for d in diverged:
            w.writerow(["DIVERGED", d["opinion_id"], d["field"], d["current"],
                        d["intended"], d["original"], d["last_batch"]])
    print(f"\nWrote {args.csv}")
    for r in reverted[:args.show]:
        print(f"  {r['opinion_id']} {r['field']}: now {r['current']!r} (intended {r['intended']!r})")


if __name__ == "__main__":
    main()
