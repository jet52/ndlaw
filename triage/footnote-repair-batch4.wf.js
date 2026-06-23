export const meta = {
  name: 'footnote-repair-batch4',
  description: 'Batch 4: final 43 archive-backed SRC_MORE (enhanced nbsp/curly guidance)',
  phases: [{ title: 'Propose', detail: 'read-only agent per opinion: byte-exact curly-quote anchors, number existing orphans' }],
}

const BATCH = [
  {id:14322,cite:'2005 ND 146',arch:'archive/2005/20040214.htm'},
  {id:15563,cite:'2011 ND 10',arch:'archive/2011/20100246.htm'},
  {id:15574,cite:'2011 ND 35',arch:'archive/2011/20100235.htm'},
  {id:15579,cite:'2011 ND 24',arch:'archive/2011/20100133.htm'},
  {id:15580,cite:'2011 ND 31',arch:'archive/2011/20100149.htm'},
  {id:15591,cite:'2011 ND 53',arch:'archive/2011/20100147.htm'},
  {id:15595,cite:'2011 ND 65',arch:'archive/2011/20100198.htm'},
  {id:15601,cite:'2011 ND 54',arch:'archive/2011/20100257.htm'},
  {id:15610,cite:'2011 ND 68',arch:'archive/2011/20100101.htm'},
  {id:15685,cite:'2011 ND 134',arch:'archive/2011/20100264.htm'},
  {id:15687,cite:'2011 ND 141',arch:'archive/2011/20100354.htm'},
  {id:15705,cite:'2011 ND 155',arch:'archive/2011/20100364.htm'},
  {id:15709,cite:'2011 ND 166',arch:'archive/2011/20110020.htm'},
  {id:15736,cite:'2011 ND 200',arch:'archive/2011/20100410.htm'},
  {id:15758,cite:'2011 ND 229',arch:'archive/2011/20110030.htm'},
  {id:15798,cite:'2012 ND 33',arch:'archive/2012/20110131.htm'},
  {id:15799,cite:'2012 ND 37',arch:'archive/2012/20110158.htm'},
  {id:15844,cite:'2012 ND 104',arch:'archive/2012/20110212.htm'},
  {id:15860,cite:'2012 ND 114',arch:'archive/2012/20110172.htm'},
  {id:15866,cite:'2012 ND 144',arch:'archive/2012/20110171.htm'},
  {id:15870,cite:'2012 ND 141',arch:'archive/2012/20110320.htm'},
  {id:15887,cite:'2012 ND 152',arch:'archive/2012/20120018.htm'},
  {id:15911,cite:'2012 ND 167',arch:'archive/2012/20120076.htm'},
  {id:15912,cite:'2012 ND 165',arch:'archive/2012/20120113.htm'},
  {id:15920,cite:'2012 ND 179',arch:'archive/2012/20110332.htm'},
  {id:15922,cite:'2012 ND 183',arch:'archive/2012/20120013.htm'},
  {id:15923,cite:'2012 ND 182',arch:'archive/2012/20120080.htm'},
  {id:15947,cite:'2012 ND 229',arch:'archive/2012/20110312.htm'},
  {id:15949,cite:'2012 ND 225',arch:'archive/2012/20110345.htm'},
  {id:15951,cite:'2012 ND 228',arch:'archive/2012/20120134.htm'},
  {id:15967,cite:'2012 ND 253',arch:'archive/2012/20120069.htm'},
  {id:15984,cite:'2013 ND 14',arch:'archive/2013/20120111.htm'},
  {id:15993,cite:'2013 ND 27',arch:'archive/2013/20120285.htm'},
  {id:16007,cite:'2013 ND 34',arch:'archive/2013/20120272.htm'},
  {id:16008,cite:'2013 ND 35',arch:'archive/2013/20120279.htm'},
  {id:16040,cite:'2013 ND 78',arch:'archive/2013/20120239.htm'},
  {id:16097,cite:'2013 ND 151',arch:'archive/2013/20130017.htm'},
  {id:16106,cite:'2013 ND 154',arch:'archive/2013/20130059.htm'},
  {id:16360,cite:'2014 ND 197',arch:'archive/2014/20130259.htm'},
  {id:16634,cite:'2015 ND 298',arch:'archive/2015/20150200.htm'},
  {id:16751,cite:'2016 ND 142',arch:'archive/2016/20150255.htm'},
  {id:16842,cite:'2017 ND 30',arch:'archive/2017/20140133.htm'},
  {id:16928,cite:'2017 ND 117',arch:'archive/2017/20160103.htm'},
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
 (3) BARE-LINE / NBSP BODIES. Some bodies sit as "\n\xa0N\n\nbody" — a NON-BREAKING SPACE (\xa0, shows as a space) then the number, blank line, then body text WITH NO PERIOD. The parser will NOT detect these. Transform to "\n\nN\n\n. body": old_exact="\n\xa0N\n\n<body opening>" (copy the \xa0 byte-exact from /tmp/db) new_exact="\n\nN\n\n. <body opening>". Likewise a body that opens with no leading "." must GET a ". " after the number.
 (2b) BODIES ARE USUALLY ALREADY PRESENT as UNNUMBERED ORPHANS. Each footnote body typically already sits in the DB as "\\n\\n. <body text>" with NO number. DO NOT use recover_body_absent unless you grep the DB and confirm the body text is genuinely missing. The fix is number_orphan: old_exact="\\n\\n. <body opening>" new_exact="\\n\\nN\\n\\n. <body opening>". If several "\\n\\n. " orphans sit consecutively they are footnotes in order — number them 1,2,3,... matching their call order.

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
