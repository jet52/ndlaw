export const meta = {
  name: 'corpus-proofing-p33',
  description: 'Corpus proofing: transcription-fidelity proofread vs authoritative source (propose + flag, never apply)',
  phases: [{ title: 'Proof', detail: 'read-only agent per opinion: source-verified corrections + flags' }],
}

const BATCH = [
 {
  "id": 19355,
  "cite": "2019 ND 140",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND140.pdf' /tmp/src_2019ND140.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND140.pdf' <page>."
 },
 {
  "id": 19354,
  "cite": "927 N.W.2d 872",
  "era": "2019 (reporter-era, OCR)",
  "report": "whitespace: 5 blank-runs(3+)",
  "sdesc": "the .doc (RTF — Westlaw) this opinion was ingested from",
  "saccess": "Source file: /Users/jerod/refs/nd/opin/N.W.2d/927/0872-Nancy-ORTEGA-Plaintiff-and-Appellant-v-Sanford-BISMARCK-Christie-Iverson-MD-Defendants-and.doc . If a `.doc`, parse footnotes/structure as RTF; if markdown, it is the OCR text — compare carefully, the DB may have diverged from it."
 },
 {
  "id": 19353,
  "cite": "927 N.W.2d 416",
  "era": "2019 (reporter-era, OCR)",
  "report": "(no structural flags)",
  "sdesc": "the reporter markdown (OCR of the N.W./N.W.2d scan) this opinion was ingested from",
  "saccess": "Source file: /Users/jerod/refs/nd/opin/markdown/2019/2019ND131.md . If a `.doc`, parse footnotes/structure as RTF; if markdown, it is the OCR text — compare carefully, the DB may have diverged from it."
 },
 {
  "id": 19352,
  "cite": "927 N.W.2d 422",
  "era": "2019 (reporter-era, OCR)",
  "report": "(no structural flags)",
  "sdesc": "the reporter markdown (OCR of the N.W./N.W.2d scan) this opinion was ingested from",
  "saccess": "Source file: /Users/jerod/refs/nd/opin/markdown/2019/2019ND125.md . If a `.doc`, parse footnotes/structure as RTF; if markdown, it is the OCR text — compare carefully, the DB may have diverged from it."
 },
 {
  "id": 19351,
  "cite": "927 N.W.2d 84",
  "era": "2019 (reporter-era, OCR)",
  "report": "whitespace: 4 blank-runs(3+)",
  "sdesc": "the .doc (RTF — Westlaw) this opinion was ingested from",
  "saccess": "Source file: /Users/jerod/refs/nd/opin/N.W.2d/927/0084-STATE-of-North-Dakota-Plaintiff-and-Appellee-v-Steven-GARDNER-Defendant-and-Appellant-No-2.doc . If a `.doc`, parse footnotes/structure as RTF; if markdown, it is the OCR text — compare carefully, the DB may have diverged from it."
 },
 {
  "id": 19350,
  "cite": "926 N.W.2d 709",
  "era": "2019 (reporter-era, OCR)",
  "report": "(no structural flags)",
  "sdesc": "the reporter markdown (OCR of the N.W./N.W.2d scan) this opinion was ingested from",
  "saccess": "Source file: /Users/jerod/refs/nd/opin/markdown/2019/2019ND118.md . If a `.doc`, parse footnotes/structure as RTF; if markdown, it is the OCR text — compare carefully, the DB may have diverged from it."
 },
 {
  "id": 17478,
  "cite": "2019 ND 123",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 5 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND123.pdf' /tmp/src_2019ND123.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND123.pdf' <page>."
 },
 {
  "id": 17477,
  "cite": "2019 ND 132",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 14 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND132.pdf' /tmp/src_2019ND132.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND132.pdf' <page>."
 },
 {
  "id": 17476,
  "cite": "2019 ND 124",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 42 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND124.pdf' /tmp/src_2019ND124.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND124.pdf' <page>."
 },
 {
  "id": 17474,
  "cite": "2019 ND 139",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 16 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND139.pdf' /tmp/src_2019ND139.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND139.pdf' <page>."
 },
 {
  "id": 17473,
  "cite": "2019 ND 136",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 19 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND136.pdf' /tmp/src_2019ND136.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND136.pdf' <page>."
 },
 {
  "id": 17472,
  "cite": "2019 ND 144",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 30 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND144.pdf' /tmp/src_2019ND144.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND144.pdf' <page>."
 },
 {
  "id": 17470,
  "cite": "2019 ND 130",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 1 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND130.pdf' /tmp/src_2019ND130.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND130.pdf' <page>."
 },
 {
  "id": 17468,
  "cite": "2019 ND 126",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 1 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND126.pdf' /tmp/src_2019ND126.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND126.pdf' <page>."
 },
 {
  "id": 17466,
  "cite": "2019 ND 128",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 7 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND128.pdf' /tmp/src_2019ND128.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND128.pdf' <page>."
 },
 {
  "id": 17464,
  "cite": "2019 ND 135",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 29 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND135.pdf' /tmp/src_2019ND135.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND135.pdf' <page>."
 },
 {
  "id": 17463,
  "cite": "2019 ND 138",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 38 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND138.pdf' /tmp/src_2019ND138.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND138.pdf' <page>."
 },
 {
  "id": 17462,
  "cite": "2019 ND 134",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND134.pdf' /tmp/src_2019ND134.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND134.pdf' <page>."
 },
 {
  "id": 17459,
  "cite": "2019 ND 127",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 5 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND127.pdf' /tmp/src_2019ND127.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND127.pdf' <page>."
 },
 {
  "id": 17458,
  "cite": "2019 ND 129",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 21 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND129.pdf' /tmp/src_2019ND129.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND129.pdf' <page>."
 },
 {
  "id": 17457,
  "cite": "2019 ND 137",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 1 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND137.pdf' /tmp/src_2019ND137.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND137.pdf' <page>."
 },
 {
  "id": 17454,
  "cite": "2019 ND 117",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND117.pdf' /tmp/src_2019ND117.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND117.pdf' <page>."
 },
 {
  "id": 17453,
  "cite": "2019 ND 119",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND119.pdf' /tmp/src_2019ND119.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND119.pdf' <page>."
 },
 {
  "id": 17452,
  "cite": "2019 ND 120",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND120.pdf' /tmp/src_2019ND120.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND120.pdf' <page>."
 },
 {
  "id": 17451,
  "cite": "2019 ND 121",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND121.pdf' /tmp/src_2019ND121.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND121.pdf' <page>."
 },
 {
  "id": 17450,
  "cite": "2019 ND 116",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND116.pdf' /tmp/src_2019ND116.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND116.pdf' <page>."
 },
 {
  "id": 17449,
  "cite": "2019 ND 115",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 8 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND115.pdf' /tmp/src_2019ND115.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND115.pdf' <page>."
 },
 {
  "id": 17448,
  "cite": "2019 ND 114",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 6 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND114.pdf' /tmp/src_2019ND114.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND114.pdf' <page>."
 },
 {
  "id": 17447,
  "cite": "2019 ND 113",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 15 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND113.pdf' /tmp/src_2019ND113.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND113.pdf' <page>."
 },
 {
  "id": 17446,
  "cite": "2019 ND 112",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 8 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND112.pdf' /tmp/src_2019ND112.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND112.pdf' <page>."
 },
 {
  "id": 17445,
  "cite": "2019 ND 111",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 11 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND111.pdf' /tmp/src_2019ND111.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND111.pdf' <page>."
 },
 {
  "id": 17443,
  "cite": "2019 ND 110",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 5 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND110.pdf' /tmp/src_2019ND110.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND110.pdf' <page>."
 },
 {
  "id": 17444,
  "cite": "2019 ND 99",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 12 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND99.pdf' /tmp/src_2019ND99.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND99.pdf' <page>."
 },
 {
  "id": 17442,
  "cite": "2019 ND 95",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND95.pdf' /tmp/src_2019ND95.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND95.pdf' <page>."
 },
 {
  "id": 17441,
  "cite": "2019 ND 109",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 15 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND109.pdf' /tmp/src_2019ND109.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND109.pdf' <page>."
 },
 {
  "id": 17440,
  "cite": "2019 ND 97",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 20 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND97.pdf' /tmp/src_2019ND97.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND97.pdf' <page>."
 },
 {
  "id": 17439,
  "cite": "2019 ND 104",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 17 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND104.pdf' /tmp/src_2019ND104.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND104.pdf' <page>."
 },
 {
  "id": 17438,
  "cite": "2019 ND 105",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 2 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND105.pdf' /tmp/src_2019ND105.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND105.pdf' <page>."
 },
 {
  "id": 17437,
  "cite": "2019 ND 96",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 7 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND96.pdf' /tmp/src_2019ND96.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND96.pdf' <page>."
 },
 {
  "id": 17436,
  "cite": "2019 ND 103",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND103.pdf' /tmp/src_2019ND103.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND103.pdf' <page>."
 },
 {
  "id": 17435,
  "cite": "2019 ND 98",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 14 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND98.pdf' /tmp/src_2019ND98.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND98.pdf' <page>."
 },
 {
  "id": 17434,
  "cite": "2019 ND 100",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND100.pdf' /tmp/src_2019ND100.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND100.pdf' <page>."
 },
 {
  "id": 17433,
  "cite": "2019 ND 92",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND92.pdf' /tmp/src_2019ND92.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND92.pdf' <page>."
 },
 {
  "id": 17432,
  "cite": "2019 ND 106",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 10 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND106.pdf' /tmp/src_2019ND106.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND106.pdf' <page>."
 },
 {
  "id": 17431,
  "cite": "2019 ND 93",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND93.pdf' /tmp/src_2019ND93.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND93.pdf' <page>."
 },
 {
  "id": 17430,
  "cite": "2019 ND 94",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND94.pdf' /tmp/src_2019ND94.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND94.pdf' <page>."
 },
 {
  "id": 17429,
  "cite": "2019 ND 107",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 3 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND107.pdf' /tmp/src_2019ND107.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND107.pdf' <page>."
 },
 {
  "id": 17428,
  "cite": "2019 ND 102",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 2 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND102.pdf' /tmp/src_2019ND102.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND102.pdf' <page>."
 },
 {
  "id": 17427,
  "cite": "2019 ND 108",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 8 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND108.pdf' /tmp/src_2019ND108.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND108.pdf' <page>."
 },
 {
  "id": 17426,
  "cite": "2019 ND 91",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND91.pdf' /tmp/src_2019ND91.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND91.pdf' <page>."
 },
 {
  "id": 17425,
  "cite": "2019 ND 101",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 4 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND101.pdf' /tmp/src_2019ND101.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND101.pdf' <page>."
 },
 {
  "id": 17424,
  "cite": "2019 ND 90",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND90.pdf' /tmp/src_2019ND90.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND90.pdf' <page>."
 },
 {
  "id": 17420,
  "cite": "2019 ND 89",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 7 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND89.pdf' /tmp/src_2019ND89.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND89.pdf' <page>."
 },
 {
  "id": 17419,
  "cite": "2019 ND 88",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 2 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND88.pdf' /tmp/src_2019ND88.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND88.pdf' <page>."
 },
 {
  "id": 17418,
  "cite": "2019 ND 85",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 3 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND85.pdf' /tmp/src_2019ND85.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND85.pdf' <page>."
 },
 {
  "id": 17417,
  "cite": "2019 ND 86",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 4 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND86.pdf' /tmp/src_2019ND86.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND86.pdf' <page>."
 },
 {
  "id": 17416,
  "cite": "2019 ND 87",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 8 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND87.pdf' /tmp/src_2019ND87.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND87.pdf' <page>."
 },
 {
  "id": 17415,
  "cite": "2019 ND 83",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 8 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND83.pdf' /tmp/src_2019ND83.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND83.pdf' <page>."
 },
 {
  "id": 17414,
  "cite": "2019 ND 82",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 11 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND82.pdf' /tmp/src_2019ND82.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND82.pdf' <page>."
 },
 {
  "id": 17413,
  "cite": "2019 ND 84",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND84.pdf' /tmp/src_2019ND84.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND84.pdf' <page>."
 },
 {
  "id": 17412,
  "cite": "2019 ND 81",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 8 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND81.pdf' /tmp/src_2019ND81.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND81.pdf' <page>."
 },
 {
  "id": 17411,
  "cite": "2019 ND 78",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 5 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND78.pdf' /tmp/src_2019ND78.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND78.pdf' <page>."
 },
 {
  "id": 19457,
  "cite": "924 N.W.2d 87",
  "era": "2019 (reporter-era, OCR)",
  "report": "(no structural flags)",
  "sdesc": "the reporter markdown (OCR of the N.W./N.W.2d scan) this opinion was ingested from",
  "saccess": "Source file: /Users/jerod/refs/nd/opin/markdown/2019/2019ND59.md . If a `.doc`, parse footnotes/structure as RTF; if markdown, it is the OCR text — compare carefully, the DB may have diverged from it."
 },
 {
  "id": 17423,
  "cite": "2019 ND 66",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 12 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND66.pdf' /tmp/src_2019ND66.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND66.pdf' <page>."
 },
 {
  "id": 17422,
  "cite": "2019 ND 69",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 12 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND69.pdf' /tmp/src_2019ND69.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND69.pdf' <page>."
 },
 {
  "id": 17410,
  "cite": "2019 ND 72",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 1 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND72.pdf' /tmp/src_2019ND72.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND72.pdf' <page>."
 },
 {
  "id": 17409,
  "cite": "2019 ND 71",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 10 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND71.pdf' /tmp/src_2019ND71.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND71.pdf' <page>."
 },
 {
  "id": 17408,
  "cite": "2019 ND 77",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 15 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND77.pdf' /tmp/src_2019ND77.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND77.pdf' <page>."
 },
 {
  "id": 17407,
  "cite": "2019 ND 68",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 20 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND68.pdf' /tmp/src_2019ND68.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND68.pdf' <page>."
 },
 {
  "id": 17406,
  "cite": "2019 ND 79",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 10 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND79.pdf' /tmp/src_2019ND79.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND79.pdf' <page>."
 },
 {
  "id": 17405,
  "cite": "2019 ND 76",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 30 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND76.pdf' /tmp/src_2019ND76.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND76.pdf' <page>."
 },
 {
  "id": 17404,
  "cite": "2019 ND 65",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 9 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND65.pdf' /tmp/src_2019ND65.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND65.pdf' <page>."
 },
 {
  "id": 17403,
  "cite": "2019 ND 74",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 23 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND74.pdf' /tmp/src_2019ND74.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND74.pdf' <page>."
 },
 {
  "id": 17402,
  "cite": "2019 ND 64",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND64.pdf' /tmp/src_2019ND64.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND64.pdf' <page>."
 },
 {
  "id": 17401,
  "cite": "2019 ND 62",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND62.pdf' /tmp/src_2019ND62.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND62.pdf' <page>."
 },
 {
  "id": 17400,
  "cite": "2019 ND 70",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND70.pdf' /tmp/src_2019ND70.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND70.pdf' <page>."
 },
 {
  "id": 17399,
  "cite": "2019 ND 63",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND63.pdf' /tmp/src_2019ND63.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND63.pdf' <page>."
 },
 {
  "id": 17398,
  "cite": "2019 ND 61",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND61.pdf' /tmp/src_2019ND61.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND61.pdf' <page>."
 },
 {
  "id": 17397,
  "cite": "2019 ND 75",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 29 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND75.pdf' /tmp/src_2019ND75.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND75.pdf' <page>."
 },
 {
  "id": 17396,
  "cite": "2019 ND 67",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 7 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND67.pdf' /tmp/src_2019ND67.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND67.pdf' <page>."
 },
 {
  "id": 17395,
  "cite": "2019 ND 80",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 38 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND80.pdf' /tmp/src_2019ND80.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND80.pdf' <page>."
 },
 {
  "id": 17394,
  "cite": "2019 ND 73",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND73.pdf' /tmp/src_2019ND73.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND73.pdf' <page>."
 },
 {
  "id": 17393,
  "cite": "2019 ND 60",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND60.pdf' /tmp/src_2019ND60.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND60.pdf' <page>."
 },
 {
  "id": 17392,
  "cite": "2019 ND 58",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 2 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND58.pdf' /tmp/src_2019ND58.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND58.pdf' <page>."
 },
 {
  "id": 17391,
  "cite": "2019 ND 57",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 14 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND57.pdf' /tmp/src_2019ND57.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND57.pdf' <page>."
 },
 {
  "id": 17390,
  "cite": "2019 ND 55",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND55.pdf' /tmp/src_2019ND55.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND55.pdf' <page>."
 },
 {
  "id": 17389,
  "cite": "2019 ND 56",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND56.pdf' /tmp/src_2019ND56.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND56.pdf' <page>."
 },
 {
  "id": 19456,
  "cite": "922 N.W.2d 782",
  "era": "2019 (reporter-era, OCR)",
  "report": "(no structural flags)",
  "sdesc": "the reporter markdown (OCR of the N.W./N.W.2d scan) this opinion was ingested from",
  "saccess": "Source file: /Users/jerod/refs/nd/opin/markdown/2019/2019ND39.md . If a `.doc`, parse footnotes/structure as RTF; if markdown, it is the OCR text — compare carefully, the DB may have diverged from it."
 },
 {
  "id": 19455,
  "cite": "923 N.W.2d 137",
  "era": "2019 (reporter-era, OCR)",
  "report": "(no structural flags)",
  "sdesc": "the reporter markdown (OCR of the N.W./N.W.2d scan) this opinion was ingested from",
  "saccess": "Source file: /Users/jerod/refs/nd/opin/markdown/2019/2019ND36.md . If a `.doc`, parse footnotes/structure as RTF; if markdown, it is the OCR text — compare carefully, the DB may have diverged from it."
 },
 {
  "id": 19454,
  "cite": "923 N.W.2d 105",
  "era": "2019 (reporter-era, OCR)",
  "report": "(no structural flags)",
  "sdesc": "the reporter markdown (OCR of the N.W./N.W.2d scan) this opinion was ingested from",
  "saccess": "Source file: /Users/jerod/refs/nd/opin/markdown/2019/2019ND35.md . If a `.doc`, parse footnotes/structure as RTF; if markdown, it is the OCR text — compare carefully, the DB may have diverged from it."
 },
 {
  "id": 17388,
  "cite": "2019 ND 45",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 5 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND45.pdf' /tmp/src_2019ND45.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND45.pdf' <page>."
 },
 {
  "id": 17387,
  "cite": "2019 ND 46",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 28 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND46.pdf' /tmp/src_2019ND46.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND46.pdf' <page>."
 },
 {
  "id": 17386,
  "cite": "2019 ND 41",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 4 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND41.pdf' /tmp/src_2019ND41.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND41.pdf' <page>."
 },
 {
  "id": 17385,
  "cite": "2019 ND 48",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 14 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND48.pdf' /tmp/src_2019ND48.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND48.pdf' <page>."
 },
 {
  "id": 17384,
  "cite": "2019 ND 44",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 18 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND44.pdf' /tmp/src_2019ND44.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND44.pdf' <page>."
 },
 {
  "id": 17383,
  "cite": "2019 ND 43",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 8 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND43.pdf' /tmp/src_2019ND43.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND43.pdf' <page>."
 },
 {
  "id": 17382,
  "cite": "2019 ND 53",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND53.pdf' /tmp/src_2019ND53.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND53.pdf' <page>."
 },
 {
  "id": 17381,
  "cite": "2019 ND 42",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 5 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND42.pdf' /tmp/src_2019ND42.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND42.pdf' <page>."
 },
 {
  "id": 17380,
  "cite": "2019 ND 33",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND33.pdf' /tmp/src_2019ND33.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND33.pdf' <page>."
 },
 {
  "id": 17379,
  "cite": "2019 ND 47",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 12 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND47.pdf' /tmp/src_2019ND47.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND47.pdf' <page>."
 },
 {
  "id": 17378,
  "cite": "2019 ND 54",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 3 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND54.pdf' /tmp/src_2019ND54.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND54.pdf' <page>."
 },
 {
  "id": 17376,
  "cite": "2019 ND 49",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 18 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND49.pdf' /tmp/src_2019ND49.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND49.pdf' <page>."
 },
 {
  "id": 17375,
  "cite": "2019 ND 40",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND40.pdf' /tmp/src_2019ND40.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND40.pdf' <page>."
 },
 {
  "id": 17374,
  "cite": "2019 ND 51",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 10 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND51.pdf' /tmp/src_2019ND51.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND51.pdf' <page>."
 },
 {
  "id": 17373,
  "cite": "2019 ND 38",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND38.pdf' /tmp/src_2019ND38.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND38.pdf' <page>."
 },
 {
  "id": 17372,
  "cite": "2019 ND 52",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 12 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND52.pdf' /tmp/src_2019ND52.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND52.pdf' <page>."
 },
 {
  "id": 17371,
  "cite": "2019 ND 50",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 12 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND50.pdf' /tmp/src_2019ND50.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND50.pdf' <page>."
 },
 {
  "id": 17370,
  "cite": "2019 ND 37",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 2 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND37.pdf' /tmp/src_2019ND37.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND37.pdf' <page>."
 },
 {
  "id": 17368,
  "cite": "2019 ND 34",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND34.pdf' /tmp/src_2019ND34.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND34.pdf' <page>."
 },
 {
  "id": 17366,
  "cite": "2019 ND 32",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND32.pdf' /tmp/src_2019ND32.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND32.pdf' <page>."
 },
 {
  "id": 17365,
  "cite": "2019 ND 31",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 25 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND31.pdf' /tmp/src_2019ND31.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND31.pdf' <page>."
 },
 {
  "id": 17364,
  "cite": "2019 ND 30",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 22 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND30.pdf' /tmp/src_2019ND30.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND30.pdf' <page>."
 },
 {
  "id": 17363,
  "cite": "2019 ND 29",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND29.pdf' /tmp/src_2019ND29.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND29.pdf' <page>."
 },
 {
  "id": 19446,
  "cite": "921 N.W.2d 176",
  "era": "2019 (reporter-era, OCR)",
  "report": "(no structural flags)",
  "sdesc": "the reporter markdown (OCR of the N.W./N.W.2d scan) this opinion was ingested from",
  "saccess": "Source file: /Users/jerod/refs/nd/opin/markdown/2019/2019ND3.md . If a `.doc`, parse footnotes/structure as RTF; if markdown, it is the OCR text — compare carefully, the DB may have diverged from it."
 },
 {
  "id": 19361,
  "cite": "921 N.W.2d 640",
  "era": "2019 (reporter-era, OCR)",
  "report": "(no structural flags)",
  "sdesc": "the reporter markdown (OCR of the N.W./N.W.2d scan) this opinion was ingested from",
  "saccess": "Source file: /Users/jerod/refs/nd/opin/markdown/2019/2019ND16.md . If a `.doc`, parse footnotes/structure as RTF; if markdown, it is the OCR text — compare carefully, the DB may have diverged from it."
 },
 {
  "id": 17362,
  "cite": "2019 ND 14",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 6 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND14.pdf' /tmp/src_2019ND14.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND14.pdf' <page>."
 },
 {
  "id": 17361,
  "cite": "2019 ND 10",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 1 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND10.pdf' /tmp/src_2019ND10.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND10.pdf' <page>."
 },
 {
  "id": 17360,
  "cite": "2019 ND 17",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 10 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND17.pdf' /tmp/src_2019ND17.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND17.pdf' <page>."
 },
 {
  "id": 17359,
  "cite": "2019 ND 25",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 3 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND25.pdf' /tmp/src_2019ND25.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND25.pdf' <page>."
 },
 {
  "id": 17358,
  "cite": "2019 ND 9",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 11 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND9.pdf' /tmp/src_2019ND9.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND9.pdf' <page>."
 }
]

const SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    opinion_id: { type: 'integer' },
    era: { type: 'string' },
    clean: { type: 'boolean' },
    proposals: { type: 'array', items: {
      type: 'object', additionalProperties: false,
      properties: {
        class: { type: 'string', enum: ['ocr_char','ocr_digit','split_join','whitespace','paragraph_seq','heading_seq','missing_text','caption','other'] },
        old_exact: { type: 'string' },
        new_exact: { type: 'string' },
        source_quote: { type: 'string' },
        verified_count: { type: 'integer' },
        source: { type: 'string' },
        evidence: { type: 'string' },
        confidence: { type: 'string', enum: ['high','medium','low'] },
        note: { type: 'string' },
      },
      required: ['class','old_exact','new_exact','source_quote','verified_count','source','confidence'],
    } },
    flags: { type: 'array', items: {
      type: 'object', additionalProperties: false,
      properties: {
        class: { type: 'string' },
        location_quote: { type: 'string' },
        description: { type: 'string' },
        confidence: { type: 'string', enum: ['high','medium','low'] },
      },
      required: ['class','location_quote','description'],
    } },
    coverage_note: { type: 'string' },
  },
  required: ['opinion_id','clean','proposals','flags'],
}

phase('Proof')
const results = await parallel(BATCH.map(op => () =>
  agent(
`You are a meticulous transcription proofreader for an AUTHORITATIVE digital edition of North Dakota Supreme Court opinions — a text the Court itself could adopt. Your job is FIDELITY to what the court actually published. You are NOT an editor: never improve, modernize, or correct the court's own writing.

OPINION: ${op.cite} (DB id ${op.id}). Era: ${op.era}.
Get the DB text:  sqlite3 opinions.db "SELECT text_content FROM opinions WHERE id=${op.id}" > /tmp/db_${op.id}.txt  — read it.
Layer-A structural report (LEADS to verify, not facts): ${op.report}
Authoritative source: ${op.sdesc}
${op.saccess}

ABSOLUTE RULES
1. PROPOSE ONLY — you never change anything.
2. FIDELITY, NOT EDITING — fix only where the DB DIVERGES from the printed source (OCR / ingestion / transcription defects). Never touch the court's own grammar, spelling, punctuation, capitalization, or word choice. If the printed source has a typo or archaic spelling, it STAYS.
3. VERIFY THEN PROPOSE — confirm every change against the source; record source + evidence + confidence. If you cannot verify against a source, do NOT propose a word/number change — emit a flag instead.
4. HIGH-RISK = FLAG, NOT FIX — any change to a NUMBER, citation, pinpoint, date, dollar amount, statute/rule number, case name, or party name goes in flags unless the source positively shows BOTH that the DB is wrong AND the correct value.
5. BYTE-EXACT ANCHORS — each proposal is {old_exact,new_exact}; old_exact copied BYTE-FOR-BYTE from /tmp/db_${op.id}.txt (curly quotes “ ” ‘ ’, en/em dashes, \xa0, \n) occurring EXACTLY ONCE. Verify the count with python3 and set verified_count; DROP any whose count != 1.
5b. SOURCE_QUOTE — EVIDENCE BINDING (REQUIRED). Every proposal must include source_quote: a VERBATIM span copied from the authoritative source that CONTAINS new_exact's corrected text (every word and every digit you added/changed must literally appear in source_quote). This is your proof the fix is real, not inferred. If you cannot copy a source span that contains your new_exact, you have not verified it — emit a FLAG instead of a proposal. Do not paraphrase or reconstruct from memory; quote the source. (A gate rejects any proposal whose added words/digits are absent from its source_quote.)
6. FOOTNOTES are handled by a separate pipeline — do NOT propose footnote edits; only flag a footnote anomaly.
7. PARAGRAPH RESTARTS — a [¶N] restart/repeat (…¶11, ¶1-9, ¶12) is USUALLY the opinion quoting another numbered document (order/statute), NOT duplicated text. Confirm the numbering resumes after the block and the repeated text differs; only flag a restart whose text DUPLICATES the original and never resumes (never auto-fix dedup).
8. FORM-FEED / PAGE FURNITURE — a 0x0C byte (page break) and any running header it precedes (a short case name + "No./Nos./Civil No. <docket>" repeating the caption) are a KNOWN artifact handled by a separate deterministic pass. Do NOT propose removing 0x0C or dropping a running header; ignore them entirely.
9. QUOTE CHARACTERS — the DB uses STRAIGHT ASCII quotes and apostrophes (straight " and ') by policy; the PDFs use curly/typographic. This difference is INTENTIONAL. Do NOT flag or propose any straight-vs-curly quote/apostrophe change. Likewise do NOT propose bracketed footnote-call (a digit in square brackets) or digit-only changes (high-risk, handled separately) — flag at most.
10. FRAGMENTED CITATIONS — markdown-sourced opinions split citations across lines with stray newlines and isolated commas (a comma alone on a line; a volume number on its own line before the reporter; a case name then newline then the year). A separate deterministic citation-rejoin pass OWNS this. Do NOT propose rejoining citations or removing stray newlines/lone-commas in citations; ignore them.
11. MARKUP CONTAMINATION — some opinions carry leftover markup: math-mode $...$, a backslash-P for the pilcrow, ### headings, <sup>...</sup> tags, stray backslashes. This is known contamination handled by a separate pass. Do NOT propose markup fixes; flag at most.
12. SPELLING IS HIGH-RISK — a misspelled-looking word may be the COURT'S OWN published typo, not an ingestion error. Propose a spelling change only if you can positively see the correct spelling in the source; mark confidence medium and state you have NOT image-verified. These are image-verified (rendered glyphs) before any apply.

ERROR CLASSES (scan for all; tag each): ocr_char (l/1/I, rn/m, cl/d, 0/O, ligatures, £→$, ■), ocr_digit (a wrong digit in PROSE only — citations/dates → flag), split_join (wrongly split/fused word), whitespace (mid-sentence hard break to rejoin; 3+ blank lines to collapse; do not reflow). Whitespace is MECHANICAL ONLY and never inserts a newline to wrap a token across a line. ELLIPSES: ND opinions print the compact four-dot form "...."; if the DB shows a spaced ". . . ." but the PDF shows "....", that spacing is an ingestion artifact — propose the compact form (it will be human-reviewed). Match the source; do not impose Bluebook spacing. paragraph_seq, heading_seq, missing_text (a line/phrase dropped at a page/column break, confirmed in source — propose VERBATIM source text or flag), caption (party-name contamination/smushing), other.

METHOD: read the DB text + report; pull the source; read the flagged regions and skim the rest; classify each candidate FIX (source-confirmed, low-risk) vs FLAG (high-risk/unverifiable/ambiguous); build byte-exact edits; verify count==1. If the opinion is clean, return clean:true (a valuable result). BIAS TO FLAG — a wrong fix corrupts authoritative text; a missed one is caught later.`,
    { label: `${op.cite}`, phase: 'Proof', schema: SCHEMA, agentType: 'Explore' }
  ).then(r => r).catch(() => null)
))

const ok = results.filter(Boolean)
log(`proofing proposals: ${ok.length}/${BATCH.length}`)
return ok
