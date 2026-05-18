"""Shared Type-Y discriminator.

A Westlaw .doc whose "All Citations" N.W. cite is disjoint from the
matched DB row's N.W. cite is either (a) the SAME opinion with a wrong
N.W. digit (citation-accuracy bug — high body overlap), or (b) a
separate supplemental publication that merely shares the `<vol> N.D.
<page>` starting page (Type Y — distinct text). The discriminator is
body-jaccard against `SAME_OPINION_J`, with a shared N.D. cite as the
Type-Y corroborant.

This module is the single source of truth for that decision, used both
by the corpus sweep (`sweep_type_y`) and at ingest time
(`ingest_westlaw.process_batch`). It is intentionally dependency-light
(only `re` + `multisource_diff`) and takes an already-parsed Westlaw doc
dict as input, so it can be imported from `ingest_westlaw` without a
circular import (`sweep_type_y` imports `ingest_westlaw`, not the
reverse).
"""

from __future__ import annotations

import re

from .multisource_diff import jaccard, normalize_words, shingles

_NW = re.compile(r"\b(\d+)\s+N\.\s?W\.(?:\s?2d)?\s+(\d+)\b")
_ND = re.compile(r"\b(\d+)\s+N\.\s?D\.\s+(\d+)\b")

# Above this body-jaccard the .doc and the DB row are the SAME opinion,
# so an N.W.-cite mismatch is a citation-accuracy bug (OCR/metadata wrong
# digit), NOT a separate Type Y publication. Below it, a shared N.D. cite
# + distinct text is a genuine supplemental-publication candidate.
SAME_OPINION_J = 0.55

# kinds
MATCH = "MATCH"                       # N.W. cites overlap → normal pairing
DOC_NO_NW = "DOC_NO_NW"
DB_NO_NW = "DB_NO_NW"
CITE_DISCREPANCY = "CITE_DISCREPANCY"  # same opinion, wrong N.W. digit
TYPE_Y = "TYPE_Y"                      # distinct text, shared N.D. page
TYPE_Y_NO_NDSHARE = "TYPE_Y_NO_NDSHARE"  # distinct text, N.D. cite differs

TYPE_Y_KINDS = (TYPE_Y, TYPE_Y_NO_NDSHARE)


def nw_keys(text: str) -> set[tuple[str, str, str]]:
    """All N.W./N.W.2d cites in a string, normalized to (vol, series, page)."""
    out = set()
    for m in _NW.finditer(text or ""):
        series = "2d" if "2d" in m.group(0).replace(" ", "") else "1"
        out.add((m.group(1), series, m.group(2)))
    return out


def nd_keys(text: str) -> set[tuple[str, str]]:
    return {(m.group(1), m.group(2)) for m in _ND.finditer(text or "")}


def _doc_cites(parsed: dict) -> list[str]:
    cites = list(parsed.get("all_citations") or [])
    if parsed.get("primary_citation"):
        cites.append(parsed["primary_citation"])
    return cites


def doc_nw_keys(parsed: dict) -> set[tuple[str, str, str]]:
    keys: set[tuple[str, str, str]] = set()
    for c in _doc_cites(parsed):
        keys |= nw_keys(c)
    return keys


def doc_nd_keys(parsed: dict) -> set[tuple[str, str]]:
    out: set[tuple[str, str]] = set()
    for c in _doc_cites(parsed):
        out |= nd_keys(c)
    return out


def fmt_nw(keys: set[tuple[str, str, str]]) -> str:
    return ";".join(
        f"{v} N.W.{'2d' if s == '2d' else ''} {p}"
        for v, s, p in sorted(keys, key=lambda k: (int(k[0]), int(k[2])))
    )


def _strip_frontmatter(text: str) -> str:
    """Return the opinion body, dropping a leading `---`-delimited YAML
    block if present. Mirrors ingest_nwcite._split_frontmatter's body
    half; inlined here to keep this module dependency-light and
    cycle-free."""
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---\n", 4)
    if end == -1:
        return text
    return text[end + 5:].lstrip("\n")


class Result:
    """Discriminator result. `kind` is the decision; the rest are the
    signals behind it (for the sweep's TSV / ingest logging)."""

    __slots__ = ("kind", "doc_nw", "db_nw", "jac", "nd_shared")

    def __init__(self, kind, doc_nw, db_nw, jac, nd_shared):
        self.kind = kind
        self.doc_nw = doc_nw
        self.db_nw = db_nw
        self.jac = jac
        self.nd_shared = nd_shared

    @property
    def is_type_y(self) -> bool:
        return self.kind in TYPE_Y_KINDS


def classify(parsed: dict, db_cites_text: str, db_text: str) -> Result:
    """Decide how a parsed Westlaw .doc relates to a matched DB opinion.

    `parsed`        — _parse_westlaw_doc output for the .doc.
    `db_cites_text` — the DB opinion's citations, any concatenation
                      containing the cite strings (used for N.W./N.D.
                      key extraction).
    `db_text`       — the DB opinion's text_content (frontmatter ok).
    """
    doc_nw = doc_nw_keys(parsed)
    if not doc_nw:
        return Result(DOC_NO_NW, doc_nw, set(), None, None)
    db_nw = nw_keys(db_cites_text)
    if not db_nw:
        return Result(DB_NO_NW, doc_nw, db_nw, None, None)
    if not doc_nw.isdisjoint(db_nw):
        return Result(MATCH, doc_nw, db_nw, None, None)
    # N.W. cites disjoint: separate publication (Type Y) vs same-opinion
    # citation-accuracy bug — decided by body text + shared N.D. cite.
    doc_body = parsed.get("full_bound_text") or parsed.get("opinion_text") or ""
    db_body = _strip_frontmatter(db_text or "")
    j = jaccard(shingles(normalize_words(doc_body)),
                shingles(normalize_words(db_body)))
    nd_shared = bool(doc_nd_keys(parsed) & nd_keys(db_cites_text))
    if j >= SAME_OPINION_J:
        kind = CITE_DISCREPANCY
    elif nd_shared:
        kind = TYPE_Y
    else:
        kind = TYPE_Y_NO_NDSHARE
    return Result(kind, doc_nw, db_nw, j, nd_shared)
