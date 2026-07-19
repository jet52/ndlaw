"""Pure helpers for the jetmemo authority-research tools.

Disposition/syllabus extraction, citing-sentence location, and the
conservative treatment-signal classifier. No DB access here; ``server.py``
holds the ``@mcp.tool()`` wrappers that aggregate over the citation graph.

Treatment classification is deliberately conservative and NON-authoritative:
it scans only the citing sentence, never emits an overall "still good law"
verdict, and the wrapper always returns the underlying sentence for human
verification. A misclassified negative treatment is worse than none.
"""

import re

from .proofread import find_paragraph

# --- disposition (modern opinions) ------------------------------------------

_DISPOSITION_WORDS = (
    "AFFIRMED", "REVERSED", "REMANDED", "VACATED", "DISMISSED", "MODIFIED",
    "REINSTATED", "GRANTED", "DENIED",
)


def extract_disposition(text: str) -> str | None:
    """Return the disposition line from a modern opinion's header, or None.

    Modern ND opinions print the disposition as a standalone all-caps line
    (e.g. ``REVERSED AND REMANDED.``) between the "Appeal from..." line and the
    "Opinion of the Court by..." byline. Derived/heuristic — callers should
    label it as such."""
    # Header is everything before the first paragraph marker (¶1); fall back to
    # a generous prefix when the opinion carries no markers.
    head_end = text.find("[¶")
    head = text[: head_end if head_end != -1 else 4000]
    for raw in head.splitlines():
        line = raw.strip()
        if not (8 <= len(line) <= 80):
            continue
        core = line.rstrip(".")
        # All-caps line (letters/spaces/punctuation only) naming a disposition.
        if core != core.upper():
            continue
        if not any(w in core for w in _DISPOSITION_WORDS):
            continue
        if re.fullmatch(r"[A-Z0-9 ,;.'\-/]+", core):
            return core
    return None


# --- syllabus (pre-1953 opinions) -------------------------------------------

_SYLLABUS_END = re.compile(
    r"\n(?:Attorneys and Law Firms|OPINION\b|West Headnotes)", re.IGNORECASE
)


def extract_syllabus(text: str) -> list[str] | None:
    """Return the court's syllabus points (pre-1953), or None if absent.

    Pre-1953 ND opinions publish a "Syllabus by the Court" — numbered holdings
    separated by non-breaking-space-only lines — before the opinion body."""
    m = re.search(r"Syllabus by the Court\.?", text)
    if not m:
        return None
    block = text[m.end():]
    end = _SYLLABUS_END.search(block)
    if end:
        block = block[: end.start()]
    block = block[:4000]
    # Points are separated by blank/nbsp-only lines.
    raw_points = re.split(r"\n[\s ]*\n", block)
    points = []
    for p in raw_points:
        cleaned = re.sub(r"[\s ]+", " ", p).strip()
        # Drop stray leading page markers ("*942" or bracketed "[*942]") and empties.
        cleaned = re.sub(r"^\[?\*\d+\]?\s*", "", cleaned)
        if len(cleaned) > 20:
            points.append(cleaned)
    return points or None


# --- citing sentence (citator) ----------------------------------------------

def citing_context(text: str, cite_str: str, before: int = 260, after: int = 220) -> dict:
    """Locate ``cite_str`` in a citing opinion and return surrounding context + ¶.

    Returns ``{found, paragraph, context}``. The context is a window around the
    cite, NOT trimmed on ". " — legal abbreviations ("v.", "N.W.", initials)
    create false sentence breaks, and a treatment verb usually sits *before*
    the case name ("We overrule X v. Y, <cite>"), so naive trimming would drop
    the very signal we need. The window is bounded by paragraph markers so it
    never bleeds across ¶s, and is always returned for human verification."""
    idx = text.find(cite_str)
    end = idx + len(cite_str)
    if idx < 0:
        pat = re.sub(r"\s+", r"\\s+", re.escape(cite_str))
        m = re.search(pat, text)
        if not m:
            return {"found": False}
        idx, end = m.start(), m.end()

    start = max(0, idx - before)
    # Don't cross a paragraph boundary on the left: start after the nearest
    # preceding [¶N] marker if one falls inside the window.
    pm = text.rfind("[¶", start, idx)
    if pm != -1:
        close = text.find("]", pm)
        start = close + 1 if 0 <= close < idx else pm
    stop = min(len(text), end + after)
    # Stop before the next paragraph marker so context stays within this ¶.
    nm = text.find("[¶", end, stop)
    if nm != -1:
        stop = nm

    context = re.sub(r"\s+", " ", text[start:stop]).strip()
    return {"found": True, "paragraph": find_paragraph(text, idx), "context": context}


# --- treatment signal (conservative) ----------------------------------------

NEGATIVE = "possible negative — verify"
DISTINGUISHED = "distinguished — verify"
POSITIVE = "possible positive"
NEUTRAL = "neutral"

# Order for surfacing: negatives must never be truncated away below positives.
SIGNAL_ORDER = {NEGATIVE: 0, DISTINGUISHED: 1, POSITIVE: 2, NEUTRAL: 3}

_NEG_TERMS = (
    "overrul", "abrogat", "supersed", "disapprov", "repudiat",
    "receded from", "recede from", "declined to follow", "decline to follow",
    "no longer good law", "called into question", "we reject", "is not good law",
)
_DIST_TERMS = ("distinguish",)
_POS_TERMS = (
    "we follow", "reaffirm", "we adhere", "adhered to", "we agree with",
)


def classify_treatment(sentence: str) -> str:
    """Conservative, sentence-local treatment signal. Negative dominates.

    NOT authoritative — the citing sentence may use a treatment word about a
    different case, or quote another court. Always read the sentence."""
    low = sentence.lower()
    if any(t in low for t in _NEG_TERMS):
        return NEGATIVE
    if any(t in low for t in _DIST_TERMS):
        return DISTINGUISHED
    if any(t in low for t in _POS_TERMS):
        return POSITIVE
    return NEUTRAL
