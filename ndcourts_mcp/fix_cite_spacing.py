"""Rejoin stray whitespace inside N.D.C.C. / N.D.A.C. section numbers.

A section number that the court's slip PDF wraps across a line (e.g.
``N.D.C.C. §§ 28-32-\\n46``) is rendered in the derived markdown — and so in
``opinions.text_content`` — with a stray space or newline inside the number
(``28-32- 46``). That is a typesetting artifact, not the court's text: the
authoritative PDF prints one section number. This tool removes the stray
whitespace, restoring fidelity to the PDF and letting the citation graph
resolve the cite.

Scope guard (why this is safe to bulk-apply):
  - Only whitespace *inside a recognized section number* is removed; no digit is
    ever changed, and text outside the number span is untouched.
  - A rejoin is auto-applied ONLY when the de-spaced number matches a strict
    N.D.C.C./N.D.A.C. grammar (title 1-2 digits, every later group exactly 2
    digits + optional decimal). Anything else — foreign statutes caught by a
    bare ``§`` (Kan./Ariz./U.P.C./municipal codes), ranges (``27-20-30 to -32``),
    or numbers my extractor truncated — is routed to a NEEDS-REVIEW report and
    left in place for manual adjudication.

Companion: jetcite ≥2.5.4 was hardened the same day so the parser tolerates the
wrap directly (``patterns/states/nd.py`` ``_SEP``); this tool cleans the stored
text so the artifact is gone at the source, not just worked around.

Usage:
    python -m ndcourts_mcp.fix_cite_spacing            # dry-run (default)
    python -m ndcourts_mcp.fix_cite_spacing --apply    # write + changelog
        [--db PATH] [--out triage/cite-spacing-rejoin.md]
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from .db import DEFAULT_DB_PATH, get_connection, log_change
from .refs_diff import _CITE_RE, _HYPHEN_SPACE_RE

BATCH = "cite-spacing-rejoin-2026-06-20"

# Strict single-cite grammars (de-spaced): title is 1-2 digits, every following
# group is exactly two digits with an optional decimal. These reject truncations
# (3-digit groups), single-digit groups (dropped leading zero), and foreign
# statute shapes — those go to needs-review.
_G = r"\d{2}(?:\.\d+)?"
_NDCC_SECTION = re.compile(rf"^\d{{1,2}}(?:\.\d+)?-{_G}-{_G}$")
_NDCC_CHAPTER = re.compile(rf"^\d{{1,2}}(?:\.\d+)?-{_G}$")
_NDAC_SECTION = re.compile(rf"^\d{{1,2}}(?:\.\d+)?-{_G}-{_G}-{_G}$")
_DASH_WS = re.compile(r"\s*-\s*")


def _signal(matched_text: str) -> str:
    b = matched_text.upper().replace(" ", "").replace(".", "")
    if "NDAC" in b:
        return "ndac"
    if "NDCC" in b:
        return "ndcc"
    return "bare"


def _is_high_confidence(cleaned: str, signal: str) -> bool:
    if signal == "ndac":
        return bool(_NDAC_SECTION.match(cleaned))
    if signal == "ndcc":
        return bool(_NDCC_SECTION.match(cleaned) or _NDCC_CHAPTER.match(cleaned))
    # bare "§": accept a well-formed NDCC section/chapter or NDAC section shape
    return bool(_NDCC_SECTION.match(cleaned) or _NDCC_CHAPTER.match(cleaned)
                or _NDAC_SECTION.match(cleaned))


def find_spots(text: str):
    """Yield (num_start, num_end, raw_num, cleaned, signal, high_conf) per spot."""
    for m in _CITE_RE.finditer(text):
        raw = m.group("num")
        if not _HYPHEN_SPACE_RE.search(raw):
            continue
        cleaned = _DASH_WS.sub("-", raw.strip())
        signal = _signal(m.group(0))
        yield (m.start("num"), m.end("num"), raw, cleaned, signal,
               _is_high_confidence(cleaned, signal))


def plan_opinion(text: str):
    """Return (new_text, applied_spots, review_spots) for one opinion."""
    spots = list(find_spots(text))
    applied, review = [], []
    for (s, e, raw, cleaned, signal, hi) in spots:
        (applied if hi else review).append((s, e, raw, cleaned, signal))
    # splice high-confidence rejoins, right-to-left to keep offsets valid
    new_text = text
    for (s, e, raw, cleaned, signal) in sorted(applied, key=lambda x: -x[0]):
        new_text = new_text[:s] + cleaned + new_text[e:]
    return new_text, applied, review


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    p.add_argument("--apply", action="store_true",
                   help="write changes + changelog (default: dry-run)")
    p.add_argument("--out", type=Path,
                   default=Path("triage") / "cite-spacing-rejoin.md")
    args = p.parse_args(argv)

    conn = get_connection(args.db)
    conn.row_factory = __import__("sqlite3").Row
    rows = conn.execute("SELECT id, text_content FROM opinions").fetchall()

    total_applied = total_review = ops_changed = 0
    review_lines, sample_lines = [], []
    for row in rows:
        oid, text = row["id"], row["text_content"] or ""
        if "-" not in text:
            continue
        new_text, applied, review = plan_opinion(text)
        if applied:
            ops_changed += 1
            total_applied += len(applied)
            if len(sample_lines) < 40:
                for (s, e, raw, cleaned, signal) in applied[:2]:
                    sample_lines.append(
                        f"| {oid} | `{raw.strip()[:24]!r}` | `{cleaned}` | {signal} |")
            if args.apply:
                conn.execute("UPDATE opinions SET text_content=? WHERE id=?",
                             (new_text, oid))
                for (s, e, raw, cleaned, signal) in applied:
                    log_change(conn, BATCH, oid, "text_content.cite_spacing",
                               raw.strip(), cleaned)
        if review:
            total_review += len(review)
            for (s, e, raw, cleaned, signal) in review:
                ctx = re.sub(r"\s+", " ", text[max(0, s - 30):e + 18]).strip()
                review_lines.append(
                    f"| {oid} | `{raw.strip()[:26]!r}` | `{cleaned}` | {signal} | …{ctx}… |")

    if args.apply:
        conn.commit()

    # report
    L = ["# N.D.C.C./N.D.A.C. citation stray-space rejoin\n",
         f"- mode: **{'APPLIED' if args.apply else 'DRY-RUN'}**  (batch `{BATCH}`)",
         f"- high-confidence rejoins: **{total_applied}** across **{ops_changed}** opinions",
         f"- needs-review (left in place): **{total_review}**\n"]
    if sample_lines:
        L += ["## Sample of applied rejoins\n",
              "| opinion | was | now | signal |", "|--|--|--|--|", *sample_lines, ""]
    if review_lines:
        L += [f"## Needs review ({total_review}) — NOT modified\n",
              "Foreign statutes (bare §), truncated extracts, or ranges. Verify each "
              "against the court PDF before any fix.\n",
              "| opinion | raw | naive-clean | signal | context |",
              "|--|--|--|--|--|", *review_lines, ""]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(L), encoding="utf-8")
    conn.close()

    print(f"{'APPLIED' if args.apply else 'DRY-RUN'}: "
          f"{total_applied} rejoins / {ops_changed} opinions; "
          f"{total_review} needs-review.")
    print(f"Report: {args.out}")
    if not args.apply:
        print("Re-run with --apply to write (back up opinions.db first).")


if __name__ == "__main__":
    main()
