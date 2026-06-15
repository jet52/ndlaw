# needs-base-source bucket — status & plan (2026-06-15)

The bucket was classified before the 1989 Blue Book was acquired. With the 1989 + 1981 BBs
and the validated historical layer now on disk, it is **reconstruction work, not a
missing-files blocker**. Group A done; Group B sourced below.

## DONE — Group A (clean single-amendment), batch `modern-groupa-clean-2026-06-15`
- **art I § 1** ✓ — prior [1981,1984-12-05] = historical § 1 ("All men…"); #116 (1984) added bear-arms.
- **art X § 6** ✓ — prior [1981,2012-12-05] = historical § 180 (poll tax, "($1.50)" dropped per modern BBs); #154 (2012) repealed.

## Group B — sourced, splice pending (heavier)

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

### art VIII § 6 — Board of Higher Education, 3-amendment chain (1994 #130, 1996 #133, 2000 #139)
10,630-char multi-subsection section. The **1989 BB has the clean pre-1994 base** (subsections 1–6
with a/b subparts) — resolves the "redline + 1981 BB both OCR-degraded" worry. Build the chain:
[1981,1994)=1989 BB base; then apply the 1994/1996/2000 CAA redlines (fetchable) for the intervening
versions; [2000,)=current. Most work in the bucket (heavy section × 3 amendments).

## Recommendation
Each Group B item is a focused pass (multi-source assembly / chain reconstruction), best done
deliberately with the splice + BB-witness gates, not batched. Build stays reproducible via
`scripts/rebuild_const_modern.sh` (add each splice script as it lands). Order by tractability:
art XIII §1 (once subsection 3 is OCR-cleaned) → art V → art VIII §6.
