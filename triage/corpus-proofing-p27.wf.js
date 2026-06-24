export const meta = {
  name: 'corpus-proofing-p27',
  description: 'Corpus proofing: transcription-fidelity proofread vs authoritative source (propose + flag, never apply)',
  phases: [{ title: 'Proof', detail: 'read-only agent per opinion: source-verified corrections + flags' }],
}

const BATCH = [
 {
  "id": 17975,
  "cite": "2022 ND 47",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 5 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND47.pdf' /tmp/src_2022ND47.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND47.pdf' <page>."
 },
 {
  "id": 17974,
  "cite": "2022 ND 46",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 11 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND46.pdf' /tmp/src_2022ND46.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND46.pdf' <page>."
 },
 {
  "id": 19700,
  "cite": "2022 ND 42",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND42.pdf' /tmp/src_2022ND42.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND42.pdf' <page>."
 },
 {
  "id": 19699,
  "cite": "2022 ND 37",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND37.pdf' /tmp/src_2022ND37.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND37.pdf' <page>."
 },
 {
  "id": 19698,
  "cite": "2022 ND 35",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND35.pdf' /tmp/src_2022ND35.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND35.pdf' <page>."
 },
 {
  "id": 19697,
  "cite": "2022 ND 34",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND34.pdf' /tmp/src_2022ND34.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND34.pdf' <page>."
 },
 {
  "id": 19696,
  "cite": "2022 ND 33",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND33.pdf' /tmp/src_2022ND33.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND33.pdf' <page>."
 },
 {
  "id": 17972,
  "cite": "2022 ND 31",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 15 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND31.pdf' /tmp/src_2022ND31.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND31.pdf' <page>."
 },
 {
  "id": 17971,
  "cite": "2022 ND 38",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 9 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND38.pdf' /tmp/src_2022ND38.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND38.pdf' <page>."
 },
 {
  "id": 17970,
  "cite": "2022 ND 41",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 10 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND41.pdf' /tmp/src_2022ND41.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND41.pdf' <page>."
 },
 {
  "id": 17969,
  "cite": "2022 ND 39",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 13 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND39.pdf' /tmp/src_2022ND39.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND39.pdf' <page>."
 },
 {
  "id": 17968,
  "cite": "2022 ND 30",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 14 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND30.pdf' /tmp/src_2022ND30.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND30.pdf' <page>."
 },
 {
  "id": 17967,
  "cite": "2022 ND 36",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 4 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND36.pdf' /tmp/src_2022ND36.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND36.pdf' <page>."
 },
 {
  "id": 17966,
  "cite": "2022 ND 40",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 11 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND40.pdf' /tmp/src_2022ND40.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND40.pdf' <page>."
 },
 {
  "id": 17965,
  "cite": "2022 ND 29",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 13 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND29.pdf' /tmp/src_2022ND29.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND29.pdf' <page>."
 },
 {
  "id": 17964,
  "cite": "2022 ND 32",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 15 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND32.pdf' /tmp/src_2022ND32.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND32.pdf' <page>."
 },
 {
  "id": 17963,
  "cite": "2022 ND 28",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 13 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND28.pdf' /tmp/src_2022ND28.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND28.pdf' <page>."
 },
 {
  "id": 19694,
  "cite": "2022 ND 27",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND27.pdf' /tmp/src_2022ND27.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND27.pdf' <page>."
 },
 {
  "id": 17955,
  "cite": "2022 ND 25",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 5 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND25.pdf' /tmp/src_2022ND25.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND25.pdf' <page>."
 },
 {
  "id": 17954,
  "cite": "2022 ND 26",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 5 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND26.pdf' /tmp/src_2022ND26.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND26.pdf' <page>."
 },
 {
  "id": 17953,
  "cite": "2022 ND 23",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 6 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND23.pdf' /tmp/src_2022ND23.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND23.pdf' <page>."
 },
 {
  "id": 17952,
  "cite": "2022 ND 22",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 8 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND22.pdf' /tmp/src_2022ND22.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND22.pdf' <page>."
 },
 {
  "id": 17951,
  "cite": "2022 ND 19",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND19.pdf' /tmp/src_2022ND19.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND19.pdf' <page>."
 },
 {
  "id": 17950,
  "cite": "2022 ND 24",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND24.pdf' /tmp/src_2022ND24.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND24.pdf' <page>."
 },
 {
  "id": 17949,
  "cite": "2022 ND 18",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 17 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND18.pdf' /tmp/src_2022ND18.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND18.pdf' <page>."
 },
 {
  "id": 17948,
  "cite": "2022 ND 21",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 4 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND21.pdf' /tmp/src_2022ND21.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND21.pdf' <page>."
 },
 {
  "id": 17947,
  "cite": "2022 ND 20",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 8 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND20.pdf' /tmp/src_2022ND20.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND20.pdf' <page>."
 },
 {
  "id": 17946,
  "cite": "2022 ND 17",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 9 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND17.pdf' /tmp/src_2022ND17.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND17.pdf' <page>."
 },
 {
  "id": 17945,
  "cite": "2022 ND 16",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 9 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND16.pdf' /tmp/src_2022ND16.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND16.pdf' <page>."
 },
 {
  "id": 19695,
  "cite": "2022 ND 3",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 1 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND3.pdf' /tmp/src_2022ND3.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND3.pdf' <page>."
 },
 {
  "id": 19638,
  "cite": "2022 ND 10",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND10.pdf' /tmp/src_2022ND10.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND10.pdf' <page>."
 },
 {
  "id": 17944,
  "cite": "2022 ND 13",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 9 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND13.pdf' /tmp/src_2022ND13.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND13.pdf' <page>."
 },
 {
  "id": 17943,
  "cite": "2022 ND 11",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 9 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND11.pdf' /tmp/src_2022ND11.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND11.pdf' <page>."
 },
 {
  "id": 17942,
  "cite": "2022 ND 2",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 12 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND2.pdf' /tmp/src_2022ND2.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND2.pdf' <page>."
 },
 {
  "id": 17941,
  "cite": "2022 ND 12",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 7 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND12.pdf' /tmp/src_2022ND12.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND12.pdf' <page>."
 },
 {
  "id": 17940,
  "cite": "2022 ND 5",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 4 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND5.pdf' /tmp/src_2022ND5.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND5.pdf' <page>."
 },
 {
  "id": 17939,
  "cite": "2022 ND 8",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 9 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND8.pdf' /tmp/src_2022ND8.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND8.pdf' <page>."
 },
 {
  "id": 17938,
  "cite": "2022 ND 14",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 4 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND14.pdf' /tmp/src_2022ND14.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND14.pdf' <page>."
 },
 {
  "id": 17937,
  "cite": "2022 ND 7",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 14 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND7.pdf' /tmp/src_2022ND7.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND7.pdf' <page>."
 },
 {
  "id": 17936,
  "cite": "2022 ND 6",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 5 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND6.pdf' /tmp/src_2022ND6.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND6.pdf' <page>."
 },
 {
  "id": 17935,
  "cite": "2022 ND 15",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 11 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND15.pdf' /tmp/src_2022ND15.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND15.pdf' <page>."
 },
 {
  "id": 17934,
  "cite": "2022 ND 9",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 5 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND9.pdf' /tmp/src_2022ND9.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND9.pdf' <page>."
 },
 {
  "id": 17933,
  "cite": "2022 ND 1",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 12 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND1.pdf' /tmp/src_2022ND1.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND1.pdf' <page>."
 },
 {
  "id": 17932,
  "cite": "2022 ND 4",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "whitespace: 6 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND4.pdf' /tmp/src_2022ND4.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND4.pdf' <page>."
 },
 {
  "id": 19707,
  "cite": "2022 ND 69",
  "era": "2022 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND69.pdf' /tmp/src_2022ND69.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2022/2022ND69.pdf' <page>."
 },
 {
  "id": 17931,
  "cite": "2021 ND 229",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 9 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND229.pdf' /tmp/src_2021ND229.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND229.pdf' <page>."
 },
 {
  "id": 17930,
  "cite": "2021 ND 232",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 6 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND232.pdf' /tmp/src_2021ND232.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND232.pdf' <page>."
 },
 {
  "id": 17929,
  "cite": "2021 ND 231",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 4 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND231.pdf' /tmp/src_2021ND231.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND231.pdf' <page>."
 },
 {
  "id": 17928,
  "cite": "2021 ND 235",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 7 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND235.pdf' /tmp/src_2021ND235.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND235.pdf' <page>."
 },
 {
  "id": 17927,
  "cite": "2021 ND 230",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 4 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND230.pdf' /tmp/src_2021ND230.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND230.pdf' <page>."
 },
 {
  "id": 17926,
  "cite": "2021 ND 240",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 9 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND240.pdf' /tmp/src_2021ND240.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND240.pdf' <page>."
 },
 {
  "id": 17925,
  "cite": "2021 ND 228",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 20 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND228.pdf' /tmp/src_2021ND228.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND228.pdf' <page>."
 },
 {
  "id": 17924,
  "cite": "2021 ND 238",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 12 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND238.pdf' /tmp/src_2021ND238.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND238.pdf' <page>."
 },
 {
  "id": 17923,
  "cite": "2021 ND 237",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 13 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND237.pdf' /tmp/src_2021ND237.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND237.pdf' <page>."
 },
 {
  "id": 17922,
  "cite": "2021 ND 236",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 8 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND236.pdf' /tmp/src_2021ND236.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND236.pdf' <page>."
 },
 {
  "id": 17921,
  "cite": "2021 ND 239",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 11 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND239.pdf' /tmp/src_2021ND239.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND239.pdf' <page>."
 },
 {
  "id": 17920,
  "cite": "2021 ND 233",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 4 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND233.pdf' /tmp/src_2021ND233.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND233.pdf' <page>."
 },
 {
  "id": 17919,
  "cite": "2021 ND 234",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 6 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND234.pdf' /tmp/src_2021ND234.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND234.pdf' <page>."
 },
 {
  "id": 17973,
  "cite": "2021 ND 227",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 5 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND227.pdf' /tmp/src_2021ND227.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND227.pdf' <page>."
 },
 {
  "id": 19619,
  "cite": "2021 ND 226",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND226.pdf' /tmp/src_2021ND226.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND226.pdf' <page>."
 },
 {
  "id": 19618,
  "cite": "2021 ND 222",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND222.pdf' /tmp/src_2021ND222.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND222.pdf' <page>."
 },
 {
  "id": 19617,
  "cite": "2021 ND 218",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND218.pdf' /tmp/src_2021ND218.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND218.pdf' <page>."
 },
 {
  "id": 17918,
  "cite": "2021 ND 221",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 5 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND221.pdf' /tmp/src_2021ND221.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND221.pdf' <page>."
 },
 {
  "id": 17917,
  "cite": "2021 ND 223",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 11 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND223.pdf' /tmp/src_2021ND223.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND223.pdf' <page>."
 },
 {
  "id": 17916,
  "cite": "2021 ND 220",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 5 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND220.pdf' /tmp/src_2021ND220.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND220.pdf' <page>."
 },
 {
  "id": 17915,
  "cite": "2021 ND 225",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 14 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND225.pdf' /tmp/src_2021ND225.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND225.pdf' <page>."
 },
 {
  "id": 17914,
  "cite": "2021 ND 224",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 5 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND224.pdf' /tmp/src_2021ND224.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND224.pdf' <page>."
 },
 {
  "id": 17913,
  "cite": "2021 ND 216",
  "era": "2021 (reporter-era, OCR)",
  "report": "whitespace: 11 blank-runs(3+)",
  "sdesc": "the reporter markdown (OCR of the N.W./N.W.2d scan) this opinion was ingested from",
  "saccess": "Source file: /Users/jerod/refs/nd/opin/markdown/2021/2021ND216.md . If a `.doc`, parse footnotes/structure as RTF; if markdown, it is the OCR text — compare carefully, the DB may have diverged from it."
 },
 {
  "id": 17912,
  "cite": "2021 ND 219",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 4 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND219.pdf' /tmp/src_2021ND219.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND219.pdf' <page>."
 },
 {
  "id": 17911,
  "cite": "2021 ND 217",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 23 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND217.pdf' /tmp/src_2021ND217.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND217.pdf' <page>."
 },
 {
  "id": 17910,
  "cite": "2021 ND 208",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 15 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND208.pdf' /tmp/src_2021ND208.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND208.pdf' <page>."
 },
 {
  "id": 17909,
  "cite": "2021 ND 212",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 9 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND212.pdf' /tmp/src_2021ND212.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND212.pdf' <page>."
 },
 {
  "id": 19615,
  "cite": "2021 ND 211",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND211.pdf' /tmp/src_2021ND211.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND211.pdf' <page>."
 },
 {
  "id": 17908,
  "cite": "2021 ND 214",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 16 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND214.pdf' /tmp/src_2021ND214.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND214.pdf' <page>."
 },
 {
  "id": 17907,
  "cite": "2021 ND 209",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 10 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND209.pdf' /tmp/src_2021ND209.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND209.pdf' <page>."
 },
 {
  "id": 17906,
  "cite": "2021 ND 207",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 5 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND207.pdf' /tmp/src_2021ND207.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND207.pdf' <page>."
 },
 {
  "id": 17905,
  "cite": "2021 ND 215",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 9 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND215.pdf' /tmp/src_2021ND215.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND215.pdf' <page>."
 },
 {
  "id": 17904,
  "cite": "2021 ND 213",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 14 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND213.pdf' /tmp/src_2021ND213.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND213.pdf' <page>."
 },
 {
  "id": 17903,
  "cite": "2021 ND 210",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 8 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND210.pdf' /tmp/src_2021ND210.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND210.pdf' <page>."
 },
 {
  "id": 19614,
  "cite": "2021 ND 206",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND206.pdf' /tmp/src_2021ND206.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND206.pdf' <page>."
 },
 {
  "id": 19613,
  "cite": "2021 ND 205",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND205.pdf' /tmp/src_2021ND205.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND205.pdf' <page>."
 },
 {
  "id": 19612,
  "cite": "2021 ND 202",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND202.pdf' /tmp/src_2021ND202.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND202.pdf' <page>."
 },
 {
  "id": 19611,
  "cite": "2021 ND 201",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND201.pdf' /tmp/src_2021ND201.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND201.pdf' <page>."
 },
 {
  "id": 17902,
  "cite": "2021 ND 198",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 7 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND198.pdf' /tmp/src_2021ND198.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND198.pdf' <page>."
 },
 {
  "id": 17901,
  "cite": "2021 ND 204",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 6 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND204.pdf' /tmp/src_2021ND204.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND204.pdf' <page>."
 },
 {
  "id": 17900,
  "cite": "2021 ND 203",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 11 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND203.pdf' /tmp/src_2021ND203.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND203.pdf' <page>."
 },
 {
  "id": 17899,
  "cite": "2021 ND 199",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 6 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND199.pdf' /tmp/src_2021ND199.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND199.pdf' <page>."
 },
 {
  "id": 17898,
  "cite": "2021 ND 200",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 8 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND200.pdf' /tmp/src_2021ND200.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND200.pdf' <page>."
 },
 {
  "id": 19610,
  "cite": "2021 ND 197",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND197.pdf' /tmp/src_2021ND197.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND197.pdf' <page>."
 },
 {
  "id": 19608,
  "cite": "2021 ND 189",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND189.pdf' /tmp/src_2021ND189.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND189.pdf' <page>."
 },
 {
  "id": 17897,
  "cite": "2021 ND 196",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 10 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND196.pdf' /tmp/src_2021ND196.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND196.pdf' <page>."
 },
 {
  "id": 17896,
  "cite": "2021 ND 195",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 8 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND195.pdf' /tmp/src_2021ND195.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND195.pdf' <page>."
 },
 {
  "id": 17895,
  "cite": "2021 ND 190",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 10 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND190.pdf' /tmp/src_2021ND190.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND190.pdf' <page>."
 },
 {
  "id": 17894,
  "cite": "2021 ND 194",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 10 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND194.pdf' /tmp/src_2021ND194.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND194.pdf' <page>."
 },
 {
  "id": 17893,
  "cite": "2021 ND 192",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 12 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND192.pdf' /tmp/src_2021ND192.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND192.pdf' <page>."
 },
 {
  "id": 17892,
  "cite": "2021 ND 191",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 5 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND191.pdf' /tmp/src_2021ND191.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND191.pdf' <page>."
 },
 {
  "id": 17891,
  "cite": "2021 ND 193",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 5 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND193.pdf' /tmp/src_2021ND193.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND193.pdf' <page>."
 },
 {
  "id": 17890,
  "cite": "2021 ND 188",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 5 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND188.pdf' /tmp/src_2021ND188.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND188.pdf' <page>."
 },
 {
  "id": 19607,
  "cite": "2021 ND 184",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND184.pdf' /tmp/src_2021ND184.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND184.pdf' <page>."
 },
 {
  "id": 19606,
  "cite": "2021 ND 181",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND181.pdf' /tmp/src_2021ND181.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND181.pdf' <page>."
 },
 {
  "id": 19605,
  "cite": "2021 ND 178",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND178.pdf' /tmp/src_2021ND178.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND178.pdf' <page>."
 },
 {
  "id": 19604,
  "cite": "2021 ND 176",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND176.pdf' /tmp/src_2021ND176.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND176.pdf' <page>."
 },
 {
  "id": 17887,
  "cite": "2021 ND 180",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 4 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND180.pdf' /tmp/src_2021ND180.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND180.pdf' <page>."
 },
 {
  "id": 17886,
  "cite": "2021 ND 183",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 9 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND183.pdf' /tmp/src_2021ND183.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND183.pdf' <page>."
 },
 {
  "id": 17885,
  "cite": "2021 ND 177",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 5 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND177.pdf' /tmp/src_2021ND177.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND177.pdf' <page>."
 },
 {
  "id": 17884,
  "cite": "2021 ND 179",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 4 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND179.pdf' /tmp/src_2021ND179.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND179.pdf' <page>."
 },
 {
  "id": 17883,
  "cite": "2021 ND 187",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 4 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND187.pdf' /tmp/src_2021ND187.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND187.pdf' <page>."
 },
 {
  "id": 17882,
  "cite": "2021 ND 185",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 8 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND185.pdf' /tmp/src_2021ND185.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND185.pdf' <page>."
 },
 {
  "id": 17881,
  "cite": "2021 ND 182",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 6 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND182.pdf' /tmp/src_2021ND182.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND182.pdf' <page>."
 },
 {
  "id": 17880,
  "cite": "2021 ND 186",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 15 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND186.pdf' /tmp/src_2021ND186.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND186.pdf' <page>."
 },
 {
  "id": 19603,
  "cite": "2021 ND 171",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND171.pdf' /tmp/src_2021ND171.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND171.pdf' <page>."
 },
 {
  "id": 17889,
  "cite": "2021 ND 169",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 10 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND169.pdf' /tmp/src_2021ND169.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND169.pdf' <page>."
 },
 {
  "id": 17888,
  "cite": "2021 ND 172",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 9 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND172.pdf' /tmp/src_2021ND172.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND172.pdf' <page>."
 },
 {
  "id": 17879,
  "cite": "2021 ND 170",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 10 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND170.pdf' /tmp/src_2021ND170.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND170.pdf' <page>."
 },
 {
  "id": 17878,
  "cite": "2021 ND 168",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 5 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND168.pdf' /tmp/src_2021ND168.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND168.pdf' <page>."
 },
 {
  "id": 17877,
  "cite": "2021 ND 173",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 13 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND173.pdf' /tmp/src_2021ND173.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND173.pdf' <page>."
 },
 {
  "id": 17876,
  "cite": "2021 ND 174",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 5 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND174.pdf' /tmp/src_2021ND174.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND174.pdf' <page>."
 },
 {
  "id": 17875,
  "cite": "2021 ND 175",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "whitespace: 14 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND175.pdf' /tmp/src_2021ND175.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND175.pdf' <page>."
 },
 {
  "id": 19601,
  "cite": "2021 ND 167",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND167.pdf' /tmp/src_2021ND167.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND167.pdf' <page>."
 },
 {
  "id": 19600,
  "cite": "2021 ND 166",
  "era": "2021 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND166.pdf' /tmp/src_2021ND166.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2021/2021ND166.pdf' <page>."
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
