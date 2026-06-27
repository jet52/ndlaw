"""Routing regression guard for scripts/marker_triage.py.

The triage tool consolidates the recurring marker-defect classes (stored-twice
dedup, garbled-glyph repair, no-number/letter-in-number, XREF/pincite suppress,
markup-wrap defer). This test pins each class to its bucket using synthetic
opinions, so a refactor cannot silently mis-route a class (e.g. auto-applying a
digit it should have sent to PDF, or eating prose in the dedup text-match).

Runs the script as a subprocess against a temp DB (the routing logic lives in
main()), mirroring how it is invoked in practice.
"""
import json
import os
import sqlite3
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "scripts", "marker_triage.py")

# id -> (text, expected_bucket)
CASES = {
    101: ("[¶1] Intro paragraph here.\n\nand we affirm.\n\n[¶\n *2]*\n The facts on appeal.\n\n[¶3] Next para.", "AUTO"),
    102: ("[¶1] Intro.\n\n[¶\n *2]*\n The relevant facts are identical here in this copy.\n\n[¶2] The relevant facts are identical here in this copy.\n\n[¶3] Next.", "DEDUP"),
    103: ("[¶4] alpha text.\n\n[¶5J beta gamma text here.\n\n[¶6] delta text.", "AUTO"),       # bracket-glyph J=]
    104: ("[¶9] alpha.\n\n[¶1G] beta letter-in-number.\n\n[¶11] gamma.", "PDF"),               # infer a digit -> PDF
    105: ("[¶27] alpha.\n\n[¶ Here the text resumes without a number.\n\n[¶29] gamma.", "PDF"),  # no number
    106: ("[¶28] alpha.\n\n[¶'29] beta apostrophe.\n\n[¶30] gamma.", "AUTO"),                  # digits intact, seq agrees
    107: ("[¶27] alpha.\n\n[¶'29] beta but 28 missing.\n\n[¶31] gamma.", "PDF"),               # seq disagrees -> PDF
    108: ("text [¶3 of syllabus, 144 N.W.2d at 752.] more.", "SKIP"),                          # XREF
    109: ("See Wagner, 2003 ND 69, [¶]14, 660 N.W.2d 593. text.", "SKIP"),                     # citation pincite
    110: ("[¶4] a.\n\n*[¶5]*\n wrapped clean marker.\n\n[¶6] c.", "DEFER"),                    # markup-wrap
    # paren/curly-corrupted markers (mismatched brackets) — stored-twice dedups
    111: ("[¶9] a.\n\n(¶ 10] We conclude the duplicated paragraph text here.\n\n[¶10] We conclude the duplicated paragraph text here.\n\n[¶11] b.", "DEDUP"),
    112: ("[¶19] a.\n\n{¶ 20] The district court found the duplicated text here.\n\n[¶20] The district court found the duplicated text here.\n\n[¶21] b.", "DEDUP"),
    # legit parenthetical cross-ref "(¶ 21)" must NOT be treated as a marker
    113: ("[¶4] As we held (¶ 21) earlier, the rule applies.\n\n[¶5] b.", "SKIP"),
}

BUCKET_FILE = {
    "AUTO": "marker-triage-auto.json",
    "DEDUP": "marker-triage-dedup.json",
    "PDF": "marker-triage-needs-pdf.json",
    "SKIP": "marker-triage-not-marker.json",
    "DEFER": "marker-triage-markup-wrap.json",
}


@pytest.fixture(scope="module")
def routed(tmp_path_factory):
    d = tmp_path_factory.mktemp("mt")
    db = str(d / "mt.db")
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE opinions(id INTEGER PRIMARY KEY, text_content TEXT)")
    con.executemany("INSERT INTO opinions VALUES(?,?)", [(i, txt) for i, (txt, _) in CASES.items()])
    con.commit()
    con.close()
    r = subprocess.run([sys.executable, SCRIPT, "--db", db, "--out-dir", str(d), "--structural"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    got = {}
    for bucket, fname in BUCKET_FILE.items():
        for row in json.load(open(d / fname)):
            oid = row.get("opinion_id") or row.get("oid")
            got.setdefault(oid, set()).add(bucket)
    # unknown must stay empty — it means "parser failed to recognize"
    assert json.load(open(d / "marker-triage-unknown.json")) == []
    return got


@pytest.mark.parametrize("oid,expected", [(i, b) for i, (_, b) in CASES.items()])
def test_marker_routes_to_expected_bucket(routed, oid, expected):
    assert expected in routed.get(oid, set()), f"id{oid} routed to {routed.get(oid)}, expected {expected}"
