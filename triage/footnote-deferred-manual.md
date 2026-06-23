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

Verify sources: `~/refs/nd/opin/archive/<year>/<docket>.htm` (FN_N_ anchors mark
call sites, not bodies) + court PDFs `~/refs/nd/opin/pdfs/<year>/<cite>.pdf`.
