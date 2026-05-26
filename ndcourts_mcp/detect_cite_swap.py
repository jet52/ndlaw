"""Adjacent-cite content-swap detector.

Catches the recurring failure where an opinion row's stored text belongs to a
DIFFERENT neutral cite than the row's DB citation — a scraper/analyzer mis-save
(wrong PDF/markdown content under a neutral-cite filename). Known instances:
Goetz 2023 ND 53/120, Interest of A.C. 2022 ND 123/169, Logan/Gehring
2000 ND 203/199, and a systematic 1997 mislabel batch surfaced by this tool.

This is the most direct threat to the authoritative-text goal: an undetected
swap means a *wrong opinion body under a correct citation*. The detector is
READ-ONLY — it flags for human review; fixing requires per-case adjudication
(relabel vs. merge-with-existing vs. re-ingest a missing real opinion).

Two independent signals, scanning only native-neutral (1997+) opinions:

  CITE   — the DB neutral cite is ABSENT from the opinion's header window while
           some other `YYYY ND n` IS present. High precision: the self-cite
           normally sits in the court header ("North Dakota Supreme Court\n
           <cites>" or "IN THE SUPREME COURT / STATE OF NORTH DAKOTA\n<cite>"),
           so its absence + a different cite present = the body is another case.
           (Tolerates the no-space "2018 ND238" rendering.)

  DOCKET  — an 8-digit docket (20XXXXXX) appears in the header window and the DB
           docket_number's 8-digit core is NOT among them. Catches leaks where
           the analyzer header cite was correct but the body text leaked
           (e.g. Logan). NOISIER: consolidated/companion dockets produce false
           positives, so DOCKET flags are advisory — verify before acting.

Usage:  python -m ndcourts_mcp.detect_cite_swap [--window N] [--report PATH]
"""
from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path

from .db import DEFAULT_DB_PATH, get_connection

_NEUTRAL = re.compile(r"(\d{4})\s+ND\s*(\d+)")   # tolerates "2018 ND238"
_DOCKET8 = re.compile(r"\b(20\d{6})\b")
DEFAULT_WINDOW = 1200
_FETCH = 6000                                    # frontmatter + window headroom


def _neutral_cites(s: str) -> list[str]:
    return [f"{y} ND {n}" for (y, n) in _NEUTRAL.findall(s)]


def _norm_cite(c: str | None) -> str:
    m = _NEUTRAL.search(c or "")
    return f"{m.group(1)} ND {m.group(2)}" if m else ""


def _body(text: str) -> str:
    """Strip a leading YAML frontmatter block so the analyzer's metadata
    `citations:` list is not mistaken for the opinion's own header cite."""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:]
    return text


def scan(conn, window: int = DEFAULT_WINDOW):
    rows = conn.execute(
        "SELECT o.id, o.date_filed, o.docket_number, o.source_path, "
        "       o.case_name, substr(o.text_content, 1, ?) AS head, "
        "       (SELECT citation FROM citations WHERE opinion_id=o.id "
        "        AND reporter='ND-neutral' LIMIT 1) AS cite "
        "FROM opinions o "
        "WHERE EXISTS(SELECT 1 FROM citations WHERE opinion_id=o.id "
        "             AND reporter='ND-neutral')",
        (_FETCH,)).fetchall()

    scanned = no_header_cite = 0
    cite_flags, docket_flags = [], []
    for r in rows:
        cite = _norm_cite(r["cite"])
        if not cite:
            continue
        scanned += 1
        win = _body(r["head"] or "")[:window]

        cites = _neutral_cites(win)
        if cites and cite not in cites:
            cite_flags.append((r["id"], cite, cites[0], r["date_filed"],
                               r["source_path"], r["case_name"]))
        elif not cites:
            no_header_cite += 1

        db_dock = _DOCKET8.search(r["docket_number"] or "")
        body_docks = _DOCKET8.findall(win)
        if db_dock and body_docks and db_dock.group(1) not in body_docks:
            docket_flags.append((r["id"], cite, db_dock.group(1),
                                 body_docks[0], r["source_path"], r["case_name"]))

    return {"scanned": scanned, "no_header_cite": no_header_cite,
            "cite": cite_flags, "docket": docket_flags}


def scan_bodydup(conn, window: int = DEFAULT_WINDOW):
    """Detect the content-claims-wrong-cite class (the Albertson/Bohe pattern,
    invisible to the CITE check because the row's label MATCHES its wrong body).

    Group native-neutral (1997+) opinions by their body header self-cite; any
    `YYYY ND n` claimed as the self-cite by 2+ distinct opinions means at least
    one has the wrong neutral cite baked into its stored text. Returns
    {body_cite: [(oid, label_cite, case_name), ...]} for collisions."""
    from collections import defaultdict
    rows = conn.execute(
        "SELECT o.id, o.case_name, substr(o.text_content,1,?) head, "
        "(SELECT citation FROM citations WHERE opinion_id=o.id AND reporter='ND-neutral' LIMIT 1) cite "
        "FROM opinions o WHERE EXISTS(SELECT 1 FROM citations WHERE opinion_id=o.id "
        "AND reporter='ND-neutral')", (_FETCH,)).fetchall()
    by_body = defaultdict(list)
    for r in rows:
        cites = _neutral_cites(_body(r["head"] or "")[:window])
        if cites:
            by_body[cites[0]].append((r["id"], _norm_cite(r["cite"]), r["case_name"]))
    return {bc: lst for bc, lst in by_body.items() if len(lst) > 1}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    ap.add_argument("--window", type=int, default=DEFAULT_WINDOW)
    ap.add_argument("--report", type=Path,
                    default=Path("triage") / f"cite-swap-scan-{date.today().isoformat()}.tsv")
    args = ap.parse_args()

    conn = get_connection(args.db)
    res = scan(conn, args.window)
    bodydup = scan_bodydup(conn, args.window)
    conn.close()

    lines = ["signal\toid\tdb_cite\tbody_cite_or_docket\tdate_filed\tcase_name\tsource_path"]
    for oid, cite, body_cite, dt, src, cn in sorted(res["cite"], key=lambda x: x[1]):
        lines.append(f"CITE\t{oid}\t{cite}\t{body_cite}\t{dt}\t{cn}\t{src}")
    for oid, cite, db_dock, body_dock, src, cn in sorted(res["docket"], key=lambda x: x[1]):
        lines.append(f"DOCKET\t{oid}\t{cite}\t{db_dock}->{body_dock}\t\t{cn}\t{src}")
    for bc in sorted(bodydup):
        for oid, label, cn in bodydup[bc]:
            lines.append(f"BODYDUP\t{oid}\t{label}\t{bc}\t\t{cn}\t")
    args.report.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("=== adjacent-cite content-swap scan ===")
    print(f"  scanned native-neutral (1997+) opinions: {res['scanned']}")
    print(f"  no neutral cite in header window:        {res['no_header_cite']}")
    print(f"  CITE flags (likely mislabel/swap):       {len(res['cite'])}")
    print(f"  DOCKET flags (advisory; consolidated FP): {len(res['docket'])}")
    print(f"  BODYDUP collisions (content claims a cite 2+ rows claim): "
          f"{len(bodydup)} cites / {sum(len(v) for v in bodydup.values())} rows")
    print(f"  report -> {args.report}")


if __name__ == "__main__":
    main()
