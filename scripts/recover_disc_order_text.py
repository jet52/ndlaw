#!/usr/bin/env python3
"""Recover full court ORDER text for 3 disciplinary opinions stored as West-synopsis-only.

id9351 (Lince), id10797 (Goetz), id20482 (McMahon) were ingested with only the West
`Synopsis` as text_content — the West-doc parser dropped the ORDER body for the ORDER-format
docs (same class as Disc. Bd. v. Johnson 481 N.W.2d 225). All three have the full court order
in their authoritative West .doc (the registered primary source, source_reporter='westlaw').
The .doc order body is recovered (West furniture — Synopsis, West Headnotes, All Citations,
End-of-Document — stripped), matching the West-doc order convention already in the corpus
(id11076/id11239: `*NNN ORDER OF DISBARMENT\n...<body>...<signatures>`).

Provenance is unchanged: source_reporter stays 'westlaw', the West .doc stays primary, so the
2026-06-22 restore-source-reporter-westlaw decision is respected. The Lince .doc is in fact
more complete than CourtListener's NW2d markdown (it carries the justice signature block).

Idempotent: sets the final correct state regardless of current state, and clears any prior
rows of its own batch first. Dry-run by default. Usage: recover_disc_order_text.py [--apply]
"""
import sqlite3, re, subprocess, sys, datetime

REFS = "/Users/jerod/refs/nd/opin"
BATCH = "recover-disc-order-text-2026-06-25"

DOCS = {
    9351:  ("N.W.2d/366/0444-Unknown.doc", "NW2d/366/444.md"),
    10797: ("N.W.2d/465/0480-Unknown.doc", "NW2d/465/480.md"),
    20482: ("N.W.2d/298/0372-Unknown.doc", None),
}


def order_body(docpath):
    txt = subprocess.run(["textutil", "-convert", "txt", "-stdout", f"{REFS}/{docpath}"],
                         capture_output=True, text=True).stdout
    # from the star-paged ORDER heading to the West "All Citations" trailer
    m = re.search(r'(\*\d+\s+ORDER OF .*?)(?:\n\s*All Citations|\nEnd of Document)', txt, re.S)
    if not m:
        raise SystemExit(f"order body not found in {docpath}")
    return m.group(1).rstrip() + "\n"


def main():
    apply = "--apply" in sys.argv
    con = sqlite3.connect("opinions.db")
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    if apply:
        con.execute("DELETE FROM changelog WHERE batch=?", (BATCH,))  # clear prior same-batch rows
    for oid, (docpath, mdpath) in DOCS.items():
        old = con.execute("SELECT text_content FROM opinions WHERE id=?", (oid,)).fetchone()[0]
        new = order_body(docpath)
        print(f"\n=== id{oid}  {len(old)} -> {len(new)} chars  (primary -> westlaw:{docpath}) ===")
        print("  OLD:", repr(old[:90]))
        print("  NEW head:", repr(new[:90]))
        print("  NEW tail:", repr(new[-90:]))
        if apply:
            con.execute("UPDATE opinions SET text_content=?, source_reporter='westlaw', source_path=? WHERE id=?",
                        (new, docpath, oid))
            con.execute("UPDATE opinion_sources SET is_primary=0 WHERE opinion_id=?", (oid,))
            con.execute("UPDATE opinion_sources SET is_primary=1 WHERE opinion_id=? AND source_path=?",
                        (oid, docpath))
            con.execute(
                "INSERT INTO changelog (timestamp, batch, opinion_id, field, old_value, new_value, authority) "
                "VALUES (?,?,?,?,?,?,?)",
                (ts, BATCH, oid, "text_content.recover_order_body",
                 old[:200], new[:200],
                 f"recovered full court ORDER text from West .doc ({docpath}); was West-synopsis-only "
                 "(parser dropped ORDER body); West furniture stripped; provenance unchanged; conf=high"))
    if apply:
        con.commit()
    print(f"\n({'APPLIED' if apply else 'dry-run'})")


if __name__ == "__main__":
    main()
