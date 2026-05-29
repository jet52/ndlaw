# Citation-graph audit — 50 random opinions, last 3 years (2026-05-29)

## Method
- Population: 731 opinions with `date_filed` in 2023-05-29..2026-05-29.
- Sample: 50, reproducibly drawn (`select_sample.py`, seed 20260529); ids in `sample.json`.
- Each opinion's FULL text was read (5 parallel auditors, 10 each) and compared against the
  stored forward citations (`text_citations` = "cases cited") and reverse edges
  (`cited_by` = "cited by"). Per-case structured findings are in the agent transcripts.
- Headline counts were re-verified independently in SQL over the same 50 ids and corpus-wide.

## Aggregate (50-case sample; 1,326 forward cites audited)
| Pattern | Sample | Corpus-wide |
|---|---|---|
| Self-citation (case lists its own cite as authority) | 49/50 cases, 54 rows | **31,331 rows, 19,759 opinions** |
| Jurisdiction mistag: N.W.x ND case tagged non-`nd` | 433 cites | **110,164 cites** |
| Antecedent NULL on case-cites | 37/50 opinions all-NULL; 0 fully populated | **95% of case-cites; only 1,767/19,788 opinions have ANY** |
| Reporter-truncation phantoms (F./So./etc.) | 8 | **1,022** |
| Parallel-cite duplication (neutral + N.W. as 2 rows) | pervasive | `parallel_group` filled on only 127,752/339,822 |
| Genuine omissions (statute/rule/constitution/foreign) | ~20 | n/a (read-only detectable) |
| **cited_by reverse-edge errors** | **0** | 0 self-edges |

## Findings, ranked

### 1. Self-citation false positive — HIGH severity, corpus-wide
Every opinion's own neutral cite (and often its N.W. parallel), printed in the caption/header,
is extracted as an authority it "cites." 31,331 rows across essentially all 19,759 opinions;
49/50 in the sample. `get_cited_authorities` resolves these back to the case itself, so the
tool shows each case citing itself.
- **Root cause:** `cite_extract` scans the whole `text_content` including the caption block; no
  exclusion of the opinion's own citations.
- **Durable fix:** in `cite_extract`, drop any extracted cite whose normalized form matches a row
  in `citations` for the same `opinion_id` (and/or skip the caption region). One-time cleanup:
  delete the 31,331 self-cite rows (logged batch). `cited_by` already excludes self-edges (0), so
  this is forward-only.

### 2. No dedup by resolved opinion in get_cited_authorities — HIGH severity, tool layer
`server.py:get_cited_authorities` emits one entry per `text_citations` row. A case cited by both
its neutral and N.W. cite resolves to the **same `oid` twice** → listed twice in `nd_cases`.
Combined with #1, the "cases cited" list is materially inflated.
- **Durable fix (cheapest, immediate):** dedupe `nd_cases` by `oid` (and exclude the subject
  opinion's own `oid`). This neutralizes both #1 and the user-facing half of #5 server-side,
  without re-extraction.

### 3. Antecedent-name coverage + correctness — MEDIUM-HIGH, corpus-wide
`antecedent_name` (the party name powering cited_by shared-page disambiguation and the
"cases cited" display) is NULL for 95% of case-cites; only ~9% of opinions have any. Where
populated, it is frequently the wrong span: corporate suffix only (`Inc.` 483, `LLC` 118,
`L.P.`, `P.C.`, `Co.`, `Corp.`), a stray leading `In ` (~214, distinct from legitimate `In re`
1,140), a tail jurisdiction word (`Divide Cnty.`), or a cross-sentence fragment
(`AAPA. See Kasprowicz v. Finck`, `Walsh County Recorder. See State v. Cleavenger`).
- **Root cause:** (a) coverage — `cite_extract` was run with the antecedent-capable jetcite
  (≥2.1.0) on only ~1,767 opinions; (b) correctness — jetcite's antecedent span logic stops at a
  corporate suffix, includes leading connectors, and crosses sentence boundaries.
- **Durable fix:** (a) re-run `cite_extract` corpus-wide once jetcite is fixed; (b) jetcite:
  consume the full party-name run (don't terminate on Inc./LLC/L.P./Co./Corp./N.A./P.C.), strip
  leading connectors (`In `, `See `, `Cf. `, `e.g., ` — but KEEP `In re`/`In the Matter of`/
  `Interest of`), and never capture across a sentence boundary.

### 4. Reporter-truncation phantoms — MEDIUM, corpus-wide
`419 F.2d 1197` → phantom `419 F. 2` (reporter "F." + series digit as page; real page lost);
same for `So.2d/So.3d` (`892 So. 2`), `F.4th` (`43 F.4`). The correct full cite is usually stored
too, so each phantom is a pure false positive plus data loss. 1,022 corpus-wide; 8/8 in sample.
- **Root cause:** jetcite tokenizes the reporter-series suffix as the page.
- **Durable fix:** jetcite reporter table must treat `F.2d/F.3d/F.4th`, `So.2d/So.3d`,
  `N.E.2d/3d`, `P.2d/3d`, etc. as atomic reporter tokens. Cleanup: delete phantom rows where a
  correct sibling exists; else re-extract.

### 5. Parallel-cite duplication — MEDIUM, by-design but unmanaged
Modern ND cases are cited as "2024 ND 110, ¶ X, 7 N.W.3d 253" and stored as two rows. The
`parallel_group` column exists for this but is filled on only 38% of rows, and
`get_cited_authorities` ignores it. Recording each cite string is defensible; showing/counting
the case twice is not.
- **Durable fix:** dedup by `oid` at the tool layer (#2 covers the resolved case); for unresolved
  parallels, populate `parallel_group` during extraction (cites sharing a pin-cite run) and
  collapse groups in the tool.

### 6. Recognizer omissions — MEDIUM/LOW, jetcite gaps
Genuine omissions were rare and clustered in forms jetcite doesn't recognize:
- **Constitutional prose:** "the Sixth Amendment of the United States Constitution",
  "Article I, § 12 of the North Dakota Constitution" missed (formal `U.S. Const. amend. VI` is
  caught). Seen in 18247, 19853, 19909, 19983.
- **Statute lists/ranges:** "§§ 28-01-07 and 28-01-08" captures only the first
  (19856; also 19880 §§ 9-03-04/-24; 20191 §§ 29-32.1-09.1/-12).
- **Rules in prose:** "Rule 11 of the North Dakota Rules of Criminal Procedure" (20151),
  "Rules of Appellate Procedure 28 and 30" (20180), "Rule of Criminal Procedure 29" (20315).
- **Foreign authorities:** California codes/case (20325), `150 Idaho 664` (18195) — lower priority.
- **N.W. parallel of a cited case:** `778 N.W.2d 786` (20180) — neutral was captured.
- **Durable fix:** extend jetcite recognizers for spelled-out constitutional refs, section
  lists/ranges, and prose rule references.

### 7. cited_by integrity — CLEAN
Across all 50 cases, every reverse edge post-dates its target and is plausible; no predating or
spurious edges; 0 self-edges corpus-wide. The defects are confined to the **forward extraction
layer**, not the reverse graph. (cited_by completeness is bounded by forward extraction in the
*citing* opinions, so the recognizer omissions in #6 are the only thing that can silently shrink
cited_by — case-cite omissions were ~0.)

## Recommended sequence
1. **Tool-layer dedup** (#2) — one server change; immediately fixes the user-facing self-cite +
   parallel double-listing for the whole corpus. No data migration.
2. **Self-cite cleanup** (#1) — delete own-cite rows in `cite_extract`, logged batch; add the
   exclusion guard so it can't recur.
3. **Jurisdiction backfill** (#1-jur) — set `jurisdiction='nd'` for N.W.x cites resolving to an
   ND opinion (110,164 rows); leave unresolved N.W. as-is.
4. **jetcite fixes** (#3b, #4, #6) — atomic reporter tokens, antecedent span logic, recognizer
   gaps — then a single corpus-wide `cite_extract` re-run (#3a) to backfill antecedents and clear
   truncation phantoms.

All data changes go through the `changelog` table + CHANGELOG-data.md per project policy.
