"""Pass 3: residual digit-divergence sweep with looser pairing, corpus-wide.

The single-flip layer is closed (digit-flips-corpus-2026-06-10), so what
remains in DB-vs-PDF digit mismatches is noise plus the multi-digit class
the single-flip pairing could not propose (e.g. printed "10." read as "3.";
"108"->"103"+"258"->"253" adjacent pairs partially caught). Candidate rules,
all requiring BOTH pre and post ±12-char context to match (stricter than
pass 2's either/or, to offset the looser token rule):
  * same length, 2 differing digit positions
  * length differs by 1 with a common prefix or suffix of len-1
DB token must be absent from the PDF ¶ and vice versa.

Output triage/digit-flip-pass3-candidates-2026-06-10.tsv. Read-only.
"""
import csv, re, sqlite3
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

def loose_pair(a, b):
    if a == b:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) == 2
    if abs(len(a) - len(b)) == 1:
        short, long_ = (a, b) if len(a) < len(b) else (b, a)
        return long_.startswith(short) or long_.endswith(short) or len(short) >= 2 and (
            long_[:len(short)-1] == short[:len(short)-1] or long_[-(len(short)-1):] == short[-(len(short)-1):])
    return False

def scan(job):
    oid, year, num = job
    from pdfminer.high_level import extract_text
    pdf = PDF_ROOT / f"{year}/{year}ND{num}.pdf"
    if not pdf.exists():
        return []
    conn = sqlite3.connect("file:opinions.db?mode=ro", uri=True)
    text = conn.execute("SELECT text_content FROM opinions WHERE id=?", (oid,)).fetchone()[0]
    conn.close()
    try:
        pt = extract_text(str(pdf))
    except Exception:
        return []
    pt = re.sub(r"\n\s*\d+\s*\n\s*\x0c", "\n", pt)
    db_map, pdf_map = para_map(text), para_map(pt)
    cands = []
    for n in sorted(set(db_map) & set(pdf_map)):
        d_db = DIGITS.findall(db_map[n])
        d_pdf = DIGITS.findall(pdf_map[n])
        if d_db == d_pdf:
            continue
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
                if loose_pair(tok, ptok) and pre[-12:] == ppre[-12:] and post[:12] == ppost[:12]:
                    cands.append((oid, f"{year}ND{num}", n, tok, ptok,
                                  f"...{pre[-30:]}[{tok}->{ptok}]{post[:30]}..."))
                    break
    return cands

def main():
    conn = sqlite3.connect("file:opinions.db?mode=ro", uri=True)
    jobs = []
    for oid, sp in conn.execute(
            "SELECT id, source_path FROM opinions WHERE source_path LIKE 'markdown/%'"):
        m = re.search(r"(\d{4})ND(\d+)\.md$", sp)
        if m:
            jobs.append((oid, m.group(1), int(m.group(2))))
    conn.close()
    print(f"{len(jobs)} opinions", flush=True)
    all_cands = []
    with Pool(10) as pool:
        for i, cands in enumerate(pool.imap_unordered(scan, jobs, chunksize=20)):
            all_cands.extend(cands)
            if (i + 1) % 1000 == 0:
                print(f"...{i+1}/{len(jobs)} cands={len(all_cands)}", flush=True)
    all_cands.sort()
    w = csv.writer(open("triage/digit-flip-pass3-candidates-2026-06-10.tsv", "w"),
                   delimiter="\t", lineterminator="\n")
    w.writerow(["oid", "cite", "para", "db_token", "pdf_token", "context"])
    w.writerows(all_cands)
    print(f"DONE: {len(all_cands)} pass-3 candidates in {len({c[0] for c in all_cands})} opinions", flush=True)

if __name__ == "__main__":
    main()
