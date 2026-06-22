"""Classify the sigscan trailing-[¶N]-drop cohort into actionable classes.

`refs_diff sigscan` flags modern opinions whose DB body's max [¶N] marker is
below the complete ~/refs source's. That set is heterogeneous:

  MARKER_GARBLED  - the signature TEXT is present in the DB body; only its [¶N]
                    marker is OCR-garbled ("[IT 29]", "[¶ 21J"), so the marker
                    regex undercounts. NOT a truncation; fix = repair the marker.
  TRUE_TRUNCATION - the signature names are genuinely absent; the DB kept only a
                    single trailing name (the Whetsel class). Fix = splice the
                    complete signature from source.
  CONTENT_LOSS    - a substantive (non-signature) paragraph was dropped; overlaps
                    the known 1997 contamination. Manual triage.
  REVIEW          - ambiguous; needs eyes.

Discriminator: build the set of plausible-justice surnames (those serving in the
opinion's year) found in (a) the dropped SOURCE paragraph(s) and (b) the DB body
tail, with OCR-tolerant matching. If the dropped paragraph carries justice names
it's a signature; whether those names survive in the DB tail separates
MARKER_GARBLED (present) from TRUE_TRUNCATION (absent).

Read-only. Emits triage/sig-drops-classified.csv.
"""
from __future__ import annotations

import csv
import re
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ndcourts_mcp.justices import JUSTICES  # noqa: E402

_FM = re.compile(r"^\s*---\s*\n.*?\n---\s*\n", re.DOTALL)
_PARA = re.compile(r"\[¶\s*(\d+)\]")
_ROLE = re.compile(r"\b(C\.\s*J\.|JJ?\.|S\.\s*J\.|D\.\s*J\.|concur|dissent|sitting in place|Dated at)\b")
DB = Path(__file__).resolve().parent.parent / "opinions.db"
REFS = Path.home() / "refs" / "nd" / "opin"


def _norm(s: str) -> str:
    return re.sub(r"[^A-Z]", "", s.upper())


def _editdist1(a: str, b: str) -> bool:
    if a == b:
        return True
    la, lb = len(a), len(b)
    if abs(la - lb) > 1:
        return False
    # substitution
    if la == lb:
        return sum(1 for x, y in zip(a, b) if x != y) == 1
    # indel
    short, lng = (a, b) if la < lb else (b, a)
    for i in range(len(lng)):
        if short == lng[:i] + lng[i + 1:]:
            return True
    return False


def plausible_surnames(year: int) -> dict[str, str]:
    """Canonical surname (normalized) -> display, for justices serving in `year`."""
    out = {}
    for _key, full, start, end in JUSTICES:
        end_y = end or 2100
        if start - 1 <= year <= end_y + 1:
            last = full.split()[-1]
            if last == "III":
                last = full.split()[-2]
            out[_norm(last)] = last
    return out


def _fuzzy_contains(hay: str, needle: str) -> bool:
    """True if any window of `hay` matches `needle` within edit distance 1.

    Both already normalized (uppercase, alpha-only, no spaces). Catches OCR
    garbles like YANDEWALLE→VANDEWALLE, MAKING→MARING."""
    n = len(needle)
    if n < 4:
        return False
    if needle in hay:
        return True
    for w in (n - 1, n, n + 1):
        for i in range(0, len(hay) - w + 1):
            if _editdist1(needle, hay[i:i + w]):
                return True
    return False


def names_in(text: str, surnames: dict[str, str]) -> set[str]:
    """Set of canonical surnames present in text, OCR-tolerant.

    Normalizes the whole text to spaceless uppercase letters (so VANDE WALLE and
    NEU-MANN rejoin) and fuzzy-matches each surname with an edit-distance-1
    sliding window.
    """
    joined = _norm(text)
    return {disp for nsur, disp in surnames.items() if _fuzzy_contains(joined, nsur)}


# substantive-prose markers: if the dropped text reads like an opinion paragraph
# (sentence verbs, citations) rather than a name list, it is NOT a signature.
_PROSE_RE = re.compile(
    r"\b(argues?|testified|affirm|reverse|remand|conclude[ds]?|held|hold|"
    r"because|whether|district court|N\.W\.2?d|U\.S\.|requires?|consider)\b", re.I)
_FOOTNOTE_RE = re.compile(r"footnote|\bN\.D\.C\.C\.|§|\bId\.\b", re.I)


def is_signature_shape(dropped: str, src_names: set[str]) -> bool:
    """A dropped paragraph is signature-shaped iff it is short and name-dense:
    >=1 plausible justice name, modest length, and not substantive prose."""
    words = dropped.split()
    if not src_names:
        return False
    if len(words) > 45:          # a panel list is short; opinion paragraphs aren't
        return False
    prose_hits = len(_PROSE_RE.findall(dropped))
    return prose_hits == 0


def missing_para_text(src: str, lo: int, hi: int) -> str:
    marks = list(_PARA.finditer(src))
    by_num = {int(m.group(1)): m for m in marks}
    out = []
    for n in range(lo + 1, hi + 1):
        m = by_num.get(n)
        if not m:
            continue
        nxt = [mm.start() for mm in marks if mm.start() > m.end()]
        end = min(nxt) if nxt else len(src)
        out.append(src[m.start():end].strip())
    return "\n".join(out)


def main():
    in_csv = Path("triage/refs-diff-sigscan.csv")
    rows = list(csv.DictReader(in_csv.open()))
    conn = sqlite3.connect(str(DB))
    out = []
    for r in rows:
        oid = int(r["oid"])
        label = r["label"]
        ym = re.match(r"(\d{4}) ND", label)
        year = int(ym.group(1)) if ym else 0
        gap = int(r["gap"])
        sp = r["source_path"]
        tc = conn.execute("SELECT text_content FROM opinions WHERE id=?", (oid,)).fetchone()[0]
        body = _FM.sub("", tc or "")
        full = Path(sp) if sp.startswith("/") else REFS / sp
        src = full.read_text(errors="replace") if full.exists() else ""

        sur = plausible_surnames(year)
        dropped = missing_para_text(src, int(r["db_max"]), int(r["src_max"]))
        tail = body[-450:]

        src_names = names_in(dropped, sur)
        tail_names = names_in(tail, sur)
        present = src_names & tail_names
        sig_shape = is_signature_shape(dropped, src_names)

        if oid == 13291:
            klass, conf = "REVIEW", "corrupt-source ¶478"
        elif gap > 2 or not sig_shape:
            # big gap or prose-heavy drop = lost opinion content, not a signature
            klass, conf = "CONTENT_LOSS", f"gap{gap} not-sig-shape"
        elif len(present) >= max(1, len(src_names) - 1):
            # the panel survives in the DB tail; only the [¶N] marker was garbled
            klass, conf = "MARKER_GARBLED", f"{len(present)}/{len(src_names)} names present"
        elif len(present) <= 1:
            # panel names genuinely absent — the Whetsel class
            klass, conf = "TRUE_TRUNCATION", f"{len(present)}/{len(src_names)} names present"
        else:
            klass, conf = "REVIEW", f"{len(present)}/{len(src_names)} names; gap{gap}"

        out.append(dict(
            oid=oid, label=label, case_name=r["case_name"], year=year, gap=gap,
            db_max=r["db_max"], src_max=r["src_max"], klass=klass, conf=conf,
            src_names="|".join(sorted(src_names)), tail_names="|".join(sorted(tail_names)),
            dropped=dropped[:200].replace("\n", " ⏎ "), source_path=sp))
    conn.close()

    from collections import Counter
    order = {"MARKER_GARBLED": 0, "TRUE_TRUNCATION": 1, "CONTENT_LOSS": 2, "REVIEW": 3}
    out.sort(key=lambda o: (order.get(o["klass"], 9), o["oid"]))
    out_csv = Path("triage/sig-drops-classified.csv")
    with out_csv.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader(); w.writerows(out)
    c = Counter(o["klass"] for o in out)
    for k in ("MARKER_GARBLED", "TRUE_TRUNCATION", "CONTENT_LOSS", "REVIEW"):
        print(f"  {k:16} {c.get(k,0)}")
    print(f"\nWrote {out_csv} ({len(out)} rows)")


if __name__ == "__main__":
    main()
