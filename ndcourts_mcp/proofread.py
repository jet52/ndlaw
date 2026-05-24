"""Pure helpers for the jetredline proofreading tools.

Citation ordering/formatting, verbatim quotation matching, and paragraph
pinpoint resolution over an opinion's ``text_content``. No DB access and no
MCP wiring live here so the logic stays unit-testable; ``server.py`` holds the
thin ``@mcp.tool()`` wrappers that call these.
"""

import difflib
import re

# Redbook/Bluebook display order for ND parallel cites: medium-neutral first,
# then the official North Dakota Reports, then the regional N.W. series newest
# to oldest, then secondary, then foreign. Synthetic (`ND-neutral-synthetic`)
# back-assigned cites are handled separately — never folded into a formatted
# citation, only surfaced bracketed.
REDBOOK_RANK = {
    "ND-neutral": 0,
    "ND": 1,
    "NW3d": 2,
    "NW2d": 3,
    "NW": 4,
    "ALR": 5,
    "LRA": 6,
    "US": 7,
    "SCT": 8,
    "LED": 9,
}

# Reporters that may appear in a formatted precedential citation string.
PRECEDENTIAL = {"ND-neutral", "ND", "NW3d", "NW2d", "NW"}

SYNTHETIC_REPORTER = "ND-neutral-synthetic"

_PARA_RE = re.compile(r"\[¶\s*(\d+)\]")

# Citation-string shapes used to pull a cite out of a free-text query.
_CITE_PATTERNS = [
    re.compile(r"\d{4}\s+ND\s+\d+"),                 # neutral / synthetic
    re.compile(r"\d+\s+N\.\s?W\.\s?(?:2d|3d)?\s+\d+"),  # regional N.W.(2d/3d)
    re.compile(r"\d+\s+N\.\s?D\.\s+\d+"),             # official N.D. Reports
]

# Quote/dash variants treated as equivalent for "verbatim modulo typography".
_QUOTE_CLASSES = {
    "'": "['‘’ʼ]",
    "‘": "['‘’ʼ]",
    "’": "['‘’ʼ]",
    "ʼ": "['‘’ʼ]",
    '"': '["“”]',
    "“": '["“”]',
    "”": '["“”]',
    "-": "[-‐‑‒–—]",
    "‐": "[-‐‑‒–—]",
    "‑": "[-‐‑‒–—]",
    "‒": "[-‐‑‒–—]",
    "–": "[-‐‑‒–—]",
    "—": "[-‐‑‒–—]",
}


# --- citations ---------------------------------------------------------------

def extract_cite(query: str) -> str | None:
    """Return the first citation-shaped substring in ``query`` (whitespace
    normalized), or None if the query carries no recognizable cite."""
    for pat in _CITE_PATTERNS:
        m = pat.search(query)
        if m:
            return re.sub(r"\s+", " ", m.group(0)).strip()
    return None


def order_citations(rows: list[dict]) -> tuple[list[dict], list[str]]:
    """Split and order an opinion's citation rows.

    ``rows`` are dicts with ``citation``/``reporter``/``is_primary``. Returns
    ``(ordered, synthetic)`` where ``ordered`` is the precedential+secondary
    set in Redbook order and ``synthetic`` is the bracketed list of
    back-assigned ``[YYYY ND nnn]`` cites (never mixed into ``ordered``)."""
    ordered = []
    synthetic = []
    for r in rows:
        rep = r["reporter"]
        if rep == SYNTHETIC_REPORTER:
            synthetic.append(f"[{r['citation']}]")
        else:
            ordered.append(r)
    ordered.sort(key=lambda r: (REDBOOK_RANK.get(r["reporter"], 99), r["citation"]))
    return ordered, synthetic


def format_redbook(case_name: str, ordered: list[dict], date_filed: str | None) -> str:
    """Build a suggested Redbook-style citation string from ordered cites.

    Uses only precedential reporters. When a medium-neutral cite is present the
    year is embedded in it (no parenthetical); otherwise the filing year is
    appended in parentheses per pre-1997 convention."""
    cites = [r["citation"] for r in ordered if r["reporter"] in PRECEDENTIAL]
    if not cites:
        return case_name
    has_neutral = any(r["reporter"] == "ND-neutral" for r in ordered)
    body = ", ".join(cites)
    if has_neutral:
        return f"{case_name}, {body}"
    year = (date_filed or "")[:4]
    return f"{case_name}, {body} ({year})" if year else f"{case_name}, {body}"


def primary_cite(rows: list[dict]) -> str | None:
    """Return the official (is_primary) citation string, if any."""
    for r in rows:
        if r["is_primary"]:
            return r["citation"]
    return None


def names_match(a: str, b: str) -> bool:
    """Loose case-name equality: case-insensitive, whitespace-collapsed,
    trailing punctuation stripped."""
    return _norm_name(a) == _norm_name(b)


def name_similarity(a: str, b: str) -> float:
    return round(difflib.SequenceMatcher(None, _norm_name(a), _norm_name(b)).ratio(), 3)


def _norm_name(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower()).rstrip(".,")


# --- paragraphs --------------------------------------------------------------

def paragraph_markers(text: str) -> list[tuple[int, int]]:
    """Return [(paragraph_number, char_offset), ...] for every ``[¶N]`` marker."""
    return [(int(m.group(1)), m.start()) for m in _PARA_RE.finditer(text)]


def find_paragraph(text: str, char_offset: int) -> int | None:
    """Paragraph number containing ``char_offset`` (last marker at or before it)."""
    para = None
    for num, pos in paragraph_markers(text):
        if pos <= char_offset:
            para = num
        else:
            break
    return para


def extract_paragraph(text: str, n: int, cap: int = 6000) -> tuple[str, bool] | None:
    """Return ``(paragraph_text, truncated)`` for ``[¶n]`` .. next marker.

    None if the marker is absent. Text runs to the next ``[¶`` marker or
    end-of-text, capped at ``cap`` chars."""
    markers = paragraph_markers(text)
    for i, (num, pos) in enumerate(markers):
        if num == n:
            end = markers[i + 1][1] if i + 1 < len(markers) else len(text)
            chunk = text[pos:end].strip()
            if len(chunk) > cap:
                return chunk[:cap], True
            return chunk, False
    return None


# --- quotations --------------------------------------------------------------

def _build_quote_regex(needle: str) -> str:
    """Whitespace-flexible, quote/dash-tolerant, case-SENSITIVE pattern for a
    quoted passage. Word changes/omissions still break the match; only
    typographic differences are absorbed."""
    parts = []
    prev_ws = False
    for ch in needle.strip():
        if ch.isspace():
            if not prev_ws:
                parts.append(r"\s+")
            prev_ws = True
            continue
        prev_ws = False
        parts.append(_QUOTE_CLASSES.get(ch, re.escape(ch)))
    return "".join(parts)


def _norm_words(s: str) -> list[str]:
    s = s.translate(str.maketrans({
        "‘": "'", "’": "'", "ʼ": "'",
        "“": '"', "”": '"',
        "‐": "-", "‑": "-", "‒": "-", "–": "-", "—": "-",
    }))
    return s.split()


def locate_quote(text: str, quote: str) -> dict:
    """Locate ``quote`` within ``text``.

    Returns a dict with at least ``found`` and ``verbatim``. When matched
    (verbatim modulo typography) it carries ``char_start``/``char_end``,
    ``paragraph``, and ``matched_text``. When only a near match exists it
    carries ``closest_text``, ``paragraph``, ``similarity``, and a word-level
    ``differences`` diff. ``case_mismatch`` flags a match that differs only in
    capitalization."""
    quote = quote.strip()
    if not quote:
        return {"found": False, "verbatim": False, "error": "empty quote"}

    pattern = _build_quote_regex(quote)

    m = re.search(pattern, text)
    if m:
        return _hit(text, m, verbatim=True)

    m = re.search(pattern, text, re.IGNORECASE)
    if m:
        res = _hit(text, m, verbatim=False)
        res["case_mismatch"] = True
        res["note"] = "Matches except for capitalization."
        return res

    return _fuzzy(text, quote)


def _hit(text: str, m: re.Match, verbatim: bool) -> dict:
    start = m.start()
    return {
        "found": True,
        "verbatim": verbatim,
        "char_start": start,
        "char_end": m.end(),
        "paragraph": find_paragraph(text, start),
        "matched_text": m.group(0),
    }


def _fuzzy(text: str, quote: str) -> dict:
    """Word-level near-match search anchored on the quote's most distinctive
    words, so a dropped/changed word surfaces with the actual text + ¶."""
    words = [(mt.group(0), mt.start(), mt.end()) for mt in re.finditer(r"\S+", text)]
    if not words:
        return {"found": False, "verbatim": False, "similarity": 0.0,
                "note": "Opinion has no text to match against."}

    qwords = _norm_words(quote)
    n = len(qwords)
    if n == 0:
        return {"found": False, "verbatim": False, "error": "empty quote"}

    norm_text_words = [_norm_words(w)[0] if _norm_words(w) else w.lower()
                       for w, _, _ in words]
    norm_lower = [w.lower() for w in norm_text_words]

    # Anchor positions: indices in the text whose word equals the quote's
    # rarest/longest word, plus the quote's first word. Keeps the scan cheap.
    anchor_qi = max(range(n), key=lambda i: len(qwords[i])) if n else 0
    anchor_word = qwords[anchor_qi].lower()
    candidates = {i - anchor_qi for i, w in enumerate(norm_lower) if w == anchor_word}
    first_word = qwords[0].lower()
    candidates |= {i for i, w in enumerate(norm_lower) if w == first_word}
    candidates = {c for c in candidates if 0 <= c <= len(words) - 1}

    best = None  # (ratio, start_idx, end_idx)
    qjoined = " ".join(w.lower() for w in qwords)
    for start in candidates:
        end = min(start + n, len(words))
        window = " ".join(norm_lower[start:end])
        ratio = difflib.SequenceMatcher(None, qjoined, window).ratio()
        if best is None or ratio > best[0]:
            best = (ratio, start, end)

    if best is None:
        return {"found": False, "verbatim": False, "similarity": 0.0,
                "note": "No anchor word from the quote appears in the opinion."}

    ratio, start, end = best
    char_start = words[start][1]
    char_end = words[end - 1][2]
    closest = text[char_start:char_end]
    diff = [d for d in difflib.ndiff(qwords, [w for w, _, _ in words[start:end]])
            if d[0] in "+-"]
    return {
        "found": False,
        "verbatim": False,
        "similarity": round(ratio, 3),
        "paragraph": find_paragraph(text, char_start),
        "closest_text": closest,
        "differences": diff,
        "note": "Not found verbatim; closest passage shown with word-level diff "
                "(- quote, + opinion).",
    }
