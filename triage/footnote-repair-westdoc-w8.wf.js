export const meta = {
  name: 'footnote-repair-westdoc-w8',
  description: 'West .doc footnote repair: bracket calls + number present bodies (ground-truth fn set supplied)',
  phases: [{ title: 'Propose', detail: 'read-only agent per opinion: byte-exact bracket+number edits' }],
}

const BATCH = [
 {
  "id": 12187,
  "cite": "1996 ND 103",
  "fns": [
   {
    "num": 1,
    "hint": "Because this matter was pending when the North Dakota Rules for Lawyer Discipline (NDRLD) became effective on January 1,"
   }
  ]
 },
 {
  "id": 12242,
  "cite": "1996 ND 157",
  "fns": [
   {
    "num": 1,
    "hint": "Chapter 30.1–?05, N.D.C.C. was repealed effective January 1, 1996, and replaced by a new chapter 30.1–?05. See 1993 N.D."
   }
  ]
 },
 {
  "id": 12245,
  "cite": "1996 ND 138",
  "fns": [
   {
    "num": 1,
    "hint": "This is a companion appeal to Criminal No. 960010, In Interest of C.R.M., 552 N.W.2d 324 (N.D.1996) ."
   }
  ]
 },
 {
  "id": 12247,
  "cite": "1996 ND 139",
  "fns": [
   {
    "num": 1,
    "hint": "This case is a companion to Criminal No. 960008, In Interest of J.A.G., 552 N.W.2d 317 (N.D.1996) ."
   },
   {
    "num": 2,
    "hint": "C.R.M. also relies on Eastburn v. J.K.H., 392 N.W.2d 406 (N.D.1986) , which relied on P.W.N. for the proposition that re"
   },
   {
    "num": 3,
    "hint": "Our conclusion is in accord with the decisions of at least one of the other states to enact the Uniform Juvenile Court A"
   }
  ]
 },
 {
  "id": 12256,
  "cite": "1996 ND 155",
  "fns": [
   {
    "num": 1,
    "hint": "The names used in this opinion are pseudonyms."
   },
   {
    "num": 2,
    "hint": "Section 14–?17–?04, N.D.C.C ., provides: “?1. A man is presumed to be the natural father of a child if: “?a. He and the "
   },
   {
    "num": 3,
    "hint": "But cf. West Virginia ex rel. Allen v. Stone, 196 W.Va. 624, 474 S.E.2d 554 (1996) [biological father has state constitu"
   },
   {
    "num": 4,
    "hint": "The prior law allowed a court in a paternity action to award “?reasonable fees of counsel ... to be paid by the parties "
   }
  ]
 },
 {
  "id": 12304,
  "cite": "1996 ND 196",
  "fns": [
   {
    "num": 1,
    "hint": "In 1994, this statute provided in relevant part: “?A person ... who is an heir, devisee, person succeeding to a renounce"
   }
  ]
 },
 {
  "id": 12319,
  "cite": "1996 ND 210",
  "fns": [
   {
    "num": 1,
    "hint": "The Share House is a facility in Fargo, similar to a halfway house, that combines residential programming with intense o"
   }
  ]
 },
 {
  "id": 12333,
  "cite": "1996 ND 228",
  "fns": [
   {
    "num": 1,
    "hint": "Section 27–?20–?34, N.D.C.C ., was amended during the 1995 Legislative Assembly. Due to the amendments, the language ori"
   },
   {
    "num": 2,
    "hint": "In 1995, our legislature enacted similar guidelines: “?In determining a childs amenability to treatment and rehabilitati"
   }
  ]
 },
 {
  "id": 19372,
  "cite": "2019 ND 204",
  "fns": [
   {
    "num": 1,
    "hint": "A court should avoid prejudging a motion before it has been made. See Dunn v. N.D. Dept of Transp. , 2010 ND 41, ¶? 12, "
   }
  ]
 },
 {
  "id": 19516,
  "cite": "2020 ND 202",
  "fns": [
   {
    "num": 1,
    "hint": "Five percent of the estimate is roughly $182,665."
   },
   {
    "num": 2,
    "hint": "More than 6.75% of the total costs."
   },
   {
    "num": 3,
    "hint": "The City defines benefit equal to cost, whether or not it assesses total cost less 5% or total cost less 6.75%. Majority"
   }
  ]
 },
 {
  "id": 19688,
  "cite": "2022 ND 214",
  "fns": [
   {
    "num": 1,
    "hint": "The district court reduced the marital estate by $91,125 to reflect the amount that William Fercho paid from his non-mar"
   },
   {
    "num": 2,
    "hint": "The courts reduction of the marital estate by $91,125 resulted in William Fercho effectively paying for a portion of thi"
   }
  ]
 },
 {
  "id": 19804,
  "cite": "2023 ND 231",
  "fns": [
   {
    "num": 1,
    "hint": "Bearce also argued on appeal that the district courts original sentence was illegal as contemplated by N.D.R.Crim.P. 35("
   }
  ]
 },
 {
  "id": 20486,
  "cite": "1984 ND 183",
  "fns": [
   {
    "num": 1,
    "hint": "The availability of Rule 10(g) agreed statements needs to be noted by every member of the bar who is or may be involved "
   },
   {
    "num": 2,
    "hint": "Rule 35 permits “?correction”? of a sentence at any time and reduction of a sentence within 120 days after it is imposed"
   },
   {
    "num": 3,
    "hint": "Correcting the record is permitted under Rule 36 at any time."
   },
   {
    "num": 4,
    "hint": "We said in State v. Rueb, 249 N.W.2d 506, 511 (N.D.1976) that procedures to reduce a sentence under Rules 35 , 47 and 49"
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
