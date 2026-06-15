# art IV [1981,1986) crosswalk — scope, model, and plan

Status: **§§1-16 SHARED SET DONE 2026-06-15** (13 spliced, batch
`modern-artiv-crosswalk-1981-1986-2026-06-15`; reproducible, integrity 0). Remaining:
§§2/5/11 stubs + §§17-46 repealed-only (see end). Original characterization below.
Goal: make point-in-time correct for `N.D. Const. art. IV, § N` in the **[1981-01-01,
1986-12-01)** window. Today the modern art IV provisions serve only post-recreation
content, so that whole window returns the wrong text (or nothing) for old citations.

## The event
Art IV (Legislative Branch) was repealed-and-recreated **effective 1986-12-01** (approved
June 12 & Nov 6, 1984; S.L. 1983 ch. 728/730, 1985 ch. 706/707). The recreation REUSED the
§1–16 citation numbers for new content. Codifier note: "new sections 1 to 8 and 12 to 16 …
repeal of former sections 1 to 13, 16 to 18, and 20 to 45 … Sections 14, 15 and 19 …
renumbered as sections 9 to 11." Former §46 (compensation) was repealed earlier (1982,
S.L. 1981 ch. 668; now art XI §26).

So the citation "art IV § N" denotes DIFFERENT provisions before/after 1986-12-01. This is a
genuine renumbering — the same problem class as the 1889→1981 reorg crosswalk
(PL-CONST-CROSSWALK), scoped to one article.

## Pre-1986 structure (from the 1981 Blue Book, the authoritative [1981,1986) witness)
Art IV = **§§ 1–46** (microfilm BB lines L142–L293). Notable: §§2, 5, 11 marked
"[Unconstitutional.]"; §1 = "The senate and house of representatives jointly shall be
designated as the legislative assembly of the state of North Dakota."

Old→new disposition:
- **Renumbered survivors:** old §14 (bribery) → new §9; old §15 (disqualification) → new §10;
  old §19 (writs/vacancy) → new §11. (The §9/10/11 *citations* in [1981,1986) held the OLD
  §9/10/11, which were REPEALED — distinct from the survivor content now there from 1986-12-01.)
- **Repealed by the recreation (1986-12-01):** old §§ 1–13, 16, 17, 18, 20–45.
- **Repealed earlier (1982):** old § 46.
- **New (created 1986-12-01):** §§ 1–8, 12–16 (already in DB, correctly dated 1986-12-01).

## Model (decided)
Each citation's version timeline reflects what it actually denoted on each date.
- **§§ 1–8, 12–16** (modern provisions exist; currently single [1986-12-01,open) new version):
  PREPEND a `[1981-01-01, 1986-11-30]` version = OLD §N content.
- **§§ 9, 10, 11** (currently [1986-12-01,…) survivor content, fixed this session): PREPEND a
  `[1981-01-01, 1986-11-30]` version = OLD §9/10/11 content (the repealed originals — NOT the
  survivors). Yields e.g. §9: [1981,1986)=old§9 → [1986-12-01,open)=bribery.
- **§§ 17, 18, 20–46** (NO modern provision — repealed, absent from the modern scheme): create
  provisions with a single `[1981-01-01, 1986-11-30]` version = OLD §N content, status
  superseded/repealed. (Lower query value — no modern citation resolves here — but needed for
  full [1981,1986) coverage. Candidate to defer.)

Boundary: prior ends 1986-11-30, recreation starts 1986-12-01 (no gap).

## Text sourcing
The [1981,1986) text == the 1980 content (no art IV amendments 1981–1986 except the §46
repeal). Two sources, cross-check:
1. **1981 Blue Book** — right numbering (art IV §N) but heavy microfilm OCR space-garble.
2. **Historical layer** (constitution_history.db, 1889 numbering, validated 1889–1980) — clean
   text but OLD 1889 § numbers. Need the art-IV-§N → 1889-§M crosswalk to pull clean text.
   Derive by despaced text-matching 1981-BB art IV §§1–46 against the historical layer; verify
   each match; use the historical (clean) text as authoritative, 1981 BB as the numbering witness.
   Clean compilations (1925/1973) are additional OCR-repair witnesses.

## Plan / next steps
1. Derive the art-IV-§N(1981) → 1889-§M crosswalk (text-match + verify). [foundational]
2. Pull clean [1981,1986) text per old §N from the historical layer (OCR-repaired vs 1925/1973).
3. Splice: prepend [1981,1986) versions to §§1–16; (optionally) create §§17–46.
4. Verify: snapshot-diff at T=1983 (need a [1981,1986) witness — the 1981 BB itself) +
   point-in-time spot checks across the 1986-12-01 boundary; integrity 0.
5. Fold into `scripts/rebuild_const_modern.sh` (or the promotion-time JSON applier).

## Derived crosswalk (2026-06-15): art IV §N(1981) → 1889 §M
Method: despaced `SequenceMatcher` of each 1981-BB art IV §N against every historical
1889 §M (latest/1980-valid version). **38/45 matched at ratio ≥0.92** (clean carry-over).
This recovers the art IV crosswalk WITHOUT the NDCC Replacement Vol 13 disposition table —
the legislative article carried verbatim from 1889, so text-matching suffices here.

High-confidence (ratio ≥0.92): §1→§52, §3→§27, §4→§28, §6→§30, §7→§31, §8→§32, §9→§33,
§10→§34, §12→§36, §13→§37, §14→§40, §15→§38, §16→§41, §17→§39, §19→§44, §20→§42, §21→§43,
§22→§53, §23→§56, §24→§51, §27→§48, §28→§50, §29→§49, §30→§54, §31→§57, §32→§58, §33→§61,
§34→§59, §35→§60, §36→§62, §37→§63, §38→§64, §39→§65, §40→§66, §41→§67, §42→§68, §44→§70,
§46→§45.

NEEDS MANUAL VERIFICATION (7):
- §2, §5, §11 — "[Unconstitutional.]" stubs (no content to match). Represent the [1981,1986)
  state as the marker/struck text per the 1981 BB; do NOT pull 1889 content.
- §18 → §75? (ratio 0.37) — weak; verify (governor/officer interest-in-contract).
- §25 → §46? (ratio 0.80) — quorum; moderate, verify.
- §43 → §182? (ratio 0.21) — special-legislation enumeration; matcher unreliable on the long
  enumerated section, verify (likely 1889 §69-area).
- §45 → §202 (ratio 0.49) — amendment-proposal procedure; §202 IS the amendment section, but
  the 1981 text is an amended/shortened form — verify which historical version applies at [1981,1986).
- Note: 1981 art IV has NO §26 (jumps 25→27) — repealed before 1981; nothing to source.

Sourcing rule: clean [1981,1986) text = the matched 1889 §M's historical version in force at
1980 (cross-check vs 1925/1973 for OCR). Verify per section that OLD §N ≠ NEW §N before
prepending (if equal, no prior version needed).

## Scale / recommendation
~16 shared sections (high value — modern citations resolve here) + ~28 repealed-only sections
(lower value). Recommend executing the **§§1–16 shared set first** (the queryable ones), then
deciding on §§17–46. This is a multi-step effort best run as its own focused pass (the
multi-agent redline method is overkill here since the text is recoverable from the historical
layer; the work is crosswalk-matching + clean-text splicing, not redline reading).
