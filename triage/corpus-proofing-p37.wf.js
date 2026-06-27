export const meta = {
  name: 'corpus-proofing-p37',
  description: 'Corpus proofing: transcription-fidelity proofread vs authoritative source (propose + flag, never apply)',
  phases: [{ title: 'Proof', detail: 'read-only agent per opinion: source-verified corrections + flags' }],
}

const BATCH = [
 {
  "id": 17040,
  "cite": "2017 ND 223",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND223.pdf' /tmp/src_2017ND223.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND223.pdf' <page>."
 },
 {
  "id": 17039,
  "cite": "2017 ND 229",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 4 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND229.pdf' /tmp/src_2017ND229.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND229.pdf' <page>."
 },
 {
  "id": 17038,
  "cite": "2017 ND 230",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND230.pdf' /tmp/src_2017ND230.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND230.pdf' <page>."
 },
 {
  "id": 17037,
  "cite": "2017 ND 228",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND228.pdf' /tmp/src_2017ND228.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND228.pdf' <page>."
 },
 {
  "id": 17036,
  "cite": "2017 ND 221",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND221.pdf' /tmp/src_2017ND221.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND221.pdf' <page>."
 },
 {
  "id": 17035,
  "cite": "2017 ND 220",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND220.pdf' /tmp/src_2017ND220.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND220.pdf' <page>."
 },
 {
  "id": 17034,
  "cite": "2017 ND 222",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND222.pdf' /tmp/src_2017ND222.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND222.pdf' <page>."
 },
 {
  "id": 17033,
  "cite": "2017 ND 219",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶25->¶27, gap ¶29->¶32; heading_seq: 2->4; whitespace: 17 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND219.pdf' /tmp/src_2017ND219.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND219.pdf' <page>."
 },
 {
  "id": 17032,
  "cite": "2017 ND 218",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 6 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND218.pdf' /tmp/src_2017ND218.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND218.pdf' <page>."
 },
 {
  "id": 17031,
  "cite": "2017 ND 217",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4; whitespace: 14 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND217.pdf' /tmp/src_2017ND217.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND217.pdf' <page>."
 },
 {
  "id": 17030,
  "cite": "2017 ND 216",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 11 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND216.pdf' /tmp/src_2017ND216.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND216.pdf' <page>."
 },
 {
  "id": 17028,
  "cite": "2017 ND 215",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4; whitespace: 14 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND215.pdf' /tmp/src_2017ND215.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND215.pdf' <page>."
 },
 {
  "id": 17029,
  "cite": "2017 ND 204",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "starpage_seq: *75 *74 *75; heading_seq: 2->4; whitespace: 2 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND204.pdf' /tmp/src_2017ND204.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND204.pdf' <page>."
 },
 {
  "id": 17027,
  "cite": "2017 ND 211",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND211.pdf' /tmp/src_2017ND211.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND211.pdf' <page>."
 },
 {
  "id": 17026,
  "cite": "2017 ND 207",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 13 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND207.pdf' /tmp/src_2017ND207.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND207.pdf' <page>."
 },
 {
  "id": 17025,
  "cite": "2017 ND 213",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶16->¶18, gap ¶19->¶21; heading_seq: 2->4; whitespace: 12 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND213.pdf' /tmp/src_2017ND213.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND213.pdf' <page>."
 },
 {
  "id": 17024,
  "cite": "2017 ND 205",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "starpage_seq: *362 *18 *363; heading_seq: 2->4; whitespace: 31 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND205.pdf' /tmp/src_2017ND205.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND205.pdf' <page>."
 },
 {
  "id": 17023,
  "cite": "2017 ND 212",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND212.pdf' /tmp/src_2017ND212.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND212.pdf' <page>."
 },
 {
  "id": 17022,
  "cite": "2017 ND 206",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 17 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND206.pdf' /tmp/src_2017ND206.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND206.pdf' <page>."
 },
 {
  "id": 17021,
  "cite": "2017 ND 210",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 10 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND210.pdf' /tmp/src_2017ND210.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND210.pdf' <page>."
 },
 {
  "id": 17020,
  "cite": "2017 ND 214",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 8 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND214.pdf' /tmp/src_2017ND214.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND214.pdf' <page>."
 },
 {
  "id": 17019,
  "cite": "2017 ND 209",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 1 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND209.pdf' /tmp/src_2017ND209.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND209.pdf' <page>."
 },
 {
  "id": 17018,
  "cite": "2017 ND 208",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 4 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND208.pdf' /tmp/src_2017ND208.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND208.pdf' <page>."
 },
 {
  "id": 17017,
  "cite": "2017 ND 203",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶23->¶26; whitespace: 22 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND203.pdf' /tmp/src_2017ND203.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND203.pdf' <page>."
 },
 {
  "id": 17011,
  "cite": "2017 ND 202",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶22->¶28; whitespace: 11 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND202.pdf' /tmp/src_2017ND202.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND202.pdf' <page>."
 },
 {
  "id": 17010,
  "cite": "2017 ND 201",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶12->¶18, gap ¶50->¶52; whitespace: 36 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND201.pdf' /tmp/src_2017ND201.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND201.pdf' <page>."
 },
 {
  "id": 17009,
  "cite": "2017 ND 200",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 14 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND200.pdf' /tmp/src_2017ND200.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND200.pdf' <page>."
 },
 {
  "id": 17008,
  "cite": "2017 ND 199",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND199.pdf' /tmp/src_2017ND199.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND199.pdf' <page>."
 },
 {
  "id": 17007,
  "cite": "2017 ND 198",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶16->¶18, gap ¶35->¶37; whitespace: 12 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND198.pdf' /tmp/src_2017ND198.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND198.pdf' <page>."
 },
 {
  "id": 17016,
  "cite": "2017 ND 188",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 8 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND188.pdf' /tmp/src_2017ND188.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND188.pdf' <page>."
 },
 {
  "id": 17015,
  "cite": "2017 ND 185",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4; whitespace: 17 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND185.pdf' /tmp/src_2017ND185.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND185.pdf' <page>."
 },
 {
  "id": 17014,
  "cite": "2017 ND 197",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 18 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND197.pdf' /tmp/src_2017ND197.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND197.pdf' <page>."
 },
 {
  "id": 17013,
  "cite": "2017 ND 191",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 2 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND191.pdf' /tmp/src_2017ND191.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND191.pdf' <page>."
 },
 {
  "id": 17012,
  "cite": "2017 ND 196",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "starpage_seq: *43 *11 *44",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND196.pdf' /tmp/src_2017ND196.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND196.pdf' <page>."
 },
 {
  "id": 17006,
  "cite": "2017 ND 193",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶7->¶9, gap ¶21->¶23; whitespace: 13 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND193.pdf' /tmp/src_2017ND193.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND193.pdf' <page>."
 },
 {
  "id": 16998,
  "cite": "2017 ND 183",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND183.pdf' /tmp/src_2017ND183.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND183.pdf' <page>."
 },
 {
  "id": 16997,
  "cite": "2017 ND 186",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND186.pdf' /tmp/src_2017ND186.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND186.pdf' <page>."
 },
 {
  "id": 16996,
  "cite": "2017 ND 190",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶14->¶16; heading_seq: 2->4; whitespace: 21 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND190.pdf' /tmp/src_2017ND190.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND190.pdf' <page>."
 },
 {
  "id": 16995,
  "cite": "2017 ND 189",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 1 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND189.pdf' /tmp/src_2017ND189.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND189.pdf' <page>."
 },
 {
  "id": 16994,
  "cite": "2017 ND 184",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶16->¶18; heading_seq: 2->4; whitespace: 2 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND184.pdf' /tmp/src_2017ND184.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND184.pdf' <page>."
 },
 {
  "id": 16993,
  "cite": "2017 ND 195",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶11->¶13; whitespace: 13 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND195.pdf' /tmp/src_2017ND195.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND195.pdf' <page>."
 },
 {
  "id": 16992,
  "cite": "2017 ND 194",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4; whitespace: 5 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND194.pdf' /tmp/src_2017ND194.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND194.pdf' <page>."
 },
 {
  "id": 16991,
  "cite": "2017 ND 187",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 1 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND187.pdf' /tmp/src_2017ND187.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND187.pdf' <page>."
 },
 {
  "id": 16990,
  "cite": "2017 ND 192",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND192.pdf' /tmp/src_2017ND192.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND192.pdf' <page>."
 },
 {
  "id": 16989,
  "cite": "2017 ND 182",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND182.pdf' /tmp/src_2017ND182.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND182.pdf' <page>."
 },
 {
  "id": 16988,
  "cite": "2017 ND 181",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND181.pdf' /tmp/src_2017ND181.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND181.pdf' <page>."
 },
 {
  "id": 16987,
  "cite": "2017 ND 180",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND180.pdf' /tmp/src_2017ND180.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND180.pdf' <page>."
 },
 {
  "id": 16986,
  "cite": "2017 ND 179",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 12 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND179.pdf' /tmp/src_2017ND179.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND179.pdf' <page>."
 },
 {
  "id": 16985,
  "cite": "2017 ND 174",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶29->¶80; whitespace: 7 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND174.pdf' /tmp/src_2017ND174.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND174.pdf' <page>."
 },
 {
  "id": 16984,
  "cite": "2017 ND 175",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶22->¶25, gap ¶25->¶28",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND175.pdf' /tmp/src_2017ND175.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND175.pdf' <page>."
 },
 {
  "id": 16983,
  "cite": "2017 ND 177",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶23->¶25, gap ¶40->¶42, gap ¶42->¶48; heading_seq: 2->4; whitespace: 23 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND177.pdf' /tmp/src_2017ND177.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND177.pdf' <page>."
 },
 {
  "id": 16982,
  "cite": "2017 ND 171",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 1->4; whitespace: 1 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND171.pdf' /tmp/src_2017ND171.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND171.pdf' <page>."
 },
 {
  "id": 16981,
  "cite": "2017 ND 178",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4; whitespace: 8 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND178.pdf' /tmp/src_2017ND178.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND178.pdf' <page>."
 },
 {
  "id": 16980,
  "cite": "2017 ND 167",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4; whitespace: 19 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND167.pdf' /tmp/src_2017ND167.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND167.pdf' <page>."
 },
 {
  "id": 16979,
  "cite": "2017 ND 172",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND172.pdf' /tmp/src_2017ND172.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND172.pdf' <page>."
 },
 {
  "id": 16978,
  "cite": "2017 ND 165",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 11 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND165.pdf' /tmp/src_2017ND165.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND165.pdf' <page>."
 },
 {
  "id": 16977,
  "cite": "2017 ND 173",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4; whitespace: 8 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND173.pdf' /tmp/src_2017ND173.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND173.pdf' <page>."
 },
 {
  "id": 16976,
  "cite": "2017 ND 168",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶11->¶13; whitespace: 15 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND168.pdf' /tmp/src_2017ND168.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND168.pdf' <page>."
 },
 {
  "id": 16975,
  "cite": "2017 ND 170",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 1->4",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND170.pdf' /tmp/src_2017ND170.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND170.pdf' <page>."
 },
 {
  "id": 16974,
  "cite": "2017 ND 166",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND166.pdf' /tmp/src_2017ND166.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND166.pdf' <page>."
 },
 {
  "id": 16973,
  "cite": "2017 ND 176",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND176.pdf' /tmp/src_2017ND176.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND176.pdf' <page>."
 },
 {
  "id": 16972,
  "cite": "2017 ND 169",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4; whitespace: 29 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND169.pdf' /tmp/src_2017ND169.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND169.pdf' <page>."
 },
 {
  "id": 16971,
  "cite": "2017 ND 164",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND164.pdf' /tmp/src_2017ND164.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND164.pdf' <page>."
 },
 {
  "id": 16970,
  "cite": "2017 ND 162",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4; whitespace: 6 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND162.pdf' /tmp/src_2017ND162.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND162.pdf' <page>."
 },
 {
  "id": 16969,
  "cite": "2017 ND 163",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "starpage_seq: *918 *844 *919; heading_seq: 2->4; whitespace: 17 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND163.pdf' /tmp/src_2017ND163.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND163.pdf' <page>."
 },
 {
  "id": 16968,
  "cite": "2017 ND 156",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND156.pdf' /tmp/src_2017ND156.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND156.pdf' <page>."
 },
 {
  "id": 16967,
  "cite": "2017 ND 154",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 4 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND154.pdf' /tmp/src_2017ND154.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND154.pdf' <page>."
 },
 {
  "id": 16966,
  "cite": "2017 ND 153",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶10->¶13; whitespace: 3 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND153.pdf' /tmp/src_2017ND153.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND153.pdf' <page>."
 },
 {
  "id": 16965,
  "cite": "2017 ND 151",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND151.pdf' /tmp/src_2017ND151.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND151.pdf' <page>."
 },
 {
  "id": 16964,
  "cite": "2017 ND 158",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4; whitespace: 4 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND158.pdf' /tmp/src_2017ND158.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND158.pdf' <page>."
 },
 {
  "id": 16963,
  "cite": "2017 ND 159",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND159.pdf' /tmp/src_2017ND159.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND159.pdf' <page>."
 },
 {
  "id": 16962,
  "cite": "2017 ND 150",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND150.pdf' /tmp/src_2017ND150.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND150.pdf' <page>."
 },
 {
  "id": 16961,
  "cite": "2017 ND 160",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 16 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND160.pdf' /tmp/src_2017ND160.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND160.pdf' <page>."
 },
 {
  "id": 16958,
  "cite": "2017 ND 152",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND152.pdf' /tmp/src_2017ND152.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND152.pdf' <page>."
 },
 {
  "id": 16957,
  "cite": "2017 ND 155",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶24->¶26; heading_seq: 2->4; whitespace: 17 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND155.pdf' /tmp/src_2017ND155.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND155.pdf' <page>."
 },
 {
  "id": 16956,
  "cite": "2017 ND 157",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 8 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND157.pdf' /tmp/src_2017ND157.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND157.pdf' <page>."
 },
 {
  "id": 16955,
  "cite": "2017 ND 161",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶5->¶7",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND161.pdf' /tmp/src_2017ND161.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND161.pdf' <page>."
 },
 {
  "id": 16960,
  "cite": "2017 ND 149",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND149.pdf' /tmp/src_2017ND149.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND149.pdf' <page>."
 },
 {
  "id": 16959,
  "cite": "2017 ND 148",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶9->¶11, gap ¶15->¶17; starpage_seq: *446 *312 *554, *224 *157 *219, *553 *306 *788, *521 *363 *553",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND148.pdf' /tmp/src_2017ND148.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND148.pdf' <page>."
 },
 {
  "id": 16954,
  "cite": "2017 ND 147",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 6 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND147.pdf' /tmp/src_2017ND147.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND147.pdf' <page>."
 },
 {
  "id": 16953,
  "cite": "2017 ND 146",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 1->5",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND146.pdf' /tmp/src_2017ND146.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND146.pdf' <page>."
 },
 {
  "id": 16952,
  "cite": "2017 ND 145",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4; whitespace: 5 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND145.pdf' /tmp/src_2017ND145.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND145.pdf' <page>."
 },
 {
  "id": 16951,
  "cite": "2017 ND 132",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4; whitespace: 7 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND132.pdf' /tmp/src_2017ND132.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND132.pdf' <page>."
 },
 {
  "id": 16950,
  "cite": "2017 ND 141",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 6 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND141.pdf' /tmp/src_2017ND141.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND141.pdf' <page>."
 },
 {
  "id": 16949,
  "cite": "2017 ND 133",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND133.pdf' /tmp/src_2017ND133.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND133.pdf' <page>."
 },
 {
  "id": 16948,
  "cite": "2017 ND 136",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶7->¶9; heading_seq: 2->4; whitespace: 14 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND136.pdf' /tmp/src_2017ND136.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND136.pdf' <page>."
 },
 {
  "id": 16947,
  "cite": "2017 ND 144",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND144.pdf' /tmp/src_2017ND144.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND144.pdf' <page>."
 },
 {
  "id": 16946,
  "cite": "2017 ND 134",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 7 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND134.pdf' /tmp/src_2017ND134.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND134.pdf' <page>."
 },
 {
  "id": 16945,
  "cite": "2017 ND 140",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4; whitespace: 10 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND140.pdf' /tmp/src_2017ND140.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND140.pdf' <page>."
 },
 {
  "id": 16944,
  "cite": "2017 ND 139",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 2 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND139.pdf' /tmp/src_2017ND139.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND139.pdf' <page>."
 },
 {
  "id": 16943,
  "cite": "2017 ND 143",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 31 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND143.pdf' /tmp/src_2017ND143.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND143.pdf' <page>."
 },
 {
  "id": 16942,
  "cite": "2017 ND 137",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶19->¶21; starpage_seq: *235 *177 *2009, *532 *521 *2016, *2016 *2004 *2016, *2016 *2004 *2016, *752 *532 *2016, *546 *541 *546",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND137.pdf' /tmp/src_2017ND137.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND137.pdf' <page>."
 },
 {
  "id": 16941,
  "cite": "2017 ND 142",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 9 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND142.pdf' /tmp/src_2017ND142.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND142.pdf' <page>."
 },
 {
  "id": 16940,
  "cite": "2017 ND 135",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 2 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND135.pdf' /tmp/src_2017ND135.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND135.pdf' <page>."
 },
 {
  "id": 16939,
  "cite": "2017 ND 138",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4; whitespace: 6 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND138.pdf' /tmp/src_2017ND138.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND138.pdf' <page>."
 },
 {
  "id": 16938,
  "cite": "2017 ND 131",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND131.pdf' /tmp/src_2017ND131.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND131.pdf' <page>."
 },
 {
  "id": 16937,
  "cite": "2017 ND 130",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND130.pdf' /tmp/src_2017ND130.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND130.pdf' <page>."
 },
 {
  "id": 16936,
  "cite": "2017 ND 129",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND129.pdf' /tmp/src_2017ND129.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND129.pdf' <page>."
 },
 {
  "id": 16934,
  "cite": "2017 ND 128",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND128.pdf' /tmp/src_2017ND128.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND128.pdf' <page>."
 },
 {
  "id": 16933,
  "cite": "2017 ND 127",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶10->¶12; whitespace: 2 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND127.pdf' /tmp/src_2017ND127.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND127.pdf' <page>."
 },
 {
  "id": 16935,
  "cite": "2017 ND 114",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND114.pdf' /tmp/src_2017ND114.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND114.pdf' <page>."
 },
 {
  "id": 16932,
  "cite": "2017 ND 118",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 13 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND118.pdf' /tmp/src_2017ND118.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND118.pdf' <page>."
 },
 {
  "id": 16930,
  "cite": "2017 ND 116",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND116.pdf' /tmp/src_2017ND116.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND116.pdf' <page>."
 },
 {
  "id": 16929,
  "cite": "2017 ND 115",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND115.pdf' /tmp/src_2017ND115.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND115.pdf' <page>."
 },
 {
  "id": 16928,
  "cite": "2017 ND 117",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 1 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND117.pdf' /tmp/src_2017ND117.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND117.pdf' <page>."
 },
 {
  "id": 16927,
  "cite": "2017 ND 119",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 8 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND119.pdf' /tmp/src_2017ND119.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND119.pdf' <page>."
 },
 {
  "id": 16926,
  "cite": "2017 ND 121",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "starpage_seq: *882 *581 *883; heading_seq: 2->4; whitespace: 5 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND121.pdf' /tmp/src_2017ND121.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND121.pdf' <page>."
 },
 {
  "id": 16925,
  "cite": "2017 ND 122",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4; whitespace: 18 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND122.pdf' /tmp/src_2017ND122.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND122.pdf' <page>."
 },
 {
  "id": 16924,
  "cite": "2017 ND 126",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND126.pdf' /tmp/src_2017ND126.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND126.pdf' <page>."
 },
 {
  "id": 16923,
  "cite": "2017 ND 120",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND120.pdf' /tmp/src_2017ND120.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND120.pdf' <page>."
 },
 {
  "id": 16922,
  "cite": "2017 ND 123",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND123.pdf' /tmp/src_2017ND123.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND123.pdf' <page>."
 },
 {
  "id": 16921,
  "cite": "2017 ND 124",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 1 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND124.pdf' /tmp/src_2017ND124.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND124.pdf' <page>."
 },
 {
  "id": 16920,
  "cite": "2017 ND 125",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 3 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND125.pdf' /tmp/src_2017ND125.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND125.pdf' <page>."
 },
 {
  "id": 16919,
  "cite": "2017 ND 113",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶17->¶19",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND113.pdf' /tmp/src_2017ND113.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND113.pdf' <page>."
 },
 {
  "id": 16918,
  "cite": "2017 ND 112",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶14->¶16; heading_seq: 2->4; whitespace: 6 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND112.pdf' /tmp/src_2017ND112.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND112.pdf' <page>."
 },
 {
  "id": 19241,
  "cite": "2017 ND 90",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND90.pdf' /tmp/src_2017ND90.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND90.pdf' <page>."
 },
 {
  "id": 19239,
  "cite": "2017 ND 88",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND88.pdf' /tmp/src_2017ND88.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND88.pdf' <page>."
 },
 {
  "id": 19238,
  "cite": "2017 ND 87",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND87.pdf' /tmp/src_2017ND87.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND87.pdf' <page>."
 },
 {
  "id": 16931,
  "cite": "2017 ND 89",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND89.pdf' /tmp/src_2017ND89.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND89.pdf' <page>."
 },
 {
  "id": 16917,
  "cite": "2017 ND 92",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4; whitespace: 30 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND92.pdf' /tmp/src_2017ND92.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND92.pdf' <page>."
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
