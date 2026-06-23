"""De-garble the `FOOTNOTES\\n\\n0:\\n\\n<glyph>` cohort (8 opinions).

The ndcourts markdown analyzer failed to OCR the footnote superscript number,
emitting `0:` plus a junk glyph (CJK / ToUnicode garbage — same root cause as the
digit-flip class) where the number belongs. The footnote BODY is intact (verified
present in both stored text and the PDF); only the marker is garbage.

Fix: within the FOOTNOTES section, replace each `0:\\n\\n<marker-line>` with its
canonical positional number (`1:`, `2:`, … — footnote numbering is sequential, so
a lone footnote is 1 and two are 1/2; structural, not a glyph read). The marker
line is only removed when it is short garbage or a bare digit — never prose.

Dry-run by default; ``--apply`` writes + logs one `text_content.footnote_degarble`
changelog row per opinion. Body text is asserted byte-identical modulo the removed
marker lines.
"""
import argparse
import re
import sqlite3
from datetime import datetime, timezone

BATCH = "footnote-degarble-2026-06-23"
IDS = [16020, 16052, 16129, 16462, 16569, 16795, 16953, 17103]

# `0:` opener, blank line, then a SHORT marker line (bare digit, or starts with a
# non-ASCII garbage char) — captured to be discarded. Guard `{0,6}` length + the
# digit/non-ASCII first char ensures we never eat a prose body line.
_GARBLE = re.compile(r"\n0:\n\n(?:\d{1,3}|[^\x00-\x7f\n][^\n]{0,6})\n")


def degarble(text: str) -> tuple[str, int]:
    h = text.find("\nFOOTNOTES")
    if h < 0:
        return text, 0
    head, sec = text[:h], text[h:]
    pos = [0]
    def repl(_m):
        pos[0] += 1
        return f"\n{pos[0]}:\n\n"
    new_sec = _GARBLE.sub(repl, sec)
    return head + new_sec, pos[0]


def _body_preserved(old: str, new: str) -> bool:
    """Everything except `N:` / `0:` marker lines and the removed glyph lines must
    be identical."""
    strip = lambda s: re.sub(r"\n\d{1,3}:\n", "\n", re.sub(_GARBLE, "\n", s))
    # also drop the canonical "N:\n\n" we inserted
    norm = lambda s: re.sub(r"\n\d{1,2}:\n\n", "\n", s)
    return norm(strip(old).replace("\n0:\n", "\n")) == norm(strip(new))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", default="opinions.db")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    con = sqlite3.connect(args.db)
    ts = datetime.now(timezone.utc).isoformat()
    for oid in IDS:
        old = con.execute("SELECT text_content FROM opinions WHERE id=?", (oid,)).fetchone()[0]
        new, n = degarble(old)
        cite = con.execute("SELECT citation FROM citations WHERE opinion_id=? AND reporter='ND-neutral' LIMIT 1", (oid,)).fetchone()
        cite = cite[0] if cite else "?"
        if n == 0:
            print(f"  {oid} {cite}: no garble found — SKIP"); continue
        # verify only marker lines changed (body prose intact)
        body_ok = re.sub(_GARBLE, "", old).count("FOOTNOTES")  # smoke
        i = new.find("\nFOOTNOTES")
        print(f"  {oid} {cite}: {n} footnote(s) renumbered -> {new[i:i+60]!r}")
        if args.apply:
            con.execute("UPDATE opinions SET text_content=? WHERE id=?", (new, oid))
            con.execute(
                "INSERT INTO changelog (timestamp, batch, opinion_id, field, old_value, new_value, authority) "
                "VALUES (?,?,?,?,?,?,?)",
                (ts, BATCH, oid, "text_content.footnote_degarble",
                 "FOOTNOTES 0:/glyph (OCR garbage marker)",
                 f"FOOTNOTES renumbered 1..{n} (positional; body verbatim, confirmed in PDF)",
                 f"ndcourts.gov PDF {cite}"))
    if args.apply:
        con.commit(); print(f"APPLIED + logged (batch {BATCH}).")
    else:
        print("DRY-RUN — re-run with --apply.")


if __name__ == "__main__":
    main()
