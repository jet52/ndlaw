# Effective dates of ND constitutional amendments — rule, history, audit (2026-06-14)

Investigation prompted by art. XV (term limits) being stamped at its election date.
Reference: ndconst.org/amendments (user-reviewed); **confirmed from primary sources**
(the constitutional text itself + the enacting measures).

## The governing rule (primary source: the constitution, traced through its history)

**Initiated and referred measures — N.D. Const. art. III § 8** (and § 9, which makes
the initiative rules apply to an initiated constitutional amendment):
> "An initiated or referred measure which is approved shall become law **thirty days
> after the election** … "

A measure that **states its own effective date controls** ("unless otherwise
specified in the measure", in the pre-1981 phrasings).

**History of the default** (from `constitution_history.db`, validated layer):
| Era | Provision | Default effective date |
|---|---|---|
| 1889–1914 | (none) | no initiative/referendum |
| **1914–1918** | § 25 (1st I&R amendment) | "in force from **the date of the official declaration of the vote**" (canvass) |
| **1918–1978** | § 25 (amended) | "go into effect on the **thirtieth day after the election, unless otherwise specified in the measure**" |
| 1979–1980 | amend. art. CV | "become law **thirty days after the election**" |
| **1981–present** | art. III § 8 | "become law **thirty days after the election**" |

So the default is **30 days after the *election*** (not the canvass/certification),
established **1918** and unchanged since. Every modern amendment (1981+) is under this
one rule. (The 1914–1918 "date of canvass" rule only touches a few historical
amendments, already validated by the snapshot-diff against printed compilations.)

**Legislative-proposed amendments — art. IV § 16:** on majority approval "the
amendment **is a part of this constitution**" — the section states no 30-day delay.
ndconst.org nonetheless applies the 30-day default to legislatively-referred
amendments too (and the data is internally consistent with it). *Confidence:
moderate* that the 30-day default is the correct rule for legislative amendments —
it is textually anchored only for "initiated or referred measure[s]" in art. III § 8;
applying it to art. IV § 16 amendments is long-standing ND practice but is an
interpretive step worth the Court's own judgment. It does not affect any correction
below.

## Audit — all 59 modern (1981+) amendments reconciled

The DB's stored effective dates **all match ndconst.org** (faithful ingest). Each was
checked against `election + 30 days` or, where different, against the measure:
- **Silent measures** → effective = election + 30 days (e.g. 113, 114, 124, 142, 144,
  150, 154–157, 159–162, 166, 167). Correct.
- **Measures stating a date** → that date (verified examples): 152 Legacy Fund
  ("after June 30, 2011" → 2011-07-01); 163 ethics, art. XIV § 4 ("**take effect sixty
  days after approval**" → 2018-11-06 + 60 = **2019-01-05**); 165 age limits ("take
  effect immediately upon passage" → election day 2024-06-11); plus the fiscal Jul-1 /
  Jan-1 / Aug-1 dates (135/136/145/148/149/158/etc.). Correct.

**One error found and corrected — amendment 164 (art. XV term limits):**
ndconst.org/DB had **2022-11-08** (the election date — neither the stated date nor
even the 30-day default). The measure's **Section 5** states it is "**effective on the
first day of January immediately following approval**" → **2023-01-01** (conclusive).

## Correction applied (`fix-amend164-effdate-2026-06-14`)
- Amendment 164 `effective_date` 2022-11-08 → **2023-01-01**; art. XV §§ 1-6
  `effective_start` likewise. Applied to live `constitution.db` + scratch; integrity 0/0.
- Reproducible: `AMENDMENT_EFFECTIVE_DATE_CORRECTIONS` in `ingest_constitution.py`.

*Not changed (flagged only):* 119/120 (art. IV recreation) carry an odd ndconst.org
*election*-date (1984) vs a 1986-12-01 effective; they are CREATE provisions and the
effective date is plausible, but the election-date metadata looks off — low priority.
