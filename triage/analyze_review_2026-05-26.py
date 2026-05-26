"""Read-only characterization of the residual §6 DEFER_MODERN review
buckets: LOWJAC_REVIEW + DOCKET_CONFLICT_MIDJAC.

For each pair, surface the signals that resolved the earlier tiers:
  - shared cite (+ type), each side's cites / docket / date / sources
  - is either side a CL "summary opinion" stub (tiny text)?
  - NW2d page-json owner (authoritative occupant of a shared N.W.2d page)
  - does either side's neutral cite duplicate ANOTHER oid (a full
    counterpart elsewhere -> stub-merge candidate)?
Emits a per-pair report to stdout for manual adjudication.
"""
import json
import re
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ndcourts_mcp.multisource_diff import (  # noqa: E402
    jaccard, normalize_words, shingles)

DB = Path("opinions.db")
NW = Path("/Users/jerod/refs/nd/opin/NW2d")
TSV = "triage/defer-modern-adjudication-2026-05-26.tsv"


def jac(db, a, b):
    ta = db.execute("SELECT text_content FROM opinions WHERE id=?",
                    (a,)).fetchone()[0] or ""
    tb = db.execute("SELECT text_content FROM opinions WHERE id=?",
                    (b,)).fetchone()[0] or ""
    return jaccard(shingles(normalize_words(ta)), shingles(normalize_words(tb)))


def is_stub(db, oid):
    t = db.execute("SELECT text_content FROM opinions WHERE id=?",
                   (oid,)).fetchone()[0] or ""
    return len(t) < 700 or "summary opinion" in t.lower()


def neutral_dupes(db, oid):
    """other oids that share this opinion's primary neutral cite."""
    nc = db.execute("SELECT citation FROM citations WHERE opinion_id=? AND "
                    "is_primary=1 AND reporter='ND-neutral'", (oid,)).fetchone()
    if not nc:
        return nc, []
    others = [r[0] for r in db.execute(
        "SELECT opinion_id FROM citations WHERE citation=? AND opinion_id<>?",
        (nc[0], oid))]
    return nc[0], others


def main():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    rows = [l.split("\t") for l in open(TSV).read().splitlines()[1:]
            if l.split("\t")[0] in ("LOWJAC_REVIEW", "DOCKET_CONFLICT_MIDJAC")]
    seen = set()
    for r in rows:
        bucket, shared, a, b = r[0], r[1], int(r[2]), int(r[3])
        if (a, b) in seen or (b, a) in seen:
            continue
        seen.add((a, b))
        print("=" * 72)
        print(f"[{bucket}] shared={shared!r}  jac={jac(db, a, b):.2f}")
        m = re.match(r"(\d+)\s*N\.?W\.?(?:2d|3d)?\s*(\d+)", shared)
        if m:
            jp = NW / m.group(1) / f"{m.group(2)}.json"
            owner = (json.loads(jp.read_text()).get("docket_number")
                     if jp.exists() else "NO_JSON")
            print(f"   NW2d/{m.group(1)}/{m.group(2)}.json owner docket: {owner!r}")
        for oid in (a, b):
            o = db.execute("SELECT case_name,docket_number,date_filed FROM "
                           "opinions WHERE id=?", (oid,)).fetchone()
            cites = [c[0] for c in db.execute(
                "SELECT citation FROM citations WHERE opinion_id=? "
                "ORDER BY is_primary DESC", (oid,))]
            srcs = [s[0] for s in db.execute(
                "SELECT source_reporter FROM opinion_sources WHERE "
                "opinion_id=?", (oid,))]
            nc, dupes = neutral_dupes(db, oid)
            tag = " STUB" if is_stub(db, oid) else ""
            dtag = f"  neutral_dupe_oids={dupes}" if dupes else ""
            print(f"   oid {oid}{tag}: {o['case_name']!r} dk={o['docket_number']!r} "
                  f"{o['date_filed']}")
            print(f"       cites={cites} srcs={srcs}{dtag}")
    db.close()


if __name__ == "__main__":
    main()
