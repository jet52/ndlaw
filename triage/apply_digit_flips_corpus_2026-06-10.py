"""Apply the print-verified corpus digit-flip corrections.

Verification record (batch of 619 candidates from
triage/digit-flip-candidates-corpus-2026-06-10.tsv):
  * 21-subagent fan-out read every rendered crop (triage/flipverify-corpus/
    verdicts_*.tsv): 581 CONFIRM / 38 UNCLEAR / 0 REJECT.
  * Personal spot-check of a deterministic 10% sample of CONFIRMs: 57/57 agree.
  * All 38 UNCLEARs re-cropped and read personally: 35 CONFIRM, 1 REJECT,
    2 special-cased.

REJECTED (DB correct, PDF text layer wrong — ToUnicode):
  * idx 617: oid 17281 ¶17 footnote marker 1->7 (print: superscript 1)
  (plus the two cohort rejects 16419/16699, pre-excluded at render time)

SPECIAL (print-verified manual fixes, NOT same-length flips): oid 14743 ¶46
quotes the disbursement statute; DB list items read "3." and "4." where the
print reads "10." and "11." (multi-digit OCR loss; the single-flip pairing
proposed 9/9 — wrong). Fixed here with context-anchored replacements.

Same safety gates as triage/apply_digit_flips_2026-06-09.py: per-(oid, ¶,
token) the standalone occurrence count must equal the number of verified
candidate rows (pass-1 guaranteed the db_token does not occur in the PDF ¶
at all). Markdown patched in step. Dry-run default; --apply writes."""
import csv, re, sqlite3, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ndcourts_mcp.db import log_change, log_provenance

BATCH = "digit-flips-corpus-2026-06-10"
REFS = Path.home() / "refs/nd/opin"
MARK = re.compile(r"\[\s*¶\s*(\d+)\s*\]")
REJECT = {(17281, 17, "1", "7"), (16419, 18, "31", "41"), (16699, 16, "09", "01")}
SPECIAL = {(14743, 46, "3", "9"), (14743, 46, "4", "9")}
# context-anchored manual fixes for the SPECIAL rows (print-verified):
MANUAL = [  # (oid, para, old_fragment, new_fragment)
    (14743, 46, "3. The legal fees for publication", "10. The legal fees for publication"),
    (14743, 46, "4. The legal fees of the c", "11. The legal fees of the c"),
]
apply = "--apply" in sys.argv
conn = sqlite3.connect("opinions.db")

cands = list(csv.DictReader(open("triage/digit-flip-candidates-corpus-2026-06-10.tsv"), delimiter="\t"))
groups = {}
for r in cands:
    key = (int(r["oid"]), int(r["para"]), r["db_token"], r["pdf_token"])
    if key in REJECT or key in SPECIAL:
        continue
    groups[key] = groups.get(key, 0) + 1

def para_span(text, n):
    toks = [(m.start(), m.end(), int(m.group(1))) for m in MARK.finditer(text)]
    for j, (s, e, num) in enumerate(toks):
        if num == n:
            return e, (toks[j + 1][0] if j + 1 < len(toks) else len(text))
    return None

by_oid = {}
for (oid, para, db_tok, pdf_tok), cnt in sorted(groups.items()):
    by_oid.setdefault(oid, []).append((para, db_tok, pdf_tok, cnt))

n_fix = 0
skips, applied = [], []
for oid, fixes in sorted(by_oid.items()):
    text, sp = conn.execute(
        "SELECT text_content, source_path FROM opinions WHERE id=?", (oid,)).fetchone()
    new = text
    oid_log = []
    for para, db_tok, pdf_tok, cnt in fixes:
        span = para_span(new, para)
        if not span:
            skips.append((oid, para, db_tok, "no ¶ span")); continue
        s, e = span
        body = new[s:e]
        pat = re.compile(r"(?<!\d)" + re.escape(db_tok) + r"(?!\d)")
        occ = len(pat.findall(body))
        if occ != cnt:
            skips.append((oid, para, db_tok, f"occurrences {occ} != verified {cnt}")); continue
        new = new[:s] + pat.sub(pdf_tok, body) + new[e:]
        oid_log.append((para, db_tok, pdf_tok, cnt))
    # manual context-anchored fixes
    for moid, mpara, old_frag, new_frag in MANUAL:
        if moid != oid:
            continue
        if new.count(old_frag) == 1:
            new = new.replace(old_frag, new_frag)
            oid_log.append((mpara, old_frag[:12], new_frag[:12], 1))
        else:
            skips.append((oid, mpara, old_frag[:20], f"manual fragment count {new.count(old_frag)} != 1"))
    if not oid_log:
        continue
    n_fix += sum(c for *_, c in oid_log)
    applied.append((oid, oid_log))
    if apply:
        conn.execute("UPDATE opinions SET text_content=? WHERE id=?", (new, oid))
        log_change(conn, BATCH, oid, "text_content.digit_flip",
                   "; ".join(f"¶{p}: {a}×{c}" for p, a, b, c in oid_log),
                   "; ".join(f"¶{p}: {b}×{c}" for p, a, b, c in oid_log),
                   authority="analyzer-OCR digit flip; printed glyphs verified (21-agent fan-out + "
                             "10% personal spot-check 57/57 + personal read of all unclears; "
                             "crops in triage/flipverify-corpus/)")
        p = REFS / sp
        if p.exists():
            md = p.read_text()
            md2 = md
            for para, db_tok, pdf_tok, cnt in oid_log:
                if len(db_tok) > 8:
                    continue  # manual fragments handled below
                span = para_span(md2, para)
                if not span:
                    continue
                s, e = span
                body = md2[s:e]
                pat = re.compile(r"(?<!\d)" + re.escape(db_tok) + r"(?!\d)")
                if len(pat.findall(body)) == cnt:
                    md2 = md2[:s] + pat.sub(pdf_tok, body) + md2[e:]
            for moid, mpara, old_frag, new_frag in MANUAL:
                if moid == oid and md2.count(old_frag) == 1:
                    md2 = md2.replace(old_frag, new_frag)
            if md2 != md:
                p.write_text(md2)

print(f"{'APPLIED' if apply else 'DRY RUN'}: {n_fix} token fixes in {len(applied)} opinions; {len(skips)} skips")
for s in skips:
    print("  SKIP", s)
if apply:
    log_provenance(conn, "digit-flips-corpus",
                   command="triage/apply_digit_flips_corpus_2026-06-10.py --apply",
                   rows_affected=len(applied),
                   notes=f"batch {BATCH}; {n_fix} digit fixes in {len(applied)} opinions; "
                         "3 rejects (text-layer ToUnicode), 2 manual list-number fixes (14743)")
    conn.commit()
