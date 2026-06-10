"""Corpus-wide digit-flip measurement pass (read-only).

Generalizes triage/digit_compare_2026-06-09.py + digit_flip_candidates_* from
the 226-opinion cohort to EVERY analyzer-era opinion (source_path under
markdown/) with a court PDF. Per ¶ present in both DB text and PDF
extraction, compares ordered digit-token sequences; for mismatched ¶s,
emits context-matched single-digit-flip candidates (same-length tokens, one
digit position differs, ±12-char context matches, DB token absent from the
PDF ¶ entirely).

Output:
  triage/digit-flip-candidates-corpus-2026-06-10.tsv  (verification worklist)
  stdout summary (opinions scanned / ¶s compared / raw mismatches / candidates)

Multiprocessing over PDFs; each worker opens its own read-only DB connection.
"""
import csv, re, sqlite3, sys
from multiprocessing import Pool
from pathlib import Path

MARK = re.compile(r"\[\s*¶\s*(\d+)\s*\]")
DIGITS = re.compile(r"\d+")
PDF_ROOT = Path.home() / "refs/nd/opin/pdfs"

def para_map(text):
    toks = [(m.start(), m.end(), int(m.group(1))) for m in MARK.finditer(text)]
    out = {}
    for j, (s, e, n) in enumerate(toks):
        end = toks[j + 1][0] if j + 1 < len(toks) else len(text)
        out.setdefault(n, text[e:end])
    return out

def norm(s):
    return re.sub(r"\s+", " ", s)

def toks_ctx(body, w=25):
    return [(m.group(), norm(body[max(0, m.start()-w):m.start()]), norm(body[m.end():m.end()+w]))
            for m in DIGITS.finditer(body)]

def flip(a, b):
    return len(a) == len(b) and sum(x != y for x, y in zip(a, b)) == 1

def scan(job):
    oid, year, num = job
    from pdfminer.high_level import extract_text
    pdf = PDF_ROOT / f"{year}/{year}ND{num}.pdf"
    if not pdf.exists():
        return (oid, "NO_PDF", 0, 0, [])
    conn = sqlite3.connect("file:opinions.db?mode=ro", uri=True)
    text = conn.execute("SELECT text_content FROM opinions WHERE id=?", (oid,)).fetchone()[0]
    conn.close()
    try:
        pt = extract_text(str(pdf))
    except Exception:
        return (oid, "PDF_ERR", 0, 0, [])
    pt = re.sub(r"\n\s*\d+\s*\n\s*\x0c", "\n", pt)  # page footers
    db_map, pdf_map = para_map(text), para_map(pt)
    n_para = n_mism = 0
    cands = []
    for n in sorted(set(db_map) & set(pdf_map)):
        d_db = DIGITS.findall(db_map[n])
        d_pdf = DIGITS.findall(pdf_map[n])
        n_para += 1
        if d_db == d_pdf:
            continue
        n_mism += 1
        dt = toks_ctx(db_map[n])
        ptk = toks_ctx(pdf_map[n])
        pdf_set = {t[0] for t in ptk}
        db_set = {t[0] for t in dt}
        for tok, pre, post in dt:
            if tok in pdf_set:
                continue
            for ptok, ppre, ppost in ptk:
                if ptok in db_set:
                    continue
                if flip(tok, ptok) and (pre[-12:] == ppre[-12:] or post[:12] == ppost[:12]):
                    cands.append((oid, f"{year}ND{num}", n, tok, ptok,
                                  f"...{pre[-30:]}[{tok}->{ptok}]{post[:30]}..."))
                    break
    return (oid, "OK", n_para, n_mism, cands)

def main():
    conn = sqlite3.connect("file:opinions.db?mode=ro", uri=True)
    jobs = []
    for oid, sp in conn.execute(
            "SELECT id, source_path FROM opinions WHERE source_path LIKE 'markdown/%'"):
        m = re.search(r"(\d{4})ND(\d+)\.md$", sp)
        if m:
            jobs.append((oid, m.group(1), int(m.group(2))))
    conn.close()
    print(f"{len(jobs)} analyzer-era opinions to scan", flush=True)

    total_para = total_mism = 0
    status = {"OK": 0, "NO_PDF": 0, "PDF_ERR": 0}
    all_cands = []
    with Pool(10) as pool:
        for i, (oid, st, n_para, n_mism, cands) in enumerate(
                pool.imap_unordered(scan, jobs, chunksize=20)):
            status[st] += 1
            total_para += n_para
            total_mism += n_mism
            all_cands.extend(cands)
            if (i + 1) % 500 == 0:
                print(f"...{i+1}/{len(jobs)} | paras={total_para} mism={total_mism} "
                      f"cands={len(all_cands)}", flush=True)

    all_cands.sort()
    w = csv.writer(open("triage/digit-flip-candidates-corpus-2026-06-10.tsv", "w"),
                   delimiter="\t", lineterminator="\n")
    w.writerow(["oid", "cite", "para", "db_token", "pdf_token", "context"])
    w.writerows(all_cands)
    print(f"\nDONE: {status} | {total_para} ¶s compared | {total_mism} raw-mismatch ¶s | "
          f"{len(all_cands)} flip candidates in {len({c[0] for c in all_cands})} opinions "
          f"-> triage/digit-flip-candidates-corpus-2026-06-10.tsv", flush=True)

if __name__ == "__main__":
    main()
