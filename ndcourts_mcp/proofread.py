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

# A footnote-body opener: a small integer alone on its own line. The reporter's
# footnote bodies are stored detached from their call site (at the page-bottom
# or opinion tail), so an offset inside one must not map to the body's
# preceding [¶] marker.
_STANDALONE_NUM = re.compile(r"(?m)^[ \t]*(\d{1,3})[ \t]*$")
# Structural boundary that ends a footnote body: the next paragraph marker or a
# reporter star-page marker.
_BODY_BOUNDARY = re.compile(r"\[¶\s*\d+\]|\[\*\d{2,4}\]")
# Reporter star-page marker, now stored in the bracketed ``[*458]`` form (= start
# of N.W.2d page 458), mirroring the ``[¶N]`` paragraph-marker convention. The
# brackets make the marker unambiguous: a bare ``*`` is emphasis (or a citation
# pincite into a cited source), never this opinion's pagination. See
# ``star_page_reformat`` for the one-time conversion + the ingest hook.
_STAR_PAGE = re.compile(r"\[\*(\d{2,4})\]")
# Volume + reporter prefix of a regional/official cite, for page pinpoints.
_REPORTER_CITE = re.compile(r"^\s*(\d+)\s+(N\.\s?W\.(?:\s?[23]d)?|N\.\s?D\.)\s+\d+")

# ndcourts-markdown footnote sections (distinct from the West/CL period form):
#   NOTES form:     "\nNOTES\n[1] body\n\n[2] body"   (calls survive inline as [N])
#   FOOTNOTES form: "\nFOOTNOTES\n\n1:\n\nbody"        (calls do not survive OCR)
_NOTES_HEADER = re.compile(r"\n[ \t]*NOTES[ \t]*\n")
_FOOTNOTES_HEADER = re.compile(r"\n[ \t]*FOOTNOTES[ \t]*\n")
_BRACKET_NOTE = re.compile(r"(?m)^[ \t]*\[(\d{1,3})\]")   # line-anchored [N] body opener
_BRACKET_CALL = re.compile(r"\[(\d{1,3})\]")              # inline [N] call (not [¶ N])
_COLON_NOTE = re.compile(r"(?m)^[ \t]*(\d{1,2}):[ \t]*$")  # "N:" body opener

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


def find_paragraph(text: str, char_offset: int,
                   markers: list[tuple[int, int]] | None = None) -> int | None:
    """Paragraph number containing ``char_offset`` (last marker at or before it)."""
    para = None
    for num, pos in (markers if markers is not None else paragraph_markers(text)):
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


# --- footnotes & star pages --------------------------------------------------

def footnote_structure(text: str) -> dict:
    """Map an opinion's footnotes: body spans and each footnote's call ¶.

    Footnote bodies are stored in the linear text detached from the ``[¶]``
    paragraph that carries the call marker. Storage format varies by source
    lineage; this dispatches across them, returning a uniform
    ``{"bodies": [(num, start, end), ...], "call_para": {num: ¶_or_None}}``
    (bodies sorted by position). ``call_para`` is ``None`` when the call marker
    did not survive (attached superscript, or a format that drops calls).

    Formats, in precedence order:

    * ``FOOTNOTES`` section (ndcourts markdown) — ``FOOTNOTES\\n\\n1:\\n\\nbody``;
      calls do not survive OCR, so ``call_para`` is ``None``.
    * ``NOTES`` section (ndcourts markdown) — ``NOTES\\n[1] body``; the call
      survives inline as ``[N]`` so the body links back to its call ¶.
    * West/CL-OCR period form ``\\n N\\n\\n. text`` + any standalone-number block
      after the final ``[¶]`` marker (the tail footnote cluster)."""
    bodies = _section_footnotes(text)
    if bodies is not None:
        return bodies
    return _standalone_footnotes(text)


def _section_footnotes(text: str) -> dict | None:
    """``FOOTNOTES``/``NOTES`` section footnotes (ndcourts markdown lineage), or
    ``None`` if neither section is present."""
    markers = paragraph_markers(text)
    # FOOTNOTES form: "N:" openers after a FOOTNOTES header; calls don't survive.
    fh = _FOOTNOTES_HEADER.search(text)
    if fh:
        opens = [(int(m.group(1)), fh.end() + m.start())
                 for m in _COLON_NOTE.finditer(text[fh.end():]) if int(m.group(1)) >= 1]
        if opens:
            return {"bodies": _spans(text, opens), "call_para": {}}
    # NOTES form: line-anchored "[N]" bodies after a NOTES header; the call is
    # the earliest inline "[N]" before the header.
    nh = _NOTES_HEADER.search(text)
    if nh:
        sec = text[nh.end():]
        opens = [(int(m.group(1)), nh.end() + m.start())
                 for m in _BRACKET_NOTE.finditer(sec)]
        if opens:
            call_para = {}
            for num, _ in opens:
                if num in call_para:
                    continue
                cm = next((m for m in _BRACKET_CALL.finditer(text, 0, nh.start())
                           if int(m.group(1)) == num), None)
                if cm is not None:
                    call_para[num] = find_paragraph(text, cm.start(), markers)
            return {"bodies": _spans(text, opens), "call_para": call_para}
    return None


def _spans(text: str, opens: list) -> list:
    """``[(num, start)]`` openers -> ``[(num, start, end)]``, each body running to
    the next opener or end-of-text."""
    opens = sorted(opens, key=lambda o: o[1])
    out = []
    for k, (num, start) in enumerate(opens):
        end = opens[k + 1][1] if k + 1 < len(opens) else len(text)
        out.append((num, start, end))
    return out


def _standalone_footnotes(text: str) -> dict:
    """West/CL-OCR period form + tail-after-last-``[¶]`` standalone bodies."""
    occ = []  # (num, line_start, after_line, is_period_form)
    for m in _STANDALONE_NUM.finditer(text):
        num = int(m.group(1))
        if 1 <= num <= 60:
            period = bool(re.match(r"\s*\.\s", text[m.end():m.end() + 12]))
            occ.append((num, m.start(), m.end(), period))
    if not occ:
        return {"bodies": [], "call_para": {}}

    markers = paragraph_markers(text)
    last_para = markers[-1][1] if markers else -1

    body_at = {}  # line_start -> num, for occurrences that open a footnote body
    for num, ls, after, period in occ:
        if period or (markers and ls > last_para):
            body_at[ls] = num

    body_lines = sorted(body_at)
    bodies = []
    for k, ls in enumerate(body_lines):
        after = next(a for n, l, a, p in occ if l == ls)
        end = body_lines[k + 1] if k + 1 < len(body_lines) else len(text)
        boundary = _BODY_BOUNDARY.search(text, after, end)
        if boundary:
            end = boundary.start()
            # Mid-text body (a page/paragraph marker follows): the West/CL
            # linearization resumes MAIN text after the note, separated by a
            # blank line (\n\n\n) — the marker alone over-extends the span by
            # everything up to the next page break. Bound at the resumption
            # when present (native pattern, e.g. id6409); bodies without the
            # sentinel keep the marker bound (RTF-verified normalization of
            # those is a data pass — see TODO-footnotes Phase 2d notes).
            resume = text.find("\n\n\n", after, end)
            if resume != -1:
                end = resume
        bodies.append((body_at[ls], ls, end))

    body_nums = {n for n, _, _ in bodies}
    body_start = {n: ls for n, ls, _ in bodies}
    call_para = {}
    for num, ls, after, period in occ:
        if ls in body_at:
            continue
        if num in body_nums and num not in call_para:
            call_para[num] = find_paragraph(text, ls, markers)
    # Fallback: an inline ``[N]`` call (ndcourts modern lineage) for a confirmed
    # footnote whose call did not survive as a bare-line marker. Gated against
    # bracketed quote-alterations (``[t]he``, a quoted ``[1]``): ``N`` must be a
    # confirmed body, ``[N]`` must be unique in the opinion, and precede the body.
    for num in body_nums - call_para.keys():
        hits = [m for m in _BRACKET_CALL.finditer(text) if int(m.group(1)) == num]
        if len(hits) == 1 and hits[0].start() < body_start[num]:
            call_para[num] = find_paragraph(text, hits[0].start(), markers)
    return {"bodies": bodies, "call_para": call_para}


def star_page_before(text: str, offset: int) -> int | None:
    """Reporter page number for ``offset`` — the last ``*NNN`` star-page marker
    at or before it. ``None`` when the opinion carries no star pages."""
    page = None
    for m in _STAR_PAGE.finditer(text):
        if m.start() <= offset:
            page = int(m.group(1))
        else:
            break
    return page


def locate_structure(text: str, offset: int, struct: dict | None = None) -> dict:
    """Resolve ``offset`` to its structural pinpoint fields.

    Returns ``{"paragraph", "footnote", "in_footnote", "reporter_page"}``. When
    the offset lands inside a footnote body, ``paragraph`` is the footnote's
    *call* paragraph (not the body's preceding marker) and ``footnote`` is its
    number; ``paragraph`` may be ``None`` if the call site is unrecoverable."""
    struct = struct if struct is not None else footnote_structure(text)
    for num, start, end in struct["bodies"]:
        if start <= offset < end:
            return {"paragraph": struct["call_para"].get(num), "footnote": num,
                    "in_footnote": True,
                    "reporter_page": star_page_before(text, offset)}
    return {"paragraph": find_paragraph(text, offset), "footnote": None,
            "in_footnote": False, "reporter_page": star_page_before(text, offset)}


def pinpoint_suffix(located: dict) -> str | None:
    """Bluebook pinpoint tail for a located quote: ``¶ 7 n.1``, ``¶ 18``,
    ``n.1``, or ``None`` when neither paragraph nor footnote is known."""
    para, fn = located.get("paragraph"), located.get("footnote")
    if para is not None and fn is not None:
        return f"¶ {para} n.{fn}"
    if fn is not None:
        return f"n.{fn}"
    if para is not None:
        return f"¶ {para}"
    return None


def reporter_pinpoint(cite_rows: list[dict], page: int | None) -> str | None:
    """``604 N.W.2d at 458`` from an opinion's parallel cites and a star page.
    Prefers the regional N.W. reporter; ``None`` if no page or no page cite."""
    if page is None:
        return None
    for r in cite_rows:
        m = _REPORTER_CITE.match(r.get("citation", ""))
        if m:
            return f"{m.group(1)} {m.group(2)} at {page}"
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

    struct = footnote_structure(text)
    pattern = _build_quote_regex(quote)

    m = re.search(pattern, text)
    if m:
        return _hit(text, m, True, struct)

    m = re.search(pattern, text, re.IGNORECASE)
    if m:
        res = _hit(text, m, False, struct)
        res["case_mismatch"] = True
        res["note"] = "Matches except for capitalization."
        return res

    return _fuzzy(text, quote, struct)


def _hit(text: str, m: re.Match, verbatim: bool, struct: dict) -> dict:
    start = m.start()
    res = {
        "found": True,
        "verbatim": verbatim,
        "char_start": start,
        "char_end": m.end(),
        "matched_text": m.group(0),
    }
    res.update(locate_structure(text, start, struct))
    return res


def _fuzzy(text: str, quote: str, struct: dict | None = None) -> dict:
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
    res = {
        "found": False,
        "verbatim": False,
        "similarity": round(ratio, 3),
        "closest_text": closest,
        "differences": diff,
        "note": "Not found verbatim; closest passage shown with word-level diff "
                "(- quote, + opinion).",
    }
    res.update(locate_structure(text, char_start, struct))
    # Tier 3: a very high word-similarity miss whose only divergence is an
    # intra-word character substitution (or soft-hyphen line break) is almost
    # certainly an OCR artifact in the stored text, not a misquote. Flag it so
    # reviewers verify against the reporter instead of "correcting" a correct
    # quotation. Compares the two sides char-by-char modulo typography/spacing.
    if ratio >= 0.97 and _ocr_artifact_only(quote, closest):
        res["likely_ocr_artifact"] = True
        res["note"] += (" The sole difference is an intra-word substitution "
                        "consistent with an OCR artifact in the stored text; "
                        "verify against the reporter before treating as a misquote.")
    return res


def _ocr_artifact_only(quote: str, closest: str) -> bool:
    """True when ``quote`` and ``closest`` differ only by a tiny char-level edit
    (an OCR substitution like ti↔cl or a soft-hyphen break), not a real word
    change. Normalizes typography, hyphenation, and whitespace first."""
    def norm(s):
        s = "".join(_norm_words(s))            # strip whitespace, fold quotes/dashes
        return s.replace("-", "").lower()      # drop hyphens (soft line breaks)
    a, b = norm(quote), norm(closest)
    if not a or not b:
        return False
    r = difflib.SequenceMatcher(None, a, b).ratio()
    return r >= 0.94
