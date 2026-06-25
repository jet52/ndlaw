export const meta = {
  name: 'corpus-proofing-p32',
  description: 'Corpus proofing: transcription-fidelity proofread vs authoritative source (propose + flag, never apply)',
  phases: [{ title: 'Proof', detail: 'read-only agent per opinion: source-verified corrections + flags' }],
}

const BATCH = [
 {
  "id": 19407,
  "cite": "2019 ND 261",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND261.pdf' /tmp/src_2019ND261.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND261.pdf' <page>."
 },
 {
  "id": 19406,
  "cite": "2019 ND 260",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND260.pdf' /tmp/src_2019ND260.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND260.pdf' <page>."
 },
 {
  "id": 19405,
  "cite": "2019 ND 259",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND259.pdf' /tmp/src_2019ND259.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND259.pdf' <page>."
 },
 {
  "id": 19404,
  "cite": "2019 ND 258",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND258.pdf' /tmp/src_2019ND258.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND258.pdf' <page>."
 },
 {
  "id": 19403,
  "cite": "2019 ND 257",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND257.pdf' /tmp/src_2019ND257.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND257.pdf' <page>."
 },
 {
  "id": 19402,
  "cite": "2019 ND 256",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND256.pdf' /tmp/src_2019ND256.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND256.pdf' <page>."
 },
 {
  "id": 19401,
  "cite": "2019 ND 255",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND255.pdf' /tmp/src_2019ND255.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND255.pdf' <page>."
 },
 {
  "id": 19400,
  "cite": "2019 ND 254",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND254.pdf' /tmp/src_2019ND254.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND254.pdf' <page>."
 },
 {
  "id": 19399,
  "cite": "2019 ND 253",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND253.pdf' /tmp/src_2019ND253.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND253.pdf' <page>."
 },
 {
  "id": 19398,
  "cite": "2019 ND 252",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND252.pdf' /tmp/src_2019ND252.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND252.pdf' <page>."
 },
 {
  "id": 19397,
  "cite": "2019 ND 251",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND251.pdf' /tmp/src_2019ND251.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND251.pdf' <page>."
 },
 {
  "id": 19396,
  "cite": "2019 ND 250",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND250.pdf' /tmp/src_2019ND250.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND250.pdf' <page>."
 },
 {
  "id": 19395,
  "cite": "2019 ND 249",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND249.pdf' /tmp/src_2019ND249.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND249.pdf' <page>."
 },
 {
  "id": 19394,
  "cite": "2019 ND 248",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND248.pdf' /tmp/src_2019ND248.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND248.pdf' <page>."
 },
 {
  "id": 19393,
  "cite": "2019 ND 247",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND247.pdf' /tmp/src_2019ND247.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND247.pdf' <page>."
 },
 {
  "id": 19392,
  "cite": "2019 ND 246",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND246.pdf' /tmp/src_2019ND246.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND246.pdf' <page>."
 },
 {
  "id": 19391,
  "cite": "2019 ND 245",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND245.pdf' /tmp/src_2019ND245.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND245.pdf' <page>."
 },
 {
  "id": 19390,
  "cite": "2019 ND 244",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND244.pdf' /tmp/src_2019ND244.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND244.pdf' <page>."
 },
 {
  "id": 19389,
  "cite": "2019 ND 243",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND243.pdf' /tmp/src_2019ND243.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND243.pdf' <page>."
 },
 {
  "id": 19388,
  "cite": "2019 ND 242",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND242.pdf' /tmp/src_2019ND242.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND242.pdf' <page>."
 },
 {
  "id": 19387,
  "cite": "2019 ND 241",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND241.pdf' /tmp/src_2019ND241.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND241.pdf' <page>."
 },
 {
  "id": 19386,
  "cite": "2019 ND 240",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶12->¶14",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND240.pdf' /tmp/src_2019ND240.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND240.pdf' <page>."
 },
 {
  "id": 19385,
  "cite": "2019 ND 239",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND239.pdf' /tmp/src_2019ND239.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND239.pdf' <page>."
 },
 {
  "id": 19384,
  "cite": "2019 ND 238",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND238.pdf' /tmp/src_2019ND238.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND238.pdf' <page>."
 },
 {
  "id": 19383,
  "cite": "2019 ND 237",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND237.pdf' /tmp/src_2019ND237.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND237.pdf' <page>."
 },
 {
  "id": 19382,
  "cite": "2019 ND 236",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND236.pdf' /tmp/src_2019ND236.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND236.pdf' <page>."
 },
 {
  "id": 19381,
  "cite": "2019 ND 235",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND235.pdf' /tmp/src_2019ND235.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND235.pdf' <page>."
 },
 {
  "id": 19380,
  "cite": "2019 ND 234",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND234.pdf' /tmp/src_2019ND234.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND234.pdf' <page>."
 },
 {
  "id": 19379,
  "cite": "2019 ND 230",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND230.pdf' /tmp/src_2019ND230.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND230.pdf' <page>."
 },
 {
  "id": 17574,
  "cite": "2019 ND 231",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 7 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND231.pdf' /tmp/src_2019ND231.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND231.pdf' <page>."
 },
 {
  "id": 17573,
  "cite": "2019 ND 232",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND232.pdf' /tmp/src_2019ND232.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND232.pdf' <page>."
 },
 {
  "id": 17572,
  "cite": "2019 ND 233",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 11 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND233.pdf' /tmp/src_2019ND233.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND233.pdf' <page>."
 },
 {
  "id": 17571,
  "cite": "2019 ND 229",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 3 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND229.pdf' /tmp/src_2019ND229.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND229.pdf' <page>."
 },
 {
  "id": 17570,
  "cite": "2019 ND 228",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 16 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND228.pdf' /tmp/src_2019ND228.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND228.pdf' <page>."
 },
 {
  "id": 17569,
  "cite": "2019 ND 227",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 13 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND227.pdf' /tmp/src_2019ND227.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND227.pdf' <page>."
 },
 {
  "id": 19378,
  "cite": "932 N.W.2d 541",
  "era": "2019 (reporter-era, OCR)",
  "report": "(no structural flags)",
  "sdesc": "the reporter markdown (OCR of the N.W./N.W.2d scan) this opinion was ingested from",
  "saccess": "Source file: /Users/jerod/refs/nd/opin/markdown/2019/2019ND226.md . If a `.doc`, parse footnotes/structure as RTF; if markdown, it is the OCR text — compare carefully, the DB may have diverged from it."
 },
 {
  "id": 19377,
  "cite": "932 N.W.2d 510",
  "era": "2019 (reporter-era, OCR)",
  "report": "(no structural flags)",
  "sdesc": "the reporter markdown (OCR of the N.W./N.W.2d scan) this opinion was ingested from",
  "saccess": "Source file: /Users/jerod/refs/nd/opin/markdown/2019/2019ND225.md . If a `.doc`, parse footnotes/structure as RTF; if markdown, it is the OCR text — compare carefully, the DB may have diverged from it."
 },
 {
  "id": 19376,
  "cite": "932 N.W.2d 523",
  "era": "2019 (reporter-era, OCR)",
  "report": "(no structural flags)",
  "sdesc": "the reporter markdown (OCR of the N.W./N.W.2d scan) this opinion was ingested from",
  "saccess": "Source file: /Users/jerod/refs/nd/opin/markdown/2019/2019ND224.md . If a `.doc`, parse footnotes/structure as RTF; if markdown, it is the OCR text — compare carefully, the DB may have diverged from it."
 },
 {
  "id": 19375,
  "cite": "932 N.W.2d 756",
  "era": "2019 (reporter-era, OCR)",
  "report": "heading_seq: 1->3; whitespace: 7 blank-runs(3+)",
  "sdesc": "the .doc (RTF — Westlaw) this opinion was ingested from",
  "saccess": "Source file: /Users/jerod/refs/nd/opin/N.W.2d/932/0756-NORTH-DAKOTA-PRIVATE-INVESTIGATIVE-AND-SECURITY-BOARD-Plaintiff-Appellant-and-Cross-Appell.doc . If a `.doc`, parse footnotes/structure as RTF; if markdown, it is the OCR text — compare carefully, the DB may have diverged from it."
 },
 {
  "id": 19374,
  "cite": "932 N.W.2d 529",
  "era": "2019 (reporter-era, OCR)",
  "report": "(no structural flags)",
  "sdesc": "the reporter markdown (OCR of the N.W./N.W.2d scan) this opinion was ingested from",
  "saccess": "Source file: /Users/jerod/refs/nd/opin/markdown/2019/2019ND214.md . If a `.doc`, parse footnotes/structure as RTF; if markdown, it is the OCR text — compare carefully, the DB may have diverged from it."
 },
 {
  "id": 17568,
  "cite": "2019 ND 220",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 9 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND220.pdf' /tmp/src_2019ND220.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND220.pdf' <page>."
 },
 {
  "id": 17566,
  "cite": "2019 ND 223",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 9 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND223.pdf' /tmp/src_2019ND223.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND223.pdf' <page>."
 },
 {
  "id": 17565,
  "cite": "2019 ND 222",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 21 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND222.pdf' /tmp/src_2019ND222.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND222.pdf' <page>."
 },
 {
  "id": 17563,
  "cite": "2019 ND 215",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 16 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND215.pdf' /tmp/src_2019ND215.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND215.pdf' <page>."
 },
 {
  "id": 17560,
  "cite": "2019 ND 218",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 20 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND218.pdf' /tmp/src_2019ND218.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND218.pdf' <page>."
 },
 {
  "id": 17558,
  "cite": "2019 ND 217",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 9 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND217.pdf' /tmp/src_2019ND217.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND217.pdf' <page>."
 },
 {
  "id": 17557,
  "cite": "2019 ND 221",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 33 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND221.pdf' /tmp/src_2019ND221.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND221.pdf' <page>."
 },
 {
  "id": 17556,
  "cite": "2019 ND 216",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND216.pdf' /tmp/src_2019ND216.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND216.pdf' <page>."
 },
 {
  "id": 19373,
  "cite": "932 N.W.2d 368",
  "era": "2019 (reporter-era, OCR)",
  "report": "(no structural flags)",
  "sdesc": "the reporter markdown (OCR of the N.W./N.W.2d scan) this opinion was ingested from",
  "saccess": "Source file: /Users/jerod/refs/nd/opin/markdown/2019/2019ND213.md . If a `.doc`, parse footnotes/structure as RTF; if markdown, it is the OCR text — compare carefully, the DB may have diverged from it."
 },
 {
  "id": 17554,
  "cite": "2019 ND 212",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND212.pdf' /tmp/src_2019ND212.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND212.pdf' <page>."
 },
 {
  "id": 17553,
  "cite": "2019 ND 211",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 15 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND211.pdf' /tmp/src_2019ND211.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND211.pdf' <page>."
 },
 {
  "id": 17552,
  "cite": "2019 ND 210",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 7 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND210.pdf' /tmp/src_2019ND210.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND210.pdf' <page>."
 },
 {
  "id": 17551,
  "cite": "2019 ND 208",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND208.pdf' /tmp/src_2019ND208.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND208.pdf' <page>."
 },
 {
  "id": 17550,
  "cite": "2019 ND 209",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND209.pdf' /tmp/src_2019ND209.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND209.pdf' <page>."
 },
 {
  "id": 17549,
  "cite": "2019 ND 207",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 6 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND207.pdf' /tmp/src_2019ND207.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND207.pdf' <page>."
 },
 {
  "id": 19372,
  "cite": "932 N.W.2d 101",
  "era": "2019 (reporter-era, OCR)",
  "report": "whitespace: 3 blank-runs(3+)",
  "sdesc": "the .doc (RTF — Westlaw) this opinion was ingested from",
  "saccess": "Source file: /Users/jerod/refs/nd/opin/N.W.2d/932/0101-STATE-of-North-Dakota-Plaintiff-and-Appellee-v-Jessica-Dawn-NELSON-Defendant-and-Appellant.doc . If a `.doc`, parse footnotes/structure as RTF; if markdown, it is the OCR text — compare carefully, the DB may have diverged from it."
 },
 {
  "id": 19371,
  "cite": "931 N.W.2d 504",
  "era": "2019 (reporter-era, OCR)",
  "report": "(no structural flags)",
  "sdesc": "the reporter markdown (OCR of the N.W./N.W.2d scan) this opinion was ingested from",
  "saccess": "Source file: /Users/jerod/refs/nd/opin/markdown/2019/2019ND200.md . If a `.doc`, parse footnotes/structure as RTF; if markdown, it is the OCR text — compare carefully, the DB may have diverged from it."
 },
 {
  "id": 19370,
  "cite": "931 N.W.2d 498",
  "era": "2019 (reporter-era, OCR)",
  "report": "whitespace: 4 blank-runs(3+)",
  "sdesc": "the .doc (RTF — Westlaw) this opinion was ingested from",
  "saccess": "Source file: /Users/jerod/refs/nd/opin/N.W.2d/931/0498-Juan-FACIO-Petitioner-and-Appellee-v-NORTH-DAKOTA-DEPARTMENT-OF-TRANSPORTATION-Respondent-.doc . If a `.doc`, parse footnotes/structure as RTF; if markdown, it is the OCR text — compare carefully, the DB may have diverged from it."
 },
 {
  "id": 17575,
  "cite": "2019 ND 203",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 13 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND203.pdf' /tmp/src_2019ND203.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND203.pdf' <page>."
 },
 {
  "id": 17548,
  "cite": "2019 ND 206",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 25 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND206.pdf' /tmp/src_2019ND206.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND206.pdf' <page>."
 },
 {
  "id": 17546,
  "cite": "2019 ND 202",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 24 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND202.pdf' /tmp/src_2019ND202.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND202.pdf' <page>."
 },
 {
  "id": 17545,
  "cite": "2019 ND 201",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 18 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND201.pdf' /tmp/src_2019ND201.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND201.pdf' <page>."
 },
 {
  "id": 17544,
  "cite": "2019 ND 205",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 8 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND205.pdf' /tmp/src_2019ND205.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND205.pdf' <page>."
 },
 {
  "id": 17543,
  "cite": "2019 ND 197",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 21 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND197.pdf' /tmp/src_2019ND197.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND197.pdf' <page>."
 },
 {
  "id": 17540,
  "cite": "2019 ND 198",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 37 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND198.pdf' /tmp/src_2019ND198.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND198.pdf' <page>."
 },
 {
  "id": 17539,
  "cite": "2019 ND 196",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 5 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND196.pdf' /tmp/src_2019ND196.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND196.pdf' <page>."
 },
 {
  "id": 19369,
  "cite": "931 N.W.2d 211",
  "era": "2019 (reporter-era, OCR)",
  "report": "(no structural flags)",
  "sdesc": "the reporter markdown (OCR of the N.W./N.W.2d scan) this opinion was ingested from",
  "saccess": "Source file: /Users/jerod/refs/nd/opin/markdown/2019/2019ND195.md . If a `.doc`, parse footnotes/structure as RTF; if markdown, it is the OCR text — compare carefully, the DB may have diverged from it."
 },
 {
  "id": 19368,
  "cite": "2019 ND 182",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND182.pdf' /tmp/src_2019ND182.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND182.pdf' <page>."
 },
 {
  "id": 17538,
  "cite": "2019 ND 193",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 16 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND193.pdf' /tmp/src_2019ND193.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND193.pdf' <page>."
 },
 {
  "id": 17537,
  "cite": "2019 ND 183",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND183.pdf' /tmp/src_2019ND183.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND183.pdf' <page>."
 },
 {
  "id": 17536,
  "cite": "2019 ND 186",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 16 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND186.pdf' /tmp/src_2019ND186.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND186.pdf' <page>."
 },
 {
  "id": 17535,
  "cite": "2019 ND 192",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 2 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND192.pdf' /tmp/src_2019ND192.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND192.pdf' <page>."
 },
 {
  "id": 17534,
  "cite": "2019 ND 187",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 7 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND187.pdf' /tmp/src_2019ND187.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND187.pdf' <page>."
 },
 {
  "id": 17533,
  "cite": "2019 ND 188",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 4 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND188.pdf' /tmp/src_2019ND188.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND188.pdf' <page>."
 },
 {
  "id": 17531,
  "cite": "2019 ND 184",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 24 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND184.pdf' /tmp/src_2019ND184.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND184.pdf' <page>."
 },
 {
  "id": 17530,
  "cite": "2019 ND 194",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 18 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND194.pdf' /tmp/src_2019ND194.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND194.pdf' <page>."
 },
 {
  "id": 17529,
  "cite": "2019 ND 189",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 7 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND189.pdf' /tmp/src_2019ND189.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND189.pdf' <page>."
 },
 {
  "id": 17522,
  "cite": "2019 ND 181",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 8 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND181.pdf' /tmp/src_2019ND181.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND181.pdf' <page>."
 },
 {
  "id": 17521,
  "cite": "2019 ND 190",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 16 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND190.pdf' /tmp/src_2019ND190.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND190.pdf' <page>."
 },
 {
  "id": 17520,
  "cite": "2019 ND 191",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 18 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND191.pdf' /tmp/src_2019ND191.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND191.pdf' <page>."
 },
 {
  "id": 17519,
  "cite": "2019 ND 185",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 6 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND185.pdf' /tmp/src_2019ND185.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND185.pdf' <page>."
 },
 {
  "id": 17518,
  "cite": "2019 ND 180",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 10 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND180.pdf' /tmp/src_2019ND180.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND180.pdf' <page>."
 },
 {
  "id": 17517,
  "cite": "2019 ND 178",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 8 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND178.pdf' /tmp/src_2019ND178.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND178.pdf' <page>."
 },
 {
  "id": 17516,
  "cite": "2019 ND 179",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 2 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND179.pdf' /tmp/src_2019ND179.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND179.pdf' <page>."
 },
 {
  "id": 17515,
  "cite": "2019 ND 177",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 4 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND177.pdf' /tmp/src_2019ND177.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND177.pdf' <page>."
 },
 {
  "id": 19367,
  "cite": "930 N.W.2d 77",
  "era": "2019 (reporter-era, OCR)",
  "report": "whitespace: 4 blank-runs(3+)",
  "sdesc": "the .doc (RTF — Westlaw) this opinion was ingested from",
  "saccess": "Source file: /Users/jerod/refs/nd/opin/N.W.2d/930/0077-STATE-of-North-Dakota-Plaintiff-and-Appellee-v-Michael-Benjamin-WILLS-Defendant-and-Appell.doc . If a `.doc`, parse footnotes/structure as RTF; if markdown, it is the OCR text — compare carefully, the DB may have diverged from it."
 },
 {
  "id": 19366,
  "cite": "930 N.W.2d 84",
  "era": "2019 (reporter-era, OCR)",
  "report": "(no structural flags)",
  "sdesc": "the reporter markdown (OCR of the N.W./N.W.2d scan) this opinion was ingested from",
  "saccess": "Source file: /Users/jerod/refs/nd/opin/markdown/2019/2019ND172.md . If a `.doc`, parse footnotes/structure as RTF; if markdown, it is the OCR text — compare carefully, the DB may have diverged from it."
 },
 {
  "id": 19365,
  "cite": "930 N.W.2d 181",
  "era": "2019 (reporter-era, OCR)",
  "report": "(no structural flags)",
  "sdesc": "the reporter markdown (OCR of the N.W./N.W.2d scan) this opinion was ingested from",
  "saccess": "Source file: /Users/jerod/refs/nd/opin/markdown/2019/2019ND171.md . If a `.doc`, parse footnotes/structure as RTF; if markdown, it is the OCR text — compare carefully, the DB may have diverged from it."
 },
 {
  "id": 19364,
  "cite": "930 N.W.2d 162",
  "era": "2019 (reporter-era, OCR)",
  "report": "(no structural flags)",
  "sdesc": "the reporter markdown (OCR of the N.W./N.W.2d scan) this opinion was ingested from",
  "saccess": "Source file: /Users/jerod/refs/nd/opin/markdown/2019/2019ND169.md . If a `.doc`, parse footnotes/structure as RTF; if markdown, it is the OCR text — compare carefully, the DB may have diverged from it."
 },
 {
  "id": 19363,
  "cite": "930 N.W.2d 166",
  "era": "2019 (reporter-era, OCR)",
  "report": "heading_seq: 1->3; whitespace: 4 blank-runs(3+)",
  "sdesc": "the .doc (RTF — Westlaw) this opinion was ingested from",
  "saccess": "Source file: /Users/jerod/refs/nd/opin/N.W.2d/930/0166-In-the-INTEREST-OF-TAG-Julie-Lawyer-Petitioner-and-Appellee-v-TAG-Respondent-and-Appellant.doc . If a `.doc`, parse footnotes/structure as RTF; if markdown, it is the OCR text — compare carefully, the DB may have diverged from it."
 },
 {
  "id": 19362,
  "cite": "930 N.W.2d 171",
  "era": "2019 (reporter-era, OCR)",
  "report": "whitespace: 5 blank-runs(3+)",
  "sdesc": "the .doc (RTF — Westlaw) this opinion was ingested from",
  "saccess": "Source file: /Users/jerod/refs/nd/opin/N.W.2d/930/0171-STATE-of-North-Dakota-Plaintiff-and-Appellee-v-Alexander-James-HOLLIS-Defendant-and-Appell.doc . If a `.doc`, parse footnotes/structure as RTF; if markdown, it is the OCR text — compare carefully, the DB may have diverged from it."
 },
 {
  "id": 19360,
  "cite": "930 N.W.2d 136",
  "era": "2019 (reporter-era, OCR)",
  "report": "(no structural flags)",
  "sdesc": "the reporter markdown (OCR of the N.W./N.W.2d scan) this opinion was ingested from",
  "saccess": "Source file: /Users/jerod/refs/nd/opin/markdown/2019/2019ND153.md . If a `.doc`, parse footnotes/structure as RTF; if markdown, it is the OCR text — compare carefully, the DB may have diverged from it."
 },
 {
  "id": 19359,
  "cite": "2019 ND 151",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND151.pdf' /tmp/src_2019ND151.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND151.pdf' <page>."
 },
 {
  "id": 17528,
  "cite": "2019 ND 159",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 21 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND159.pdf' /tmp/src_2019ND159.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND159.pdf' <page>."
 },
 {
  "id": 17527,
  "cite": "2019 ND 168",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 6 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND168.pdf' /tmp/src_2019ND168.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND168.pdf' <page>."
 },
 {
  "id": 17526,
  "cite": "2019 ND 156",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 3 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND156.pdf' /tmp/src_2019ND156.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND156.pdf' <page>."
 },
 {
  "id": 17525,
  "cite": "2019 ND 165",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 8 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND165.pdf' /tmp/src_2019ND165.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND165.pdf' <page>."
 },
 {
  "id": 17514,
  "cite": "2019 ND 154",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 18 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND154.pdf' /tmp/src_2019ND154.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND154.pdf' <page>."
 },
 {
  "id": 17513,
  "cite": "2019 ND 155",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 9 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND155.pdf' /tmp/src_2019ND155.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND155.pdf' <page>."
 },
 {
  "id": 17512,
  "cite": "2019 ND 166",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 7 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND166.pdf' /tmp/src_2019ND166.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND166.pdf' <page>."
 },
 {
  "id": 17511,
  "cite": "2019 ND 174",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 18 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND174.pdf' /tmp/src_2019ND174.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND174.pdf' <page>."
 },
 {
  "id": 17510,
  "cite": "2019 ND 173",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 12 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND173.pdf' /tmp/src_2019ND173.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND173.pdf' <page>."
 },
 {
  "id": 17508,
  "cite": "2019 ND 162",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 7 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND162.pdf' /tmp/src_2019ND162.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND162.pdf' <page>."
 },
 {
  "id": 17504,
  "cite": "2019 ND 175",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 49 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND175.pdf' /tmp/src_2019ND175.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND175.pdf' <page>."
 },
 {
  "id": 17503,
  "cite": "2019 ND 164",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND164.pdf' /tmp/src_2019ND164.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND164.pdf' <page>."
 },
 {
  "id": 17501,
  "cite": "2019 ND 158",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 2 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND158.pdf' /tmp/src_2019ND158.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND158.pdf' <page>."
 },
 {
  "id": 17500,
  "cite": "2019 ND 157",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 7 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND157.pdf' /tmp/src_2019ND157.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND157.pdf' <page>."
 },
 {
  "id": 17499,
  "cite": "2019 ND 160",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 6 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND160.pdf' /tmp/src_2019ND160.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND160.pdf' <page>."
 },
 {
  "id": 17498,
  "cite": "2019 ND 170",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND170.pdf' /tmp/src_2019ND170.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND170.pdf' <page>."
 },
 {
  "id": 17497,
  "cite": "2019 ND 161",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 19 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND161.pdf' /tmp/src_2019ND161.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND161.pdf' <page>."
 },
 {
  "id": 17485,
  "cite": "2019 ND 152",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND152.pdf' /tmp/src_2019ND152.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND152.pdf' <page>."
 },
 {
  "id": 17484,
  "cite": "2019 ND 148",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND148.pdf' /tmp/src_2019ND148.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND148.pdf' <page>."
 },
 {
  "id": 17483,
  "cite": "2019 ND 150",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND150.pdf' /tmp/src_2019ND150.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND150.pdf' <page>."
 },
 {
  "id": 17482,
  "cite": "2019 ND 149",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND149.pdf' /tmp/src_2019ND149.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND149.pdf' <page>."
 },
 {
  "id": 17481,
  "cite": "2019 ND 147",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "starpage_seq: *780 *456 *457; whitespace: 42 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND147.pdf' /tmp/src_2019ND147.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND147.pdf' <page>."
 },
 {
  "id": 17480,
  "cite": "2019 ND 145",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 7 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND145.pdf' /tmp/src_2019ND145.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND145.pdf' <page>."
 },
 {
  "id": 17479,
  "cite": "2019 ND 146",
  "era": "2019 (modern, PDF-authoritative)",
  "report": "whitespace: 3 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND146.pdf' /tmp/src_2019ND146.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2019/2019ND146.pdf' <page>."
 },
 {
  "id": 19358,
  "cite": "927 N.W.2d 452",
  "era": "2019 (reporter-era, OCR)",
  "report": "(no structural flags)",
  "sdesc": "the reporter markdown (OCR of the N.W./N.W.2d scan) this opinion was ingested from",
  "saccess": "Source file: /Users/jerod/refs/nd/opin/markdown/2019/2019ND143.md . If a `.doc`, parse footnotes/structure as RTF; if markdown, it is the OCR text — compare carefully, the DB may have diverged from it."
 },
 {
  "id": 19357,
  "cite": "927 N.W.2d 104",
  "era": "2019 (reporter-era, OCR)",
  "report": "whitespace: 5 blank-runs(3+)",
  "sdesc": "the .doc (RTF — Westlaw) this opinion was ingested from",
  "saccess": "Source file: /Users/jerod/refs/nd/opin/N.W.2d/927/0104-Bruce-Wayne-LEE-Plaintiff-and-Appellant-v-Kimberly-Marie-LEE-Defendant-and-Appellee-No-201.doc . If a `.doc`, parse footnotes/structure as RTF; if markdown, it is the OCR text — compare carefully, the DB may have diverged from it."
 },
 {
  "id": 19356,
  "cite": "927 N.W.2d 474",
  "era": "2019 (reporter-era, OCR)",
  "report": "(no structural flags)",
  "sdesc": "the reporter markdown (OCR of the N.W./N.W.2d scan) this opinion was ingested from",
  "saccess": "Source file: /Users/jerod/refs/nd/opin/markdown/2019/2019ND141.md . If a `.doc`, parse footnotes/structure as RTF; if markdown, it is the OCR text — compare carefully, the DB may have diverged from it."
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
