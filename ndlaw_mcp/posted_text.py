"""The Council's double postings in the CURRENT export text (JT 2026-11-07).

While an amendment is pending, ndlegis prints every version of a section in one
block: the text in force first, its heading carrying "(Effective through <D>)"
(or a contingent / repeal / expiry note), then the catchline again with the
posted version's own note — "(Effective after <D>)", "(Effective for taxable
years beginning after <D>)", "(Contingent effective date - See note)" — and that
version's text; 57-39.2-26 prints three. The export glues the catchline to the
end of the previous text ("…development fund.Auditor to prepare budget…"), so a
reader of ``text_content`` sees one run of prose with a parenthetical in the
middle. ~100 current sections (2025-07-01 compile).

``split_versions`` cuts that text at each repeated catchline + note into blocks
(nothing dropped: the catchline line becomes the block's header), and
``describe`` turns a note into the plain sentence the page and the tool show
("Takes effect July 1, 2029 — not yet in force").

Stage 2 rulings 23–26 (JT 2026-11-07, PLAN-session-laws § 4a): in the derived
``statutes.stage2.db`` a posted block with a DATED note becomes its own version
row — ``note_window`` reads the bounds a note gives and ``future_plan`` lays the
blocks out as versions for the loader (``scripts/build_statutes_stage2.py``). A
contingent block has no date and stays in the text (ruling 25): the page and
``lookup_authority`` keep splitting it at serve time. Nothing here writes.
"""
from __future__ import annotations

import re
from datetime import date, timedelta

from .current_since import fmt_date

NOTE = re.compile(r"\((?:Effective|Contingent|Expired|Expires|Repealed effective|Suspended|Retroactive|"
                  r"Applicable|Applies)\b[^()]*\)")
_MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
_DATE = rf"(?:{_MONTHS}) \d{{1,2}}, \d{{4}}"


def _iso(s: str) -> str:
    m, d, y = re.match(rf"({_MONTHS}) (\d{{1,2}}), (\d{{4}})", s).groups()
    return date(int(y), (_MONTHS.split("|").index(m)) + 1, int(d)).isoformat()


def _plus_one(iso: str) -> str:
    return (date.fromisoformat(iso) + timedelta(days=1)).isoformat()


def heading_note(heading: str | None) -> str | None:
    """The note the current text's heading carries, or None."""
    m = NOTE.search(heading or "")
    return m.group(0) if m else None


def catchline_stem(heading: str | None) -> str:
    """The heading without its note or trailing period: the string the export
    repeats before each posted version."""
    return NOTE.sub("", heading or "").strip().rstrip(".").strip()


def split_versions(text: str, heading: str | None) -> list[dict]:
    """[{note, header, text}] — one block when the text holds a single version.
    ``header`` is the repeated catchline line as printed (None for the first
    block, whose note sits in the page heading); ``text`` is the block's body."""
    stem = catchline_stem(heading)
    if len(stem) < 4:
        return [{"note": heading_note(heading), "header": None, "text": text}]
    # two header orders: catchline then note (the export and captures since 2016) and note
    # then catchline (captures to 2016: "(Effective after June 30, 2008) Service of process.")
    pat = re.compile(r"(?:" + re.escape(stem) + r"\.?\s*(" + NOTE.pattern + r")"
                     r"|(" + NOTE.pattern + r")\s*" + re.escape(stem) + r"\.?)[ \t]*")
    cuts = [m for m in pat.finditer(text) if m.start() > 0]
    if not cuts:
        return [{"note": heading_note(heading), "header": None, "text": text}]
    blocks = [{"note": heading_note(heading), "header": None, "text": text[:cuts[0].start()].rstrip()}]
    for i, m in enumerate(cuts):
        end = cuts[i + 1].start() if i + 1 < len(cuts) else len(text)
        blocks.append({"note": m.group(1) or m.group(2), "header": m.group(0).strip(), "text": text[m.end():end].strip()})
    return blocks


def note_window(note: str | None) -> tuple[str | None, str | None]:
    """The half-open [start, end) bounds a note gives, ISO or None each.

    "(Effective after D)" → (D+1, None); "(Effective after D, and through E)" →
    (D+1, E+1); "(Effective for taxable years beginning after D)" → (D+1, None)
    (ruling 26's judgment call: the applicability year opens the day after D);
    "(Effective through E)" → (None, E+1); "(Effective for … beginning before D)"
    → (None, D). Anything else — contingent, repeal, expiry, retroactive — gives
    (None, None): it dates nothing a version row could carry."""
    if not note:
        return None, None
    c = note[1:-1].strip() if note.startswith("(") and note.endswith(")") else note.strip()
    m = re.fullmatch(rf"Effective after ({_DATE}), and through ({_DATE})", c)
    if m:
        return _plus_one(_iso(m.group(1))), _plus_one(_iso(m.group(2)))
    m = re.fullmatch(rf"Effective after ({_DATE})", c)
    if m:
        return _plus_one(_iso(m.group(1))), None
    m = re.fullmatch(rf"Effective for .+? beginning after ({_DATE})", c)
    if m:
        return _plus_one(_iso(m.group(1))), None
    m = re.fullmatch(rf"Effective through ({_DATE})", c)
    if m:
        return None, _plus_one(_iso(m.group(1)))
    m = re.fullmatch(rf"Effective for .+? beginning before ({_DATE})", c)
    if m:
        return None, _iso(m.group(1))
    return None, None


def future_plan(text: str, heading: str | None) -> dict | None:
    """How the export's double text lays out as version rows (rulings 23, 25).

    None when the text holds one version. Otherwise::

        {"in_force": {"text": …, "note": …, "end_hint": E+1 or None},
         "future":   [{"start", "end_hint", "note", "header", "text"}, …],
         "undated":  [notes of posted blocks that give no date]}

    ``future`` is in text order, each block's ``start`` from its own note. When
    ``undated`` is non-empty the loader leaves the row whole (an undated row
    could never answer an ``as_of``); ``future`` is still reported."""
    blocks = split_versions(text, heading)
    if len(blocks) < 2:
        return None
    first = blocks[0]
    _, end_hint = note_window(first["note"])
    plan = {"in_force": {"text": first["text"], "note": first["note"], "end_hint": end_hint},
            "future": [], "undated": []}
    for b in blocks[1:]:
        start, end = note_window(b["note"])
        if start is None:
            plan["undated"].append(b["note"])
            continue
        plan["future"].append({"start": start, "end_hint": end, "note": b["note"],
                               "header": b["header"], "text": b["text"]})
    return plan


def future_only_start(heading: str | None) -> str | None:
    """Ruling 24: a section whose ONLY text is posted for a future date carries
    the note in its heading — "(Effective after D)" → D+1, else None. Only the
    plain "after" form: a "through" or applicability note heads text in force."""
    n = heading_note(heading)
    if not n or not re.fullmatch(rf"\(Effective after {_DATE}\)", n):
        return None
    return note_window(n)[0]


def flag_note(flags: str | None) -> str | None:
    """The posted block's note as the loader stored it in ``loader_flags``
    (`posted-note=(Effective after June 30, 2029)`), or None."""
    m = re.search(r"posted-note=(\([^)]*\))", flags or "")
    return m.group(1) if m else None


def posted_header(heading: str | None, note: str) -> str:
    """The catchline line the export prints before a posted block, rebuilt from
    the provision heading and the block's note (what the loader does not store)."""
    return f"{catchline_stem(heading)}. {note}"


def describe(note: str | None, today: date | None = None) -> str | None:
    """Plain words for a note. None when there is no note."""
    if not note:
        return None
    t = (today or date.today()).isoformat()
    c = note[1:-1].strip()
    m = re.fullmatch(rf"Effective after ({_DATE}), and through ({_DATE})", c)
    if m:
        a, b = _plus_one(_iso(m.group(1))), _iso(m.group(2))
        return (f"Takes effect {fmt_date(a)} and runs through {fmt_date(b)} — not yet in force" if a > t
                else f"In force {fmt_date(a)} through {fmt_date(b)}")
    m = re.fullmatch(rf"Effective after ({_DATE})", c)
    if m:
        a = _plus_one(_iso(m.group(1)))
        return f"Takes effect {fmt_date(a)} — not yet in force" if a > t else f"In force since {fmt_date(a)}"
    m = re.fullmatch(rf"Effective through ({_DATE})", c)
    if m:
        b = _iso(m.group(1))
        return f"Current text — in force through {fmt_date(b)}" if b >= t else f"Was in force through {fmt_date(b)}"
    m = re.fullmatch(rf"Effective for (.+?) beginning after ({_DATE})", c)
    if m:
        return f"Applies to {m.group(1)} beginning after {fmt_date(_iso(m.group(2)))}"
    m = re.fullmatch(rf"Effective for (.+?) beginning before ({_DATE})", c)
    if m:
        return f"Current text — applies to {m.group(1)} beginning before {fmt_date(_iso(m.group(2)))}"
    m = re.fullmatch(rf"Effective for (.+)", c)
    if m:
        return f"Applies {m.group(1)}"
    m = re.fullmatch(rf"Repealed effective ({_DATE})", c)
    if m:
        return f"Current text — repealed effective {fmt_date(_iso(m.group(1)))}"
    m = re.fullmatch(rf"Expired effective ({_DATE})", c)
    if m:
        return f"Expired effective {fmt_date(_iso(m.group(1)))}"
    if c.startswith("Contingent effective"):
        return "Contingent on a condition the act states — not yet in force"
    if c.startswith("Contingent expiration"):
        return "Current text — expires on a condition the act states"
    if c.startswith("Contingent repeal"):
        return "Current text — repealed on a condition the act states"
    return c
