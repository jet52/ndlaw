#!/usr/bin/env python3
"""art. IX §12/§13: fix stale current text + reconstruct chains.

ndconst.org's snapshot for §12/§13 still carries pre-2024 terminology though it
records amendment 166 (2023 SCR 4001 "Updated Terminology", eff. 2024-12-05) as
applied. So the stored "current" text is actually the pre-2024 version. The TRUE
current text (verified against bill 23-3015) lives in
out-multi/multi-batch-ix.json (am166.version_after).

Modes:
  --db <path> --live     : just correct the current-version text to the TRUE
                           current (flat modern layer; e.g. live constitution.db).
  --db <path> --chain     : correct current text AND splice prior versions
                           (the scratch reconstruction).
Gate: the DB's stored current text == am166.version_before (stale, fresh pull) OR ==
am166.version_after (base already corrected — replay against an evolved base); the
text-correction step runs only in the stale case. Each reverse_edit_list applies;
chain continuity holds.
Idempotent (batch-scoped). Run after fix_amend167 (which set §12/§13 start 2024-12-05).
"""
import argparse, json, re, sqlite3, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
from ndcourts_mcp import corpus  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = json.loads((HERE / "out-multi" / "multi-batch-ix.json").read_text())
BATCH = "modern-ix-stale-text-2026-06-14"


def norm(s):
    return " ".join((s or "").split())


def kn(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def apply_edits(t, edits):
    for a, b in edits:
        if t.count(a) != 1:
            raise ValueError(f"anchor x{t.count(a)}: {a[:40]!r}")
        t = t.replace(a, b)
    return t


def _heading(con, vid):
    h = con.execute("SELECT p.heading FROM provisions p JOIN provision_versions v "
                    "ON v.provision_id=p.id WHERE v.id=?", (vid,)).fetchone()
    return (h[0] if h else None) or ""


def fts_replace(con, vid, cite, old_text, new_text):
    """provisions_fts is external-content FTS5 (manually managed): remove the old
    row with the 'delete' command (needs the originally-indexed values), then add."""
    head = _heading(con, vid)
    con.execute("INSERT INTO provisions_fts(provisions_fts, rowid, citation, heading, text_content) "
                "VALUES('delete', ?, ?, ?, ?)", (vid, cite, head, old_text))
    corpus.index_version_fts(con, vid, cite, head, new_text)


def fts_add(con, vid, cite, text):
    corpus.index_version_fts(con, vid, cite, _heading(con, vid), text)


def day_before(d):
    from datetime import date, timedelta
    return (date.fromisoformat(d) - timedelta(days=1)).isoformat()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", type=Path, required=True)
    ap.add_argument("--chain", action="store_true", help="also splice prior versions")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    con = sqlite3.connect(args.db)
    prov = {o["citation"]: o for o in OUT}

    plans = []
    for cite, o in prov.items():
        r = con.execute("SELECT p.id, p.current_version_id, v.text_content "
                        "FROM provisions p JOIN provision_versions v ON v.id=p.current_version_id "
                        "WHERE p.citation=?", (cite,)).fetchone()
        if not r:
            print(f"  SKIP {cite}: not in DB"); continue
        pid, vid, stale = r[0], r[1], norm(r[2])
        amds = o["amendments"]
        true_current = norm(amds[-1]["version_after_text"])
        # gates
        probs = []
        # The DB current may be the STALE ndconst.org text (a fresh pull) OR already the
        # corrected version_after (base absorbed the correction in a prior build). Accept
        # either; only the stale case needs the text-correction step below.
        cur_kn = kn(stale)
        already_corrected = cur_kn == kn(true_current)
        if cur_kn != kn(amds[-1]["version_before_text"]) and not already_corrected:
            probs.append("stored current matches neither version_before (stale) nor version_after (corrected)")
        for a in amds:
            try:
                got = apply_edits(norm(a["version_after_text"]), [tuple(e) for e in a["reverse_edit_list"]])
                if kn(got) != kn(a["version_before_text"]):
                    probs.append(f"mech mismatch @ {a['amendment_number']}")
            except Exception as e:
                probs.append(f"mech err @ {a['amendment_number']}: {e}")
        for e, l in zip(amds, amds[1:]):
            if kn(l["version_before_text"]) != kn(e["version_after_text"]):
                probs.append(f"continuity {e['amendment_number']}->{l['amendment_number']}")
        plans.append((cite, pid, vid, stale, true_current, amds, probs, already_corrected))

    print(f"DB: {args.db}  mode={'chain' if args.chain else 'live-text-only'}")
    ok = True
    for cite, pid, vid, stale, tc, amds, probs, already_corrected in plans:
        state = "already-corrected" if already_corrected else "stale->correct"
        print(f"  {cite:26} {state}; cur={len(stale)}c true={len(tc)}c  gates={'OK' if not probs else probs}")
        if probs:
            ok = False
    if not ok:
        print("GATE FAIL — not applying."); con.close(); return
    if not args.apply:
        print("(dry run) re-run with --apply"); con.close(); return

    for cite, pid, vid, stale, tc, amds, probs, already_corrected in plans:
        # 1. correct the current version text — only if the DB still holds the stale text
        if not already_corrected:
            fts_replace(con, vid, cite, stale, tc)
            con.execute("UPDATE provision_versions SET text_content=?, "
                        "source_authority='current text (ndconst.org, corrected for amend 166)' WHERE id=?", (tc, vid))
            con.execute("INSERT INTO changelog (batch, provision_id, version_id, field, old_value, new_value, authority) "
                        "VALUES (?,?,?,?,?,?,?)", (BATCH, pid, vid, "stale_current_text_corrected",
                        "pre-2024 terminology (ndconst.org stale)", "amend 166 enacted text (bill 23-3015)",
                        "2023 SCR 4001"))
        # 2. chain mode: splice priors
        if args.chain:
            con.execute("DELETE FROM provision_versions WHERE provision_id=? AND batch=?", (pid, BATCH))
            dates = [a["effective_date"] for a in amds]
            con.execute("UPDATE provision_versions SET effective_start=? WHERE id=?", (dates[-1], vid))
            # head [1981, d0)
            ivals = [("1981-01-01", day_before(dates[0]), norm(amds[0]["version_before_text"]),
                      f"head before amend {amds[0]['amendment_number']}")]
            for i in range(len(amds) - 1):
                ivals.append((dates[i], day_before(dates[i + 1]), norm(amds[i]["version_after_text"]),
                              f"amend {amds[i]['amendment_number']}"))
            for start, end, text, note in ivals:
                nvid = con.execute("INSERT INTO provision_versions (provision_id, effective_start, effective_end, "
                    "text_content, source_authority, batch) VALUES (?,?,?,?,?,?)",
                    (pid, start, end, text, f"agent-read chain ({note})", BATCH)).lastrowid
                fts_add(con, nvid, cite, text)
                con.execute("INSERT INTO changelog (batch, provision_id, version_id, field, new_value, authority) "
                    "VALUES (?,?,?,?,?,?)", (BATCH, pid, nvid, "version_splice_chain",
                    f"[{start} -> {end}] {note}", "multi-agent chain campaign"))
    con.commit()

    # integrity
    g = con.execute("""WITH v AS (SELECT provision_id, effective_start, effective_end,
      LEAD(effective_start) OVER (PARTITION BY provision_id ORDER BY effective_start) nxt FROM provision_versions)
      SELECT count(*) FROM v WHERE nxt IS NOT NULL AND effective_end IS NOT NULL AND effective_end!=''
      AND date(effective_end)!=date(nxt) AND date(effective_end,'+1 day')!=date(nxt)""").fetchone()[0]
    print(f"APPLIED. integrity gaps={g}")
    for cite, pid, *_ in plans:
        vs = con.execute("SELECT effective_start, COALESCE(effective_end,'open') FROM provision_versions "
                         "WHERE provision_id=? ORDER BY effective_start", (pid,)).fetchall()
        print(f"  {cite}: {[f'{s}->{e}' for s,e in vs]}")
    con.close()


if __name__ == "__main__":
    main()
