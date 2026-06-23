export const meta = {
  name: 'footnote-repair-batch2b-skips',
  description: 'Batch 2b: re-propose the 9 gate-skipped opinions with sharpened byte-exact + already-present-orphan guidance',
  phases: [{ title: 'Propose', detail: 'read-only agent per opinion: byte-exact curly-quote anchors, number existing orphans' }],
}

const BATCH = [
  {id:13182,cite:'1999 ND 195',arch:'archive/1999/990034.htm'},
  {id:13218,cite:'2000 ND 158',arch:'archive/2000/990356.htm'},
  {id:13240,cite:'2000 ND 170',arch:'archive/2000/990353.htm'},
  {id:13281,cite:'2000 ND 222',arch:'archive/2000/20000228.htm'},
  {id:13362,cite:'2001 ND 83',arch:'archive/2001/20000286.htm'},
  {id:13408,cite:'2001 ND 127',arch:'archive/2001/20000328.htm'},
  {id:13416,cite:'2001 ND 137',arch:'archive/2001/20000305.htm'},
  {id:13592,cite:'2002 ND 111',arch:'archive/2002/20020013.htm'},
  {id:13657,cite:'2002 ND 164',arch:'archive/2002/20010315.htm'},
]

const SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    opinion_id: { type: 'integer' },
    cite: { type: 'string' },
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
                old_exact: { type: 'string', description: 'byte-exact substring copied from DB text, occurs EXACTLY once' },
                new_exact: { type: 'string', description: 'replacement' },
                verified_count: { type: 'integer', description: 'occurrences of old_exact you measured (must be 1)' },
              },
              required: ['old_exact', 'new_exact', 'verified_count'],
            },
          },
          append_body: { type: 'string', description: 'verbatim full body, ONLY for recover_body_absent' },
          body_present_in_db: { type: 'boolean', description: 'self-check: is a long contiguous run of the body already in the DB?' },
          call_para: { type: ['integer', 'null'] },
          confidence: { type: 'string', enum: ['high', 'medium', 'low'] },
        },
        required: ['num', 'action', 'confidence'],
      },
    },
    conflict: { type: 'string' },
    overall_confidence: { type: 'string', enum: ['high', 'medium', 'low'] },
  },
  required: ['opinion_id', 'footnotes', 'overall_confidence'],
}

const REFS = '/Users/jerod/refs/nd/opin'

phase('Propose')
const results = await parallel(BATCH.map(op => () =>
  agent(
`Produce APPLYABLE footnote-repair edit-pairs for ND opinion ${op.cite} (DB id ${op.id}). Propose only. A prior pass on this opinion was REJECTED by a byte-exact gate — fix that.

Get DB text:  sqlite3 opinions.db "SELECT text_content FROM opinions WHERE id=${op.id}" > /tmp/db_${op.id}.txt   (run from repo cwd). Read it.
Authoritative source: ${REFS}/${op.arch}  — footnote bodies follow the LAST name="FN_N_" anchor.

TWO FAILURE MODES that broke the prior pass — avoid both:
 (1) CURLY QUOTES. This DB uses Unicode curly quotes “ ” ‘ ’, en/em dashes – —, and non-breaking spaces. A call site like (“Connie”)1 will NOT match an ASCII anchor ("Connie")1. Copy old_exact BYTE-FOR-BYTE from /tmp/db_${op.id}.txt including curly glyphs.
 (2) BODIES ARE USUALLY ALREADY PRESENT as UNNUMBERED ORPHANS. Each footnote body typically already sits in the DB as "\\n\\n. <body text>" with NO number. DO NOT use recover_body_absent unless you grep the DB and confirm the body text is genuinely missing. The fix is number_orphan: old_exact="\\n\\n. <body opening>" new_exact="\\n\\nN\\n\\n. <body opening>". If several "\\n\\n. " orphans sit consecutively they are footnotes in order — number them 1,2,3,... matching their call order.

Target state per footnote: inline [N] call at the call site + a numbered body "N\\n\\n. body". ASCII brackets only. Footnotes run 1..N with none skipped.

Per footnote choose ONE action + emit EXACT edits:
- retrofit_bareline_to_bracket / fix_marker: bracket the call digit. old_exact="<curly-exact ...>)N <next>" or "<word>.N <next>"  new_exact same with [N].
- number_orphan: number an existing unnumbered body (see above).
- strip_residual: remove a stray duplicate marker.
- recover_body_absent: ONLY after confirming absence; set append_body + body_present_in_db=false.
- already_clean / not_a_footnote: no edits.

MANDATORY: for every old_exact, measure its count in the DB:
  python3 -c "import sqlite3; t=sqlite3.connect('opinions.db').execute('SELECT text_content FROM opinions WHERE id=${op.id}').fetchone()[0]; print(t.count(r'''<paste old_exact>'''))"
Set verified_count to the measured number. DROP any edit whose count != 1 and re-pick a longer unique BYTE-EXACT anchor. Every edit must be marker-only (changes only brackets/digits/periods/whitespace; identical letters & other punctuation).`,
    { label: `${op.cite}`, phase: 'Propose', schema: SCHEMA, agentType: 'Explore' }
  ).then(r => r).catch(() => null)
))

const ok = results.filter(Boolean)
log(`editpair proposals: ${ok.length}/${BATCH.length}`)
return ok
