"""Corpus-wide Type Y supplemental-publication detector (read-only).

Type Y: a Westlaw .doc paired to a DB opinion whose own "All Citations"
N.W. cite differs from every N.W. cite the DB row carries. In the bound
N.D. Reports era the reporter sometimes published a supplemental
(rehearing, concurrence, follow-on per curiam) at a *discontinuous* N.W.
page while sharing the N.D. starting page; the volume-based ingest paired
that supplemental .doc with the main DB row on the shared N.D. cite. The
correct model is one DB row per distinct publication, so each mismatch is
a candidate for a new opinion row (see insert_supplemental_opinions).

This module only *detects* and reports — it never writes to the DB.
Output: triage/type-y-sweep-<date>.tsv with one row per flagged pairing.

Usage:
    python -m ndcourts_mcp.sweep_type_y [--db DB] [--limit N] [--out PATH]
"""

from __future__ import annotations

import argparse
import os
import re
import signal
import subprocess
import sys
from datetime import date
from pathlib import Path

from . import typey
from .db import DEFAULT_DB_PATH, get_connection
from .ingest_westlaw import _parse_westlaw_doc


def _doc_to_text_hard(path: Path, timeout: int = 25) -> str:
    """textutil .doc->txt with a process-group hard kill on timeout.

    The shared ingest_westlaw._doc_to_text uses subprocess.run(timeout=),
    which on a wedged/D-state textutil child fails to reap it and blocks
    indefinitely (observed: a single bad .doc hung a corpus sweep for
    hours). Here textutil runs in its own session so a timeout can
    SIGKILL the whole process group and move on."""
    p = subprocess.Popen(
        ["textutil", "-convert", "txt", "-stdout", str(path)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, start_new_session=True,
    )
    try:
        out, err = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except ProcessLookupError:
            pass
        p.wait()
        raise
    if p.returncode != 0:
        raise RuntimeError(f"textutil rc={p.returncode} on {path}: {err[:120]}")
    return out

REFS_ROOT = Path.home() / "refs" / "nd" / "opin"


def _resolve(sp: str) -> Path:
    """opinion_sources.source_path is a mix of absolute (bound-volume
    ingest) and refs-relative (receive_westlaw _archive_doc) paths.
    Resolve relative ones against REFS_ROOT — same rule invariants uses."""
    return Path(sp) if os.path.isabs(sp) else REFS_ROOT / sp


_HDR = ("kind\toid\tdate_filed\tcase_name\tjac\tnd_shared\t"
        "db_nw\tdoc_nw\tdb_cites\tdoc_path\n")


def _row_tsv(r: dict) -> str:
    return "\t".join(str(x) for x in (
        r["kind"], r["id"], r["date_filed"], r["case_name"],
        r.get("jac", ""), r.get("nd", ""),
        r.get("db_nw", ""), r.get("doc_nw", ""),
        (r["cites"] or "").replace("\t", " "),
        r["source_path"])) + "\n"


def _classify(r) -> dict:
    """Sweep wrapper around the shared `typey.classify` discriminator.
    Handles the file-I/O framing (MISSING_DOC / PARSE_ERROR) the sweep
    needs and maps the pure result onto the byte-identical TSV row."""
    doc = _resolve(r["source_path"])
    if not doc.exists():
        return dict(r, kind="MISSING_DOC", doc_nw="", db_nw="", jac="", nd="")
    try:
        parsed = _parse_westlaw_doc(_doc_to_text_hard(doc)) or {}
    except Exception as e:  # noqa: BLE001 — incl. TimeoutExpired (hard-killed)
        return dict(r, kind="PARSE_ERROR", doc_nw=type(e).__name__,
                    db_nw=str(e)[:50], jac="", nd="")
    res = typey.classify(parsed, r["cites"] or "", r["text_content"] or "")
    if res.kind == typey.MATCH:
        return {}  # .doc N.W. cite matches the DB row — normal pairing
    if res.kind == typey.DOC_NO_NW:
        return dict(r, kind="DOC_NO_NW", doc_nw="", db_nw="", jac="", nd="")
    if res.kind == typey.DB_NO_NW:
        return dict(r, kind="DB_NO_NW", doc_nw=typey.fmt_nw(res.doc_nw),
                    db_nw="", jac="", nd="")
    return dict(r, kind=res.kind,
                doc_nw=typey.fmt_nw(res.doc_nw),
                db_nw=typey.fmt_nw(res.db_nw),
                jac=f"{res.jac:.2f}", nd="Y" if res.nd_shared else "n")


def sweep(conn, limit: int | None, out_path: Path,
          resume: bool) -> dict:
    rows = conn.execute(
        """SELECT o.id, o.date_filed, o.case_name, o.text_content,
                  s.source_path,
                  (SELECT GROUP_CONCAT(citation, ' | ') FROM citations c
                    WHERE c.opinion_id = o.id) AS cites
           FROM opinion_sources s
           JOIN opinions o ON o.id = s.opinion_id
           WHERE s.source_reporter = 'westlaw'
             AND s.source_path LIKE '%.doc'
           ORDER BY o.date_filed, o.id"""
    ).fetchall()
    if limit:
        rows = rows[:limit]

    done: set[int] = set()
    progress = out_path.with_suffix(".progress")
    if resume and out_path.exists():
        for ln in out_path.read_text().splitlines()[1:]:
            parts = ln.split("\t")
            if len(parts) > 1 and parts[1].isdigit():
                done.add(int(parts[1]))
        mode = "a"
    else:
        mode = "w"

    from collections import Counter
    tally: Counter = Counter()
    n = len(rows)
    with out_path.open(mode) as f:
        if mode == "w":
            f.write(_HDR)
        for i, r in enumerate(rows):
            if r["id"] in done:
                continue
            if i % 100 == 0:
                msg = (f"{i}/{n} scanned, {sum(tally.values())} flagged "
                       f"(oid {r['id']}, {r['date_filed']})")
                progress.write_text(msg)
                print("  .. " + msg, file=sys.stderr, flush=True)
            res = _classify(dict(r))
            if res:
                f.write(_row_tsv(res))
                f.flush()
                tally[res["kind"]] += 1
    progress.write_text(f"DONE {n}/{n}")
    print(f"  done: {n} scanned", file=sys.stderr)
    return dict(tally)




def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--resume", action="store_true",
                    help="append, skipping oids already in --out")
    ap.add_argument("--out", type=Path,
                    default=Path("triage")
                    / f"type-y-sweep-{date.today().isoformat()}.tsv")
    args = ap.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection(args.db)
    try:
        tally = sweep(conn, args.limit, args.out, args.resume)
    finally:
        conn.close()
    print(f"wrote -> {args.out}")
    for k, c in sorted(tally.items(), key=lambda kv: -kv[1]):
        print(f"  {k}: {c}")


if __name__ == "__main__":
    main()
