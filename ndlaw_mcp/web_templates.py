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
- ``Syllabus by the Court`` → ``<h2>``.
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

from ndlaw_mcp import proofread

# ---------------------------------------------------------------------------
# page shell
# ---------------------------------------------------------------------------

_STYLE = """
  body { font-family: Georgia, 'Times New Roman', serif; max-width: 46rem;
         margin: 2.5rem auto; padding: 0 1.25rem; line-height: 1.55; color: #1a1a1a; }
  h1 { font-size: 1.35rem; margin-bottom: .2rem; line-height: 1.3; }
  h2 { font-size: 1.1rem; margin-top: 1.8rem; }
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
         official_url: str | None = None) -> str:
    """Wrap ``body`` (already-safe HTML) in the shared page shell."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{html.escape(title)}</title>
<style>{_STYLE}</style>
</head>
<body>
{f'<h1>{html.escape(h1)}</h1>' if h1 else ''}
{body}
<footer>{disclaimer_html(official_url)}</footer>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# opinion-body renderer
# ---------------------------------------------------------------------------

_H2_LABELS = {"Concurrence", "Dissent", "On Rehearing", "Concurrence in Part"}
_MD_HEAD = re.compile(r"^##\s*(.+?)\s*$")
_SYLLABUS = re.compile(r"^Syllabus by the Court\.?$")
_FOOTNOTES_HEAD = re.compile(r"^FOOTNOTES?$")
_FIGURE = re.compile(r"^\[Figure \d+")
_FN_BODY = re.compile(r"^(\d{1,3})\.\s")
_PARA = re.compile(r"\[¶\s?(\d+)\]")
_STAR = re.compile(r"\[\*(\d+)\]")
# second-series star pages in dual-paginated West texts (**846 = the N.W.
# page where [*747] is the N.D. page) — bare by corpus convention (only the
# ambiguous single-star series was bracketed). Styled like [*N], own anchor
# namespace. (?<![\w*]) keeps *** omissions out; (?![\d*]) bounds the number.
_STAR2 = re.compile(r"(?<![\w*])\*\*(\d{1,4})(?![\d*])")
_FN_REF = re.compile(r"\[(\d{1,3})\]")
# West italics: *span* where the span starts with a letter/quote/paren and
# contains a letter. (?<![\w*]) / (?![\w*]) keep ** star pages and ***
# omissions out; the no-digit start keeps "[*458] text [*463]" out.
# Closing star: the CL lineage often GLUES the close to the next word
# ("*Amegard v. Cayko,*2010 ND 83"), so a following word char is allowed;
# (?<!\[) keeps a [*N] star-page marker from serving as a fake closer,
# (?!\*) keeps ** pairs out, and the 250-char content cap keeps a
# mis-paired stray star from minting an absurd page-long "span"
# (italicized law-review titles, the longest genuine class, run ~160).
_ITAL = re.compile(
    r"(?<![\w*])\*(?=[^*\n]*[A-Za-z])"
    r"([A-Za-z(\"'‘“§][^*\n]{0,250}?[^\s*]|[A-Za-z])(?<!\[)\*(?!\*)")


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
WRITING_SEP = re.compile("^" + proofread.WRITING_SEP_PAT)


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
            if WRITING_SEP.match(lines[j]):
                end = j
                break
        nums = {m.group(1) for ln2 in lines[h + 1:end]
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
            if nxt and (_DASH_RULE.match(nxt) or _DASH_RULE.match(nxt2)):
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
    in_quote = False

    def close_quote():
        nonlocal in_quote
        if in_quote:
            out.append("</blockquote>")
            in_quote = False

    for i, raw in enumerate(lines):
        stripped = raw.strip()
        if not stripped:
            continue
        # Contract 7: tab-leading paragraph = block quote; consecutive quote
        # paragraphs (blank lines between) group into one <blockquote>
        is_quote = raw.startswith("\t")
        if is_quote and not in_quote:
            out.append("<blockquote>")
            in_quote = True
        elif not is_quote:
            close_quote()
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
            # displayed bracketed like [*N] (JT 2026-07-28); the brackets are
            # display-layer only — the stored text keeps the bare **N form
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
        esc = _PARA.sub(para_sub, esc)
        esc = _STAR.sub(star_sub, esc)
        esc = _STAR2.sub(star2_sub, esc)

        # separate-writing byline ("LEVINE, Justice, dissenting.",
        # "ERICKSTAD, Chief Justice.", star-page-prefixed forms) renders as
        # a heading (JT 2026-07-29) — after the marker substitutions so a
        # leading [*N] keeps its anchor
        if WRITING_SEP.match(raw):
            out.append(f'<h2 class="byline">{esc}</h2>')
            continue

        if in_sec is not None:
            bm = _FN_BODY.match(stripped)
            n = bm.group(1) if bm else None
            if (n and n in sections[in_sec][1]
                    and (in_sec, n) not in seen_fn):
                seen_fn.add((in_sec, n))
                pre = sec_prefix(in_sec)
                cut = esc.find(f"{n}.")
                body_esc = esc[cut + len(n) + 1:] if cut >= 0 else esc
                back = (f'<a href="#fnref{pre}{n}">↩</a> '
                        if (in_sec, n) in seen_ref else "")
                out.append(f'<p class="fn" id="fn{pre}{n}"><b>{n}.</b>'
                           f"{body_esc} {back}</p>")
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

        out.append(f"<p>{esc}</p>")

    close_quote()
    out.append("</div>")
    return "\n".join(out)


_BOLD = re.compile(r"\*\*([^*\n]+)\*\*")


def render_provision_body(text: str) -> str:
    """Provision text -> HTML. The rules corpus stores markdown-lite:
    ``**bold**`` subdivision labels and ``> ``/``> > `` indent levels
    (N.D.C.C./N.D.A.C. text is plain and passes through unchanged).
    Escape first; then only the closed grammar transforms."""
    out = []
    for ln in text.split("\n"):
        if not ln.strip():
            continue
        depth = 0
        while ln.startswith("> ") or ln == ">":
            depth += 1
            ln = ln[2:] if ln.startswith("> ") else ""
        esc = html.escape(ln.strip())
        esc = _BOLD.sub(r"<strong>\1</strong>", esc)
        cls = f' class="ind{min(depth, 4)}"' if depth else ""
        out.append(f"<p{cls}>{esc}</p>")
    return "".join(out)
