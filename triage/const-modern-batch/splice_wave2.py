#!/usr/bin/env python3
"""Apply Wave-2 verification outcomes to scratch (/tmp/const-scratch.db).

1. Correct art XII §2: the Wave-1 prior was wrong (3rd-read adjudication picked
   the second read); replace that scratch version's text with the second read.
2. Splice 3 NEW Wave-2 redlines (art II §1, IX §7, XII §1): MECH-passed, single
   read, no clean-BB witness -> scratch + needs-2nd-read.
3. Report (no DB change) the promotions: 9 second-reads confirmed on Wave-1 text,
   plus the create-section / needs-base-source dispositions.
Idempotent for the new splices (batch-scoped delete + re-insert)."""
import json, re, sqlite3
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB = "/tmp/const-scratch.db"
W1_BATCH = "modern-redline-agent-2026-06-14"
W2_BATCH = "modern-redline-wave2-2026-06-14"


def norm(s):
    return " ".join((s or "").split())


def out(name):
    return {o["citation"]: o for o in json.loads((HERE / "out" / name).read_text())}


def main():
    con = sqlite3.connect(DB)
    sr = out("secondread.json")
    b6 = out("wave2-batch-6.json"); b8 = out("wave2-batch-8.json")

    # --- 1. correct art XII §2 (replace Wave-1 prior text with the second read) ---
    cite = "N.D. Const. art. XII, § 2"
    prior = norm(sr[cite]["prior_text"])
    pid = con.execute("SELECT id FROM provisions WHERE citation=?", (cite,)).fetchone()[0]
    row = con.execute("""SELECT id FROM provision_versions WHERE provision_id=? AND batch=?
                         AND effective_end IS NOT NULL""", (pid, W1_BATCH)).fetchone()
    if row:
        con.execute("UPDATE provision_versions SET text_content=?, "
                    "source_authority='agent-read redline (3rd-read adjudicated B)' WHERE id=?",
                    (prior, row[0]))
        con.execute("INSERT INTO changelog (batch, provision_id, version_id, field, old_value, "
                    "new_value, authority) VALUES (?,?,?,?,?,?,?)",
                    (W2_BATCH, pid, row[0], "version_text_correction", "wave-1 prior (wrong)",
                     "3rd-read adjudicated second-read prior", "multi-agent redline campaign wave 2"))
        print(f"corrected XII §2 prior (version {row[0]})")
    else:
        print("WARN: XII §2 wave-1 prior version not found")

    # --- 2. splice 3 new Wave-2 redlines (needs-2nd-read) ---
    NEW = {"N.D. Const. art. II, § 1": b6, "N.D. Const. art. IX, § 7": b6,
           "N.D. Const. art. XII, § 1": b8}
    for cite, src in NEW.items():
        o = src[cite]; d1 = o["amendment_date"]; prior = norm(o["prior_text"])
        r = con.execute("SELECT id, current_version_id FROM provisions WHERE citation=?", (cite,)).fetchone()
        pid, vid = r
        con.execute("DELETE FROM provision_versions WHERE provision_id=? AND batch=?", (pid, W2_BATCH))
        con.execute("UPDATE provision_versions SET effective_start=? WHERE id=?", (d1, vid))
        end = (date.fromisoformat(d1) - timedelta(days=1)).isoformat()
        nvid = con.execute("INSERT INTO provision_versions (provision_id, effective_start, "
            "effective_end, text_content, source_authority, batch) VALUES (?,?,?,?,?,?)",
            (pid, "1981-01-01", end, prior,
             "agent-read redline (wave2, needs-2nd-read)", W2_BATCH)).lastrowid
        con.execute("INSERT INTO changelog (batch, provision_id, version_id, field, new_value, authority) "
            "VALUES (?,?,?,?,?,?)", (W2_BATCH, pid, nvid, "version_splice_agent_redline",
            f"[1981-01-01 -> {end}] prior reconstructed by agent (needs-2nd-read)",
            "multi-agent redline campaign wave 2"))
        print(f"spliced {cite}  [1981-01-01 -> {end}]")

    con.commit()

    # --- 3. integrity ---
    g = con.execute("""WITH v AS (SELECT provision_id, effective_start, effective_end,
      LEAD(effective_start) OVER (PARTITION BY provision_id ORDER BY effective_start) nxt FROM provision_versions)
      SELECT count(*) FROM v WHERE nxt IS NOT NULL AND effective_end IS NOT NULL AND effective_end!=''
      AND date(effective_end)!=date(nxt) AND date(effective_end,'+1 day')!=date(nxt)""").fetchone()[0]
    m = con.execute("""SELECT count(*) FROM (SELECT p.id FROM provisions p
      JOIN provision_versions v ON v.provision_id=p.id WHERE p.corpus='const'
      AND (v.effective_end IS NULL OR v.effective_end='') GROUP BY p.id HAVING count(*)>1)""").fetchone()[0]
    nrec = con.execute("""SELECT count(*) FROM (SELECT p.id FROM provisions p
      JOIN provision_versions v ON v.provision_id=p.id
      WHERE p.corpus='const' AND p.citation LIKE '%art.%' AND p.citation NOT LIKE '%amend%'
      GROUP BY p.id HAVING count(*)>1)""").fetchone()[0]
    print(f"\nintegrity: gaps/overlaps={g}  >1-open={m}  (expect 0/0)")
    print(f"modern provisions now multi-version (reconstructed): {nrec}")
    con.close()


if __name__ == "__main__":
    main()
