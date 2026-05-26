"""Parse a correctly-named C-Track opinion PDF (born-digital, 2018+) into the
fields needed to rebuild a DB row. Authoritative source for cite-swap repairs.

pdftotext layout:
    Filed MM/DD/YY by Clerk of the Supreme Court        (optional; may repeat)
    IN THE SUPREME COURT
    STATE OF NORTH DAKOTA
    YYYY ND n
    <caption parties>
    No. <docket>[ , No. <docket> ...]
    Appeal from the District Court ...
    <DISPOSITION>.
    Opinion of the Court by <Justice>, Justice.   |  Per Curiam.
    ...
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

_CITE = re.compile(r"\b(\d{4})\s+ND\s+(\d+)\b")
_DOCKET = re.compile(r"\bNo\.\s*(\d{8})\b")
_FILED = re.compile(r"Filed\s+(\d{1,2})/(\d{1,2})/(\d{2,4})")
_MONTHS = {m: i for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july",
     "august", "september", "october", "november", "december"], 1)}
_STAMP = re.compile(r"\b(" + "|".join(_MONTHS) + r")\s+(\d{1,2}),\s+(\d{4})", re.I)
_AUTHOR = re.compile(r"Opinion of the Court by\s+([A-Za-z'\-]+),?\s+(?:Justice|C\.?J\.?|Chief Justice)", re.I)
_PERCURIAM = re.compile(r"\bPer Curiam\b", re.I)


def pdftotext(path: Path, page1: bool = False) -> str:
    cmd = ["pdftotext"] + (["-f", "1", "-l", "1"] if page1 else []) + [str(path), "-"]
    return subprocess.run(cmd, capture_output=True, text=True).stdout


def parse(path: Path) -> dict:
    raw = pdftotext(path)                 # full body (plain, flowing text)
    p1 = pdftotext(path, page1=True)      # page 1 only — for the file stamp/cite
    flat = re.sub(r"[ \t]+", " ", raw)
    cite_m = _CITE.search(flat)
    cite = f"{cite_m.group(1)} ND {cite_m.group(2)}" if cite_m else None
    dockets = _DOCKET.findall(flat)
    # filed date from PAGE 1 only (the clerk stamp): "MONTH DD, YYYY" or M/D/YY.
    # NOTE: some stamps are image-only (not OCR'd) — then no date is found and
    # the caller must render+read page 1 visually.
    dates = []
    sm = _STAMP.search(p1)
    if sm:
        dates.append(f"{int(sm.group(3)):04d}-{_MONTHS[sm.group(1).lower()]:02d}-{int(sm.group(2)):02d}")
    for mm, dd, yy in _FILED.findall(p1):
        yyyy = yy if len(yy) == 4 else ("20" + yy)
        dates.append(f"{int(yyyy):04d}-{int(mm):02d}-{int(dd):02d}")
    # caption: between the cite and the first 'No. <docket>'
    caption = None
    if cite_m:
        after = flat[cite_m.end():]
        no = re.search(r"\bNo\.\s*\d{8}", after)
        if no:
            caption = re.sub(r"\s+", " ", after[:no.start()]).strip()
    pc = bool(_PERCURIAM.search(flat[:1500]))
    am = _AUTHOR.search(flat)
    author = None if pc else (am.group(1) if am else None)
    return {"cite": cite, "dockets": dockets, "dates": dates,
            "caption": caption, "per_curiam": pc, "author": author,
            "text": raw.strip(), "text_len": len(raw.strip())}


if __name__ == "__main__":
    import sys
    for p in sys.argv[1:]:
        d = parse(Path(p))
        print(f"{p}")
        print(f"  cite={d['cite']} dockets={d['dockets']} dates={d['dates']} "
              f"pc={d['per_curiam']} author={d['author']} textlen={d['text_len']}")
        print(f"  caption={(d['caption'] or '')[:90]}")
