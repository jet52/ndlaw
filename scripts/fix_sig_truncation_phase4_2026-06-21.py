"""Phase 4: positional insertion of dropped MAJORITY PANELS.

The remaining TRUE_TRUNCATION cohort is uniform: the majority panel was dropped
while a trailing element survived in the DB — a concurrence/dissent "concurs in
the result" notation, a participation note ("The Honorable X ... did not
participate"), or a separate-writing signature. The panel belongs BEFORE that
trailing element, not appended after.

Because the dropped span is the consecutive tail of the opinion (panel +
trailing element) and the DB's last paragraph IS that trailing element,
inserting the panel immediately before the DB's last paragraph reconstructs the
source order.

DIVERGENCE GUARD (the load-bearing safety check): every justice named in the
DB's trailing element must also appear in the dropped source signature region.
If the DB names a justice the source doesn't (e.g. 2014 ND 148 / oid 16311: DB
"Sandstrom concurs in the result" vs source "Crothers concurs"), the two are
factually different texts -> skip to manual.

The inserted panel = the source signature lines whose justice is NOT already in
the DB trailing element (so a notation the DB already renders is never
duplicated). Every inserted name is corroborated against the court PDF.

Dry-run by default. `--apply` writes + logs `restore-sig-truncation-phase4-2026-06-21`.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import re
import sqlite3
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("sig1", HERE / "fix_sig_truncation_2026-06-21.py")
sig1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sig1)

DB = HERE.parent / "opinions.db"
REFS = Path.home() / "refs" / "nd" / "opin"
BATCH = "restore-sig-truncation-phase4-2026-06-21"

# the DB's trailing element must look like a signature/notation, not opinion prose
_TRAILING = re.compile(
    r"concurs?\b|dissents?\b|concur in|sitting in place|did not participate|"
    r"unavoidably absent|disqualified|, C?J\.|, JJ\.|Surrogate Judge|District Judge", re.I)


def justices_in(text: str) -> set[str]:
    nt = sig1._norm(text)
    found = {s for s in sig1.MODERN_SURNAMES if sig1._fuzzy_in(nt, sig1._norm(s))}
    # drop a surname subsumed by a longer matched one (normalization erases word
    # boundaries, so "Sand" matches inside "Sandstrom"); keep only the longest.
    return {s for s in found
            if not any(s != o and sig1._norm(s) in sig1._norm(o) for o in found)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--report", type=Path, default=Path("triage/sig-truncation-phase4-fix.md"))
    args = ap.parse_args()

    rows = [r for r in csv.DictReader(open("triage/sig-drops-classified.csv"))
            if r["klass"] == "TRUE_TRUNCATION"]
    conn = sqlite3.connect(str(DB))
    planned, skipped = [], []
    for r in rows:
        oid = int(r["oid"]); label = r["label"]; sp = r["source_path"]; year = int(label[:4])
        tc = conn.execute("SELECT text_content FROM opinions WHERE id=?", (oid,)).fetchone()[0]
        fm = sig1._FM.match(tc)
        body = tc[fm.end():] if fm else tc
        src = (Path(sp) if sp.startswith("/") else REFS / sp).read_text(errors="replace")
        db_max, src_max = int(r["db_max"]), int(r["src_max"])

        # DB trailing element = last paragraph; must be a signature/notation
        paras = re.split(r"\n\s*\n", body.rstrip())
        db_last = paras[-1].strip()
        if not _TRAILING.search(db_last):
            skipped.append((oid, label, "DB tail is prose, not a trailing notation")); continue
        db_just = justices_in(db_last)
        if not db_just:
            skipped.append((oid, label, "no justice in DB trailing element")); continue

        # dropped source signature region (consecutive tail)
        marks = list(sig1._PARA.finditer(src))
        by = {int(m.group(1)): m for m in marks}
        drop_text = []
        ok = True
        for n in range(db_max + 1, src_max + 1):
            m = by.get(n)
            if not m:
                ok = False; break
            end = min([mm.start() for mm in marks if mm.start() > m.end()] + [len(src)])
            drop_text.append(re.sub(r"\s+", " ", src[m.end():end]).strip())
        if not ok:
            skipped.append((oid, label, "dropped paragraphs not locatable")); continue
        combined = " ".join(drop_text)
        # skip datelines/footnotes, or a standalone roman-numeral section divider
        # (a dropped paragraph that is JUST "VI" etc. — NOT a "V." middle initial)
        if (re.search(r"Dated at|§|N\.D\.C\.C\.|footnote", combined)
                or any(re.fullmatch(r"[IVX]{1,4}", t.strip()) for t in drop_text)):
            skipped.append((oid, label, "dateline/section-marker/footnote in source")); continue

        parsed = sig1.split_panel(combined, year)
        if not parsed:
            skipped.append((oid, label, "source signature unparseable")); continue
        src_just = {s for _ln, s in parsed}

        # DIVERGENCE GUARD: DB trailing justice(s) must all be in the source region
        if not db_just <= src_just:
            skipped.append((oid, label, f"divergence: DB has {db_just - src_just} not in source")); continue

        # panel = source lines whose justice the DB does NOT already render
        panel = [ln for ln, s in parsed if s not in db_just]
        if not panel:
            skipped.append((oid, label, "no missing panel members")); continue
        # an inline roman-numeral section marker fused into a panel line
        # ("VII Dale V. Sandstrom") -> structurally complex, route to manual
        if any(re.match(r"^[IVX]{1,4}\s", ln) for ln in panel):
            skipped.append((oid, label, "roman-numeral section marker in panel")); continue
        # PDF corroboration
        pn = sig1.pdf_names(label)
        if pn is None:
            skipped.append((oid, label, "no PDF to verify")); continue
        if not all(sig1._fuzzy_in(pn, sig1._norm(s)) for ln, s in parsed if ln in panel):
            skipped.append((oid, label, "PDF name mismatch")); continue

        # surgical positional insert: before the DB's last paragraph
        insert = f"[¶ {db_max + 1}] " + "\n".join(panel)
        start_last = body.rstrip().rfind(db_last)
        head = body[:start_last].rstrip("\n")
        new_body = head + "\n\n" + insert + "\n\n" + db_last + ("\n" if body.endswith("\n") else "")
        new_tc = (tc[:fm.end()] if fm else "") + new_body
        planned.append(dict(oid=oid, label=label, insert=insert, db_last=db_last[:80],
                            old_tc=tc, new_tc=new_tc))

    from collections import Counter
    L = [f"# Signature-truncation Phase 4 (positional panel insert) — {'APPLY' if args.apply else 'DRY-RUN'}\n",
         f"- planned: **{len(planned)}**", f"- skipped: **{len(skipped)}**\n", "## Planned\n"]
    for p in planned:
        L.append(f"### {p['label']} (oid {p['oid']})")
        L.append("Insert BEFORE trailing element:")
        for ln in p["insert"].split("\n"):
            L.append(f"  {ln}")
        L.append(f"trailing element kept: …{p['db_last']!r}")
        L.append("")
    L.append("## Skipped\n")
    for reason, n in Counter(s[2] for s in skipped).most_common():
        L.append(f"- {reason}: {n}")
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(L), encoding="utf-8")
    print(f"planned={len(planned)}  skipped={len(skipped)}")
    for reason, n in Counter(s[2] for s in skipped).most_common():
        print(f"  skip: {reason}: {n}")

    if args.apply:
        for p in planned:
            conn.execute(
                "INSERT INTO changelog (batch, opinion_id, field, old_value, new_value) "
                "VALUES (?,?,?,?,?)", (BATCH, p["oid"], "text_content", p["old_tc"], p["new_tc"]))
            conn.execute("UPDATE opinions SET text_content=? WHERE id=?", (p["new_tc"], p["oid"]))
        conn.commit()
        print(f"APPLIED {len(planned)}, logged batch {BATCH}")
    conn.close()
    print(f"Report: {args.report}")


if __name__ == "__main__":
    main()
