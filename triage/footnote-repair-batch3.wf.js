export const meta = {
  name: 'footnote-repair-batch3',
  description: 'Batch 3: 30 archive-backed SRC_MORE (incl. batch-1 skips) with sharpened byte-exact + orphan guidance',
  phases: [{ title: 'Propose', detail: 'read-only agent per opinion: byte-exact curly-quote anchors, number existing orphans' }],
}

const BATCH = [
  {id:12401,cite:'1997 ND 43',arch:'archive/1997/960145.htm'},
  {id:12501,cite:'1997 ND 169',arch:'archive/1997/970047.htm'},
  {id:12503,cite:'1997 ND 165',arch:'archive/1997/970052.htm'},
  {id:12520,cite:'1997 ND 176',arch:'archive/1997/960211.htm'},
  {id:12929,cite:'1999 ND 137',arch:'archive/1999/980269.htm'},
  {id:12939,cite:'1999 ND 153',arch:'archive/1999/990096.htm'},
  {id:12940,cite:'1999 ND 143',arch:'archive/1999/980272.htm'},
  {id:12941,cite:'1999 ND 144',arch:'archive/1999/980342.htm'},
  {id:12944,cite:'1999 ND 150',arch:'archive/1999/990020.htm'},
  {id:12946,cite:'1999 ND 151',arch:'archive/1999/990050.htm'},
  {id:13716,cite:'2002 ND 122',arch:'archive/2002/20010148.htm'},
  {id:13791,cite:'2003 ND 74',arch:'archive/2003/20030024.htm'},
  {id:14004,cite:'2004 ND 86',arch:'archive/2004/20030157.htm'},
  {id:14046,cite:'2004 ND 120',arch:'archive/2004/20030337.htm'},
  {id:14322,cite:'2005 ND 146',arch:'archive/2005/20040214.htm'},
  {id:14465,cite:'2006 ND 47',arch:'archive/2006/20050210.htm'},
  {id:14633,cite:'2006 ND 210',arch:'archive/2006/20060063.htm'},
  {id:14647,cite:'2006 ND 228',arch:'archive/2006/20060132.htm'},
  {id:14708,cite:'2007 ND 37',arch:'archive/2007/20060167.htm'},
  {id:14756,cite:'2007 ND 83',arch:'archive/2007/20060256.htm'},
  {id:14785,cite:'2007 ND 111',arch:'archive/2007/20060341.htm'},
  {id:14888,cite:'2008 ND 9',arch:'archive/2008/20070123.htm'},
  {id:15299,cite:'2009 ND 189',arch:'archive/2009/20080350.htm'},
  {id:15490,cite:'2010 ND 155',arch:'archive/2010/20090392.htm'},
  {id:15496,cite:'2010 ND 172',arch:'archive/2010/20100006.htm'},
  {id:15509,cite:'2010 ND 196',arch:'archive/2010/20090285.htm'},
  {id:15533,cite:'2010 ND 218',arch:'archive/2010/20090318.htm'},
  {id:15536,cite:'2010 ND 215',arch:'archive/2010/20100156.htm'},
  {id:15546,cite:'2010 ND 227',arch:'archive/2010/20090260.htm'},
  {id:15558,cite:'2010 ND 247',arch:'archive/2010/20100116.htm'},
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
`Produce APPLYABLE footnote-repair edit-pairs for ND opinion ${op.cite} (DB id ${op.id}). Propose only. Self-verify every anchor byte-exact.

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
