"""Deterministic gate between agent proposals and apply. Vets each proposed
footnote repair against the live DB text so agent errors (esp. a body claimed
absent that is actually present-but-malformed -> would duplicate) are caught
before any write. Read-only; prints a per-proposal verdict + summary.

Verdicts:
  OK            - safe to apply (anchor unique / body genuinely absent)
  FALSE_ABSENT  - recover_body_absent but the body is already in the DB (REJECT)
  BAD_ANCHOR    - db_anchor missing or not unique (REJECT, needs re-locate)
  REVIEW        - low-stakes / informational (already_clean, not_a_footnote)
"""
import json
import re
import sqlite3
import sys


def norm(s):
    return re.sub(r"\s+", " ", s).strip().lower()


def first_words(s, n=10):
    w = re.findall(r"[A-Za-z0-9]+", s)
    return " ".join(w[:n]).lower()


def main():
    proposals_file = sys.argv[1]
    db = sys.argv[2] if len(sys.argv) > 2 else "opinions.db"
    data = json.load(open(proposals_file))
    if isinstance(data, dict):
        data = data.get("result", data)
    con = sqlite3.connect(db)
    from collections import Counter
    verd = Counter()
    flagged = []
    for o in data:
        oid = o["opinion_id"]
        t = con.execute("SELECT text_content FROM opinions WHERE id=?", (oid,)).fetchone()
        if not t:
            continue
        t = t[0]
        tnorm = norm(t)
        twords = set(re.findall(r"[a-z0-9]+", tnorm))
        for f in o.get("footnotes", []):
            act = f["action"]
            v = "OK"
            detail = ""
            if act in ("already_clean", "not_a_footnote"):
                v = "REVIEW"
            elif act == "recover_body_absent":
                body = f.get("source_body_verbatim", "")
                fw = first_words(body, 10)
                # is the body's opening already present in the DB?
                if fw and fw in tnorm:
                    v = "FALSE_ABSENT"; detail = f"body opening present in DB: {fw[:50]!r}"
                else:
                    # also try a distinctive 6-gram from mid-body
                    w = re.findall(r"[A-Za-z0-9]+", body)
                    mid = " ".join(w[len(w)//2:len(w)//2 + 8]).lower()
                    if mid and mid in tnorm:
                        v = "FALSE_ABSENT"; detail = f"body midsection present: {mid[:50]!r}"
            else:  # fix_marker, number_orphan, strip_residual, retrofit_bareline_to_bracket
                anc = f.get("db_anchor", "")
                if not anc:
                    v = "BAD_ANCHOR"; detail = "empty anchor"
                else:
                    c = t.count(anc)
                    if c == 0:
                        v = "BAD_ANCHOR"; detail = "anchor not found"
                    elif c > 1:
                        v = "BAD_ANCHOR"; detail = f"anchor not unique (x{c})"
            verd[v] += 1
            if v not in ("OK", "REVIEW"):
                flagged.append((oid, o.get("cite", ""), f["num"], act, v, detail))
    print("verdicts:", dict(verd))
    print("\nflagged (must fix before apply):")
    for oid, cite, num, act, v, detail in flagged:
        print(f"  id{oid} {cite} fn{num} {act}: {v} — {detail}")


if __name__ == "__main__":
    main()
