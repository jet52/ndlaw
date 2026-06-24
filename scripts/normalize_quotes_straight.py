"""Normalize typographic (curly) quotes to straight ASCII across text_content.

User decision (2026-06-24): the authoritative edition uses straight ASCII quotes
and apostrophes. Maps the four curly quote characters to their ASCII forms:

    “ U+201C  open double   -> "  (U+0022)
    ” U+201D  close double  -> "
    ‘ U+2018  open single   -> '  (U+0027)
    ’ U+2019  apostrophe / close single -> '

NOTE this is intentionally LOSSY (open/close direction is discarded). The
directional data remains recoverable from the court PDFs; per-opinion changelog
rows record the substitution counts. OUT OF SCOPE (left untouched, ambiguous /
not curly quotes): primes ′″ (U+2032/2033), grave accent ` (U+0060), guillemets
«» — flagged for separate review if desired.

Per-opinion gate: the ONLY change is the four mapped chars (verified by applying
the map to old == new, and new contains none of the four). Dry-run by default;
report (md + json). FTS auto-syncs via the opinions_au trigger on --apply.

Usage: normalize_quotes_straight.py [--apply] [--db opinions.db]
       [--batch quotes-straight-2026-06-24] [--out triage/quotes-straight]
"""
import argparse
import json
import sqlite3
from datetime import datetime, timezone

TRANS = {0x201C: '"', 0x201D: '"', 0x2018: "'", 0x2019: "'"}
CURLY = set(TRANS)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", default="opinions.db")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--batch", default="quotes-straight-2026-06-24")
    ap.add_argument("--out", default="triage/quotes-straight")
    args = ap.parse_args()
    con = sqlite3.connect(args.db)
    ts = datetime.now(timezone.utc).isoformat()
    # candidates: any of the four curly chars present
    like = " OR ".join(f"instr(text_content,char({cp}))>0" for cp in CURLY)
    ids = [r[0] for r in con.execute(f"SELECT id FROM opinions WHERE {like}").fetchall()]

    report, applied, skipped = [], 0, 0
    tot = {cp: 0 for cp in CURLY}
    for oid in ids:
        old = con.execute("SELECT text_content FROM opinions WHERE id=?", (oid,)).fetchone()[0]
        counts = {cp: old.count(chr(cp)) for cp in CURLY}
        new = old.translate(TRANS)
        # gate: only the four chars changed, none remain
        if any(chr(cp) in new for cp in CURLY) or len(new) != len(old):
            skipped += 1
            report.append({"opinion_id": oid, "status": "SKIP_gate"})
            continue
        applied += 1
        for cp in CURLY:
            tot[cp] += counts[cp]
        report.append({"opinion_id": oid, "status": "OK", "counts": {f"U+{cp:04X}": counts[cp] for cp in CURLY if counts[cp]}})
        if args.apply:
            con.execute("UPDATE opinions SET text_content=? WHERE id=?", (new, oid))
            con.execute(
                "INSERT INTO changelog (timestamp, batch, opinion_id, field, old_value, new_value, authority) "
                "VALUES (?,?,?,?,?,?,?)",
                (ts, args.batch, oid, "text_content.quote_normalize",
                 f"curly “{counts[0x201C]} ”{counts[0x201D]} ‘{counts[0x2018]} ’{counts[0x2019]}",
                 "straight \" '", "user policy: straight ASCII quotes; direction recoverable from PDFs"))
    json.dump(report, open(f"{args.out}.json", "w"), ensure_ascii=False, indent=1)
    md = [f"# Curly->straight quote normalization — {'APPLIED' if args.apply else 'DRY-RUN'}", "",
          f"{applied} opinions OK, {skipped} skipped.", "",
          "Chars replaced (total occurrences):",
          f"- “ U+201C open-dq: {tot[0x201C]}", f"- ” U+201D close-dq: {tot[0x201D]}",
          f"- ‘ U+2018 open-sq: {tot[0x2018]}", f"- ’ U+2019 apos/close: {tot[0x2019]}", "",
          "Out of scope (left as-is): primes ′″, grave `, guillemets «»."]
    open(f"{args.out}.md", "w").write("\n".join(md))
    print(f"candidates: {len(ids)}  OK: {applied}  skipped: {skipped}")
    print(f"replaced: “{tot[0x201C]} ”{tot[0x201D]} ‘{tot[0x2018]} ’{tot[0x2019]}")
    print(f"report -> {args.out}.md / .json")
    if args.apply:
        con.commit()
        print(f"COMMITTED batch {args.batch}.")


if __name__ == "__main__":
    main()
