#!/usr/bin/env python3
"""Apply corrections from the Blue-Book re-validation workflow (2026-06-08).

38 post-1955 Blue-Book-sourced amendments were re-validated against clean
session-law text (CAA/CMA). 30 were clean (incl. 2 whose only divergence was
OCR noise in the session-law scan, not the stored text). 8 had real errors:
2 substantive (body), 6 metadata/date. This applies the 7 cleanly-fixable items
plus CVII's split effective dates. Two items spill to the structural backlog:
XC's art-54-subsection-1 change, and (already) the per-change-date modeling.
"""
import json
from pathlib import Path

JSON = Path("/Users/jerod/code/ndcourts-mcp/data/constitution_amendments.json")
doc = json.loads(JSON.read_text())
recs = {r["number"]: r for r in doc["amendments"]}
log = []

# ---- LXXIV (§215): apply the rename that the amendment enacted but the stored text missed ----
r = recs["LXXIV"]; ch = r["changes"][0]
old = "Third: The Agricultural College at the City of Fargo, in the County of Cass."
new = "Third: The North Dakota State University of Agriculture and Applied Science at the City of Fargo, in the County of Cass."
assert old in ch["text"], "LXXIV: old Third paragraph not found"
ch["text"] = ch["text"].replace(old, new)
r["election_date"] = "1960-11-08"
r["sources_verified"] = ["~/refs/nd/sess/1961_sl/CMA.pdf ch. 407 (Constitutional Measures Approved; clean) — re-validated 2026-06-08; the amendment reenacted only the third paragraph of §215 to rename the institution"]
r["confidence"] = "high"
log.append("LXXIV §215: applied missing rename (Agricultural College -> ND State University of Agriculture and Applied Science) in paragraph Third")

# ---- XC (§216): replace OCR/annotation-contaminated text with clean session-law §216 ----
r = recs["XC"]; ch = r["changes"][0]
ch["text"] = (
"Section 216. The following named public institutions are hereby permanently located as "
"hereinafter provided, each to have so much of the remaining grant of one hundred seventy "
"thousand acres of land made by the United States for \"other educational and charitable "
"institutions\" as is allotted by law, namely:\n\n"
"First: A soldiers' home, when located, or such other charitable institution as the legislative "
"assembly may determine, at Lisbon, in the county of Ransom, with a grant of forty thousand acres "
"of land.\n\n"
"Second: The blind asylum shall be known as the North Dakota school for the blind and may be "
"removed from the county of Pembina to such other location as may be determined by the board of "
"administration to be in the best interests of the students of such institution and the state of "
"North Dakota.\n\n"
"Third: A school of forestry, or such other institution as the legislative assembly may determine, "
"at such place in one of the counties of McHenry, Ward, Bottineau, or Rolette, as the electors of "
"said counties may determine by an election for that purpose, to be held as provided by the "
"legislative assembly.\n\n"
"Fourth: A scientific school or such other educational or charitable institution as the legislative "
"assembly may prescribe, at the city of Wahpeton, county of Richland, with a grant of forty thousand "
"acres.\n\n"
"Fifth: A state normal school at the city of Minot in the county of Ward.\n\n"
"Sixth: (a) A state normal school at the city of Dickinson, in the county of Stark. (b) A state "
"hospital for the insane at such place within this state as shall be selected by the legislative "
"assembly, provided, that no other institution of a character similar to any one of those located "
"by this article shall be established or maintained without a revision of this Constitution."
)
r["election_date"] = "1972-09-05"
r["confidence"] = "high"
r["structural_followup"] = ("Chapter 526 SECTION 2 ALSO amended and reenacted subsection 1 of "
"amend. art. LIV (State Board of Higher Education membership). Not applied here — same "
"single-provision art-LIV issue as LXXVIII/XCVI. Backlog.")
log.append("XC §216: replaced annotation/OCR-contaminated text with clean session-law §216 (removed Blue Book editorial note; fixed Bottineau comma, Stark period, Constitution cap). Flagged art-54-subsec-1 second change to structural backlog.")

# ---- LXXIX (§113): fix authority chamber House -> Senate; drop unsupported (mislabeled) ----
r = recs["LXXIX"]
r["authority"] = ('Senate Concurrent Resolution "T", chapter 454, 1963 Session Laws; enacted '
'ch. 474, 1965 Session Laws ("Constitutional Measures, Approved"). Approved June 30, 1964.')
r["election_date"] = "1964-06-30"
log.append("LXXIX §113: authority chamber House->Senate Concurrent Resolution 'T'; removed unsupported '(mislabeled T)'; added election_date")

# ---- XCIII (§§74,77): add election_date ----
recs["XCIII"]["election_date"] = "1974-11-05"
log.append("XCIII: election_date -> 1974-11-05")

# ---- C (§214, Sched): add election_date ----
recs["C"]["election_date"] = "1978-09-05"
log.append("C: election_date -> 1978-09-05")

# ---- CIV (§§121-129): fix authority 'Senate House' -> 'House'; add election_date ----
r = recs["CIV"]
r["authority"] = r["authority"].replace("Senate House Concurrent Resolution No. 3014",
                                        "House Concurrent Resolution No. 3014")
r["election_date"] = "1978-11-07"
log.append("CIV: authority 'Senate House' -> 'House Concurrent Resolution No. 3014'; added election_date")

# ---- CV (art CV, §25, art XXXIII repeals): EXPRESS effective date Jan 1 1979 ----
r = recs["CV"]
r["election_date"] = "1978-11-07"
r["effective_date"] = "1979-01-01"   # SECTION 4 of ch. 696: express effective date
r["authority"] = r["authority"].replace("Senate... House Concurrent Resolution No. 3088",
                                        "House Concurrent Resolution No. 3088")
r["authority"] += " Express effective date January 1, 1979 (SECTION 4 of the resolution)."
log.append("CV: effective_date 1978-12-07 -> 1979-01-01 (express, SECTION 4); election_date 1978-11-07; cleaned authority. Note: CV repealed §25 (explains §25 status=repealed in base) and art. XXXIII.")

# ---- CVII (§173 + §69): split effective dates ----
r = recs["CVII"]
r["election_date"] = "1980-09-02"
for ch in r["changes"]:
    if ch["target"] == "N.D. Const. § 173":
        ch["effective_date"] = "1983-01-01"   # SECTION 3 delayed effective date
# record-level effective_date stays 1980-10-02 for the §69 repeal
r["authority"] += " Per SECTION 3, the §173 amendment took effect January 1, 1983; the §69 repeal took effect thirty days after certification (1980-10-02)."
log.append("CVII: §173 change effective_date -> 1983-01-01 (delayed per SECTION 3); §69 repeal stays 1980-10-02; added election_date")

JSON.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
print("Applied %d corrections:" % len(log))
for l in log: print("  -", l)
