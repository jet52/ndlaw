export const meta = {
  name: 'corpus-proofing-p22',
  description: 'Corpus proofing: transcription-fidelity proofread vs authoritative source (propose + flag, never apply)',
  phases: [{ title: 'Proof', detail: 'read-only agent per opinion: source-verified corrections + flags' }],
}

const BATCH = [
 {
  "id": 19824,
  "cite": "2023 ND 6",
  "era": "2023 (modern, PDF-authoritative)",
  "report": "whitespace: 1 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2023/2023ND6.pdf' /tmp/src_2023ND6.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2023/2023ND6.pdf' <page>."
 },
 {
  "id": 19818,
  "cite": "2023 ND 4",
  "era": "2023 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2023/2023ND4.pdf' /tmp/src_2023ND4.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2023/2023ND4.pdf' <page>."
 },
 {
  "id": 19711,
  "cite": "2022 ND 139",
  "era": "2023 (reporter-era, OCR)",
  "report": "(no structural flags)",
  "sdesc": "the reporter markdown (OCR of the N.W./N.W.2d scan) this opinion was ingested from",
  "saccess": "Source file: /Users/jerod/refs/nd/opin/markdown/2023/2023ND1.md . If a `.doc`, parse footnotes/structure as RTF; if markdown, it is the OCR text — compare carefully, the DB may have diverged from it."
 },
 {
  "id": 18125,
  "cite": "2023 ND 3",
  "era": "2023 (modern, PDF-authoritative)",
  "report": "whitespace: 5 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2023/2023ND3.pdf' /tmp/src_2023ND3.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2023/2023ND3.pdf' <page>."
 },
 {
  "id": 18124,
  "cite": "2023 ND 2",
  "era": "2023 (modern, PDF-authoritative)",
  "report": "whitespace: 14 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2023/2023ND2.pdf' /tmp/src_2023ND2.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2023/2023ND2.pdf' <page>."
 },
 {
  "id": 18123,
  "cite": "2023 ND 7",
  "era": "2023 (modern, PDF-authoritative)",
  "report": "whitespace: 13 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2023/2023ND7.pdf' /tmp/src_2023ND7.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2023/2023ND7.pdf' <page>."
 },
 {
  "id": 18122,
  "cite": "2023 ND 5",
  "era": "2023 (modern, PDF-authoritative)",
  "report": "whitespace: 5 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2023/2023ND5.pdf' /tmp/src_2023ND5.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2023/2023ND5.pdf' <page>."
 },
 {
  "id": 19693,
  "cite": "2022 ND 236",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 4 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND236.pdf' /tmp/src_2022ND236.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND236.pdf' <page>."
 },
 {
  "id": 19692,
  "cite": "2022 ND 235",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND235.pdf' /tmp/src_2022ND235.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND235.pdf' <page>."
 },
 {
  "id": 18121,
  "cite": "2022 ND 230",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 10 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND230.pdf' /tmp/src_2022ND230.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND230.pdf' <page>."
 },
 {
  "id": 18120,
  "cite": "2022 ND 229",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "heading_seq: 3->5; whitespace: 12 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND229.pdf' /tmp/src_2022ND229.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND229.pdf' <page>."
 },
 {
  "id": 18119,
  "cite": "2022 ND 234",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "heading_seq: 3->5; whitespace: 8 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND234.pdf' /tmp/src_2022ND234.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND234.pdf' <page>."
 },
 {
  "id": 18118,
  "cite": "2022 ND 233",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 9 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND233.pdf' /tmp/src_2022ND233.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND233.pdf' <page>."
 },
 {
  "id": 18117,
  "cite": "2022 ND 232",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 6 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND232.pdf' /tmp/src_2022ND232.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND232.pdf' <page>."
 },
 {
  "id": 18116,
  "cite": "2022 ND 238",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 5 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND238.pdf' /tmp/src_2022ND238.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND238.pdf' <page>."
 },
 {
  "id": 18115,
  "cite": "2022 ND 237",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 5 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND237.pdf' /tmp/src_2022ND237.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND237.pdf' <page>."
 },
 {
  "id": 18114,
  "cite": "2022 ND 231",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 7 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND231.pdf' /tmp/src_2022ND231.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND231.pdf' <page>."
 },
 {
  "id": 18113,
  "cite": "2022 ND 228",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 6 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND228.pdf' /tmp/src_2022ND228.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND228.pdf' <page>."
 },
 {
  "id": 19691,
  "cite": "2022 ND 227",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND227.pdf' /tmp/src_2022ND227.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND227.pdf' <page>."
 },
 {
  "id": 19690,
  "cite": "2022 ND 225",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND225.pdf' /tmp/src_2022ND225.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND225.pdf' <page>."
 },
 {
  "id": 19689,
  "cite": "2022 ND 215",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶36->¶40",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND215.pdf' /tmp/src_2022ND215.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND215.pdf' <page>."
 },
 {
  "id": 19688,
  "cite": "2022 ND 214",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 11 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND214.pdf' /tmp/src_2022ND214.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND214.pdf' <page>."
 },
 {
  "id": 19687,
  "cite": "2022 ND 213",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND213.pdf' /tmp/src_2022ND213.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND213.pdf' <page>."
 },
 {
  "id": 18111,
  "cite": "2022 ND 224",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 6 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND224.pdf' /tmp/src_2022ND224.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND224.pdf' <page>."
 },
 {
  "id": 18110,
  "cite": "2022 ND 217",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 9 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND217.pdf' /tmp/src_2022ND217.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND217.pdf' <page>."
 },
 {
  "id": 18109,
  "cite": "2022 ND 222",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 5 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND222.pdf' /tmp/src_2022ND222.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND222.pdf' <page>."
 },
 {
  "id": 18108,
  "cite": "2022 ND 212",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 17 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND212.pdf' /tmp/src_2022ND212.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND212.pdf' <page>."
 },
 {
  "id": 18107,
  "cite": "2022 ND 218",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 5 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND218.pdf' /tmp/src_2022ND218.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND218.pdf' <page>."
 },
 {
  "id": 18106,
  "cite": "2022 ND 219",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 6 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND219.pdf' /tmp/src_2022ND219.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND219.pdf' <page>."
 },
 {
  "id": 18105,
  "cite": "2022 ND 220",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 7 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND220.pdf' /tmp/src_2022ND220.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND220.pdf' <page>."
 },
 {
  "id": 18104,
  "cite": "2022 ND 221",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 8 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND221.pdf' /tmp/src_2022ND221.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND221.pdf' <page>."
 },
 {
  "id": 18103,
  "cite": "2022 ND 216",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 19 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND216.pdf' /tmp/src_2022ND216.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND216.pdf' <page>."
 },
 {
  "id": 18102,
  "cite": "2022 ND 223",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 5 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND223.pdf' /tmp/src_2022ND223.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND223.pdf' <page>."
 },
 {
  "id": 18101,
  "cite": "2022 ND 226",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 4 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND226.pdf' /tmp/src_2022ND226.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND226.pdf' <page>."
 },
 {
  "id": 18100,
  "cite": "2022 ND 206",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 9 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND206.pdf' /tmp/src_2022ND206.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND206.pdf' <page>."
 },
 {
  "id": 18099,
  "cite": "2022 ND 205",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 14 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND205.pdf' /tmp/src_2022ND205.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND205.pdf' <page>."
 },
 {
  "id": 18098,
  "cite": "2022 ND 208",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 19 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND208.pdf' /tmp/src_2022ND208.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND208.pdf' <page>."
 },
 {
  "id": 18097,
  "cite": "2022 ND 210",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 6 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND210.pdf' /tmp/src_2022ND210.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND210.pdf' <page>."
 },
 {
  "id": 18096,
  "cite": "2022 ND 207",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 9 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND207.pdf' /tmp/src_2022ND207.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND207.pdf' <page>."
 },
 {
  "id": 18095,
  "cite": "2022 ND 211",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 15 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND211.pdf' /tmp/src_2022ND211.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND211.pdf' <page>."
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
        verified_count: { type: 'integer' },
        source: { type: 'string' },
        evidence: { type: 'string' },
        confidence: { type: 'string', enum: ['high','medium','low'] },
        note: { type: 'string' },
      },
      required: ['class','old_exact','new_exact','verified_count','source','confidence'],
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
6. FOOTNOTES are handled by a separate pipeline — do NOT propose footnote edits; only flag a footnote anomaly.
7. PARAGRAPH RESTARTS — a [¶N] restart/repeat (…¶11, ¶1-9, ¶12) is USUALLY the opinion quoting another numbered document (order/statute), NOT duplicated text. Confirm the numbering resumes after the block and the repeated text differs; only flag a restart whose text DUPLICATES the original and never resumes (never auto-fix dedup).
8. FORM-FEED / PAGE FURNITURE — a 0x0C byte (page break) and any running header it precedes (a short case name + "No./Nos./Civil No. <docket>" repeating the caption) are a KNOWN artifact handled by a separate deterministic pass. Do NOT propose removing 0x0C or dropping a running header; ignore them entirely.
9. QUOTE CHARACTERS — the DB uses STRAIGHT ASCII quotes and apostrophes (straight " and ') by policy; the PDFs use curly/typographic. This difference is INTENTIONAL. Do NOT flag or propose any straight-vs-curly quote/apostrophe change. Likewise do NOT propose bracketed footnote-call (a digit in square brackets) or digit-only changes (high-risk, handled separately) — flag at most.

ERROR CLASSES (scan for all; tag each): ocr_char (l/1/I, rn/m, cl/d, 0/O, ligatures, £→$, ■), ocr_digit (a wrong digit in PROSE only — citations/dates → flag), split_join (wrongly split/fused word), whitespace (mid-sentence hard break to rejoin; 3+ blank lines to collapse; do not reflow). Whitespace is MECHANICAL ONLY and never inserts a newline to wrap a token across a line. ELLIPSES: ND opinions print the compact four-dot form "...."; if the DB shows a spaced ". . . ." but the PDF shows "....", that spacing is an ingestion artifact — propose the compact form (it will be human-reviewed). Match the source; do not impose Bluebook spacing. paragraph_seq, heading_seq, missing_text (a line/phrase dropped at a page/column break, confirmed in source — propose VERBATIM source text or flag), caption (party-name contamination/smushing), other.

METHOD: read the DB text + report; pull the source; read the flagged regions and skim the rest; classify each candidate FIX (source-confirmed, low-risk) vs FLAG (high-risk/unverifiable/ambiguous); build byte-exact edits; verify count==1. If the opinion is clean, return clean:true (a valuable result). BIAS TO FLAG — a wrong fix corrupts authoritative text; a missed one is caught later.`,
    { label: `${op.cite}`, phase: 'Proof', schema: SCHEMA, agentType: 'Explore' }
  ).then(r => r).catch(() => null)
))

const ok = results.filter(Boolean)
log(`proofing proposals: ${ok.length}/${BATCH.length}`)
return ok
