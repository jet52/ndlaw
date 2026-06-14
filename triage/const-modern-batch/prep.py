#!/usr/bin/env python3
"""Prep the multi-agent redline campaign (v2): for each single-amendment modern
provision not yet reconstructed, resolve its CAA/IMA/INITM PDF, choose the
measure page(s), render to PNG, and emit per-agent batch files.

v2 changes (2026-06-14, after Wave 1 prep bugs):
- Locate by the source_url's `#page=N` anchor (or render the whole file when it
  is small) instead of a pdftotext content-scan. These session-law PDFs store
  body text in AcroForm field XObjects that pdftotext DROPS, so the scan blanked
  and 44/51 provisions fell to 'page-not-located'. mutool draw flattens the
  fields, so we render and let the visual-reading agents locate the section.
- resolve_pdf now honors the exact source_url filename (IMA/INITM vs CAA).
- Render cache keyed by (pdf, page) so provisions sharing one multi-section
  measure (e.g. art IV §1-8) reuse renders; those provisions are kept in the
  same batch so one agent reads the measure once.
"""
import json, re, subprocess, sqlite3, importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
PNG = HERE / "png"; PNG.mkdir(exist_ok=True)
spec = importlib.util.spec_from_file_location(
    "recon", HERE.parent.parent / "scripts" / "reconstruct_modern_versions.py")
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
DB = "/tmp/const-scratch.db"
NBATCH = 8
SMALL_PP = 12        # render every page of files this size or smaller
GIANT_PP = 60        # never scan/render whole-file beyond this without an anchor
DPI = "200"

_render_cache: dict[tuple, str] = {}


def page_count(pdf):
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
    m = re.search(r"Pages:\s+(\d+)", info)
    return int(m.group(1)) if m else 1


def choose_pages(pdf, url, n_sections):
    """Return a list of 1-based page numbers to render, or None to skip.

    Small file  -> all pages (cheap, removes the locating problem entirely).
    Large file  -> a window around the #page anchor sized to the measure.
    No anchor + large -> None (skip; caller records the reason)."""
    pages = page_count(pdf)
    if pages <= SMALL_PP:
        return list(range(1, pages + 1))
    am = re.search(r"#page=(\d+)", url or "")
    if am and pages <= GIANT_PP:
        n = int(am.group(1))
        span = 3 + (max(1, n_sections) - 1)        # cover multi-section reprints
        lo, hi = max(1, n - 1), min(pages, n + span)
        return list(range(lo, hi + 1))
    return None


def render(pdf, pg):
    """Render one page to PNG via mutool (flattens AcroForm body text that
    pdftoppm/pdftotext drop). Cached by (pdf, page) so shared measures render
    once."""
    key = (str(pdf), pg)
    if key in _render_cache:
        return _render_cache[key]
    # Slug must be unique per SOURCE FILE: many sessions name the file CAA.pdf, so
    # stem alone collides (1985 CAA vs 1991 CAA). Prefix with the session dir.
    slug = re.sub(r"[^A-Za-z0-9]", "", f"{pdf.parent.name}_{pdf.stem}") or "pdf"
    dest = PNG / f"{slug}-p{pg:02d}.png"
    subprocess.run(["mutool", "draw", "-r", DPI, "-o", str(dest), str(pdf), str(pg)],
                   capture_output=True)
    if not dest.exists():   # fallback to pdftoppm
        subprocess.run(["pdftoppm", "-png", "-r", DPI, "-f", str(pg), "-l", str(pg),
                        str(pdf), str(PNG / f"{slug}-p{pg:02d}")], capture_output=True)
        hits = sorted(PNG.glob(f"{slug}-p{pg:02d}*.png"))
        dest = hits[0] if hits else None
    out = str(dest) if dest and Path(dest).exists() else None
    _render_cache[key] = out
    return out


def main():
    con = sqlite3.connect(DB)
    rows = con.execute("""
        SELECT p.id, p.citation, v.text_content,
          (SELECT min(a.effective_date) FROM amendments a WHERE a.provision_id=p.id AND a.effective_date>='1981-01-01'),
          (SELECT count(*) FROM amendments a WHERE a.provision_id=p.id AND a.effective_date>='1981-01-01'),
          EXISTS(SELECT 1 FROM provision_versions vv WHERE vv.provision_id=p.id
                 AND (vv.batch LIKE 'modern-versions%' OR vv.batch LIKE 'modern-redline%'))
        FROM provisions p JOIN provision_versions v ON v.id=p.current_version_id
        WHERE p.corpus='const' AND p.citation LIKE '%art.%' AND p.citation NOT LIKE '%amend%'
    """).fetchall()

    tasks, skipped = [], []
    for pid, cite, cur, d1, namd, done in rows:
        if not namd or namd > 1 or done:
            continue
        a = con.execute("SELECT amendment_number, source_url, affected, raw FROM amendments "
                        "WHERE provision_id=? AND effective_date=?", (pid, d1)).fetchone()
        num, url, affected, raw = (a or (None, None, None, None))
        n_sections = (affected or "").count(";") + 1
        measure_sections = [s.strip() for s in (affected or "").split(";") if s.strip()]
        pdf = R.resolve_pdf(url) if url else None
        if not pdf:
            skipped.append({"citation": cite, "amendment_date": d1, "number": num,
                            "source_url": url, "reason": "pdf-unresolved"}); continue
        pgs = choose_pages(pdf, url, n_sections)
        if not pgs:
            skipped.append({"citation": cite, "amendment_date": d1, "number": num,
                            "source_url": url, "reason": "giant-no-anchor"}); continue
        pngs = [p for p in (render(pdf, pg) for pg in pgs) if p]
        if not pngs:
            skipped.append({"citation": cite, "amendment_date": d1, "number": num,
                            "source_url": url, "reason": "render-failed"}); continue
        hint = subprocess.run(["pdftotext", "-layout", str(pdf), "-"],
                              capture_output=True, text=True).stdout[:3000]
        tasks.append({"citation": cite, "amendment_date": d1, "amendment_number": num,
                      "source_url": url, "pdf": pdf.name, "measure_group": f"{pdf.stem}:{num}",
                      "n_affected_sections": n_sections, "measure_sections": measure_sections,
                      "current_text": " ".join(cur.split()), "page_numbers": pgs,
                      "png_paths": pngs, "pdftext_hint": hint})
    con.close()

    # Keep a measure together (one agent reads it once), then balance across batches.
    groups: dict[str, list] = {}
    for t in tasks:
        groups.setdefault(t["measure_group"], []).append(t)
    batches = [[] for _ in range(NBATCH)]
    for i, g in enumerate(sorted(groups.values(), key=len, reverse=True)):
        # assign each measure-group to the currently-lightest batch
        b = min(range(NBATCH), key=lambda j: len(batches[j]))
        batches[b].extend(g)
    for i, b in enumerate(batches, 1):
        (HERE / f"wave2-batch-{i}.json").write_text(json.dumps(b, ensure_ascii=False, indent=2))
    (HERE / "skipped-wave2.json").write_text(json.dumps(skipped, ensure_ascii=False, indent=2))

    print(f"prepped {len(tasks)} provisions in {len(groups)} measure-groups "
          f"across {NBATCH} batches; {len(skipped)} skipped")
    from collections import Counter
    print("  skip reasons:", dict(Counter(s["reason"] for s in skipped)))
    for i, b in enumerate(batches, 1):
        cs = [t["citation"].replace("N.D. Const. ", "") for t in b]
        print(f"  wave2-batch-{i}: {len(b)} -> {cs}")
    if skipped:
        print("\n  skipped:")
        for s in skipped:
            print(f"    {s['reason']:16} {s['citation'].replace('N.D. Const. ','')}")


if __name__ == "__main__":
    main()
