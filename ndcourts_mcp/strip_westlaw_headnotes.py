"""Corrective sweep: remove leaked Westlaw editorial (West Headnotes,
Procedural Posture, Synopsis stub) from westlaw-sourced text_content.

Root cause (fixed forward in ingest_westlaw._is_section_header): modern
Westlaw writes "West Headnotes (20)" with a count, so the exact-match
section DROP never fired and the headnote block + Synopsis stub +
"Procedural Posture(s)" leaked into stored text_content — Westlaw
editorial the redistribution scope (NOTICE.md) excludes.

Corrective rule, scope-aligned: court-authored content begins at the
FIRST of — "Syllabus by the Court", "Syllabus", "Attorneys and Law
Firms", "Opinion", or the first author/per-curiam line. Everything
before that (Synopsis stub, West Headnotes block, Procedural Posture)
is editorial; rebuild text_content = frontmatter + body-from-that-
marker. Rows with editorial markers but NO court-start marker are
flagged for manual review, never blindly truncated. A kept body that
collapses (<50% length or <400 chars) is also flagged, not applied.

Snapshot before --apply; full prior text logged to changelog for
revert; dry-run default.

Usage:
  python -m ndcourts_mcp.strip_westlaw_headnotes
  python -m ndcourts_mcp.strip_westlaw_headnotes --apply
"""

from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path

from .db import DEFAULT_DB_PATH, get_connection, log_change, log_provenance
from .ingest_nwcite import _split_frontmatter
from .strip_westlaw_synopsis import strip_synopsis_editorial

BATCH = f"strip-westlaw-headnotes-{date.today().isoformat()}"

_STAR = re.compile(r"^\*\d+\s+")
_WH = re.compile(r"^(?:\*\d+\s+)?West Headnotes\b", re.IGNORECASE)
_PP = re.compile(r"^\s*Procedural Posture\(s\):.*$", re.IGNORECASE | re.MULTILINE)
_AUTHOR = re.compile(
    r"^[A-Z][A-Z.'’\- ]+,\s*(?:C\.\s*J|JJ|J|Judge|Justice|Chief\s+Justice"
    r"|District\s+Judge|Acting\s+C\.\s*J|Surrogate\s+Judge)\.")
_COURT_HDR = ("Syllabus by the Court", "Syllabus",
              "Attorneys and Law Firms", "Opinion",
              "On Petition for Rehearing", "On Rehearing", "On Reargument")


def _is_court_boundary(line: str) -> bool:
    s = _STAR.sub("", line.strip()).rstrip(".")
    return s in _COURT_HDR or bool(_AUTHOR.match(s)) or s == "PER CURIAM"


def _excise_headnotes(body: str) -> tuple[str, bool]:
    """Surgically remove the West Headnotes block(s): from a
    'West Headnotes (N)' line up to (but not including) the next
    court-authored boundary. Court Synopsis narrative (which precedes
    West Headnotes) is left untouched. Returns (new_body, changed)."""
    lines = body.splitlines(keepends=True)
    out, i, changed = [], 0, False
    while i < len(lines):
        if _WH.match(lines[i].strip()):
            changed = True
            j = i + 1
            while j < len(lines) and not _is_court_boundary(lines[j]):
                j += 1
            i = j                       # drop [WH header, court boundary)
            continue
        out.append(lines[i])
        i += 1
    return "".join(out), changed


def run(conn, apply: bool) -> dict:
    # Target ONLY the unambiguous editorial markers. "Synopsis" alone is
    # NOT a target — the project deliberately preserves court-authored
    # Synopsis narrative; its editorial stub is handled surgically by the
    # reused strip_synopsis_editorial.
    rows = conn.execute(
        "SELECT id, case_name, text_content FROM opinions "
        "WHERE source_reporter='westlaw' AND ("
        "text_content LIKE '%West Headnotes%' OR "
        "text_content LIKE '%Procedural Posture(s)%')"
    ).fetchall()
    st = {"scanned": len(rows), "stripped": 0, "unchanged": 0,
          "flagged_incomplete": 0}
    report = []
    for r in rows:
        oid, name, tc = r["id"], r["case_name"], r["text_content"]
        fm, body = _split_frontmatter(tc)
        nb, wh_changed = _excise_headnotes(body)
        nb, n_pp = _PP.subn("", nb)
        nb = re.sub(r"\n{3,}", "\n\n", nb).strip()
        # Reuse the existing, tested Synopsis-editorial stripper (keeps
        # court narrative, drops the editorial stub).
        nb, _, _ = strip_synopsis_editorial(nb)
        if not wh_changed and n_pp == 0:
            st["unchanged"] += 1
            continue
        # Post-condition: the result must carry NO residual editorial.
        if ("West Headnotes" in nb
                or re.search(r"Procedural Posture\(s\):", nb)):
            st["flagged_incomplete"] += 1
            report.append(f"FLAG_INCOMPLETE\t{oid}\t{name[:46]}\t"
                          f"residual editorial after strip")
            if apply:
                conn.execute("INSERT OR REPLACE INTO review_flags "
                             "(opinion_id, note) VALUES (?, ?)",
                             (oid, f"[{BATCH}] residual West Headnotes/"
                              f"Procedural Posture after strip — manual"))
            continue
        new_tc = (fm.rstrip() + "\n\n" + nb) if fm else nb
        st["stripped"] += 1
        report.append(f"STRIP\t{oid}\t{name[:42]}\t{len(tc)}->{len(new_tc)}"
                       f"\twh={wh_changed} pp={n_pp}")
        if apply:
            log_change(conn, BATCH, oid, "text_content", tc,
                       f"editorial-stripped (-{len(tc) - len(new_tc)}ch)",
                       authority="redistribution scope (NOTICE.md): "
                       "Westlaw West Headnotes / Procedural Posture are "
                       "editorial, not court-authored")
            conn.execute("UPDATE opinions SET text_content=? WHERE id=?",
                         (new_tc, oid))

    rpt = Path("triage") / f"{BATCH}.tsv"
    rpt.parent.mkdir(parents=True, exist_ok=True)
    rpt.write_text("kind\toid\tcase\tdetail\n" + "\n".join(report),
                   encoding="utf-8")
    if apply:
        log_provenance(
            conn, operation="strip_westlaw_headnotes",
            command="python -m ndcourts_mcp.strip_westlaw_headnotes --apply",
            rows_affected=st["stripped"],
            notes=(f"batch {BATCH}; corrective editorial strip "
                   f"(West Headnotes block + Procedural Posture lines, "
                   f"Synopsis stub via strip_synopsis_editorial): "
                   f"stripped={st['stripped']} unchanged={st['unchanged']} "
                   f"flagged_incomplete={st['flagged_incomplete']}; "
                   f"revert via cleanup revert {BATCH}"),
        )
        conn.commit()
    return st, rpt


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    conn = get_connection(args.db)
    try:
        st, rpt = run(conn, apply=args.apply)
    finally:
        conn.close()
    mode = "APPLIED" if args.apply else "DRY RUN"
    print(f"=== strip_westlaw_headnotes: {mode} (batch {BATCH}) ===")
    for k, v in st.items():
        print(f"  {k:<26} {v}")
    print(f"  report -> {rpt}")


if __name__ == "__main__":
    main()
