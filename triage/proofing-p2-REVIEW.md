# P2 proofing — REVIEW queue (PDF-confirmed, meaning-affecting)

17 proposals across 13 opinions. Each is byte-exact + PDF-verified;
they need your sign-off because they touch content, not just layout.

## 2026 ND 47 (id 20354)
- **split_join** (review:pdf_confirmed) conf=high
  - OLD: ". I[\u00b62]"
  - NEW: ".\n\n                                        I\n\n[\u00b62]"
  - why: Section heading 'I' is fused with paragraph marker '[¶2]' without proper line breaks. Source shows them properly separated with centered alignment for the section heading.

## 2026 ND 48 (id 20355)
- **caption** (review:pdf_confirmed) conf=high
  - OLD: "State of North Dakota,\n\nv.\n\nDelon Evan Davis,\n\nPlaintiff and Appellee\n\nDefendant and Appellant"
  - NEW: "State of North Dakota,\n\nPlaintiff and Appellee\n\nv.\n\nDelon Evan Davis,\n\nDefendant and Appellant"
  - why: The case caption in the DB text has the party labels (Plaintiff and Appellee / Defendant and Appellant) placed after both parties instead of aligned to each respective party. The authoritative PDF shows the correct format: 'State of North D

## 2026 ND 53 (id 20361)
- **split_join** (review:pdf_confirmed) conf=high
  - OLD: "made several specific the circumstances findings demonstrating surrounding the present parenting time schedule"
  - NEW: "made several specific findings demonstrating that the circumstances surrounding the present parenting time schedule"
  - why: OCR/ingestion error in paragraph [¶7] within the Prchal v. Prchal quotation. The quoted text has words scrambled: 'specific the circumstances findings demonstrating surrounding' should be 'specific findings demonstrating that the circumstan

## 2026 ND 54 (id 20362)
- **caption** (review:pdf_confirmed) conf=high
  - OLD: "IN THE SUPREME COURT\nSTATE OF NORTH DAKOTA\n\n2026 ND 54\n\nNeil Galpin,\nv.\n\nCantina Holdings, LLC,\nand Clay Butte Holdings, LLC,\n\nPlaintiff and Appellee\n\nDefendants and Appellants\n\nNo. 20250254\n\n"
  - NEW: "IN THE SUPREME COURT\nSTATE OF NORTH DAKOTA\n\n2026 ND 54\n\nNeil Galpin,                                             Plaintiff and Appellee\n      v.\nCantina Holdings, LLC,\nand Clay Butte Holdings, LLC,                      Defendants and Appell"
  - why: PDF source shows party names and designations on same lines (names left-aligned, designations right-aligned on same line). DB incorrectly separates them to different lines. Also includes 6-space indent before 'v.' and 33-space indent before

## 2026 ND 55 (id 20363)
- **caption** (review:pdf_confirmed) conf=high
  - OLD: "Mark Allen Rath,\n\nand\n\nDefendant and Appellant\n\nState of North Dakota,"
  - NEW: "Mark Allen Rath,\n\nDefendant and Appellant\n\nand\n\nState of North Dakota,"
  - why: This is a caption structure defect: the party designation 'Defendant and Appellant' belongs with 'Mark Allen Rath,' (as the second party), not between the connector 'and' and the third party 'State of North Dakota,'

## 2026 ND 58 (id 20366)
- **caption** (review:pdf_confirmed) conf=high
  - OLD: "Larry Alber,\n\nv.\n\nPlaintiff and Appellant"
  - NEW: "Larry Alber,\n\nPlaintiff and Appellant\n\nv."
  - why: Caption formatting error: party designation separated from party name by 'v.' divider. Standard legal caption format places designations with party names, with 'v.' separating the parties.
- **whitespace** (review:held_from_auto(ws-semantic)) conf=high
  - OLD: "prejudicial. . . . . When"
  - NEW: "prejudicial. .... When"
  - why: Ellipsis formatting in quoted material from case law. PDF shows four periods (....); DB has incorrectly spaced five periods (. . . . .)
- **whitespace** (review:held_from_auto(ws-semantic)) conf=high
  - OLD: "adequate? . . . . . . . I mean"
  - NEW: "adequate? .... . . . I mean"
  - why: Ellipsis formatting in court transcript quote. PDF shows distinct ellipsis pattern: four periods followed by spaced periods. DB incorrectly normalized to continuous spaced periods.

## 2026 ND 61 (id 20370)
- **ocr_char** (review:pdf_confirmed) conf=high
  - OLD: "ND 221, \u00b6 13, 932 N.W.2d 386). B"
  - NEW: "ND 221, \u00b6 13, 932 N.W.2d 386)."
  - why: PDF does not have this character inline; 'B' appears as its own section marker on a separate line after ¶10.

## 2026 ND 66 (id 20375)
- **split_join** (review:pdf_confirmed) conf=high
  - OLD: "a marital share of immediately received Richard\u2019s military retirement. Richard $50,500.00"
  - NEW: "a marital share of Richard\u2019s military retirement. Richard immediately received $50,500.00"
  - why: DB ¶20 contains a garbled quotation from the district court's findings. The phrase reads 'a marital share of immediately received Richard's military retirement. Richard $50,500.00' where 'immediately received' is wrongly inserted between 'o

## 2026 ND 69 (id 20378)
- **split_join** (review:pdf_confirmed) conf=high
  - OLD: "member who is the victim of domestic violence. If the child, residential the welfare of necessary responsibility for a child may be awarded"
  - NEW: "member who is the victim of domestic violence. If necessary to protect the welfare of the child, residential responsibility for a child may be awarded"
  - why: Text in ¶11 shows scrambled statute quotation with words reordered. PDF shows correct statutory language: 'If necessary to protect the welfare of the child, residential responsibility'. Occurs exactly once in statute quotation.
- **other** (review:pdf_confirmed) conf=high
  - OLD: "chapter 14-07.1. to protect N.D.C.C. \u00a7 14-09-06.2(1)(j)."
  - NEW: "chapter 14-07.1.\n\nN.D.C.C. \u00a7 14-09-06.2(1)(j)."
  - why: Extraneous text 'to protect' inserted between end of statute text and citation. PDF shows proper separation with blank line between statute end and citation. This is same statute passage as previous issue - continuation of ¶11 scramble.

## 2026 ND 70 (id 20380)
- **other** (review:pdf_confirmed) conf=high
  - OLD: "children as protected parties under the DVPO. B"
  - NEW: "children as protected parties under the DVPO."
  - why: Stray section label 'B' appended to end of [¶12]; the section heading should appear separately, not attached to paragraph text

## 2026 ND 71 (id 20392)
- **paragraph_seq** (review:pdf_confirmed) conf=high
  - OLD: "[\u00b65] Lisa Fair McEvers, C.J. Jerod E. Tufte Jon J. Jensen Douglas A. Bahr Mark A. Friese"
  - NEW: "[\u00b65] Lisa Fair McEvers, C.J.\n     Jerod E. Tufte\n     Jon J. Jensen\n     Douglas A. Bahr\n     Mark A. Friese"
  - why: DB collapsed multi-line signature block into single line; source has each justice on separate line with indentation

## 2026 ND 75 (id 20396)
- **whitespace** (review:held_from_auto(ws-semantic)) conf=medium
  - OLD: "section 12-44.1- 32 or 12-54.1-01"
  - NEW: "section 12-44.1-\n      32 or 12-54.1-01"
  - why: In the quoted statute text in [¶6], the PDF shows '12-44.1-' at the end of one line and '32' indented on the next line. The DB has incorrectly joined this with a space ('12-44.1- 32'), losing the line break structure. The indentation indica

## 2026 ND 78 (id 20399)
- **split_join** (review:pdf_confirmed) conf=high
  - OLD: "I N   T H E   S U P R E M E   C O U R T"
  - NEW: "IN THE SUPREME COURT"
  - why: PDF source contains normal word spacing 'IN THE SUPREME COURT'. DB has characters separated by spaces: 'I N   T H E   S U P R E M E   C O U R T'. This is an OCR artifact from pdftotext -layout where character-level spacing was preserved ins
- **paragraph_seq** (review:pdf_confirmed) conf=high
  - OLD: "[\u00b62] Lisa Fair McEvers, C.J. Jerod E. Tufte Jon J. Jensen Douglas A. Bahr Mark A. Friese"
  - NEW: "[\u00b62] Lisa Fair McEvers, C.J.\n     Jerod E. Tufte\n     Jon J. Jensen\n     Douglas A. Bahr\n     Mark A. Friese"
  - why: PDF source shows justice names on separate lines with 5-space indentation after the first line. DB has all justice names on a single line with only spaces between them. The newlines and indentation were stripped during ingestion.
