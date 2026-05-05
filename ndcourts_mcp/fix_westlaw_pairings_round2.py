"""Fix four more wrong-paired Westlaw .docs surfaced by the multi-source diff audit.

Same shape as the original 9-pairings cluster (see ``fix_westlaw_pairings``):
two opinions share the same bound N.D. page, the volume-based ingest
arbitrarily paired one .doc with one opinion and orphaned the other.
The diff audit caught these four because each wrongly-paired .doc has
text totally unrelated to the linked opinion (similarity < 0.20).

Pairs to fix:

  vol/page 51/300  Dorr State Bank v Adams (oid 3011) ↔ Dickey v Gesme (oid 3007)
  vol/page 21/69   Willis v Weatherwax     (oid 699)  ↔ State ex rel Kramer v Kiefer (oid 733)
  vol/page 12/504  Montgomery v Tucker     (oid 5982) ↔ Sykes v Allen   (oid 6023)
  vol/page 27/458  Hackney v Lynn          (oid 1186) ↔ Bussey v Boynton (oid 1189)

In each case the "wrong-paired" opinion has the wrong .doc currently
attached; the "correct-but-orphan" opinion has no Westlaw .doc at all.
The matching .doc files exist in ``N.D./<vol>/`` named after their
true case names. Fix:

  1. Delete the wrong .doc ↔ wrong-paired opinion linkage.
  2. Insert wrong .doc ↔ correct opinion (its actual home).
  3. Insert the orphan .doc ↔ wrong-paired opinion (so it gets its
     correct .doc).

After applying, run ``merge_westlaw_text --apply`` to pull the
corrected text into both opinions in each pair.

Usage:
    python -m ndcourts_mcp.fix_westlaw_pairings_round2 [--apply]
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

from .db import DEFAULT_DB_PATH, get_connection, log_provenance


REFS_ROOT = Path("/Users/jerod/refs/nd/opin/N.D.")
BATCH = "fix-westlaw-pairings-round2-2026-05-04"


@dataclass(frozen=True)
class Pair:
    vol: int
    page: int
    wrong_paired_doc: str       # currently linked to wrong_paired_opinion; belongs to correct_opinion
    wrong_paired_opinion: int
    correct_opinion: int        # true home of wrong_paired_doc
    orphan_doc: str             # currently unlinked; belongs to wrong_paired_opinion
    orphan_opinion: int         # = wrong_paired_opinion (the row that needs the orphan)

    def wrong_paired_path(self) -> Path:
        return REFS_ROOT / str(self.vol) / self.wrong_paired_doc

    def orphan_path(self) -> Path:
        return REFS_ROOT / str(self.vol) / self.orphan_doc


PAIRS: list[Pair] = [
    Pair(
        vol=51, page=300,
        wrong_paired_doc="0300-Dickey-County-v-Gesme.doc",
        wrong_paired_opinion=3011,           # Dorr v. Adams
        correct_opinion=3007,                # County of Dickey v. Gesme
        orphan_doc="0300-Dorr-County-State-Bank-v-Adams.doc",
        orphan_opinion=3011,
    ),
    Pair(
        vol=21, page=69,
        wrong_paired_doc="0069-State-v-Kiefer.doc",
        wrong_paired_opinion=699,            # Willis v. Weatherwax
        correct_opinion=733,                 # State ex rel Kramer v. Kiefer
        orphan_doc="0069-Willis-v-Weatherwax.doc",
        orphan_opinion=699,
    ),
    Pair(
        vol=12, page=504,
        wrong_paired_doc="0504-Sykes-v-Allen.doc",
        wrong_paired_opinion=5982,           # Montgomery v. Tucker
        correct_opinion=6023,                # Sykes v. Allen
        orphan_doc="0504-Montgomery-v-Tucker.doc",
        orphan_opinion=5982,
    ),
    Pair(
        vol=27, page=458,
        wrong_paired_doc="0458-Bussey-v-Boynton.doc",
        wrong_paired_opinion=1186,           # Hackney v. Lynn
        correct_opinion=1189,                # Bussey v. Boynton
        orphan_doc="0458-Hackney-v-Lynn.doc",
        orphan_opinion=1186,
    ),
]


def _log(conn, oid, field, old, new):
    conn.execute(
        "INSERT INTO changelog (batch, opinion_id, field, old_value, new_value) "
        "VALUES (?, ?, ?, ?, ?)",
        (BATCH, oid, field, old, new),
    )


def _doc_path_in_db(p: Pair, doc: str) -> str:
    """The path string the existing opinion_sources row uses (absolute)."""
    return str(REFS_ROOT / str(p.vol) / doc)


def apply_pair(conn, p: Pair) -> int:
    written = 0
    wrong_doc_db = _doc_path_in_db(p, p.wrong_paired_doc)
    orphan_doc_db = _doc_path_in_db(p, p.orphan_doc)

    if not p.wrong_paired_path().exists():
        raise RuntimeError(f"missing .doc on disk: {p.wrong_paired_path()}")
    if not p.orphan_path().exists():
        raise RuntimeError(f"missing .doc on disk: {p.orphan_path()}")

    # 1. Delete wrong linkage
    row = conn.execute(
        "SELECT id FROM opinion_sources "
        "WHERE opinion_id = ? AND source_reporter = 'westlaw' AND source_path = ?",
        (p.wrong_paired_opinion, wrong_doc_db),
    ).fetchone()
    if row is None:
        raise RuntimeError(
            f"no opinion_sources row for opinion {p.wrong_paired_opinion} "
            f"linked to {wrong_doc_db}"
        )
    conn.execute("DELETE FROM opinion_sources WHERE id = ?", (row["id"],))
    _log(conn, p.wrong_paired_opinion, "opinion_sources.westlaw",
         f"row {row['id']} → {wrong_doc_db}", None)
    written += 1

    # 2. Insert correct linkage for the wrong .doc (it belongs to correct_opinion)
    text_length = p.wrong_paired_path().stat().st_size
    cur = conn.execute(
        "INSERT INTO opinion_sources "
        "(opinion_id, source_reporter, source_path, text_length, is_primary, added_at) "
        "VALUES (?, 'westlaw', ?, ?, 0, datetime('now'))",
        (p.correct_opinion, wrong_doc_db, text_length),
    )
    _log(conn, p.correct_opinion, "opinion_sources.westlaw",
         None, f"row {cur.lastrowid} → {wrong_doc_db}")
    written += 1

    # 3. Insert orphan linkage to its true home (= wrong_paired_opinion)
    text_length = p.orphan_path().stat().st_size
    cur = conn.execute(
        "INSERT INTO opinion_sources "
        "(opinion_id, source_reporter, source_path, text_length, is_primary, added_at) "
        "VALUES (?, 'westlaw', ?, ?, 0, datetime('now'))",
        (p.orphan_opinion, orphan_doc_db, text_length),
    )
    _log(conn, p.orphan_opinion, "opinion_sources.westlaw",
         None, f"row {cur.lastrowid} → {orphan_doc_db}")
    written += 1

    return written


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    p.add_argument("--apply", action="store_true",
                   help="Write changes (default is dry-run)")
    args = p.parse_args()

    print(f"Pairs queued: {len(PAIRS)}")
    for pair in PAIRS:
        print(f"  vol {pair.vol} page {pair.page}:")
        print(f"    detach    {pair.wrong_paired_doc} from oid {pair.wrong_paired_opinion}")
        print(f"    attach    {pair.wrong_paired_doc} to   oid {pair.correct_opinion}")
        print(f"    attach    {pair.orphan_doc} to   oid {pair.orphan_opinion}")

    if not args.apply:
        print("\n(dry-run; pass --apply to write changes)")
        return

    print(f"\nApplying… batch={BATCH}")
    conn = get_connection(args.db)
    written = 0
    try:
        for pair in PAIRS:
            written += apply_pair(conn, pair)
        log_provenance(
            conn,
            operation="fix_westlaw_pairings_round2",
            command=" ".join(sys.argv),
            rows_affected=written,
            notes=f"batch={BATCH}; pairs={len(PAIRS)}",
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise

    print(f"Done. {written} changelog rows written.")
    print()
    print("Next: run `python -m ndcourts_mcp.merge_westlaw_text --apply "
          f"--batch {BATCH}-text-merge` to refresh text_content for "
          f"{len(PAIRS) * 2} affected opinions.")


if __name__ == "__main__":
    main()
