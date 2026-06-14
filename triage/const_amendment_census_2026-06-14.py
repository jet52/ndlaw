#!/usr/bin/env python3
"""Amendment census (#4 of TODO-const-history-validation.md).

Read-only. Builds one master amendment table from both constitution DBs,
normalizes the amendment numbering (arabic / Roman / compound), enumerates the
full sequence, and flags gaps — the numbers absent from our data that need an
external authority (Blue Book amendment list / SoS measure history) to confirm
they are genuine non-amendments rather than silently-missing ones.

Output:
  triage/const-census-2026-06-14.tsv   one row per amendment number we hold
  stdout summary: sequence span, gaps, structural-hole confirmation

NOT an external cross-check yet — it builds the skeleton and the gap list the
cross-check works from.
"""
import sqlite3
import re
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HIST = ROOT / "constitution_history.db"
SERVED = ROOT / "constitution.db"
OUT = ROOT / "triage" / "const-census-2026-06-14.tsv"

ROMAN = {
    "I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000,
}


def roman_to_int(s: str):
    s = s.strip().upper()
    if not s or any(ch not in ROMAN for ch in s):
        return None
    total, prev = 0, 0
    for ch in reversed(s):
        val = ROMAN[ch]
        total += -val if val < prev else val
        prev = max(prev, val)
    return total


def parse_number(raw):
    """Return a sorted list of ints for an amendment_number cell.

    Handles arabic ('5'), Roman ('XCVIII'), and compounds ('5 & 6',
    'XXI & XXII', 'V and VI'). Returns [] if unparseable.
    """
    if raw is None:
        return []
    parts = re.split(r"\s*(?:&|and|,)\s*", str(raw).strip())
    out = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if p.isdigit():
            out.append(int(p))
        else:
            n = roman_to_int(p)
            if n is not None:
                out.append(n)
    return sorted(set(out))


def load(db, label):
    con = sqlite3.connect(db)
    rows = con.execute(
        "SELECT amendment_number, effective_date, election_date, action, "
        "affected, raw FROM amendments"
    ).fetchall()
    con.close()
    out = []
    for num, eff, elec, action, affected, raw in rows:
        for n in (parse_number(num) or [None]):
            out.append({
                "n": n, "raw_num": num, "eff": eff, "elec": elec,
                "action": action, "affected": affected, "raw": raw,
                "src": label,
            })
    return out


def affected_to_keys(affected):
    """Best-effort: pull provision lookup fragments from an `affected` cell.

    Returns a list of (kind, token) where kind is 'amend' (amend. art. ROMAN),
    'section' (bare/old § N), so we can test whether the named provision's text
    timeline actually moved on the amendment's date.
    """
    if not affected:
        return []
    keys = []
    for m in re.finditer(r"amend\.?\s*art\.?\s*([IVXLCDM]+)", affected, re.I):
        keys.append(("amend", m.group(1).upper()))
    for m in re.finditer(r"(?:art\.?\s*)?(?:§\s*)?\b(\d{1,3})\b", affected):
        keys.append(("section", m.group(1)))
    return keys


def applied_dates(db):
    """Map provision-citation -> set of version effective_start dates."""
    con = sqlite3.connect(db)
    rows = con.execute(
        "SELECT p.citation, v.effective_start FROM provisions p "
        "JOIN provision_versions v ON v.provision_id=p.id WHERE p.corpus='const'"
    ).fetchall()
    con.close()
    by_cite = {}
    for cite, start in rows:
        by_cite.setdefault(cite, set()).add(start)
    return by_cite


def is_applied(recs, by_cite):
    """Did the text timeline of an affected provision move on the eff_date?

    Returns 'Y' / 'N' / '?' (couldn't resolve the affected provision).
    """
    resolved_any = False
    for r in recs:
        eff = r["eff"]
        if not eff:
            continue
        for kind, tok in affected_to_keys(r["affected"]):
            # Find a provision citation that ends with this token.
            for cite, starts in by_cite.items():
                if kind == "amend" and re.search(rf"art\.?\s*{tok}\b", cite):
                    resolved_any = True
                    if eff in starts:
                        return "Y"
                elif kind == "section" and re.search(rf"§\s*{tok}\b", cite) and "art." not in cite:
                    resolved_any = True
                    if eff in starts:
                        return "Y"
    return "N" if resolved_any else "?"


def main():
    hist = load(HIST, "history")
    served = load(SERVED, "served")
    by_cite = applied_dates(SERVED)

    # Index by normalized number.
    by_n = {}
    for r in hist + served:
        by_n.setdefault(r["n"], []).append(r)

    numbered = sorted(n for n in by_n if n is not None)
    unparsed = by_n.get(None, [])
    lo, hi = numbered[0], numbered[-1]
    present = set(numbered)
    # Check from 1, not from our floor — amendment I may be missing below lo.
    gaps = [n for n in range(1, hi + 1) if n not in present]

    def to_roman(n):
        vals = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
                (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
                (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]
        s = ""
        for v, sym in vals:
            while n >= v:
                s += sym
                n -= v
        return s

    # Write master table.
    OUT.parent.mkdir(exist_ok=True)
    with open(OUT, "w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["number", "roman", "eff_date", "election_date", "action",
                    "in_history", "in_served", "text_applied", "affected",
                    "subject_raw"])
        unapplied = []
        for n in numbered:
            recs = by_n[n]
            srcs = {r["src"] for r in recs}
            r0 = recs[0]
            affected = " | ".join(sorted({(r["affected"] or "") for r in recs}))
            applied = is_applied(recs, by_cite)
            if applied == "N":
                unapplied.append((n, to_roman(n), r0["eff"], affected[:80]))
            w.writerow([
                n, to_roman(n), r0["eff"] or "", r0["elec"] or "",
                r0["action"] or "",
                "Y" if "history" in srcs else "",
                "Y" if "served" in srcs else "",
                applied, affected[:300], (r0["raw"] or "")[:120],
            ])

    # Report.
    print(f"=== Amendment census ===")
    print(f"history rows: {len(hist)}  served rows: {len(served)}")
    print(f"distinct numbers held: {len(numbered)}  span: {to_roman(lo)}({lo}) .. {to_roman(hi)}({hi})")
    print(f"unparsed amendment_number cells: {len(unparsed)}")
    print()
    print(f"=== SEQUENCE GAPS ({len(gaps)}) — numbers absent from our data, need external confirm ===")
    for n in gaps:
        print(f"  {to_roman(n):>8} ({n})")
    print()
    print(f"=== EVENT-RECORDED but TEXT-NOT-APPLIED ({len(unapplied)}) — amendment row exists, "
          f"but the affected provision's timeline never moved on that date ===")
    for n, rom, eff, aff in unapplied:
        print(f"  {rom:>8} ({n})  {eff or '?':<12} {aff}")
    print()
    # Known structural holes from PL-CONST-STRUCTURAL.
    structural = {"LXXVIII": 78, "XCVI": 96, "LXXXI": 81}
    print("=== structural-hole check (PL-CONST-STRUCTURAL expects these missing/partial) ===")
    for label, n in structural.items():
        status = "PRESENT" if n in present else "ABSENT"
        print(f"  {label} ({n}): {status}")
    print()
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
