"""One-off scoping: classify PDF-era ND opinions as scanned (OCR-required)
vs born-digital, by inspecting the court PDF structure (read-only, no
reprocessing). Scanned PDFs carry ~one full-page raster image per page;
born-digital text PDFs carry ~none.

Output: triage/pdf-extraction-classification-2026-05-18.tsv + summary.
"""
from __future__ import annotations

import math
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ndcourts_mcp.db import get_connection  # noqa: E402

REFS = Path("/Users/jerod/refs/nd/opin")
OUT = Path(__file__).resolve().parent / "pdf-extraction-classification-2026-05-18.tsv"


def pdf_metrics(pdf: Path) -> tuple[int, int, float, int]:
    """Return (pages, fullpage_image_count, image_megapixels, kb_per_page)."""
    size_kb = pdf.stat().st_size // 1024
    try:
        info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True,
                               text=True, timeout=30).stdout
        pages = next((int(l.split()[1]) for l in info.splitlines()
                      if l.startswith("Pages:")), 0)
    except Exception:
        pages = 0
    try:
        il = subprocess.run(["pdfimages", "-list", str(pdf)],
                             capture_output=True, text=True,
                             timeout=60).stdout.splitlines()[2:]
    except Exception:
        il = []
    full = 0
    pix = 0
    for ln in il:
        c = ln.split()
        if len(c) < 5:
            continue
        try:
            w, h = int(c[3]), int(c[4])
        except ValueError:
            continue
        if w > 0 and h > 0:
            pix += w * h
            if w > 1000 and h > 1000:   # full-page-scale raster
                full += 1
    kbpp = size_kb // pages if pages else size_kb
    return pages, full, pix / 1_000_000, kbpp


def is_scanned(pages: int, full: int, mp: float, kbpp: int) -> bool:
    # Primary signal: a full-page image for at least half the pages.
    # Backstop (over-inclusive per policy): heavy KB/page with any raster.
    if pages and full >= max(1, math.ceil(pages * 0.5)):
        return True
    if full >= 1 and kbpp > 60:
        return True
    return False


def main() -> None:
    conn = get_connection(Path("opinions.db"))
    rows = conn.execute(
        "SELECT o.id, o.date_filed, o.source_path, "
        "  (SELECT c.citation FROM citations c WHERE c.opinion_id=o.id "
        "   AND c.reporter='ND-neutral' LIMIT 1) AS neutral, "
        "  (SELECT COUNT(*) FROM opinion_sources s WHERE s.opinion_id=o.id) AS nsrc "
        "FROM opinions o "
        "WHERE o.date_filed>='1997-01-01' AND o.source_reporter='ND' "
        "ORDER BY o.date_filed"
    ).fetchall()

    out = OUT.open("w")
    out.write("oid\tneutral\tyear\tpages\tfullpage_imgs\timg_mp\tkb_per_page\t"
              "classification\thas_2nd_source\tpdf_path\n")
    n = scanned = scanned_need_wl = missing_pdf = 0
    by_year: dict[str, list[int]] = {}
    for r in rows:
        n += 1
        sp = r["source_path"] or ""
        pdf = REFS / sp.replace("markdown/", "pdfs/").replace(".md", ".pdf") \
            if sp.startswith("markdown/") else None
        yr = (r["date_filed"] or "")[:4]
        if not pdf or not pdf.exists():
            missing_pdf += 1
            out.write(f'{r["id"]}\t{r["neutral"]}\t{yr}\t\t\t\t\tNO_PDF\t'
                      f'{1 if r["nsrc"]>=2 else 0}\t{pdf}\n')
            continue
        pages, full, mp, kbpp = pdf_metrics(pdf)
        sc = is_scanned(pages, full, mp, kbpp)
        cls = "SCANNED_OCR" if sc else "born_digital"
        has2 = 1 if r["nsrc"] >= 2 else 0
        if sc:
            scanned += 1
            by_year.setdefault(yr, [0, 0])
            by_year[yr][0] += 1
            if not has2:
                scanned_need_wl += 1
                by_year[yr][1] += 1
        out.write(f'{r["id"]}\t{r["neutral"]}\t{yr}\t{pages}\t{full}\t'
                  f'{mp:.1f}\t{kbpp}\t{cls}\t{has2}\t{pdf}\n')
        if n % 500 == 0:
            print(f"  ...{n}/{len(rows)} scanned={scanned}", flush=True)
    out.close()

    print(f"\n=== PDF-era classification ({n} ND opinions) ===")
    print(f"missing PDF on disk:      {missing_pdf}")
    print(f"SCANNED (OCR-required):   {scanned}")
    print(f"  of those WITHOUT a 2nd source (mandatory Westlaw): {scanned_need_wl}")
    print(f"  of those that already have a 2nd source:           {scanned - scanned_need_wl}")
    print(f"born-digital:             {n - scanned - missing_pdf}")
    print("\n--- scanned-needing-Westlaw by year (scanned_total / need_wl) ---")
    for y in sorted(by_year):
        print(f"  {y}: {by_year[y][0]} / {by_year[y][1]}")
    print(f"\nTSV: {OUT}")


if __name__ == "__main__":
    main()
