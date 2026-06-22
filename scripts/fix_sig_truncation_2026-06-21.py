"""Restore signature blocks dropped from modern DB opinion bodies.

The modern DB body was ingested verbatim from an OLD clean-format markdown whose
analyzer collapsed the final `[¶N]` signature paragraph down to a single trailing
name (the Whetsel class). The CURRENT ~/refs source is complete and matches the
court PDF. This splices the complete signature paragraph back in.

SAFE COHORT ONLY (strict guards):
  - classified TRUE_TRUNCATION (panel names genuinely absent from the DB tail),
  - gap == 1 (exactly the final signature paragraph dropped),
  - single-signature opinion (no concurrence/dissent separate writing — those
    need positional insertion, routed to manual review),
  - the dropped SOURCE paragraph is a PLAIN panel list (no 'concur', dateline,
    or footnote text mixed in),
  - every restored justice name is corroborated by the court PDF (gold standard).

The DB body's trailing signature FRAGMENT (the orphan kept name / dateline) is
identified as the maximal trailing run of signature-like lines and replaced with
`[¶ M+1] <panel, one justice per line>` rebuilt verbatim from the source.

Dry-run by default. `--apply` writes + logs to changelog (batch
`restore-sig-truncation-2026-06-21`).
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
_PARA = re.compile(r"\[¶\s*(\d+)\]")
DB = Path(__file__).resolve().parent.parent / "opinions.db"
REFS = Path.home() / "refs" / "nd" / "opin"
BATCH = "restore-sig-truncation-2026-06-21"

_SIG_LINE = re.compile(
    r"(C\.\s*J\.|S\.\s*J\.|D\.\s*J\.|,\s*JJ?\.|Dated at|concur|dissent)", re.I)
_PLAIN_BLOCK = re.compile(r"concur|dissent|Dated at|footnote|§|N\.D\.C\.C\.|N\.W\.", re.I)


def _norm(s: str) -> str:
    return re.sub(r"[^A-Z]", "", s.upper())


def plausible(year: int):
    out = []
    for _k, full, start, end in JUSTICES:
        if (start - 1) <= year <= ((end or 2100) + 1):
            last = full.split()[-1]
            if last == "III":
                last = full.split()[-2]
            out.append((full, last))
    return out


def _last_name(full: str) -> str:
    last = full.split()[-1]
    return full.split()[-2] if last == "III" else last


# All modern justice surnames (post-1960) for signature anchoring. Hard tenure
# dates in justices.py are unreliable (justices sit as surrogates outside their
# term, and at least one start year — Jensen's — is wrong), so name-splitting
# must NOT be year-gated; the court PDF is the authority that each name is real.
MODERN_SURNAMES = {_last_name(full): _last_name(full)
                   for _k, full, _s, e in JUSTICES if (e or 2100) >= 1960}


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


_ROLE_TOK = re.compile(r"^(C\.?J\.?|S\.?J\.?|D\.?J\.?|JJ?\.?|C\.|J\.)$", re.I)


def split_panel(sig_text: str, year: int):
    """Split a run like 'Gerald W. VandeWalle, C.J. Lisa Fair McEvers ...' into
    one justice per line, VERBATIM. A justice entry ends at a known surname token
    (+ any trailing role suffix like C.J./S.J.); the next token begins the next
    justice. Returns [(line, surname), ...] or None if no surname anchors found.
    """
    text = re.sub(r"\s+", " ", sig_text).strip()
    toks = text.split()
    pl = {_norm(last): last for last in MODERN_SURNAMES}
    out = []
    cur = []
    cur_sur = None
    i = 0
    while i < len(toks):
        t = toks[i]
        cur.append(t)
        nt = _norm(t)
        if nt in pl:                       # this token is a surname -> close entry
            cur_sur = pl[nt]
            # consume trailing role-suffix tokens (C.J., S.J., ...) into this line
            j = i + 1
            while j < len(toks) and _ROLE_TOK.match(toks[j].rstrip(",")):
                cur.append(toks[j]); j += 1
            out.append((" ".join(cur).strip(" ,"), cur_sur))
            cur = []; cur_sur = None
            i = j
            continue
        i += 1
    if cur:                                # trailing non-surname remnant -> reject
        return None
    return out or None


def trailing_sig_fragment(body: str):
    """Return (cut_index, fragment): the maximal trailing run of orphan
    signature-like lines to drop, and the body index where it starts.

    The walk STOPS at any line carrying a `[¶N]` marker — those are real
    paragraphs (e.g. a `[¶ 13] Dated at Bismarck...` dateline) and must be kept.
    If the signature was dropped entirely (no orphan name kept), the fragment is
    empty and cut_index is end-of-body (the new signature is appended)."""
    lines = body.rstrip("\n").split("\n")
    i = len(lines)
    while i > 0:
        ln = lines[i - 1].strip()
        if "[¶" in ln:                       # real paragraph marker -> keep
            break
        if ln == "" or _looks_sig_line(ln):
            i -= 1
        else:
            break
    frag = "\n".join(lines[i:]) if i < len(lines) else ""
    idx = len("\n".join(lines[:i]))
    return idx, frag


def _looks_sig_line(ln: str) -> bool:
    if _SIG_LINE.search(ln):
        return True
    # a bare justice full-name line (no sentence punctuation, <=6 words)
    if len(ln.split()) <= 6 and not re.search(r"[.;:][a-z]", ln):
        nl = _norm(ln)
        # any modern justice surname fuzzily present and line is name-shaped
        if re.match(r"^[A-Z]", ln) and len(nl) >= 4:
            for _k, full, _s, _e in JUSTICES:
                last = full.split()[-1]
                if last == "III":
                    last = full.split()[-2]
                if _fuzzy_in(nl, _norm(last)) and not re.search(r"\b(the|of|and|to|for|in|is|we|a)\b", ln.lower()):
                    return True
    return False


def pdf_names(label: str):
    m = re.match(r"(\d{4}) ND (\d+)", label)
    if not m:
        return None
    pdf = REFS / "pdfs" / m.group(1) / f"{m.group(1)}ND{m.group(2)}.pdf"
    if not pdf.exists():
        return None
    try:
        txt = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True,
                             text=True, timeout=60).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    return _norm(txt)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--report", type=Path, default=Path("triage/sig-truncation-fix.md"))
    args = ap.parse_args()

    rows = [r for r in csv.DictReader(open("triage/sig-drops-classified.csv"))
            if r["klass"] == "TRUE_TRUNCATION" and int(r["gap"]) == 1]
    conn = sqlite3.connect(str(DB))
    conn.row_factory = sqlite3.Row
    MULTI = re.compile(r"concur in the result|concurring|dissent|specially concur|, J\., (?:concurs|dissents)", re.I)

    planned, skipped = [], []
    for r in rows:
        oid = int(r["oid"]); label = r["label"]; sp = r["source_path"]
        year = int(label[:4])
        op = conn.execute("SELECT per_curiam,text_content FROM opinions WHERE id=?", (oid,)).fetchone()
        tc = op["text_content"]
        fm = _FM.match(tc)
        body = tc[fm.end():] if fm else tc
        src = (Path(sp) if sp.startswith("/") else REFS / sp).read_text(errors="replace")

        if MULTI.search(body):
            skipped.append((oid, label, "multi-opinion")); continue
        # the dropped source paragraph = highest [¶N]
        marks = list(_PARA.finditer(src))
        last = marks[-1]
        sig_src = src[last.end():].strip()
        sig_num = int(last.group(1))
        if _PLAIN_BLOCK.search(sig_src):
            skipped.append((oid, label, "non-plain-panel source")); continue
        parsed = split_panel(sig_src, year)
        if not parsed or len(parsed) < 1:
            skipped.append((oid, label, "unparseable panel")); continue
        lines = [ln for ln, _sur in parsed]
        # PDF corroboration: every restored surname must appear in the PDF
        pn = pdf_names(label)
        if pn is None:
            skipped.append((oid, label, "no PDF to verify")); continue
        if not all(_fuzzy_in(pn, _norm(sur)) for _ln, sur in parsed):
            skipped.append((oid, label, "PDF name mismatch")); continue

        frag = trailing_sig_fragment(body)
        if not frag:
            skipped.append((oid, label, "no trailing fragment")); continue
        idx, fragment = frag
        new_sig = f"[¶ {sig_num}] " + "\n".join(lines)
        new_body = body[:idx].rstrip("\n") + "\n\n" + new_sig + "\n"
        new_tc = (tc[:fm.end()] if fm else "") + new_body
        planned.append(dict(oid=oid, label=label, sig_num=sig_num,
                            old_frag=fragment, new_sig=new_sig,
                            old_tc=tc, new_tc=new_tc))

    # report
    L = [f"# Signature-truncation splice — {'APPLY' if args.apply else 'DRY-RUN'}\n",
         f"- planned: **{len(planned)}**", f"- skipped: **{len(skipped)}**\n",
         "## Planned splices (orphan fragment → restored signature)\n"]
    for p in planned[:args.limit] if args.limit else planned:
        L.append(f"### {p['label']} (oid {p['oid']})")
        L.append("```")
        L.append("OLD trailing fragment:")
        L.append(f"  {p['old_frag']!r}")
        L.append("NEW signature:")
        for ln in p["new_sig"].split("\n"):
            L.append(f"  {ln}")
        L.append("```\n")
    from collections import Counter
    L.append("## Skipped (routed to manual review)\n")
    for reason, n in Counter(s[2] for s in skipped).most_common():
        L.append(f"- {reason}: {n}")
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(L), encoding="utf-8")

    print(f"planned={len(planned)}  skipped={len(skipped)}")
    from collections import Counter as C
    for reason, n in C(s[2] for s in skipped).most_common():
        print(f"  skip: {reason}: {n}")

    if args.apply:
        for p in planned:
            conn.execute(
                "INSERT INTO changelog (batch, opinion_id, field, old_value, new_value) "
                "VALUES (?,?,?,?,?)",
                (BATCH, p["oid"], "text_content", p["old_tc"], p["new_tc"]))
            conn.execute("UPDATE opinions SET text_content=? WHERE id=?",
                         (p["new_tc"], p["oid"]))
        conn.commit()
        print(f"APPLIED {len(planned)} splices, logged batch {BATCH}")
    conn.close()
    print(f"Report: {args.report}")


if __name__ == "__main__":
    main()
