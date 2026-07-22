"""Pure helpers for the Notes of Decisions tool (``get_notes_of_decisions``).

Occurrence-level scanning of citing opinions for a primary-law authority:
every in-text mention (not just the first recorded citation), the subsection
pinpoint each mention carries, and the conservative per-opinion signals
(mentions / quotes_provision / construes). No DB access; ``server.py`` holds
the ``@mcp.tool()`` wrapper that aggregates over the citation graph.

Doctrine (mirrors ``memo.py``): signals are heuristic and NON-authoritative —
the wrapper always returns the underlying verbatim context window for human
verification, and the ``construes`` flag never claims more than "interpretive
vocabulary appears near this mention".

Rule-set disambiguation: a bare in-text "Rule 12" is ambiguous when an opinion
cites the same number across rule sets (N.D.R.Civ.P. 12 vs N.D.R.Crim.P. 12).
Attribution ladder, most reliable first: (1) an explicit rule-set marker
immediately trailing the number ("Rule 60(b), N.D.R.Civ.P."); (2) the nearest
preceding rule-set marker anywhere earlier in the opinion; (3) if the opinion's
extracted citations show it cites this number in exactly ONE rule set, that
set; (4) otherwise the mention is dropped from the occurrence list (the
opinion itself still appears via its recorded citation).
"""

from __future__ import annotations

import re

from .corpus import normalize_pincite
from .memo import context_window
from .proofread import find_paragraph

# --- occurrence scanning -----------------------------------------------------

# Boundaries for a dash-numbered NDCC/NDAC section token: not embedded in a
# longer number ("114-09-…", "14-09-06.21", "14-09-06.2-01") and, for a
# 2-segment chapter token, not the prefix of a full section cite ("28-32-01").
def section_token_re(section: str) -> re.Pattern:
    return re.compile(
        r"(?<![\d.\-])" + re.escape(section) + r"(?![\d\-])(?!\.\d)"
    )


_CONST_MODERN_RE = re.compile(
    r"^N\.D\. Const\. art\. ([IVXLCDM]+), § (\d+(?:\.\d+)?)$"
)
_CONST_HISTORICAL_RE = re.compile(r"^N\.D\. Const\. § (\d+(?:\.\d+)?)$")


def const_target(normalized: str) -> dict | None:
    """Parse a canonical constitution cite into an occurrence-scan target.

    Modern → {article, section}; original 1889 numbering → {article: None,
    section}. Other forms (amend. art., Schedule…) → None (caller falls back
    to the recorded-citation context)."""
    m = _CONST_MODERN_RE.match(normalized)
    if m:
        return {"article": m.group(1), "section": m.group(2)}
    m = _CONST_HISTORICAL_RE.match(normalized)
    if m:
        return {"article": None, "section": m.group(1)}
    return None


def const_occurrences(text: str, article: str | None, section: str) -> list[tuple[int, int]]:
    """Spans of in-text references to a constitutional provision.

    A section-number mention counts only with corroboration in a window around
    it: the article numeral (modern cites) or a Constitution mention
    (original-numbering cites). Bare "§ 8" with no anchor nearby is ignored —
    precision over recall."""
    sec_re = re.compile(
        r"(?:§§?|[Ss]ections?)\s*" + re.escape(section) + r"(?!\d)(?!\.\d)"
    )
    if article:
        anchor = re.compile(
            r"[Aa]rt(?:icle)?\.?\s+" + article + r"(?![IVXLCDM])")
    else:
        anchor = re.compile(r"[Cc]onst(?:itution|\.)?")
    spans = []
    for m in sec_re.finditer(text):
        lo = max(0, m.start() - 120)
        hi = min(len(text), m.end() + 80)
        if anchor.search(text, lo, hi):
            spans.append((m.start(), m.end()))
    return spans


# --- rule-set markers and disambiguation -------------------------------------

def _flex_prefix_pattern(prefix: str) -> str:
    """A regex for a rule-set prefix tolerant of spacing variants.

    'N.D.R.Civ.P.' matches 'N.D.R.Civ.P.', 'N. D. R. Civ. P.'; the spaced
    canonicals ('N.D. Sup. Ct. Admin. R.') also match their compact forms."""
    out = []
    for ch in prefix:
        if ch == ".":
            out.append(r"\.\s*")
        elif ch == " ":
            out.append(r"\s*")
        else:
            out.append(re.escape(ch))
    return "".join(out)


# Spelled-out names for the commonly narrated rule sets (the compact-dotted
# marker for every set is generated from its canonical prefix). Federal sets
# are included so a bare "Rule 12" following a federal-rules discussion is not
# attributed to the ND set.
_SPELLED_MARKERS = {
    "N.D.R.Civ.P.": [r"North Dakota Rules of Civil Procedure",
                     r"Rules of Civil Procedure"],
    "N.D.R.Crim.P.": [r"Rules of Criminal Procedure"],
    "N.D.R.Ev.": [r"Rules of Evidence"],
    "N.D.R.App.P.": [r"Rules of Appellate Procedure"],
    "N.D.R.Ct.": [r"Rules of Court"],
    "N.D.R.Juv.P.": [r"Rules of Juvenile Procedure"],
    "N.D. Sup. Ct. Admin. R.": [r"Administrative Rule"],
    "N.D. Sup. Ct. Admin. Order": [r"Administrative Order"],
    "N.D.R. Prof. Conduct": [r"Rules of Professional Conduct"],
    "N.D. Code Jud. Conduct": [r"Code of Judicial Conduct"],
    "Fed. R. Civ. P.": [r"Federal Rules of Civil Procedure"],
    "Fed. R. Crim. P.": [r"Federal Rules of Criminal Procedure"],
    "Fed. R. Evid.": [r"Federal Rules of Evidence"],
    "Fed. R. App. P.": [r"Federal Rules of Appellate Procedure"],
}

_CORE_RULE_SETS = (
    "N.D.R.Civ.P.", "N.D.R.Crim.P.", "N.D.R.Ev.", "N.D.R.App.P.",
    "N.D.R.Ct.", "N.D.R.Juv.P.", "N.D. Sup. Ct. Admin. R.",
    "N.D. Sup. Ct. Admin. Order", "N.D.R. Prof. Conduct",
    "N.D. Code Jud. Conduct", "Fed. R. Civ. P.", "Fed. R. Crim. P.",
    "Fed. R. Evid.", "Fed. R. App. P.",
)

_MARKER_PATTERNS: list[tuple[str, re.Pattern]] = [
    (canon, re.compile(pat))
    for canon in _CORE_RULE_SETS
    for pat in [_flex_prefix_pattern(canon)] + _SPELLED_MARKERS.get(canon, [])
]


def rule_set_markers(text: str) -> list[tuple[int, int, str]]:
    """Every rule-set mention in ``text`` as (start, end, canonical_prefix),
    sorted by position. A marker fully contained in a longer one is dropped
    ('Rules of Civil Procedure' inside 'Federal Rules of Civil Procedure')."""
    hits: list[tuple[int, int, str]] = []
    for canon, pat in _MARKER_PATTERNS:
        for m in pat.finditer(text):
            hits.append((m.start(), m.end(), canon))
    hits.sort(key=lambda h: (h[0], -(h[1] - h[0])))
    kept: list[tuple[int, int, str]] = []
    for s, e, c in hits:
        if kept and s >= kept[-1][0] and e <= kept[-1][1]:
            continue  # contained in the previous (longer) marker
        kept.append((s, e, c))
    return kept


_RULE_NUM_BOUNDARY = r"(?!\d)(?!\.\d)(?![A-Za-z])"

# What may sit between "Rule 60(b)" and a trailing set marker: an optional
# parenthetical pinpoint, commas/space, an optional "of the". Anything more
# ("Rule 12 and N.D.R.Ev. 403") rejects the trailing attribution.
_TRAILING_GAP_RE = re.compile(
    r"[\s,]*(?:\([^)]{1,20}\))?[\s,]*(?:of\s+the\s+)?$"
)


def rule_occurrences(
    text: str, prefix: str, number: str, sole_set: str | None = None,
) -> list[tuple[int, int]]:
    """Spans of in-text references to rule ``number`` of rule set ``prefix``.

    Explicit-prefix mentions ("N.D.R.Civ.P. 56") match directly; bare
    "Rule 56" mentions are attributed via the ladder in the module docstring.
    ``sole_set``: the one rule set the citing opinion is recorded as citing
    this number under, or None when recorded citations show several sets (or
    none) — the last-resort attribution."""
    num = re.escape(number) + _RULE_NUM_BOUNDARY
    spans: list[tuple[int, int]] = []

    explicit = re.compile(_flex_prefix_pattern(prefix) + r"\s*" + num)
    spans.extend((m.start(), m.end()) for m in explicit.finditer(text))

    markers = rule_set_markers(text)
    bare = re.compile(r"\b[Rr]ules?\s+" + num)
    for m in bare.finditer(text):
        s, e = m.start(), m.end()
        # Skip a bare match inside an explicit-prefix span (defensive; the
        # explicit patterns don't contain the word "Rule" today).
        if any(s0 <= s < e0 for s0, e0 in spans):
            continue
        attributed = None
        for ms, _me, canon in markers:
            if e <= ms <= e + 80 and _TRAILING_GAP_RE.fullmatch(text[e:ms]):
                attributed = canon
                break
        if attributed is None:
            preceding = [c for ms, _me, c in markers if ms < s]
            if preceding:
                attributed = preceding[-1]
        if attributed is None:
            attributed = sole_set
        if attributed == prefix:
            spans.append((s, e))
    spans.sort()
    return spans


def rule_target(normalized: str) -> dict | None:
    """Split a canonical rule cite into {prefix, number}.

    The number is the final whitespace-delimited token ('N.D.R.Civ.P. 56' →
    prefix 'N.D.R.Civ.P.', number '56')."""
    parts = normalized.rsplit(" ", 1)
    if len(parts) != 2 or not re.match(r"^\d", parts[1]):
        return None
    return {"prefix": parts[0], "number": parts[1]}


# --- subsection pinpoints ----------------------------------------------------

# A trailing pinpoint chain directly after the section/rule number:
# "(1)", "(1)(j)", "(b)(2)". Components are 1–2 digits or 1–4 letters —
# NOT a 4-digit year "(2007)" or a prose parenthetical "(emphasis added)".
_TRAILING_PIN_RE = re.compile(r"^(?:\((?:[0-9]{1,2}|[A-Za-z]{1,4})\))+")

# The preceding form: "subsection 1 of [section] X" / "subdivision (j) of ...".
_PRECEDING_PIN_RE = re.compile(
    r"[Ss]ub(?:section|division)s?\s+\(?([0-9]{1,2}|[a-z])\)?\s+of\s+"
    r"(?:[Ss]ection\s+)?$"
)


def pincite_at(text: str, start: int, end: int) -> str | None:
    """The subsection pinpoint a mention at ``text[start:end]`` carries, as a
    normalized path ('(1)(j)'), or None. Trailing chain wins over the
    preceding 'subsection N of' form."""
    m = _TRAILING_PIN_RE.match(text[end:end + 40])
    if m:
        return normalize_pincite(m.group(0))
    m = _PRECEDING_PIN_RE.search(text[max(0, start - 40):start])
    if m:
        return normalize_pincite(f"({m.group(1)})")
    return None


# --- per-opinion signals -----------------------------------------------------

# Interpretive vocabulary near a mention → the opinion is (heuristically)
# CONSTRUING the provision, not just citing it. Conservative and sentence-
# local, same doctrine as memo.classify_treatment: never authoritative.
_CONSTRUE_TERMS = (
    "construe", "construing", "construed", "statutory construction",
    "construction of", "interpret", "plain language", "plain meaning",
    "meaning of", "ambiguous", "ambiguity", "legislative intent",
    "legislative history", "we read", "canon of",
)


def classify_construes(context: str) -> bool:
    low = context.lower()
    return any(t in low for t in _CONSTRUE_TERMS)


_NORM_WORD_RE = re.compile(r"[a-z0-9]+")


def norm_words(s: str) -> list[str]:
    """Typography-tolerant word tokens (lowercased alphanumerics)."""
    return _NORM_WORD_RE.findall(s.lower())


def quotes_provision(opinion_text: str, provision_words: list[str], n: int = 8) -> bool:
    """True if the opinion reproduces ≥``n`` consecutive words of the
    provision's text (word-level, typography-tolerant). Provisions shorter
    than ``n`` words are matched whole; under 4 words the check is skipped
    (too short to distinguish quotation from coincidence)."""
    if len(provision_words) < 4:
        return False
    n = min(n, len(provision_words))
    op_words = norm_words(opinion_text)
    if len(op_words) < n:
        return False
    op_shingles = {" ".join(op_words[i:i + n]) for i in range(len(op_words) - n + 1)}
    return any(
        " ".join(provision_words[i:i + n]) in op_shingles
        for i in range(len(provision_words) - n + 1)
    )


# --- occurrence entry assembly ----------------------------------------------

def occurrence_entries(
    text: str, spans: list[tuple[int, int]], *, want_pincite: bool,
    max_contexts: int = 3,
) -> tuple[list[dict], list[str]]:
    """Build the per-mention entries for one citing opinion.

    Returns ``(entries, pincites)``: up to ``max_contexts`` entries
    ({paragraph, context, pincite?}) plus the DISTINCT normalized pincites
    across ALL spans (so subsection grouping sees every mention even when
    contexts are truncated)."""
    entries: list[dict] = []
    pincites: list[str] = []
    seen_contexts: set[str] = set()
    for start, end in spans:
        pin = pincite_at(text, start, end) if want_pincite else None
        if pin and pin not in pincites:
            pincites.append(pin)
        if len(entries) < max_contexts:
            context = context_window(text, start, end)
            if context in seen_contexts:
                # Several mentions inside one ¶ yield the same window; the
                # mention still counts (and its pincite is captured above).
                continue
            seen_contexts.add(context)
            entry = {
                "paragraph": find_paragraph(text, start),
                "context": context,
            }
            if pin:
                entry["pincite"] = pin
            entries.append(entry)
    return entries, pincites
