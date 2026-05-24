"""SCOPE SCAN (read-only) — find + BUCKET opinions whose case_name COLUMN
disagrees with the authoritative caption in their own text_content frontmatter.

Candidate = column-name and frontmatter `title:` share no distinctive party
token. Candidates fall into categories with OPPOSITE correct actions, so we
bucket rather than bulk-apply:

  CONTAMINATION  the column holds a DIFFERENT real case (Longtine/Herrick class):
                 column docket is a synthesized YYYYNDnnn / YYYYMMDD, frontmatter
                 has a real docket, and the frontmatter caption appears in the
                 body. → SAFE TO FIX (column ← frontmatter title/title_full/docket).
  VARIANT        same case, OCR/spelling/spacing difference. The column is often
                 the value corrected by the vols-1–79 case-name sweep, so
                 overwriting from frontmatter would REGRESS it. → LEAVE.
  CONFIDENTIAL   juvenile/adoption/guardianship: the anonymized column caption is
                 correct; the frontmatter title carries party names. Overwriting
                 would DE-ANONYMIZE. → LEAVE + flag for separate vetting.
  REVIEW         everything else (no clear synthetic-docket signal) → manual.

Read-only. `--emit-fixes` prints a Python list of CONTAMINATION fix tuples.
"""

from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from ndcourts_mcp.db import DEFAULT_DB_PATH, get_connection  # noqa: E402

_STOP = {
    "v", "vs", "the", "of", "and", "in", "re", "ex", "rel", "et", "al",
    "state", "north", "dakota", "city", "county", "interest", "matter",
    "estate", "application", "petition", "request", "board", "township",
    "commissioner", "department", "disciplinary", "action", "against",
    "town", "inc", "llc", "llp", "co", "corp", "company", "for", "child",
    "children", "minor", "deceased", "reinstatement", "name", "change",
}
_ANNOT = re.compile(
    r"\(.*?\)|\[.*?\]|,?\s*et\s+al\.?|\bCONFIDENTIAL\b|consolidated.*|consol\..*|"
    r"cross-?ref.*", re.I,
)
_CONF_RE = re.compile(
    r"confidential|interest of|adoption of|guardianship|conservatorship|"
    r"\ba (child|minor)\b|, children", re.I,
)
_INITIALS_PARTY = re.compile(r"\b[A-Z]\.[A-Z]\.")
_SYNTH_DOCKET = re.compile(r"^\d{4}ND\d+$|^\d{8}$")


def _sig_tokens(name: str) -> set[str]:
    name = _ANNOT.sub(" ", name or "")
    toks = re.findall(r"[a-zA-Z]{3,}", name.lower())
    return {t for t in toks if t not in _STOP}


def _norm(name: str) -> str:
    return re.sub(r"[^a-z]", "", _ANNOT.sub("", (name or "")).lower())


def _frontmatter(head: str) -> dict[str, str]:
    m = re.match(r"---\s*\n(.*?)\n---", head, re.S)
    if not m:
        return {}
    fm, out = m.group(1), {}
    for key in ("title", "title_full", "docket_number"):
        km = re.search(rf'^{key}:\s*"?(.*?)"?\s*$', fm, re.M)
        if km and km.group(1).strip():
            out[key] = km.group(1).strip()
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--emit-fixes", action="store_true")
    args = ap.parse_args()

    conn = get_connection(DEFAULT_DB_PATH)
    rows = conn.execute(
        "SELECT id, case_name, docket_number, "
        "substr(text_content, 1, 1600) AS head FROM opinions"
    ).fetchall()

    buckets: dict[str, list] = {"CONTAMINATION": [], "VARIANT": [],
                                "CONFIDENTIAL": [], "REVIEW": []}
    for r in rows:
        fm = _frontmatter(r["head"])
        title = fm.get("title")
        if not title:
            continue
        col_tok, fm_tok = _sig_tokens(r["case_name"]), _sig_tokens(title)
        if not col_tok or not fm_tok or not col_tok.isdisjoint(fm_tok):
            continue

        col, col_dock = r["case_name"], (r["docket_number"] or "")
        fm_dock = fm.get("docket_number", "")
        rec = (r["id"], col, title, fm.get("title_full"), col_dock, fm_dock)

        if difflib.SequenceMatcher(None, _norm(col), _norm(title)).ratio() >= 0.72:
            buckets["VARIANT"].append(rec)
        elif _CONF_RE.search(col) or _CONF_RE.search(title) or _INITIALS_PARTY.search(title):
            buckets["CONFIDENTIAL"].append(rec)
        elif _SYNTH_DOCKET.match(col_dock) and fm_dock and not _SYNTH_DOCKET.match(fm_dock):
            # body must confirm the frontmatter caption (a distinctive token of it)
            body = r["head"].lower()
            if any(t in body for t in fm_tok):
                buckets["CONTAMINATION"].append(rec)
            else:
                buckets["REVIEW"].append(rec)
        else:
            buckets["REVIEW"].append(rec)

    for name, recs in buckets.items():
        print(f"\n===== {name}: {len(recs)} =====")
        for oid, col, title, _tf, cd, fd in sorted(recs):
            dock = f"  [docket {cd!r}->{fd!r}]" if fd and fd != cd else ""
            print(f"  oid {oid}: {col!r}  ==>  {title!r}{dock}")

    if args.emit_fixes:
        print("\n# CONTAMINATION fix tuples (oid, old_case_name):")
        print("FIX_OIDS = [")
        for oid, col, *_ in sorted(buckets["CONTAMINATION"]):
            print(f"    ({oid}, {col!r}),")
        print("]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
