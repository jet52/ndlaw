#!/usr/bin/env python3
"""Prep the multi-agent redline campaign: for each single-amendment modern
provision not yet reconstructed, resolve its CAA, locate the measure page(s),
render to PNG, and emit per-agent batch files."""
import json, re, subprocess, sqlite3, importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
PNG = HERE / "png"; PNG.mkdir(exist_ok=True)
spec = importlib.util.spec_from_file_location(
    "recon", HERE.parent.parent / "scripts" / "reconstruct_modern_versions.py")
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
DB = "/tmp/const-scratch.db"
NBATCH = 9


def find_pages(pdf, roman, sec):
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
    m = re.search(r"Pages:\s+(\d+)", info); pages = int(m.group(1)) if m else 30
    if pages > 100:
        return "GIANT"   # whole-session PDF (2400+ pp); locate separately
    pat = re.compile(rf"section\s+{re.escape(sec)}\s+of\s+article\s+{roman}\b", re.I)
    crt = re.compile(rf"(section|article)\s+{re.escape(sec)}\s+of\s+(the\s+)?(north dakota|article {roman})", re.I)
    for pg in range(1, pages + 1):
        out = subprocess.run(["pdftotext", "-layout", "-f", str(pg), "-l", str(pg),
                              str(pdf), "-"], capture_output=True, text=True).stdout
        if (pat.search(out) or crt.search(out)) and re.search(r"as follows|created and enacted", out, re.I):
            # render this page + next (measures often span 2 pages)
            return [pg, min(pg + 1, pages)]
    return None


def render(pdf, pg, slug):
    # mutool draw flattens AcroForm field text (these session-law PDFs store body
    # text in form-field XObjects that pdftoppm/pdftotext DROP — leaving only the
    # strike/underline rules). Found by the agent team 2026-06-14.
    dest = PNG / f"{slug}-p{pg}.png"
    r = subprocess.run(["mutool", "draw", "-r", "200", "-o", str(dest),
                        str(pdf), str(pg)], capture_output=True)
    if dest.exists():
        return str(dest)
    # fallback to pdftoppm if mutool absent
    subprocess.run(["pdftoppm", "-png", "-r", "200", "-f", str(pg), "-l", str(pg),
                    str(pdf), str(PNG / f"{slug}-p{pg}")], capture_output=True)
    hits = sorted(PNG.glob(f"{slug}-p{pg}*.png"))
    return str(hits[0]) if hits else None


def main():
    con = sqlite3.connect(DB)
    rows = con.execute("""
        SELECT p.id, p.citation, v.text_content,
          (SELECT min(a.effective_date) FROM amendments a WHERE a.provision_id=p.id AND a.effective_date>='1981-01-01'),
          (SELECT count(*) FROM amendments a WHERE a.provision_id=p.id AND a.effective_date>='1981-01-01'),
          EXISTS(SELECT 1 FROM provision_versions vv WHERE vv.provision_id=p.id AND vv.batch LIKE 'modern-versions%')
        FROM provisions p JOIN provision_versions v ON v.id=p.current_version_id
        WHERE p.corpus='const' AND p.citation LIKE '%art.%' AND p.citation NOT LIKE '%amend%'
    """).fetchall()
    tasks, skipped = [], []
    for pid, cite, cur, d1, namd, done in rows:
        if not namd or namd > 1 or done:
            continue
        a = con.execute("SELECT amendment_number, source_url FROM amendments WHERE provision_id=? AND effective_date=?",
                        (pid, d1)).fetchone()
        num, url = (a or (None, None))
        m = re.search(r"art\.\s+([IVXL]+),\s+§\s+(\d+)", cite)
        roman, sec = m.group(1), m.group(2)
        pdf = R.resolve_pdf(url) if url else None
        pages = find_pages(pdf, roman, sec) if pdf else None
        if pages == "GIANT":
            skipped.append({"citation": cite, "amendment_date": d1, "number": num,
                            "source_url": url, "reason": "giant-session-pdf"})
            continue
        if not pages:
            skipped.append({"citation": cite, "amendment_date": d1, "number": num,
                            "source_url": url, "reason": "page-not-located"})
            continue
        slug = cite.replace("N.D. Const. ", "").replace(" ", "").replace(",", "").replace("§", "s")
        pngs = [render(pdf, pg, slug) for pg in pages]
        pngs = [p for p in pngs if p]
        hint = subprocess.run(["pdftotext", "-layout", "-f", str(pages[0]), "-l", str(pages[-1]),
                               str(pdf), "-"], capture_output=True, text=True).stdout[:4000]
        tasks.append({"citation": cite, "amendment_date": d1, "amendment_number": num,
                      "source_url": url, "current_text": " ".join(cur.split()),
                      "png_paths": pngs, "pdftext_hint": hint})
    con.close()

    # split into NBATCH agent batches (round-robin for even load)
    batches = [[] for _ in range(NBATCH)]
    for i, t in enumerate(tasks):
        batches[i % NBATCH].append(t)
    for i, b in enumerate(batches, 1):
        (HERE / f"batch-{i}.json").write_text(json.dumps(b, ensure_ascii=False, indent=2))
    (HERE / "skipped.json").write_text(json.dumps(skipped, ensure_ascii=False, indent=2))
    print(f"prepped {len(tasks)} provisions across {NBATCH} batches; "
          f"{len(skipped)} skipped (page-not-located)")
    for i, b in enumerate(batches, 1):
        print(f"  batch-{i}: {len(b)} provisions -> {[t['citation'].replace('N.D. Const. ','') for t in b]}")


if __name__ == "__main__":
    main()
