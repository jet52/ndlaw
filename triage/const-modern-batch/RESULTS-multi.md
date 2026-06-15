# Multi-amendment chain wave — results (2026-06-14)

The 22 modern provisions amended >1× since 1981 need a version CHAIN, not a single
redline. `prep_multi.py` renders EACH amendment's measure per provision; 6 chain-
agents reconstructed them; `splice_multichain.py` verified + spliced.

## Chain model
Each amendment's measure is a redline of THAT amendment only. Walk latest→earliest:
the latest amendment's "version_after" must equal current DB text; reverse each
amendment's redline to get the version before it; the next-earlier amendment's
"after" must equal it (continuity); STOP at a CREATE (chain head = created text,
no earlier version); a carried-from-1981 provision's earliest reversal yields the
[1981, d1) head, gated vs the 1981 Blue Book.

## Verification gates (splice_multichain.py)
MECH (reverse_edit_list applies, anchors unique) · LATEST (latest after == current,
DokuWiki `<WRAP>`/`])]` artifacts stripped) · CONTINUITY (each link connects) ·
HEAD-BB (carried heads vs 1981 BB where the article is clean) · DISCONTINUITY guard.

## Result — 12 of 14 chains spliced (scratch). Modern reconstructed 22 → 34. Integrity 0/0.

**Created (head = create date, no [1981,d1) — 8):**
- art IV §13 — created 1985, REDLINE 1987, REDLINE 1992 (3 ver)
- art VII §8 — created 1982 (with all of art VII), REDLINE 1998, REDLINE 2002 (3 ver)
- art IV §3 / §4 / §5 / §6 — each created 1985-86 (legislative-article recreation),
  one later REDLINE (1997/1997/2016/2012) (2 ver each)
- art X §24 — created 1995, REDLINE 2016 (2 ver)
- art V §5 — created 1997 (executive-article replacement), REDLINE 2000 (2 ver)

**Carried-from-1981 (head reconstructed to 1981 — 4):**
- art X §5 — head[1981] **BB-NEAR(0.99)** (independent witness), REDLINE 1988, REDLINE 2003
- art I §16 — REDLINE 1982, REDLINE 2006 (head: no-clean-BB-witness → needs-2nd-read)
- art IX §1 — REDLINE 1982, REDLINE 2009 (head: no-clean-BB-witness → needs-2nd-read)
- art IX §2 — REDLINE 1982, REDLINE 2009 (head: no-clean-BB-witness → needs-2nd-read)

## Skipped (2 discontinuities — NOT spliced; current stays single-version)
- **art V §1, art V §12** — the agents caught that the 1997 measure CREATED a new
  art V section while the earlier 1986 amendment amends the OLD, now-REPEALED §1/§12
  (different lineage). Splicing the 1986 amendment into the current section would
  corrupt the timeline. Current = single create-1997 version; **needs-base-source**
  for the pre-1997 old-§1/§12 text (and the old sections belong to the repealed-
  predecessor lineage, not the current cite).

## Deferred (not in this wave)
- **art XVI §1-5, art IX §13 (6)** — 2024 amendments. Data issue surfaced: bill-doc
  23-3092 (DB-linked to amend 167 / art XVI) actually amends **art X §26** (legacy
  fund). The 2024 `source_url`/`affected` mappings need review before reconstruction.
  Downloaded bill PDFs are cached (`caa-cache/billdoc_23-30{15,92}-0*.pdf`).
- **art VIII §6** — heavy multi-subsection; native source (PL-SOURCE-FILES).

## Addendum 2026-06-14 — art X §26 (Legacy Fund) reconstructed
After the 2024 amendment-data fix made art X §26 a proper 2-amendment provision
(created 2011 HCR 3054, amended 2024 HCR 3033), it was reconstructed via
`splice_x26_2011.py`. Because §26 is a *created* provision, the [2011,2024) head =
the 2011-enacted text transcribed verbatim from the on-disk creation measure (a
clean CREATE reprint — no redline reversal). Gate: the unchanged subsection 3
("Statutory programs…") is byte-identical between the 2011 text and current, and
every 2024 change was cross-validated against the 2024 redline (fifteen→five
percent; "may not be expended until after June 30, 2017"→"may be expended, but";
"principal of the North Dakota legacy fund"→"moneys in the legacy fund"; subsec
4./5. numbers added 2024). 2 versions, integrity 0. **Modern reconstructed 34 → 35.**

## Still owed before live
Carried heads without a BB witness (art I §16, IX §1, IX §2) and all single-read
chain intervals want a confirming second read; then a modern snapshot-diff. The
art X §5 head is BB-witnessed. Modern stays scratch-only.
