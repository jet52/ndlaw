"""Pure helpers for the one-call draft cite-check (``check_draft``).

Draft-side extraction: every case citation (with the antecedent case name
where one cleanly precedes the cite), every ND authority citation (N.D.C.C.,
N.D.A.C., court rules via the notes.py rule-set attribution ladder, and the
Constitution), quotation spans, ``Id.`` reference resolution, and the
quote→citation attribution heuristic. No DB access; ``server.py`` holds the
``@mcp.tool()`` wrapper that runs the verification passes.

Doctrine: extraction is regex-only (jetcite is an ingest-time dependency, not
a serve-time one) and precision-first — an authority reference the extractor
is unsure about is dropped or reported as ambiguous, never guessed. Quote
attribution follows the legal convention that support follows the quotation
("quote." *Cite.*): the first citation shortly AFTER the closing quote wins,
falling back to the nearest citation before it within the same paragraph;
attribution is a heuristic and every flag carries the draft context for human
verification.
"""

from __future__ import annotations

import re

from . import notes, research

# --------------------------------------------------------------------------- #
# case citations + antecedent names
# --------------------------------------------------------------------------- #


def case_cite_spans(text: str) -> list[dict]:
    """Every ND / N.W. / N.D. reporter citation with its draft offsets.

    Returns ``[{start, end, kind: 'case', citation}]`` sorted by position;
    ``citation`` is normalized to DB form (see ``research.extract_case_cites``).
    """
    out: list[dict] = []
    seen: set[tuple[int, int]] = set()
    for pat in research._CASE_CITE_RES:
        for m in pat.finditer(text):
            span = (m.start(), m.end())
            if span in seen:
                continue
            seen.add(span)
            out.append({
                "start": m.start(), "end": m.end(), "kind": "case",
                "citation": research.normalize_cite_string(m.group(0)),
            })
    out.sort(key=lambda c: c["start"])
    return out


# The "In re …" caption family, anchored to the citation.
_INRE_TAIL_RE = re.compile(
    r"((?:In re|In the Matter of|Matter of|Estate of|Interest of|"
    r"State ex rel\.)\s+[A-Z][\w'’.&\-() ]{0,60}?),?\s*$")
# The defendant side of a "v." caption, running to the citation.
_V_TAIL_RE = re.compile(r"\s(vs?\.)\s+([A-Z][\w'’.&\-() ]{0,60}?),?\s*$")
# Plaintiff-side tokens, walked backwards: capitalized words plus the
# lowercase particles real captions contain. A plain prose word ("held",
# "in") stops the walk, so "As held in Smith v. Jones" captures only
# "Smith v. Jones".
_NAME_TOKEN_RE = re.compile(r"[A-Z][\w'’.&\-]*,?")
_NAME_PARTICLES = {"of", "the", "and", "ex", "rel.", "de", "la", "van", "von"}
# NOTE: bare "In"/"Matter" must never appear here — they are load-bearing
# leads of real captions ("In re …", "Matter of …").
_NAME_LEAD_JUNK = re.compile(
    r"^(?:[Ss]ee(?:,? e\.g\.,?| also)?|E\.g\.,?|Accord,?|Cf\.|[Qq]uoting|"
    r"[Cc]iting|[Cc]ompare|Under|Following|As|And|But|In)\s+(?!re\b|the Matter\b)")


def _strip_lead_junk(name: str) -> str | None:
    while True:
        stripped = _NAME_LEAD_JUNK.sub("", name)
        if stripped == name:
            return name or None
        name = stripped


def antecedent_name(text: str, cite_start: int) -> str | None:
    """The case name written immediately before the cite, or None.

    Conservative: only a clean "Name v. Name," / "In re …," tail directly
    abutting the citation is captured (markdown emphasis stripped; prose
    lead-ins like "As held in" walked off). A tail ending in a pinpoint or
    another cite ("¶ 8,") captures nothing — a parallel cite inherits the
    name via opinion-level dedupe, never a guess.
    """
    tail = re.sub(r"[*_]", "", text[max(0, cite_start - 120):cite_start])
    m = _INRE_TAIL_RE.search(tail)
    if m:
        return _strip_lead_junk(m.group(1).strip())
    m = _V_TAIL_RE.search(tail)
    if m is None:
        return None
    name_toks: list[str] = []
    for tok in reversed(tail[:m.start()].split()):
        if _NAME_TOKEN_RE.fullmatch(tok) or tok.lower() in _NAME_PARTICLES:
            name_toks.insert(0, tok)
        else:
            break
    if not name_toks:
        return None
    name = " ".join(name_toks + [m.group(1), m.group(2).strip()])
    return _strip_lead_junk(name)


# --------------------------------------------------------------------------- #
# authority citations (N.D.C.C. / N.D.A.C. / court rules / Constitution)
# --------------------------------------------------------------------------- #

# A dash-numbered token only counts as an authority cite with citation
# vocabulary directly before it — bare "7-1-1997" (a date) never matches.
_SECTION_CTX_RE = re.compile(
    r"(?:§§?|[Ss]ections?|[Cc]hapters?|[Cc]h\.|N\.?\s?D\.?\s?C\.?\s?C\.?)[\s,]*$")
_ADMIN_NEAR_RE = re.compile(
    r"N\.?\s?D\.?\s?A\.?\s?C\.?|Admin(?:istrative)?\.?\s?Code")
_CHAPTER_CTX_RE = re.compile(r"(?:[Cc]hapters?|[Cc]h\.)[\s,]*$")


def statute_admin_spans(text: str) -> list[dict]:
    """N.D.C.C. section/chapter and N.D.A.C. section citations with offsets.

    ``[{start, end, kind: 'statute'|'admin', citation, pincite}]``. Segment
    depth routes the corpus (4 → N.D.A.C., per the parser's existing rule);
    3-segment tokens in an Admin.-Code context are NDAC *chapters* and are
    skipped (not modeled as provisions).
    """
    out: list[dict] = []
    for m in research._SECTION_RE.finditer(text):
        tok = m.group(1)
        segs = tok.split("-")
        before = text[max(0, m.start() - 40):m.start()]
        admin_near = _ADMIN_NEAR_RE.search(text[max(0, m.start() - 80):m.start()])
        has_ctx = _SECTION_CTX_RE.search(before)
        if not (has_ctx or (admin_near and len(segs) >= 4)):
            continue
        if len(segs) >= 4:
            kind, citation = "admin", f"N.D.A.C. § {tok}"
        elif len(segs) == 3:
            if admin_near:
                continue  # NDAC chapter reference — no provision to verify
            kind, citation = "statute", f"N.D.C.C. § {tok}"
        else:  # 2 segments = NDCC chapter
            if admin_near:
                continue
            kind, citation = "statute", f"N.D.C.C. ch. {tok}"
        out.append({
            "start": m.start(1), "end": m.end(1), "kind": kind,
            "citation": citation,
            "pincite": notes.pincite_at(text, m.start(1), m.end(1)),
        })
    return out


_ND_RULE_PREFIXES = sorted(
    {v for v in research._RULE_ALIASES.values() if not v.startswith("Fed.")},
    key=len, reverse=True,
)
_RULE_NUM_GROUP = r"(\d+(?:[.-]\d+)*[A-Za-z]?)"


def rule_cite_spans(text: str) -> list[dict]:
    """Court-rule citations with offsets, three populations:

    * explicit ND prefix ("N.D.R.Civ.P. 56") → kind 'court_rule' + citation;
    * bare "Rule 56" attributed via the notes.py marker ladder (trailing
      marker → nearest preceding marker) → 'court_rule' with the attributed
      set, 'federal_rule' when a federal set wins (reported, not verified),
      or citation None when unattributable (reported as ambiguous);
    * the trailing "Rule 56, N.D.R.Civ.P." form arrives via the bare path.
    """
    out: list[dict] = []
    taken: list[tuple[int, int]] = []
    for prefix in _ND_RULE_PREFIXES:
        pat = re.compile(
            notes._flex_prefix_pattern(prefix) + r"\s*" + _RULE_NUM_GROUP
            + notes._RULE_NUM_BOUNDARY)
        for m in pat.finditer(text):
            if any(s <= m.start() < e for s, e in taken):
                continue
            taken.append((m.start(), m.end()))
            out.append({
                "start": m.start(), "end": m.end(), "kind": "court_rule",
                "citation": f"{prefix} {m.group(1)}",
                "pincite": notes.pincite_at(text, m.start(), m.end()),
            })

    markers = notes.rule_set_markers(text)
    bare = re.compile(r"\b[Rr]ules?\s+" + _RULE_NUM_GROUP
                      + notes._RULE_NUM_BOUNDARY)
    for m in bare.finditer(text):
        s, e = m.start(), m.end()
        if any(s0 <= s < e0 or s <= s0 < e for s0, e0 in taken):
            continue
        attributed = None
        for ms, _me, canon in markers:
            if e <= ms <= e + 80 and notes._TRAILING_GAP_RE.fullmatch(text[e:ms]):
                attributed = canon
                break
        if attributed is None:
            preceding = [c for ms, _me, c in markers if ms < s]
            attributed = preceding[-1] if preceding else None
        if attributed is None:
            entry_kind, citation = "court_rule", None      # ambiguous
        elif attributed.startswith("Fed."):
            entry_kind, citation = "federal_rule", f"{attributed} {m.group(1)}"
        else:
            entry_kind, citation = "court_rule", f"{attributed} {m.group(1)}"
        out.append({
            "start": s, "end": e, "kind": entry_kind, "citation": citation,
            "pincite": notes.pincite_at(text, s, e),
        })
    out.sort(key=lambda c: c["start"])
    return out


# "N.D. Const. art. I, § 8" and "article I, section 8 of the North Dakota
# Constitution". Original-1889 numbering and amendment articles are not
# extracted (rare in modern drafts; precision-first).
_CONST_SPAN_RES = [
    re.compile(
        r"N\.\s?D\.\s?Const\.?,?\s+[Aa]rt(?:icle)?\.?\s+([IVXLCDM]+),?\s*"
        r"(?:§§?|[Ss]ec(?:tion)?s?\.?)\s*(\d+(?:\.\d+)?)"),
    re.compile(
        r"[Aa]rt(?:icle)?\.?\s+([IVXLCDM]+),?\s*(?:§§?|[Ss]ections?)\s*"
        r"(\d+(?:\.\d+)?)"
        r"(?=[^.]{0,60}?of the (?:North Dakota|N\.\s?D\.) Constitution)"),
]


def const_cite_spans(text: str) -> list[dict]:
    out: list[dict] = []
    taken: list[tuple[int, int]] = []
    for pat in _CONST_SPAN_RES:
        for m in pat.finditer(text):
            if any(s <= m.start() < e for s, e in taken):
                continue
            taken.append((m.start(), m.end()))
            out.append({
                "start": m.start(), "end": m.end(), "kind": "constitution",
                "citation": f"N.D. Const. art. {m.group(1)}, § {m.group(2)}",
                "pincite": notes.pincite_at(text, m.start(), m.end()),
            })
    out.sort(key=lambda c: c["start"])
    return out


_CAPTION_ANNOTATION_RE = re.compile(r"\s*\([A-Z][A-Z .\-]+\)\s*$")


def strip_caption_annotations(name: str) -> str:
    """Drop a trailing ALL-CAPS caption annotation — '(CONFIDENTIAL)' — from a
    canonical case name before name-drift comparison. Mixed-case trailing
    parentheticals (real party matter) are kept."""
    return _CAPTION_ANNOTATION_RE.sub("", name)


# --------------------------------------------------------------------------- #
# Id. references
# --------------------------------------------------------------------------- #

_ID_RE = re.compile(r"\b[Ii]d\.")


def id_reference_spans(text: str, cites: list[dict]) -> list[dict]:
    """Each ``Id.`` resolved to the nearest preceding real citation.

    Returned entries mirror the cite shape (kind/citation inherited) with
    ``via_id: True`` — they participate in quote attribution but never create
    their own verification flags."""
    out: list[dict] = []
    for m in _ID_RE.finditer(text):
        prev = None
        for c in cites:
            if c["end"] <= m.start():
                prev = c
            else:
                break
        if prev is not None and prev.get("citation"):
            out.append({
                "start": m.start(), "end": m.end(), "kind": prev["kind"],
                "citation": prev["citation"], "via_id": True,
                "pincite": prev.get("pincite"),
            })
    return out


# --------------------------------------------------------------------------- #
# quotations + attribution
# --------------------------------------------------------------------------- #

_QUOTE_RES = [
    re.compile(r"“([^“”]{15,2400})”"),
    re.compile(r'"([^"]{15,2400})"'),
]


def quotation_spans(text: str, min_words: int = 5) -> list[dict]:
    """Double-quoted spans of at least ``min_words`` words.

    ``[{start, end, quote}]`` (offsets cover the quote marks; ``quote`` is the
    inner text). Curly pairs are matched first; a straight-quote span
    overlapping one is dropped. Block quotes a plain-text draft renders
    without quotation marks are NOT detected (documented v1 limitation)."""
    out: list[dict] = []
    taken: list[tuple[int, int]] = []
    for pat in _QUOTE_RES:
        for m in pat.finditer(text):
            if any(s < m.end() and m.start() < e for s, e in taken):
                continue
            if len(m.group(1).split()) < min_words:
                continue
            taken.append((m.start(), m.end()))
            out.append({"start": m.start(), "end": m.end(), "quote": m.group(1)})
    out.sort(key=lambda q: q["start"])
    return out


def attribute_quotes(
    text: str, quotes: list[dict], cites: list[dict],
    window_after: int = 200, window_before: int = 600,
) -> None:
    """Attach ``cite`` (or None) to each quote dict, in place.

    First citation starting within ``window_after`` chars AFTER the closing
    quote wins (the "quote." *Cite.* convention — the citation's case name
    sits in that gap); else the nearest citation ENDING before the quote,
    within the same paragraph and ``window_before`` chars."""
    ordered = sorted(cites, key=lambda c: c["start"])
    for q in quotes:
        target = None
        for c in ordered:
            if q["end"] <= c["start"] <= q["end"] + window_after:
                target = c
                break
            if c["start"] > q["end"] + window_after:
                break
        if target is None:
            para_start = max(text.rfind("\n\n", 0, q["start"]),
                             text.rfind("[¶", 0, q["start"]), 0)
            floor = max(para_start, q["start"] - window_before)
            for c in ordered:
                if c["end"] <= q["start"] and c["start"] >= floor:
                    target = c
                elif c["start"] >= q["start"]:
                    break
        q["cite"] = target


# --------------------------------------------------------------------------- #
# one-call extraction
# --------------------------------------------------------------------------- #


def extract_all(text: str) -> dict:
    """Run every extractor and the attribution pass over a draft.

    Returns ``{cases, authorities, ambiguous_rules, federal_rules, quotes}``.
    ``cases`` carry ``antecedent`` (or None); ``authorities`` are the
    verifiable ND statute/admin/rule/const cites; quotes carry ``cite``
    (a case/authority/Id. entry, or None = unattributed)."""
    cases = case_cite_spans(text)
    for c in cases:
        c["antecedent"] = antecedent_name(text, c["start"])

    raw_auth = statute_admin_spans(text) + rule_cite_spans(text) + const_cite_spans(text)
    raw_auth.sort(key=lambda c: c["start"])
    authorities = [a for a in raw_auth
                   if a["kind"] in ("statute", "admin", "court_rule",
                                    "constitution") and a["citation"]]
    ambiguous_rules = [a for a in raw_auth
                       if a["kind"] == "court_rule" and not a["citation"]]
    federal_rules = [a for a in raw_auth if a["kind"] == "federal_rule"]

    real_cites = sorted(cases + authorities, key=lambda c: c["start"])
    id_refs = id_reference_spans(text, real_cites)
    quotes = quotation_spans(text)
    attribute_quotes(text, quotes, sorted(real_cites + id_refs,
                                          key=lambda c: c["start"]))
    return {
        "cases": cases,
        "authorities": authorities,
        "ambiguous_rules": ambiguous_rules,
        "federal_rules": federal_rules,
        "quotes": quotes,
    }
