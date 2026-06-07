#!/usr/bin/env python3
"""Validate the ND Constitution 1889 base text (Model 1 history) against two
independent authorities.

The base text we ingest is ndconst.org's 1889 snapshot (a clean transcription).
This script cross-checks every section of that base, by CONTENT (not by section
number — the sources use different numbering conventions), against:

  1. The official 1889 publication PDF (ndlegis.gov historical-constitution-
     documents) — requires `pdftotext` (poppler) on PATH; OCR-noisy.
  2. The State Constitutions Project transcription (stateconstitutions.umd.edu).

For each base section it reports the best content-similarity found in either
source. Sections matching >=0.85 are considered validated; the handful below are
listed for manual review (empirically all benign: umd-side OCR, section-number
prefixes, digits-vs-words, or section-boundary segmentation).

Usage: python scripts/validate_1889_base.py
"""

import difflib
import re
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

NDCONST = "https://ndconst.org/date/1889-11-02?do=export_raw"
UMD = "http://www.stateconstitutions.umd.edu/texts/ND_1889_final_parts_0.txt"
PDF = ("https://ndlegis.gov/sites/default/files/resource/"
       "historical-constitution-documents/1889-constitution.pdf")
UA = "ndcourts-mcp 1889-validation (CC0 corpus build)"


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def norm(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def parse_ndconst(raw: str) -> list[tuple[str, str]]:
    out, art, sec, buf = [], None, None, []
    def flush():
        nonlocal sec, buf
        if sec is not None:
            out.append((f"{art}:{sec}", "\n".join(buf).strip()))
        buf = []
    for line in raw.splitlines():
        if (m := re.match(r"=====\s*ARTICLE\s+([IVXLCDM]+)", line)):
            flush(); sec = None; art = m.group(1); continue
        if (m := re.match(r"=====\s*(SCHEDULE|PREAMBLE)", line, re.I)):
            flush(); sec = None; art = m.group(1).upper(); continue
        if (m := re.match(r"===\s*Section\s+([0-9A-Za-z]+)\.\s*===", line)):
            flush(); sec = m.group(1); continue
        if sec is not None:
            buf.append(line)
    flush()
    return out


def parse_blocks_umd(raw: str) -> list[str]:
    out, cur, buf = [], None, []
    for line in raw.splitlines():
        if "SSTART" in line:
            if cur:
                out.append("\n".join(buf).strip())
            buf, cur = [], 1; continue
        if line.startswith("***"):
            if cur:
                out.append("\n".join(buf).strip())
            buf, cur = [], None; continue
        if cur:
            buf.append(line)
    if cur:
        out.append("\n".join(buf).strip())
    return [t for t in out if t]


def parse_blocks_pdf(text: str) -> list[str]:
    parts = re.split(r"\n\s*§\s*\d+\.", text)
    return [p.strip() for p in parts if len(p.strip()) > 40]


def best(n: str, pool: list[str]) -> float:
    return max((difflib.SequenceMatcher(None, n, p).ratio() for p in pool), default=0.0)


def main() -> int:
    ndc = parse_ndconst(get(NDCONST).decode("utf-8", "replace"))
    umd = [norm(t) for t in parse_blocks_umd(get(UMD).decode("utf-8", "replace"))]

    pdf: list[str] = []
    if (exe := _which("pdftotext")):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "c.pdf"
            p.write_bytes(get(PDF))
            subprocess.run([exe, "-layout", str(p), str(Path(d) / "c.txt")], check=True)
            pdf = [norm(t) for t in parse_blocks_pdf((Path(d) / "c.txt").read_text())]
    else:
        print("WARNING: pdftotext not found; validating against umd only.", file=sys.stderr)

    rows = [(label, max(best(norm(t), umd), best(norm(t), pdf) if pdf else 0.0))
            for label, t in ndc]
    for thr in (0.95, 0.90, 0.85):
        print(f"  >= {thr}: {sum(1 for _, s in rows if s >= thr)}/{len(rows)}")
    flagged = [(l, s) for l, s in rows if s < 0.85]
    print(f"\nbelow 0.85 (manual review) [{len(flagged)}]:")
    for label, s in flagged:
        print(f"   {label:14} best={s:.2f}")
    return 0


def _which(name: str):
    from shutil import which
    return which(name)


if __name__ == "__main__":
    raise SystemExit(main())
