#!/usr/bin/env python3
"""Apply per-item adjudicated Synopsis dispositions (the 81 short factual/ambiguous blocks).

Two actions, both gated by the same structural invariants as strip_west_synopsis_v2.py:

  "full"  — the whole West editorial block is removed (Synopsis label -> first court
            element, which is preserved). For dispositions, separate-opinion notices,
            West procedural-posture synopses, holding summaries. The removed span must
            contain NO court element and the syllabus-variant / star-page / 'Attorneys'
            counts must be byte-identical before/after.

  "label" — only the orphan 'Synopsis' label line is removed; all following text (the
            court-voice factual record or counsel appearances) is preserved. The removed
            span must equal exactly the label + trailing whitespace.

Decisions file: {"full":[ids...], "label":[ids...], "defer":[ids...]}.
Dry-run by default. Usage:
  strip_synopsis_adjudicated.py DECISIONS.json [--apply] [--batch NAME] [--db opinions.db]
"""
import sqlite3, re, json, sys, datetime

SYLL = re.compile(r'S[uy]l+[ai]bus', re.I)
STAR = re.compile(r'\*+\s?\d')
MARK = ["Attorneys and Law Firms", "Opinion\n"]


def boundary(t):
    i = t.find("Synopsis")
    if i < 0:
        return None
    cand = [t.find(m, i + 8) for m in MARK]
    cand = [e for e in cand if e > 0]
    ms = SYLL.search(t, i + 8)
    if ms:
        cand.append(ms.start())
    st = STAR.search(t, i + 8)
    if st:
        cand.append(st.start())
    if not cand:
        return None
    return i, min(cand)


def counts(t):
    return (len(SYLL.findall(t)), len(STAR.findall(t)), t.count("Attorneys and Law Firms"))


def plan_full(t):
    b = boundary(t)
    if b is None:
        return None, "no-boundary"
    i, e = b
    removed = t[i:e]
    if SYLL.search(removed) or STAR.search(removed) or "Attorneys and Law Firms" in removed \
            or "Opinion\n" in removed:
        return None, "court-element-in-removed"
    new = t[:i] + t[e:]
    if counts(t) != counts(new):
        return None, "element-count-changed"
    return (new, removed), None


def plan_label(t):
    i = t.find("Synopsis")
    if i < 0:
        return None, "no-label"
    # body starts at first non-whitespace after the label token
    j = i + len("Synopsis")
    k = j
    while k < len(t) and (t[k].isspace() or t[k] == '\xa0'):
        k += 1
    removed = t[i:k]
    # removed must be ONLY the label + surrounding whitespace
    if removed.replace('\xa0', ' ').strip() != "Synopsis":
        return None, "label-not-isolated"
    # junction safety: text before label must end clean (newline/space) or be at start
    if i != 0 and not (t[i - 1] == '\n' or t[i - 1] == ' ' or t[i - 1] == '\xa0'):
        return None, "junction-mash"
    new = t[:i] + t[k:]
    if counts(t) != counts(new):
        return None, "element-count-changed"
    return (new, removed), None


def main():
    path = sys.argv[1]
    apply = "--apply" in sys.argv
    batch = sys.argv[sys.argv.index("--batch") + 1] if "--batch" in sys.argv else "synopsis-adjudicated"
    db = sys.argv[sys.argv.index("--db") + 1] if "--db" in sys.argv else "opinions.db"
    dec = json.load(open(path))
    con = sqlite3.connect(db)
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    applied = 0
    skip = {}
    for action, ids in (("full", dec.get("full", [])), ("label", dec.get("label", []))):
        for oid in ids:
            row = con.execute("SELECT text_content FROM opinions WHERE id=?", (oid,)).fetchone()
            if not row:
                skip["not-found"] = skip.get("not-found", 0) + 1
                continue
            old = row[0]
            res, reason = (plan_full if action == "full" else plan_label)(old)
            if res is None:
                skip[f"{action}:{reason}"] = skip.get(f"{action}:{reason}", 0) + 1
                print(f"  SKIP id{oid} [{action}]: {reason}")
                continue
            new, removed = res
            applied += 1
            if apply:
                con.execute("UPDATE opinions SET text_content=? WHERE id=?", (new, oid))
                note = ("West editorial Synopsis block (adjudicated full strip; court element "
                        "preserved, element-count-gated)" if action == "full"
                        else "West 'Synopsis' section label removed (adjudicated label-only; "
                             "court-voice factual record / counsel appearances preserved)")
                con.execute(
                    "INSERT INTO changelog (timestamp, batch, opinion_id, field, old_value, new_value, authority) "
                    "VALUES (?,?,?,?,?,?,?)",
                    (ts, batch, oid, f"text_content.synopsis_{action}",
                     removed[:200], "", note + "; conf=high"))
            else:
                print(f"  OK id{oid} [{action}] -{len(removed)}c: {removed.replace(chr(10),'/')[:90]!r}")
    if apply:
        con.commit()
    print(f"\napplied: {applied}  skipped: {skip}  ({'APPLIED' if apply else 'dry-run'})")


if __name__ == "__main__":
    main()
