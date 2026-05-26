"""READ-ONLY verification of the 15 native-neutral-cite collision pairs.

For each pair print: keep/drop (keep = markdown/ND-sourced, earlier date),
docket match, text jaccard, lengths, and any rehearing/amended/withdrawn
markers in either text. A pure CL double-ingest = same docket + high jaccard
+ no distinguishing rehearing/amended text on the later row -> MERGE.
A real rehearing/amended/supplemental publication -> KEEP BOTH (flagged).
"""
from __future__ import annotations

from ndcourts_mcp.db import get_connection
from ndcourts_mcp.multisource_diff import jaccard, normalize_words, shingles

PAIRS = [
    ("1997 ND 11", 12365, 12366), ("1997 ND 9", 12353, 12354),
    ("1999 ND 2", 12808, 12809), ("2000 ND 203", 13290, 13291),
    ("2001 ND 10", 13303, 13304), ("2001 ND 7", 13299, 13300),
    ("2002 ND 6", 13499, 13500), ("2002 ND 9", 13497, 13498),
    ("2003 ND 11", 13714, 13715), ("2004 ND 13", 13938, 13939),
    ("2004 ND 8", 13931, 13932), ("2006 ND 2", 14391, 14392),
    ("2007 ND 9", 14685, 14686), ("2008 ND 9", 14888, 14889),
    ("2010 ND 9", 15325, 15326),
]

MARKERS = ("ehearing", "mended", "ithdrawn", "upersed", "upplement")


def info(conn, oid):
    r = conn.execute(
        "SELECT date_filed, docket_number, source_reporter, source_path, "
        "text_content, disposition FROM opinions WHERE id=?", (oid,)).fetchone()
    return r


def markers(txt):
    t = txt or ""
    return ",".join(m for m in MARKERS if m in t) or "-"


def main():
    conn = get_connection()
    print(f"{'cite':<12}{'keep':>6}{'drop':>6}  {'dockmatch':<9}"
          f"{'jac':>6}  {'klen':>7}{'dlen':>7}  keep_mark / drop_mark")
    for cite, a, b in PAIRS:
        ra, rb = info(conn, a), info(conn, b)
        # keep = ND/markdown source if identifiable, else earlier date
        a_md = (ra["source_reporter"] == "ND") or ("markdown" in (ra["source_path"] or ""))
        b_md = (rb["source_reporter"] == "ND") or ("markdown" in (rb["source_path"] or ""))
        if a_md and not b_md:
            keep, drop, rk, rd = a, b, ra, rb
        elif b_md and not a_md:
            keep, drop, rk, rd = b, a, rb, ra
        else:
            # both or neither markdown: keep earlier date
            if ra["date_filed"] <= rb["date_filed"]:
                keep, drop, rk, rd = a, b, ra, rb
            else:
                keep, drop, rk, rd = b, a, rb, ra
        j = jaccard(shingles(normalize_words(rk["text_content"] or "")),
                    shingles(normalize_words(rd["text_content"] or "")))
        dock = "SAME" if (rk["docket_number"] or "X") == (rd["docket_number"] or "Y") else \
               f'{rk["docket_number"]}|{rd["docket_number"]}'
        print(f"{cite:<12}{keep:>6}{drop:>6}  {dock:<9}{j:>6.2f}  "
              f'{len(rk["text_content"] or ""):>7}{len(rd["text_content"] or ""):>7}  '
              f"{markers(rk['text_content'])} / {markers(rd['text_content'])}")
        print(f"             keep {rk['date_filed']} {rk['source_reporter']:<9} "
              f"| drop {rd['date_filed']} {rd['source_reporter']}")
    conn.close()


if __name__ == "__main__":
    main()
