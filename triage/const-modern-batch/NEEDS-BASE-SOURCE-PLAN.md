# needs-base-source bucket — status & plan (2026-06-15)

The bucket was classified before the 1989 Blue Book was acquired. With the 1989 + 1981 BBs
and the validated historical layer now on disk, it is **reconstruction work, not a
missing-files blocker**. Group A done; Group B sourced below.

## DONE — Group A (clean single-amendment), batch `modern-groupa-clean-2026-06-15`
- **art I § 1** ✓ — prior [1981,1984-12-05] = historical § 1 ("All men…"); #116 (1984) added bear-arms.
- **art X § 6** ✓ — prior [1981,2012-12-05] = historical § 180 (poll tax, "($1.50)" dropped per modern BBs); #154 (2012) repealed.

## Group B — STATUS 2026-06-15
- **art XIII § 1 — DONE** (`splice_artxiii_1_1996.py`, batch `modern-artxiii1-compact-1996`).
  3-subsection Compact; sub2 == historical §203, sub1+sub3 vs 1913 (overlap 0.976), all 14 $ amounts cross-verified.
- **art V §§ 1-12 — DONE** (`splice_artv_pre1997.py` 10 sections + `splice_artv_chains_1986.py` §1/§12).
  Reorganization crosswalk + the 1986 chains for §1/§12. §13 = pre-1997 orphan (deferred).
- **art VIII § 6 — REMAINING** (the one heavy item). See below.

## Group B detail (original sourcing notes)

### art XIII § 1 — 3-subsection 1996 drop (#132 "eliminates outdated language", eff 1996-07-11)
The pre-1996 §1 had THREE subsections; 1996 kept only subsection 1 (modernized: shall→must,
"his or her"→"that person's", "shall ever"→"may ever") and DELETED 2 & 3.
Reconstruct prior [1981-01-01, 1996-07-10] = the 3-subsection text. **Sources (mixed, verified vs 1989 BB):**
- **subsection 1** (toleration): 1925 official, clean — "1. Perfect toleration of religious sentiment
  shall be secured, and no inhabitant of this state shall ever be molested in person or property on
  account of his or her mode of religious worship." (== 1989 BB).
- **subsection 2** (public-lands disclaimer): **historical § 203** (post-1958 version, clean/validated —
  has the 1958-added "provided, however, that the Legislative Assembly … provide for the acceptance of
  such jurisdiction" clause that the 1925 lacks; == 1989 BB). NOT the 1925 (pre-1958).
- **subsection 3** (territorial-debt adjustment): 1925 official "3. In order that payment of the debts
  and liabilities contracted or incurred by and on behalf of the territory of Dakota …" — **LONG,
  obsolete, OCR-garbled ("pro- vided", "con gress", "\Vashington")**; needs careful OCR repair +
  cross-check (1973 BB has it as "Third."). This is the one real effort item.
Splice: prepend the assembled [1981,1996-07-10] version; current [1996-07-11,) unchanged.

### art V §§ 1–12 — 1997 executive-article replacement (#135, SL7CNSTM.pdf, eff 1997-07-01)
The 1997 measure replaced the executive article (so the prior isn't in the measure redline). The
**1989 BB has the full pre-1997 executive article** ("Section 1. The executive power shall be vested
in a governor…"). TODO before splice: (a) confirm replace-vs-renumber (does pre-1997 §N map to
post-1997 §N? spot-check content alignment — if renumbered, use the art-IV crosswalk technique);
(b) §1 and §12 also carry a 1986 amendment (#121/#122, CAA 1987) → they need [1981,1986)+[1986,1997)
layers (1981 BB + 1989 BB + the 1986 redline); §2–11 are single-step ([pre-1997]=1989 BB, [1997,)=current).

### art VIII § 6 — Board of Higher Education, 3-amendment chain (REMAINING)
10,630-char multi-subsection section; current DB has ONLY [2000-07-13, open) → all of [1981,2000)
is uncovered. Needs the FULL 4-version chain (no partial splice — would leave an integrity gap):
- [1981-01-01, 1994-12-07]  base      — 1989 BB clean pre-1994 base (subsections 1-6 + a/b subparts)
- [1994-12-08, 1996-12-04]  after #130 — 1994 student-member add (CAA 1995 p5)
- [1996-12-05, 2000-07-12]  after #133 — 1996 terms 7yr->4yr (SL7CNSTM 1997 p10)
- [2000-07-13, open)        current    — already in DB (#139)
METHOD: the two intermediates require READING the 1994 & 1996 session-law REDLINES (render the
AcroForm CAA/CNSTM PDFs via `mutool draw` at 400-500 dpi; struck=deleted, underlined=added) — the
campaign's redline method (prep_multi.py -> agent -> verify), OR reverse-walk from current using
the redline edit-lists. Gate: mech (apply(edits,after)==before), chain continuity, 1989 BB base
witness. This is a focused pass, not a quick splice — deferred to its own session.

## Recommendation
Each Group B item is a focused pass (multi-source assembly / chain reconstruction), best done
deliberately with the splice + BB-witness gates, not batched. Build stays reproducible via
`scripts/rebuild_const_modern.sh` (add each splice script as it lands). Order by tractability:
art XIII §1 (once subsection 3 is OCR-cleaned) → art V → art VIII §6.
