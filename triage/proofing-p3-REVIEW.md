# P3 proofing — REVIEW queue (PDF-confirmed, meaning-affecting)

14 proposals / 10 opinions. Byte-exact + PDF-verified; need sign-off.

## 2026 ND 16 (id 20320)
- **whitespace** (review:pdf_confirmed) conf=high
  - OLD: "parties. . . . . (iv)"
  - NEW: "parties. .... (iv)"
  - why: The authoritative PDF page 6 displays the text: '(ii) A party who files a complaint or other initiating pleading must serve notice of filing on the other parties. .... (iv) The defendant may file...' with four consecutiv

## 2026 ND 19 (id 20323)
- **split_join** (review:pdf_confirmed) conf=high
  - OLD: "When the unjust tortious conduct, such as enrichment allegations are predicated on misrepresentation or fraud, the claim is properly characterized as one arising in tort. Id. at 1008. in \u201cdeliberate\n\n"
  - NEW: "When the unjust enrichment allegations are predicated on tortious conduct, such as misrepresentation or fraud, the claim is properly characterized as one arising in tort. Id. at 1008.\n\n"
  - why: Paragraph 21: scrambled syntax. 'Tortious conduct, such as enrichment allegations' is reversed - should be 'enrichment allegations are predicated on tortious conduct'. The fragment 'in “deliberate' at end should not exis
- **split_join** (review:pdf_confirmed) conf=high
  - OLD: "[\u00b622] Sangster\u2019s complaint alleges UND engaged illegal treatment\u201d of the flight instructors."
  - NEW: "[\u00b622] Sangster\u2019s complaint alleges UND engaged in \u201cdeliberate illegal treatment\u201d of the flight instructors."
  - why: Paragraph 22: missing 'in' and 'deliberate'. Opening quote is wrong position. The phrase 'in “deliberate' was split away at end of [¶21] and should be part of [¶22]. Correct form: 'engaged in “deliberate illegal treatmen

## 2026 ND 22 (id 20327)
- **caption** (review:pdf_confirmed) conf=high
  - OLD: "State of North Dakota,\n\nv.\n\nPlaintiff and Appellee\n\nAngel Alberto Torres-Sosa,\n\nDefendant and Appellant"
  - NEW: "State of North Dakota,\n\nPlaintiff and Appellee\n\nv.\n\nAngel Alberto Torres-Sosa,\n\nDefendant and Appellant"
  - why: The official PDF renders the case caption with the vs/parties correctly paired: 'State of North Dakota, Plaintiff and Appellee' on one side and 'Angel Alberto Torres-Sosa, Defendant and Appellant' on the other, with 'v.'

## 2026 ND 30 (id 20336)
- **paragraph_seq** (review:pdf_confirmed) conf=high
  - OLD: "[\u00b611] We affirm the judgment of conviction.\n\nIV"
  - NEW: "IV\n\n[\u00b611] We affirm the judgment of conviction."
  - why: Source PDF has IV (centered, line 131) followed by blank line (132) then [¶11] (line 133). DB incorrectly places IV after [¶11]. This is a structural error in paragraph/section sequencing.

## 2026 ND 34 (id 20340)
- **split_join** (review:pdf_confirmed) conf=high
  - OLD: "by designating him a vexatious litigant. the due process and constitutional"
  - NEW: "by designating him a vexatious litigant."
  - why: Fragment 'the due process and constitutional' was detached from its proper position (start of ¶11) and appended to end of ¶10. This disrupts both paragraph structure and readability. Removing it restores correct paragrap

## 2026 ND 35 (id 20341)
- **other** (review:pdf_confirmed) conf=high
  - OLD: "State v. Castleman, 2024 ND 93, \u00b6 5, 6 N.W.3d 850. A"
  - NEW: "State v. Castleman, 2024 ND 93, \u00b6 5, 6 N.W.3d 850."
  - why: pdftotext extraction shows 'A' as a formatted standalone line; DB has it appended to paragraph text
- **other** (review:pdf_confirmed) conf=high
  - OLD: "and did not rely on any impermissible factor. B"
  - NEW: "and did not rely on any impermissible factor."
  - why: pdftotext extraction shows 'B' as a formatted standalone line; DB has it appended to paragraph text

## 2026 ND 38 (id 20344)
- **paragraph_seq** (review:pdf_confirmed) conf=high
  - OLD: "[\u00b63] Lisa Fair McEvers, C.J. Daniel J. Crothers Jerod E. Tufte Jon J. Jensen Douglas A. Bahr"
  - NEW: "[\u00b63] Lisa Fair McEvers, C.J.\n     Daniel J. Crothers\n     Jerod E. Tufte\n     Jon J. Jensen\n     Douglas A. Bahr"
  - why: The PDF source shows the judge signature block formatted with individual judge names on separate indented lines (lines 47-51 of pdftotext output). The DB has collapsed all judges onto a single line, removing newlines and

## 2026 ND 39 (id 20345)
- **whitespace** (review:pdf_confirmed) conf=high
  - OLD: "; . . . . "
  - NEW: "; .... "
  - why: DB ingestion produced spaced dots (non-standard); PDF shows compact form '; ....' (standard Bluebook convention for omitted statutory text)
- **whitespace** (review:pdf_confirmed) conf=high
  - OLD: ": . . . . "
  - NEW: ": .... "
  - why: DB has spaced ellipsis; PDF shows compact form within statutory quotation

## 2026 ND 40 (id 20347)
- **split_join** (review:pdf_confirmed) conf=high
  - OLD: "portion of the hearing. In Schmitz v. North Dakota State Board of Chiropractic Examiners, this Court\n\n[\u00b68] explained when"
  - NEW: "portion of the hearing.\n\n[\u00b68] In Schmitz v. North Dakota State Board of Chiropractic Examiners, this Court\nexplained when"
  - why: DB text has 'hearing. In Schmitz...this Court' at end of [¶7], then '[¶8] explained' on next line. Source PDF has 'hearing.' ending [¶7], then '[¶8] In Schmitz...this Court' opening [¶8], followed by 'explained' on next 
- **split_join** (review:pdf_confirmed) conf=high
  - OLD: " functions. law presumes governmental operations are conducted with\n\n[\u00b655] The regularity."
  - NEW: " functions.\n\n[\u00b655] The law presumes governmental operations are conducted with\nregularity."
  - why: DB shows: 'functions. law presumes governmental operations are conducted with\n\n[¶55] The regularity.' Source shows: 'functions.\n\n[¶55] The law presumes governmental operations are conducted with\nregularity.' Verifie

## 2026 ND 44 (id 20351)
- **paragraph_seq** (review:pdf_confirmed) conf=high
  - OLD: "[\u00b610] The appeal is dismissed for lack of jurisdiction.\n\nIII\n\n[\u00b611]"
  - NEW: "III\n\n[\u00b610] The appeal is dismissed for lack of jurisdiction.\n\n[\u00b611]"
  - why: Section heading III is in wrong sequence position relative to paragraph [¶10]. PDF source clearly shows III should precede [¶10], not follow it.
