"""Splice missing signature-block paragraphs from court PDFs.

Worklist: triage/text-missing-measured-2026-06-09.tsv, opinions whose ONLY
missing paragraph is class=SIGNATURE (justice names, <160 chars, no prose
words). The paragraph body is re-extracted from the court PDF at apply time
and spliced verbatim as `[¶ N] <body>` immediately BEFORE the next present
marker — order-preserving, and footnote-safe (footnote blocks that sit
between the flanking markers stay attached to the preceding paragraph,
matching analyzer layout). Both DB text_content and the on-disk markdown
source are updated.

Gates (any failure -> skip + report):
  * exactly one missing ¶ for the opinion, class SIGNATURE
  * [¶N] absent and both flanking markers present in DB text
  * PDF re-extraction yields the ¶N body; body still classifies as a
    signature block (len<160, no the/of/and/to/that)
  * no line of the body is a bare number (page-number artifact guard)
"""
import csv, re, sqlite3, sys
from pathlib import Path
from pdfminer.high_level import extract_text
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ndcourts_mcp.db import log_change, log_provenance

BATCH = "sig-splice-2026-06-09"
REFS = Path.home() / "refs/nd/opin"
MARK = re.compile(r"\[¶\s*(\d+)\]")
PROSE = re.compile(r"\b(the|of|and|to|that)\b")
apply = "--apply" in sys.argv
conn = sqlite3.connect("opinions.db")

rows = list(csv.DictReader(open("triage/text-missing-measured-2026-06-09.tsv"), delimiter="\t"))
by_oid = {}
for r in rows:
    by_oid.setdefault(int(r["oid"]), []).append(r)
work = {o: rs[0] for o, rs in by_oid.items()
        if len(rs) == 1 and rs[0]["class"] == "SIGNATURE"}

def insert_before_next(text, n, body, spaced):
    """Insert `[¶ n] body` immediately before the next present marker.
    Returns (new_text, reason_or_None)."""
    toks = [(m.start(), m.end(), int(m.group(1))) for m in MARK.finditer(text)]
    nums = {t[2] for t in toks}
    if n in nums:
        return None, "marker already present"
    if not any(p < n for p in nums) or not any(p > n for p in nums):
        return None, "not flanked"
    nxt = min((t for t in toks if t[2] > n), key=lambda t: t[2])
    block = f"{spaced}{n}] {body}\n\n"
    return text[:nxt[0]] + block + text[nxt[0]:], None

n_ok = n_skip = 0
skips, samples = [], []
for i, (oid, r) in enumerate(sorted(work.items())):
    n = int(r["missing_para"])
    text, sp = conn.execute(
        "SELECT text_content, source_path FROM opinions WHERE id=?", (oid,)).fetchone()
    m = re.search(r"(\d{4})ND(\d+)\.md$", sp or "")
    if not m:
        skips.append((oid, n, f"unexpected source_path {sp}")); n_skip += 1; continue
    pdf = Path.home() / f"refs/nd/opin/pdfs/{m.group(1)}/{m.group(1)}ND{int(m.group(2))}.pdf"
    if not pdf.exists():
        skips.append((oid, n, "no PDF")); n_skip += 1; continue
    try:
        t = extract_text(str(pdf))
    except Exception as ex:
        skips.append((oid, n, f"pdf error {str(ex)[:40]}")); n_skip += 1; continue
    ptoks = [(mm.start(), mm.end(), int(mm.group(1))) for mm in MARK.finditer(t)]
    body = None
    for j, (s, e, num) in enumerate(ptoks):
        if num == n:
            end = ptoks[j + 1][0] if j + 1 < len(ptoks) else len(t)
            body = t[e:end].strip()
            break
    if not body:
        skips.append((oid, n, "PDF lacks marker/body")); n_skip += 1; continue
    # normalize intra-block whitespace: collapse blank lines, strip line ends.
    # Drop page-footer numbers and section-heading roman numerals that pdfminer
    # sweeps in when the signature block spans a page break (verified artifacts:
    # bare digits sit at \x0c breaks; roman headings already exist in the DB text).
    lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
    lines = [ln for ln in lines
             if not re.fullmatch(r"\d+", ln) and not re.fullmatch(r"[IVXLC]+", ln)]
    body = "\n".join(lines)
    if not body:
        skips.append((oid, n, "empty after artifact strip")); n_skip += 1; continue
    if len(body) >= 160 or PROSE.search(body.lower()):
        skips.append((oid, n, f"no longer classifies SIGNATURE: {body[:60]!r}")); n_skip += 1; continue
    spaced = "[¶ " if re.search(r"\[¶ \d", text) else "[¶"
    new, why = insert_before_next(text, n, body, spaced)
    if why:
        skips.append((oid, n, why)); n_skip += 1; continue
    n_ok += 1
    if len(samples) < 8:
        samples.append(f"oid{oid} ¶{n}: {body[:80]!r}")
    if apply:
        conn.execute("UPDATE opinions SET text_content=? WHERE id=?", (new, oid))
        log_change(conn, BATCH, oid, "text_content.splice_para",
                   f"¶{n} missing", f"{spaced}{n}] {body}",
                   authority=f"signature block spliced verbatim from court PDF {pdf.name}")
        p = REFS / sp
        if p.exists():
            md = p.read_text()
            md2, mwhy = insert_before_next(md, n, body, spaced)
            if md2:
                p.write_text(md2)
            else:
                skips.append((oid, n, f"md not updated: {mwhy}"))
    if (i + 1) % 100 == 0:
        print(f"...{i+1}/{len(work)}")

print(f"{'APPLIED' if apply else 'DRY RUN'}: {n_ok} spliced, {n_skip} skipped (of {len(work)})")
for s in samples:
    print("  ", s)
if skips:
    print("SKIPS:")
    for oid, n, why in skips:
        print(f"  oid{oid} ¶{n}: {why}")
if apply:
    log_provenance(conn, "sig-splice", command="triage/splice_signatures_2026-06-09.py --apply",
                   rows_affected=n_ok,
                   notes=f"batch {BATCH}; {n_ok} signature-block ¶s spliced verbatim from court PDFs")
    conn.commit()
