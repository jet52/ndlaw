"""Repair OCR-garbled / missing paragraph markers on signature blocks.

These opinions (classified MARKER_GARBLED by classify_sig_drops) have a COMPLETE
signature panel in the DB body, but its `[¶N]` marker is OCR-garbled
('[IT 29]', '[¶ 21J', '[1111]', '[f 13]', '(¶ 8]', '[UlO]') or absent entirely.
sigscan undercounts the max marker as a result. Text is already complete — only
the marker needs fixing.

Repair: in the trailing signature paragraph, find the first justice name and
replace whatever occupies the "marker slot" before it (the garble, or nothing)
with `[¶ {src_max}] `, where src_max is the marker number the complete source
carries for that paragraph.

STRICT SKIPS (routed to manual review):
  - the signature paragraph already starts with a valid `[¶ N]` marker,
  - no justice surname found in the trailing paragraph,
  - panel names not all corroborated by the court PDF,
  - the panel is split by a page-break artifact (*NNN) — ambiguous slot.

Dry-run by default. `--apply` writes + logs batch `fix-marker-garbled-2026-06-21`.
"""
from __future__ import annotations

import argparse
import csv
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ndcourts_mcp.justices import JUSTICES  # noqa: E402

_FM = re.compile(r"^(\s*---\s*\n.*?\n---\s*\n)", re.DOTALL)
_VALID_MARK = re.compile(r"^\s*\[¶\s*\d+\]")
DB = Path(__file__).resolve().parent.parent / "opinions.db"
REFS = Path.home() / "refs" / "nd" / "opin"
BATCH = "fix-marker-garbled-2026-06-21"


def _last(full: str) -> str:
    t = full.split()[-1]
    return full.split()[-2] if t == "III" else t


MODERN = sorted({_last(f) for _k, f, _s, e in JUSTICES if (e or 2100) >= 1960},
                key=len, reverse=True)


def _norm(s: str) -> str:
    return re.sub(r"[^A-Z]", "", s.upper())


def _editdist1(a: str, b: str) -> bool:
    if a == b:
        return True
    if abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) == 1
    s, l = (a, b) if len(a) < len(b) else (b, a)
    return any(s == l[:i] + l[i + 1:] for i in range(len(l)))


def _fuzzy_in(hay: str, needle: str) -> bool:
    if len(needle) < 4:
        return False
    if needle in hay:
        return True
    n = len(needle)
    return any(_editdist1(needle, hay[i:i + w])
               for w in (n - 1, n, n + 1) for i in range(len(hay) - w + 1))


def pdf_norm(label: str):
    m = re.match(r"(\d{4}) ND (\d+)", label)
    if not m:
        return None
    pdf = REFS / "pdfs" / m.group(1) / f"{m.group(1)}ND{m.group(2)}.pdf"
    if not pdf.exists():
        return None
    try:
        return _norm(subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True,
                                    text=True, timeout=60).stdout)
    except (OSError, subprocess.SubprocessError):
        return None


# A leading paragraph marker, possibly OCR-garbled: opening bracket/paren, then
# up to a few ¶/digit/OCR-confusable chars, an optional number, an optional
# (single) garbled closing char. Bounded so it can never eat into a name.
_GARBLED_MARK = re.compile(r"^\s*[\[(]\s*[¶\dIlTfUVSÍ!|O]{1,4}\s*\d{0,3}\s*[\])Jl1!Í]?")
_NAME_START = re.compile(r"^[A-Z][A-Za-z.'’-]*")


def strip_marker_slot(para: str):
    """Return (slot, remainder): the leading garbled-marker token (or '') and the
    signature text after it. Replacing slot with the correct `[¶N]` marker never
    touches a justice name. Returns None if the paragraph neither starts with a
    bracket marker nor with a name token (i.e. structure is unexpected)."""
    m = _GARBLED_MARK.match(para)
    if m:
        rest = para[m.end():].lstrip(" ,")
        return para[:m.end()], rest
    # no bracket: must start directly with a name token to prepend a marker
    if _NAME_START.match(para.lstrip()):
        return "", para.lstrip()
    return None


def panel_surnames(para: str):
    found = []
    nj = _norm(para)
    for sur in MODERN:
        if _fuzzy_in(nj, _norm(sur)):
            found.append(sur)
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--report", type=Path, default=Path("triage/marker-garbled-fix.md"))
    args = ap.parse_args()

    rows = [r for r in csv.DictReader(open("triage/sig-drops-classified.csv"))
            if r["klass"] == "MARKER_GARBLED"]
    conn = sqlite3.connect(str(DB))
    planned, skipped = [], []
    for r in rows:
        oid = int(r["oid"]); label = r["label"]; src_max = int(r["src_max"])
        tc = conn.execute("SELECT text_content FROM opinions WHERE id=?", (oid,)).fetchone()[0]
        fm = _FM.match(tc)
        body = tc[fm.end():] if fm else tc
        paras = re.split(r"\n\s*\n", body.rstrip())
        # last paragraph containing a justice name = the signature
        sig_idx = None
        for k in range(len(paras) - 1, -1, -1):
            if panel_surnames(paras[k]):
                sig_idx = k; break
        if sig_idx is None:
            skipped.append((oid, label, "no signature paragraph")); continue
        para = paras[sig_idx]
        if _VALID_MARK.match(para):
            skipped.append((oid, label, "valid marker already present")); continue
        # split panel: a page-break artifact (a standalone *NNN line) can split the
        # signature across paragraphs, leaving the chosen para as only the 2nd half.
        # Detect by checking whether the preceding real paragraph (skipping empty /
        # pure page-marker paras) also carries justice names.
        prev = sig_idx - 1
        while prev >= 0 and (not paras[prev].strip() or re.fullmatch(r"\*?\d{2,4}", paras[prev].strip())):
            prev -= 1
        if prev >= 0:
            pp = paras[prev].rstrip()
            # a split panel's first half dangles: it carries a justice name but has
            # no sentence terminator and no 'concur'/'JJ.' (the terminator is in the
            # 2nd half). Ordinary prose ends in punctuation, so it won't trip this.
            if (panel_surnames(pp) and not re.search(r'[.!?:"”\)]$', pp)
                    and not re.search(r"concur|JJ\.", pp)):
                skipped.append((oid, label, "split panel (page break)")); continue
        sur = panel_surnames(para)
        has_role = bool(re.search(r"\b(C\.\s*J\.|S\.\s*J\.|D\.\s*J\.|JJ?\.|concur)\b", para))
        if len(sur) < 2 and not has_role:
            skipped.append((oid, label, "single-name / no-role panel")); continue
        slot = strip_marker_slot(para)
        if slot is None:
            skipped.append((oid, label, "unexpected paragraph start")); continue
        old_slot, remainder = slot
        # PDF corroboration
        pn = pdf_norm(label)
        if pn is None:
            skipped.append((oid, label, "no PDF to verify")); continue
        if not all(_fuzzy_in(pn, _norm(s)) for s in sur):
            skipped.append((oid, label, "PDF name mismatch")); continue

        new_para = f"[¶ {src_max}] " + remainder
        # surgical: replace ONLY the signature paragraph in-place, preserving all
        # other whitespace (a split/rejoin would renormalize paragraph gaps).
        if body.count(para) != 1:
            skipped.append((oid, label, "signature paragraph not uniquely locatable")); continue
        new_body = body.replace(para, new_para, 1)
        new_tc = (tc[:fm.end()] if fm else "") + new_body
        planned.append(dict(oid=oid, label=label, src_max=src_max,
                            old_slot=old_slot, panel=remainder[:72],
                            old_tc=tc, new_tc=new_tc))

    L = [f"# Marker-garbled repair — {'APPLY' if args.apply else 'DRY-RUN'}\n",
         f"- planned: **{len(planned)}**", f"- skipped: **{len(skipped)}**\n",
         "## Planned (marker slot → corrected marker)\n"]
    for p in planned:
        L.append(f"- **{p['label']}** (oid {p['oid']}): "
                 f"`{p['old_slot']!r}` → `[¶ {p['src_max']}] ` + «{p['panel']}…»")
    L.append("\n## Skipped (manual review)\n")
    from collections import Counter
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
