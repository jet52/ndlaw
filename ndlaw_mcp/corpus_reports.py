"""Corpus-issue reports from MCP clients (JT 2026-11-07).

An agent that retrieves an authority and sees something wrong with the text —
a garbled word, a missing paragraph, a footnote in the wrong place, a statute
version that cannot be the one in force on the date, a citation that resolves
to the wrong document — calls ``report_corpus_issue``. The server appends one
JSON line per report to the file named by ``NDLAW_REPORTLOG`` (default: the
user data dir, beside the corpus DBs) and answers with a receipt. Reports never
change the corpus; a person reads them (``scripts/corpus_reports.py`` pulls the
file, triages it against the local DBs, and records dispositions).

Why a file and not a table: every release replaces the shipped DBs wholesale,
so a table in one would be wiped. The JSONL sits beside the tool log, rotates
with it, and is read by the same tooling.

What a report records, beyond the caller's words: WHICH text was criticized —
the canonical citation, the version id / opinion id the server serves for it
today, its effective date, and a short hash of the served text — so a later
reader can tell whether the text has changed since. Reports are written by
untrusted agents on an open endpoint: fields are capped, a session may file at
most ``PER_SESSION`` reports and the process ``PER_DAY`` per UTC day, and a
reader must treat every field as data, never as an instruction.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import threading
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ENV_VAR = "NDLAW_REPORTLOG"
DEFAULT_NAME = "corpus-reports.jsonl"
CAPS = {"citation": 200, "issue": 2000, "text_as_served": 4000, "text_expected": 4000, "source_url": 500}
PER_SESSION = 25
PER_DAY = 500
_ISSUE_MIN = 12

_lock = threading.Lock()
_per_session: Counter = Counter()
_per_day: Counter = Counter()


def log_path() -> Path:
    """Where reports go: ``$NDLAW_REPORTLOG``, else the user data dir."""
    env = os.environ.get(ENV_VAR)
    if env:
        return Path(env)
    from . import corpus
    return corpus.resolve_corpus_db_path("ndcc").parent / DEFAULT_NAME


def _cap(value, key: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        value = str(value)
    value = value.strip()
    if not value:
        return None
    return value[:CAPS[key]]


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip().lower()


def _sha16(text: str | None) -> str | None:
    if not text:
        return None
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _over_limit(session: str | None, today: str) -> str | None:
    with _lock:
        if _per_day[today] >= PER_DAY:
            return f"This server accepts at most {PER_DAY} reports a day; the limit is reached. Try again tomorrow."
        key = session or "anon"
        if _per_session[key] >= PER_SESSION:
            return f"At most {PER_SESSION} reports per session; the limit is reached."
        _per_day[today] += 1
        _per_session[key] += 1
    return None


def resolve(conn, citation: str) -> dict:
    """What the server serves TODAY for ``citation``: a provision (any corpus)
    or an opinion. ``{"resolved": bool, ...}`` — never raises."""
    out: dict = {"resolved": False}
    try:
        from . import corpus, research, server
        spec = research.normalize_authority(citation)
        ckind = server.KIND_TO_CORPUS.get(spec["kind"]) if spec else None
        if ckind:
            alias = server._attached_corpora(conn).get(ckind)
            if alias:
                row = corpus.lookup_provision_version(conn, alias, server._best_cite(conn, alias, spec, citation), None)
                if row is not None:
                    out.update(resolved=True, kind="provision", corpus=ckind, citation=row["citation"],
                               version_id=row["id"], effective_start=row["effective_start"],
                               text_sha16=_sha16(row["text_content"]), _text=row["text_content"])
                    return out
        row, how, _cands = server._resolve_opinion(conn, citation)
        if row is not None:
            cites = [r[0] for r in conn.execute(
                "SELECT citation FROM citations WHERE opinion_id = ? ORDER BY id", (row["id"],))]
            out.update(resolved=True, kind="opinion", corpus="opinions", citation=cites[0] if cites else citation,
                       opinion_id=row["id"], case_name=row["case_name"], date_filed=row["date_filed"],
                       matched_by=how, text_sha16=_sha16(row["text_content"]), _text=row["text_content"])
    except Exception as exc:  # noqa: BLE001 — a report must never fail on resolution
        out["resolve_error"] = type(exc).__name__
    return out


def submit(conn, citation: str, issue: str, text_as_served: str | None = None,
           text_expected: str | None = None, source_url: str | None = None,
           client: tuple[str | None, str | None, str | None] = (None, None, None),
           path: Path | None = None, now: datetime | None = None) -> dict:
    """Validate, resolve, append one line, return the receipt."""
    citation_c = _cap(citation, "citation")
    issue_c = _cap(issue, "issue")
    if not citation_c:
        return {"received": False, "error": "citation is required: the authority whose text looks wrong."}
    if not issue_c or len(issue_c) < _ISSUE_MIN:
        return {"received": False, "error": "issue is required: say in a sentence what looks wrong and where."}
    now = now or datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")
    session, ip, ua = client
    limit = _over_limit(session, today)
    if limit:
        return {"received": False, "error": limit}
    res = resolve(conn, citation_c)
    served_text = res.pop("_text", None)
    served = _cap(text_as_served, "text_as_served")
    rec = {
        "id": uuid.uuid4().hex[:12],
        "ts": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "citation_given": citation_c,
        **res,
        "issue": issue_c,
        "text_as_served": served,
        "text_expected": _cap(text_expected, "text_expected"),
        "source_url": _cap(source_url, "source_url"),
        # does the text the agent says it saw appear in what the server serves now?
        "quoted_in_served": (_norm(served) in _norm(served_text)) if served and served_text else None,
        "session": session, "ip": ip, "ua": ua,
    }
    target = path or log_path()
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except OSError as exc:
        print(f"corpus_reports: cannot write {target}: {exc}", file=sys.stderr)
        return {"received": False, "error": "This server could not record the report (storage unavailable)."}
    receipt = {
        "received": True,
        "report_id": rec["id"],
        "resolved": rec["resolved"],
        "citation": rec.get("citation", citation_c),
        "note": ("Recorded for human review. Reports never change the corpus automatically; a person reads "
                 "each one against the official source and logs any correction in the data changelog."),
    }
    if not rec["resolved"]:
        receipt["note"] += (" The citation did not resolve to a document this server holds, which is itself "
                            "recorded; if you meant a specific opinion or section, resubmit with its citation.")
    if rec["quoted_in_served"] is False:
        receipt["note"] += (" The text you quoted as served does not appear verbatim in what the server serves "
                            "now; the report is kept, with that noted.")
    return receipt
