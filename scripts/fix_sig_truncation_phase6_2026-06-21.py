"""Phase 6: participation-note truncations (panel<->note ordering).

Two clean shapes remain among the surrogate/participation cases:

  POSITIONAL  - the DB ends with a participation note ("The Honorable X ... did
                not participate") and the majority PANEL paragraph that precedes
                it in the source was dropped. Insert the panel before the note.
  APPEND      - the DB ends with the panel ("... JJ, concur.") and the trailing
                participation NOTE was dropped. Append the note.

Only panels that parse cleanly to >=3 KNOWN justices are handled here; panels
that embed a surrogate judge (Grosz/Graff, not in the roster) are left to manual
review, as are datelines and the genuine 16311 divergence. Every inserted panel
name is corroborated by the court PDF, and a panel is never inserted if its
justices already sit in the DB tail.

Dry-run by default. `--apply` writes + logs `restore-sig-truncation-phase6-2026-06-21`.
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
BATCH = "restore-sig-truncation-phase6-2026-06-21"
NOTE = re.compile(r"^The Honorable\b|sitting in place|unavoidably absent|did not participate", re.I)


def _match(nt, ns):
    return (ns in nt) if len(ns) < 5 else sig1._fuzzy_in(nt, ns)


def justices(text):
    nt = sig1._norm(text)
    f = {s for s in sig1.MODERN_SURNAMES if _match(nt, sig1._norm(s))}
    return {s for s in f if not any(s != o and sig1._norm(s) in sig1._norm(o) for o in f)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--report", type=Path, default=Path("triage/sig-truncation-phase6-fix.md"))
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
        marks = list(sig1._PARA.finditer(src))
        by = {int(m.group(1)): m for m in marks}
        drop = []
        for n in range(int(r["db_max"]) + 1, int(r["src_max"]) + 1):
            m = by.get(n)
            if not m:
                continue
            end = min([mm.start() for mm in marks if mm.start() > m.end()] + [len(src)])
            drop.append((n, re.sub(r"\s+", " ", src[m.end():end]).strip()))
        note_paras = [(n, t) for n, t in drop if NOTE.match(t)]
        panel_paras = [(n, t) for n, t in drop if not NOTE.match(t)]
        db_last = re.split(r"\n\s*\n", body.rstrip())[-1].strip()

        if NOTE.search(db_last) and panel_paras:
            # POSITIONAL: insert the clean panel before the DB's note
            pn_num, pn_text = panel_paras[0]
            parsed = sig1.split_panel(pn_text, year)
            if not parsed or len(parsed) < 3:
                skipped.append((oid, label, "panel unparseable (surrogate?)")); continue
            if any(re.search(r"[SD]\.\s*J\.", ln) for ln, _s in parsed):
                skipped.append((oid, label, "surrogate judge in panel (manual)")); continue
            sur = [s for _ln, s in parsed]
            if any(s in justices(body[-260:]) for s in sur):
                skipped.append((oid, label, "panel already in DB tail")); continue
            pn = sig1.pdf_names(label)
            if pn is None or not all(sig1._fuzzy_in(pn, sig1._norm(s)) for s in sur):
                skipped.append((oid, label, "no PDF / name mismatch")); continue
            insert = f"[¶ {pn_num}] " + "\n".join(ln for ln, _s in parsed)
            start = body.rstrip().rfind(db_last)
            new_body = body[:start].rstrip("\n") + "\n\n" + insert + "\n\n" + db_last + ("\n" if body.endswith("\n") else "")
            planned.append(dict(oid=oid, label=label, kind="insert panel", add=insert,
                                ctx=db_last[:70], old_tc=tc, new_tc=(tc[:fm.end()] if fm else "") + new_body))
        elif note_paras and re.search(r"JJ,?\.?\s*concur|concur\.$|, JJ", db_last):
            # APPEND: the DB ends with the panel; append the dropped note
            nn, nt = note_paras[-1]
            add = f"[¶ {nn}] " + nt
            new_body = body.rstrip("\n") + "\n\n" + add + ("\n" if body.endswith("\n") else "")
            planned.append(dict(oid=oid, label=label, kind="append note", add=add,
                                ctx=db_last[:70], old_tc=tc, new_tc=(tc[:fm.end()] if fm else "") + new_body))
        else:
            skipped.append((oid, label, "not a clean participation panel/note shape")); continue

    from collections import Counter
    L = [f"# Signature-truncation Phase 6 (participation notes) — {'APPLY' if args.apply else 'DRY-RUN'}\n",
         f"- planned: **{len(planned)}**", f"- skipped: **{len(skipped)}**\n", "## Planned\n"]
    for p in planned:
        L.append(f"### {p['label']} (oid {p['oid']}) — {p['kind']}")
        L.append(f"context (DB tail): …{p['ctx']!r}")
        for ln in p["add"].split("\n"):
            L.append(f"  {ln}")
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
