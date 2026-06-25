#!/usr/bin/env python3
"""Strip residual West editorial 'Synopsis' blocks — v2 (court-element-terminated).

v1 (strip_west_synopsis.py) only handled Synopsis blocks bounded *directly* by
'Attorneys and Law Firms' with no court 'Syllabus by the Court' in between. That left
the larger deferred set where the West 'Synopsis' note sits immediately before the
court Syllabus (or before a star-page that opens the Syllabus/opinion). v2 generalizes
the terminator to the FIRST following court element and preserves it verbatim:

  terminator = earliest of:
     - a Syllabus label incl. OCR variants  (S[uy]l+[ai]bus)
     - a star-page marker                   (\\*+\\s?\\d  e.g. **52 / *329)
     - 'Attorneys and Law Firms'
     - 'Opinion\\n'

The removed span is ONLY the West editorial matter between the 'Synopsis' label and that
court element. The block must be short (<400 chars) and its body must match a strict
West-editorial whitelist (empty / disposition note / separate-opinion notice /
cross-reference / rehearing note) — anything resembling a factual statement of the case
is SKIPPED for individual handling ([[project_redistribution_scope]],
[[project_court_syllabus]]).

Hard invariants re-checked per opinion before write (a boundary-detection bug cannot pass):
  - the removed span contains NO court element (no syllabus-variant, star-page,
    'Attorneys and Law Firms', or 'Opinion\\n');
  - counts of syllabus-variants, star-pages, and 'Attorneys and Law Firms' are identical
    in old and new text (we removed only West editorial, never court text).

Dry-run by default. Usage:
  strip_west_synopsis_v2.py IDS.json [--apply] [--batch NAME] [--db opinions.db]
"""
import sqlite3, re, json, sys, datetime

SYLL = re.compile(r'S[uy]l+[ai]bus', re.I)
STAR = re.compile(r'\*+\s?\d')
MARK = ["Attorneys and Law Firms", "Opinion\n"]
FACT = re.compile(r'^(this is|defendant|plaintiff|petitioner|facts:|on\s+\w+\s+\d|'
                  r'from an order|the plaintiff|the defendant|action by|action to|'
                  r'the district court of|exhibits|conclusions and recommendations)', re.I)
DISPO = re.compile(r'^(the\s+)?(judgment|order|orders|decree|application|petition|appeal|'
                   r'appeals|writ|conviction|sentence|injunction|case|cause|action|motion|'
                   r'judgments)?[\s,]*(and\s+(judgment|order)\s+)?(affirmed|reversed|modified|'
                   r'remanded|vacated|dismissed|denied|granted|sustained|overruled|quashed|'
                   r'set aside|annulled|discharged|new trial)\b', re.I)
SEPOP = re.compile(r'\b(J\.|JJ\.|C\.\s?J\.|Judge|Justice)\b.*\b(dissent|concur|filed|opinion)', re.I)
SEPOP2 = re.compile(r'\b(dissent(ed|ing)?|concurr(ed|ing)?)\b.*\b(J\.|JJ\.|Judge)', re.I)
XREF = re.compile(r'^(see,?\s+also|for\s+former\s+(opinion|opinions|decision|decisions|report))', re.I)
REH = re.compile(r'^rehearing\s+(denied|granted|pending)', re.I)


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


def is_west_editorial(body):
    b = body.replace('\xa0', ' ').strip()
    if FACT.match(b):
        return False
    return (b == "" or DISPO.match(b) or XREF.match(b) or REH.match(b)
            or SEPOP.search(b) or SEPOP2.search(b))


def counts(t):
    return (len(SYLL.findall(t)), len(STAR.findall(t)), t.count("Attorneys and Law Firms"))


def plan(t):
    b = boundary(t)
    if b is None:
        return None, "no-boundary"
    i, e = b
    if e - i >= 400:
        return None, "block>=400"
    body = t[i + 8:e]
    if not is_west_editorial(body):
        return None, "not-west-editorial"
    removed = t[i:e]
    # removed must contain no court element
    if SYLL.search(removed) or STAR.search(removed) or "Attorneys and Law Firms" in removed \
            or "Opinion\n" in removed:
        return None, "court-element-in-removed"
    new = t[:i] + t[e:]
    if counts(t) != counts(new):
        return None, "element-count-changed"
    return (new, removed), None


def main():
    path = sys.argv[1]
    apply = "--apply" in sys.argv
    batch = sys.argv[sys.argv.index("--batch") + 1] if "--batch" in sys.argv else "west-synopsis-strip-v2"
    db = sys.argv[sys.argv.index("--db") + 1] if "--db" in sys.argv else "opinions.db"
    ids = json.load(open(path))
    con = sqlite3.connect(db)
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    applied = 0
    skip = {}
    for oid in ids:
        row = con.execute("SELECT text_content FROM opinions WHERE id=?", (oid,)).fetchone()
        if not row:
            skip["not-found"] = skip.get("not-found", 0) + 1
            continue
        old = row[0]
        res, reason = plan(old)
        if res is None:
            skip[reason] = skip.get(reason, 0) + 1
            print(f"  SKIP id{oid}: {reason}")
            continue
        new, removed = res
        applied += 1
        if apply:
            con.execute("UPDATE opinions SET text_content=? WHERE id=?", (new, oid))
            con.execute(
                "INSERT INTO changelog (timestamp, batch, opinion_id, field, old_value, new_value, authority) "
                "VALUES (?,?,?,?,?,?,?)",
                (ts, batch, oid, "text_content.west_synopsis_strip",
                 removed[:200], "",
                 "West .doc editorial Synopsis block (court-element-terminated, <400 chars, "
                 "whitelist=disposition/separate-opinion/cross-ref/rehearing); court Syllabus, "
                 "star-pages, attorneys preserved (element-count-gated); conf=high"))
        else:
            print(f"  OK id{oid}: -{len(removed)} chars: {removed.strip()[:90]!r}")
    if apply:
        con.commit()
    print(f"\napplied: {applied}  skipped: {skip}  ({'APPLIED' if apply else 'dry-run'})")


if __name__ == "__main__":
    main()
