"""Classify the 2,054 ambiguous case-name diffs into buckets.

Buckets:
  KEEP_DB_PURE_ABBREV   — Westlaw is strictly a shorter abbreviation of DB
  KEEP_DB_HAS_REL       — DB has 'ex rel.'/'Ex Rel.' that Westlaw drops
  KEEP_DB_HAS_ESTATE    — DB has 'Estate of' framing that Westlaw drops
  ACCEPT_WL_OCR_FIX     — DB has surname OCR garble that Westlaw fixes
                          (Levenshtein-1 on a single surname token)
  ACCEPT_WL_ENCODING_FIX — DB has Unicode garbage (&198, ¤, &amp;) Westlaw fixes
  ACCEPT_WL_ADDS_DETAIL — Westlaw adds role suffix or locality detail
                          that DB lacks (Atty. Gen., Sheriff, "of X")
  ACCEPT_WL_FULL_NAME   — DB has truncated/abbreviated party where Westlaw
                          has the full proper name (e.g. DB Aetna, WL Ætna)
  DEFER_WL_GARBAGE      — Westlaw caption contains encoding garbage or parser
                          artifacts (¤, &198, "(two cases)", trailing "v.")
  DEFER_MULTICASE       — Westlaw caption has "Same v. ..." or multiple v.s
                          (multi-case consolidated bound captions)
  DEFER_AMBIG           — anything else

Writes triage/casenames-ambig-review-classified-2026-05-20.tsv.
"""
from __future__ import annotations

import csv
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from ndcourts_mcp.ingest_westlaw import _normalize_case_name  # noqa: E402
from ndcourts_mcp.review_casenames import normalize_westlaw_name  # noqa: E402

INPUT = REPO / "triage" / "casenames-ambig-review-2026-05-20.tsv"
OUTPUT = REPO / "triage" / "casenames-ambig-review-classified-2026-05-20.tsv"

# Abbreviation expansions — if DB has the long form and WL has the short
# form (or vice-versa), treat as pure abbreviation.
ABBREVS = {
    "manufacturing": "mfg",
    "company": "co",
    "companies": "cos",
    "corporation": "corp",
    "incorporated": "inc",
    "association": "assn",
    "associations": "assns",
    "railway": "ry",
    "railroad": "rr",
    "insurance": "ins",
    "investment": "inv",
    "investments": "invs",
    "national": "nat",
    "northern": "n",
    "southern": "s",
    "eastern": "e",
    "western": "w",
    "pacific": "pac",
    "saint": "st",
    "sainte": "ste",
    "district": "dist",
    "department": "dept",
    "township": "tp",
    "commissioners": "commrs",
    "cooperative": "co-op",
    "mutual": "mut",
    "telephone": "tel",
    "electric": "elec",
    "hospital": "hosp",
    "board": "bd",
    "limited": "ltd",
    "machine": "mach",
    "construction": "const",
    "savings": "sav",
    "service": "serv",
    "transportation": "transp",
    "supervisor": "super",
    "supervisors": "supers",
}
ABBREVS_REV = {v: k for k, v in ABBREVS.items()}


# Garbage character or sequence in either string
GARBAGE_RX = re.compile(r"(?:&\d+|¤|&amp;|&#\d+|\x00|�)")

# Role suffix attached after the defendant (Atty. Gen., Sheriff, etc.)
ROLE_RX = re.compile(
    r",\s*(?:District\s+Judge|State\s+Auditor|Attorney\s+General"
    r"|Atty\.\s+Gen\.|Secretary\s+of\s+State|Governor|Mayor"
    r"|County\s+Auditor|Sheriff|Treasurer|Tax\s+Commissioner"
    r"|State'?s\s+Atty\.|State\s+Fire\s+Marshal|Judge|Trustee"
    r"|Warden|County\s+Com'?rs?|Commrs?|Garnishee|Intervener"
    r"|Plaintiff[-\s]?Respondent|Defendant[-\s]?Appellant"
    r"|Defendants?|Appellants?|Respondents?|Owners?"
    r")s?\.?\s*",
    re.IGNORECASE,
)

# "of <PLACE>" appended (with optional state)
LOCALITY_RX = re.compile(
    r"\s+(?:of|in)\s+[A-Z][A-Za-z.&'-]+(?:[,\s]+[A-Z][A-Za-z.&'-]+)*"
    r"(?:[,\s]+(?:N\.\s*D\.|S\.\s*D\.|Minn\.|Mont\.|Wis\.|Ia\.|Ill\.|U\.\s*S\.|N\.\s*Y\.))?",
)

# Multi-case markers
MULTICASE_RX = re.compile(
    r"\b(?:Same\s+v\.|\(two\s+cases\)|\(three\s+cases\)|Consolidated)",
    re.IGNORECASE,
)

# DB has "ex rel."/"Estate of" framing that WL might drop
EX_REL_RX = re.compile(r"\b(?:ex\s+rel\.?|estate\s+of|re\s+the)\b", re.IGNORECASE)


def norm_unicode(s: str) -> str:
    return unicodedata.normalize("NFKD", s).replace("'", "'").replace("'", "'")


def core_tokens(s: str) -> list[str]:
    """Lowercase the case-name down to its essential word stems for
    abbreviation comparison: strip punctuation, lowercase, drop common
    connectives, and collapse abbreviations to their canonical short form."""
    s = norm_unicode(s).lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    out = []
    for tok in s.split():
        if tok in {"v", "vs", "the", "of", "and", "in", "re", "ex", "rel",
                   "for", "to", "et", "al", "ux", "vir", "a"}:
            continue
        # canonicalize to abbreviation form
        out.append(ABBREVS.get(tok, tok))
    return out


def _matches_or_abbreviates(wl_tok: str, db_tok: str) -> bool:
    """True if a Westlaw token is either equal to a DB token or a
    canonical abbreviation of it. Covers: exact match, canonical abbrev
    map (mfg/manufacturing), single-letter prefix (p./paul, s./sault),
    or stem prefix (mach/machine, ph/phoenix)."""
    if wl_tok == db_tok:
        return True
    if ABBREVS.get(db_tok) == wl_tok:
        return True
    if ABBREVS_REV.get(wl_tok) == db_tok:
        return True
    # Single-letter or two-letter abbreviation (st. p. -> paul, s.s.m. -> sault/ste/marie)
    if len(wl_tok) <= 2 and db_tok.startswith(wl_tok):
        return True
    # Stem abbreviation (mach -> machine, mfr -> manufacturer)
    if len(wl_tok) >= 3 and db_tok.startswith(wl_tok):
        return True
    return False


def is_pure_abbreviation(db: str, wl: str) -> bool:
    """True if WL is a strict abbreviation/shortening of DB. Every WL
    core token must align in order to a DB token via _matches_or_abbreviates,
    AND every DB token must be covered by some WL token (no information
    lost — just shortened)."""
    db_t = core_tokens(db)
    wl_t = core_tokens(wl)
    if not wl_t or not db_t:
        return False
    # Greedy ordered alignment of WL tokens to DB tokens.
    i = 0
    covered = [False] * len(db_t)
    for wt in wl_t:
        found = -1
        for j in range(i, len(db_t)):
            if _matches_or_abbreviates(wt, db_t[j]):
                found = j
                break
        if found < 0:
            return False
        covered[found] = True
        i = found + 1
    # Every DB token must be covered (no DB-only information that WL omits).
    return all(covered)


def is_pure_abbreviation_with_parties(db: str, wl: str) -> bool:
    """True if WL is a pure-abbreviation of DB on BOTH sides of 'v.' separately.
    Loosens the strict full-sequence requirement when only one party is
    being abbreviated (handles 'Manufacturing Co.' vs 'Mfg. Co.' even if
    plaintiff sides have different word counts)."""
    def split_v(s):
        # use the lowercase-normalized form
        s_low = norm_unicode(s).lower()
        parts = re.split(r"\bv\.?\b", s_low, maxsplit=1)
        return parts if len(parts) == 2 else None
    a = split_v(db)
    b = split_v(wl)
    if not a or not b:
        return False
    return is_pure_abbreviation(a[0], b[0]) and is_pure_abbreviation(a[1], b[1])


def is_db_extra_only(db: str, wl: str) -> bool:
    """True if DB has tokens that WL lacks (i.e. DB is strictly more
    informative). Catches 'Magoffin v. Watros ex rel. Brouillard' (DB)
    vs 'Magoffin v. Watros' (WL)."""
    db_t = core_tokens(db)
    wl_t = core_tokens(wl)
    if not wl_t or not db_t:
        return False
    if len(db_t) <= len(wl_t):
        return False
    # Every WL token (canonicalized) must appear in DB tokens.
    db_set = set(db_t)
    for t in wl_t:
        if t not in db_set and ABBREVS_REV.get(t, t) not in db_set:
            return False
    return True


def lev1(a: str, b: str) -> bool:
    if a == b:
        return True
    if abs(len(a) - len(b)) > 1 or min(len(a), len(b)) < 4:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) == 1
    lo, hi = (a, b) if len(a) < len(b) else (b, a)
    for i in range(len(hi)):
        if lo == hi[:i] + hi[i + 1:]:
            return True
    return False


def detect_ocr_fix(db: str, wl: str) -> bool:
    """True if DB and WL differ by Levenshtein-1 on a single surname
    token AND every other token matches (after abbrev canonicalization)."""
    db_t = core_tokens(db)
    wl_t = core_tokens(wl)
    if len(db_t) != len(wl_t):
        return False
    diff_idx = []
    for i, (a, b) in enumerate(zip(db_t, wl_t)):
        if a != b and ABBREVS_REV.get(a, a) != ABBREVS_REV.get(b, b):
            diff_idx.append(i)
    if len(diff_idx) != 1:
        return False
    i = diff_idx[0]
    return lev1(db_t[i], wl_t[i])


def detect_encoding_fix(db: str, wl: str) -> bool:
    """True if DB contains an HTML/encoding-garbage sequence that the WL
    string cleans up. Catches '&198tna' (DB) -> 'Ætna' (WL)."""
    return bool(GARBAGE_RX.search(db) and not GARBAGE_RX.search(wl))


def detect_wl_garbage(db: str, wl: str) -> bool:
    return bool(GARBAGE_RX.search(wl) or "¤" in wl)


def detect_wl_adds_role(db: str, wl: str) -> bool:
    """True if WL inserts a comma-set role suffix that DB lacks (Atty.
    Gen., Sheriff, etc.). Verified by stripping ROLE_RX from WL and
    seeing if the residue is core-equivalent to DB."""
    stripped = ROLE_RX.sub("", normalize_westlaw_name(wl)).strip().rstrip(",.")
    if stripped == wl.strip():
        return False
    return is_pure_abbreviation(db, stripped) or _normalize_case_name(db) == _normalize_case_name(stripped)


def detect_wl_adds_locality(db: str, wl: str) -> bool:
    """True if WL appends 'of X' locality detail after the defendant
    that DB lacks, and the rest matches."""
    if " of " not in wl.lower():
        return False
    # Strip every 'of X' or 'of X, ST' phrase from WL; if the residue
    # matches DB (modulo abbreviation), it's a locality-add.
    stripped = wl
    for _ in range(5):
        m = re.search(r"\s+of\s+[A-Z][A-Za-z.&'-]+(?:\s+[A-Z][A-Za-z.&'-]+)*"
                      r"(?:,\s*[A-Z][A-Za-z.]+\.?)?", stripped)
        if not m:
            break
        stripped = stripped[:m.start()] + stripped[m.end():]
    return (
        is_pure_abbreviation_with_parties(db, stripped)
        or is_pure_abbreviation(db, stripped)
        or _normalize_case_name(db) == _normalize_case_name(stripped)
    )


def detect_wl_adds_parenthetical(db: str, wl: str) -> bool:
    """True if WL has '(Intervener)' / '(Garnishee)' / '(State, Intervenors)'
    parenthetical detail not in DB."""
    m = re.search(r"\s*\([^)]+\)", wl)
    if not m:
        return False
    stripped = (wl[:m.start()] + wl[m.end():]).strip()
    return (
        is_pure_abbreviation_with_parties(db, stripped)
        or is_pure_abbreviation(db, stripped)
        or _normalize_case_name(db) == _normalize_case_name(stripped)
    )


def detect_multicase(wl: str) -> bool:
    return bool(MULTICASE_RX.search(wl))


def detect_db_has_relator(db: str, wl: str) -> bool:
    return bool(EX_REL_RX.search(db) and not EX_REL_RX.search(wl))


_DOCKET_TRAIL_RX = re.compile(
    r"\.?\s*(?:Cr|Civ|Crim)\.?\s+\d*[A-Za-z]?\.?\s*\|?\s*$",
    re.IGNORECASE,
)
_TRAIL_ET_UX_RX = re.compile(r"\s+et\s+(?:ux|vir)\.?", re.IGNORECASE)
_AETNA_RX = re.compile(r"\bAetna\b", re.IGNORECASE)
_AETNA_BOUND_RX = re.compile(r"\bÆtna\b", re.IGNORECASE)


def strip_decorations(wl: str) -> str:
    """Strip Westlaw 'decorations' that are not party-information: trailing
    'Cr. 137' / 'Civ. No. 5118' docket markers, 'et ux.' / 'et vir.', and
    trailing pipe separators. Mirrors review_casenames.normalize_westlaw_name
    but a bit more aggressive on docket markers."""
    s = wl
    for _ in range(5):
        prev = s
        s = _DOCKET_TRAIL_RX.sub("", s).rstrip()
        s = _TRAIL_ET_UX_RX.sub("", s).rstrip()
        s = re.sub(r"\s*\|\s*$", "", s).rstrip()
        s = re.sub(r",\s*$", "", s).rstrip()
        if s == prev:
            break
    return s


def detect_county_swap(db: str, wl: str) -> bool:
    """True if WL has 'X County' where DB has 'County of X' (or vice
    versa), and the rest aligns."""
    def normalize_counties(s):
        s = re.sub(r"\bCounty\s+of\s+([A-Z][A-Za-z]+)", r"\1 County", s)
        s = re.sub(r"\bCity\s+of\s+([A-Z][A-Za-z]+)", r"\1 City", s)
        return s
    if normalize_counties(db) == normalize_counties(wl):
        return True
    return False


def detect_state_expansion(db: str, wl: str) -> bool:
    """True if WL expands a state name ('Michigan' -> 'State of Michigan')
    that DB has bare."""
    if "State of " in wl and "State of " not in db:
        stripped = wl.replace("State of ", "")
        return _normalize_case_name(stripped) == _normalize_case_name(db)
    return False


def detect_ae_encoding(db: str, wl: str) -> bool:
    """DB 'Aetna' / 'aetna' vs WL 'Ætna' or vice versa."""
    has_ae_db = bool(_AETNA_RX.search(db))
    has_lig_wl = bool(_AETNA_BOUND_RX.search(wl))
    if not (has_ae_db and has_lig_wl):
        return False
    db_eq = _normalize_case_name(_AETNA_RX.sub("Ætna", db))
    wl_eq = _normalize_case_name(wl)
    return db_eq == wl_eq


def classify(db: str, wl_norm: str, wl_titled: str) -> str:
    """Return the bucket label."""
    if detect_wl_garbage(db, wl_norm):
        return "DEFER_WL_GARBAGE"
    if detect_multicase(wl_norm):
        return "DEFER_MULTICASE"
    if detect_encoding_fix(db, wl_norm):
        return "ACCEPT_WL_ENCODING_FIX"
    if detect_ae_encoding(db, wl_norm):
        return "ACCEPT_WL_ENCODING_FIX"
    if detect_ocr_fix(db, wl_norm):
        return "ACCEPT_WL_OCR_FIX"
    if detect_db_has_relator(db, wl_norm):
        return "KEEP_DB_HAS_REL"
    if detect_county_swap(db, wl_norm):
        return "KEEP_DB_PURE_ABBREV"  # reordering only — keep DB
    if is_pure_abbreviation(db, wl_norm) or is_pure_abbreviation_with_parties(db, wl_norm):
        return "KEEP_DB_PURE_ABBREV"
    # Try after stripping Westlaw decorations (Cr. 137, et ux., etc.).
    wl_stripped = strip_decorations(wl_norm)
    if wl_stripped != wl_norm:
        if (is_pure_abbreviation(db, wl_stripped)
                or is_pure_abbreviation_with_parties(db, wl_stripped)
                or _normalize_case_name(db) == _normalize_case_name(wl_stripped)):
            return "KEEP_DB_PURE_ABBREV"
    if is_db_extra_only(db, wl_norm):
        return "KEEP_DB_HAS_REL"  # DB has strictly more — same action
    if detect_state_expansion(db, wl_norm):
        return "ACCEPT_WL_ADDS_DETAIL"
    if detect_wl_adds_role(db, wl_norm):
        return "ACCEPT_WL_ADDS_DETAIL"
    if detect_wl_adds_locality(db, wl_norm):
        return "ACCEPT_WL_ADDS_DETAIL"
    if detect_wl_adds_parenthetical(db, wl_norm):
        return "ACCEPT_WL_ADDS_DETAIL"
    # Token-set diff: figure out what tokens (in canonical form) WL has
    # that DB lacks (and vice versa). If WL adds only party-detail tokens
    # and DB adds nothing material, ACCEPT_WL.
    db_set = set(core_tokens(db))
    wl_set = set(core_tokens(wl_norm))
    wl_only = wl_set - db_set
    db_only = db_set - wl_set
    # Decoration tokens — adding these to WL doesn't add party-info.
    DECORATION = {"co", "cos", "corp", "inc", "ltd", "limited", "the", "of"}
    # Known party-detail tokens — locality/role/state-name-like.
    PARTY_DETAIL_HINT = {
        "county", "city", "state", "north", "south", "east", "west",
        "atty", "gen", "sheriff", "auditor", "treasurer", "mayor",
        "judge", "clerk", "commr", "commrs", "commissioner",
        "commissioners", "board", "office", "officer", "warden",
        "trustee", "marshal", "intervener", "intervenor", "garnishee",
        "appellant", "respondent", "plaintiff", "defendant", "court",
        "examiner", "receiver", "administrator", "executor",
        "secretary", "governor", "department", "township", "borough",
        "village", "minn", "ill", "wis", "iowa", "ia", "ny", "pa", "md",
        "mont", "neb", "sd", "nd", "ohio", "us", "usa", "ltd", "inc",
        "mortgagor", "mortgagee", "guardian", "estate",
    }
    if wl_only and not db_only - DECORATION:
        # WL strict superset (ignoring decoration). Are the additions
        # party-detail-like (or do they contain proper-noun-looking tokens)?
        non_decor_added = wl_only - DECORATION
        if non_decor_added:
            # Detail if at least one token is a known party-detail hint
            # OR a Title-Case proper noun (long word likely a place/name).
            has_hint = bool(non_decor_added & PARTY_DETAIL_HINT)
            has_proper_noun = any(
                len(t) >= 4 and t.isalpha() and t not in PARTY_DETAIL_HINT
                for t in non_decor_added
            )
            if has_hint or has_proper_noun:
                return "ACCEPT_WL_ADDS_DETAIL"
    # Same logic in reverse — DB adds tokens, WL doesn't.
    if db_only and not wl_only - DECORATION:
        return "KEEP_DB_HAS_REL"

    # Broader role-comma detection: if WL has "Defendant, Title Words" appositive
    # that DB lacks, and the rest matches, treat as ACCEPT_WL_ADDS_DETAIL.
    m = re.search(r",\s+[A-Z][a-zA-Z'.&\s-]{2,80}(?:\s+(?:Com'?rs?|Officer|"
                  r"Auditor|Treasurer|Sheriff|Mayor|Judge|Clerk|Director|"
                  r"Marshal|Commissioner|Trustee|Board|Court|County|District|"
                  r"Assessor|Superintendent|Examiner|Receiver|Warden|Atty\.?"
                  r"|Manager|Co-Partner|Partner|Members|Council|Comm'?r|"
                  r"State|Township|City|Office))(?:[.,]\s*|$)",
                  wl_norm)
    if m:
        # Strip the appositive and re-check
        cand = (wl_norm[:m.start()] + wl_norm[m.end():]).strip().rstrip(".,")
        if (is_pure_abbreviation(db, cand)
                or is_pure_abbreviation_with_parties(db, cand)
                or _normalize_case_name(db) == _normalize_case_name(cand)):
            return "ACCEPT_WL_ADDS_DETAIL"
    return "DEFER_AMBIG"


def main() -> int:
    rows = []
    with INPUT.open() as fh:
        rdr = csv.DictReader(fh, delimiter="\t")
        for r in rdr:
            verdict = classify(r["db_name"], r["wl_norm"], r["wl_titled"])
            r["verdict"] = verdict
            rows.append(r)

    cols = list(rows[0].keys())
    with OUTPUT.open("w") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, delimiter="\t", extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)

    print(f"Classified {len(rows)} rows -> {OUTPUT.relative_to(REPO)}")
    counts = Counter(r["verdict"] for r in rows)
    print("\nVerdict breakdown:")
    for k in sorted(counts):
        print(f"  {k:<24} {counts[k]:>5}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
