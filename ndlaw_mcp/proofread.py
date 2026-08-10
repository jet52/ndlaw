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
_STAR_PAGE2 = re.compile(r"\[\*\*(\d{1,4})\]")   # dual-paginated second series
# Volume + reporter prefix of a regional/official cite, for page pinpoints.
_REPORTER_CITE = re.compile(r"^\s*(\d+)\s+(N\.\s?W\.(?:\s?[23]d)?|N\.\s?D\.)\s+(\d+)")

# ndcourts-markdown footnote sections (distinct from the West/CL period form):
#   NOTES form:     "\nNOTES\n[1] body\n\n[2] body"   (calls survive inline as [N])
#   FOOTNOTES form: "\nFOOTNOTES\n\n1:\n\nbody"        (calls do not survive OCR)
_NOTES_HEADER = re.compile(r"\n[ \t]*NOTES[ \t]*\n")
_FOOTNOTES_HEADER = re.compile(r"\n[ \t]*FOOTNOTES[ \t]*\n")
# Separate-writing author line ("LEVINE, Justice, dissenting.") — ends a
# per-writing FOOTNOTES section (convention ratified by JT 2026-07-29:
# each writing keeps its own section, numbering as printed). The canonical
# pattern; web_templates builds its line-matcher from this string.
WRITING_SEP_PAT = (
    r"(?:\[\*\d+\]\s+)?"
    r"(?!The\b|Honorable\b|Hon\.)[A-Z][A-Za-z'’ .-]{1,40},\s+"
    r"(?:Acting\s+|Chief\s+|Surrogate\s+|District\s+)*"
    r"(?:Justice|Judge|C\.\s?J\.|J\.)"
    r"(?:[,.]?\s*\(?(?:respectfully\s+|specially\s+)*"
    r"(?:concurring|dissenting|writing\s+separately)[^.\n]{0,50}\.?"
    r"|\.)\s*$")
# Matches a full author line in either form: with participle ("LEVINE,
# Justice, dissenting.", "ERICKSTAD, Chief Justice, respectfully
# dissenting.", "VOGEL, Judge (dissenting).", "MESCHKE, Justice, writing
# separately.") or bare ("ERICKSTAD, Chief Justice." — Sakellson's dissent
# opens this way, the header having already said who dissents). A leading
# star-page marker is allowed ("[*452] LEVINE, Justice, concurring in
# result." — Wiederholt). The name part carries no comma, which excludes
# "Appeal from ..., Judge." caption lines; header furniture ("Erickstad,
# C.J., filed dissenting opinion.", "VandeWalle, J., concurred specially.")
# fails both branches, as do signature lines ("MESCHKE and GIERKE, JJ.,
# concur.") and judge-designation footnote bodies ("The Honorable Eugene A.
# Burdick, Surrogate Judge." — Finch v. Backes fn 2). Match against the RAW
# line — a tab-leading (block-quoted) author line is quoted text, not a
# boundary. SPACE-led lines DO match (`^ *`, spaces only, never tab): 134
# separators in the 2019–24 band are stored with one leading space
# (space-led-separators-census-2026-08-09), and a matcher blind to it let a
# per-writing FOOTNOTES section run past the boundary into the next writing.
_WRITING_SEP = re.compile(r"(?m)^ *" + WRITING_SEP_PAT)
_BRACKET_NOTE = re.compile(r"(?m)^[ \t]*\[(\d{1,3})\]")   # line-anchored [N] body opener
# Inline footnote call. `[nN]` is the corpus notation (JT 2026-08-04): a bare
# `[N]` cannot serve, because treatise subdivisions (`§ 34.11[5]`), bracketed
# pages (`490 U.S. [163]`) and the courts' own enumerators (`described in [1]
# or [2]`) share that shape. The bare form is still accepted — the notation
# pass only reached opinions with a FOOTNOTES heading.
_BRACKET_CALL = re.compile(r"\[n?(\d{1,3})\]")             # inline call (not [¶ N])
_COLON_NOTE = re.compile(r"(?m)^[ \t]*(\d{1,2}):[ \t]*$")  # "N:" body opener
# Repaired West/CL period form (batch `footnote-def-join-2026-07-24`): the label
# and its orphaned period rejoined onto the body line — "1. See ABA Standards
# ..." — which is what the court's archive HTML itself renders. Unlike the split
# form it is NOT self-identifying: a quoted statutory subsection opens the same
# way, so a match counts as a body only when the footnote's CALL survives earlier
# in the text (see `_labelled_bodies`).
_LABELLED_NOTE = re.compile(r"(?m)^(?:\[n(\d{1,3})\]|(\d{1,3})\.)[ \t]+(?=\S)")


def _note_num(m: "re.Match") -> int:
    """Footnote number from a `_LABELLED_NOTE` match, either notation."""
    return int(m.group(1) or m.group(2))

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
    ``{"bodies": [(num, start, end), ...], "call_para": {num: ¶_or_None},
    "call_at": {num: offset}, "detached": bool}`` (bodies sorted by position).
    ``call_para`` is ``None`` when the call marker did not survive (attached
    superscript, or a format that drops calls).

    ``call_at`` is the call marker's byte offset — the same site ``call_para``
    names, kept unrounded so `locate_structure` can read the reporter page off
    it. ``detached`` is ``True`` when the bodies live in a trailing section
    rather than at the position where they were printed, which makes a body's
    own offset useless for pagination.

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
            return {"bodies": _spans(text, opens), "call_para": {},
                    "call_at": {}, "detached": True}
        # Relocated form (batch `footnote-relocate-2026-07-25`): "N. body" openers
        # inside the FOOTNOTES section, calls left inline in the body as [N].
        # When the heading is present the SECTION is authoritative — otherwise a
        # quoted statutory subsection earlier in the opinion ("1. The court shall
        # ...") could be taken for footnote 1's body.
        #
        # Per-writing sections (JT 2026-07-29): an opinion carries ONE section
        # per writing, each ending at the next separate-writing author line;
        # numbering restarts per writing, so ``bodies`` may repeat a number.
        # ``call_para``/``call_at`` are keyed by the body's START offset here
        # (unique), with the legacy num key kept as a fallback for callers.
        heads = list(_FOOTNOTES_HEADER.finditer(text))
        all_bodies, call_para, call_at = [], {}, {}
        prev_end = 0
        for k, hm in enumerate(heads):
            limit = heads[k + 1].start() if k + 1 < len(heads) else len(text)
            sep = _WRITING_SEP.search(text, hm.end(), limit)
            reg_end = sep.start() if sep else limit
            opens, seen = [], set()
            for m in _LABELLED_NOTE.finditer(text, hm.end(), reg_end):
                num = _note_num(m)
                if num not in seen:
                    seen.add(num)
                    opens.append((num, m.start()))
            spans = []
            for j, (num, pos) in enumerate(opens):
                end = opens[j + 1][1] if j + 1 < len(opens) else reg_end
                spans.append((num, pos, end))
            for num, pos, _ in spans:
                # Same discipline as the standalone path: a surviving bare-
                # number call line is authoritative; an inline [N] counts only
                # when it is UNIQUE in this writing's span (2016 ND 249: the
                # real call is at ¶4 and a spurious [1] sits at ¶16). The call
                # search window is this writing's text: [prev section end,
                # this heading).
                cp = next((prev_end + m.start() for m in
                           _STANDALONE_NUM.finditer(text[prev_end:hm.start()])
                           if int(m.group(1)) == num), None)
                if cp is None:
                    hits = [m for m in _BRACKET_CALL.finditer(
                                text, prev_end, hm.start())
                            if int(m.group(1)) == num]
                    cp = hits[0].start() if len(hits) == 1 else None
                if cp is not None:
                    call_para[pos] = find_paragraph(text, cp, markers)
                    call_at[pos] = cp
                    call_para.setdefault(num, call_para[pos])
                    call_at.setdefault(num, cp)
            all_bodies.extend(spans)
            prev_end = reg_end
        if all_bodies:
            return {"bodies": all_bodies, "call_para": call_para,
                    "call_at": call_at, "detached": True}
    # NOTES form: line-anchored "[N]" bodies after a NOTES header; the call is
    # the earliest inline "[N]" before the header.
    nh = _NOTES_HEADER.search(text)
    if nh:
        sec = text[nh.end():]
        opens = [(int(m.group(1)), nh.end() + m.start())
                 for m in _BRACKET_NOTE.finditer(sec)]
        if opens:
            call_para, call_at = {}, {}
            for num, _ in opens:
                if num in call_para:
                    continue
                cm = next((m for m in _BRACKET_CALL.finditer(text, 0, nh.start())
                           if int(m.group(1)) == num), None)
                if cm is not None:
                    call_para[num] = find_paragraph(text, cm.start(), markers)
                    call_at[num] = cm.start()
            return {"bodies": _spans(text, opens), "call_para": call_para,
                    "call_at": call_at, "detached": True}
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


def _labelled_bodies(text: str, occ: list) -> list:
    """Repaired ``N. body`` footnote openers, confirmed by a surviving call.

    ``N. `` at the start of a line is ambiguous on its face — a quoted statutory
    subsection looks identical — so an opener counts only when footnote ``N``'s
    CALL appears earlier in the text, either as the inline ``[N]`` marker (batch
    `footnote-ref-inline-2026-07-24`) or as a still-unrepaired bare-number line.
    First occurrence per number wins, so a later numbered list cannot displace
    the real body."""
    bare_at = {}
    for num, ls, _after, _period in occ:
        bare_at.setdefault(num, ls)
    out, seen = [], set()
    for m in _LABELLED_NOTE.finditer(text):
        num = _note_num(m)
        if not (1 <= num <= 60) or num in seen:
            continue
        called = any(int(c.group(1)) == num
                     for c in _BRACKET_CALL.finditer(text, 0, m.start()))
        if not called and bare_at.get(num, len(text)) >= m.start():
            continue
        seen.add(num)
        out.append((num, m.start(), m.end()))
    return out


def _standalone_footnotes(text: str) -> dict:
    """West/CL-OCR period form, its repaired ``N. body`` shape, and
    tail-after-last-``[¶]`` standalone bodies."""
    occ = []  # (num, line_start, after_line, is_period_form)
    for m in _STANDALONE_NUM.finditer(text):
        num = int(m.group(1))
        if 1 <= num <= 60:
            period = bool(re.match(r"\s*\.\s", text[m.end():m.end() + 12]))
            occ.append((num, m.start(), m.end(), period))

    labelled = _labelled_bodies(text, occ)
    if not occ and not labelled:
        return {"bodies": [], "call_para": {}, "call_at": {}, "detached": False}

    markers = paragraph_markers(text)
    last_para = markers[-1][1] if markers else -1

    body_at = {}  # line_start -> num, for occurrences that open a footnote body
    after_of = {}  # line_start -> offset just past the opener
    for num, ls, after, period in occ:
        if period or (markers and ls > last_para):
            body_at[ls] = num
            after_of[ls] = after
    for num, ls, after in labelled:
        body_at[ls] = num
        after_of[ls] = after

    body_lines = sorted(body_at)
    bodies = []
    for k, ls in enumerate(body_lines):
        after = after_of[ls]
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
    call_para, call_at = {}, {}
    for num, ls, after, period in occ:
        if ls in body_at:
            continue
        if num in body_nums and num not in call_para:
            call_para[num] = find_paragraph(text, ls, markers)
            call_at[num] = ls
    # Fallback: an inline ``[N]``/``[nN]`` call for a confirmed footnote whose
    # call did not survive as a bare-line marker. Gated against bracketed
    # quote-alterations (``[t]he``, a quoted ``[1]``): ``N`` must be a
    # confirmed body and the call unique BEFORE the body opener. The window
    # must stop at the body: the ``[nN]`` notation deliberately uses one token
    # for the call and the definition label, so a whole-text search would
    # always find two and refuse (the 2026-08-05 headingless batch exposed
    # this — same window discipline as the FOOTNOTES-heading path).
    for num in body_nums - call_para.keys():
        hits = [m for m in _BRACKET_CALL.finditer(text, 0, body_start[num])
                if int(m.group(1)) == num]
        if len(hits) == 1:
            call_para[num] = find_paragraph(text, hits[0].start(), markers)
            call_at[num] = hits[0].start()
    return {"bodies": bodies, "call_para": call_para,
            "call_at": call_at, "detached": False}


def star_page_before(text: str, offset: int, series: int = 1) -> int | None:
    """Reporter page for ``offset`` — the last star-page marker at or before it.

    ``series=1`` reads ``[*NNN]``, ``series=2`` the second series ``[**NNN]``
    carried by dual-paginated West texts. ``None`` when that series is absent."""
    page = None
    rx = _STAR_PAGE if series == 1 else _STAR_PAGE2
    for m in rx.finditer(text):
        if m.start() <= offset:
            page = int(m.group(1))
        else:
            break
    return page


def star_series_reporters(text: str, cite_rows: list[dict]) -> dict[int, tuple[str, str]]:
    """Which reporter each star-page series belongs to: ``{series: (vol, rep)}``.

    Necessary because the marker's SHAPE does not tell you: measured against
    each opinion's own cite bands, ``[*NNN]`` sits in the N.W. band alone in
    14,350 opinions but the N.D. Reports band alone in 893 — the dual-paginated
    old West texts, which are exactly the ones also carrying ``[**NNN]``.

    Assignment is by first page, not by band: the bands overlap in precisely the
    dual case (1941 ND 80 is ``1 N.W.2d 335`` / ``71 N.D. 363``, and 363 falls
    inside both). A series' LOWEST marker is the page the opinion opens on in
    that reporter, so each series takes the cite whose first page it starts at.
    A series is left unassigned rather than guessed when nothing fits."""
    cites = []
    for r in cite_rows:
        m = _REPORTER_CITE.match(r.get("citation", ""))
        if m:
            cites.append((m.group(1), m.group(2), int(m.group(3))))
    if not cites:
        return {}
    out: dict[int, tuple[str, str]] = {}
    taken: set[int] = set()
    mins = {}
    for s, rx in ((1, _STAR_PAGE), (2, _STAR_PAGE2)):
        vals = [int(m.group(1)) for m in rx.finditer(text)]
        if vals:
            mins[s] = min(vals)
    if len(cites) == 1:
        # nothing to disambiguate; the sole reporter owns whatever is present
        for s in mins:
            out[s] = (cites[0][0], cites[0][1])
        return out
    # closest first page wins, and a series cannot start before its reporter does
    for s in sorted(mins, key=lambda s: mins[s]):
        best, best_d = None, None
        for i, (vol, rep, fp) in enumerate(cites):
            if i in taken or mins[s] < fp - 2:
                continue
            d = mins[s] - fp
            if best_d is None or d < best_d:
                best, best_d = i, d
        if best is not None:
            taken.add(best)
            out[s] = (cites[best][0], cites[best][1])
    return out


def locate_structure(text: str, offset: int, struct: dict | None = None) -> dict:
    """Resolve ``offset`` to its structural pinpoint fields.

    Returns ``{"paragraph", "footnote", "in_footnote", "reporter_page",
    "reporter_page_2"}`` — the second field is the dual-pagination ``[**NNN]``
    series, ``None`` in the ~97% of opinions that carry only one series. When
    the offset lands inside a footnote body, ``paragraph`` is the footnote's
    *call* paragraph (not the body's preceding marker) and ``footnote`` is its
    number; ``paragraph`` may be ``None`` if the call site is unrecoverable.

    **Reporter page inside a footnote comes from the CALL SITE** (JT ruling
    2026-07-26), not from the body's own offset: a note prints at the foot of the
    page carrying its call. This matters because the bodies of a relocated
    opinion sit in a trailing ``FOOTNOTES`` section, so scanning from the body
    would report the opinion's LAST page for every footnote in it.

    When the call did not survive, a *detached* body has no usable position at
    all and the page is ``None`` — better than a page known to be wrong. An
    inline body still sits where it was printed, so it keeps the scan."""
    struct = struct if struct is not None else footnote_structure(text)
    for num, start, end in struct["bodies"]:
        if start <= offset < end:
            # start-keyed first (per-writing sections repeat numbers), num
            # fallback for the legacy single-section paths
            cm = struct.get("call_at", {})
            call_at = cm.get(start, cm.get(num))
            if call_at is not None:
                page = star_page_before(text, call_at)
                page2 = star_page_before(text, call_at, series=2)
            elif struct.get("detached"):
                page = page2 = None
            else:
                page = star_page_before(text, offset)
                page2 = star_page_before(text, offset, series=2)
            pm = struct.get("call_para", {})
            return {"paragraph": pm.get(start, pm.get(num)), "footnote": num,
                    "in_footnote": True, "reporter_page": page,
                    "reporter_page_2": page2}
    return {"paragraph": find_paragraph(text, offset), "footnote": None,
            "in_footnote": False,
            "reporter_page": star_page_before(text, offset),
            "reporter_page_2": star_page_before(text, offset, series=2)}


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


def reporter_pinpoint(cite_rows: list[dict], page: int | None,
                      page2: int | None = None,
                      text: str | None = None) -> str | None:
    """``604 N.W.2d at 458`` from an opinion's parallel cites and a star page.

    With ``text`` and a dual-paginated opinion, BOTH series are resolved and
    paired with the right reporter, returning e.g.
    ``71 N.D. at 363, 1 N.W.2d at 335``.

    Passing ``text`` matters: without it this function paired the star page with
    the FIRST reporter cite, which fabricates a pinpoint wherever `[*NNN]` is
    the N.D. page — 1941 ND 80 reported ``1 N.W.2d at 363`` though that volume
    opens at 335. A page is dropped rather than mislabelled when its reporter
    cannot be identified."""
    if page is None and page2 is None:
        return None
    if text is not None:
        owners = star_series_reporters(text, cite_rows)
        parts = []
        for s, p in ((1, page), (2, page2)):
            if p is None or s not in owners:
                continue
            vol, rep = owners[s]
            parts.append((rep, f"{vol} {rep} at {p}"))
        if parts:
            # the regional N.W. reporter leads, per the documented preference
            parts.sort(key=lambda kv: 0 if "W" in kv[0] else 1)
            return ", ".join(p for _, p in parts)
        return None
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
