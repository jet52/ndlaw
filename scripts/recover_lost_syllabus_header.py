#!/usr/bin/env python3
"""Restore the dropped 'Syllabus by the Court' header + leading point(s) for 20 opinions.

These West-doc opinions have text_content beginning `Synopsis\n2.` (or `\n3.`/`\n4.`): the
ingest parse dropped the `*NNN Syllabus by the Court` header and the leading court syllabus
point(s), and left a stray West `Synopsis` label. The surviving points and the opinion body
are intact and correct. The full syllabus is in the authoritative West .doc.

Fix (minimal, body-preserving): replace the leading `Synopsis\n` with the West .doc's
`*NNN Syllabus by the Court` header + the missing point(s) 1..(first_db_point-1). Everything
from the first surviving DB point onward is left byte-identical.

Safety: the West .doc's point `first_db_point` must align with the DB's first surviving point
(prefix match) — otherwise the syllabi disagree and the opinion is SKIPPED for manual review.

Dry-run by default. Usage: recover_lost_syllabus_header.py [--apply]
"""
import sqlite3, re, subprocess, sys, datetime

REFS = "/Users/jerod/refs/nd/opin"
BATCH = "recover-lost-syllabus-header-2026-06-25"
IDS = [6418, 6420, 6424, 6427, 6439, 6441, 6450, 6458, 6471, 7249,
       7459, 7503, 13150, 13266, 13532, 13618, 13633, 13781, 13875, 14029]


def doc_text(sp):
    return subprocess.run(["textutil", "-convert", "txt", "-stdout", f"{REFS}/{sp}"],
                          capture_output=True, text=True).stdout


def _norm(s):
    # ingest normalization for these West docs: curly quotes -> straight (em/en-dash, nbsp,
    # section sign are preserved verbatim, matching the DB body)
    return (s.replace('‘', "'").replace('’', "'")
             .replace('“', '"').replace('”', '"'))


def doc_syllabus_points(dx):
    """(star, {point_number: text}) — the '*NNN' star-page and points from the .doc syllabus."""
    sm = re.search(r'(\*\d+)\s+Syllabus by the Court', dx)
    if not sm:
        return None, {}
    star = sm.group(1)
    region = dx[sm.end():]
    # syllabus runs until the author byline / Attorneys / opinion start
    stop = re.search(r'\n([A-Z][A-Z .]+,?\s+(?:J\.|JJ\.|C\. ?J\.|Judge|Justice|Acting)|'
                     r'Attorneys and Law Firms|PER CURIAM|OPINION)', region)
    if stop:
        region = region[:stop.start()]
    pts = {}
    for m in re.finditer(r'(?:^|\n)\s*(\d+)\.\s+(.*?)(?=\n\s*\d+\.\s|\Z)', region, re.S):
        pts[int(m.group(1))] = re.sub(r'\s*\n\s*', ' ', m.group(2)).strip()
    return star, pts


def main():
    apply = "--apply" in sys.argv
    con = sqlite3.connect("opinions.db")
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    if apply:
        con.execute("DELETE FROM changelog WHERE batch=?", (BATCH,))
    ok = skip = 0
    for oid in IDS:
        sp, t = con.execute("SELECT source_path, text_content FROM opinions WHERE id=?", (oid,)).fetchone()
        m = re.match(r'Synopsis\n(\d+)\.', t)
        if not m:
            print(f"  SKIP id{oid}: no 'Synopsis\\nN.' head"); skip += 1; continue
        first = int(m.group(1))
        star, pts = doc_syllabus_points(doc_text(sp))
        if not star or any(n not in pts for n in range(1, first + 1)):
            print(f"  SKIP id{oid}: doc syllabus incomplete (need 1..{first}, have {sorted(pts)[:6]})"); skip += 1; continue
        # alignment: doc point `first` must match the DB's first surviving point (quote-normalized)
        db_first_text = t[len("Synopsis\n"):].split("\n", 1)[0]
        db_first_body = db_first_text.split(".", 1)[1].strip()[:30]
        if not _norm(pts[first]).startswith(_norm(db_first_body)):
            print(f"  SKIP id{oid}: point {first} mismatch\n     doc:{_norm(pts[first])[:60]!r}\n     db :{_norm(db_first_body)!r}"); skip += 1; continue
        header = f"{star} Syllabus by the Court."
        prefix = "\n\xa0\n".join(f"{n}. {_norm(pts[n])}" for n in range(1, first))
        new = f"{header}\n{prefix}\n\xa0\n" + t[len("Synopsis\n"):]
        # body invariant: everything from the first surviving point on is unchanged
        assert new.endswith(t[len("Synopsis\n"):])
        ok += 1
        print(f"\n  OK id{oid}: +{header!r} +pts 1..{first-1}  (+{len(new)-len(t)}c)")
        for n in range(1, first):
            print(f"     restored {n}. {pts[n][:80]}")
        if apply:
            con.execute("UPDATE opinions SET text_content=? WHERE id=?", (new, oid))
            con.execute(
                "INSERT INTO changelog (timestamp, batch, opinion_id, field, old_value, new_value, authority) "
                "VALUES (?,?,?,?,?,?,?)",
                (ts, BATCH, oid, "text_content.restore_syllabus_header",
                 t[:160], new[:160],
                 f"restored dropped '{header}' header + syllabus point(s) 1..{first-1} from West .doc "
                 f"({sp}); removed stray 'Synopsis' label; body unchanged; conf=high"))
    if apply:
        con.commit()
    print(f"\n{ok} ok, {skip} skipped ({'APPLIED' if apply else 'dry-run'})")


if __name__ == "__main__":
    main()
