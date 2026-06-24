export const meta = {
  name: 'footnote-repair-westdoc-retry2',
  description: 'West .doc footnote repair: bracket calls + number present bodies (ground-truth fn set supplied)',
  phases: [{ title: 'Propose', detail: 'read-only agent per opinion: byte-exact bracket+number edits' }],
}

const BATCH = [
 {
  "id": 8078,
  "cite": "1979 ND 119",
  "fns": [
   {
    "num": 1,
    "hint": "Section 27-13-05, N.D.C.C. , provides: “?An attorney, except as otherwise provided in sections 27-13-06 and 27-13-07, wh"
   },
   {
    "num": 2,
    "hint": "Section 27-14-02, N.D.C.C. , provides, in part: “?The certificate of admission to the bar of this state of an attorney a"
   },
   {
    "num": 3,
    "hint": "Canon 1, DR1-102, Code of Professional Responsibility, provides, in part: “?(A) A lawyer shall not: “?(1) Violate a Disc"
   },
   {
    "num": 4,
    "hint": "Canon 9, DR9-102, Code of Professional Responsibility, provides: “?(A) All funds of clients paid to a lawyer or law firm"
   },
   {
    "num": 5,
    "hint": "In his brief to this court, counsel for Lee stated: “?In view of the fact Respondent, through counsel, has already stipu"
   },
   {
    "num": 6,
    "hint": "Disciplinary Rule 9-102(B)(4) provides, in part, that a lawyer shall: “?(4) Promptly pay or deliver to the client as req"
   },
   {
    "num": 7,
    "hint": "See Secs. 6-08-16 and 6-08-16.2, N.D.C.C."
   }
  ]
 },
 {
  "id": 9338,
  "cite": "1985 ND 40",
  "fns": [
   {
    "num": 1,
    "hint": "“?Indian lands shall remain under the absolute jurisdiction and control of the Congress of the United States.”? Enabling"
   },
   {
    "num": 2,
    "hint": "“?The people inhabiting this state do agree and declare that they forever disclaim all right and title to the unappropri"
   },
   {
    "num": 4,
    "hint": "“?Although much has been said about reservation problems at numerous conferences and meetings, and even on the floors of"
   },
   {
    "num": 5,
    "hint": "“?i. The assumption of civil jurisdiction by the State would provide, among other things, a tool for: 1. Determining the"
   },
   {
    "num": 6,
    "hint": "“?SECTION 1.) In accordance with the provisions of Public Law 280 of the 83rd Congress and Section 203 of the North Dako"
   },
   {
    "num": 7,
    "hint": "“?Marvin Sonosky, 1700 K St., Washington, D.C., representing Standing Rock Indian reservation, spoke against passage of "
   },
   {
    "num": 8,
    "hint": "“?§? 2.) Acceptance of jurisdiction may be by either of the following methods: 1. Upon petition of a majority of the enr"
   },
   {
    "num": 9,
    "hint": "“?All courts shall be open, and every man for any injury done him in his lands, goods, person or reputation shall have r"
   },
   {
    "num": 10,
    "hint": "“?All laws of a general nature shall have a uniform operation.”? N.D. Const. art. I, §? 22 ."
   },
   {
    "num": 11,
    "hint": "“?The district court shall have original jurisdiction of all causes, except as otherwise provided by law, and such appel"
   },
   {
    "num": 12,
    "hint": "“?All persons born or naturalized in the United States, and subject to the jurisdiction thereof, are citizens of the Uni"
   },
   {
    "num": 13,
    "hint": "“?Civil jurisdiction as herein provided over an Indian reservation may be terminated by petition of three-fourths of the"
   }
  ]
 }
]

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
