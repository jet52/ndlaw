"""Name equivalence for citation-graph work — the shared matcher behind the
antecedent-witness audit, cite_reconcile, and shared-cite collision
resolution (2026-07-13, worked from the three manual queues).

The naive distinctive-token overlap fails on three ND-caption realities:

1. AGENCY ABBREVIATIONS — DB captions often abbreviate state agencies
   ("...v. WSI") while citing opinions print the full name ("...v. Workforce
   Safety & Ins."), and vice versa. `AGENCY_ALIASES` expands both sides.
2. LEGAL ABBREVIATION STEMS — "Dep't"/"Department", "Comm'n"/"Commission",
   "Transp."/"Transportation", "Servs."/"Services": compared by prefix stem
   (min 3 chars) rather than exact token equality.
3. INITIALS-ONLY PARTIES — juvenile/confidential captions ("Interest of
   K.J.C.") tokenize to nothing (single letters are dropped as
   non-distinctive). Initial GROUPS (2+ consecutive dotted capitals) are
   compared as strings instead.

`match_score(a, b)` returns 0 when the names share nothing recognizable —
the FALSE-edge signal — and a positive strength count otherwise. It is a
WITNESS metric (protects against wrong edges), not a search key; the
reconciler's cite-component anchors remain the safety on any re-point.
"""

from __future__ import annotations

import re

_NAME_STOP = frozenset({
    "v", "vs", "in", "re", "matter", "of", "the", "and", "a", "an",
    "ex", "rel", "et", "al", "no", "city", "state", "county",
})


def _name_tokens(name: str) -> set[str]:
    """Distinctive lowercase word tokens of a case name (drops structural words). Moved here
    from cite_extract 2026-11-24 so the published server can import this module."""
    if not name:
        return set()
    return {t for t in re.findall(r"[a-z0-9]+", name.lower())
            if t not in _NAME_STOP and len(t) > 1}

# Corporate/relational suffixes + generic procedural words — not distinctive
# (mirrors cite_reconcile._SUFFIX_TOKENS; kept in sync there).
SUFFIX_TOKENS = frozenset({
    "llc", "inc", "ltd", "co", "corp", "llp", "lllp", "pc", "pllc",
    "ass", "assn", "association", "company", "corporation",
    "partnership", "pship", "ship",   # "Ltd. P'ship" spans (2026-07-23)
    "interest", "matter", "estate", "guardianship", "conservatorship",
    "adoption", "marriage", "disciplinary", "application", "petition",
    "confidential", "consolidated",
})

# ND state-agency abbreviations <-> full-name tokens. Expansion is applied to
# BOTH names being compared, so either direction matches. Tokens are the
# post-_name_tokens lowercase forms.
AGENCY_ALIASES: dict[str, frozenset[str]] = {
    "wsi": frozenset({"workforce", "safety", "insurance", "ins"}),
    "ndic": frozenset({"industrial", "commission", "comm"}),
    "nddot": frozenset({"transportation", "transp", "dot"}),
    "dot": frozenset({"transportation", "transp"}),
    "nddhs": frozenset({"human", "services", "department", "dep"}),
    "nddhhs": frozenset({"health", "human", "services", "department", "dep"}),
    "dhs": frozenset({"human", "services"}),
    "ndpers": frozenset({"public", "employees", "retirement", "system"}),
    "psc": frozenset({"public", "service", "commission"}),
    "bci": frozenset({"bureau", "criminal", "investigation"}),
    "omb": frozenset({"office", "management", "budget"}),
    # deliberately NOT aliased: BND/BNSF — their expansions (bank, north,
    # northern, dakota) are too common; poisoning AGENCY_VOCAB with them
    # disqualified legitimate matches (Northern State Bank pa746)
}

_INITIAL_GROUP = re.compile(r"(?:\b[A-Z]\.){2,}")

# initials groups that are corporate/structural, not party-identifying —
# 'L.P.'/'L.L.C.'/'P.C.' spans would otherwise "match" any entity with the
# same suffix (caught live 2026-07-13: a bare 'L.P.' antecedent proposed
# re-pointing correct edges between unrelated L.P. cases)
_NON_PARTY_GROUPS = frozenset({
    "lp", "llc", "llp", "pc", "pllc", "ltd", "co", "us", "usa",
    "nd", "sd", "mn", "jj", "cj",     # states; justice-signature initials
})


def tokens(name: str | None) -> set[str]:
    return _name_tokens(name or "") - SUFFIX_TOKENS


def expand(toks: set[str]) -> set[str]:
    out = set(toks)
    for t in toks:
        out |= AGENCY_ALIASES.get(t, frozenset())
    return out


def initial_groups(name: str | None) -> set[str]:
    """{'kjc', ...} for each run of 2+ dotted capitals in the caption,
    excluding corporate/structural groups (L.P., L.L.C., U.S., ...)."""
    return {g.replace(".", "").replace(" ", "").lower()
            for g in _INITIAL_GROUP.findall(name or "")} - _NON_PARTY_GROUPS


def _cross_form_initials(name_a: str | None, name_b: str | None) -> set[str]:
    """Dotted initials on one side matching an undotted smushed token on the
    other — pre-1997 stored captions write juvenile initials without periods
    ('In Interest of KB', 'Adoption of JSPL', 'In Interest of Dg') while
    citing courts print 'K.B.' / 'J.S.P.L.'. Dotted-side gating keeps this
    precise: an ordinary word can only match if the OTHER caption carries the
    same letters as genuine dotted initials."""
    def raw_tokens(name):
        return {t.lower() for t in re.findall(r"[A-Za-z]+", name or "")}
    return ((initial_groups(name_a) & raw_tokens(name_b))
            | (initial_groups(name_b) & raw_tokens(name_a))) - _NON_PARTY_GROUPS


# 3-char tokens allowed to prefix-match (common legal abbreviations); generic
# prefixes require >=4 chars so 'van' can't claim 'vandewalle'
_SHORT_ABBREVS = frozenset({
    "dep", "ins", "div", "sec", "bur", "adm", "emp", "sav", "nat", "fin",
    "mut", "tel", "pub", "sch",
})


def _stem_eq(a: str, b: str) -> bool:
    """Equal, or one is an abbreviation-length prefix of the other
    ('transp' ~ 'transportation', 'dep' ~ 'department')."""
    if a == b:
        return True
    if len(a) > len(b):
        a, b = b, a
    if b.startswith(a):
        return len(a) >= 4 or a in _SHORT_ABBREVS
    return False


# every token that belongs to agency vocabulary (abbreviations + expansions):
# useful for finding candidates, but never sufficient to QUALIFY a match on
# its own — any 'Dep't of Human Servs. v. X' shares it with any 'Y v. NDDHS'
AGENCY_VOCAB: frozenset[str] = frozenset(AGENCY_ALIASES) | frozenset(
    t for exp in AGENCY_ALIASES.values() for t in exp)


def nonagency_pair(name_a: str | None, name_b: str | None) -> bool:
    """True when the two captions share a stem-matched pair of tokens that
    are NOT agency vocabulary, or a party-initials group — the qualification
    bar for automatic edge corrections."""
    ta = {t for t in tokens(name_a)
          if t not in AGENCY_VOCAB and not any(_stem_eq(t, v) for v in AGENCY_VOCAB)}
    tb = {t for t in tokens(name_b)
          if t not in AGENCY_VOCAB and not any(_stem_eq(t, v) for v in AGENCY_VOCAB)}
    if any(_stem_eq(a, b) for a in ta for b in tb):
        return True
    return bool(initial_groups(name_a) & initial_groups(name_b)
                or _cross_form_initials(name_a, name_b))


def match_score(name_a: str | None, name_b: str | None) -> int:
    """Count of recognizably-shared name elements between two captions.
    0 = nothing shared (FALSE-edge signal). Initial-group matches count 2
    (they identify a party as strongly as a surname)."""
    ta, tb = expand(tokens(name_a)), expand(tokens(name_b))
    score = 0
    used: set[str] = set()
    for a in ta:
        for b in tb:
            if b not in used and _stem_eq(a, b):
                score += 1
                used.add(b)
                break
    shared_initials = ((initial_groups(name_a) & initial_groups(name_b))
                       | _cross_form_initials(name_a, name_b))
    score += 2 * len(shared_initials)
    return score
