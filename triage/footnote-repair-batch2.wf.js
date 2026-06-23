export const meta = {
  name: 'footnote-repair-batch2-editpairs',
  description: 'Batch 2: exact edit-pair footnote repair proposals (archive-backed SRC_MORE, self-verified, propose-only)',
  phases: [{ title: 'Propose', detail: 'read-only agent per opinion: emit verified old->new edit pairs + append bodies' }],
}

const BATCH = [
  {id:12958,cite:'1999 ND 173',arch:'archive/1999/990027.htm'},
  {id:12959,cite:'1999 ND 170',arch:'archive/1999/990017.htm'},
  {id:12960,cite:'1999 ND 166',arch:'archive/1999/980345.htm'},
  {id:12961,cite:'1999 ND 168',arch:'archive/1999/990029.htm'},
  {id:12962,cite:'1999 ND 172',arch:'archive/1999/990010.htm'},
  {id:12964,cite:'1999 ND 129',arch:'archive/1999/990031.htm'},
  {id:13010,cite:'1999 ND 195',arch:'archive/1999/990034.htm'},
  {id:13024,cite:'1999 ND 221',arch:'archive/1999/990175.htm'},
  {id:13034,cite:'1999 ND 214',arch:'archive/1999/990218.htm'},
  {id:13182,cite:'2000 ND 121',arch:'archive/2000/990255.htm'},
  {id:13213,cite:'2000 ND 161',arch:'archive/2000/20000024.htm'},
  {id:13218,cite:'2000 ND 158',arch:'archive/2000/990356.htm'},
  {id:13234,cite:'2000 ND 174',arch:'archive/2000/20000248.htm'},
  {id:13240,cite:'2000 ND 170',arch:'archive/2000/990353.htm'},
  {id:13281,cite:'2000 ND 222',arch:'archive/2000/20000228.htm'},
  {id:13323,cite:'2001 ND 37',arch:'archive/2001/20000119.htm'},
  {id:13351,cite:'2001 ND 71',arch:'archive/2001/20000234.htm'},
  {id:13362,cite:'2001 ND 83',arch:'archive/2001/20000286.htm'},
  {id:13383,cite:'2001 ND 102',arch:'archive/2001/20000364.htm'},
  {id:13408,cite:'2001 ND 127',arch:'archive/2001/20000328.htm'},
  {id:13416,cite:'2001 ND 137',arch:'archive/2001/20000305.htm'},
  {id:13430,cite:'2001 ND 143',arch:'archive/2001/20000278.htm'},
  {id:13466,cite:'2001 ND 183',arch:'archive/2001/20010098.htm'},
  {id:13487,cite:'2001 ND 205',arch:'archive/2001/20010194.htm'},
  {id:13497,cite:'2002 ND 9',arch:'archive/2002/20010200.htm'},
  {id:13499,cite:'2002 ND 6',arch:'archive/2002/20010160.htm'},
  {id:13592,cite:'2002 ND 111',arch:'archive/2002/20020013.htm'},
  {id:13654,cite:'2002 ND 154',arch:'archive/2002/20020228.htm'},
  {id:13657,cite:'2002 ND 164',arch:'archive/2002/20010315.htm'},
  {id:13686,cite:'2002 ND 188',arch:'archive/2002/20020078.htm'},
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
`Produce APPLYABLE footnote-repair edit-pairs for ND opinion ${op.cite} (DB id ${op.id}). Propose only.

Get DB text:  sqlite3 opinions.db "SELECT text_content FROM opinions WHERE id=${op.id}" > /tmp/db_${op.id}.txt   (run from repo cwd). Read it.
Authoritative source: ${REFS}/${op.arch}  — footnote bodies follow the LAST name="FN_N_" anchor; calls are <sup>(N)</sup> mapped to DB [¶N] markers.

Target state per footnote: a numbered period body "N\\n\\n. body" the parser reads + an inline [N] call. ASCII only. Footnotes run 1..N.

For each footnote, choose ONE action and emit the EXACT edits to reach the target:
- fix_marker / number_orphan / retrofit_bareline_to_bracket / strip_residual: give edits[] as {old_exact, new_exact} where old_exact is copied BYTE-FOR-BYTE from the DB text (include curly quotes ""'', en-dashes –, non-breaking spaces, and \\n newlines exactly) and occurs EXACTLY ONCE.
  * number a dropped body: old_exact="\\n\\n. <body opening>"  new_exact="\\n\\nN\\n\\n. <body opening>"
  * bracket an attached call digit: old_exact="<word>.N <next>"  new_exact="<word>.[N] <next>"
  * fix a body marker: old_exact=".Nbody" or ".In"  new_exact="N\\n\\n. body" or ". In"
- recover_body_absent: ONLY if the body is truly not in the DB. Set append_body=<full verbatim body from source>, body_present_in_db=false, and (if a call digit is attached) one bracket edit for the call. If you find a long contiguous run of the body already in the DB, it is NOT absent — use fix_marker/number_orphan instead and set body_present_in_db=true.
- already_clean / not_a_footnote: no edits.

MANDATORY self-verification for every old_exact: run
  python3 -c "import sqlite3; t=sqlite3.connect('opinions.db').execute('SELECT text_content FROM opinions WHERE id=${op.id}').fetchone()[0]; import sys; print(t.count(open('/tmp/oe_${op.id}.txt').read()))"
or equivalent, and set verified_count to the measured count. DROP any edit whose old_exact count != 1 (re-pick a longer unique anchor). Do not guess.

If the DB has MORE footnote bodies than the source, or numbering disagrees, set conflict + overall_confidence=low and propose a renumber, not a blind insert. Verbatim-match bodies.`,
    { label: `${op.cite}`, phase: 'Propose', schema: SCHEMA, agentType: 'Explore' }
  ).then(r => r).catch(() => null)
))

const ok = results.filter(Boolean)
log(`editpair proposals: ${ok.length}/${BATCH.length}`)
return ok
