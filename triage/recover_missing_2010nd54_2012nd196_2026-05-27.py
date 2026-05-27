"""Recover the 2 genuinely-missing post-1997 opinions found via the
neutral-cite sequence-gap analysis (2026-05-27).

Every year 1997-2026 runs 1->max gap-free EXCEPT three slots; one (2010 ND
149) was an existing row with a mis-tagged reporter (fixed separately), and
these two are absent from the corpus entirely:
  * 2010 ND 54  — Hoffner v. Job Service North Dakota (docket 20090357,
                  789 N.W.2d 731, per curiam, filed 2010-04-06)
  * 2012 ND 196 — Bank of North Dakota v. Brown (docket 20120145,
                  821 N.W.2d 385, per curiam, filed 2012-09-25)

Both have on-disk archive HTML; CREATE each from it (guard: archive title
cites the expected neutral cite). New rows: neutral cite primary, N.W.2d
parallel secondary, archive primary source. Snapshot
opinions.db.bak-pre-recover-gaps-2026-05-27. Dry-run default.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from ndcourts_mcp.db import (DEFAULT_DB_PATH, get_connection, log_change,
                             log_provenance)
from ndcourts_mcp.ingest import _classify_reporter, recompute_primary
from ndcourts_mcp.scrape_archive import parse_opinion_page

REFS = Path("/Users/jerod/refs/nd/opin")
BATCH = "recover-seq-gaps-2026-05-27"

TARGETS = [
    dict(year=2010, docket="20090357", neutral="2010 ND 54"),
    dict(year=2012, docket="20120145", neutral="2012 ND 196"),
]


def _norm_nd(c: str) -> str:
    m = re.search(r"(\d{4})\s+ND\s+0*(\d+)", c or "")
    return f"{m.group(1)} ND {m.group(2)}" if m else (c or "")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    conn = get_connection(args.db)
    print(f"=== {'APPLY' if args.apply else 'DRY RUN'} (batch {BATCH}) ===")
    created = 0
    for t in TARGETS:
        neutral = t["neutral"]
        # must not already exist
        if conn.execute("SELECT 1 FROM citations WHERE citation=?", (neutral,)).fetchone():
            print(f"  {neutral}: already present — SKIP")
            continue
        htm = REFS / f"archive/{t['year']}/{t['docket']}.htm"
        if not htm.exists():
            print(f"  {neutral}: archive {t['docket']}.htm MISSING — SKIP")
            continue
        p = parse_opinion_page(htm.read_text(encoding="utf-8", errors="replace"))
        title_cites = {_norm_nd(c) for c in (p.get("citations") or [])}
        if _norm_nd(neutral) not in title_cites:
            print(f"  {neutral}: GUARD FAIL — archive title cites {p.get('citations')}; SKIP")
            continue
        text = p.get("text", "")
        if len(text) < 150:
            print(f"  {neutral}: text too short ({len(text)}); SKIP")
            continue
        title = p.get("title", "")
        case_name = re.split(r",\s*\d{4}\s+ND\s+\d+", title)[0].strip() or neutral
        date_filed = p.get("date_filed")
        per_curiam = 1 if "per curiam" in (p.get("author_raw") or "").lower() else 0
        # citations: neutral + the parallel N.W. cite from the title
        cites = [neutral] + [c for c in (p.get("citations") or [])
                             if not re.search(r"\bND\b", c)]
        arch_rel = f"archive/{t['year']}/{t['docket']}.htm"
        cite_lines = "".join(f' - "{c}"\n' for c in cites)
        full_text = (f'---\ntitle: "{case_name}"\ncourt: "North Dakota Supreme Court"\n'
                     f'date_filed: {date_filed}\ncitations:\n{cite_lines}'
                     f'docket_number: "{t["docket"]}"\n---\n\n{text}')

        print(f"  CREATE {neutral}: '{case_name}'  date={date_filed} pc={per_curiam} "
              f"docket={t['docket']} cites={cites} textlen={len(text)}")
        if not args.apply:
            continue
        cur = conn.execute(
            "INSERT INTO opinions (case_name, date_filed, court, docket_number, "
            "author, per_curiam, source_reporter, source_path, text_content) "
            "VALUES (?, ?, 'North Dakota Supreme Court', ?, NULL, ?, 'archive', ?, ?)",
            (case_name, date_filed, t["docket"], per_curiam, arch_rel, full_text))
        oid = cur.lastrowid
        log_change(conn, BATCH, oid, "opinions.insert", None,
                   f"{neutral} | {case_name} | {date_filed} | archive {arch_rel}",
                   authority=f"recovered missing opinion from archive {arch_rel} "
                             f"(neutral-cite sequence gap)")
        for c in cites:
            conn.execute("INSERT INTO citations (opinion_id, citation, reporter, "
                         "is_primary) VALUES (?, ?, ?, 0)",
                         (oid, c, _classify_reporter(c)))
            log_change(conn, BATCH, oid, "citation", None, c, authority=f"archive {arch_rel}")
        recompute_primary(conn, oid)
        conn.execute(
            "INSERT INTO opinion_sources (opinion_id, source_reporter, source_path, "
            "text_length, is_primary, added_at) VALUES (?, 'archive', ?, ?, 1, "
            "strftime('%Y-%m-%dT%H:%M:%S','now'))", (oid, arch_rel, len(full_text)))
        conn.execute(
            "INSERT INTO validation_status (opinion_id, era_tier, crosscheck_state, "
            "authority_source, sources_seen, batch, validated_at, note) VALUES "
            "(?, 'modern_1997_2019', 'single_source_accepted', ?, '[\"archive\"]', ?, "
            "strftime('%Y-%m-%dT%H:%M:%S','now'), ?)",
            (oid, f"archive {arch_rel}", BATCH,
             "recovered missing opinion (neutral-cite sequence gap) from court archive HTML"))
        created += 1
        print(f"     -> created oid {oid}")

    if args.apply:
        log_provenance(
            conn, operation="recover_seq_gaps",
            command="python -m triage.recover_missing_2010nd54_2012nd196_2026-05-27 --apply",
            rows_affected=created,
            notes=(f"batch {BATCH}; created {created} missing opinions (2010 ND 54 "
                   f"Hoffner, 2012 ND 196 Bank of ND v. Brown) from on-disk archive "
                   f"HTML, found via sequence-gap analysis. Snapshot "
                   f"opinions.db.bak-pre-recover-gaps-2026-05-27."))
        conn.commit()
        print(f"\n  committed. created={created}")
    conn.close()


if __name__ == "__main__":
    main()
