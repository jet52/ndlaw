"""Apply the 3 clean cite-swap fixes from C-Track PDFs (canonical tree = ~/refs/nd/opin).

(1) 2021 ND 163 rebuild (oid 19599): label already correct; content was a verified
    exact dup (jaccard 1.0) of 19583 (2021 ND 106). Rebuild text/metadata from the
    authoritative ~/Downloads/2021ND163.pdf; copy PDF + write markdown into refs.
(2) Norberg swap (19652 2022 ND 139-content-2023 ND 1  <->  19711 2023 ND 1-content-2022 ND 139):
    swap the neutral-cite labels + source_paths + the misnamed on-disk md/pdf files.
    Dates already match content (19652=2023-01-05, 19711=2022-07-21).
(3) Legacie-Lowe swap (19736 <-> 19833): same swap; plus fix 19833's date to 2023-08-02
    (real 2023 ND 140 date; 19736/2023 ND 88 keeps 2023-05-09, which is correct).

Snapshot: opinions.db.bak-pre-ctrack-clean3-2026-05-26. File renames are symmetric
(via temp), no data loss. DB row deletions: none.
"""
from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

from ndcourts_mcp.db import DEFAULT_DB_PATH, get_connection, log_change, log_provenance
from triage.ctrack_pdf import parse as parse_pdf

REFS = Path("/Users/jerod/refs/nd/opin")
DL = Path("/Users/jerod/Downloads")
BATCH = "fix-ctrack-clean3-2026-05-26"


def clean_text(raw: str) -> str:
    i = raw.find("IN THE SUPREME COURT")
    body = raw[i:] if i != -1 else raw
    body = body.replace("\f", "\n")
    return re.sub(r"\n{3,}", "\n\n", body).strip() + "\n"


def swap_files(a: Path, b: Path, apply: bool):
    print(f"    swap file {a.name} <-> {b.name}  (exist: {a.exists()}/{b.exists()})")
    if not apply:
        return
    tmp = a.with_suffix(a.suffix + ".swaptmp")
    a.rename(tmp); b.rename(a); tmp.rename(b)


def swap_cite_and_source(conn, oid_a, cite_a, src_a, oid_b, cite_b, src_b, apply):
    """A currently has cite_a/src_a, B has cite_b/src_b -> give A cite_b/src_b, B cite_a/src_a."""
    print(f"    {oid_a}: cite {cite_a}->{cite_b}, src ->{src_b}")
    print(f"    {oid_b}: cite {cite_b}->{cite_a}, src ->{src_a}")
    if not apply:
        return
    for oid, oldc, newc, news in [(oid_a, cite_a, cite_b, src_b), (oid_b, cite_b, cite_a, src_a)]:
        log_change(conn, BATCH, oid, "citation", oldc, newc, authority="C-Track PDF (file-level cite swap)")
        conn.execute("UPDATE citations SET citation=? WHERE opinion_id=? AND citation=? AND reporter='ND-neutral'",
                     (newc, oid, oldc))
        conn.execute("UPDATE opinions SET source_path=? WHERE id=?", (news, oid))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    conn = get_connection(args.db)
    print(f"=== {'APPLY' if args.apply else 'DRY RUN'} (batch {BATCH}) ===")

    # (1) 2021 ND 163 rebuild from PDF -------------------------------------
    print("(1) rebuild 19599 = 2021 ND 163 from ~/Downloads/2021ND163.pdf")
    d = parse_pdf(DL / "2021ND163.pdf")
    assert d["cite"] == "2021 ND 163", d["cite"]
    text = clean_text(d["text"])
    new = dict(case_name="Interest of K.B.", date="2021-09-09",
               docket=d["dockets"][0], author=d["author"], pc=int(d["per_curiam"]))
    print(f"    -> case_name={new['case_name']} date={new['date']} docket={new['docket']} "
          f"author={new['author']} pc={new['pc']} textlen={len(text)}")
    if args.apply:
        (REFS / "pdfs/2021").mkdir(parents=True, exist_ok=True)
        (REFS / "markdown/2021").mkdir(parents=True, exist_ok=True)
        shutil.copyfile(DL / "2021ND163.pdf", REFS / "pdfs/2021/2021ND163.pdf")
        (REFS / "markdown/2021/2021ND163.md").write_text(text, encoding="utf-8")
        old = conn.execute("SELECT case_name,date_filed,docket_number,author,per_curiam FROM opinions WHERE id=19599").fetchone()
        for f, o, n in [("case_name", old["case_name"], new["case_name"]),
                        ("date_filed", old["date_filed"], new["date"]),
                        ("docket_number", old["docket_number"], new["docket"]),
                        ("author", old["author"], new["author"]),
                        ("per_curiam", str(old["per_curiam"]), str(new["pc"])),
                        ("text_content", "<leaked: 2021 ND 106 dup>", "<rebuilt from 2021ND163.pdf>")]:
            if str(o) != str(n):
                log_change(conn, BATCH, 19599, f, str(o), str(n), authority="rebuilt from C-Track 2021ND163.pdf")
        conn.execute("UPDATE opinions SET case_name=?, date_filed=?, docket_number=?, author=?, "
                     "per_curiam=?, text_content=?, source_reporter='ND', source_path=? WHERE id=19599",
                     (new["case_name"], new["date"], new["docket"], new["author"], new["pc"],
                      text, "markdown/2021/2021ND163.md"))

    # (2) Norberg swap -----------------------------------------------------
    print("(2) Norberg swap 19652<->19711")
    swap_cite_and_source(conn, 19652, "2022 ND 139", "markdown/2022/2022ND139.md",
                         19711, "2023 ND 1", "markdown/2023/2023ND1.md", args.apply)
    swap_files(REFS / "markdown/2022/2022ND139.md", REFS / "markdown/2023/2023ND1.md", args.apply)
    swap_files(REFS / "pdfs/2022/2022ND139.pdf", REFS / "pdfs/2023/2023ND1.pdf", args.apply)

    # (3) Legacie-Lowe swap + date fix ------------------------------------
    print("(3) Legacie-Lowe swap 19736<->19833 + 19833 date->2023-08-02")
    swap_cite_and_source(conn, 19736, "2023 ND 140", "markdown/2023/2023ND140.md",
                         19833, "2023 ND 88", "markdown/2023/2023ND88.md", args.apply)
    swap_files(REFS / "markdown/2023/2023ND140.md", REFS / "markdown/2023/2023ND88.md", args.apply)
    swap_files(REFS / "pdfs/2023/2023ND140.pdf", REFS / "pdfs/2023/2023ND88.pdf", args.apply)
    if args.apply:
        log_change(conn, BATCH, 19833, "date_filed", "2023-05-09", "2023-08-02",
                   authority="real 2023 ND 140 filing date per C-Track 2023ND140.pdf")
        conn.execute("UPDATE opinions SET date_filed='2023-08-02' WHERE id=19833")

    if args.apply:
        log_provenance(conn, operation="fix_ctrack_clean3",
                       command="python -m triage.fix_ctrack_clean3_2026-05-26 --apply",
                       rows_affected=5,
                       notes=(f"batch {BATCH}; 2021 ND 163 rebuilt from C-Track PDF (19599); "
                              f"Norberg (19652/19711) + Legacie-Lowe (19736/19833) cite-label swaps "
                              f"+ on-disk md/pdf renames; 19833 date 2023-05-09->2023-08-02. "
                              f"Snapshot opinions.db.bak-pre-ctrack-clean3-2026-05-26."))
        conn.commit()
        print("  committed.")
    conn.close()


if __name__ == "__main__":
    main()
