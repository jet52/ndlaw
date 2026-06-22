"""Phase 2 of signature-truncation repair: the cases Phase 1 skipped.

Phase 1 (fix_sig_truncation_2026-06-21) handled single-signature opinions only.
The remaining TRUE_TRUNCATION cohort is mostly MULTI-OPINION (a concurrence or
dissent follows the majority), which splits into:

  (A) APPEND-SAFE  - the dropped final paragraph is a separate-writing signature
                     the DB is simply missing; the DB body ends with the
                     concurrence/dissent prose. Appending [¶N] at the end is
                     positionally correct.
  (B) MISORDER     - the dropped paragraph is the MAJORITY panel, but the DB
                     already renders the trailing concurrence-in-result note, so
                     appending would duplicate names / misorder. -> manual.

Discriminator: append ONLY IF none of the dropped paragraph's justice surnames
already appear in the DB body tail (no overlap). Plus the proven guards: the
dropped paragraph parses as a clean panel, and every name is corroborated by the
court PDF. Datelines / surrogate-only / spelled-out-role paragraphs that don't
parse are routed to manual review rather than verbatim-appended.

Dry-run by default. `--apply` writes + logs batch `restore-sig-truncation-phase2-2026-06-21`.
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
BATCH = "restore-sig-truncation-phase2-2026-06-21"
_PLAIN_BLOCK = re.compile(r"Dated at|footnote|§|N\.D\.C\.C\.|N\.W\.|Surrogate|Chief Justice", re.I)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--report", type=Path, default=Path("triage/sig-truncation-phase2-fix.md"))
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

        # dropped paragraphs (db_max, src_max], in order
        marks = list(sig1._PARA.finditer(src))
        by_num = {int(m.group(1)): m for m in marks}
        dropped = []
        ok = True
        for n in range(db_max + 1, src_max + 1):
            m = by_num.get(n)
            if not m:
                ok = False; break
            nxt = [mm.start() for mm in marks if mm.start() > m.end()]
            end = min(nxt) if nxt else len(src)
            dropped.append((n, src[m.end():end].strip()))
        if not ok or not dropped:
            skipped.append((oid, label, "dropped paragraphs not locatable")); continue

        # each dropped paragraph must parse as a clean panel (no dateline/footnote)
        if any(_PLAIN_BLOCK.search(t) for _n, t in dropped):
            skipped.append((oid, label, "dateline/surrogate/spelled-role")); continue
        parsed = []
        for n, t in dropped:
            pp = sig1.split_panel(t, year)
            if not pp:
                parsed = None; break
            parsed.append((n, pp))
        if parsed is None:
            skipped.append((oid, label, "unparseable panel")); continue

        # SINGLE-SIGNATURE GUARD: append is positionally safe only when the dropped
        # paragraph is a lone separate-writing signature (one justice signing after
        # their concurrence/dissent). A multi-name panel is the MAJORITY signature,
        # which belongs BEFORE any separate writing the DB already has -> positional
        # insert, not append -> manual.
        lines_total = [ln for _n, pp in parsed for ln in pp]
        if len(lines_total) != 1:
            skipped.append((oid, label, "multi-name panel (positional, not append)")); continue

        # OVERLAP GUARD: if the dropped surname already appears in the DB tail,
        # the DB already has this signature -> append would duplicate.
        tail = sig1._norm(body[-260:])
        all_sur = {sur for _n, pp in parsed for _ln, sur in pp}
        if any(sig1._fuzzy_in(tail, sig1._norm(s)) for s in all_sur):
            skipped.append((oid, label, "name overlap with DB tail (misorder risk)")); continue

        # PDF corroboration
        pn = sig1.pdf_names(label)
        if pn is None:
            skipped.append((oid, label, "no PDF to verify")); continue
        if not all(sig1._fuzzy_in(pn, sig1._norm(s)) for _n, pp in parsed for _ln, s in pp):
            skipped.append((oid, label, "PDF name mismatch")); continue

        add = "\n\n".join(f"[¶ {n}] " + "\n".join(ln for ln, _s in pp) for n, pp in parsed)
        new_body = body.rstrip("\n") + "\n\n" + add + "\n"
        new_tc = (tc[:fm.end()] if fm else "") + new_body
        planned.append(dict(oid=oid, label=label, add=add,
                            db_tail=body[-90:], old_tc=tc, new_tc=new_tc))

    from collections import Counter
    L = [f"# Signature-truncation Phase 2 (multi-opinion) — {'APPLY' if args.apply else 'DRY-RUN'}\n",
         f"- planned: **{len(planned)}**", f"- skipped: **{len(skipped)}**\n",
         "## Planned appends (DB tail … → appended signature)\n"]
    for p in planned:
        L.append(f"### {p['label']} (oid {p['oid']})")
        L.append(f"DB ends: …{p['db_tail']!r}")
        L.append("Appended:")
        for ln in p["add"].split("\n"):
            L.append(f"  {ln}")
        L.append("")
    L.append("## Skipped\n")
    for reason, n in Counter(s[2] for s in skipped).most_common():
        L.append(f"- {reason}: {n}")
        for oid, lbl, rr in skipped:
            if rr == reason:
                L.append(f"  - {lbl} (oid {oid})")
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
