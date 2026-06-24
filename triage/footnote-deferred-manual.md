# Footnote corpus pass — deferred for manual review

These archive-backed opinions have footnotes **present but parser-unindexed**
(not lost — citation-graph detector stays 175/0). They were skipped by the gated
applier because their structure is ambiguous enough that an automated number/call
mapping risks corrupting authoritative text. Each needs a careful per-PDF/per-
archive read.

| id | cite | why deferred |
|----|------|--------------|
| 12939 | 1999 ND 153 | 4 real footnotes but fn3 body is an inline block-quote at the call site while others are detached orphans; 3 stray West key-number residue markers `[13][14][15]` interleaved with `[¶N]`. Body→number mapping not safe to automate. |
| 12940 | 1999 ND 143 | 22-footnote opinion; calls fn12/13/19 have no detectable matching body (already-clean vs absent unclear); agent also proposed a false-absent dup body for fn23 (gate blocked). Needs full manual reconciliation. |
| 13716 | 2002 ND 122 | 2 footnotes in `\n\xa0N\n\n` bare-line form, but the call digit did not survive in the text and the DB paragraph flow diverges from the archive — call placement ambiguous. |
| 12401 | 1997 ND 43 | 6-footnote bare-line opinion incl. a table-mangled fn2 (`48,000.00 ... 2`); the known comma→period over-correction case. Bodies present; numbering needs manual care. |
| 15799 | 2012 ND 37 | engine src_nums=1 but the DB carries **two** `\n\n. ` orphan bodies (one is likely main text); call survives only for fn1. Can't disambiguate which orphan is the footnote without a close read. |
| 16360 | 2014 ND 197 | dissent footnote with OCR garble (`(cid:54)õ`, mangled spacing) at both the call (`”).1`) and body opener; not safe to bracket/number mechanically. |
| 16928 | 2017 ND 117 | majority + dissent each with their own footnote stream (src_nums=1,2); agent proposed a `recover_body_absent` **append** whose text isn't confirmable as a missing body. Appending unverified text to authoritative text is the wrong default — needs a manual per-PDF read. |

**False positive (no action):** 16751 (2016 ND 142) — the archive extractor misread the
repeated page-header caption ("Bjorneby v. Nodak Mutual… 2016 ND 142…") as a footnote
body; the opinion has no footnotes. Stays `SRC_MORE` in the engine output but is clean.

Verify sources: `~/refs/nd/opin/archive/<year>/<docket>.htm` (FN_N_ anchors mark
call sites, not bodies) + court PDFs `~/refs/nd/opin/pdfs/<year>/<cite>.pdf`.

## West-doc footnote residue (manual) — 20 opinions, added 2026-06-24

After the 223-opinion West-doc sweep (W1-W8) + two consolidated re-passes,
**203/223 resolved (91%)**. These 20 (1978-1988) persistently skipped — mostly
high-footnote-count opinions (1986 ND 104 = 21 fn, 1979 ND 30 / 1985 ND 40 = 12)
where the agents hit byte-anchor/connection limits. Footnote bodies are PRESENT
in the DB (parser-undetected, not lost — detector stays 175/0); these are polish.
List: triage/westdoc-footnote-residue-manual.json. Ground-truth footnote sets
available via scripts/westdoc_footnotes.py; repair with the editpair workflow +
heal + gated applier, or by hand for the largest ones.
