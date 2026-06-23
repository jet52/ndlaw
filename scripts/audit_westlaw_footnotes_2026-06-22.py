"""Audit: which Westlaw-sourced opinions lost their footnotes at ingest?

`ingest_westlaw._parse_westlaw_doc` cuts the opinion at the "All Citations"
footer; the Westlaw `Footnotes` section prints *after* that line, so footnote
bodies were dropped from the stored text. This re-parses each archived `.doc`,
extracts its footnote section, and checks whether those bodies survive in the
opinion's `text_content`.

Read-only. Writes `triage/westlaw-footnote-audit.tsv` + a summary. Use --limit
for a quick sample. The MISSING rows are the re-ingest worklist for the
HTML-based parser fix.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

REFS = [Path.home() / "refs/nd/opin", Path.home() / "refs/opin"]
OUT = Path("triage/westlaw-footnote-audit.tsv")


def doc_to_text(path: Path) -> str:
    r = subprocess.run(["textutil", "-convert", "txt", "-stdout", str(path)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip())
    return r.stdout


def resolve(sp: str) -> Path | None:
    for root in REFS:
        p = root / sp
        if p.exists():
            return p
    p = Path(sp)
    return p if p.exists() else None


def footnote_section(text: str) -> str:
    """Text of the trailing `Footnotes` section, or '' if none."""
    lines = text.splitlines()
    fn_idx = None
    for j in range(len(lines) - 1, -1, -1):
        if lines[j].strip() == "Footnotes":
            fn_idx = j
            break
    if fn_idx is None:
        return ""
    body = []
    for l in lines[fn_idx + 1:]:
        s = l.strip()
        if s == "End of Document" or s.startswith("©"):
            break
        body.append(l)
    return "\n".join(body).strip()


def _alnum(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def snippets(fn_text: str, n: int = 3, length: int = 50) -> list[str]:
    """Distinctive normalized windows of footnote *body* prose (skip the bare
    number/citation-link lines), for presence testing against stored text."""
    prose = " ".join(l for l in fn_text.splitlines()
                     if len(l.strip()) > 20 and not l.strip().isdigit())
    a = _alnum(prose)
    if len(a) < length:
        return [a] if a else []
    step = max(1, (len(a) - length) // n)
    return [a[i:i + length] for i in range(0, len(a) - length + 1, step)][:n]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", default="opinions.db")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    import sqlite3
    con = sqlite3.connect(args.db)
    q = """SELECT o.id, o.text_content,
                  (SELECT os.source_path FROM opinion_sources os
                     WHERE os.opinion_id=o.id AND os.source_reporter='westlaw'
                       AND os.source_path LIKE '%.doc' LIMIT 1) AS doc,
                  (SELECT c.citation FROM citations c
                     WHERE c.opinion_id=o.id ORDER BY c.is_primary DESC LIMIT 1) AS cite
           FROM opinions o WHERE o.source_reporter='westlaw'"""
    rows = con.execute(q).fetchall()
    if args.limit:
        rows = rows[:args.limit]

    OUT.parent.mkdir(exist_ok=True)
    counts = {"MISSING_NUM": 0, "MISSING_LETTERED": 0, "PRESENT": 0,
              "NO_FOOTNOTES": 0, "NO_DOC": 0, "ERR": 0}
    out_rows = []
    for k, (oid, text, doc, cite) in enumerate(rows):
        if k % 500 == 0:
            print(f"  {k}/{len(rows)}...", file=sys.stderr)
        if not doc:
            counts["NO_DOC"] += 1
            out_rows.append((oid, cite, "NO_DOC", "", 0, ""))
            continue
        path = resolve(doc)
        if path is None:
            counts["NO_DOC"] += 1
            out_rows.append((oid, cite, "NO_DOC", "", 0, doc))
            continue
        try:
            fn = footnote_section(doc_to_text(path))
        except Exception as e:
            counts["ERR"] += 1
            out_rows.append((oid, cite, "ERR", "", 0, str(e)[:60]))
            continue
        if not fn:
            counts["NO_FOOTNOTES"] += 1
            out_rows.append((oid, cite, "NO_FOOTNOTES", "", 0, ""))
            continue
        snips = snippets(fn)
        stored = _alnum(text or "")
        hits = sum(1 for s in snips if s and s in stored)
        # Substantive numbered footnotes (bare-digit label lines) vs Westlaw
        # lettered/star notes (a1/A1/*, usually "Rehearing denied …" or attorney
        # daggers) — different value, tracked separately.
        n_fn = len(re.findall(r"(?m)^\s*\d{1,3}\s*$", fn))
        kind = "numbered" if n_fn else "lettered"
        if hits == 0:
            counts["MISSING_NUM" if n_fn else "MISSING_LETTERED"] += 1
            out_rows.append((oid, cite, "MISSING", kind, n_fn, fn[:80].replace("\n", " ")))
        else:
            counts["PRESENT"] += 1
            out_rows.append((oid, cite, "PRESENT", kind, n_fn, ""))

    with OUT.open("w") as f:
        f.write("opinion_id\tcite\tstatus\tkind\tfn_count\tnote\n")
        for r in out_rows:
            f.write("\t".join(str(x) for x in r) + "\n")

    print(f"\nScanned {len(rows)} westlaw-sourced opinions:")
    for k, v in counts.items():
        print(f"  {k:14} {v}")
    print(f"\nWrote {OUT}")
    print("MISSING rows = footnote bodies dropped at ingest (re-ingest worklist).")


if __name__ == "__main__":
    main()
