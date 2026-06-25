export const meta = {
  name: 'corpus-proofing-p36',
  description: 'Corpus proofing: transcription-fidelity proofread vs authoritative source (propose + flag, never apply)',
  phases: [{ title: 'Proof', detail: 'read-only agent per opinion: source-verified corrections + flags' }],
}

const BATCH = [
 {
  "id": 19324,
  "cite": "2018 ND 55",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND55.pdf' /tmp/src_2018ND55.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND55.pdf' <page>."
 },
 {
  "id": 19323,
  "cite": "2018 ND 54",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND54.pdf' /tmp/src_2018ND54.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND54.pdf' <page>."
 },
 {
  "id": 19322,
  "cite": "2018 ND 53",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND53.pdf' /tmp/src_2018ND53.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND53.pdf' <page>."
 },
 {
  "id": 19321,
  "cite": "2018 ND 52",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND52.pdf' /tmp/src_2018ND52.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND52.pdf' <page>."
 },
 {
  "id": 19320,
  "cite": "2018 ND 51",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND51.pdf' /tmp/src_2018ND51.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND51.pdf' <page>."
 },
 {
  "id": 19319,
  "cite": "2018 ND 50",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND50.pdf' /tmp/src_2018ND50.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND50.pdf' <page>."
 },
 {
  "id": 19317,
  "cite": "2018 ND 49",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND49.pdf' /tmp/src_2018ND49.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND49.pdf' <page>."
 },
 {
  "id": 19316,
  "cite": "2018 ND 48",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND48.pdf' /tmp/src_2018ND48.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND48.pdf' <page>."
 },
 {
  "id": 19315,
  "cite": "2018 ND 47",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND47.pdf' /tmp/src_2018ND47.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND47.pdf' <page>."
 },
 {
  "id": 19314,
  "cite": "2018 ND 46",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND46.pdf' /tmp/src_2018ND46.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND46.pdf' <page>."
 },
 {
  "id": 19313,
  "cite": "2018 ND 45",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND45.pdf' /tmp/src_2018ND45.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND45.pdf' <page>."
 },
 {
  "id": 19312,
  "cite": "2018 ND 44",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND44.pdf' /tmp/src_2018ND44.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND44.pdf' <page>."
 },
 {
  "id": 19311,
  "cite": "2018 ND 43",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND43.pdf' /tmp/src_2018ND43.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND43.pdf' <page>."
 },
 {
  "id": 19310,
  "cite": "2018 ND 42",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND42.pdf' /tmp/src_2018ND42.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND42.pdf' <page>."
 },
 {
  "id": 19309,
  "cite": "2018 ND 41",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND41.pdf' /tmp/src_2018ND41.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND41.pdf' <page>."
 },
 {
  "id": 19308,
  "cite": "2018 ND 40",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND40.pdf' /tmp/src_2018ND40.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND40.pdf' <page>."
 },
 {
  "id": 19306,
  "cite": "2018 ND 39",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND39.pdf' /tmp/src_2018ND39.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND39.pdf' <page>."
 },
 {
  "id": 19305,
  "cite": "2018 ND 38",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND38.pdf' /tmp/src_2018ND38.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND38.pdf' <page>."
 },
 {
  "id": 19304,
  "cite": "2018 ND 37",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND37.pdf' /tmp/src_2018ND37.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND37.pdf' <page>."
 },
 {
  "id": 19303,
  "cite": "2018 ND 36",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND36.pdf' /tmp/src_2018ND36.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND36.pdf' <page>."
 },
 {
  "id": 19302,
  "cite": "2018 ND 35",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND35.pdf' /tmp/src_2018ND35.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND35.pdf' <page>."
 },
 {
  "id": 19301,
  "cite": "2018 ND 34",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND34.pdf' /tmp/src_2018ND34.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND34.pdf' <page>."
 },
 {
  "id": 19300,
  "cite": "2018 ND 33",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND33.pdf' /tmp/src_2018ND33.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND33.pdf' <page>."
 },
 {
  "id": 19299,
  "cite": "2018 ND 32",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND32.pdf' /tmp/src_2018ND32.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND32.pdf' <page>."
 },
 {
  "id": 19298,
  "cite": "2018 ND 31",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND31.pdf' /tmp/src_2018ND31.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND31.pdf' <page>."
 },
 {
  "id": 19340,
  "cite": "2018 ND 9",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND9.pdf' /tmp/src_2018ND9.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND9.pdf' <page>."
 },
 {
  "id": 19334,
  "cite": "2018 ND 8",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND8.pdf' /tmp/src_2018ND8.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND8.pdf' <page>."
 },
 {
  "id": 19333,
  "cite": "2018 ND 7",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND7.pdf' /tmp/src_2018ND7.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND7.pdf' <page>."
 },
 {
  "id": 19329,
  "cite": "2018 ND 6",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND6.pdf' /tmp/src_2018ND6.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND6.pdf' <page>."
 },
 {
  "id": 19318,
  "cite": "2018 ND 5",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND5.pdf' /tmp/src_2018ND5.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND5.pdf' <page>."
 },
 {
  "id": 19307,
  "cite": "2018 ND 4",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND4.pdf' /tmp/src_2018ND4.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND4.pdf' <page>."
 },
 {
  "id": 19297,
  "cite": "2018 ND 30",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND30.pdf' /tmp/src_2018ND30.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND30.pdf' <page>."
 },
 {
  "id": 19296,
  "cite": "2018 ND 3",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND3.pdf' /tmp/src_2018ND3.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND3.pdf' <page>."
 },
 {
  "id": 19295,
  "cite": "2018 ND 29",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND29.pdf' /tmp/src_2018ND29.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND29.pdf' <page>."
 },
 {
  "id": 19294,
  "cite": "2018 ND 28",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND28.pdf' /tmp/src_2018ND28.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND28.pdf' <page>."
 },
 {
  "id": 19293,
  "cite": "2018 ND 27",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND27.pdf' /tmp/src_2018ND27.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND27.pdf' <page>."
 },
 {
  "id": 19292,
  "cite": "2018 ND 26",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND26.pdf' /tmp/src_2018ND26.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND26.pdf' <page>."
 },
 {
  "id": 19291,
  "cite": "2018 ND 25",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND25.pdf' /tmp/src_2018ND25.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND25.pdf' <page>."
 },
 {
  "id": 19284,
  "cite": "2018 ND 24",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND24.pdf' /tmp/src_2018ND24.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND24.pdf' <page>."
 },
 {
  "id": 19276,
  "cite": "2018 ND 23",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND23.pdf' /tmp/src_2018ND23.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND23.pdf' <page>."
 },
 {
  "id": 19275,
  "cite": "2018 ND 22",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND22.pdf' /tmp/src_2018ND22.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND22.pdf' <page>."
 },
 {
  "id": 19274,
  "cite": "2018 ND 21",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND21.pdf' /tmp/src_2018ND21.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND21.pdf' <page>."
 },
 {
  "id": 19273,
  "cite": "2018 ND 20",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND20.pdf' /tmp/src_2018ND20.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND20.pdf' <page>."
 },
 {
  "id": 19272,
  "cite": "2018 ND 2",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND2.pdf' /tmp/src_2018ND2.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND2.pdf' <page>."
 },
 {
  "id": 19270,
  "cite": "2018 ND 19",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND19.pdf' /tmp/src_2018ND19.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND19.pdf' <page>."
 },
 {
  "id": 19269,
  "cite": "2018 ND 18",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND18.pdf' /tmp/src_2018ND18.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND18.pdf' <page>."
 },
 {
  "id": 19264,
  "cite": "2018 ND 17",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND17.pdf' /tmp/src_2018ND17.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND17.pdf' <page>."
 },
 {
  "id": 19258,
  "cite": "2018 ND 16",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND16.pdf' /tmp/src_2018ND16.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND16.pdf' <page>."
 },
 {
  "id": 19251,
  "cite": "2018 ND 15",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND15.pdf' /tmp/src_2018ND15.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND15.pdf' <page>."
 },
 {
  "id": 19248,
  "cite": "2018 ND 14",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND14.pdf' /tmp/src_2018ND14.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND14.pdf' <page>."
 },
 {
  "id": 19247,
  "cite": "2018 ND 13",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND13.pdf' /tmp/src_2018ND13.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND13.pdf' <page>."
 },
 {
  "id": 19245,
  "cite": "2018 ND 12",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND12.pdf' /tmp/src_2018ND12.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND12.pdf' <page>."
 },
 {
  "id": 19244,
  "cite": "2018 ND 11",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND11.pdf' /tmp/src_2018ND11.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND11.pdf' <page>."
 },
 {
  "id": 19243,
  "cite": "2018 ND 10",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND10.pdf' /tmp/src_2018ND10.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND10.pdf' <page>."
 },
 {
  "id": 19242,
  "cite": "2018 ND 1",
  "era": "2018 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND1.pdf' /tmp/src_2018ND1.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2018/2018ND1.pdf' <page>."
 },
 {
  "id": 17105,
  "cite": "2017 ND 291",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶4->¶6; heading_seq: 2->4; whitespace: 18 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND291.pdf' /tmp/src_2017ND291.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND291.pdf' <page>."
 },
 {
  "id": 17104,
  "cite": "2017 ND 290",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 1 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND290.pdf' /tmp/src_2017ND290.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND290.pdf' <page>."
 },
 {
  "id": 17103,
  "cite": "2017 ND 285",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND285.pdf' /tmp/src_2017ND285.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND285.pdf' <page>."
 },
 {
  "id": 17102,
  "cite": "2017 ND 289",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶29->¶31",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND289.pdf' /tmp/src_2017ND289.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND289.pdf' <page>."
 },
 {
  "id": 17101,
  "cite": "2017 ND 276",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND276.pdf' /tmp/src_2017ND276.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND276.pdf' <page>."
 },
 {
  "id": 17100,
  "cite": "2017 ND 280",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND280.pdf' /tmp/src_2017ND280.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND280.pdf' <page>."
 },
 {
  "id": 17099,
  "cite": "2017 ND 286",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 16 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND286.pdf' /tmp/src_2017ND286.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND286.pdf' <page>."
 },
 {
  "id": 17098,
  "cite": "2017 ND 275",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND275.pdf' /tmp/src_2017ND275.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND275.pdf' <page>."
 },
 {
  "id": 17097,
  "cite": "2017 ND 273",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND273.pdf' /tmp/src_2017ND273.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND273.pdf' <page>."
 },
 {
  "id": 17096,
  "cite": "2017 ND 278",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND278.pdf' /tmp/src_2017ND278.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND278.pdf' <page>."
 },
 {
  "id": 17095,
  "cite": "2017 ND 277",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND277.pdf' /tmp/src_2017ND277.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND277.pdf' <page>."
 },
 {
  "id": 17094,
  "cite": "2017 ND 274",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND274.pdf' /tmp/src_2017ND274.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND274.pdf' <page>."
 },
 {
  "id": 17093,
  "cite": "2017 ND 288",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 2 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND288.pdf' /tmp/src_2017ND288.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND288.pdf' <page>."
 },
 {
  "id": 17092,
  "cite": "2017 ND 283",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 1 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND283.pdf' /tmp/src_2017ND283.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND283.pdf' <page>."
 },
 {
  "id": 17091,
  "cite": "2017 ND 279",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND279.pdf' /tmp/src_2017ND279.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND279.pdf' <page>."
 },
 {
  "id": 17089,
  "cite": "2017 ND 284",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND284.pdf' /tmp/src_2017ND284.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND284.pdf' <page>."
 },
 {
  "id": 17088,
  "cite": "2017 ND 281",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND281.pdf' /tmp/src_2017ND281.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND281.pdf' <page>."
 },
 {
  "id": 17087,
  "cite": "2017 ND 287",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4; whitespace: 8 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND287.pdf' /tmp/src_2017ND287.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND287.pdf' <page>."
 },
 {
  "id": 17086,
  "cite": "2017 ND 282",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND282.pdf' /tmp/src_2017ND282.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND282.pdf' <page>."
 },
 {
  "id": 17090,
  "cite": "2017 ND 272",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND272.pdf' /tmp/src_2017ND272.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND272.pdf' <page>."
 },
 {
  "id": 17082,
  "cite": "2017 ND 271",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶2->¶4, gap ¶14->¶16; whitespace: 1 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND271.pdf' /tmp/src_2017ND271.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND271.pdf' <page>."
 },
 {
  "id": 17081,
  "cite": "2017 ND 267",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 1->4; whitespace: 4 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND267.pdf' /tmp/src_2017ND267.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND267.pdf' <page>."
 },
 {
  "id": 17080,
  "cite": "2017 ND 270",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 1 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND270.pdf' /tmp/src_2017ND270.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND270.pdf' <page>."
 },
 {
  "id": 17079,
  "cite": "2017 ND 268",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND268.pdf' /tmp/src_2017ND268.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND268.pdf' <page>."
 },
 {
  "id": 17077,
  "cite": "2017 ND 269",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4; whitespace: 5 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND269.pdf' /tmp/src_2017ND269.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND269.pdf' <page>."
 },
 {
  "id": 17076,
  "cite": "2017 ND 261",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND261.pdf' /tmp/src_2017ND261.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND261.pdf' <page>."
 },
 {
  "id": 17071,
  "cite": "2017 ND 262",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 10 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND262.pdf' /tmp/src_2017ND262.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND262.pdf' <page>."
 },
 {
  "id": 17070,
  "cite": "2017 ND 266",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶10->¶13, gap ¶29->¶31, gap ¶35->¶86; heading_seq: 2->4; whitespace: 32 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND266.pdf' /tmp/src_2017ND266.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND266.pdf' <page>."
 },
 {
  "id": 17069,
  "cite": "2017 ND 265",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 12 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND265.pdf' /tmp/src_2017ND265.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND265.pdf' <page>."
 },
 {
  "id": 17068,
  "cite": "2017 ND 259",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND259.pdf' /tmp/src_2017ND259.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND259.pdf' <page>."
 },
 {
  "id": 17066,
  "cite": "2017 ND 263",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4; whitespace: 26 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND263.pdf' /tmp/src_2017ND263.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND263.pdf' <page>."
 },
 {
  "id": 17065,
  "cite": "2017 ND 260",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 5 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND260.pdf' /tmp/src_2017ND260.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND260.pdf' <page>."
 },
 {
  "id": 17064,
  "cite": "2017 ND 257",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND257.pdf' /tmp/src_2017ND257.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND257.pdf' <page>."
 },
 {
  "id": 17063,
  "cite": "2017 ND 258",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND258.pdf' /tmp/src_2017ND258.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND258.pdf' <page>."
 },
 {
  "id": 17062,
  "cite": "2017 ND 264",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 9 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND264.pdf' /tmp/src_2017ND264.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND264.pdf' <page>."
 },
 {
  "id": 17061,
  "cite": "2017 ND 256",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND256.pdf' /tmp/src_2017ND256.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND256.pdf' <page>."
 },
 {
  "id": 17060,
  "cite": "2017 ND 255",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND255.pdf' /tmp/src_2017ND255.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND255.pdf' <page>."
 },
 {
  "id": 17085,
  "cite": "2017 ND 246",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4; whitespace: 23 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND246.pdf' /tmp/src_2017ND246.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND246.pdf' <page>."
 },
 {
  "id": 17084,
  "cite": "2017 ND 240",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 3 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND240.pdf' /tmp/src_2017ND240.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND240.pdf' <page>."
 },
 {
  "id": 17083,
  "cite": "2017 ND 248",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶2->¶8; whitespace: 3 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND248.pdf' /tmp/src_2017ND248.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND248.pdf' <page>."
 },
 {
  "id": 17078,
  "cite": "2017 ND 242",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶27->¶29, gap ¶31->¶82; whitespace: 10 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND242.pdf' /tmp/src_2017ND242.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND242.pdf' <page>."
 },
 {
  "id": 17075,
  "cite": "2017 ND 245",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 1->3; whitespace: 2 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND245.pdf' /tmp/src_2017ND245.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND245.pdf' <page>."
 },
 {
  "id": 17074,
  "cite": "2017 ND 254",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4; whitespace: 9 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND254.pdf' /tmp/src_2017ND254.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND254.pdf' <page>."
 },
 {
  "id": 17073,
  "cite": "2017 ND 236",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND236.pdf' /tmp/src_2017ND236.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND236.pdf' <page>."
 },
 {
  "id": 17072,
  "cite": "2017 ND 235",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND235.pdf' /tmp/src_2017ND235.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND235.pdf' <page>."
 },
 {
  "id": 17059,
  "cite": "2017 ND 249",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4; whitespace: 5 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND249.pdf' /tmp/src_2017ND249.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND249.pdf' <page>."
 },
 {
  "id": 17058,
  "cite": "2017 ND 238",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND238.pdf' /tmp/src_2017ND238.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND238.pdf' <page>."
 },
 {
  "id": 17057,
  "cite": "2017 ND 237",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND237.pdf' /tmp/src_2017ND237.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND237.pdf' <page>."
 },
 {
  "id": 17056,
  "cite": "2017 ND 252",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4; whitespace: 4 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND252.pdf' /tmp/src_2017ND252.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND252.pdf' <page>."
 },
 {
  "id": 17055,
  "cite": "2017 ND 247",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 4 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND247.pdf' /tmp/src_2017ND247.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND247.pdf' <page>."
 },
 {
  "id": 17054,
  "cite": "2017 ND 244",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 1->4; whitespace: 14 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND244.pdf' /tmp/src_2017ND244.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND244.pdf' <page>."
 },
 {
  "id": 17053,
  "cite": "2017 ND 241",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND241.pdf' /tmp/src_2017ND241.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND241.pdf' <page>."
 },
 {
  "id": 17052,
  "cite": "2017 ND 243",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4; whitespace: 10 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND243.pdf' /tmp/src_2017ND243.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND243.pdf' <page>."
 },
 {
  "id": 17051,
  "cite": "2017 ND 253",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "heading_seq: 2->4; whitespace: 13 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND253.pdf' /tmp/src_2017ND253.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND253.pdf' <page>."
 },
 {
  "id": 17050,
  "cite": "2017 ND 251",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "whitespace: 1 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND251.pdf' /tmp/src_2017ND251.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND251.pdf' <page>."
 },
 {
  "id": 17049,
  "cite": "2017 ND 250",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND250.pdf' /tmp/src_2017ND250.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND250.pdf' <page>."
 },
 {
  "id": 17048,
  "cite": "2017 ND 239",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND239.pdf' /tmp/src_2017ND239.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND239.pdf' <page>."
 },
 {
  "id": 17047,
  "cite": "2017 ND 234",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND234.pdf' /tmp/src_2017ND234.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND234.pdf' <page>."
 },
 {
  "id": 17046,
  "cite": "2017 ND 233",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND233.pdf' /tmp/src_2017ND233.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND233.pdf' <page>."
 },
 {
  "id": 17045,
  "cite": "2017 ND 232",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶19->¶21; heading_seq: 2->4; whitespace: 25 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND232.pdf' /tmp/src_2017ND232.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND232.pdf' <page>."
 },
 {
  "id": 17067,
  "cite": "2017 ND 231",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "paragraph_seq: gap ¶24->¶26; whitespace: 9 blank-runs(3+)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND231.pdf' /tmp/src_2017ND231.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND231.pdf' <page>."
 },
 {
  "id": 17044,
  "cite": "2017 ND 224",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND224.pdf' /tmp/src_2017ND224.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND224.pdf' <page>."
 },
 {
  "id": 17043,
  "cite": "2017 ND 226",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND226.pdf' /tmp/src_2017ND226.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND226.pdf' <page>."
 },
 {
  "id": 17042,
  "cite": "2017 ND 227",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND227.pdf' /tmp/src_2017ND227.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND227.pdf' <page>."
 },
 {
  "id": 17041,
  "cite": "2017 ND 225",
  "era": "2017 (modern, PDF-authoritative)",
  "report": "(no structural flags)",
  "sdesc": "the court's official PDF (the authoritative original; the DB text was derived from it, so any divergence is an ingestion/processing defect)",
  "saccess": "Extract it:  pdftotext -layout '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND225.pdf' /tmp/src_2017ND225.txt  — read it. For a digit/char you must see rendered, use:  mutool draw -r 300 -o /tmp/p%d.png '/Users/jerod/refs/nd/opin/pdfs/2017/2017ND225.pdf' <page>."
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
