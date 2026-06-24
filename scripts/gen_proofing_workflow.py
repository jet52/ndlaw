"""Generate a corpus-proofing Workflow script for a date-descending slice.

Each agent receives: the opinion's DB text (it fetches), its Layer-A structural
report, its era, and the authoritative source for that era. It proofs for
transcription defects, verifies against the source, and returns proposals + flags
(prompt = triage/corpus-proofing-prompt-v2.md, kept in sync here).

Usage: gen_proofing_workflow.py OFFSET LIMIT OUT [--db opinions.db]
"""
import json
import os
import re
import sqlite3
import sys

OFFSET, LIMIT, OUT = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
DB = sys.argv[sys.argv.index("--db") + 1] if "--db" in sys.argv else "opinions.db"
REFS = os.path.expanduser("~/refs/nd/opin")

# Layer-A structural report keyed by opinion id
struct = {}
for ln in open("triage/corpus-structural-report.jsonl"):
    r = json.loads(ln)
    struct[r["id"]] = r["flags"]

con = sqlite3.connect(DB)
_cols = ("SELECT o.id, o.date_filed, "
         "  (SELECT citation FROM citations c WHERE c.opinion_id=o.id ORDER BY is_primary DESC LIMIT 1) cite, "
         "  (SELECT source_path FROM opinion_sources s WHERE s.opinion_id=o.id ORDER BY is_primary DESC LIMIT 1) src "
         "FROM opinions o ")
if "--ids" in sys.argv:
    # re-run a specific id list (e.g. agents the workflow dropped); OFFSET/LIMIT ignored
    ids = [int(x) for x in sys.argv[sys.argv.index("--ids") + 1].split(",")]
    q = f"{_cols} WHERE o.id IN ({','.join('?' * len(ids))})"
    rows = con.execute(q, ids).fetchall()
else:
    rows = con.execute(
        _cols + "WHERE o.text_content IS NOT NULL AND o.text_content<>'' "
        "ORDER BY o.date_filed DESC LIMIT ? OFFSET ?", (LIMIT, OFFSET)).fetchall()


def era_source(cite, year, src):
    """-> (era_label, source_desc, source_access) for the prompt."""
    nd = (cite or "").replace(" ", "")
    pdf = f"{REFS}/pdfs/{year}/{nd}.pdf"
    if year >= 1997 and os.path.exists(pdf):
        return (f"{year} (modern, PDF-authoritative)",
                "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
                f"Extract it:  pdftotext -layout '{pdf}' /tmp/src_{nd}.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '{pdf}' <page>.")
    # older: hand the on-disk source path (reporter markdown / West .doc)
    if src:
        p = src if os.path.isabs(src) else f"{REFS}/{src}"
        kind = ".doc (RTF — Westlaw)" if src.endswith(".doc") else "reporter markdown (OCR of the N.W./N.W.2d scan)"
        return (f"{year} (reporter-era, OCR)",
                f"the {kind} this opinion was ingested from",
                f"Source file: {p} . If a `.doc`, parse footnotes/structure as RTF; if markdown, it is the OCR text — compare carefully, the DB may have diverged from it.")
    return (f"{year}", "no auto-pinned source on disk",
            "No source file is pinned; FLAG anything uncertain rather than propose word/number changes.")


batch = []
for oid, date, cite, src in rows:
    year = int((date or "0")[:4])
    era, sdesc, saccess = era_source(cite, year, src)
    flags = struct.get(oid, {})
    rep = "; ".join(f"{k}: {', '.join(map(str, v))}" for k, v in flags.items()) or "(no structural flags)"
    batch.append({"id": oid, "cite": cite or f"id{oid}", "era": era,
                  "report": rep, "sdesc": sdesc, "saccess": saccess})

BATCH_JS = json.dumps(batch, ensure_ascii=False, indent=1)

SCRIPT = r'''export const meta = {
  name: 'corpus-proofing-__TAG__',
  description: 'Corpus proofing: transcription-fidelity proofread vs authoritative source (propose + flag, never apply)',
  phases: [{ title: 'Proof', detail: 'read-only agent per opinion: source-verified corrections + flags' }],
}

const BATCH = __BATCH__

const SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    opinion_id: { type: 'integer' },
    era: { type: 'string' },
    clean: { type: 'boolean' },
    proposals: { type: 'array', items: {
      type: 'object', additionalProperties: false,
      properties: {
        class: { type: 'string', enum: ['ocr_char','ocr_digit','split_join','whitespace','paragraph_seq','heading_seq','missing_text','caption','other'] },
        old_exact: { type: 'string' },
        new_exact: { type: 'string' },
        verified_count: { type: 'integer' },
        source: { type: 'string' },
        evidence: { type: 'string' },
        confidence: { type: 'string', enum: ['high','medium','low'] },
        note: { type: 'string' },
      },
      required: ['class','old_exact','new_exact','verified_count','source','confidence'],
    } },
    flags: { type: 'array', items: {
      type: 'object', additionalProperties: false,
      properties: {
        class: { type: 'string' },
        location_quote: { type: 'string' },
        description: { type: 'string' },
        confidence: { type: 'string', enum: ['high','medium','low'] },
      },
      required: ['class','location_quote','description'],
    } },
    coverage_note: { type: 'string' },
  },
  required: ['opinion_id','clean','proposals','flags'],
}

phase('Proof')
const results = await parallel(BATCH.map(op => () =>
  agent(
`You are a meticulous transcription proofreader for an AUTHORITATIVE digital edition of North Dakota Supreme Court opinions — a text the Court itself could adopt. Your job is FIDELITY to what the court actually published. You are NOT an editor: never improve, modernize, or correct the court's own writing.

OPINION: ${op.cite} (DB id ${op.id}). Era: ${op.era}.
Get the DB text:  sqlite3 opinions.db "SELECT text_content FROM opinions WHERE id=${op.id}" > /tmp/db_${op.id}.txt  — read it.
Layer-A structural report (LEADS to verify, not facts): ${op.report}
Authoritative source: ${op.sdesc}
${op.saccess}

ABSOLUTE RULES
1. PROPOSE ONLY — you never change anything.
2. FIDELITY, NOT EDITING — fix only where the DB DIVERGES from the printed source (OCR / ingestion / transcription defects). Never touch the court's own grammar, spelling, punctuation, capitalization, or word choice. If the printed source has a typo or archaic spelling, it STAYS.
3. VERIFY THEN PROPOSE — confirm every change against the source; record source + evidence + confidence. If you cannot verify against a source, do NOT propose a word/number change — emit a flag instead.
4. HIGH-RISK = FLAG, NOT FIX — any change to a NUMBER, citation, pinpoint, date, dollar amount, statute/rule number, case name, or party name goes in flags unless the source positively shows BOTH that the DB is wrong AND the correct value.
5. BYTE-EXACT ANCHORS — each proposal is {old_exact,new_exact}; old_exact copied BYTE-FOR-BYTE from /tmp/db_${op.id}.txt (curly quotes “ ” ‘ ’, en/em dashes, \xa0, \n) occurring EXACTLY ONCE. Verify the count with python3 and set verified_count; DROP any whose count != 1.
6. FOOTNOTES are handled by a separate pipeline — do NOT propose footnote edits; only flag a footnote anomaly.
7. PARAGRAPH RESTARTS — a [¶N] restart/repeat (…¶11, ¶1-9, ¶12) is USUALLY the opinion quoting another numbered document (order/statute), NOT duplicated text. Confirm the numbering resumes after the block and the repeated text differs; only flag a restart whose text DUPLICATES the original and never resumes (never auto-fix dedup).
8. FORM-FEED / PAGE FURNITURE — a 0x0C byte (page break) and any running header it precedes (a short case name + "No./Nos./Civil No. <docket>" repeating the caption) are a KNOWN artifact handled by a separate deterministic pass. Do NOT propose removing 0x0C or dropping a running header; ignore them entirely.
9. QUOTE CHARACTERS — the DB uses STRAIGHT ASCII quotes and apostrophes (" and ') by policy; the PDFs use curly/typographic (“ ” ‘ ’). This difference is INTENTIONAL. Do NOT flag or propose any straight-vs-curly quote/apostrophe change. Likewise do NOT propose footnote `[N]`-call or digit-only changes (those are high-risk, handled separately) — flag at most.

ERROR CLASSES (scan for all; tag each): ocr_char (l/1/I, rn/m, cl/d, 0/O, ligatures, £→$, ■), ocr_digit (a wrong digit in PROSE only — citations/dates → flag), split_join (wrongly split/fused word), whitespace (mid-sentence hard break to rejoin; 3+ blank lines to collapse; do not reflow). Whitespace is MECHANICAL ONLY and never inserts a newline to wrap a token across a line. ELLIPSES: ND opinions print the compact four-dot form "...."; if the DB shows a spaced ". . . ." but the PDF shows "....", that spacing is an ingestion artifact — propose the compact form (it will be human-reviewed). Match the source; do not impose Bluebook spacing. paragraph_seq, heading_seq, missing_text (a line/phrase dropped at a page/column break, confirmed in source — propose VERBATIM source text or flag), caption (party-name contamination/smushing), other.

METHOD: read the DB text + report; pull the source; read the flagged regions and skim the rest; classify each candidate FIX (source-confirmed, low-risk) vs FLAG (high-risk/unverifiable/ambiguous); build byte-exact edits; verify count==1. If the opinion is clean, return clean:true (a valuable result). BIAS TO FLAG — a wrong fix corrupts authoritative text; a missed one is caught later.`,
    { label: `${op.cite}`, phase: 'Proof', schema: SCHEMA, agentType: 'Explore' }
  ).then(r => r).catch(() => null)
))

const ok = results.filter(Boolean)
log(`proofing proposals: ${ok.length}/${BATCH.length}`)
return ok
'''

tag = OUT.split("proofing-")[-1].split(".")[0] if "proofing-" in OUT else "batch"
open(OUT, "w").write(SCRIPT.replace("__BATCH__", BATCH_JS).replace("__TAG__", tag))
print(f"wrote {OUT}: {len(batch)} opinions [{OFFSET}:{OFFSET+LIMIT}] "
      f"({batch[0]['cite']} … {batch[-1]['cite']})")
