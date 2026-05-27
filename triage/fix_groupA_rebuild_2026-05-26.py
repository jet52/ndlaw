"""Group A cite-swap repair — rebuild the two genuinely-missing opinions
from user-supplied Westlaw .docs + add Jesser's N.W.2d parallel.

Context (verified this session against the .docs + web):
  * 19290 (label 2018 ND 246) held a DUPLICATE of 2017 ND 1 — the real
    2018 ND 246 (a distinct 11/15/2018 per curiam DAPL pro-hac-vice
    extension order, docket 20160436, 920 N.W.2d 908) was missing.
  * 19429 (label 2019 ND 283 State v. Pailing) held a DUPLICATE of
    *Jesser* — the real State v. Pailing (936 N.W.2d 78, docket 20190086,
    12/12/2019, Crothers J.) was missing.
  * 19433 (Jesser, 2019 ND 287) is CORRECT; only lacked the 936 N.W.2d
    102 parallel.

NOT a swap with the corrected-opinion phantoms (2020 ND 287 / 2023 ND 225
/ 2025 ND 232): per the Court's practice (ruled this session) a corrected
opinion keeps its ORIGINAL neutral cite; the new-year stamp on the
reissue is a template artifact. So Nodak (2022 ND 225) / Albertson
(2023 ND 225) / Sanderson (2024 ND 232) / Bohe (2025 ND 232) are already
correctly cited and are NOT touched here.

Rebuild = replace leaked text with the editorial-stripped Westlaw body
(reusing receive_westlaw._parse / _archive_doc), fix date/docket, add the
N.W.2d parallel, archive the .doc to the canonical refs N.W.2d tree, make
westlaw the primary source, detach the corrupt ND markdown source.
Snapshot opinions.db.bak-pre-groupA-rebuild-2026-05-26; text swaps NOT
changelog-revertible -> revert via snapshot. Dry-run default.
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

BATCH = "section7-groupA-rebuild-2026-05-26"
DL = Path.home() / "Downloads"

REBUILDS = {
    19290: dict(
        doc=DL / "2018ND246 Matter of Petition to Permit Temporary Provision "
                 "of Legal Services by Qualified Attorneys from Outsi.doc",
        neutral="2018 ND 246", nw="920 N.W.2d 908",
        date="2018-11-15", docket="20160436"),
    19429: dict(
        doc=DL / "State v Pailing.doc",
        neutral="2019 ND 283", nw="936 N.W.2d 78",
        date="2019-12-12", docket="20190086"),
}
JESSER_OID, JESSER_NW = 19433, "936 N.W.2d 102"


def _clean_body(body: str) -> str:
    # Drop an orphan leading "Synopsis" header left after the parser
    # stripped the Background/Holdings/Procedural-Posture editorial.
    body = re.sub(r"^\s*Synopsis\s*\n+", "", body)
    return body.strip()


def _frontmatter(case_name: str, date_filed: str, cites: list[str]) -> str:
    return (f'---\ntitle: "{case_name}"\ncourt: "North Dakota Supreme Court"\n'
            f'date_filed: {date_filed}\ncitations:\n'
            + "".join(f' - "{c}"\n' for c in cites) + "---\n\n")


def _add_cite(conn, oid: int, cite: str, apply: bool) -> str:
    exists = conn.execute(
        "SELECT 1 FROM citations WHERE opinion_id=? AND citation=?",
        (oid, cite)).fetchone()
    if exists:
        return f"cite {cite!r} already present"
    if apply:
        conn.execute(
            "INSERT INTO citations (opinion_id, citation, reporter, is_primary) "
            "VALUES (?, ?, ?, 0)", (oid, cite, _classify_reporter(cite)))
        log_change(conn, BATCH, oid, "citation", None, cite,
                   authority=f"Westlaw bound parallel ({cite})")
    return f"+cite {cite!r} ({_classify_reporter(cite)})"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    conn = get_connection(args.db)
    print(f"=== {'APPLY' if args.apply else 'DRY RUN'} (batch {BATCH}) ===")

    for oid, spec in REBUILDS.items():
        doc = spec["doc"]
        if not doc.exists():
            raise SystemExit(f"missing doc: {doc}")
        row = conn.execute("SELECT case_name, date_filed, docket_number, "
                           "source_path FROM opinions WHERE id=?",
                           (oid,)).fetchone()
        parsed = _parse(_doc_to_text(str(doc))) or {}
        body = _clean_body(parsed.get("full_bound_text")
                           or parsed.get("opinion_text") or "")
        if len(body) < 400:
            raise SystemExit(f"oid {oid}: parsed body too short ({len(body)})")
        cites = [spec["neutral"], spec["nw"]]
        text = _frontmatter(row["case_name"], spec["date"], cites) + body
        archive_path = (_archive_doc(doc, spec["nw"], row["case_name"])
                        if args.apply else f"N.W.2d/(dry)/{doc.name}")
        print(f"\n  oid {oid}  {row['case_name'][:40]!r}  -> {spec['neutral']} / {spec['nw']}")
        print(f"    date {row['date_filed']} -> {spec['date']};  docket "
              f"{row['docket_number']!r} -> {spec['docket']!r}")
        print(f"    body_len={len(body)}  archive={archive_path}")
        print(f"    {_add_cite(conn, oid, spec['nw'], args.apply)}")
        if not args.apply:
            continue
        log_change(conn, BATCH, oid, "text_content", f"<leaked {len(row['source_path'] or '')}b src>",
                   f"westlaw:{archive_path}", authority=f"Westlaw bound ({spec['nw']})")
        if row["date_filed"] != spec["date"]:
            log_change(conn, BATCH, oid, "date_filed", row["date_filed"],
                       spec["date"], authority=f"Westlaw bound ({spec['nw']})")
        log_change(conn, BATCH, oid, "docket_number", row["docket_number"],
                   spec["docket"], authority=f"Westlaw bound ({spec['nw']})")
        conn.execute(
            "UPDATE opinions SET text_content=?, date_filed=?, docket_number=?, "
            "source_reporter='westlaw', source_path=? WHERE id=?",
            (text, spec["date"], spec["docket"], archive_path, oid))
        # detach corrupt ND markdown source; install westlaw primary
        conn.execute("DELETE FROM opinion_sources WHERE opinion_id=? "
                     "AND source_reporter='ND'", (oid,))
        conn.execute("UPDATE opinion_sources SET is_primary=0 WHERE opinion_id=?",
                     (oid,))
        conn.execute(
            "INSERT INTO opinion_sources (opinion_id, source_reporter, "
            "source_path, text_length, is_primary, added_at) VALUES "
            "(?, 'westlaw', ?, ?, 1, strftime('%Y-%m-%dT%H:%M:%S','now'))",
            (oid, archive_path, len(body)))
        conn.execute(
            "UPDATE validation_status SET crosscheck_state='corrected', "
            "authority_source=?, batch=?, "
            "validated_at=strftime('%Y-%m-%dT%H:%M:%S','now'), note=? "
            "WHERE opinion_id=?",
            (f"Westlaw bound ({spec['nw']})", BATCH,
             "leaked-text row rebuilt from user-supplied Westlaw .doc; "
             "N.W.2d parallel added; corrupt ND markdown detached", oid))

    # Jesser: parallel cite only (text untouched pending in-body normalization)
    print(f"\n  oid {JESSER_OID}  Jesser  {_add_cite(conn, JESSER_OID, JESSER_NW, args.apply)}")

    if args.apply:
        log_provenance(
            conn, operation="section7_groupA_rebuild",
            command="python -m triage.fix_groupA_rebuild_2026-05-26 --apply",
            source_paths=str(DL),
            rows_affected=len(REBUILDS) + 1,
            notes=(f"batch {BATCH}; rebuilt 19290 (2018 ND 246) + 19429 "
                   f"(State v. Pailing 2019 ND 283) from Westlaw .docs, added "
                   f"N.W.2d parallels (920 N.W.2d 908 / 936 N.W.2d 78) + Jesser "
                   f"936 N.W.2d 102; snapshot opinions.db.bak-pre-groupA-rebuild-"
                   f"2026-05-26; text swaps not changelog-revertible"))
        conn.commit()
        print("\n  committed.")
    conn.close()


if __name__ == "__main__":
    main()
