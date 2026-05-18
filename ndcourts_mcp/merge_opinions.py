"""§6 duplicate-row merge engine.

CourtListener double-ingested many pre-Westlaw opinions under two
cluster_ids: a parties caption ("Loe v. Ovind", high cluster_id, CL
mis-defaulted author, full panel in `judges`, 0 inbound cites) and a
matter caption ("In re Estate of Brudevig", low cluster_id, correct
per-opinion author, thin `judges`, the inbound citations). Same cite,
same date, near-identical text. They are ONE opinion.

`merge_pair` collapses drop → keep best-of-breed:
  * keep.case_name  := canonical_name (caller-supplied, human-reviewed)
  * keep.judges     := the fuller of the two panels
  * keep.author     := keep's own; fall back to drop only if keep empty
  * text_content    := UNTOUCHED (the post-merge Westlaw receive re-run
                       installs the authoritative bound text; this pass
                       only dedups + re-points, never rewrites opinion
                       text — keeps the scope clean and reversible)
  * every opinion-referencing row (citations, opinion_sources,
    text_citations, cited_by both directions, changelog, review_flags,
    quality_scores, validation_status, westlaw_requests,
    cite_extract_progress, duplicate_candidates) re-pointed drop → keep
    with constraint-aware dedup; self-cites dropped
  * opinions row `drop` deleted (FTS stays correct via the AD/AU
    triggers; no manual FTS surgery)

Every mutation is logged to changelog under the batch; a final
log_provenance row records the run with a revert recipe. Snapshot +
invariants + dry-run discipline is the caller's responsibility (the
__main__ driver enforces dry-run default).
"""

from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path

from .db import DEFAULT_DB_PATH, get_connection, log_change, log_provenance
from .multisource_diff import jaccard, normalize_words, shingles

BATCH = f"section6-dedup-{date.today().isoformat()}"

# Two rows sharing a cite+date are the same opinion only if their text
# agrees this closely; below this they are distinct opinions on a
# shared reporter page and must NOT be merged.
_DUP_FLOOR = 0.55


def _panel_len(j: str | None) -> int:
    return len(re.findall(r"[A-Za-z]+", j or ""))


def _canonical_name(matter_name: str) -> str:
    """Conservative: only the unambiguous probate transform
    'In Re X's Estate' / 'In Re Estate of X' -> 'Estate of X' (current
    ND Supreme Court style). Every other matter caption is preserved
    verbatim — dedup must not impose a regex-guessed caption on
    juvenile/guardianship/will/disciplinary matters; authoritative
    re-captioning of those is a separate human pass."""
    s = matter_name.strip()
    m = re.match(r"In Re\s+(.+?)'s Estate$", s, re.I)
    if m:
        return f"Estate of {m.group(1).strip()}"
    m = re.match(r"In Re\s+Estate of\s+(.+)$", s, re.I)
    if m:
        return f"Estate of {m.group(1).strip()}"
    return s


def _dedup_simple(conn, table, col, keep, drop):
    """Re-point `col` drop->keep for a table with no uniqueness
    constraint (citations, opinion_sources, changelog)."""
    conn.execute(f"UPDATE {table} SET {col}=? WHERE {col}=?", (keep, drop))


def _repoint_unique(conn, table, col, keep, drop, uniq_cols):
    """Re-point drop->keep, deleting drop rows that would violate
    uniq_cols against an existing keep row."""
    others = ", ".join(c for c in uniq_cols if c != col)
    where_other = " AND ".join(
        f"d.{c}=k.{c}" for c in uniq_cols if c != col) or "1=1"
    conn.execute(
        f"DELETE FROM {table} WHERE {col}=? AND EXISTS "
        f"(SELECT 1 FROM {table} k WHERE k.{col}=? "
        f"AND {where_other.replace('d.', table + '.')})",
        (drop, keep))
    conn.execute(f"UPDATE {table} SET {col}=? WHERE {col}=?", (keep, drop))


def _move_pk_table(conn, table, keep, drop):
    """opinion_id is PK: keep keep's row; move drop's only if keep
    has none."""
    has_keep = conn.execute(
        f"SELECT 1 FROM {table} WHERE opinion_id=?", (keep,)).fetchone()
    if has_keep:
        conn.execute(f"DELETE FROM {table} WHERE opinion_id=?", (drop,))
    else:
        conn.execute(
            f"UPDATE {table} SET opinion_id=? WHERE opinion_id=?",
            (keep, drop))


def _fix_single_primary(conn, table, keep):
    rows = conn.execute(
        f"SELECT id, is_primary FROM {table} WHERE opinion_id=? "
        f"ORDER BY is_primary DESC, id", (keep,)).fetchall()
    if not rows:
        return
    conn.execute(f"UPDATE {table} SET is_primary=0 WHERE opinion_id=?",
                 (keep,))
    conn.execute(f"UPDATE {table} SET is_primary=1 WHERE id=?",
                 (rows[0]["id"],))


def merge_pair(conn, keep: int, drop: int, canonical_name: str,
               apply: bool, batch: str = BATCH) -> dict:
    k = conn.execute("SELECT case_name, judges, author FROM opinions "
                      "WHERE id=?", (keep,)).fetchone()
    d = conn.execute("SELECT case_name, judges, author FROM opinions "
                      "WHERE id=?", (drop,)).fetchone()
    if k is None or d is None:
        raise SystemExit(f"merge_pair: missing row keep={keep} drop={drop}")

    new_judges = (d["judges"] if _panel_len(d["judges"])
                  > _panel_len(k["judges"]) else k["judges"])
    new_author = k["author"] or d["author"]

    plan = {
        "keep": keep, "drop": drop,
        "name": f'{k["case_name"]!r} -> {canonical_name!r}',
        "judges": f'{k["judges"]!r} -> {new_judges!r}',
        "author": f'{k["author"]!r} -> {new_author!r}',
    }
    if not apply:
        return plan

    # --- re-point every opinion-referencing table ---
    # citations / opinion_sources must DEDUP on re-point: duplicate
    # opinions share the same cites and source paths, so a blind
    # opinion_id UPDATE leaves duplicate (opinion_id, citation) /
    # (opinion_id, source_path) rows on the survivor. _fix_single_primary
    # (below) only fixes is_primary, not the dup rows themselves.
    _repoint_unique(conn, "citations", "opinion_id", keep, drop,
                    ["opinion_id", "citation"])
    _repoint_unique(conn, "opinion_sources", "opinion_id", keep, drop,
                    ["opinion_id", "source_path"])
    _repoint_unique(conn, "text_citations", "opinion_id", keep, drop,
                    ["opinion_id", "normalized"])
    # changelog is an append-only audit log: many rows per opinion are
    # expected and correct, so re-attribute without dedup.
    _dedup_simple(conn, "changelog", "opinion_id", keep, drop)
    # cited_by: both directions, drop self-cites, respect the unique pair
    conn.execute("DELETE FROM cited_by WHERE cited_opinion_id=? "
                 "AND citing_opinion_id=?", (drop, keep))
    conn.execute("DELETE FROM cited_by WHERE cited_opinion_id=? "
                 "AND citing_opinion_id=?", (keep, drop))
    for col, other in (("cited_opinion_id", "citing_opinion_id"),
                       ("citing_opinion_id", "cited_opinion_id")):
        conn.execute(
            f"DELETE FROM cited_by WHERE {col}=? AND EXISTS "
            f"(SELECT 1 FROM cited_by c WHERE c.{col}=? "
            f"AND c.{other}=cited_by.{other})", (drop, keep))
        conn.execute(f"UPDATE cited_by SET {col}=? WHERE {col}=?",
                     (keep, drop))
    conn.execute("DELETE FROM cited_by WHERE cited_opinion_id="
                 "citing_opinion_id")

    for tbl in ("review_flags", "quality_scores", "validation_status",
                "westlaw_requests", "cite_extract_progress"):
        _move_pk_table(conn, tbl, keep, drop)

    # duplicate_candidates: resolve the pair, re-point stragglers
    conn.execute(
        "UPDATE duplicate_candidates SET reviewed=1, resolved_as='merged', "
        "reviewed_at=strftime('%Y-%m-%dT%H:%M:%S','now') "
        "WHERE (opinion_a=? AND opinion_b=?) OR (opinion_a=? AND "
        "opinion_b=?)", (keep, drop, drop, keep))
    for col in ("opinion_a", "opinion_b"):
        other = "opinion_b" if col == "opinion_a" else "opinion_a"
        conn.execute(
            f"DELETE FROM duplicate_candidates WHERE {col}=? AND "
            f"({other}=? OR EXISTS (SELECT 1 FROM duplicate_candidates c "
            f"WHERE c.{col}=? AND c.{other}=duplicate_candidates.{other}))",
            (drop, keep, keep))
        conn.execute(
            f"UPDATE duplicate_candidates SET {col}=? WHERE {col}=?",
            (keep, drop))
    conn.execute("DELETE FROM duplicate_candidates WHERE opinion_a="
                 "opinion_b")

    _fix_single_primary(conn, "citations", keep)
    _fix_single_primary(conn, "opinion_sources", keep)

    # --- best-of-breed metadata on the survivor; text untouched ---
    if canonical_name != k["case_name"]:
        log_change(conn, batch, keep, "case_name", k["case_name"],
                   canonical_name, authority=f"§6 merge drop={drop}")
    if new_judges != k["judges"]:
        log_change(conn, batch, keep, "judges", k["judges"], new_judges,
                   authority=f"§6 merge drop={drop}")
    if new_author != k["author"]:
        log_change(conn, batch, keep, "author", k["author"], new_author,
                   authority=f"§6 merge drop={drop}")
    conn.execute(
        "UPDATE opinions SET case_name=?, judges=?, author=? WHERE id=?",
        (canonical_name, new_judges, new_author, keep))

    # Attribute the merge-audit row to the SURVIVOR: a changelog row
    # keyed to `drop` would itself re-introduce an FK reference to the
    # row we are about to delete (changelog.opinion_id -> opinions.id,
    # NO ACTION).
    log_change(conn, batch, keep, "merge.absorbed",
               f'oid {drop} {d["case_name"]!r}', None,
               authority=f"§6 duplicate-row merge: {drop} -> {keep}")
    conn.execute("DELETE FROM opinions WHERE id=?", (drop,))
    return plan


def _jac(conn, a: int, b: int) -> float:
    ta = conn.execute("SELECT text_content FROM opinions WHERE id=?",
                       (a,)).fetchone()[0] or ""
    tb = conn.execute("SELECT text_content FROM opinions WHERE id=?",
                       (b,)).fetchone()[0] or ""
    return jaccard(shingles(normalize_words(ta)),
                   shingles(normalize_words(tb)))


_MODERN_CUTOFF = "1997-01-01"   # ND adopted the YYYY-ND medium-neutral
                                # cite in 1997; the post-cutoff set is
                                # the released corpus -> vetted separately


def _corpus_pairs(conn) -> dict:
    """Corpus-wide §6 scan. Every citation shared by exactly two
    same-day opinions is a candidate pair. Classified:

      MERGE          pre-1997 pair, text jaccard >= _DUP_FLOOR -> a CL
                     double-ingest; (j) carried for the apply gate
      NEEDS_DECISION jaccard < _DUP_FLOOR -> distinct opinions sharing
                     a reporter page; never auto-merge
      DEFER_MODERN   keep.date_filed >= 1997 -> released-corpus set,
                     deferred by date (robust to cite-format variance:
                     neutral cites appear as both 'YYYY ND n' and
                     'YYYY N.D. n')
      DEFER_MULTI    cite shared by >2 rows -> not a simple pair

    keep = more inbound cited_by (tie -> lower cluster_id). MERGE rows
    sorted by (date, cite) so --limit batches are stable."""
    buckets = {"MERGE": [], "NEEDS_DECISION": [], "DEFER_MODERN": [],
               "DEFER_MULTI": []}
    rows = conn.execute(
        "SELECT citation FROM citations GROUP BY citation "
        "HAVING COUNT(DISTINCT opinion_id) >= 2").fetchall()
    for (cite,) in rows:
        cs = conn.execute(
            "SELECT o.id, o.case_name cn, o.date_filed df, "
            "o.cluster_id cl, (SELECT COUNT(*) FROM cited_by "
            "WHERE cited_opinion_id=o.id) cb FROM opinions o "
            "WHERE o.id IN (SELECT opinion_id FROM citations "
            "WHERE citation=?)", (cite,)).fetchall()
        if len(cs) > 2:
            buckets["DEFER_MULTI"].append((cite, len(cs)))
            continue
        a, b = cs
        if a["df"] != b["df"] or not a["df"]:
            continue                       # different opinions, skip
        if (a["cb"], -(a["cl"] or 0)) >= (b["cb"], -(b["cl"] or 0)):
            keep, drop = a, b
        else:
            keep, drop = b, a
        if keep["df"] >= _MODERN_CUTOFF:
            buckets["DEFER_MODERN"].append(
                (cite, keep["id"], keep["cn"], drop["id"], drop["cn"]))
            continue
        j = _jac(conn, keep["id"], drop["id"])
        if j < _DUP_FLOOR:
            buckets["NEEDS_DECISION"].append(
                (cite, keep["id"], keep["cn"], drop["id"], drop["cn"],
                 f"jaccard {j:.2f} < {_DUP_FLOOR} — distinct/shared-page"))
            continue
        buckets["MERGE"].append(
            (keep["df"], cite, keep["id"], keep["cn"], drop["id"],
             drop["cn"], j))
    buckets["MERGE"].sort(key=lambda t: (t[0], t[1]))
    return buckets


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=None,
                    help="apply at most N merges this run (required "
                         "with --apply — enforces reviewed batches)")
    ap.add_argument("--min-jaccard", type=float, default=0.85,
                    help="only MERGE rows at/above this text-jaccard "
                         "are apply-eligible (default 0.85; lower "
                         "tranches want separate review)")
    args = ap.parse_args()
    if args.apply and not args.limit:
        raise SystemExit("--apply requires --limit N (never blind-apply "
                          "the full corpus; review in batches)")
    conn = get_connection(args.db)
    batch = f"section6-dedup-corpus-{date.today().isoformat()}"
    b = _corpus_pairs(conn)
    merges = b["MERGE"]
    applied = elig = stale = 0
    out = ["kind\tcite\tkeep\tdrop\tname_old->canonical\tdetail"]
    for _df, cc, keep, kn, drop, dn, j in merges:
        canon = _canonical_name(kn)
        # An opinion can sit in two shared-cite pairs; once an earlier
        # merge in THIS batch deletes it, a later pair is stale. Skip
        # and converge on re-run (the scan always reflects live rows).
        if not conn.execute("SELECT 1 FROM opinions WHERE id IN (?,?) "
                            "GROUP BY 1 HAVING COUNT(*)=2",
                            (keep, drop)).fetchone():
            stale += 1
            out.append(f"SKIPPED_STALE\t{cc}\t{keep}\t{drop}\t"
                       f"{kn!r}\tone row already merged in this batch — "
                       f"re-run to converge")
            continue
        if j < args.min_jaccard:
            p = merge_pair(conn, keep, drop, canon, apply=False,
                           batch=batch)
            out.append(f"MERGE-HOLD-LOWJAC\t{cc}\t{keep}\t{drop}\t"
                       f"{kn!r} -> {canon!r}\tj={j:.2f} < "
                       f'{args.min_jaccard}; drop={dn!r}; {p["judges"]}')
            continue
        elig += 1
        do = args.apply and applied < args.limit
        p = merge_pair(conn, keep, drop, canon, apply=do, batch=batch)
        if do:
            applied += 1
        tag = "MERGE-APPLIED" if do else "MERGE-PENDING"
        out.append(f"{tag}\t{cc}\t{keep}\t{drop}\t{kn!r} -> {canon!r}\t"
                   f'j={j:.2f}; drop={dn!r}; {p["judges"]}; {p["author"]}')
    for cc, ki, kn, di, dn, why in b["NEEDS_DECISION"]:
        out.append(f"NEEDS_DECISION\t{cc}\t{ki}\t{di}\t"
                   f"{kn!r} | {dn!r}\t{why}")
    for cc, ki, kn, di, dn in b["DEFER_MODERN"]:
        out.append(f"DEFER_MODERN\t{cc}\t{ki}\t{di}\t"
                   f"{kn!r} | {dn!r}\t1997+ neutral-cite; separate pass")
    for cc, n in b["DEFER_MULTI"]:
        out.append(f"DEFER_MULTI\t{cc}\t\t\t\t{n} rows share this cite")
    rpt = Path("triage") / f"{batch}.tsv"
    rpt.write_text("\n".join(out), encoding="utf-8")
    if args.apply and applied:
        log_provenance(
            conn, operation="section6_dedup_corpus",
            command=f"python -m ndcourts_mcp.merge_opinions --apply "
                    f"--limit {args.limit}",
            rows_affected=applied,
            notes=(f"batch {batch}; corpus-wide §6 merge, applied "
                   f"{applied} of {len(merges)} MERGE candidates "
                   f"(reviewed batch, limit {args.limit}); revert via "
                   f"snapshot restore (row deletions not changelog-"
                   f"revertible)"))
        conn.commit()
    held = len(merges) - elig
    print(f"=== §6 corpus dedup: {'APPLIED' if args.apply else 'DRY RUN'} "
          f"(batch {batch}) ===")
    print(f"  MERGE total        {len(merges)} "
          f"(>= {args.min_jaccard}: {elig} eligible"
          f"{f', {applied} applied' if args.apply else ''}; "
          f"< {args.min_jaccard}: {held} held-lowjac)")
    if stale:
        print(f"  skipped_stale      {stale} (re-run to converge)")
    print(f"  needs_decision     {len(b['NEEDS_DECISION'])}")
    print(f"  defer_modern       {len(b['DEFER_MODERN'])}")
    print(f"  defer_multi        {len(b['DEFER_MULTI'])}")
    print(f"  report -> {rpt}")
    conn.close()


if __name__ == "__main__":
    main()
