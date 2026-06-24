"""Authoritative footnote extraction from Westlaw N.D. Reports ``.doc`` files.

The ``.doc`` files under ``~/refs/nd/opin/N.W.2d/<vol>/<page>-<slug>.doc`` are
actually **RTF**, and Westlaw encodes footnotes as bookmarked table rows, not as
the flat ``N\\nbody`` text that the old textutil heuristic guessed at (which
over-counted badly — e.g. 1893 ND 17 "36" footnotes that don't exist).

Each footnote is one 2-cell table row:

    {\\*\\bkmkstart co_footnote_B00111975119675_52}{\\*\\bkmkend ...}
    {\\field ... HYPERLINK "#co_fnRef_..."}{\\fldrslt {\\super ... 1 }...}}   <- number cell
    \\par ... \\cell \\intbl                                                  <- end number cell
    { ... <BODY TEXT> \\par }                                                 <- body cell
    ... \\cell \\row                                                          <- end body cell / row

``extract_westdoc_rtf(path)`` returns ``{num: body_text}`` using the bookmark
set as the authoritative footnote count and the body cell as the verbatim text.
"""
import re
import sys

# one footnote row: bkmkstart, then everything up to the row terminator
_FN_ROW = re.compile(
    r"\\\*\\bkmkstart (co_footnote_B\d+_\d+)\}(.*?)\\row", re.DOTALL)
# the footnote number sits on its own line inside the \super run; control words
# like \b0 \fs20 carry digits, so anchor on the standalone-line form.
_SUPER_NUM = re.compile(r"\\super\b.*?(?:^|\n)\s*(\d{1,3})\s*(?:\n|$)", re.DOTALL | re.MULTILINE)
_CTRL = re.compile(r"\\([a-zA-Z]+)(-?\d+)? ?")
_HEX = re.compile(r"\\'([0-9a-fA-F]{2})")
_UNI = re.compile(r"\\u(-?\d+) ?\??")


def _rtf_text(s: str) -> str:
    """Strip RTF control words/groups from a fragment, return literal text."""
    # drop whole destination groups we never want as text
    s = re.sub(r"\{\\\*\\bkmk(?:start|end)[^}]*\}", " ", s)
    s = re.sub(r"\{\\field.*?\{\\fldrslt", " ", s, flags=re.DOTALL)
    s = re.sub(r"\\fldinst[^}]*\}", " ", s)
    s = _UNI.sub(lambda m: chr(int(m.group(1)) % 65536), s)
    s = _HEX.sub(lambda m: bytes([int(m.group(1), 16)]).decode("cp1252", "replace"), s)
    s = s.replace("\\par", " ").replace("\\line", " ").replace("\\tab", " ")
    s = s.replace("\\cell", " ")
    # literal escaped braces/backslash before stripping grouping braces
    s = s.replace("\\{", "\x01").replace("\\}", "\x02").replace("\\\\", "\x03")
    s = _CTRL.sub("", s)              # remaining control words
    s = s.replace("{", " ").replace("}", " ")
    s = s.replace("\x01", "{").replace("\x02", "}").replace("\x03", "\\")
    return re.sub(r"\s+", " ", s).strip()


def extract_westdoc_rtf(path: str) -> dict:
    """-> {footnote_num: body_text} from a Westlaw RTF .doc, or {} if none."""
    try:
        raw = open(path, "rb").read().decode("latin-1", "ignore")
    except OSError:
        return {}
    out = {}
    for m in _FN_ROW.finditer(raw):
        body_region = m.group(2)
        # number: the \super digit in the number cell (before the first \cell).
        # The Westlaw bookmark-id encoding of the number is INCONSISTENT across
        # docs (B0011=fn1 here, B0001=fn1 there), so the visible superscript is
        # the reliable source.
        sm = _SUPER_NUM.search(body_region.split("\\cell", 1)[0])
        if not sm:
            continue
        num = int(sm.group(1))
        # body: the cell after the number cell
        parts = body_region.split("\\cell")
        body = _rtf_text(parts[1]) if len(parts) > 1 else ""
        if 1 <= num <= 99 and body and num not in out:
            out[num] = body
    return out


if __name__ == "__main__":
    for p in sys.argv[1:]:
        fns = extract_westdoc_rtf(p)
        print(f"\n{p}\n  {len(fns)} footnotes: {sorted(fns)}")
        for n in sorted(fns):
            print(f"  [{n}] {fns[n][:140]}")
