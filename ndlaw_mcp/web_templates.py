"""HTML assembly for the citation-URL web interface (PLAN-web-interface.md).

Hand-rolled template strings + ``html.escape`` — zero new dependencies. All DB
text is escaped BEFORE any markup transformation; the renderer then recognizes
only the corpus's closed marker grammar (fidelity spike 2026-07-28,
``scripts/web_fidelity_spike_2026-07-28.py``):

- ``[¶N]`` paragraph markers (the court prints these literally) → self-linking
  anchors ``id="pN"``. Bare ``¶ N`` in running text is a *reference*, not a
  marker — left untouched.
- ``[*N]`` star-page markers → anchors ``id="starN"``.
- exactly four ``##`` section labels corpus-wide (Concurrence / Dissent /
  On Rehearing / Concurrence in Part) → ``<h2>``.
- ``FOOTNOTES`` heading + inline ``[N]`` refs + ``N.`` bodies (ratified
  footnote convention) → bidirectional links, gated on the heading and the
  collected footnote numbers so bracketed numbers elsewhere stay text.
- Standalone section-furniture lines (``Syllabus of/by the Court``,
  ``Synopsis``, ``Attorneys and Law Firms``, ``Opinion``) → ``<h2>``.
- ``[Figure N: …]`` captions → styled paragraph.
- Lines that begin with whitespace are *continuations* of the previous line
  (the CL-era converter split italic spans and their following cites onto
  their own space-indented lines) — they are rejoined into one paragraph
  before rendering. Verified corpus-wide 2026-07-28: every leading-space
  line class is a continuation; none are tables or block layout.
- Single-asterisk pairs ``*…*`` are West italic markup → ``<em>``, guarded
  so ``***`` omissions, ``* * *`` spaced omissions, and ``**85``-style
  second-series star pages can never match (content must start with a
  letter/quote/paren and contain a letter). Anything unpaired stays
  verbatim; nothing else is ever treated as markdown.
"""
from __future__ import annotations

import html
import re

from ndlaw_mcp import proofread, rule_subsections

# ---------------------------------------------------------------------------
# page shell
# ---------------------------------------------------------------------------

_STYLE = """
  body { font-family: Georgia, 'Times New Roman', serif; max-width: 46rem;
         margin: 2.5rem auto; padding: 0 1.25rem; line-height: 1.55; color: #1a1a1a; }
  h1 { font-size: 1.35rem; margin-bottom: .2rem; line-height: 1.3; }
  h2 { font-size: 1.1rem; margin-top: 1.8rem; }
  h3.section { font-size: 1rem; margin: 1.5rem 0 .3rem; text-align: center; }
  a { color: #1a5276; }
  .meta { color: #444; font-size: .95em; margin: .15rem 0; }
  .meta b { color: #1a1a1a; }
  .cites { margin: .3rem 0 .1rem; }
  .counts { margin: 1rem 0; padding: .5em .9em; background: #f4f4f2;
            border-radius: 4px; font-size: .95em; }
  .body p { margin: .65em 0; }
  .pm { text-decoration: none; color: inherit; font-weight: bold; }
  .pm:hover { color: #1a5276; }
  .star { color: #8a6d1a; font-size: .85em; vertical-align: super; }
  del.redline { text-decoration: line-through; color: #8b2500; }
  ins.redline { text-decoration: underline; color: #1a5f2a; }
  .fn-ref { text-decoration: none; }
  .fn { font-size: .93em; }
  .figure { font-style: italic; color: #555; }
  pre.tbl { font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
            font-size: .85em; overflow-x: auto; line-height: 1.45; }
  blockquote { margin: .8em 0 .8em 2.2em; padding-left: .9em;
               border-left: 2px solid #ccc; }
  .srcs { margin-top: 1.2rem; font-size: .95em; }
  .ind1 { margin-left: 1.6rem; }
  .ind2 { margin-left: 3.2rem; }
  .ind3 { margin-left: 4.8rem; }
  .ind4 { margin-left: 6.4rem; }
  .candidates li { margin: .4em 0; }
  .pager { margin: 1.2rem 0; }
  footer { margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #ddd;
           color: #666; font-size: .85em; }
  @media (prefers-color-scheme: dark) {
    body { background: #16181d; color: #d8d8d4; }
    .meta { color: #aaa; } .meta b { color: #d8d8d4; }
    a { color: #7fb3d5; }
    .counts { background: #23262d; }
    .star { color: #c9a227; }
    del.redline { color: #e07a5f; } ins.redline { color: #7fd58a; }
    .figure { color: #999; }
    blockquote { border-color: #444; }
    footer { border-color: #333; color: #999; }
  }
"""

# Wording RATIFIED by JT 2026-07-30 (PLAN-web-interface §4.1).
DISCLAIMER = (
    "Unofficial copy, served from the <a href=\"https://ndlaw.org/\">ndlaw</a> "
    "corpus (<a href=\"https://creativecommons.org/publicdomain/zero/1.0/\">CC0</a>), "
    "compiled from public sources with extensive validation. Validation is "
    "not complete and some work remains to verify clean text from imperfect "
    "and inconsistent sources. Not an official publication of the State of "
    "North Dakota or its courts. Verify against an official source before "
    "citing in an official filing with a court or other tribunal."
)

_OFFICIAL_PHRASE = "an official source"

# Per-corpus official-source fallbacks for the footer link, used when a
# document carries no URL of its own. Phase B extends per-document links
# from jetcite's official-URL generators (text_citations.url already
# proves the pattern: ndlegis.gov/cencode/tNNcNN.pdf#nameddest=...).
OFFICIAL_FALLBACK = {
    "opinions": "https://www.ndcourts.gov/supreme-court/opinions",
    "ndcc": "https://ndlegis.gov/general-information/north-dakota-century-code",
    "ndac": "https://ndlegis.gov/agency-rules/north-dakota-administrative-code",
    "const": "https://ndlegis.gov/constitution",
    "rule": "https://www.ndcourts.gov/legal-resources/rules",
    "ag": "https://attorneygeneral.nd.gov/",
    "jeac": "https://www.ndcourts.gov/committees/judicial-ethics-advisory-committee",
}


# Data-currency line for the footer, set once at server startup by
# web.register() (DB-file mtime + MAX(date_filed)). None outside the
# server (CLI renderers, tests that never call register), and the footer
# then omits the line rather than guessing.
DATA_STAMP: str | None = None


def set_data_stamp(stamp: str | None) -> None:
    global DATA_STAMP
    DATA_STAMP = stamp


def disclaimer_html(official_url: str | None = None) -> str:
    """The footer disclaimer; when a document-specific (or per-corpus)
    official URL is known, the ratified phrase 'an official source'
    becomes the link — the instruction and its destination live in the
    same sentence."""
    if not official_url:
        return DISCLAIMER
    link = (f'<a href="{html.escape(official_url, quote=True)}">'
            f"{_OFFICIAL_PHRASE}</a>")
    return DISCLAIMER.replace(_OFFICIAL_PHRASE, link, 1)


def page(title: str, body: str, *, h1: str | None = None,
         official_url: str | None = None, canonical: str | None = None) -> str:
    """Wrap ``body`` (already-safe HTML) in the shared page shell.

    ``canonical`` names the preferred URL when a document is reachable at more
    than one (a provision answers to both ``/rule/ndrappp/4`` and the short
    ``/ndrappp4``); both serve 200, and this is what tells a tool which one to
    quote."""
    link = ""
    if canonical:
        link = (f'\n<link rel="canonical" '
                f'href="{html.escape(canonical, quote=True)}">')
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{html.escape(title)}</title>{link}
<style>{_STYLE}</style>
</head>
<body>
{f'<h1>{html.escape(h1)}</h1>' if h1 else ''}
{body}
<footer>{disclaimer_html(official_url)}{f'<br>{html.escape(DATA_STAMP)}' if DATA_STAMP else ''}</footer>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# opinion-body renderer
# ---------------------------------------------------------------------------

_H2_LABELS = {"Concurrence", "Dissent", "On Rehearing", "Concurrence in Part"}
_MD_HEAD = re.compile(r"^##\s*(.+?)\s*$")
# standalone section-furniture lines render as headings (JT 2026-08-06, the
# syllabus-restore eyeball round): both syllabus forms as printed, plus the
# West structural labels the texts carry. Full-line anchored so body prose
# mentioning "opinion" is never caught.
_SYLLABUS = re.compile(
    r"^(?:Syllabus (?:of|by) the Court\.?"
    r"|Synopsis"
    r"|Attorneys and Law Firms"
    r"|Opinion)$")
_FOOTNOTES_HEAD = re.compile(r"^FOOTNOTES?$")
_FIGURE = re.compile(r"^\[Figure \d+")
# body opener, both notations: the `[nN]` corpus form and the legacy `N.`
_FN_BODY = re.compile(r"^(?:\[n(\d{1,3})\]|(\d{1,3})\.)\s")
_PARA = re.compile(r"\[¶\s?(\d+)\]")
_STAR = re.compile(r"\[\*(\d+)\]")
# Second-series star page in dual-paginated West texts. BRACKETED as of
# 2026-08-04 (JT: both series in square brackets) — the storage now matches
# what this renderer always displayed. The bare `**NNN` form is gone from the
# corpus; nothing should reintroduce it.
_STAR2 = re.compile(r"\[\*\*(\d{1,4})\]")
# Redline notation (JT 2026-08-17): where the court PRINTED a struck/underlined
# amendment — a quoted bill in session-law form, a rule-amendment order — the
# storage keeps both states in CriticMarkup: `{--struck--}` and `{++added++}`.
# The braces are collision-free in this corpus (0 hits before adoption); the
# renderer shows them as <del>/<ins>. Struck spans are the court's text too
# (an opinion may argue from the deleted words), so nothing is dropped.
_CRITIC_DEL = re.compile(r"\{--(.+?)--\}", re.S)
_CRITIC_INS = re.compile(r"\{\+\+(.+?)\+\+\}", re.S)
# Inline footnote CALL — the sigilled `[nN]` form only (JT 2026-08-04). The
# bare `[N]` must not be linked: treatise subdivisions (`§ 34.11[5]`),
# bracketed pages (`490 U.S. [163]`) and the courts' own enumerators
# ("described in [1] or [2]") share that shape, and linking them silently
# turned the court's own text into footnote references.
_FN_REF = re.compile(r"\[n(\d{1,3})\]")
# West italics: *span* where the span starts with a letter/quote/paren and
# contains a letter. (?<![\w*]) / (?![\w*]) keep ** star pages and ***
# omissions out; the no-digit start keeps "[*458] text [*463]" out.
# Closing star: the CL lineage often GLUES the close to the next word
# ("*Amegard v. Cayko,*2010 ND 83"), so a following word char is allowed;
# (?<!\[) keeps a [*N] star-page marker from serving as a fake closer,
# (?!\*) keeps ** pairs out, and the 250-char content cap keeps a
# mis-paired stray star from minting an absurd page-long "span"
# (italicized law-review titles, the longest genuine class, run ~160).
# `$` is in the opening class because emphasis legitimately begins with it:
# forfeiture case names (*State v. $33,000.00 U.S. Currency*) and appropriation
# amounts the court italicized (2018 ND 189 ¶ 29, archive `<em>$300,000 to an
# organization that provides workplace safety</em>`). 8 such spans across 4
# opinions rendered as literal asterisks until it was added. Digits stay OUT —
# a leading digit is a star page, not a span.
_ITAL = re.compile(
    r"(?<![\w*])\*(?=[^*\n]*[A-Za-z])"
    r"([A-Za-z(\"'‘“§$][^*\n]{0,250}?[^\s*]|[A-Za-z])(?<!\[)\*(?!\*)")


_BARE_ITAL_LINE = re.compile(r"^\*[^*\n]{1,80}\*[,.;:]?$")
_TERMINAL = re.compile(r"[.?!:;\"'’”)\]]$")


def _logical_lines(text: str) -> list[str]:
    """Rejoin space-indented continuation lines onto their predecessor.

    Tab-leading lines are Contract-7 block-quote paragraphs — never joined.
    A column-0 line that is a BARE italic span ("*may*") is a CL-lineage
    mid-sentence split: it joins the previous line when that line ends
    mid-sentence, and pulls the next line up when it starts lowercase.
    """
    out: list[str] = []
    pulled_span = False
    for raw in text.split("\n"):
        if (raw[:1] == " " and raw.strip()
                and out and out[-1].strip()):
            out[-1] = out[-1].rstrip() + " " + raw.strip()
            pulled_span = False
        elif (_BARE_ITAL_LINE.match(raw) and out and out[-1].strip()
                and not _TERMINAL.search(out[-1].rstrip())):
            out[-1] = out[-1].rstrip() + " " + raw.strip()
            pulled_span = True
        elif (pulled_span and raw[:1].isalpha() and raw[:1].islower()
                and out):
            out[-1] = out[-1].rstrip() + " " + raw.strip()
            pulled_span = False
        else:
            out.append(raw)
            pulled_span = False
    return out


# Separate-writing author line ("VANDE WALLE, Justice, concurring specially.",
# "LEVINE, Justice, dissenting.") — the boundary that ends a per-writing
# FOOTNOTES section (convention ratified by JT 2026-07-29: each writing keeps
# its own FOOTNOTES section, numbering as printed, placed at the end of that
# writing). Shared by the renderer and the section-lift tooling.
# `^ *` (spaces only, never tab): space-led separators exist in storage
# (134 sites, 2019–24 band) and must still read as boundaries; a tab-led
# author line is block-quoted text and must keep failing.
WRITING_SEP = re.compile("^ *" + proofread.WRITING_SEP_PAT)


# Top-level section numeral on its own line — "I", "II.", "XI". The corpus
# stores section furniture as bare lines in every era (census 2026-08-09:
# 4,576 opinions, zero heading forms), so heading-ness is a RENDER decision
# (JT 2026-08-14: renderer-side, storage untouched).
_ROMAN_LINE = re.compile(r"^(?=[IVX])(X{0,3})(IX|IV|V?I{0,3})\.?$")


def _roman_val(s: str) -> int:
    s = s.rstrip(".")
    vals = {"I": 1, "V": 5, "X": 10}
    total, prev = 0, 0
    for ch in reversed(s):
        v = vals[ch]
        total = total - v if v < prev else total + v
        prev = max(prev, v)
    return total


def _roman_section_heads(lines: list[str], sections) -> set[int]:
    """Line indexes to render as ``<h3 class="section">`` (JT 2026-08-14).

    Top-level Roman section numerals sit one level below the ``<h2>``
    byline. Promotion is deliberately strict — a missed heading renders as
    the plain ``<p>`` it always was, but a wrongly promoted enumerator
    would restyle the court's quoted material — so every gate errs toward
    NOT promoting:

    * modern-format opinions only (a ``[¶N]`` marker present). Pre-1997
      texts quote complaints and findings with column-0 Roman paragraph
      enumerators ("XI." / "That Defendant has not…"), the exact false
      positive; the modern band tab-indents quotes (Contract 7).
    * column 0 only — a tab-led numeral is inside a block quote.
    * outside FOOTNOTE sections.
    * strict arithmetic sequence from I within a writing segment
      (WRITING_SEP resets; a fresh "I" may also restart a run mid-segment,
      e.g. an appended rehearing), with at least two members — a lone "I"
      is as likely an OCR fragment as a heading. Sequences broken by a
      mis-stored sibling (census 2026-08-14: ~640 lines corpus-wide, the
      space-led/one-line storage defect queues) stay plain paragraphs and
      heal automatically as those storage repairs land.
    * one sequence exception (JT 2026-08-14, 2017 ND 152): a numeral
      EQUAL to the last accepted one — the court's own duplicate section
      heading, confirmed against the slip PDF — promotes too, but only
      when body content (a ``[¶N]`` line) still follows it. The census of
      the whole class is 18 lines: 15 are genuine duplicate headings
      flanked by body paragraphs; 3 are stray trailing numerals after the
      signature block at end-of-document (a storage artifact, not a
      heading), and the content-follows condition is exactly what
      separates them. ``expected`` does not advance on a duplicate, so a
      court that recovers its numbering afterward still sequences.
    """
    if not any("[¶" in ln for ln in lines):
        return set()
    fn_ranges = [(h, end) for h, _, end in sections]
    seg = 0
    seg_at: list[int] = []
    for raw in lines:
        if WRITING_SEP.match(raw):
            seg += 1
        seg_at.append(seg)
    cands: list[tuple[int, int]] = []          # (line_idx, numeral value)
    for i, raw in enumerate(lines):
        s = raw.strip()
        if (s and not raw.startswith("\t") and _ROMAN_LINE.match(s)
                and not any(h < i < e for h, e in fn_ranges)):
            cands.append((i, _roman_val(s)))
    def _body_follows(i: int) -> bool:
        sg = seg_at[i]
        for j in range(i + 1, len(lines)):
            if seg_at[j] != sg:
                return False
            if lines[j].lstrip().startswith("[¶"):
                return True
        return False

    expected: dict[int, int] = {}
    last: dict[int, int] = {}                  # segment -> last accepted value
    ok: dict[int, int] = {}                    # line_idx -> segment
    for i, v in cands:
        sg = seg_at[i]
        if v == 1:
            expected[sg] = 2
            last[sg] = 1
            ok[i] = sg
        elif expected.get(sg) == v:
            expected[sg] = v + 1
            last[sg] = v
            ok[i] = sg
        elif last.get(sg) == v and _body_follows(i):
            ok[i] = sg                         # duplicate heading; expected stays
    per_seg: dict[int, int] = {}
    for sg in ok.values():
        per_seg[sg] = per_seg.get(sg, 0) + 1
    return {i for i, sg in ok.items() if per_seg[sg] >= 2}


def _collect_footnote_sections(lines: list[str]):
    """``[(head_idx, nums, end_idx)]`` for every FOOTNOTES heading.

    A section's region runs from its heading to the next separate-writing
    author line (per-writing sections, JT 2026-07-29) or the next heading /
    end of document. Numbers are the ``N.`` body openers inside the region.
    """
    heads = [i for i, ln in enumerate(lines)
             if _FOOTNOTES_HEAD.match(ln.strip())]
    sections = []
    for k, h in enumerate(heads):
        limit = heads[k + 1] if k + 1 < len(heads) else len(lines)
        end = limit
        for j in range(h + 1, limit):
            # a following writing ends the section — byline form, or the
            # signature-form concurrence ("I concur in the result." + name)
            # that WRITING_SEP cannot see (JT web review 2026-08-06)
            if WRITING_SEP.match(lines[j]) or re.match(
                    r"I (?:respectfully )?(?:concur|dissent)",
                    lines[j].strip()):
                end = j
                break
        nums = {(m.group(1) or m.group(2)) for ln2 in lines[h + 1:end]
                if (m := _FN_BODY.match(ln2.strip()))}
        sections.append((h, nums, end))
    return sections


_TABLE_ANCHOR = re.compile(r"^\[Table \d+\]$")
_DASH_RULE = re.compile(r"^-{3,}(\s+-+)*\s*$")


def _extract_table_blocks(text: str):
    """Pull ``[Table N]`` + monospace block out before line-joining.

    The block is the anchor line plus following non-blank lines; a single
    blank line continues the block only in the title pattern (title, blank,
    header, dash rule). Right-aligned cells give the block leading-space
    lines that ``_logical_lines`` would otherwise merge away.
    """
    lines = text.split("\n")
    blocks: list[str] = []
    out: list[str] = []
    i = 0
    while i < len(lines):
        if not _TABLE_ANCHOR.match(lines[i].strip()):
            out.append(lines[i])
            i += 1
            continue
        blk = [lines[i]]
        j = i + 1
        while j < len(lines):
            if lines[j].strip():
                blk.append(lines[j])
                j += 1
                continue
            nxt = lines[j + 1].strip() if j + 1 < len(lines) else ""
            nxt2 = lines[j + 2].strip() if j + 2 < len(lines) else ""
            if nxt and (_DASH_RULE.match(nxt) or _DASH_RULE.match(nxt2)
                        # headerless title pattern (2026-08-17): title, blank,
                        # then rows with two-space column gaps and no rule
                        or (len(blk) == 2 and re.search(r"\S {2,}\S", nxt))):
                blk.append(lines[j])
                j += 1
                continue
            break
        blocks.append("\n".join(blk))
        out.append(f"\x00TBL{len(blocks) - 1}\x00")
        i = j
    return "\n".join(out), blocks


def render_body(text: str) -> str:
    """Escape-then-transform ``text_content`` into fidelity-first HTML."""
    text, tbl_blocks = _extract_table_blocks(text)
    lines = _logical_lines(text)
    sections = _collect_footnote_sections(lines)
    head_idxs = {h for h, _, _ in sections}
    roman_heads = _roman_section_heads(lines, sections)

    # Headingless opinions (the 2026-08-05 witness batches) carry `[nN]`
    # definitions with no FOOTNOTES heading to section them. When no heading
    # exists, every line-leading `[nN]` label is a definition anchor and the
    # inline calls link to it (JT 2026-08-05) — first occurrence per number
    # wins, matching the sectioned path's duplicate discipline.
    headless_defs: dict[str, int] = {}
    if not sections:
        for i, ln in enumerate(lines):
            if ln.startswith("\t"):
                continue  # tab-opened = quoted material, never a def anchor
            m = re.match(r"\[n(\d{1,3})\]\s", ln.strip())
            if m and m.group(1) not in headless_defs:
                headless_defs[m.group(1)] = i

    # A body may span several paragraphs (quoted policy text, a./b. lists):
    # every line from one opener to the next keeps the fn styling and the ↩
    # back-link sits on the body's LAST paragraph (JT 2026-08-05).
    # {line_idx: (kind, n, is_last)} for the headingless path.
    headless_rng: dict[int, tuple[str, str, bool]] = {}
    if headless_defs:
        order = sorted((i, n) for n, i in headless_defs.items())
        for k, (i, n) in enumerate(order):
            end = order[k + 1][0] if k + 1 < len(order) else len(lines)
            # Contract 9 places defs at the end of their WRITING, so a
            # following separate writing (byline or signature-form
            # concurrence) is NOT def-body continuation — 10 fleet opinions
            # carry one (the 2021 ND 228 ↩ landed after "I concur in the
            # result. Gerald W. VandeWalle"; JT web review 2026-08-06)
            for j in range(i + 1, end):
                s = lines[j].strip()
                # a [¶N] body paragraph is never definition continuation
                # either — 1999 ND 150 stores its ¶30 signature panel AFTER
                # the defs, and the fn2 body swallowed it plus the following
                # label line, parking the ↩ on "Concurrence" (JT web review
                # 2026-08-14)
                if (WRITING_SEP.match(lines[j])
                        or re.match(r"I (?:respectfully )?(?:concur|dissent)", s)
                        or re.match(r"\[¶\d+\]", s)):
                    end = j
                    break
            last_nb = max((j for j in range(i, end) if lines[j].strip()),
                          default=i)
            headless_rng[i] = ("open", n, last_nb == i)
            for j in range(i + 1, end):
                headless_rng[j] = ("cont", n, j == last_nb)

    # sectioned-path body ranges, same one-opener-to-the-next rule
    sec_rng: dict[int, tuple[str, int, str, bool]] = {}
    for k, (h, nums, end) in enumerate(sections):
        openers: list[tuple[int, str]] = []
        seen_nums: set[str] = set()
        for i2 in range(h + 1, end):
            if lines[i2].startswith("\t"):
                # tab-opened = quoted material inside a def body (Wold's
                # fn5 committee list), never a def opener — stripping the
                # tab made inner list numbers steal the anchors from the
                # real defs below (JT web review 2026-08-06)
                continue
            bm2 = _FN_BODY.match(lines[i2].strip())
            if bm2:
                n2 = bm2.group(1) or bm2.group(2)
                if n2 in nums and n2 not in seen_nums:
                    seen_nums.add(n2)
                    openers.append((i2, n2))
        for j2, (i2, n2) in enumerate(openers):
            bend = openers[j2 + 1][0] if j2 + 1 < len(openers) else end
            last_nb = max((j3 for j3 in range(i2, bend) if lines[j3].strip()),
                          default=i2)
            sec_rng[i2] = ("open", k, n2, last_nb == i2)
            for j3 in range(i2 + 1, bend):
                sec_rng[j3] = ("cont", k, n2, j3 == last_nb)

    def sec_prefix(k: int) -> str:
        # section 1 keeps the legacy unsuffixed ids (#fn1); later writings'
        # sections are namespaced (#fn2-1)
        return "" if k == 0 else f"{k + 1}-"

    def ref_section(i: int, n: str) -> int | None:
        """Section a ``[n]`` ref at line ``i`` resolves to: its own region's
        section if inside one, else the first following section carrying n."""
        for k, (h, nums, end) in enumerate(sections):
            if h < i < end and n in nums:
                return k
            if h > i and n in nums:
                return k
        return None

    seen_para: set[str] = set()
    seen_star: set[str] = set()
    seen_star2: set[str] = set()
    seen_ref: set[tuple[int, str]] = set()
    seen_fn: set[tuple[int, str]] = set()
    out: list[str] = ['<div class="body">']
    quote_depth = 0

    def set_quote_depth(want: int):
        """Open/close <blockquote> so the nesting matches the leading-tab count.

        Contract 7 stores one tab per quote level, and a quotation that quotes
        something further in — a statute's lettered subdivisions, an opinion
        quoting a record that quotes a rule — carries two or three. Rendering
        every depth as one flat <blockquote> loses the structure the court set:
        2021 ND 190 ¶7 prints its N.D.C.C. 30.1-19-03(2) body at one level and
        its `a.`/`b.` items at the next (JT, 2026-08-09).
        """
        nonlocal quote_depth
        while quote_depth < want:
            out.append("<blockquote>")
            quote_depth += 1
        while quote_depth > want:
            out.append("</blockquote>")
            quote_depth -= 1

    def close_quote():
        set_quote_depth(0)

    for i, raw in enumerate(lines):
        stripped = raw.strip()
        if not stripped:
            continue
        # Contract 7: tab-leading paragraph = block quote; consecutive quote
        # paragraphs (blank lines between) group into one <blockquote>, and a
        # deeper tab run nests inside the level above it.
        depth = len(raw) - len(raw.lstrip("\t"))
        is_quote = depth > 0
        set_quote_depth(depth)
        esc = html.escape(raw.lstrip("\t") if is_quote else raw, quote=False)

        m = _MD_HEAD.match(stripped)
        if m and m.group(1) in _H2_LABELS:
            out.append(f"<h2>{html.escape(m.group(1))}</h2>")
            continue
        if _SYLLABUS.match(stripped):
            out.append(f"<h2>{html.escape(stripped)}</h2>")
            continue
        if i in head_idxs:
            out.append(f"<h2>{html.escape(stripped)}</h2>")
            continue
        if i in roman_heads:
            # top-level section numeral, one level below the byline <h2>
            out.append(f'<h3 class="section">{html.escape(stripped)}</h3>')
            continue
        if _FIGURE.match(stripped):
            out.append(f'<p class="figure">{esc}</p>')
            continue
        tm = re.fullmatch(r"\x00TBL(\d+)\x00", stripped)
        if tm:
            blk = tbl_blocks[int(tm.group(1))]
            anchor, _, body_blk = blk.partition("\n")
            # the [Table N] line is OUR anchor (tables.db key), not the
            # court's text — never display it (JT 2026-07-29); it survives
            # only as the element id for deep links
            am = re.search(r"\d+", anchor)
            aid = f' id="table{am.group(0)}"' if am else ""
            out.append(f'<pre class="tbl"{aid}>{html.escape(body_blk)}</pre>')
            continue

        in_sec = next((k for k, (h, _, end) in enumerate(sections)
                       if h < i < end), None)

        def para_sub(m: re.Match) -> str:
            n = m.group(1)
            if n in seen_para:
                return m.group(0)
            seen_para.add(n)
            return (f'<a class="pm" id="p{n}" href="#p{n}">'
                    f"[¶{n}]</a>")

        def star_sub(m: re.Match) -> str:
            n = m.group(1)
            if n in seen_star:
                return f'<span class="star">[*{n}]</span>'
            seen_star.add(n)
            return f'<span class="star" id="star{n}">[*{n}]</span>'

        def star2_sub(m: re.Match) -> str:
            # stored and displayed bracketed (JT 2026-08-04)
            n = m.group(1)
            if n in seen_star2:
                return f'<span class="star">[**{n}]</span>'
            seen_star2.add(n)
            return f'<span class="star" id="star2-{n}">[**{n}]</span>'

        # CL splits a case name and its trailing punctuation into two
        # ADJACENT spans ("*Serr**,*at ¶ 12"): close+open collapse into
        # one span, and the print-space returns after it
        esc = re.sub(r"(?<=\S)\*\*([,.;:])\*\s*", r"\1* ", esc)

        def _ital_sub(m):
            # glued close ("*Cayko,*2010") gets its print-space back
            nxt = m.string[m.end():m.end() + 1]
            sp = " " if (nxt.isalnum() or nxt == "(") else ""
            return f"<em>{m.group(1)}</em>{sp}"
        esc = _ITAL.sub(_ital_sub, esc)
        esc = _CRITIC_DEL.sub(r'<del class="redline">\1</del>', esc)
        esc = _CRITIC_INS.sub(r'<ins class="redline">\1</ins>', esc)
        esc = _PARA.sub(para_sub, esc)
        esc = _STAR.sub(star_sub, esc)
        esc = _STAR2.sub(star2_sub, esc)

        # separate-writing byline ("LEVINE, Justice, dissenting.",
        # "ERICKSTAD, Chief Justice.", star-page-prefixed forms) renders as
        # a heading (JT 2026-07-29) — after the marker substitutions so a
        # leading [*N] keeps its anchor
        if WRITING_SEP.match(raw):
            out.append(f'<h2 class="byline">{esc.lstrip(" ")}</h2>')
            continue

        if in_sec is not None:
            rng = sec_rng.get(i)
            if rng:
                kind, sk, n, last = rng
                pre = sec_prefix(sk)
                back = (f' <a href="#fnref{pre}{n}">↩</a>'
                        if last and (sk, n) in seen_ref else "")
                if kind == "open":
                    seen_fn.add((sk, n))
                    # strip the stored label — the renderer supplies its own
                    # "N." Both notations: `[nN]` and the legacy `N.`
                    lbl = f"[n{n}]"
                    cut = esc.find(lbl)
                    if cut >= 0:
                        body_esc = esc[cut + len(lbl):]
                    else:
                        cut = esc.find(f"{n}.")
                        body_esc = esc[cut + len(n) + 1:] if cut >= 0 else esc
                    out.append(f'<p class="fn" id="fn{pre}{n}"><b>{n}.</b>'
                               f"{body_esc}{back}</p>")
                else:
                    # continuation paragraph of a multi-paragraph body
                    out.append(f'<p class="fn">{esc}{back}</p>')
                continue
        elif sections:
            def ref_sub(m: re.Match) -> str:
                n = m.group(1)
                k = ref_section(i, n)
                if k is None:
                    return m.group(0)
                pre = sec_prefix(k)
                anchor = ("" if (k, n) in seen_ref
                          else f' id="fnref{pre}{n}"')
                seen_ref.add((k, n))
                return (f'<a class="fn-ref"{anchor} href="#fn{pre}{n}">'
                        f"<sup>[{n}]</sup></a>")
            esc = _FN_REF.sub(ref_sub, esc)
        elif headless_defs:
            rng = headless_rng.get(i)
            if rng:
                kind, n, last = rng
                back = (f' <a href="#fnref{n}">↩</a>'
                        if last and ("h", n) in seen_ref else "")
                if kind == "open":
                    # definition opener: anchor + renderer-supplied label
                    lbl = f"[n{n}]"
                    cut = esc.find(lbl)
                    body_esc = esc[cut + len(lbl):] if cut >= 0 else esc
                    out.append(f'<p class="fn" id="fn{n}"><b>{n}.</b>'
                               f"{body_esc}{back}</p>")
                else:
                    # continuation paragraph of a multi-paragraph body
                    out.append(f'<p class="fn">{esc}{back}</p>')
                continue

            def href_sub(m: re.Match) -> str:
                n = m.group(1)
                if n not in headless_defs or headless_defs[n] <= i:
                    return m.group(0)   # no def below to land on
                anchor = ("" if ("h", n) in seen_ref
                          else f' id="fnref{n}"')
                seen_ref.add(("h", n))
                return (f'<a class="fn-ref"{anchor} href="#fn{n}">'
                        f"<sup>[{n}]</sup></a>")
            esc = _FN_REF.sub(href_sub, esc)

        # Any `[nN]` still standing is a footnote this renderer cannot link —
        # a legacy-form or duplicate site. Display it the way the pre-notation
        # text read rather than leaking the sigil: a line-leading label
        # becomes "N.", an inline call a bare superscript.
        esc = re.sub(r"^\[n(\d{1,3})\](\s)", r"<b>\1.</b>\2", esc)
        esc = _FN_REF.sub(lambda m: f"<sup>[{m.group(1)}]</sup>", esc)

        out.append(f"<p>{esc}</p>")

    close_quote()
    out.append("</div>")
    return "\n".join(out)


_BOLD = re.compile(r"\*\*([^*\n]+)\*\*")


def render_provision_body(text: str, *, anchors: bool = False) -> str:
    """Provision text -> HTML. The rules corpus stores markdown-lite:
    ``**bold**`` subdivision labels and ``> ``/``> > `` indent levels
    (N.D.C.C./N.D.A.C. text is plain and passes through unchanged).
    Escape first; then only the closed grammar transforms.

    ``anchors=True`` (rules corpus only) stamps each subdivision paragraph
    with a stable id derived from its pincite path — ``id="e-1"`` for
    Rule X(e)(1) — and makes the printed label a self-link, so
    ``/ndrcivp56#e-1`` scrolls to the subsection. Ids come from
    ``rule_subsections.anchor_map``, which anchors nothing unless the
    whole version parses clean (a wrong anchor is worse than none)."""
    amap = rule_subsections.anchor_map(text) if anchors else {}
    out = []
    for idx, ln in enumerate(text.split("\n")):
        if not ln.strip():
            continue
        depth = 0
        while ln.startswith("> ") or ln == ">":
            depth += 1
            ln = ln[2:] if ln.startswith("> ") else ""
        esc = html.escape(ln.strip())
        esc = _BOLD.sub(r"<strong>\1</strong>", esc)
        aid = ""
        a = amap.get(idx)
        if a:
            aid = f' id="{a}"'
            # the paragraph's leading printed label becomes its self-link;
            # first occurrence only, and the label text is escape-inert
            label = f"({a.rsplit('-', 1)[-1]})"
            for cand in (label, label.upper()):
                pos = esc.find(cand)
                if pos >= 0:
                    esc = (esc[:pos]
                           + f'<a class="pm" href="#{a}">{cand}</a>'
                           + esc[pos + len(cand):])
                    break
        cls = f' class="ind{min(depth, 4)}"' if depth else ""
        out.append(f"<p{cls}{aid}>{esc}</p>")
    return "".join(out)
