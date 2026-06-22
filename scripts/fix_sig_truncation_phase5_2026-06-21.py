"""Phase 5: orphan-name signature replacement (prose-tail remainder).

A handful of TRUE_TRUNCATION cases are the original Whetsel pattern — the DB
body kept ONLY the panel's last justice name as a bare trailing line, dropping
the marker and the rest of the panel. Phase 1 skipped them because the source
panel ends with a footnote-reference digit ("... Jerod E. Tufte 1"), which broke
split_panel.

This replaces the orphan trailing name with the complete `[¶ src_max] <panel,
one justice per line>` from the source, after stripping a trailing footnote
digit. Guards: the orphan must equal the source panel's LAST member (confirming
the kept-last-name shape) and no other panel member may already be in the DB
tail (else it is not a simple orphan); every name corroborated by the court PDF.

Dry-run by default. `--apply` writes + logs `restore-sig-truncation-phase5-2026-06-21`.
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
BATCH = "restore-sig-truncation-phase5-2026-06-21"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--report", type=Path, default=Path("triage/sig-truncation-phase5-fix.md"))
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

        paras = re.split(r"\n\s*\n", body.rstrip())
        orphan = paras[-1].strip()
        # orphan must be a bare 1-name signature line (no notation, <=6 words)
        if len(orphan.split()) > 6 or re.search(r"concur|dissent|affirm|reverse|remand|\bwe\b", orphan, re.I):
            skipped.append((oid, label, "DB tail not a bare orphan name")); continue
        if "[" in orphan:
            skipped.append((oid, label, "orphan has a marker")); continue
        # if the paragraph BEFORE the orphan is itself a concurrence/dissent
        # notation, the orphan is the tail of a split trailing element (positional
        # case), not a clean kept-last-name -> replacing would duplicate it.
        if len(paras) >= 2 and re.search(r"concur|dissent", paras[-2], re.I):
            skipped.append((oid, label, "preceding paragraph is a concurrence (positional)")); continue

        # source dropped panel (strip a trailing footnote-reference digit)
        marks = list(sig1._PARA.finditer(src))
        by = {int(m.group(1)): m for m in marks}
        if src_max not in by:
            skipped.append((oid, label, "source paragraph missing")); continue
        m = by[src_max]
        end = min([mm.start() for mm in marks if mm.start() > m.end()] + [len(src)])
        panel_text = re.sub(r"\s+", " ", src[m.end():end]).strip()
        panel_text = re.sub(r"\s+\d+$", "", panel_text)          # drop trailing footnote digit
        panel_text = re.sub(r"\s+(?:VI{0,3}|I{2,3}|IV|IX|X)$", "", panel_text)  # trailing section heading
        parsed = sig1.split_panel(panel_text, year)
        if not parsed or len(parsed) < 2:
            skipped.append((oid, label, "panel unparseable / single-name")); continue
        panel_surnames = [s for _ln, s in parsed]

        # orphan must equal the panel's LAST member (kept-last-name shape)
        orphan_just = justices(orphan)
        if not orphan_just or panel_surnames[-1] not in orphan_just:
            skipped.append((oid, label, "orphan is not the panel's last member")); continue
        # and no OTHER panel member may already sit in the DB tail
        tail_just = justices(body[-300:])
        if any(s in tail_just for s in panel_surnames[:-1]):
            skipped.append((oid, label, "other panel members already in DB tail")); continue
        # PDF corroboration
        pn = sig1.pdf_names(label)
        if pn is None or not all(sig1._fuzzy_in(pn, sig1._norm(s)) for s in panel_surnames):
            skipped.append((oid, label, "no PDF / name mismatch")); continue

        new_sig = f"[¶ {src_max}] " + "\n".join(ln for ln, _s in parsed)
        start_orphan = body.rstrip().rfind(orphan)
        new_body = body[:start_orphan].rstrip("\n") + "\n\n" + new_sig + ("\n" if body.endswith("\n") else "")
        new_tc = (tc[:fm.end()] if fm else "") + new_body
        planned.append(dict(oid=oid, label=label, orphan=orphan, new_sig=new_sig,
                            old_tc=tc, new_tc=new_tc))

    from collections import Counter
    L = [f"# Signature-truncation Phase 5 (orphan replace) — {'APPLY' if args.apply else 'DRY-RUN'}\n",
         f"- planned: **{len(planned)}**", f"- skipped: **{len(skipped)}**\n", "## Planned\n"]
    for p in planned:
        L.append(f"### {p['label']} (oid {p['oid']})")
        L.append(f"orphan replaced: {p['orphan']!r}")
        L.append("with:")
        for ln in p["new_sig"].split("\n"):
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


def justices(text: str) -> set[str]:
    nt = sig1._norm(text)
    found = set()
    for s in sig1.MODERN_SURNAMES:
        ns = sig1._norm(s)
        if (ns in nt) if len(ns) < 5 else sig1._fuzzy_in(nt, ns):
            found.add(s)
    return {s for s in found if not any(s != o and sig1._norm(s) in sig1._norm(o) for o in found)}


if __name__ == "__main__":
    main()
