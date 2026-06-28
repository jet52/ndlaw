export const meta = {
  name: 'corpus-proofing-p38',
  description: 'Corpus proofing: transcription-fidelity proofread vs authoritative source (propose + flag, never apply)',
  phases: [{ title: 'Proof', detail: 'read-only agent per opinion: source-verified corrections + flags' }],
}

const BATCH = [
 {
  "id": 16829,
  "cite": "2017 ND 1",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND1.pdf' /tmp/src_2017ND1.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND1.pdf' <page>."
 },
 {
  "id": 16830,
  "cite": "2017 ND 23",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND23.pdf' /tmp/src_2017ND23.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND23.pdf' <page>."
 },
 {
  "id": 16831,
  "cite": "2017 ND 15",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND15.pdf' /tmp/src_2017ND15.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND15.pdf' <page>."
 },
 {
  "id": 16832,
  "cite": "2017 ND 24",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 11 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND24.pdf' /tmp/src_2017ND24.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND24.pdf' <page>."
 },
 {
  "id": 16833,
  "cite": "2017 ND 27",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 9 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND27.pdf' /tmp/src_2017ND27.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND27.pdf' <page>."
 },
 {
  "id": 16835,
  "cite": "2017 ND 13",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND13.pdf' /tmp/src_2017ND13.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND13.pdf' <page>."
 },
 {
  "id": 16836,
  "cite": "2017 ND 31",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 5 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND31.pdf' /tmp/src_2017ND31.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND31.pdf' <page>."
 },
 {
  "id": 16837,
  "cite": "2017 ND 29",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND29.pdf' /tmp/src_2017ND29.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND29.pdf' <page>."
 },
 {
  "id": 16838,
  "cite": "2017 ND 28",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 7 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND28.pdf' /tmp/src_2017ND28.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND28.pdf' <page>."
 },
 {
  "id": 16839,
  "cite": "2017 ND 17",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 8 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND17.pdf' /tmp/src_2017ND17.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND17.pdf' <page>."
 },
 {
  "id": 16840,
  "cite": "2017 ND 14",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 12 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND14.pdf' /tmp/src_2017ND14.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND14.pdf' <page>."
 },
 {
  "id": 16841,
  "cite": "2017 ND 21",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND21.pdf' /tmp/src_2017ND21.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND21.pdf' <page>."
 },
 {
  "id": 16842,
  "cite": "2017 ND 30",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND30.pdf' /tmp/src_2017ND30.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND30.pdf' <page>."
 },
 {
  "id": 16843,
  "cite": "2017 ND 26",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 12 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND26.pdf' /tmp/src_2017ND26.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND26.pdf' <page>."
 },
 {
  "id": 16854,
  "cite": "2017 ND 10",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 2 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND10.pdf' /tmp/src_2017ND10.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND10.pdf' <page>."
 },
 {
  "id": 16855,
  "cite": "2017 ND 20",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND20.pdf' /tmp/src_2017ND20.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND20.pdf' <page>."
 },
 {
  "id": 16856,
  "cite": "2017 ND 19",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4; whitespace: 15 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND19.pdf' /tmp/src_2017ND19.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND19.pdf' <page>."
 },
 {
  "id": 16857,
  "cite": "2017 ND 18",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶12->¶18; whitespace: 5 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND18.pdf' /tmp/src_2017ND18.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND18.pdf' <page>."
 },
 {
  "id": 16858,
  "cite": "2017 ND 25",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶10->¶12, gap ¶25->¶27; heading_seq: 2->4; whitespace: 27 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND25.pdf' /tmp/src_2017ND25.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND25.pdf' <page>."
 },
 {
  "id": 16859,
  "cite": "2017 ND 33",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 10 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND33.pdf' /tmp/src_2017ND33.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND33.pdf' <page>."
 },
 {
  "id": 16860,
  "cite": "2017 ND 34",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 18 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND34.pdf' /tmp/src_2017ND34.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND34.pdf' <page>."
 },
 {
  "id": 16861,
  "cite": "2017 ND 35",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4; whitespace: 15 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND35.pdf' /tmp/src_2017ND35.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND35.pdf' <page>."
 },
 {
  "id": 16862,
  "cite": "2017 ND 22",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4; whitespace: 14 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND22.pdf' /tmp/src_2017ND22.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND22.pdf' <page>."
 },
 {
  "id": 16863,
  "cite": "2017 ND 42",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4; whitespace: 20 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND42.pdf' /tmp/src_2017ND42.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND42.pdf' <page>."
 },
 {
  "id": 16864,
  "cite": "2017 ND 54",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND54.pdf' /tmp/src_2017ND54.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND54.pdf' <page>."
 },
 {
  "id": 16865,
  "cite": "2017 ND 48",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 3 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND48.pdf' /tmp/src_2017ND48.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND48.pdf' <page>."
 },
 {
  "id": 16866,
  "cite": "2017 ND 52",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4; whitespace: 1 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND52.pdf' /tmp/src_2017ND52.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND52.pdf' <page>."
 },
 {
  "id": 16867,
  "cite": "2017 ND 51",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4; whitespace: 2 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND51.pdf' /tmp/src_2017ND51.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND51.pdf' <page>."
 },
 {
  "id": 16868,
  "cite": "2017 ND 53",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶12->¶18; whitespace: 3 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND53.pdf' /tmp/src_2017ND53.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND53.pdf' <page>."
 },
 {
  "id": 16869,
  "cite": "2017 ND 45",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 12 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND45.pdf' /tmp/src_2017ND45.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND45.pdf' <page>."
 },
 {
  "id": 16870,
  "cite": "2017 ND 47",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND47.pdf' /tmp/src_2017ND47.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND47.pdf' <page>."
 },
 {
  "id": 16871,
  "cite": "2017 ND 49",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶7->¶9, gap ¶26->¶28; starpage_seq: *130 *129 *130; heading_seq: 2->4; whitespace: 19 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND49.pdf' /tmp/src_2017ND49.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND49.pdf' <page>."
 },
 {
  "id": 16872,
  "cite": "2017 ND 50",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4; whitespace: 8 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND50.pdf' /tmp/src_2017ND50.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND50.pdf' <page>."
 },
 {
  "id": 16873,
  "cite": "2017 ND 56",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND56.pdf' /tmp/src_2017ND56.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND56.pdf' <page>."
 },
 {
  "id": 16874,
  "cite": "2017 ND 60",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 21 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND60.pdf' /tmp/src_2017ND60.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND60.pdf' <page>."
 },
 {
  "id": 16876,
  "cite": "2017 ND 66",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND66.pdf' /tmp/src_2017ND66.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND66.pdf' <page>."
 },
 {
  "id": 16877,
  "cite": "2017 ND 77",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶17->¶19; whitespace: 75 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND77.pdf' /tmp/src_2017ND77.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND77.pdf' <page>."
 },
 {
  "id": 16878,
  "cite": "2017 ND 64",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4; whitespace: 11 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND64.pdf' /tmp/src_2017ND64.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND64.pdf' <page>."
 },
 {
  "id": 16879,
  "cite": "2017 ND 67",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 2 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND67.pdf' /tmp/src_2017ND67.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND67.pdf' <page>."
 },
 {
  "id": 16880,
  "cite": "2017 ND 65",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND65.pdf' /tmp/src_2017ND65.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND65.pdf' <page>."
 },
 {
  "id": 16881,
  "cite": "2017 ND 71",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4; whitespace: 15 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND71.pdf' /tmp/src_2017ND71.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND71.pdf' <page>."
 },
 {
  "id": 16882,
  "cite": "2017 ND 68",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND68.pdf' /tmp/src_2017ND68.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND68.pdf' <page>."
 },
 {
  "id": 16883,
  "cite": "2017 ND 69",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4; whitespace: 11 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND69.pdf' /tmp/src_2017ND69.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND69.pdf' <page>."
 },
 {
  "id": 16884,
  "cite": "2017 ND 70",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND70.pdf' /tmp/src_2017ND70.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND70.pdf' <page>."
 },
 {
  "id": 16885,
  "cite": "2017 ND 75",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4; whitespace: 21 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND75.pdf' /tmp/src_2017ND75.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND75.pdf' <page>."
 },
 {
  "id": 16886,
  "cite": "2017 ND 76",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4; whitespace: 78 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND76.pdf' /tmp/src_2017ND76.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND76.pdf' <page>."
 },
 {
  "id": 16887,
  "cite": "2017 ND 72",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 24 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND72.pdf' /tmp/src_2017ND72.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND72.pdf' <page>."
 },
 {
  "id": 16888,
  "cite": "2017 ND 73",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND73.pdf' /tmp/src_2017ND73.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND73.pdf' <page>."
 },
 {
  "id": 16889,
  "cite": "2017 ND 74",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 5 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND74.pdf' /tmp/src_2017ND74.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND74.pdf' <page>."
 },
 {
  "id": 16890,
  "cite": "2017 ND 78",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4; whitespace: 4 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND78.pdf' /tmp/src_2017ND78.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND78.pdf' <page>."
 },
 {
  "id": 16891,
  "cite": "2017 ND 79",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 1 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND79.pdf' /tmp/src_2017ND79.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND79.pdf' <page>."
 },
 {
  "id": 16892,
  "cite": "2017 ND 80",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶12->¶18",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND80.pdf' /tmp/src_2017ND80.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND80.pdf' <page>."
 },
 {
  "id": 16893,
  "cite": "2017 ND 81",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND81.pdf' /tmp/src_2017ND81.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND81.pdf' <page>."
 },
 {
  "id": 16894,
  "cite": "2017 ND 82",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND82.pdf' /tmp/src_2017ND82.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND82.pdf' <page>."
 },
 {
  "id": 16895,
  "cite": "2017 ND 86",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND86.pdf' /tmp/src_2017ND86.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND86.pdf' <page>."
 },
 {
  "id": 16896,
  "cite": "2017 ND 85",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶2->¶8",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND85.pdf' /tmp/src_2017ND85.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND85.pdf' <page>."
 },
 {
  "id": 16897,
  "cite": "2017 ND 99",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 5 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND99.pdf' /tmp/src_2017ND99.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND99.pdf' <page>."
 },
 {
  "id": 16898,
  "cite": "2017 ND 101",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶4->¶6, gap ¶10->¶12; heading_seq: 2->4",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND101.pdf' /tmp/src_2017ND101.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND101.pdf' <page>."
 },
 {
  "id": 16899,
  "cite": "2017 ND 93",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 14 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND93.pdf' /tmp/src_2017ND93.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND93.pdf' <page>."
 },
 {
  "id": 16900,
  "cite": "2017 ND 102",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 4 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND102.pdf' /tmp/src_2017ND102.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND102.pdf' <page>."
 },
 {
  "id": 16901,
  "cite": "2017 ND 107",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 5 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND107.pdf' /tmp/src_2017ND107.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND107.pdf' <page>."
 },
 {
  "id": 16902,
  "cite": "2017 ND 95",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 1 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND95.pdf' /tmp/src_2017ND95.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND95.pdf' <page>."
 },
 {
  "id": 16903,
  "cite": "2017 ND 97",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 13 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND97.pdf' /tmp/src_2017ND97.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND97.pdf' <page>."
 },
 {
  "id": 16904,
  "cite": "2017 ND 109",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 4 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND109.pdf' /tmp/src_2017ND109.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND109.pdf' <page>."
 },
 {
  "id": 16905,
  "cite": "2017 ND 104",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4; whitespace: 4 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND104.pdf' /tmp/src_2017ND104.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND104.pdf' <page>."
 },
 {
  "id": 16906,
  "cite": "2017 ND 98",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 7 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND98.pdf' /tmp/src_2017ND98.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND98.pdf' <page>."
 },
 {
  "id": 16907,
  "cite": "2017 ND 108",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 1 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND108.pdf' /tmp/src_2017ND108.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND108.pdf' <page>."
 },
 {
  "id": 16908,
  "cite": "2017 ND 96",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND96.pdf' /tmp/src_2017ND96.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND96.pdf' <page>."
 },
 {
  "id": 16909,
  "cite": "2017 ND 110",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND110.pdf' /tmp/src_2017ND110.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND110.pdf' <page>."
 },
 {
  "id": 16910,
  "cite": "2017 ND 111",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND111.pdf' /tmp/src_2017ND111.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND111.pdf' <page>."
 },
 {
  "id": 16911,
  "cite": "2017 ND 91",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND91.pdf' /tmp/src_2017ND91.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND91.pdf' <page>."
 },
 {
  "id": 16912,
  "cite": "2017 ND 106",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 1->3; whitespace: 17 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND106.pdf' /tmp/src_2017ND106.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND106.pdf' <page>."
 },
 {
  "id": 16913,
  "cite": "2017 ND 105",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶2->¶8; whitespace: 18 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND105.pdf' /tmp/src_2017ND105.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND105.pdf' <page>."
 },
 {
  "id": 16914,
  "cite": "2017 ND 100",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4; whitespace: 15 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND100.pdf' /tmp/src_2017ND100.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND100.pdf' <page>."
 },
 {
  "id": 16915,
  "cite": "2017 ND 94",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4; whitespace: 14 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND94.pdf' /tmp/src_2017ND94.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND94.pdf' <page>."
 },
 {
  "id": 16916,
  "cite": "2017 ND 103",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND103.pdf' /tmp/src_2017ND103.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND103.pdf' <page>."
 },
 {
  "id": 19209,
  "cite": "2017 ND 11",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND11.pdf' /tmp/src_2017ND11.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND11.pdf' <page>."
 },
 {
  "id": 19210,
  "cite": "2017 ND 12",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND12.pdf' /tmp/src_2017ND12.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND12.pdf' <page>."
 },
 {
  "id": 19211,
  "cite": "2017 ND 16",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND16.pdf' /tmp/src_2017ND16.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND16.pdf' <page>."
 },
 {
  "id": 19212,
  "cite": "2017 ND 2",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND2.pdf' /tmp/src_2017ND2.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND2.pdf' <page>."
 },
 {
  "id": 19213,
  "cite": "2017 ND 3",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND3.pdf' /tmp/src_2017ND3.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND3.pdf' <page>."
 },
 {
  "id": 19214,
  "cite": "2017 ND 32",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND32.pdf' /tmp/src_2017ND32.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND32.pdf' <page>."
 },
 {
  "id": 19215,
  "cite": "2017 ND 36",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND36.pdf' /tmp/src_2017ND36.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND36.pdf' <page>."
 },
 {
  "id": 19216,
  "cite": "2017 ND 37",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND37.pdf' /tmp/src_2017ND37.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND37.pdf' <page>."
 },
 {
  "id": 19217,
  "cite": "2017 ND 38",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND38.pdf' /tmp/src_2017ND38.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND38.pdf' <page>."
 },
 {
  "id": 19218,
  "cite": "2017 ND 39",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND39.pdf' /tmp/src_2017ND39.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND39.pdf' <page>."
 },
 {
  "id": 19219,
  "cite": "2017 ND 4",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND4.pdf' /tmp/src_2017ND4.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND4.pdf' <page>."
 },
 {
  "id": 19220,
  "cite": "2017 ND 40",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND40.pdf' /tmp/src_2017ND40.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND40.pdf' <page>."
 },
 {
  "id": 19221,
  "cite": "2017 ND 41",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND41.pdf' /tmp/src_2017ND41.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND41.pdf' <page>."
 },
 {
  "id": 19222,
  "cite": "2017 ND 43",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND43.pdf' /tmp/src_2017ND43.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND43.pdf' <page>."
 },
 {
  "id": 19223,
  "cite": "2017 ND 44",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND44.pdf' /tmp/src_2017ND44.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND44.pdf' <page>."
 },
 {
  "id": 19224,
  "cite": "2017 ND 46",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND46.pdf' /tmp/src_2017ND46.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND46.pdf' <page>."
 },
 {
  "id": 19225,
  "cite": "2017 ND 5",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND5.pdf' /tmp/src_2017ND5.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND5.pdf' <page>."
 },
 {
  "id": 19226,
  "cite": "2017 ND 55",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND55.pdf' /tmp/src_2017ND55.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND55.pdf' <page>."
 },
 {
  "id": 19227,
  "cite": "2017 ND 57",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND57.pdf' /tmp/src_2017ND57.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND57.pdf' <page>."
 },
 {
  "id": 19228,
  "cite": "2017 ND 58",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND58.pdf' /tmp/src_2017ND58.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND58.pdf' <page>."
 },
 {
  "id": 19229,
  "cite": "2017 ND 59",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND59.pdf' /tmp/src_2017ND59.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND59.pdf' <page>."
 },
 {
  "id": 19230,
  "cite": "2017 ND 6",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND6.pdf' /tmp/src_2017ND6.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND6.pdf' <page>."
 },
 {
  "id": 19231,
  "cite": "2017 ND 61",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND61.pdf' /tmp/src_2017ND61.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND61.pdf' <page>."
 },
 {
  "id": 19232,
  "cite": "2017 ND 62",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND62.pdf' /tmp/src_2017ND62.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND62.pdf' <page>."
 },
 {
  "id": 19233,
  "cite": "2017 ND 63",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND63.pdf' /tmp/src_2017ND63.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND63.pdf' <page>."
 },
 {
  "id": 19234,
  "cite": "2017 ND 7",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND7.pdf' /tmp/src_2017ND7.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND7.pdf' <page>."
 },
 {
  "id": 19235,
  "cite": "2017 ND 8",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND8.pdf' /tmp/src_2017ND8.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND8.pdf' <page>."
 },
 {
  "id": 19236,
  "cite": "2017 ND 83",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND83.pdf' /tmp/src_2017ND83.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND83.pdf' <page>."
 },
 {
  "id": 19237,
  "cite": "2017 ND 84",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND84.pdf' /tmp/src_2017ND84.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND84.pdf' <page>."
 },
 {
  "id": 19240,
  "cite": "2017 ND 9",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND9.pdf' /tmp/src_2017ND9.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND9.pdf' <page>."
 },
 {
  "id": 20521,
  "cite": "2026 ND 116",
  "era": "2026 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2026/2026ND116.pdf' /tmp/src_2026ND116.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2026/2026ND116.pdf' <page>."
 },
 {
  "id": 20522,
  "cite": "2026 ND 117",
  "era": "2026 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2026/2026ND117.pdf' /tmp/src_2026ND117.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2026/2026ND117.pdf' <page>."
 },
 {
  "id": 20523,
  "cite": "2026 ND 118",
  "era": "2026 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2026/2026ND118.pdf' /tmp/src_2026ND118.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2026/2026ND118.pdf' <page>."
 },
 {
  "id": 20524,
  "cite": "2026 ND 119",
  "era": "2026 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2026/2026ND119.pdf' /tmp/src_2026ND119.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2026/2026ND119.pdf' <page>."
 },
 {
  "id": 20525,
  "cite": "2026 ND 120",
  "era": "2026 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2026/2026ND120.pdf' /tmp/src_2026ND120.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2026/2026ND120.pdf' <page>."
 },
 {
  "id": 20526,
  "cite": "2026 ND 121",
  "era": "2026 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2026/2026ND121.pdf' /tmp/src_2026ND121.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2026/2026ND121.pdf' <page>."
 },
 {
  "id": 20527,
  "cite": "2026 ND 122",
  "era": "2026 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2026/2026ND122.pdf' /tmp/src_2026ND122.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2026/2026ND122.pdf' <page>."
 },
 {
  "id": 20528,
  "cite": "2026 ND 123",
  "era": "2026 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2026/2026ND123.pdf' /tmp/src_2026ND123.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2026/2026ND123.pdf' <page>."
 },
 {
  "id": 20529,
  "cite": "2026 ND 124",
  "era": "2026 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2026/2026ND124.pdf' /tmp/src_2026ND124.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2026/2026ND124.pdf' <page>."
 },
 {
  "id": 20530,
  "cite": "2026 ND 125",
  "era": "2026 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2026/2026ND125.pdf' /tmp/src_2026ND125.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2026/2026ND125.pdf' <page>."
 },
 {
  "id": 20531,
  "cite": "2026 ND 126",
  "era": "2026 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2026/2026ND126.pdf' /tmp/src_2026ND126.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2026/2026ND126.pdf' <page>."
 },
 {
  "id": 20532,
  "cite": "2026 ND 127",
  "era": "2026 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2026/2026ND127.pdf' /tmp/src_2026ND127.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2026/2026ND127.pdf' <page>."
 },
 {
  "id": 20533,
  "cite": "2026 ND 128",
  "era": "2026 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2026/2026ND128.pdf' /tmp/src_2026ND128.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2026/2026ND128.pdf' <page>."
 },
 {
  "id": 20534,
  "cite": "2026 ND 129",
  "era": "2026 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2026/2026ND129.pdf' /tmp/src_2026ND129.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2026/2026ND129.pdf' <page>."
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
