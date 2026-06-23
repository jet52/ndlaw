"""Phase 1: strip residual West key-number material from westlaw/nw-lineage
opinions so the bracketed `[N]` markers stop colliding with footnote call `[N]`.

Two sub-cases (see corpus analysis):
  (a) marker-only: `[1] [2]` runs at a line/paragraph start, embedded before the
      OPINION's own prose or before `[¶N]`. -> strip just the bracket tokens.
  (b) headnote-text: `[N]` followed by a West topic line (e.g. "Municipal,
      County, and Local Government - Bona fide purchasers"). -> needs the whole
      line removed; FLAGGED here for review, not auto-stripped.

Inline `[N]` after a word/punctuation (`district court[1]`) are footnote calls /
references and are LEFT ALONE.

Scope: only opinions in the WEST_HEADNOTE triage bucket. Dry-run by default
(prints stats + samples + case-(b) flags). ``--apply`` strips case-(a) markers
only and logs one ``text_content.west_keynote_strip`` row per opinion; case-(b)
opinions are skipped and listed for agent review.
"""
import argparse
import re
import sqlite3
from datetime import datetime, timezone

BATCH = "west-keynote-strip-2026-06-23"
TRIAGE = "triage/footnote-corpus-triage-2026-06-23.tsv"

# A line-start run of one-or-more [N] key-number brackets (digits only), with
# optional leading/intervening whitespace/nbsp. [¶ N] is NOT matched (¶ != digit).
RUN = re.compile(r"(?m)^([ \t\xa0]*)((?:\[\d{1,3}\][ \t\xa0]*)+)")
# topic-line signature: a SHORT West "Topic - Subtopic" head (the " - " dash is the
# reliable West key-number-topic separator; opinion prose / court syllabus does not
# use it that way). Kept conservative so prose runs fall through to case-(a).
TOPIC = re.compile(r"^[A-Z][A-Za-z.,&'’() ]{2,45} - [A-Z][A-Za-z]")


def west_ids():
    ids = []
    for ln in open(TRIAGE):
        p = ln.split("\t")
        if len(p) > 3 and p[3] == "WEST_HEADNOTE":
            ids.append(int(p[0]))
    return ids


def analyze(text):
    """Return (case_a_runs, case_b_flags). Each run = (start, end, remainder_head)."""
    a, b = [], []
    for m in RUN.finditer(text):
        rest = text[m.end():m.end() + 70]
        # keep [¶..] safe: if the remainder begins with a paragraph marker it's a
        # pure marker run before opinion prose -> case (a).
        head = rest.lstrip()
        if TOPIC.match(head):
            b.append((m.start(), m.end(), head[:60]))
        else:
            a.append((m.start(), m.end(), head[:40]))
    return a, b


def strip_markers(text):
    # remove case-(a) bracket runs (only the [N] tokens + their spaces), keep rest
    out = []
    last = 0
    for m in RUN.finditer(text):
        head = text[m.end():m.end() + 70].lstrip()
        if TOPIC.match(head):
            continue  # leave case-(b) for review
        out.append(text[last:m.start()])
        out.append(m.group(1))  # preserve original leading whitespace
        last = m.end()
    out.append(text[last:])
    return "".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", default="opinions.db")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    con = sqlite3.connect(args.db)
    ts = datetime.now(timezone.utc).isoformat()
    ids = west_ids()
    n_strip = n_caseb = total_markers = 0
    caseb_ids = []
    samples = []
    for oid in ids:
        row = con.execute("SELECT text_content FROM opinions WHERE id=?", (oid,)).fetchone()
        if not row:
            continue
        t = row[0]
        a, b = analyze(t)
        if b:
            n_caseb += 1
            caseb_ids.append(oid)
        if not a:
            continue
        new = strip_markers(t)
        removed = len(re.findall(r"\[\d{1,3}\]", t)) - len(re.findall(r"\[\d{1,3}\]", new))
        total_markers += removed
        n_strip += 1
        if len(samples) < 10 and removed:
            mk = a[0]
            samples.append(f"  id{oid}: {t[mk[0]:mk[1]]!r} -> kept head {mk[2]!r}")
        if args.apply and new != t:
            con.execute("UPDATE opinions SET text_content=? WHERE id=?", (new, oid))
            con.execute(
                "INSERT INTO changelog (timestamp, batch, opinion_id, field, old_value, new_value, authority) "
                "VALUES (?,?,?,?,?,?,?)",
                (ts, BATCH, oid, "text_content.west_keynote_strip",
                 f"{removed} West key-number [N] marker(s) (case-a, line-start runs)",
                 "stripped key-number markers; opinion prose retained",
                 "West key-number apparatus (not court text)"))
    print(f"case-(a) opinions to strip: {n_strip}  | markers removed: {total_markers}")
    print(f"case-(b) opinions (headnote TEXT — flagged for review, NOT stripped): {n_caseb}")
    print("samples:")
    print("\n".join(samples))
    if args.apply:
        con.commit()
        print(f"APPLIED case-(a) (batch {BATCH}); case-(b) ids → triage/west-caseb-review.txt")
        open("triage/west-caseb-review.txt", "w").write("\n".join(map(str, caseb_ids)))
    else:
        print("DRY-RUN — re-run with --apply. case-(b) sample ids:", caseb_ids[:10])


if __name__ == "__main__":
    main()
