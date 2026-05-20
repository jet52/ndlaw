"""Digital adjudication of mispaired Westlaw .docs for vols 16-79.

Methodology (per fix-casenames-vol11-15-bound-2026-05-19 batch):
    1. Each row in casenames-mispaired-2026-05-18.tsv pairs a .doc to a DB
       opinion via *shared citation*; the .doc caption may belong to that
       opinion or to a sibling on the same page.
    2. Compute jaccard(.doc body tokens, DB row text_content tokens).
       SAME (jac >= 0.55)  -> the .doc IS this opinion -> fix DB case_name.
       DIFF (jac < 0.20)   -> sibling on shared cite.
                              * if .doc is already paired with a DIFFERENT
                                opinion in opinion_sources -> ALREADY_PAIRED
                                (false positive; no DB change).
                              * else -> ORPHAN_SIBLING (potential corpus
                                gap, flag for human).
       AMBIG (mid-band)    -> defer to human review.
    3. Also detect FALSE_POSITIVE_NORM: where wl_doc_caption and DB row
       case_name only differ by curly-apos / ligature / case (e.g.
       'O’Malley' vs "O'Malley"). DB already matches bound, no change.

Output: triage/casenames-mispaired-adjudication-2026-05-20.tsv
        + summary printed to stdout.

Does NOT modify the DB. Apply via a separate --apply step after review.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from ndcourts_mcp.db import get_connection, DEFAULT_DB_PATH  # noqa: E402
from ndcourts_mcp.ingest_westlaw import (  # noqa: E402
    _doc_to_text,
    _normalize_case_name,
)
from ndcourts_mcp.review_casenames import (  # noqa: E402
    normalize_westlaw_name,
)

INPUT_TSV = REPO / "triage" / "casenames-mispaired-2026-05-18.tsv"
OUTPUT_TSV = REPO / "triage" / "casenames-mispaired-adjudication-2026-05-20.tsv"

JAC_SAME = 0.55
JAC_DIFF = 0.20

# Stopwords kept narrow — bound-text opinions overlap heavily in legal boilerplate,
# but we mostly want to distinguish DIFFERENT case bodies. Keep most legal terms.
_WORD = re.compile(r"[a-z]{4,}")  # 4+ letter words only, lowercased

# Drop the most common procedural/legal words that appear in nearly every opinion
# and inflate jaccard between unrelated cases on the same page.
_STOP = {
    "court", "case", "cause", "appeal", "appellant", "appellee", "respondent",
    "plaintiff", "plaintiffs", "defendant", "defendants", "judgment", "judgments",
    "order", "motion", "trial", "term", "north", "dakota", "supreme", "syllabus",
    "opinion", "filed", "this", "that", "with", "from", "have", "were", "been",
    "their", "they", "such", "which", "upon", "said", "shall", "would", "where",
    "there", "thereof", "therein", "thereto", "wherein", "whether", "before",
    "after", "above", "under", "must", "made", "make", "also", "found", "find",
    "held", "hold", "held",
}


def tokens(text: str) -> set[str]:
    text = (text or "").lower()
    return {w for w in _WORD.findall(text) if w not in _STOP}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def normalize_unicode(s: str) -> str:
    """Normalize curly apostrophes and ligatures so casefold-equivalent
    captions don't get flagged as mispaired."""
    s = unicodedata.normalize("NFKD", s)
    s = s.replace("’", "'").replace("‘", "'")
    s = s.replace("“", '"').replace("”", '"')
    s = re.sub(r"[̀-ͯ]", "", s)  # strip combining marks (ae<->æ)
    return s


_TRAIL_DATE = re.compile(
    r"\s+(?:Jan|Feb|Mar(?:ch)?|Apr(?:il)?|May|June?|July?|Aug|Sept?|Oct|Nov|Dec)\.?"
    r"\s+\d{1,2}[.,]?\s+\d{4}\s*\.?\s*$",
    re.IGNORECASE,
)
_LEAD_DOCKET = re.compile(
    r"^\s*(?:Cr|Civ|Crim)(?:im(?:inal)?|il)?\.?\s+(?:No\.\s*)?\d+[A-Za-z]?\.?\s*\|?\s*",
    re.IGNORECASE,
)
_INTRA_DOCKET = re.compile(
    r"\s+(?:Cr|Civ|Crim)(?:im(?:inal)?|il)?\.?\s+(?:No\.\s*)?\d+[A-Za-z]?\.?\s*\|?\s*$",
    re.IGNORECASE,
)
_TRAIL_DANGLING_V = re.compile(r"\s+v\.?\s*$", re.IGNORECASE)
# Standalone trailing docket marker left behind after the number stripped
# off (e.g. "...Warden. Cr." -> "...Warden.") — distinct from _INTRA_DOCKET
# which requires the number to be present.
_TRAIL_BARE_DOCKET = re.compile(
    r"\.\s*(?:Cr|Civ|Crim)\.?\s*\|?\s*$", re.IGNORECASE,
)


def deep_strip(s: str) -> str:
    """Apply normalize_westlaw_name then strip residual artifacts that the
    review_casenames regexes miss: trailing dates ('June 19. 1907'),
    'Cr.' docket prefixes embedded mid-caption, and trailing dangling 'v.'.
    Does NOT strip legitimate trailing abbreviation periods ('Co.', 'Ry.',
    'Inc.') — that's normalize_westlaw_name's job and it's already correct."""
    s = normalize_westlaw_name(s)
    for _ in range(5):
        prev = s
        s = _TRAIL_DATE.sub("", s).rstrip()
        s = _INTRA_DOCKET.sub("", s).rstrip()
        s = _TRAIL_DANGLING_V.sub("", s).rstrip()
        s = _TRAIL_BARE_DOCKET.sub(".", s).rstrip()
        # Strip trailing comma only — leave periods to normalize_westlaw_name.
        s = re.sub(r",\s*$", "", s).rstrip()
        if s == prev:
            break
    return s


def captions_equal_after_norm(db_name: str, wl_caption: str) -> bool:
    """True if the DB caption and Westlaw caption are equal after Unicode
    + deep-strip + ndcourts_mcp._normalize_case_name normalization."""
    db_norm = _normalize_case_name(normalize_unicode(db_name))
    wl_clean = deep_strip(normalize_unicode(wl_caption))
    wl_norm = _normalize_case_name(wl_clean)
    return bool(db_norm) and db_norm == wl_norm


def smart_titlecase(s: str) -> str:
    """Title-case while keeping connectives lowercase and handling
    Mc/Mac/O' prefixes (regression in review_casenames._smart_titlecase
    surfaced by the vol-11-15 batch). E.g. McDEVITT -> McDevitt,
    O’TOOLE -> O'Toole, MacH. CO. -> Mach. Co.
    """
    s = normalize_unicode(s)
    lowercase_tokens = {"v.", "v", "ex", "rel.", "rel", "and", "of", "the",
                        "in", "re", "et", "al.", "for", "to", "&"}
    out = []
    for word in s.split(" "):
        wl = word.lower()
        if wl in lowercase_tokens and out:
            out.append(wl)
            continue
        # Mixed-case Mc/Mac (e.g. "McKEE'S") — the rest of the body is upper,
        # so handle these even though word.isupper() is False.
        mm = re.match(r"^(Mc|Mac)([A-Z]+)(.*)$", word)
        if mm and mm.group(2):
            pre, body, tail = mm.groups()
            first, rest = body[0], body[1:]
            tail = re.sub(r"'S(?=\W|$)", "'s", tail.title())
            out.append(f"{pre}{first}{rest.lower()}{tail}")
            continue
        if word.isupper() and len(word) > 1:
            # Preserve U.S. style initialisms
            if re.fullmatch(r"[A-Z]\.(?:[A-Z]\.)+", word):
                out.append(word)
                continue
            # Mc / Mac prefix — allow any non-letter tail (possessive, period)
            mm = re.match(r"^(Mc|Mac)([A-Z])([A-Z]+)(.*)$", word)
            if mm:
                pre, first, rest, tail = mm.groups()
                tail = re.sub(r"'S(?=\W|$)", "'s", tail.title())
                out.append(f"{pre}{first}{rest.lower()}{tail}")
                continue
            # O' prefix (apostrophe already normalized to straight)
            om = re.match(r"^O'([A-Z])([A-Z]*)(.*)$", word)
            if om:
                first, rest, tail = om.groups()
                tail = re.sub(r"'S(?=\W|$)", "'s", tail.title())
                out.append(f"O'{first}{rest.lower()}{tail}")
                continue
            titled = word.title()
            # word.title() inserts upper after apostrophe ("BRADY'S" -> "Brady'S");
            # restore the lowercase possessive "'s".
            titled = re.sub(r"'S(?=\W|$)", "'s", titled)
            out.append(titled)
        else:
            out.append(word)
    return " ".join(out)


def read_mispaired() -> list[dict]:
    with INPUT_TSV.open() as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--volumes", default=None,
                        help="Restrict to volumes (e.g. '16-79' or '16,17,18')")
    args = parser.parse_args()

    vol_filter: set[int] | None = None
    if args.volumes:
        vf: set[int] = set()
        for part in args.volumes.split(","):
            if "-" in part:
                lo, hi = part.split("-", 1)
                vf.update(range(int(lo), int(hi) + 1))
            else:
                vf.add(int(part))
        vol_filter = vf

    conn = get_connection(args.db)
    rows = read_mispaired()
    if vol_filter:
        rows = [r for r in rows if int(r["volume"]) in vol_filter]
    print(f"Adjudicating {len(rows)} mispaired entries"
          f"{f' (vols {sorted(vol_filter)[0]}-{sorted(vol_filter)[-1]})' if vol_filter else ''}")

    verdicts: list[dict] = []
    for r in rows:
        oid = int(r["opinion_id"])
        doc_path = Path(r["doc_path"])
        op_text = conn.execute(
            "SELECT case_name, text_content FROM opinions WHERE id = ?", (oid,)
        ).fetchone()
        if not op_text:
            verdicts.append({**r, "jaccard": "", "verdict": "MISSING_OP",
                             "suggested_action": "skip",
                             "suggested_new_value": "",
                             "doc_pair_oid": "", "doc_pair_name": ""})
            continue
        db_name = op_text["case_name"] or ""
        db_text = op_text["text_content"] or ""

        # FALSE_POSITIVE_NORM: captions only differ by unicode/ligature
        if captions_equal_after_norm(db_name, r["wl_doc_caption"]):
            verdicts.append({**r, "jaccard": "1.000",
                             "verdict": "FALSE_POSITIVE_NORM",
                             "suggested_action": "no_change",
                             "suggested_new_value": "",
                             "doc_pair_oid": "", "doc_pair_name": ""})
            continue

        # Compute jaccard over .doc body
        try:
            doc_body = _doc_to_text(doc_path)
        except Exception as e:
            verdicts.append({**r, "jaccard": "", "verdict": f"DOC_ERROR:{e}",
                             "suggested_action": "skip",
                             "suggested_new_value": "",
                             "doc_pair_oid": "", "doc_pair_name": ""})
            continue

        jac = jaccard(tokens(doc_body), tokens(db_text))
        jac_str = f"{jac:.3f}"

        # Is this .doc already paired with a DIFFERENT opinion via opinion_sources?
        pair = conn.execute(
            """SELECT o.id, o.case_name FROM opinion_sources s
                  JOIN opinions o ON o.id = s.opinion_id
                  WHERE s.source_path = ? AND s.source_reporter = 'westlaw'""",
            (str(doc_path),),
        ).fetchone()
        pair_oid = pair["id"] if pair else ""
        pair_name = pair["case_name"] if pair else ""

        if jac >= JAC_SAME:
            wl_raw = r["wl_doc_caption"]
            wl_clean = deep_strip(normalize_unicode(wl_raw))
            new_value = smart_titlecase(wl_clean)
            # Re-check FALSE_POSITIVE_NORM after deep_strip: caption may
            # have a date/docket suffix that masked an equivalence.
            if _normalize_case_name(wl_clean) == _normalize_case_name(
                normalize_unicode(db_name)
            ):
                verdicts.append({
                    **r, "jaccard": jac_str,
                    "verdict": "FALSE_POSITIVE_NORM",
                    "suggested_action": "no_change",
                    "suggested_new_value": "",
                    "doc_pair_oid": pair_oid, "doc_pair_name": pair_name,
                })
                continue
            # Safety: any proposal still containing residue (trailing 'v.',
            # 'Cr', solo year, dangling 'No.') gets bumped to human review.
            # Also flag truncated-source captions — the Westlaw caption itself
            # ends with 'v.' (no defendant), so we'd publish an incomplete name.
            wl_raw_stripped = re.sub(r"[\s|]+$", "",
                                     normalize_unicode(wl_raw))
            truncated_source = re.search(r"\sv\.?$", wl_raw_stripped) is not None
            sus = (
                re.search(r"\sv\.?\s*$", new_value)
                or re.search(r"\bCr\s*$", new_value)
                or re.search(r"\bNo\.?\s*\d*\s*$", new_value)
                or re.search(r"\b(?:19|18|20)\d{2}\s*\.?\s*$", new_value)
                or truncated_source
            )
            if sus:
                verdicts.append({
                    **r, "jaccard": jac_str,
                    "verdict": "SAME_NEEDS_HUMAN",
                    "suggested_action": "human_review",
                    "suggested_new_value": new_value,
                    "doc_pair_oid": pair_oid, "doc_pair_name": pair_name,
                })
                continue
            verdicts.append({
                **r, "jaccard": jac_str, "verdict": "SAME",
                "suggested_action": "update_case_name",
                "suggested_new_value": new_value,
                "doc_pair_oid": pair_oid, "doc_pair_name": pair_name,
            })
        elif jac < JAC_DIFF:
            if pair and pair["id"] != oid:
                verdict = "ALREADY_PAIRED"
                action = "no_change"
            elif pair and pair["id"] == oid:
                # .doc paired with THIS opinion yet body doesn't match — shouldn't
                # happen but flag it. Could be wrong opinion_sources entry.
                verdict = "SELF_PAIRED_LOW_JAC"
                action = "human_review"
            else:
                verdict = "ORPHAN_SIBLING"
                action = "human_review_potential_gap"
            verdicts.append({
                **r, "jaccard": jac_str, "verdict": verdict,
                "suggested_action": action,
                "suggested_new_value": "",
                "doc_pair_oid": pair_oid, "doc_pair_name": pair_name,
            })
        else:
            verdicts.append({
                **r, "jaccard": jac_str, "verdict": "AMBIG",
                "suggested_action": "human_review",
                "suggested_new_value": "",
                "doc_pair_oid": pair_oid, "doc_pair_name": pair_name,
            })

    # Write output
    cols = ["volume", "opinion_id", "primary_citation", "db_name",
            "opinion_text_title", "wl_doc_caption", "doc_path",
            "jaccard", "verdict", "suggested_action", "suggested_new_value",
            "doc_pair_oid", "doc_pair_name"]
    with OUTPUT_TSV.open("w") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, delimiter="\t",
                           extrasaction="ignore")
        w.writeheader()
        for v in verdicts:
            w.writerow(v)

    # Summary
    from collections import Counter
    by_verdict = Counter(v["verdict"] for v in verdicts)
    print("\nVerdict breakdown:")
    for k in sorted(by_verdict):
        print(f"  {k:<26}  {by_verdict[k]}")
    print(f"\nWrote {OUTPUT_TSV.relative_to(REPO)}")
    print(f"  apply with: python triage/apply_mispaired_2026-05-20.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
