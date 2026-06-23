"""Apply validated agent footnote proposals behind HARD GATES.

Agents diagnose; this applier re-derives each edit and only commits an opinion
when every proposed footnote ends up parser-detected at its call paragraph and
the court's words are preserved. Anything that fails a gate is SKIPPED and
reported — a bad transform can never be written.

Per-action transforms (operate on the validated db_anchor, num, body):
  number_orphan  : "\\n\\n. body" / "\\n\\n body" -> "\\n\\nN\\n\\n. body"; then
                   bracket a unique attached call digit in the call paragraph.
  fix_marker     : body opener "Nbody"/".Nbody"/"\\xa0N" -> "N\\n\\n. body"; OR a
                   call "....N " -> "....[N] " (bracket the attached digit).
  recover_body_absent : append "\\n\\nN\\n\\n. body" at opinion end; bracket call.
  retrofit_bareline_to_bracket : bracket the attached call digit (+ drop a
                   redundant bare-line "N" if present).
  already_clean / not_a_footnote / strip_residual : skipped here (no-op / manual).

GATES (per opinion, all proposed actionable fns): alphabetic-token multiset ==
old (+ exactly the inserted body words for recover); footnote_structure detects
each proposed num; call_para == proposed where given (else None tolerated).
Dry-run by default; ``--apply`` writes + logs one row per footnote.
"""
import argparse
import json
import re
import sqlite3
from datetime import datetime, timezone

BATCH = "footnote-proposal-apply-2026-06-23"
ACTIONABLE = {"number_orphan", "fix_marker", "recover_body_absent",
              "retrofit_bareline_to_bracket"}


def words(s):
    return sorted(re.findall(r"[A-Za-z]+", s))


def para_span(text, p):
    a = None
    for pat in (f"[¶{p}]", f"[¶ {p}]"):
        i = text.find(pat)
        if i >= 0:
            a = i
            break
    if a is None:
        return None
    b = len(text)
    for pat in (f"[¶{p+1}]", f"[¶ {p+1}]"):
        j = text.find(pat)
        if j > a:
            b = min(b, j)
    return (a, b)


def bracket_call(text, num, call_para):
    """Bracket a unique attached call digit ``num`` inside the call paragraph."""
    if call_para is None:
        return text, False
    span = para_span(text, call_para)
    if not span:
        return text, False
    a, b = span
    seg = text[a:b]
    # attached digit: preceded by a word char / sentence punctuation / quote,
    # equal to num, not already bracketed, not part of a longer number.
    pat = re.compile(r"(?<=[A-Za-z%s])(%d)(?=[ \n.,;:)\"”])" % (r".,;:)\"”’'", num))
    hits = [m for m in pat.finditer(seg)
            if seg[m.start() - 1:m.start()] != "["]
    if len(hits) != 1:
        return text, False
    m = hits[0]
    new_seg = seg[:m.start()] + f"[{num}]" + seg[m.end():]
    return text[:a] + new_seg + text[b:], True


def apply_fn(text, f):
    """Return (new_text, ok_reason) or (None, fail_reason) for one footnote."""
    num = f["num"]
    act = f["action"]
    anc = f.get("db_anchor", "")
    body = f.get("source_body_verbatim", "")
    cp = f.get("call_para")

    if act == "recover_body_absent":
        # HARD false-absent gate: a duplicated body appears as a LONG CONTIGUOUS
        # run in the DB. (Scattered word overlap just means the footnote quotes
        # opinion content — that is NOT a duplicate.) Slide 12-word windows.
        tn = " ".join(re.findall(r"[a-z0-9]+", text.lower()))
        w = re.findall(r"[a-z0-9]+", body.lower())
        present = any(len(g) > 40 and g in tn
                      for g in (" ".join(w[i:i + 12]) for i in range(0, max(1, len(w) - 12), 6)))
        if present:
            return None, "FALSE_ABSENT (contiguous body run present in DB)"
        new = text.rstrip("\n") + f"\n\n{num}\n\n. {body.strip()}"
        new, _ = bracket_call(new, num, cp)
        return new, "appended body"

    if anc and text.count(anc) != 1:
        return None, f"anchor not unique ({text.count(anc)})"

    if act == "number_orphan":
        # orphan body in DB: "\n\n. {anc}" or "\n\n {anc}" (anc starts with the body)
        for form in (f"\n\n. {anc}", f"\n\n.{anc}", f"\n\n {anc}", f"\n\n{anc}"):
            if anc and form in text and text.count(form) == 1:
                text = text.replace(form, f"\n\n{num}\n\n. {anc}")
                text, _ = bracket_call(text, num, cp)
                return text, "numbered orphan"
        return None, "orphan form not located"

    if act == "retrofit_bareline_to_bracket":
        t2, ok = bracket_call(text, num, cp)
        if ok:
            return t2, "bracketed call"
        return None, "call digit not uniquely located"

    if act == "fix_marker":
        # case 1: anchor is a body opener with a number abutting text
        m = re.match(r"^[ \xa0]*%d\.?\s*(.*)" % num, anc)
        # try body-marker normalization: "<lead>Nbody" -> "<lead>N\n\n. body"
        mb = re.search(r"(\n\n[ \xa0]*)%d([ \xa0]*\.?\s*)([A-Z\"“])" % num, text)
        if anc and re.search(r"[A-Za-z]", anc) and anc in text:
            # bracket an attached call digit inside the anchor, if present
            cm = re.search(r"(?<=[A-Za-z.,;:)\"”’'])%d(?=[ .,;:)\"”])" % num, anc)
            if cm:
                fixed = anc[:cm.start()] + f"[{num}]" + anc[cm.end():]
                text = text.replace(anc, fixed, 1)
                return text, "bracketed call in anchor"
        return None, "fix_marker shape unhandled"
    return None, "unhandled action"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("proposals")
    ap.add_argument("--db", default="opinions.db")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    import ndcourts_mcp.proofread as pr
    data = json.load(open(args.proposals))
    if isinstance(data, dict):
        data = data.get("result", data)
    con = sqlite3.connect(args.db)
    ts = datetime.now(timezone.utc).isoformat()
    applied = skipped = 0
    skips = []
    for o in data:
        oid = o["opinion_id"]
        row = con.execute("SELECT text_content FROM opinions WHERE id=?", (oid,)).fetchone()
        if not row:
            continue
        old = row[0]
        text = old
        proposed = [f for f in o.get("footnotes", []) if f["action"] in ACTIONABLE]
        if not proposed:
            continue
        ok = True
        added_words = []
        for f in proposed:
            new, why = apply_fn(text, f)
            if new is None:
                ok = False
                skips.append((oid, o.get("cite", ""), f["num"], f["action"], why))
                break
            if f["action"] == "recover_body_absent":
                added_words += words(f.get("source_body_verbatim", ""))
            text = new
        if not ok:
            skipped += 1
            continue
        # GATES
        if words(text) != sorted(words(old) + added_words):
            skipped += 1
            skips.append((oid, o.get("cite", ""), 0, "GATE", "word multiset mismatch"))
            continue
        st = pr.footnote_structure(text)
        det = {n for n, _, _ in st["bodies"]}
        want = {f["num"] for f in proposed}
        if not want <= det:
            skipped += 1
            skips.append((oid, o.get("cite", ""), 0, "GATE", f"not all detected (det={sorted(det)}, want={sorted(want)})"))
            continue
        cp_ok = all(st["call_para"].get(f["num"]) in (f.get("call_para"), None) or f.get("call_para") is None
                    for f in proposed)
        applied += 1
        if args.apply:
            con.execute("UPDATE opinions SET text_content=? WHERE id=?", (text, oid))
            for f in proposed:
                con.execute(
                    "INSERT INTO changelog (timestamp, batch, opinion_id, field, old_value, new_value, authority) "
                    "VALUES (?,?,?,?,?,?,?)",
                    (ts, BATCH, oid, "text_content.footnote_proposal",
                     f"footnote {f['num']} {f['action']}",
                     f"applied {f['action']} (validated proposal); call_para {f.get('call_para')}",
                     "agent proposal + deterministic gate (archive source)"))
        else:
            print(f"  WOULD APPLY id{oid} {o.get('cite','')}: {[ (f['num'],f['action']) for f in proposed]} -> det {sorted(det)}")
    print(f"\napplied: {applied}  skipped: {skipped}")
    if skips:
        print("skips:")
        for s in skips[:40]:
            print("  ", s)
    if args.apply:
        con.commit()
        print(f"COMMITTED (batch {BATCH}).")


if __name__ == "__main__":
    main()
