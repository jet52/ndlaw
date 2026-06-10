"""Render print-verification crops for the corpus digit-flip candidates.

Same method as triage/render_flip_crops_2026-06-09.py: locate the PDF-side
token via the text layer, render a 3x crop of the printed glyphs (the
arbiter — the text layer alone is NOT verification). Skips the two known
text-layer rejects from the cohort pass. Output triage/flipverify-corpus/
<idx>_<oid>_p<para>_<db>-vs-<pdf>.png + manifest.tsv. Read-only.
"""
import csv, re, sqlite3
from pathlib import Path
import fitz

KNOWN_REJECTS = {(16419, 18, "31", "41"), (16699, 16, "09", "01")}
out_dir = Path("triage/flipverify-corpus")
out_dir.mkdir(exist_ok=True)
conn = sqlite3.connect("file:opinions.db?mode=ro", uri=True)
cands = list(csv.DictReader(open("triage/digit-flip-candidates-corpus-2026-06-10.tsv"), delimiter="\t"))

manifest = []
doc_cache = {}
for idx, r in enumerate(cands):
    oid, para = int(r["oid"]), int(r["para"])
    if (oid, para, r["db_token"], r["pdf_token"]) in KNOWN_REJECTS:
        manifest.append((idx, oid, para, r["db_token"], r["pdf_token"], "KNOWN_REJECT", "", r["context"]))
        continue
    m = re.match(r"(\d{4})ND(\d+)", r["cite"])
    pdf = Path.home() / f"refs/nd/opin/pdfs/{m.group(1)}/{m.group(1)}ND{int(m.group(2))}.pdf"
    if str(pdf) not in doc_cache:
        doc_cache.clear()
        doc_cache[str(pdf)] = fitz.open(str(pdf))
    doc = doc_cache[str(pdf)]
    post = r["context"].split("]", 1)[1] if "]" in r["context"] else ""
    needles = [f'{r["pdf_token"]}{post[:8].rstrip(".")}'.strip(), r["pdf_token"]]
    hit = None
    for needle in needles:
        if not needle:
            continue
        for pno in range(doc.page_count):
            rects = doc[pno].search_for(needle)
            if rects:
                hit = (pno, rects[0])
                break
        if hit:
            break
    if not hit:
        manifest.append((idx, oid, para, r["db_token"], r["pdf_token"], "NOT_FOUND", "", r["context"]))
        continue
    pno, rect = hit
    page = doc[pno]
    clip = fitz.Rect(max(0, rect.x0 - 175), max(0, rect.y0 - 18),
                     min(page.rect.x1, rect.x1 + 175), min(page.rect.y1, rect.y1 + 18))
    pix = page.get_pixmap(matrix=fitz.Matrix(3, 3), clip=clip)
    fn = f"{idx:03d}_{oid}_p{para}_{r['db_token']}-vs-{r['pdf_token']}.png"
    pix.save(str(out_dir / fn))
    manifest.append((idx, oid, para, r["db_token"], r["pdf_token"], "RENDERED", fn, r["context"]))
    if (idx + 1) % 100 == 0:
        print(f"...{idx+1}/{len(cands)}", flush=True)

w = csv.writer(open(out_dir / "manifest.tsv", "w"), delimiter="\t", lineterminator="\n")
w.writerow(["idx", "oid", "para", "db_token", "pdf_token", "status", "file", "context"])
w.writerows(manifest)
from collections import Counter
print(Counter(m[5] for m in manifest))
