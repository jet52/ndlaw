"""Fix the Interest of H.J.J.N. text-swap (2024 ND 70 <-> 2024 ND 132).

Same docket 20240060, a retained-jurisdiction sequence; the scraper's
name-scramble put each opinion's text on the OTHER's row:
  * 19877 (label 2024 ND 132) held the 2024 ND 70 text.
  * 20044 (label 2024 ND 70)  held the 2024 ND 132 text.
jaccard(19877,20044)=0.179 -> genuinely two distinct opinions.

Keep each row's EXISTING neutral cite (20044 has 1 inbound cited_by as
2024 ND 70; no repointing) and rebuild each from the user-supplied
authoritative Westlaw .doc so text/date/docket/parallel/author all align:
  * 20044 = 2024 ND 70  — McEvers, Remanded; jurisdiction retained,
            filed 2024-04-18, 5 N.W.3d 775.
  * 19877 = 2024 ND 132 — PER CURIAM mem (post-remand affirm),
            filed 2024-07-05, 9 N.W.3d 656.

Snapshot opinions.db.bak-pre-hjjn-swap-2026-05-26; text swaps revert via
snapshot. Dry-run default.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from ndcourts_mcp.db import (DEFAULT_DB_PATH, get_connection, log_change,
                             log_provenance)
from ndcourts_mcp.ingest import _classify_reporter
from ndcourts_mcp.ingest_westlaw import _doc_to_text
from ndcourts_mcp.receive_westlaw import _archive_doc, _parse

BATCH = "section7-hjjn-swap-2026-05-26"
DL = Path.home() / "Downloads"

SPECS = {
    20044: dict(doc=DL / "Interest of HJJN 70.doc",
                neutral="2024 ND 70", nw="5 N.W.3d 775",
                date="2024-04-18", docket="20240060",
                author="McEvers", per_curiam=0),
    19877: dict(doc=DL / "Interest of HJJN 132.doc",
                neutral="2024 ND 132", nw="9 N.W.3d 656",
                date="2024-07-05", docket="20240060",
                author=None, per_curiam=1),
}


def _clean_body(body: str) -> str:
    return re.sub(r"^\s*Synopsis\s*\n+", "", body).strip()


def _frontmatter(case_name: str, date_filed: str, cites: list[str]) -> str:
    return (f'---\ntitle: "{case_name}"\ncourt: "North Dakota Supreme Court"\n'
            f'date_filed: {date_filed}\ncitations:\n'
            + "".join(f' - "{c}"\n' for c in cites) + "---\n\n")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    conn = get_connection(args.db)
    print(f"=== {'APPLY' if args.apply else 'DRY RUN'} (batch {BATCH}) ===")

    for oid, s in SPECS.items():
        if not s["doc"].exists():
            raise SystemExit(f"missing doc: {s['doc']}")
        row = conn.execute("SELECT case_name, date_filed, docket_number, author, "
                           "per_curiam FROM opinions WHERE id=?", (oid,)).fetchone()
        parsed = _parse(_doc_to_text(str(s["doc"]))) or {}
        body = _clean_body(parsed.get("full_bound_text")
                           or parsed.get("opinion_text") or "")
        if len(body) < 300:
            raise SystemExit(f"oid {oid}: body too short ({len(body)})")
        # sanity: the doc's own neutral cite must match the target cite
        raw = _doc_to_text(str(s["doc"]))
        assert s["neutral"] in raw, f"{s['neutral']} not in {s['doc'].name}"
        cites = [s["neutral"], s["nw"]]
        text = _frontmatter(row["case_name"], s["date"], cites) + body
        archive_path = (_archive_doc(s["doc"], s["nw"], row["case_name"])
                        if args.apply else f"N.W.3d/(dry)/{s['doc'].name}")
        print(f"\n  oid {oid}  keep cite {s['neutral']}  (+{s['nw']})")
        print(f"    text: now holds the WRONG opinion -> rebuild from {s['doc'].name}  body={len(body)}")
        print(f"    date {row['date_filed']} -> {s['date']};  docket "
              f"{row['docket_number']!r} -> {s['docket']!r};  "
              f"author {row['author']!r}->{s['author']!r}  pc {row['per_curiam']}->{s['per_curiam']}")
        if not args.apply:
            continue
        # add the N.W.3d parallel if absent
        if not conn.execute("SELECT 1 FROM citations WHERE opinion_id=? AND citation=?",
                            (oid, s["nw"])).fetchone():
            conn.execute("INSERT INTO citations (opinion_id, citation, reporter, "
                         "is_primary) VALUES (?,?,?,0)",
                         (oid, s["nw"], _classify_reporter(s["nw"])))
            log_change(conn, BATCH, oid, "citation", None, s["nw"],
                       authority=f"Westlaw bound parallel ({s['nw']})")
        auth = f"Westlaw bound ({s['nw']})"
        log_change(conn, BATCH, oid, "text_content", "<swapped-in wrong opinion>",
                   f"westlaw:{archive_path}", authority=auth)
        log_change(conn, BATCH, oid, "date_filed", row["date_filed"], s["date"], authority=auth)
        log_change(conn, BATCH, oid, "docket_number", row["docket_number"], s["docket"], authority=auth)
        if row["author"] != s["author"]:
            log_change(conn, BATCH, oid, "author", row["author"], s["author"], authority=auth)
        if row["per_curiam"] != s["per_curiam"]:
            log_change(conn, BATCH, oid, "per_curiam", str(row["per_curiam"]), str(s["per_curiam"]), authority=auth)
        conn.execute(
            "UPDATE opinions SET text_content=?, date_filed=?, docket_number=?, "
            "author=?, per_curiam=?, source_reporter='westlaw', source_path=? WHERE id=?",
            (text, s["date"], s["docket"], s["author"], s["per_curiam"], archive_path, oid))
        conn.execute("DELETE FROM opinion_sources WHERE opinion_id=? AND source_reporter='ND'", (oid,))
        conn.execute("UPDATE opinion_sources SET is_primary=0 WHERE opinion_id=?", (oid,))
        conn.execute(
            "INSERT INTO opinion_sources (opinion_id, source_reporter, source_path, "
            "text_length, is_primary, added_at) VALUES (?, 'westlaw', ?, ?, 1, "
            "strftime('%Y-%m-%dT%H:%M:%S','now'))", (oid, archive_path, len(body)))
        conn.execute(
            "UPDATE validation_status SET crosscheck_state='corrected', authority_source=?, "
            "batch=?, validated_at=strftime('%Y-%m-%dT%H:%M:%S','now'), note=? WHERE opinion_id=?",
            (auth, BATCH, "H.J.J.N. text-swap repaired from user-supplied Westlaw .doc; "
             "N.W.3d parallel added; corrupt ND markdown detached", oid))

    if args.apply:
        log_provenance(
            conn, operation="section7_hjjn_swap",
            command="python -m triage.fix_hjjn_swap_2026-05-26 --apply",
            source_paths=str(DL), rows_affected=2,
            notes=(f"batch {BATCH}; repaired Interest of H.J.J.N. text-swap "
                   f"(20044=2024 ND 70 / 5 N.W.3d 775 McEvers; 19877=2024 ND 132 "
                   f"/ 9 N.W.3d 656 per curiam), rebuilt from Westlaw .docs, kept "
                   f"each existing neutral cite. Snapshot opinions.db.bak-pre-hjjn-"
                   f"swap-2026-05-26; text swaps not changelog-revertible."))
        conn.commit()
        print("\n  committed.")
    conn.close()


if __name__ == "__main__":
    main()
