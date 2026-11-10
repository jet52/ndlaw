"""Pure helpers for the human-research tools.

Terms-and-connectors Boolean/proximity → FTS5 translation, statutory/rule authority
normalization, and salient-term extraction for related-opinion search. No DB
access; ``server.py`` holds the ``@mcp.tool()`` wrappers.
"""

import re

# --- Terms-and-connectors Boolean / proximity → FTS5 -------------------------------

# Approximation note (surfaced to callers): FTS5 has no sentence or paragraph
# unit, so /s and /p map to token-distance NEAR windows.
PROX_S = 20  # /s  same sentence  ≈ within 20 tokens
PROX_P = 50  # /p  same paragraph ≈ within 50 tokens

_BOOL_WORDS = {"AND", "OR", "NOT"}

_TOKEN_RE = re.compile(
    r"""
      "(?P<phrase>[^"]*)"        # "quoted phrase"
    | /(?P<prox>s|p|\d+)         # proximity: /s /p /N
    | (?P<amp>&)
    | (?P<pipe>\|)
    | (?P<pct>%)
    | (?P<word>[^\s&|%/"]+)      # a bare word
    """,
    re.X | re.I,
)


def _word_to_fts(w: str) -> str:
    """West reporter truncation ! → FTS5 prefix *; drop unsupported bare wildcards."""
    w = w.replace("!", "*")
    # FTS5 only supports a trailing prefix '*'; collapse any others and a lone '*'.
    w = re.sub(r"\*+", "*", w)
    if w == "*":
        return ""
    # A '*' only has meaning at the end in FTS5.
    if "*" in w and not w.endswith("*"):
        w = w.replace("*", "")
    return w


# --- Plain search text → a valid FTS5 MATCH expression ------------------------------

# FTS5 reads a bareword as letters, digits, '_' and non-ASCII only; anything
# else is syntax. So "self-represented" parsed as the column filter
# "-represented" (no such column) and "29-32.1-09" died at the '.' — about
# one search_opinions call in seven on 2026-10-28 failed that way.
_FTS_BAREWORD = re.compile(r"[0-9A-Za-z_\u0080-\U0010FFFF]+\*?")
_FTS_TOKEN = re.compile(r'"[^"]*"\*?|[^\s"]+')
_FTS_OPS = {"AND", "OR", "NOT"}


def fts_query(query: str) -> str:
    """Make plain search text a valid FTS5 MATCH expression while keeping the
    syntax the search tools advertise: uppercase AND / OR / NOT, "quoted
    phrases", parentheses, and a trailing * prefix.

    Any other term that is not an FTS5 bareword is quoted as a phrase, so
    'self-represented' → '"self-represented"' and a statute number
    '29-32.1-09' → '"29-32.1-09"' (the tokenizer splits it, the phrase keeps
    its parts adjacent). Operators FTS5 would reject — leading, trailing,
    doubled, or next to a parenthesis that cannot take them — are dropped, as
    are unbalanced quotes and parentheses. Returns '' for text with no terms.
    """
    raw: list[str] = []
    for t in _FTS_TOKEN.findall(query or ""):
        if t.startswith('"'):
            raw.append(t)
            continue
        # Grouping parens sit at a term's edges; a subdivision's are inside
        # it ('Rule 4(b)', '28-32-46(1)') and stay part of the term.
        lead = len(t) - len(t.lstrip("("))
        t = t[lead:]
        trail = 0
        while t.endswith(")") and t.count(")") > t.count("("):
            t, trail = t[:-1], trail + 1
        raw += ["("] * lead + ([t] if t else []) + [")"] * trail
    if raw.count("(") != raw.count(")"):
        raw = [t for t in raw if t not in "()"]
    toks: list[str] = []
    for t in raw:
        if t.startswith('"'):
            if t.strip('"*'):
                toks.append(t)
        elif t in ("(", ")") or t in _FTS_OPS or _FTS_BAREWORD.fullmatch(t):
            toks.append(t)
        else:
            star = t.endswith("*") and len(t) > 1
            body = t[:-1] if star else t
            toks.append('"' + body.replace('"', '""') + '"' + ("*" if star else ""))
    # Operators are binary in FTS5: each needs a term (or ')' ) before it and a
    # term (or '(') after it. Drop the ones that don't; repeat until stable.
    changed = True
    while changed:
        changed = False
        out: list[str] = []
        for i, t in enumerate(toks):
            if t in _FTS_OPS:
                prev = out[-1] if out else None
                nxt = toks[i + 1] if i + 1 < len(toks) else None
                if (prev is None or prev in _FTS_OPS or prev == "("
                        or nxt is None or nxt in _FTS_OPS or nxt == ")"):
                    changed = True
                    continue
            out.append(t)
        # an empty "( )" pair left behind
        while "(" in out:
            i = next((k for k in range(len(out) - 1)
                      if out[k] == "(" and out[k + 1] == ")"), None)
            if i is None:
                break
            del out[i:i + 2]
            changed = True
        toks = out
    return " ".join(toks)


def fts_query_quoted(query: str) -> str:
    """Last-resort form: every term quoted, operators and parentheses dropped
    (an implicit AND of literal terms). Always parses."""
    words = [w for w in re.findall(r'[^\s()"]+', query or "") if w not in _FTS_OPS]
    return " ".join('"' + w.replace('"', '""') + '"' for w in words)


def translate_boolean(query: str) -> tuple[str, list[str]]:
    """Translate a terms-and-connectors query to an FTS5 MATCH expression.

    Supported: ``&`` (AND), ``|`` / ``OR`` (OR), ``%`` / ``NOT`` (BUT NOT),
    ``/N`` (within N tokens → NEAR/N), ``/s`` (same sentence ≈ NEAR/20),
    ``/p`` (same paragraph ≈ NEAR/50), ``!`` truncation (→ prefix ``*``), and
    ``"quoted phrases"``. Returns ``(fts_query, notes)``.
    """
    notes: list[str] = []
    items: list[tuple[str, object]] = []  # (kind, value) ; prox value is int K
    for m in _TOKEN_RE.finditer(query):
        if m.group("phrase") is not None:
            items.append(("term", f'"{m.group("phrase").strip()}"'))
        elif m.group("prox") is not None:
            p = m.group("prox").lower()
            k = PROX_S if p == "s" else PROX_P if p == "p" else int(p)
            items.append(("prox", k))
        elif m.group("amp"):
            items.append(("op", "AND"))
        elif m.group("pipe"):
            items.append(("op", "OR"))
        elif m.group("pct"):
            items.append(("op", "NOT"))
        else:
            w = m.group("word")
            if w.upper() in _BOOL_WORDS:
                items.append(("op", w.upper()))
            else:
                fts = _word_to_fts(w)
                if fts:
                    items.append(("term", fts))

    has_prox = any(k == "prox" for k, _ in items)
    has_s = False
    has_p = False
    for k, v in items:
        if k == "prox" and v == PROX_S:
            has_s = True
        if k == "prox" and v == PROX_P:
            has_p = True

    out: list[str] = []
    i = 0
    while i < len(items):
        kind, val = items[i]
        if kind == "term":
            run_terms = [val]
            run_k: list[int] = []
            j = i + 1
            while (j + 1 < len(items) and items[j][0] == "prox"
                   and items[j + 1][0] == "term"):
                run_k.append(items[j][1])  # type: ignore[arg-type]
                run_terms.append(items[j + 1][1])
                j += 2
            if len(run_terms) > 1:
                out.append(f"NEAR({' '.join(run_terms)}, {max(run_k)})")
                i = j
            else:
                out.append(val)
                i += 1
        elif kind == "op":
            out.append(val)
            i += 1
        else:  # stray proximity op without two operands
            i += 1

    if has_s:
        notes.append(f"/s approximated as NEAR/{PROX_S} (no true sentence unit)")
    if has_p:
        notes.append(f"/p approximated as NEAR/{PROX_P} (no true paragraph unit)")
    return " ".join(out).strip(), notes


# --- statutory / court-rule authority normalization ------------------------

# Court-rule abbreviation aliases → canonical normalized prefix in the corpus.
# Keys are the input collapsed to lowercase with spaces and dots stripped (see
# ``low`` in normalize_authority), so both the compact dotted form
# ("N.D.R.Civ.P.") and the spaced form ("N.D. Sup. Ct. Admin. R.") of a rule
# set map to the one canonical citation prefix actually stored in rules.db.
_RULE_ALIASES = {
    # Core rule sets (stored compact-dotted).
    "ndrcivp": "N.D.R.Civ.P.", "ndrcrimp": "N.D.R.Crim.P.",
    "ndrev": "N.D.R.Ev.", "ndrappp": "N.D.R.App.P.",
    "ndrjuvp": "N.D.R.Juv.P.", "ndrct": "N.D.R.Ct.",
    "ndrctp": "N.D.R.Ct.",
    # ND Supreme Court rule sets (stored spaced). Longer keys are listed before
    # the shorter ones they contain so the most specific alias wins, but every
    # alias for a set maps to the same canonical prefix, so order is not
    # load-bearing for correctness.
    "ndsupctadminorder": "N.D. Sup. Ct. Admin. Order",
    "supctadminorder": "N.D. Sup. Ct. Admin. Order",
    "administrativeorder": "N.D. Sup. Ct. Admin. Order",
    "adminorder": "N.D. Sup. Ct. Admin. Order",
    "ndsupctadminr": "N.D. Sup. Ct. Admin. R.",
    "supctadminr": "N.D. Sup. Ct. Admin. R.",
    "administrativerule": "N.D. Sup. Ct. Admin. R.",
    "adminr": "N.D. Sup. Ct. Admin. R.",
    "admissiontopracticer": "Admission to Practice R.",
    "ndrprofconduct": "N.D.R. Prof. Conduct",
    "ndrlawyerdiscipl": "N.D.R. Lawyer Discipl.",
    "ndrlocalctpr": "N.D.R. Local Ct. Pr.",
    "ndrcontinuinglegaleduc": "N.D.R. Continuing Legal Educ.",
    "ndrprocr": "N.D.R. Proc. R.",
    "ndcodejudconduct": "N.D. Code Jud. Conduct",
    "ndstdsimposinglawyersanctions": "N.D. Stds. Imposing Lawyer Sanctions",
    "rjudconductcomm": "R. Jud. Conduct Comm.",
    "ltdpracticeoflawbylawstudentsr": "Ltd. Practice of Law by Law Students R.",
    # Federal rule sets (no corpus, but classify so we don't misread as statute).
    "frcivp": "Fed. R. Civ. P.", "frcrimp": "Fed. R. Crim. P.",
    "frevid": "Fed. R. Evid.", "frev": "Fed. R. Evid.",
    "frapp": "Fed. R. App. P.",
}

# Order alias probing by descending key length so a specific prefix
# ("ndsupctadminorder") is tried before a generic substring of it ("adminr").
_RULE_ALIAS_ORDER = sorted(_RULE_ALIASES, key=len, reverse=True)

# "AR 22" / "A.R. 22" — the bare shorthand for the Supreme Court Admin. Rules.
_AR_SHORTHAND_RE = re.compile(r"^\s*a\.?\s*r\.?\s+\d", re.I)

# A dash-numbered section/chapter id: a leading number then ONE OR MORE
# "-NN" segments. The unbounded tail is load-bearing for N.D. Admin. Code,
# whose cites are four segments deep (title-article-chapter-section, e.g.
# "10-01-01-01"); a fixed 3-segment cap silently truncated the 4th, so the
# parser's canonical form pointed at a non-existent provision. N.D.C.C. (≤3
# segments) is unaffected.
_SECTION_RE = re.compile(r"\b(\d+(?:\.\d+)?(?:-\d+(?:\.\d+)?)+)\b")
# A rule "number" may be an int (56), a decimal (2.1), multi-segment (8.3.1),
# hyphenated (22-1), or carry a trailing letter (5A). Anchored to the first
# digit-led token so a trailing pinpoint (", § 3(c)") is not absorbed.
_RULE_NUM_RE = re.compile(r"\b(\d+(?:[.-]\d+)*[A-Za-z]?)\b")


# --- case-citation extraction (for draft proofreading) ----------------------

# Only the reporter forms that resolve to in-corpus ND opinions — the only
# cites the citator can act on. Foreign cites can't be checked here anyway.
_CASE_CITE_RES = [
    re.compile(r"\b\d{4}\s+ND\s+\d+\b"),                       # neutral / synthetic
    re.compile(r"\b\d+\s+N\.\s?W\.\s?(?:2d|3d)?\s+\d+\b"),     # N.W. / N.W.2d / N.W.3d
    re.compile(r"\b\d+\s+N\.\s?D\.\s+\d+\b"),                  # official N.D. Reports
]


def normalize_cite_string(cite: str) -> str:
    """Collapse whitespace and edition spacing so a draft cite matches the DB
    form ('N.W. 2d' → 'N.W.2d', '2013  ND 169' → '2013 ND 169')."""
    c = re.sub(r"\s+", " ", cite.strip())
    # The older opinions space the reporter abbreviation ("4 N. D. 1",
    # "58 N. W. 454"); the DB form is unspaced. Found by the 2026-11-07
    # check_draft self-sweep: 3,186 distinct cites / 10,954 sites failed to
    # resolve for this alone.
    c = re.sub(r"\bN\.\s+(W|D)\.", r"N.\1.", c)
    return re.sub(r"(\.\s?[A-Z]\.)\s*(\d[a-z]+)", lambda m: m.group(0).replace(" ", ""), c)


def extract_case_cites(text: str) -> list[str]:
    """All distinct ND / N.W. / N.D. case-citation strings in ``text``,
    normalized to DB form, preserving first-seen order."""
    seen: dict[str, None] = {}
    for pat in _CASE_CITE_RES:
        for m in pat.finditer(text):
            seen.setdefault(normalize_cite_string(m.group(0)), None)
    return list(seen)


def normalize_authority(query: str) -> dict:
    """Parse a statute/rule reference into a match spec against text_citations.

    Returns ``{kind, token, exact}`` where ``kind`` is 'statute' | 'court_rule'
    | None, ``token`` is the section/rule number to match on a token boundary,
    and ``exact`` is a best-effort canonical normalized string (or None)."""
    q = query.strip()
    low = q.lower().replace(" ", "").replace(".", "")

    # Constitution? (e.g. "N.D. Const. art. I, § 8", "ND Const Art I Sec 8")
    if "const" in low and ("nd" in low or "northdakota" in low):
        return {"kind": "constitution", "token": None, "exact": q}

    # Administrative code? ("N.D.A.C. § 75-02-04.1-02", "N.D. Admin. Code ...",
    # "NDAC 75-02-04.1-02"). Canonical form is N.D.A.C. — matching jetcite's
    # normalized 'regulation' cites so opinions cross-link.
    if "admincode" in low or low.startswith("ndac") or "adminc" in low:
        m = _SECTION_RE.search(q)
        sec = m.group(1) if m else None
        # Three components is an admin-code CHAPTER (title-article-chapter);
        # four is a section. Reading '75-02-04.1' as a section would answer a
        # chapter question with "no such provision".
        if sec and sec.count("-") + 1 == 3:
            return {"kind": "admin", "token": sec,
                    "exact": f"N.D.A.C. ch. {sec}"}
        exact = f"N.D.A.C. § {sec}" if sec else None
        return {"kind": "admin", "token": sec, "exact": exact}

    # Court rule? Recognize via (a) a known rule-set alias — covering both the
    # compact dotted prefixes (N.D.R.Civ.P.) and the spaced ND Supreme Court
    # sets (N.D. Sup. Ct. Admin. R.); (b) the "AR 22" shorthand; (c) a bare
    # rule-set marker — the word "rule" or an "R." token, spaced or not.
    rule_prefix = None
    for alias in _RULE_ALIAS_ORDER:
        if alias in low:
            rule_prefix = _RULE_ALIASES[alias]
            break
    if rule_prefix is None and _AR_SHORTHAND_RE.match(q):
        rule_prefix = "N.D. Sup. Ct. Admin. R."
    if rule_prefix or re.search(r"\brule\b", q, re.I) or re.search(r"\.\s*R\.", q):
        m = _RULE_NUM_RE.search(q)
        token = m.group(1) if m else None
        exact = f"{rule_prefix} {token}" if rule_prefix and token else None
        return {"kind": "court_rule", "token": token, "exact": exact}

    # Bare dash-numbered cite with no corpus prefix — disambiguate by depth.
    # N.D. Admin. Code cites are four segments (title-article-chapter-section);
    # N.D.C.C. is at most three (chapter is two, section is three). So a
    # four-segment bare number can only be admin code, and a two-segment one is
    # an N.D.C.C. chapter.
    m = _SECTION_RE.search(q)
    if m:
        sec = m.group(1)
        groups = sec.split("-")
        if len(groups) >= 4:
            return {"kind": "admin", "token": sec, "exact": f"N.D.A.C. § {sec}"}
        if len(groups) == 2:  # title-chapter → chapter cite
            exact = f"N.D.C.C. ch. {sec}"
        else:
            exact = f"N.D.C.C. § {sec}"
        return {"kind": "statute", "token": sec, "exact": exact}

    return {"kind": None, "token": None, "exact": None}


def authority_token_matches(normalized: str, token: str) -> bool:
    """True if ``normalized`` cites exactly ``token`` (boundary-safe).

    Guards against '1-02-02' matching '11-02-02': the token must be the final
    whitespace-delimited unit of the normalized cite."""
    return normalized.split()[-1] == token if normalized else False


# --- salient terms (related-opinion keyword half) ---------------------------

_STOPWORDS = {
    # generic
    "the", "a", "an", "and", "or", "but", "not", "of", "to", "in", "on", "for",
    "with", "as", "by", "at", "from", "is", "was", "were", "are", "be", "been",
    "this", "that", "these", "those", "it", "its", "he", "she", "they", "we",
    "his", "her", "their", "our", "which", "who", "whom", "whose", "had", "has",
    "have", "will", "would", "shall", "may", "must", "can", "could", "did",
    "does", "do", "no", "if", "then", "than", "there", "here", "such", "any",
    "all", "also", "only", "more", "most", "other", "some", "into", "under",
    "upon", "when", "where", "while", "because", "however",
    # legal boilerplate
    "court", "courts", "opinion", "opinions", "district", "supreme", "appeal",
    "appeals", "appellant", "appellee", "plaintiff", "defendant", "justice",
    "judge", "case", "cases", "north", "dakota", "state", "county", "law",
    "section", "argues", "argued", "held", "holding", "affirmed", "reversed",
    "remanded", "order", "judgment", "motion", "filed", "trial", "matter",
    "facts", "evidence", "rule", "see", "also", "id", "para", "syllabus",
}

_WORD_RE = re.compile(r"[A-Za-z][A-Za-z'\-]{2,}")


def salient_terms(text: str, k: int = 12) -> list[str]:
    """Top content words of an opinion (frequency over a stopword filter)."""
    freq: dict[str, int] = {}
    for m in _WORD_RE.finditer(text):
        w = m.group(0).lower()
        if len(w) < 4 or w in _STOPWORDS:
            continue
        freq[w] = freq.get(w, 0) + 1
    ranked = sorted(freq, key=lambda w: (-freq[w], w))
    return ranked[:k]
