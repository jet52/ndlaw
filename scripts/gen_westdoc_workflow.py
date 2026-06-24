"""Generate a self-contained West-doc footnote-repair Workflow script for a slice
of triage/westdoc-footnote-sets.json. Usage: gen_westdoc_workflow.py START END OUT
"""
import json
import sys

START, END, OUT = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
data = json.load(open("triage/westdoc-footnote-sets.json"))[START:END]

# embed per-opinion footnote hints as a JS object literal via JSON
batch_js = json.dumps(
    [{"id": d["id"], "cite": d["cite"],
      "fns": [{"num": f["num"], "hint": f["body_prefix"]} for f in d["footnotes"]]}
     for d in data], ensure_ascii=False, indent=1)

SCRIPT = r'''export const meta = {
  name: 'footnote-repair-westdoc-__TAG__',
  description: 'West .doc footnote repair: bracket calls + number present bodies (ground-truth fn set supplied)',
  phases: [{ title: 'Propose', detail: 'read-only agent per opinion: byte-exact bracket+number edits' }],
}

const BATCH = __BATCH__

const SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    opinion_id: { type: 'integer' },
    footnotes: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        properties: {
          num: { type: 'integer' },
          action: { type: 'string', enum: ['already_clean', 'fix_marker', 'number_orphan', 'recover_body_absent', 'retrofit_bareline_to_bracket', 'strip_residual', 'not_a_footnote'] },
          edits: {
            type: 'array',
            items: {
              type: 'object', additionalProperties: false,
              properties: {
                old_exact: { type: 'string' },
                new_exact: { type: 'string' },
                verified_count: { type: 'integer' },
              },
              required: ['old_exact', 'new_exact', 'verified_count'],
            },
          },
          append_body: { type: 'string' },
          body_present_in_db: { type: 'boolean' },
          call_para: { type: ['integer', 'null'] },
          confidence: { type: 'string', enum: ['high', 'medium', 'low'] },
        },
        required: ['num', 'action', 'confidence'],
      },
    },
    overall_confidence: { type: 'string', enum: ['high', 'medium', 'low'] },
  },
  required: ['opinion_id', 'footnotes', 'overall_confidence'],
}

phase('Propose')
const results = await parallel(BATCH.map(op => () =>
  agent(
`Produce APPLYABLE footnote-repair edit-pairs for ND opinion ${op.cite} (DB id ${op.id}). Propose only.

This opinion's AUTHORITATIVE footnote set (extracted from the Westlaw source .doc) is:
${op.fns.map(f => `  [${f.num}] ${f.hint}`).join('\n')}

Get DB text:  sqlite3 opinions.db "SELECT text_content FROM opinions WHERE id=${op.id}" > /tmp/db_${op.id}.txt   (run from repo cwd). Read it.

In the DB these footnote BODIES are PRESENT inline but UNMARKED (the parser detects 0). Each body
sits after its calling paragraph, usually as a bare-line "\\n\\xa0N\\n\\n<body>" or "\\n\\n. <body>" or
"\\nN\\n\\n<body>" (\\xa0 = non-breaking space). The call digit N usually survives attached to a word
("word.N " or "wordN "). For each footnote above, locate the body (search its hint text) and the call.

Target state per footnote: inline [N] call at the call site + a numbered period body "N\\n\\n. body".
ASCII brackets only. Number every footnote 1..N.

Per footnote emit EXACT marker-only edits (change ONLY brackets/digits/periods/whitespace; identical
letters & other punctuation), each old_exact copied BYTE-FOR-BYTE from /tmp/db (incl. curly quotes
" " ' ', en-dashes, \\xa0, \\n) and occurring EXACTLY ONCE:
- retrofit_bareline_to_bracket / fix_marker: bracket the call digit. old_exact="<word>.N <next>" or
  "<word>N <next>"  new_exact same with [N].
- number_orphan: number the present body. old_exact="\\n\\xa0N\\n\\n<open>" or "\\n\\n. <open>" or
  "\\nN\\n\\n<open>"  new_exact="\\n\\nN\\n\\n. <open>" (strip the nbsp, ensure "N\\n\\n. ").
- recover_body_absent: ONLY if the body truly is NOT in the DB (you searched the hint and it is absent).
  Set append_body=<full verbatim body> (use the .doc text; if you only have the 120-char hint, say so
  and set confidence=low), body_present_in_db=false.
- already_clean / not_a_footnote: no edits.

MANDATORY self-verification for every old_exact: run
  python3 -c "import sqlite3; t=sqlite3.connect('opinions.db').execute('SELECT text_content FROM opinions WHERE id=${op.id}').fetchone()[0]; print(t.count(open('/tmp/oe.txt').read()))"
and set verified_count to the measured count. DROP any edit whose count != 1; re-pick a longer unique
BYTE-EXACT anchor. Do not guess. Prefer number_orphan over recover_body_absent — the bodies are
almost always already present.`,
    { label: `${op.cite}`, phase: 'Propose', schema: SCHEMA, agentType: 'Explore' }
  ).then(r => r).catch(() => null)
))

const ok = results.filter(Boolean)
log(`westdoc proposals: ${ok.length}/${BATCH.length}`)
return ok
'''

tag = OUT.split("westdoc-")[-1].split(".")[0] if "westdoc-" in OUT else "batch"
out = SCRIPT.replace("__BATCH__", batch_js).replace("__TAG__", tag)
open(OUT, "w").write(out)
print(f"wrote {OUT}: {len(data)} opinions [{START}:{END}]")
