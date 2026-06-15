#!/usr/bin/env python3
"""Second-read correction: art. IX § 7 [1981-01-01,1982-12-01) head.

The wave-2 redline reversal of the 1982 amendment kept an ADDED span (the handoff's
"#1 read error"). The 1982 amendment changed "All lands MENTIONED IN THE PRECEDING
SECTION shall be appraised" -> "All lands RECEIVED BY THE STATE FOR ANY SPECIFIC
EDUCATIONAL OR CHARITABLE INSTITUTION shall be appraised". Reversing should restore
"mentioned in the preceding section" AND drop "received by the state for any specific
educational or charitable institution". The agent restored the struck phrase but failed
to drop "for any specific educational or charitable institution", and wrote a comma
where the original has a semicolon ("common schools; but").

Caught by the second-read pass: the head scored only 0.859 vs the 1981 BB (every other
owed head scored >= 0.971). The corrected text is the pre-1982 §7, confirmed by a
QUADRUPLE witness — 1981 Blue Book + 1925 official (orig § 160) + 1954 BB + 1973 BB,
all identical. Text-only change to a non-current version; FTS untouched. Scratch only.
"""
import re
import sqlite3
import sys
from pathlib import Path

DB = "/tmp/const-scratch.db"
BATCH = "modern-ix7-secondread-2026-06-15"
CITE = "N.D. Const. art. IX, § 7"
HEAD_START = "1981-01-01"

CORRECT = ("All lands mentioned in the preceding section shall be appraised and sold in "
           "the same manner and under the same limitations and subject to all the "
           "conditions as to price and sale as provided above for the appraisal and sale "
           "of lands for the benefit of common schools; but a distinct and separate "
           "account shall be kept by the proper officers of each of said funds; provided, "
           "that the limitations as to the time in which school land may be sold shall "
           "apply only to lands granted for the support of common schools.")

BAD_FRAGMENT = "for any specific educational or charitable institution"  # the un-dropped 1982 add


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def main(apply=False):
    con = sqlite3.connect(DB)
    row = con.execute(
        "SELECT v.id, v.effective_start, v.effective_end, v.text_content "
        "FROM provisions p JOIN provision_versions v ON v.provision_id=p.id "
        "WHERE p.citation=? ORDER BY v.effective_start LIMIT 1", (CITE,)).fetchone()
    vid, s, e, cur = row
    problems = []
    if s != HEAD_START:
        problems.append(f"earliest version starts {s}, expected {HEAD_START}")
    if BAD_FRAGMENT not in cur and norm(cur) != norm(CORRECT):
        problems.append("head no longer contains the bad fragment and isn't already corrected — inspect")
    # witness gate: corrected text contained (despaced) in the 1925 clean source
    clean = norm((Path.home() / "refs/nd/const/processed/1925_official_constitution.md").read_text())
    if norm(CORRECT) not in clean:
        problems.append("corrected text NOT contained in 1925 official (witness gate)")

    print(f"{CITE}  head [{s}->{e}]")
    print(f"  current head has bad fragment: {BAD_FRAGMENT in cur}")
    print(f"  corrected text witnessed in 1925 official: {norm(CORRECT) in clean}")
    if norm(cur) == norm(CORRECT):
        print("  (already corrected — idempotent skip)"); con.close(); return
    if problems:
        print("GATE FAIL:")
        for p in problems:
            print("  -", p)
        con.close(); return
    print("GATES PASS.")
    if not apply:
        print("(dry run) re-run with --apply"); con.close(); return

    con.execute("UPDATE provision_versions SET text_content=?, "
                "source_authority='wave-2 redline (1982 amend reversal), CORRECTED on second "
                "read — 1981 BB + 1925 official § 160 + 1954/1973 BB (quadruple witness)' "
                "WHERE id=?", (CORRECT, vid))
    con.execute("INSERT INTO changelog (batch, provision_id, version_id, field, new_value, authority) "
                "SELECT ?, provision_id, id, 'text_content_secondread_fix', ?, ? "
                "FROM provision_versions WHERE id=?",
                (BATCH, "dropped un-reversed 1982 addition 'for any specific educational or "
                        "charitable institution'; comma->semicolon ('common schools; but')",
                 "1981 BB + 1925 official § 160 + 1954/1973 BB", vid))
    con.commit()
    print("CORRECTED art IX §7 head.")
    con.close()


if __name__ == "__main__":
    main(apply="--apply" in sys.argv)
