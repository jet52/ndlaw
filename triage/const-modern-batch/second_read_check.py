#!/usr/bin/env python3
"""Second-read pass: witness each owed reconstructed version against the Blue Books.

For every owed provision, for each (BB, T) witness, report whether the DB version IN
FORCE at T is reconstructed and how it scores against the BB's text for that (art,§):
containment (norm(db) in norm(bb)) or fuzzy ratio. A reconstructed version that is in
force at a BB's date and matches that BB is independently witnessed (the BB is a
separate publication from the redline PDF + 1981 BB the agent originally used).

Group A (recon in force @1989) → 1989 BB is the independent second witness.
Group B (recon head not in force @1989: IX §7/§10 short [1981,1982) prior; X §26
created 2011) → flagged for a targeted measure/1981-BB second read.
"""
import re
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from snapshot_diff_modern import parse_comp, norm, best_ratio, COMPS, ROMAN

DB = "/tmp/const-scratch.db"
OWED = ["art. I, § 16", "art. II, § 1", "art. IX, § 1", "art. IX, § 2",
        "art. IX, § 7", "art. IX, § 10", "art. IX, § 12", "art. IX, § 13",
        "art. X, § 26", "art. XII, § 1"]


def key_of(cite):
    m = re.search(rf"art\.\s+([{ROMAN}]+),\s+§\s+(\d+)", cite)
    return (m.group(1), int(m.group(2))) if m else None


def db_inforce(con, cite, T):
    rows = con.execute(
        "SELECT effective_start, COALESCE(effective_end,'open'), text_content, batch "
        "FROM provision_versions pv JOIN provisions p ON pv.provision_id=p.id "
        "WHERE p.citation=? ORDER BY effective_start", (cite,)).fetchall()
    for s, e, txt, b in rows:
        if s <= T and (e == "open" or e >= T):
            return s, e, txt, b
    return None


def main():
    con = sqlite3.connect(DB)
    comps = {y: parse_comp(COMPS[y][0]) for y in COMPS}
    for o in OWED:
        cite = f"N.D. Const. {o}"
        k = key_of(cite)
        print(f"\n{o}  (art {k[0]} §{k[1]})")
        for y in COMPS:
            T = COMPS[y][1]
            inf = db_inforce(con, cite, T)
            if not inf:
                print(f"   {y}: DB has no version in force @{T} (correctly absent)")
                continue
            s, e, txt, b = inf
            recon = not (b.startswith("const-ingest") or b.startswith("const-history"))
            tag = "RECON" if recon else "current"
            comptext = comps[y].get(k)
            if comptext is None:
                print(f"   {y}: [{s}->{e}] {tag:7s} | NOT in {y} BB (parse miss / absent)")
                continue
            dn, cn = norm(txt), norm(comptext)
            if dn and dn in cn:
                verdict = "CONTAINED ✓"
            else:
                verdict = f"ratio={best_ratio(dn, cn):.3f}"
            print(f"   {y}: [{s}->{e}] {tag:7s} | {verdict}")
    con.close()


if __name__ == "__main__":
    main()
