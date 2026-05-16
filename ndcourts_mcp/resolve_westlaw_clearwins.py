"""Conservative 'clear wins' pass over the receive_westlaw ambiguous queue.

The receive batch left N docs AMBIGUOUS because formulaic captions
(disciplinary / vacancy) defeat the caption matcher even when a human
instantly sees the answer (e.g. the "...DISCIPLINARY ACTION AGAINST
SLETTEN..." doc obviously belongs to "In re Disciplinary Action
Against Sletten", not "...Moosbrugger"). This promotes ONLY the
unambiguous ones, by anchoring on the distinctive party surname:

  promote doc -> candidate IFF
    * exactly one cleaned-cite candidate contains a doc surname, and
      no other candidate does, AND
    * that candidate is NOT part of a duplicate pair (no other opinion
      shares its (case_name, date_filed)) — dup-entangled items defer
      to a dedicated dedup session, AND
    * jaccard(doc text, candidate text) >= 0.20 (same safety floor as
      receive_westlaw; never overwrite a low-similarity row).

Anything else stays in the manual queue untouched. Reuses
receive_westlaw._promote so the write path, authority stamping and
changelog are identical. Snapshot + invariants discipline; dry-run
default.

Usage:
  python -m ndcourts_mcp.resolve_westlaw_clearwins
  python -m ndcourts_mcp.resolve_westlaw_clearwins --apply
"""

from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path

from .db import DEFAULT_DB_PATH, get_connection, log_provenance
from .ingest_westlaw import _doc_to_text
from .receive_westlaw import (
    _archive_doc,
    _clean_cite,
    _candidates,
    _parse,
    _promote,
    jaccard,
    normalize_words,
    shingles,
)

BATCH = f"westlaw-queue-clearwins-{date.today().isoformat()}"
INCOMING = Path.home() / "refs" / "nd" / "opin" / "westlaw-incoming"
REPORT = Path("triage") / "westlaw-receive-2026-05-15.tsv"

# ALLCAPS tokens that are structural, not party surnames. The Westlaw
# caption uppercases surnames ("Douglas D. SLETTEN"); these are the
# words to ignore when harvesting the distinctive name.
_STOP = {
    "STATE", "NORTH", "DAKOTA", "SUPREME", "COURT", "APPEALS", "BOARD",
    "DISCIPLINARY", "ACTION", "AGAINST", "MATTER", "APPLICATION", "ESTATE",
    "INTEREST", "BAR", "MEMBER", "PETITIONER", "RESPONDENT", "RESPONDENTS",
    "DEFENDANT", "DEFENDANTS", "PLAINTIFF", "PLAINTIFFS", "APPELLANT",
    "APPELLANTS", "APPELLEE", "APPELLEES", "INC", "COMPANY", "CORPORATION",
    "CITY", "COUNTY", "BANK", "TRUST", "THE", "OF", "AND", "JUDGE",
    "JUDGESHIP", "VACANCY", "CHAMBER", "JUDICIAL", "DISTRICT", "DECEASED",
    "CHILD", "CHILDREN", "REQUEST", "HONORABLE", "COMMISSION", "CONSERVATOR",
    "GUARDIANSHIP", "PROPERTY", "REINSTATEMENT", "PETITION",
}


def _surnames(name: str) -> set[str]:
    toks = re.findall(r"\b[A-Z][A-Z'’\-]{2,}\b", name or "")
    return {t.replace("’", "'") for t in toks if t not in _STOP}


def _is_dup_member(conn, cand: dict) -> bool:
    """True if another opinion shares this one's (case_name, date) — a
    pre-existing duplicate pair; defer rather than promote into it."""
    n = conn.execute(
        "SELECT COUNT(*) FROM opinions WHERE case_name=? AND date_filed=?",
        (cand["case_name"], cand["date_filed"]),
    ).fetchone()[0]
    return n > 1


def run(conn, apply: bool) -> dict:
    # cite -> [(doc, parsed)]
    idx: dict[str, list] = {}
    for d in INCOMING.rglob("*.doc"):
        try:
            p = _parse(_doc_to_text(d))
        except Exception:  # noqa: BLE001
            p = None
        if p and p.get("primary_citation"):
            idx.setdefault(_clean_cite(p["primary_citation"]), []).append(
                (d, p))

    st = {"ambiguous_in": 0, "clear_win": 0, "defer_dup": 0,
          "defer_unclear": 0, "defer_lowsim": 0}
    report = []
    for line in REPORT.read_text(encoding="utf-8").splitlines()[1:]:
        f = line.split("\t")
        if f[0] != "AMBIGUOUS":
            continue
        st["ambiguous_in"] += 1
        cite = _clean_cite(f[1])
        docs = idx.get(cite, [])
        # the doc whose parsed caption == the reported one
        doc_parsed = None
        for d, p in docs:
            if (p.get("case_name") or "?")[:60] == (f[2] or "?")[:60]:
                doc_parsed = (d, p)
                break
        if not doc_parsed:
            st["defer_unclear"] += 1
            continue
        d, p = doc_parsed
        wl_sn = _surnames(p.get("case_name", ""))
        if not wl_sn:
            st["defer_unclear"] += 1
            continue
        cands = _candidates(conn, [cite])
        hit = [c for c in cands
               if _surnames(c["case_name"]) & wl_sn]
        if len(hit) != 1:
            st["defer_unclear"] += 1
            report.append(f"DEFER_UNCLEAR\t{cite}\t{p.get('case_name','?')[:50]}"
                          f"\t{len(hit)} surname-candidates")
            continue
        cand = hit[0]
        if _is_dup_member(conn, cand):
            st["defer_dup"] += 1
            report.append(f"DEFER_DUP\t{cite}\t{cand['case_name'][:50]}"
                          f"\toid={cand['id']} (dup pair)")
            continue
        wl_text = p.get("full_bound_text") or p.get("opinion_text") or ""
        sim = jaccard(
            shingles(normalize_words(
                conn.execute("SELECT text_content FROM opinions WHERE id=?",
                             (cand["id"],)).fetchone()[0])),
            shingles(normalize_words(wl_text)))
        if sim < 0.20:
            st["defer_lowsim"] += 1
            report.append(f"DEFER_LOWSIM\t{cite}\t{cand['case_name'][:50]}"
                          f"\toid={cand['id']} jaccard={sim:.2f}")
            continue
        st["clear_win"] += 1
        # Actually archive the .doc (real path), like receive_westlaw —
        # a placeholder path breaks source_files_on_disk.
        rel = (_archive_doc(d, p.get("primary_citation", ""),
                            p.get("case_name", "?")) if apply
               else f"N.W.2d/(clearwin-dry)/{d.name}")
        # _promote handles its own changelog/authority/validation_status
        # under BATCH (imported BATCH is receive_westlaw's; pass ours by
        # temporarily setting the module global).
        import ndcourts_mcp.receive_westlaw as RW
        old = RW.BATCH
        RW.BATCH = BATCH
        try:
            msg = _promote(conn, cand["id"], p, rel, apply)
        finally:
            RW.BATCH = old
        report.append(f"CLEAR_WIN\t{cite}\t{cand['case_name'][:50]}"
                       f"\toid={cand['id']}\t{msg}")

    rpt = Path("triage") / f"{BATCH}.tsv"
    rpt.write_text("kind\tcite\tcase\tdetail\n" + "\n".join(report),
                   encoding="utf-8")
    if apply:
        log_provenance(
            conn, operation="resolve_westlaw_clearwins",
            command="python -m ndcourts_mcp.resolve_westlaw_clearwins --apply",
            rows_affected=st["clear_win"],
            notes=(f"batch {BATCH}; surname-anchored clear-win promotes "
                   f"from the receive ambiguous queue: "
                   f"clear_win={st['clear_win']} "
                   f"defer_dup={st['defer_dup']} "
                   f"defer_unclear={st['defer_unclear']} "
                   f"defer_lowsim={st['defer_lowsim']}; "
                   f"revert via cleanup revert {BATCH} then "
                   f"align_primary_source --apply"),
        )
        conn.commit()
    return st, rpt


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    conn = get_connection(args.db)
    try:
        st, rpt = run(conn, apply=args.apply)
    finally:
        conn.close()
    mode = "APPLIED" if args.apply else "DRY RUN"
    print(f"=== clear-wins: {mode} (batch {BATCH}) ===")
    for k, v in st.items():
        print(f"  {k:<16} {v}")
    print(f"  report -> {rpt}")


if __name__ == "__main__":
    main()
