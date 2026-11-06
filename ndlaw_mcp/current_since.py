"""When a current N.D.C.C. section's text took effect (PLAN-session-laws § 4a, Stage 1).

statutes.db dates every section by the code export, not by the act that wrote
its words, so an older opinion cannot tell from the version alone whether it
construed today's text. The ``current_since`` table (scripts/build_current_since.py)
carries the act and the date; this module reads it, renders the sentence a
reader sees, and says whether an opinion filed on a given date predates the
current text.

Wording follows JT's rulings of 2026-10-31 (the effective date; plain words
with a caveat) and a second ruling that day (text not yet in force; an applicability rule
beside the date; contingent acts "on certification"), and of 2026-11-06: a contingent act
whose certification has been found reads "(S.L. 2017, ch. 199, effective on certification)"
(basis ``contingent-certified``), and a later act's section that has not yet taken effect is
named after the sentence (flag ``pending-amendment:<session>/<ch>/<§>``).
"""

from __future__ import annotations

import re
import sqlite3
from datetime import date

_MONTHS = ["Jan.", "Feb.", "Mar.", "Apr.", "May", "June", "July", "Aug.",
           "Sept.", "Oct.", "Nov.", "Dec."]
_CAVEAT = "For an earlier date, check the revision history."
DIRECTIVE = "S.L. 2021, ch. 352, § 102"


def fmt_date(iso: str) -> str:
    """'2019-10-01' -> 'Oct. 1, 2019' (Redbook month abbreviations)."""
    y, m, d = (int(x) for x in iso[:10].split("-"))
    return f"{_MONTHS[m - 1]} {d}, {y}"


def has_table(conn: sqlite3.Connection, alias: str) -> bool:
    return conn.execute(
        f"SELECT 1 FROM {alias}.sqlite_master WHERE type='table' "
        f"AND name='current_since'").fetchone() is not None


def fetch(conn: sqlite3.Connection, alias: str, provision_id: int) -> dict | None:
    """The stamp for a provision, or None (no table, no row, or stale)."""
    if not has_table(conn, alias):
        return None
    cur = conn.execute(
        f"SELECT * FROM {alias}.current_since WHERE provision_id = ? AND stale = 0",
        (provision_id,))
    row = cur.fetchone()
    if row is None:
        return None
    return dict(zip([c[0] for c in cur.description], row))


def _rule_clause(rule: str) -> str:
    """An applicability or retroactivity rule as a clause after the date."""
    r = rule.strip().rstrip(".")
    if r.startswith("(") and r.endswith(")"):      # a note-expired row holds the code's note verbatim
        r = r[1:-1].strip().rstrip(".")
    if r.lower().startswith("effective for "):
        return ", " + r[len("effective "):]
    head = r[:1].lower() + r[1:]
    if head.startswith(("applies", "retroactively")):
        return "; by its terms it " + head
    return "; by its terms it is " + head


def _years(lo: str | None, hi: str | None) -> str:
    a, b = (lo or "")[:4], (hi or "")[:4]
    if a and b and a != b:
        return f"between {a} and {b}"
    return f"in {a or b}"


def sentence(stamp: dict | None, today: date | None = None) -> str | None:
    """The sentence a reader sees, or None when there is nothing to say."""
    if not stamp:
        return None
    today_iso = (today or date.today()).isoformat()
    kind, acts, eff, basis = stamp["kind"], stamp["acts"], stamp["effective"], stamp["basis"] or ""
    rule = stamp.get("rule") or ""
    if kind == "unchanged":
        return "No amendment found since 1997; earlier history not yet compiled."
    if kind == "reviser":
        return (f"Current wording first appears in the code "
                f"{_years(stamp['window_lo'], stamp['window_hi'])}; "
                f"no session law found for the change.")
    if kind == "directive":
        return (f"Current wording reflects the agency-name substitution {DIRECTIVE} "
                f"directs, effective {fmt_date(eff)}.")
    if kind != "act":
        return None
    if not eff:
        return (f"Current text took effect on a certification its act requires ({acts}); "
                f"the date is not compiled. {_CAVEAT}")
    when = fmt_date(eff)
    if basis.startswith("stated-deferred") and "; " in acts:
        # a later act set the date of an earlier act's text: name the one that wrote the words
        src, setter = acts.split("; ", 1)
        acts = f"{src}; effective date set by {setter}"
    if eff > today_iso:
        return f"This text takes effect {when} ({acts}). The text in force until then is not yet compiled."
    if basis.startswith("stated-deferred-or-earlier"):
        return (f"Current text effective by {when} ({acts}), or earlier on a certification "
                f"the act provides for. {_CAVEAT}")
    tail = ""
    if basis == "contingent-certified":
        acts += ", effective on certification"
    elif basis == "note-expired":
        # ruling 14 (2026-11-06): the code carried the act's effective-date note until the date
        # passed, then stripped it; the note's date is the section's date
        acts += ", per the effective-date note the code carried until that date"
        if rule and re.search(r"taxable|occurring|for .{0,40}(years?|periods?)", rule):
            tail = _rule_clause(rule)
    elif basis == "contingent-dated":
        tail = ", on a condition the act states"
    elif rule and ("applicability" in basis or "retroactive" in basis):
        tail = _rule_clause(rule)
    return f"Current text effective {when} ({acts}){tail}. {_CAVEAT}{_pending(stamp)}"


def _pending(stamp: dict) -> str:
    """A later act's section not yet in force, from the pending-amendment flag."""
    for f in (stamp.get("flags") or "").split():
        if f.startswith("pending-amendment:"):
            sess, ch, sec = f.split(":", 1)[1].split("/")
            return (f" A later amendment, S.L. {sess}, ch. {ch}, § {sec}, takes effect on a "
                    f"certification not yet made.")
    return ""


def opinion_relation(stamp: dict | None, date_filed: str | None) -> str:
    """Whether an opinion filed on ``date_filed`` construed the current text:
    'current', 'earlier', or 'unknown'."""
    if not stamp or not date_filed:
        return "unknown"
    filed = date_filed[:10]
    kind, eff = stamp["kind"], stamp["effective"]
    lo, hi = stamp.get("window_lo") or "", stamp.get("window_hi") or ""
    lo_iso = f"{lo[:4]}-{lo[4:6]}-{lo[6:8]}" if lo else ""
    hi_iso = f"{hi[:4]}-{hi[4:6]}-{hi[6:8]}" if hi else ""
    if kind == "unchanged":
        # no act 1997-2026 names it: the same words since at least 1997
        return "current" if filed >= "1997-01-01" else "unknown"
    if kind in ("act", "directive") and eff and not (stamp["basis"] or "").startswith("stated-deferred-or-earlier"):
        return "current" if filed >= eff else "earlier"
    # no exact date (reviser change, undated certification, an outer bound): the
    # capture window brackets the change
    if eff and filed >= eff:
        return "current"
    if hi_iso and filed >= hi_iso:
        return "current"
    if lo_iso and filed < lo_iso:
        return "earlier"
    return "unknown"
