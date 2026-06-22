"""Normalize confirmed justice-name OCR garbles (follow-on to audit #11 roster_fuzzy).

Only fixes a garble when it is UNAMBIGUOUSLY a corruption of one roster justice:
  1. edit distance 1-2 from a roster surname (dist-2 gated to len>=6), not an exact
     roster surname, len>=4;
  2. **era-consistent** — exactly ONE roster surname at min distance whose tenure
     includes the opinion's year (±1). This single check excludes the false
     positives the detector surfaced: real surrogate judges near a roster name but
     in the wrong era (Zane Anderson~Pederson, Benson~Bronson, Buhr~Bahr, Geiger~Teigen)
     and junk words in old junk-panels (Hearing~Maring on a 1900s panel), since the
     near roster justice's tenure won't match;
  3. not a duplicate — the canonical surname is not already a token in the same field.

Anything ambiguous (two era-consistent justices, e.g. Burre between Burke 1919-37 and
Burr 1933-49 in the overlap years) is skipped for manual review, never guessed.

Dry-run by default. `--apply` backs up the DB, writes, logs `fix-roster-garbles-2026-06-22`.
"""
from __future__ import annotations

import argparse
import shutil
import sqlite3
from collections import defaultdict
from pathlib import Path

from ndcourts_mcp.audit_corpus import _lev
from ndcourts_mcp.justices import JUSTICES, KNOWN_LAST_NAMES

DB = Path(__file__).resolve().parent.parent / "opinions.db"
BATCH = "fix-roster-garbles-2026-06-22"

# tenure[surname] = [(start, end), ...]; display[surname] = canonical Title-Case form
_TENURE: dict[str, list] = defaultdict(list)
_DISPLAY: dict[str, str] = {}
for _key, _full, _start, _end in JUSTICES:
    _last = _full.split()[-1]
    if _last == "III":
        _last = _full.split()[-2]
    sn = _last.lower()
    _TENURE[sn].append((_start, _end or 2100))
    _DISPLAY[sn] = _last
_DISPLAY.setdefault("gierke", "Gierke")
_TENURE.setdefault("gierke", [(1978, 1991)])


def _era_ok(sn: str, year: int) -> bool:
    return any(s - 1 <= year <= e + 1 for s, e in _TENURE.get(sn, []))


# Tokens that survive the edit-distance + era checks but are plausible REAL
# alternate surnames (possible surrogate judges) or English words — never auto-fix
# these; leave for manual review. (Clear gibberish like "Buree"/"Eisk" is not here.)
_EXCLUDE = {
    "pedersen", "paulsen", "knudsen", "peterson", "spaulding", "newman", "newmann",
    "neuman", "gross", "sands", "norris", "knudsen",            # plausible real surnames
    "risk", "trace", "loss", "race", "grade", "said", "grac", "norman",  # English words
    "bure", "burk",  # equidistant (d1) between Burke AND Burr — attribution rests only on
             # era, and they co-occur with other Burke-garbles in unclear-composition panels
    "mourns", "mortus", "morbus",  # English/Latin words at d2 from Morris
}


def resolve(garble: str, year: int):
    """Return canonical Title-Case surname if the garble unambiguously maps to one
    era-consistent roster justice, else None."""
    g = garble.lower()
    if len(g) < 4 or g in KNOWN_LAST_NAMES or g in _EXCLUDE:
        return None
    best = 99
    cands = []
    for sn in KNOWN_LAST_NAMES:
        d = _lev(g, sn, 2)
        if d < best:
            best = d
            cands = [sn]
        elif d == best:
            cands.append(sn)
    if best == 1 and len(g) < 4:
        return None
    if best == 2 and len(g) < 6:
        return None
    if best > 2:
        return None
    era = [sn for sn in cands if _era_ok(sn, year)]
    if len(era) == 1:
        return _DISPLAY[era[0]]
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--show", type=int, default=12, help="sample N full before/after")
    args = ap.parse_args()
    conn = sqlite3.connect(str(DB))

    planned = []           # (oid, field, old_value, new_value, [(garble,canon)])
    pair_counts = defaultdict(int)
    skips = defaultdict(int)
    for oid, date_filed, author, judges in conn.execute(
            "SELECT id, date_filed, author, judges FROM opinions"):
        year = int((date_filed or "0")[:4]) or None
        if not year:
            continue
        for field_name, value in (("author", author), ("judges", judges)):
            if not value:
                continue
            tokens = [t.strip() for t in value.split(",")]
            present = {t.lower() for t in tokens}
            changed = []
            new_tokens = list(tokens)
            for i, tok in enumerate(tokens):
                canon = resolve(tok.strip().lower(), year)
                if not canon or canon == tok:
                    continue
                if canon.lower() in present and canon.lower() != tok.strip().lower():
                    skips["dup-canonical-already-in-field"] += 1
                    continue
                new_tokens[i] = canon
                present.add(canon.lower())
                changed.append((tok, canon))
            if changed:
                new_value = ", ".join(new_tokens)
                if new_value != value:
                    planned.append((oid, field_name, value, new_value, changed))
                    for old, canon in changed:
                        pair_counts[(old, canon)] += 1

    print(f"=== {'APPLY' if args.apply else 'DRY-RUN'} — {len(planned)} fields, "
          f"{sum(len(p[4]) for p in planned)} token fixes ===\n")
    print("top garble→canonical (count):")
    for (old, canon), n in sorted(pair_counts.items(), key=lambda kv: -kv[1])[:30]:
        print(f"   {n:>4}  {old:<12}→ {canon}")
    if skips:
        print("\nskips:", dict(skips))
    print(f"\n--- sample {args.show} fields (before → after) ---")
    for oid, field_name, old, new, changed in planned[:args.show]:
        print(f"  oid {oid} [{field_name}] {[f'{o}->{c}' for o,c in changed]}")
        print(f"      {old!r}")
        print(f"   -> {new!r}")

    if args.apply and planned:
        bak = DB.with_name(DB.name + ".bak-roster-garbles-2026-06-22")
        if not bak.exists():
            shutil.copy2(DB, bak); print(f"\nbackup → {bak.name}")
        for oid, field_name, old, new, changed in planned:
            note = "; ".join(f"{o}→{c}" for o, c in changed)
            conn.execute("INSERT INTO changelog (batch,opinion_id,field,old_value,new_value,authority) "
                         "VALUES (?,?,?,?,?,?)", (BATCH, oid, field_name, old, new,
                         f"OCR roster garble normalized (era-verified): {note}"))
            conn.execute(f"UPDATE opinions SET {field_name}=? WHERE id=?", (new, oid))
        conn.commit()
        print(f"\nAPPLIED {len(planned)} field updates; logged {BATCH}")
    conn.close()


if __name__ == "__main__":
    main()
