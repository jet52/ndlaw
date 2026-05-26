"""De-duplicate opinion 13240 (Johnson v. Johnson, 2000 ND 170) text_content.

text_content held the opinion TWICE: a frontmatter/title/attorney shell followed
by copy1 [first 'MARING, Justice' .. second] (the half whose [¶N] markers had been
mojibake'd, repaired in demangle-13240-2026-05-26) and copy2 [second 'MARING,
Justice' .. end] (the originally-intact copy, complete through the ¶166 Sandstrom
dissent). Healthy 2000-era siblings carry a single copy: frontmatter + '# Title'
+ court/cite + byline + body.

Fix: keep the shell up to the first byline, then the single clean copy2 body:
    recon = text[:first_MARING] + text[second_MARING:]
copy2 is kept (it was never corrupted; copy1 was the mojibake'd one). Result:
one coherent opinion, ¶1–166, 0 garbage chars.

Run with --apply to write; default dry-run. Logged to changelog for revert.
"""
from __future__ import annotations
import argparse, re, sqlite3

BATCH = "dedup-13240-2026-05-26"
OID = 13240


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    conn = sqlite3.connect("opinions.db")
    old = conn.execute("SELECT text_content FROM opinions WHERE id=?", (OID,)).fetchone()[0]
    occ = [m.start() for m in re.finditer(r"MARING, Justice", old)]
    assert len(occ) == 2, f"expected 2 byline occurrences, found {len(occ)}"
    recon = old[:occ[0]] + old[occ[1]:]
    # invariants on the result
    assert recon.count("MARING, Justice") == 1
    assert recon.count("Madonna Johnson appeals") == 1
    paras = [int(m.group(1)) for m in re.finditer(r"\[¶\s*(\d+)\]", recon)]
    assert paras and max(paras) == 166, f"opinion not complete (max ¶ {max(paras) if paras else None})"
    print(f"len {len(old)} -> {len(recon)}; ¶1..{max(paras)}; "
          f"MARING x{recon.count('MARING, Justice')}")
    if args.apply:
        conn.execute("INSERT INTO changelog (batch, opinion_id, field, old_value, new_value) "
                     "VALUES (?,?, 'text_content', ?, ?)",
                     (BATCH, OID, f"len={len(old)} (duplicated copy1+copy2)",
                      f"len={len(recon)} (deduplicated, copy2 kept)"))
        conn.execute("UPDATE opinions SET text_content=? WHERE id=?", (recon, OID))
        conn.commit()
        print("APPLIED")
    else:
        print("DRY RUN")
    conn.close()


if __name__ == "__main__":
    main()
