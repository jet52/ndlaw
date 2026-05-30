#!/usr/bin/env python3
"""Shared helpers for the paragraph-marker re-OCR pipeline (§ TODO #4).

normalize_marker_md(): marker .md -> clean opinion text for text_content
  (strip ## headings, '- ' list prefixes before [¶N], markdown escapes/emphasis,
   rejoin page-split paragraphs). The SAME normalized text is what we validate
   against Westlaw and what we write, so the comparison is honest.

westlaw_body() / marker_body(): the opinion body (from first [¶N] onward, with
  Westlaw's editorial synopsis/headnotes/trailing matter removed), markers
  stripped, tokenized for word-for-word comparison.
"""
import re

_MARKER = re.compile(r"\[¶\s*(\d+)\]")
# Westlaw body markers vary by doc, each using ONE distinctive form:
#   bracketed '[¶1]' (most), curly '{ ¶1}' (e.g. 2022 ND 183), or bare line-start
#   '¶1'. Bracket/curly are self-delimiting (pincites are plain '¶ 6'); the bare
#   form is line-anchored so mid-line pincites are never counted.
_WL_BRACKET = re.compile(r"\[¶\s*(\d+)\]")
_WL_CURLY = re.compile(r"\{\s*¶\s*(\d+)\s*\}?")
_WL_BARE = re.compile(r"(?m)^[ \t\xa0]*¶[ \t]*(\d+)")
_WL_FORMS = (_WL_BRACKET, _WL_CURLY, _WL_BARE)
_ANY_PARA = re.compile(r"[\[{]?\s*¶\s*\d+\s*[\]}]?")
_WL_TAIL = re.compile(r"\n(?:All Citations|End of Document)\b")

# Greek/Cyrillic homoglyphs the OCR substitutes for Latin letters (ND opinions
# never contain Greek/Cyrillic, so mapping these lookalikes to Latin is safe and
# repairs genuine OCR errors — e.g. Roman numeral 'I'/'i' read as iota).
_HOMOGLYPHS = str.maketrans({
    "ι": "i", "Ι": "I", "ο": "o", "Ο": "O", "α": "a", "Α": "A", "ν": "v",
    "Ν": "N", "ρ": "p", "Ρ": "P", "ε": "e", "Ε": "E", "τ": "t", "Τ": "T",
    "Χ": "X", "χ": "x", "Υ": "Y", "Κ": "K", "Μ": "M", "Η": "H", "Β": "B",
    "Ζ": "Z", "‚": ",", "А": "A", "В": "B", "С": "C", "Е": "E", "Н": "H",
    "К": "K", "М": "M", "О": "O", "Р": "P", "Т": "T", "Х": "X", "е": "e",
    "о": "o", "с": "c", "р": "p", "х": "x", "а": "a",
})


def fix_homoglyphs(s: str) -> str:
    return s.translate(_HOMOGLYPHS)


def normalize_marker_md(md: str) -> str:
    md = fix_homoglyphs(md)
    md = md.replace("\\$", "$")   # unescape markdown '\$' first so pilcrow forms
    #                               like '[\$\quad 25\$]' canonicalize below
    md = md.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")  # decode entities
    # Canonicalize OCR/markdown pilcrow variants to '[¶N]'. Marker renders ¶ as a
    # LaTeX command in math mode, and which command varies by paragraph:
    # '[ $\P$ 21]', '[ $\P6$ ]', '[$\quad 25$]'. Target the known pilcrow commands
    # (\P, \quad) only — a broad '$ or \' rule wrongly catches escaped dollar
    # amounts and other bracketed math.
    md = re.sub(r"\[\s*\$?\\(?:P|quad)\$?\s*(\d+)\s*\$?\s*\]", r"[¶\1]", md)
    # Strip marker's HTML/LaTeX markup so it doesn't leak into text_content:
    md = re.sub(r"<br\s*/?>", " ", md)                          # line-break tags -> space
    md = re.sub(r"</?(?:su[bp]|b|u|i|em|strong|del|ins|mark|small|span|math)\s*/?>", "", md)  # strip formatting tags, keep content
    md = re.sub(r"\\frac\{(\d+)\}\{(\d+)\}", r"\1/\2", md)      # \frac{1}{4} -> 1/4
    md = re.sub(r"\\(?:math[a-z]*|text[a-z]*|bf|it|rm)\{([^}]*)\}", r"\1", md)  # \mathbf{x} -> x
    md = re.sub(r"\$\\[a-zA-Z]+\$", "", md)                      # stray \cmd in math
    md = re.sub(r"(?<![A-Za-z])\\[a-zA-Z]+(?![A-Za-z])", "", md)  # bare \command leakage
    lines = []
    for ln in md.splitlines():
        s = ln.rstrip()
        # Flatten markdown tables marker emits for caption/columnar layouts:
        # drop separator rows, join a row's non-empty cells into plain text.
        if re.match(r"^\s*\|[\s:|-]+\|?\s*$", s):
            continue
        if re.match(r"^\s*\|.*\|\s*$", s):
            cells = [c.strip() for c in s.strip().strip("|").split("|")]
            s = " ".join(c for c in cells if c)
        s = re.sub(r"^#{1,6}\s+", "", s)               # drop heading hashes
        s = re.sub(r"^-\s+(?=\[¶)", "", s)             # '- [¶4]' -> '[¶4]'
        s = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", s)      # drop image refs
        s = s.replace("\\$", "$").replace("\\&", "&").replace("\\.", ".")
        s = re.sub(r"\*(\w[^*]*?)\*", r"\1", s)         # de-emphasize *Id*
        lines.append(s)
    text = "\n".join(lines)
    # Promote bare line-start [N] markers (OCR dropped the ¶ glyph for that one
    # paragraph — marker emits '[9]' instead of '[¶9]') ONLY when N fills a gap
    # in the 1..max paragraph sequence. The sequence + boundary constraint keeps
    # a stray bracketed footnote ref from being mistaken for a marker.
    nums = [int(m.group(1)) for m in re.finditer(r"\[¶\s*(\d+)\]", text)]
    if nums:
        present = set(nums)
        for g in range(1, max(nums) + 1):
            if g not in present:
                text, k = re.subn(rf"(?m)^\s*-?\s*\[{g}\]", f"[¶{g}]", text, count=1)
                if k:
                    present.add(g)
    # Rejoin paragraphs: a paragraph runs from one [¶N] to the next; collapse the
    # internal blank lines marker introduces at page breaks.
    parts = re.split(r"(\n*\[¶\s*\d+\])", text)
    out, buf = [], parts[0].strip()
    if buf:
        out.append(buf)
    for i in range(1, len(parts), 2):
        marker = parts[i].strip()
        body = parts[i + 1] if i + 1 < len(parts) else ""
        body = re.sub(r"\s*\n\s*\n\s*", " ", body)      # join page-split lines
        body = re.sub(r"[ \t]+", " ", body).strip()
        out.append(f"{marker} {body}")
    return "\n\n".join(out).strip() + "\n"


def markers(text: str) -> list[int]:
    return [int(m.group(1)) for m in _MARKER.finditer(text)]


def seq_ok(nums: list[int]) -> bool:
    """True iff markers are exactly 1..N once each, in order."""
    return bool(nums) and nums == list(range(1, len(nums) + 1))


def _body_from_first_marker(text: str) -> str:
    m = _MARKER.search(text)
    return text[m.start():] if m else text


def westlaw_markers(wl_body: str) -> list[int]:
    for pat in _WL_FORMS:
        ms = [int(m.group(1)) for m in pat.finditer(wl_body)]
        if ms:
            return ms
    return []


def westlaw_body(wl_txt: str) -> str:
    m = next((mm for p in _WL_FORMS for mm in [p.search(wl_txt)] if mm), None)
    body = wl_txt[m.start():] if m else wl_txt
    cut = _WL_TAIL.search(body)
    if cut:
        body = body[:cut.start()]
    return body


def marker_body(norm_md: str) -> str:
    return _body_from_first_marker(norm_md)


_TOKEN = re.compile(r"\w+")


def tokenize(body: str) -> list[str]:
    """Lowercased word tokens for comparison: paragraph markers and Westlaw
    inline star-pagination (*549) removed (the court PDF has no star-pages)."""
    body = _ANY_PARA.sub(" ", body)        # strip [¶N] and bare ¶N (both forms)
    body = re.sub(r"\*\d+", " ", body)      # strip Westlaw star-pagination
    return _TOKEN.findall(body.lower())


def nw_parallel_from_westlaw(wl_txt: str) -> str | None:
    """Recover the N.W. reporter parallel cite from the Westlaw 'All Citations'."""
    m = re.search(r"All Citations\s*\n([^\n]+)", wl_txt)
    if not m:
        return None
    nw = re.search(r"\d+\s+N\.W\.\s?\d?d?\s+\d+", m.group(1))
    return nw.group(0) if nw else None
