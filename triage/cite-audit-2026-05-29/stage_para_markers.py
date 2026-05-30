#!/usr/bin/env python3
"""Stage inputs for the paragraph-marker re-OCR batch (§ priority TODO #4).

Builds para-markers/ working tree:
  pdfs_in/<cite>.pdf       — the 57 court PDFs, copied for marker batch input
  marker_out/              — marker --force_ocr output lands here
  westlaw_doc/             — the 57 Westlaw .doc (RTF) files from the zip
  westlaw_txt/<idx>.txt    — textutil-converted plain text (clean [¶N])
  mapping.json             — idx -> {cite, year, num, pdf, wl_doc, wl_txt}

The zip entries are 'NN - Case.doc' where NN is the 1-based line number of
missing-para-markers.txt, so file NN maps to cites[NN-1].
"""
import json
import os
import shutil
import subprocess
import zipfile

BASE = "/Users/jerod/code/ndcourts-mcp/triage/cite-audit-2026-05-29"
WORK = f"{BASE}/para-markers"
ZIP = "/Users/jerod/Downloads/Westlaw Precision - 57 items from Find And Print.zip"
PDF_ROOT = "/Users/jerod/refs/nd/opin/pdfs"

cites = [l.strip() for l in open(f"{BASE}/missing-para-markers.txt") if l.strip()]
for d in ("pdfs_in", "marker_out", "westlaw_doc", "westlaw_txt"):
    os.makedirs(f"{WORK}/{d}", exist_ok=True)

# Unzip Westlaw docs (names like '01 - State v Smith.doc')
with zipfile.ZipFile(ZIP) as z:
    names = sorted(z.namelist())
    z.extractall(f"{WORK}/westlaw_doc")
assert len(names) == len(cites), f"zip has {len(names)} != {len(cites)} cites"

mapping = []
for idx, cite in enumerate(cites, start=1):
    yr, num = cite.split(" ND ")
    slug = f"{yr}ND{num}"
    src_pdf = f"{PDF_ROOT}/{yr}/{slug}.pdf"
    dst_pdf = f"{WORK}/pdfs_in/{slug}.pdf"
    shutil.copy(src_pdf, dst_pdf)
    # zip entry for this index
    wl_doc = next(n for n in names if n.startswith(f"{idx:02d} - "))
    wl_doc_path = f"{WORK}/westlaw_doc/{wl_doc}"
    wl_txt_path = f"{WORK}/westlaw_txt/{idx:02d}_{slug}.txt"
    subprocess.run(["textutil", "-convert", "txt", wl_doc_path, "-output", wl_txt_path],
                   check=True)
    mapping.append({"idx": idx, "cite": cite, "year": yr, "num": num, "slug": slug,
                    "pdf": dst_pdf, "wl_doc": wl_doc_path, "wl_txt": wl_txt_path})

json.dump(mapping, open(f"{WORK}/mapping.json", "w"), indent=2)
print(f"staged {len(mapping)} opinions -> {WORK}")
print("pdfs_in:", len(os.listdir(f'{WORK}/pdfs_in')), "| westlaw_txt:", len(os.listdir(f'{WORK}/westlaw_txt')))
