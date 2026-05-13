"""Triage 50 westlaw+NW pairs in 0.50-0.70 similarity band.

For each pair classify as:
  WRONG_PAIRING — case_name/parties disagree → Westlaw .doc is a different case
  TRUNCATION   — one side has substantially less body (e.g., NW <50% of westlaw)
  OCR_NOISE    — case_name matches, lengths comparable, just OCR shingle drift
  CONTAMINATION — case_name on CL row matches but the NW md's frontmatter parallel cites
                  reference a different opinion (the cross-contamination pattern)
  UNCLEAR      — needs human review
"""
import csv, re, sqlite3, sys, pathlib

REFS = pathlib.Path('/Users/jerod/refs/nd/opin')
DB   = '/Users/jerod/code/ndcourts-mcp/opinions.db'

def normalize_name(s):
    s = s.lower()
    s = re.sub(r'[^a-z0-9 ]+', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    # collapse common variants
    s = s.replace(' et al', '').replace(' inc', '').replace(' co', '')
    return s

def parties(name):
    name = name.lower()
    if ' v. ' in name: a,b = name.split(' v. ', 1)
    elif ' v ' in name: a,b = name.split(' v ', 1)
    elif ' vs ' in name: a,b = name.split(' vs ', 1)
    else: return (name, '')
    return (normalize_name(a), normalize_name(b))

def split_body(text):
    # remove yaml frontmatter
    if text.startswith('---'):
        end = text.find('\n---', 3)
        if end > 0: text = text[end+4:]
    # heuristic: strip the leading title/citation header in CL markdown
    return text

def word_count(text):
    return len(re.findall(r'\b\w+\b', split_body(text)))

def fingerprint(text, n=300):
    """Extract a representative substring for visual comparison."""
    body = split_body(text)
    # strip frontmatter-like trailing pieces and find first paragraph of real prose
    body = re.sub(r'^\s*#.*$', '', body, flags=re.M)  # strip md headings
    body = re.sub(r'^\s*[A-Z][A-Z., ]+\s*$', '', body, flags=re.M)  # ALL CAPS title lines
    body = re.sub(r'\s+', ' ', body).strip()
    return body[:n]

def parse_frontmatter(md_text):
    if not md_text.startswith('---'): return {}
    end = md_text.find('\n---', 3)
    if end < 0: return {}
    fm = md_text[3:end]
    out = {}
    for line in fm.splitlines():
        m = re.match(r'^\s*(\w+):\s*"?([^"]*)"?\s*$', line)
        if m: out[m.group(1)] = m.group(2).strip()
    # citations list
    cites = re.findall(r'^\s*-\s*"([^"]+)"', fm, re.M)
    if cites: out['citations'] = cites
    return out

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

results = []
with open('/tmp/sample50.csv') as f:
    rdr = csv.DictReader(f)
    for r in rdr:
        oid = int(r['oid'])
        sec_path = r['sec_path']
        sim = float(r['sim'])
        p_words = int(r['p_words'])
        s_words = int(r['s_words'])

        db = conn.execute('SELECT case_name, text_content FROM opinions WHERE id=?', (oid,)).fetchone()
        if not db:
            results.append((oid, 'UNCLEAR', 'no DB row', sim, p_words, s_words, r['case_name'], ''))
            continue

        md_path = REFS / sec_path
        if not md_path.exists():
            results.append((oid, 'UNCLEAR', f'missing {md_path}', sim, p_words, s_words, db['case_name'], ''))
            continue
        md_text = md_path.read_text()
        fm = parse_frontmatter(md_text)

        # parties match
        p_db = parties(db['case_name'])
        p_md = parties(fm.get('title', ''))
        name_match = (p_db[0] and p_db[0] in p_md[0] + ' ' + p_md[1]) or \
                     (p_md[0] and p_md[0] in p_db[0] + ' ' + p_db[1]) or \
                     (p_db == p_md)

        # parallel-cite cross-check: csv citation should be in markdown's frontmatter cites
        csv_cite = r['citation']
        # filename-derived cite isn't always exact (NW/100/1084_2.md); skip filename-only mismatches
        # by deriving the volume/page from the path
        _m = re.match(r'NW2?d?/(\d+)/(\d+)(?:_\d+)?\.md', sec_path)
        derived_cite = f"{_m.group(1)} N.W. {_m.group(2)}" if _m else csv_cite
        md_cites = fm.get('citations', [])
        cite_match = any(csv_cite.replace(' ', '') == c.replace(' ', '') for c in md_cites)

        # primary fingerprint vs secondary fingerprint
        fp_db = fingerprint(db['text_content'])
        fp_md = fingerprint(md_text)

        # also check the markdown's first 50 prose words
        md_words = re.findall(r'\b\w+\b', split_body(md_text).lower())
        db_words = re.findall(r'\b\w+\b', split_body(db['text_content']).lower())

        # Are first ~30 content words overlapping?
        # (CL md starts with title; westlaw starts with frontmatter that we already stripped)
        # Skip the obvious header tokens
        md_skip = {'mathias','versus','vs','v','court','citations','-','---','title','full','date','filed','court','north','dakota','supreme'}
        md_real = [w for w in md_words if w not in md_skip][:60]
        db_real = [w for w in db_words if w not in md_skip][:60]
        overlap = len(set(md_real) & set(db_real))

        # truncation
        wr = s_words / max(p_words, 1)

        # classify
        if not name_match:
            cat = 'WRONG_PAIRING'
            note = f'db="{db["case_name"]}" md="{fm.get("title","")}"'
        elif not cite_match:
            cat = 'CONTAMINATION_CANDIDATE'
            note = f'csv_cite={csv_cite} md_cites={md_cites}'
        elif wr < 0.50:
            cat = 'TRUNCATION'
            note = f'wr={wr:.2f}'
        elif overlap < 8 and wr < 0.80:
            cat = 'UNCLEAR'
            note = f'overlap={overlap}/60 wr={wr:.2f}'
        else:
            cat = 'OCR_NOISE'
            note = f'overlap={overlap}/60 wr={wr:.2f}'

        results.append((oid, cat, note, sim, p_words, s_words, db['case_name'], fm.get('title','')))

# print
from collections import Counter
counts = Counter(r[1] for r in results)
print('=== Distribution ===')
for cat, n in sorted(counts.items(), key=lambda x: -x[1]):
    print(f'  {cat:25s} {n}')
print()
print('=== Sample detail ===')
for r in sorted(results, key=lambda x: (x[1], x[3])):
    print(f'oid={r[0]:5d}  sim={r[3]:.3f}  pw={r[4]:5d} sw={r[5]:5d}  {r[1]:25s}  {r[6][:50]:50s}  {r[2]}')
