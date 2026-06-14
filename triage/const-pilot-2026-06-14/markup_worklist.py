#!/usr/bin/env python3
"""Generate the Claude-direct-read worklist for redline (markup) measures in
phase-1 scope. For each amendment of each markup provision, locate the page that
reprints the section, isolate it to a single-page PDF, and emit a worklist row.

Output: isolated PDFs under markup-pages/, and worklist.tsv.
"""
import importlib.util, re, subprocess, sqlite3, csv
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "recon", HERE.parent.parent / "scripts" / "reconstruct_modern_versions.py")
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)

OUT = HERE / "markup-pages"; OUT.mkdir(exist_ok=True)


def find_page(pdf, roman, sec):
    n = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
    m = re.search(r"Pages:\s+(\d+)", n); pages = int(m.group(1)) if m else 30
    pat = re.compile(rf"section\s+{re.escape(sec)}\s+of\s+article\s+{roman}\b", re.I)
    for pg in range(1, pages + 1):
        out = subprocess.run(["pdftotext", "-layout", "-f", str(pg), "-l", str(pg),
                              str(pdf), "-"], capture_output=True, text=True).stdout
        if pat.search(out) and re.search(r"as follows:", out, re.I):
            return pg
    return None


def main():
    con = sqlite3.connect("/tmp/const-scratch.db")
    scope = {p["cite"]: p for p in R.load_scope(con).values()}
    rows = []
    for cite, p in scope.items():
        if not R.is_pure_single(p) or p["text"].strip().lower().startswith("repealed"):
            continue
        roman, sec = R.parse_cite(cite)
        if not roman:
            continue
        last = p["amds"][-1]["eff"]
        pdf = R.resolve_pdf(p["amds"][-1]["url"])
        latest_cls = "LOCATE_FAIL"
        if pdf:
            ex = R.extract_reenact(R.pdftext(pdf), roman, sec)
            latest_cls = "LOCATE_FAIL" if ex is None else R.classify(ex, p["text"])
        if latest_cls in ("CLEAN", "LOCATE_FAIL"):
            continue  # clean = pdftotext path; locate_fail = out of phase-1
        # markup provision — isolate every amendment page
        slug = cite.replace("N.D. Const. ", "").replace(" ", "").replace(",", "").replace("§", "s")
        for a in p["amds"]:
            pdf = R.resolve_pdf(a["url"])
            if not pdf:
                rows.append((cite, a["num"], a["eff"], "NO_PDF", "", len(R.tokens(p["text"]))))
                continue
            pg = find_page(pdf, roman, sec)
            if not pg:
                rows.append((cite, a["num"], a["eff"], "NO_PAGE", str(pdf), len(R.tokens(p["text"]))))
                continue
            dest = OUT / f"{slug}-{a['eff']}-{a['num']}.pdf"
            subprocess.run(["qpdf", str(pdf), "--pages", ".", str(pg), "--", str(dest)],
                           capture_output=True)
            rows.append((cite, a["num"], a["eff"], f"p{pg}", dest.name,
                         len(R.tokens(p["text"]))))
    with open(HERE / "worklist.tsv", "w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["cite", "amendment", "eff_date", "page", "isolated_pdf", "current_tok"])
        w.writerows(rows)
    print(f"markup provisions → {len({r[0] for r in rows})}; pages to read → "
          f"{sum(1 for r in rows if r[3].startswith('p'))}")
    for r in rows:
        print(f"  {r[0]:<26} {r[1] or '?':<7} {r[2]}  {r[3]:<10} {r[4]}")


if __name__ == "__main__":
    main()
