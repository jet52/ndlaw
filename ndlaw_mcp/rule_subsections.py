"""Subdivision structure for the rules corpus's markdown-lite text.

The rules corpus stores whole rules whose text follows a closed grammar
(the same one ``web_templates.render_provision_body`` renders): paragraphs
separated by newlines, ``> `` prefixes giving nesting depth, and a
subdivision opening with a parenthesized label — bold with a catchline at
the top level (``**(a) By a Claiming Party.** ...``) or plain below
(``(1) ...``, ``(A) ...``).

This module parses that grammar into ``provision_subsections`` rows (the
same shape the NDCC ingest builds from ndlegis HTML) and into per-line
anchor ids for the web renderer, so a pin cite like N.D.R.Civ.P. 56(e)(1)
can resolve to its subsection text and deep-link as ``#e-1``.

Precision-first, like the NDCC ``parse_if_faithful`` gate: a parenthesized
token becomes a subdivision only when its label *continues* an open
sibling run (a→b, 1→2, ii→iii, A→B) or validly *starts* a new run
(a / 1 / A / i / I). A version is indexed (and anchored) only when its
parse is FULLY clean: every label-shaped token accounted for, no duplicate
paths, and no upper-ALPHA run nested directly under a lower-alpha run.
That last tell matters: rules whose source text glues intermediate labels
into italic runs (``*(1) Mission Statement.*`` hidden inside the ``(a)``
paragraph — N.D.R.Ct. 8.1 is the exemplar) surface as (A)(B)(C) directly
under (a) and would silently take WRONG paths like ``(a)(a)``. Measured
2026-08-14: 1,898 of 2,116 versions (89.7%) parse clean; the 218 held
versions render without anchors rather than with wrong ones.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# A candidate subdivision label opening a paragraph: optional bold marker,
# then a short parenthesized alphanumeric token. Tokens longer than 4 chars
# are never labels ("(added)"), and mixed alnum ("(3a)") is not a shape any
# ND rule uses.
_LABEL_RE = re.compile(r"^(?:\*\*)?\((\d{1,4}|[A-Za-z]{1,4})\)")

_ROMAN_VAL = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100}
_ROMANS = [
    "i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x",
    "xi", "xii", "xiii", "xiv", "xv", "xvi", "xvii", "xviii", "xix", "xx",
    "xxi", "xxii", "xxiii", "xxiv", "xxv", "xxvi", "xxvii", "xxviii",
    "xxix", "xxx",
]
_ROMAN_ORD = {r: n + 1 for n, r in enumerate(_ROMANS)}


def _alpha_ord(s: str) -> int | None:
    """Bijective base-26 ordinal: a=1 .. z=26, aa=27, bb? no — 'aa' style.

    ND rules continue z with aa, bb-style doubling is not used; the
    Bluebook/ndcourts convention is a..z, aa, ab, ... (bijective base-26).
    """
    if not s.isalpha():
        return None
    n = 0
    for ch in s.lower():
        n = n * 26 + (ord(ch) - ord("a") + 1)
    return n


def _readings(label: str) -> dict[str, int]:
    """Every (kind -> ordinal) reading a label admits.

    kinds: 'num', 'alpha' (lowercase letters), 'ALPHA' (uppercase letters),
    'roman' (lowercase), 'ROMAN' (uppercase). '(i)' reads as both alpha #9
    and roman #1; the sibling-run state disambiguates.
    """
    out: dict[str, int] = {}
    if label.isdigit():
        out["num"] = int(label)
        return out
    lower = label.lower()
    if label.islower():
        a = _alpha_ord(label)
        if a is not None:
            out["alpha"] = a
        if lower in _ROMAN_ORD:
            out["roman"] = _ROMAN_ORD[lower]
    elif label.isupper():
        a = _alpha_ord(label)
        if a is not None:
            out["ALPHA"] = a
        if lower in _ROMAN_ORD:
            out["ROMAN"] = _ROMAN_ORD[lower]
    return out


# A run may only START at the first element of its sequence. 'i'/'I' start
# roman runs, never alpha ones (an alpha run reaches 'i' only by continuing
# from 'h'); everything else alphabetic starts alpha only at 'a'/'A'.
_STARTS = {"1": "num", "a": "alpha", "A": "ALPHA", "i": "roman", "I": "ROMAN"}

_KIND_TO_LABEL_TYPE = {
    "num": "pnum", "alpha": "palpha", "ALPHA": "palpha",
    "roman": "proman", "ROMAN": "proman",
}


@dataclass
class _Frame:
    depth: int
    label: str          # as printed, e.g. 'A'
    kind: str
    ordinal: int
    row: dict = field(default_factory=dict)


@dataclass
class Parse:
    """Result of parsing one version's text.

    ``rows``/``anchors`` are best-effort and always populated as far as the
    parse got (the census wants them); consumers must honor ``clean`` —
    only a fully clean parse may be indexed or anchored.
    """
    rows: list[dict]            # provision_subsections-shaped dicts
    anchors: dict[int, str]     # line index -> anchor id ('e-1')
    labels: dict[int, str]      # line index -> printed label ('(1)')
    violations: list[str]       # human-readable notes, for the census
    clean: bool                 # True => safe to index / anchor


def split_line(ln: str) -> tuple[int, str]:
    """(depth, stripped text) for one stored line — the renderer's walk."""
    depth = 0
    while ln.startswith("> ") or ln == ">":
        depth += 1
        ln = ln[2:] if ln.startswith("> ") else ""
    return depth, ln.strip()


def path_to_anchor(labels: list[str]) -> str:
    return "-".join(l.lower() for l in labels)


def parse(text: str) -> Parse:
    """Parse a rule version's text into subdivision rows + anchors."""
    rows: list[dict] = []
    anchors: dict[int, str] = {}
    printed: dict[int, str] = {}
    violations: list[str] = []
    stack: list[_Frame] = []
    seen_paths: set[str] = set()
    dup = False
    seq = 0

    for idx, raw in enumerate(text.split("\n")):
        if not raw.strip():
            continue
        depth, ln = split_line(raw)
        plain = ln.replace("**", "")
        m = _LABEL_RE.match(ln)
        if not m:
            # continuation paragraph: belongs to the innermost open node
            if stack:
                stack[-1].row["text"] += " " + plain
            continue
        label = m.group(1)
        readings = _readings(label)
        # Visual depth and logical depth are decoupled: many rules store a
        # child run at the SAME indent as its parent ('(a)' then '(1) (2)'
        # all flush). Indentation only CLOSES frames (a shallower label
        # never continues a deeper run); nesting among the same-indent
        # frames is decided by sequence logic. Nothing is mutated until
        # the label is accepted, so a rejected token ('(1985)') cannot
        # close open frames.
        j = len(stack)
        while j > 0 and stack[j - 1].depth > depth:
            j -= 1
        # deepest same-indent frame whose run this label continues
        cont = None
        n_cont = 0
        i = j - 1
        while i >= 0 and stack[i].depth == depth:
            if readings.get(stack[i].kind) == stack[i].ordinal + 1:
                if cont is None:
                    cont = i
                n_cont += 1
            i -= 1
        if cont is not None:
            if n_cont > 1:
                violations.append(
                    f"line {idx}: ({label}) continues more than one open "
                    f"run at depth {depth}; took the innermost")
            old = stack[cont]
            del stack[cont:]
            frame = _Frame(depth, label, old.kind, old.ordinal + 1)
        else:
            kind = _STARTS.get(label)
            if kind is None:
                violations.append(
                    f"line {idx}: ({label}) neither continues an open run "
                    f"nor starts one at depth {depth}")
                if stack:
                    stack[-1].row["text"] += " " + plain
                continue
            del stack[j:]
            frame = _Frame(depth, label, kind, 1)
        path_labels = [f.label for f in stack] + [frame.label]
        # the wrong-path tell for hidden intermediate levels: ND drafting
        # nests alpha -> num -> ALPHA -> roman, so a run STARTING directly
        # under a parent of its own kind ((a) under (a), (1) under (1)) or
        # an upper-ALPHA run directly under lower-alpha means a level the
        # text hides (italic-glued labels, unparsed 'Section N.' headings)
        if frame.ordinal == 1 and stack and (
                stack[-1].kind == frame.kind
                or (frame.kind == "ALPHA" and stack[-1].kind == "alpha")):
            violations.append(
                f"line {idx}: ({label}) new {frame.kind} run directly under "
                f"({stack[-1].label}) — likely hidden intermediate level")
        pincite = "".join(f"({l.lower()})" for l in path_labels)
        if pincite in seen_paths:
            dup = True
            violations.append(f"line {idx}: duplicate path {pincite}")
            break
        seen_paths.add(pincite)
        seq += 1
        frame.row = {
            "pincite": pincite,
            "printed_label": f"({label})",
            "label_type": _KIND_TO_LABEL_TYPE[frame.kind],
            "depth": len(path_labels),
            "seq": seq,
            "text": plain,
            "line_idx": idx,
        }
        rows.append(frame.row)
        anchors[idx] = path_to_anchor(path_labels)
        printed[idx] = f"({label})"
        stack.append(frame)

    clean = not dup and not violations
    return Parse(rows, anchors, printed, violations, clean=clean)


def anchor_map(text: str) -> dict[int, str]:
    """line index -> anchor id, for the renderer. Empty unless clean."""
    p = parse(text)
    return p.anchors if p.clean else {}
