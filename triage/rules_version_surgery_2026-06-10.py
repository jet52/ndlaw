"""rules.db provision_versions surgery — fixes every version_intervals flag
(11 zero-width) plus the foreign-page attachments behind them.

Root causes (all verified against the live ndcourts.gov pages 2026-06-10 —
page H1 titles + Effective Dates; see CHANGELOG-data.md):

A. FOREIGN PAGES filed as rule versions: the ingest followed version-history
   links to documents that are not the rule (their H1 names another
   instrument). Moved to their own provisions (created here):
     * appendix-k(-2)        -> N.D.R.Ct. appendix k        (was in 3.5)
     * appendix-f(-1)        -> N.D.R.Ct. appendix f        (was in 8.8)
     * appendix-a-to-rule-8-9 -> N.D.R.Ct. appendix a to rule 8.9 (was in 8.9)
     * table-a(-2)           -> N.D.R.Civ.P. Table A        (was in 81)
     * 8-3-1(-1)             -> N.D.R.Ct. 8.3.1             (was in 8.3)
   (Admin Order 21 carried five Admin RULE 21 pages — byte-identical
   duplicates of provision 505's own rows -> deleted, not moved.)

B. SAME-DATE REPUBLICATION TWINS: two site pages, same effective date,
   (near-)identical text. The non-current twin is deleted (full text is in
   the snapshot; ratio noted in changelog).

C. RENUMBER/REPEAL PAGES with the successor's effective date: the old text's
   true adoption date is not on the page -> effective_start=NULL (schema:
   'NULL == original/unknown, in force from -inf'), end = supersession date.
     * 4.1: pre-repeal text [NULL -> 2000-03-01]; repeal notice
       [2000-03-01 -> NULL]; provision status -> 'repealed'.
     * 5.3: pre-renumber text (page titled 'RULE 8.1 RECEIVERS')
       [NULL -> 2013-03-01].
     * appendix b: pre-2000 form [NULL -> 2000-03-01].

Maintains provisions.current_version_id and the external-content FTS
(delete + re-add for moved rows). Snapshot: rules.db.bak-pre-version-surgery-
2026-06-10. Dry-run default; --apply writes.
"""
import sqlite3, sys

BATCH = "rules-version-surgery-2026-06-10"
apply = "--apply" in sys.argv
conn = sqlite3.connect("rules.db")
conn.row_factory = sqlite3.Row

def log(provision_id, version_id, field, old, new, authority):
    conn.execute(
        "INSERT INTO changelog (batch, provision_id, version_id, field, old_value, new_value, authority) "
        "VALUES (?,?,?,?,?,?,?)",
        (BATCH, provision_id, version_id, field, str(old), str(new), authority))

def fts_delete(vid):
    # external-content FTS: the 'delete' command needs the originally indexed
    # values, which index_version_fts built from the provisions join — rebuild
    # the same tuple from the version's CURRENT (pre-change) provision.
    r = conn.execute(
        "SELECT p.citation, p.heading, v.text_content FROM provision_versions v "
        "JOIN provisions p ON p.id = v.provision_id WHERE v.id=?", (vid,)).fetchone()
    if r:
        conn.execute(
            "INSERT INTO provisions_fts(provisions_fts, rowid, citation, heading, text_content) "
            "VALUES('delete', ?, ?, ?, ?)", (vid, r[0], r[1] or "", r[2]))

def fts_add(vid, citation, heading, text):
    conn.execute("INSERT INTO provisions_fts(rowid, citation, heading, text_content) VALUES (?,?,?,?)",
                 (vid, citation, heading or "", text))

import re
def cite_key(citation):
    s = citation.lower().replace("§", " ")
    s = re.sub(r"(?<=[a-z])\.", "", s)
    s = re.sub(r"\b(?:sec|section|subsec|subsection|subdiv|subdivision)\b", " ", s)
    s = re.sub(r"[^a-z0-9.\- ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()

NEW_PROVISIONS = [
    # (citation, heading, [(version_id, start, end)], current_vid, from_provision)
    ("N.D.R.Ct. appendix k", "APPENDIX K. RULE 3.5 ELECTRONIC FILING REQUIREMENTS",
     [(1132, "2018-03-01", "2019-03-01"), (1134, "2019-03-01", None)], 1134, 316),
    ("N.D.R.Ct. appendix f", "APPENDIX F. RULE 8.8 ALTERNATIVE DISPUTE RESOLUTION STATEMENT",
     [(1236, "2001-03-01", "2003-03-01"), (1237, "2003-03-01", None)], 1237, 350),
    ("N.D.R.Ct. appendix a to rule 8.9", "APPENDIX A TO RULE 8.9. CODE OF MEDIATION ETHICS",
     [(1242, "2007-03-01", None)], 1242, 351),
    ("N.D.R.Civ.P. Table A", "TABLE A. SPECIAL STATUTORY PROCEEDINGS UNDER RULE 81",
     [(525, "2001-01-01", "2025-03-01"), (527, "2025-03-01", None)], 527, 118),
    ("N.D.R.Ct. 8.3.1",
     "RULE 8.3.1 CASE MANAGEMENT (DETERMINATION OF PARENTAL RIGHTS OR CHANGE OF RESIDENTIAL RESPONSIBILITY)",
     [(1209, "2018-03-01", "2021-03-01"), (1210, "2021-03-01", None)], 1210, 345),
]

INTERVAL_FIXES = [  # (version_id, provision_id, new_start_or_KEEP, new_end, why)
    (1131, 316, "KEEP", "2019-03-01", "3.5 v13 runs to v14 (3/1/2019) after appendix-k removal"),
    (1133, 316, "KEEP", "2021-03-01", "3.5 v14 runs to v15 (3/1/2021) after appendix-k removal"),
    (1235, 350, "KEEP", "2006-10-01", "8.8 2001 text runs to 8-8-2 (10/1/2006) after appendix-f removal"),
    (1241, 351, "KEEP", "2009-08-01", "8.9 2001 text runs to 8-9-2 (8/1/2009) after appendix removal"),
    (524, 118, "KEEP", "2011-03-01", "81 1990 text runs to 2011 amendment after Table A removal"),
    (1208, 345, "KEEP", None, "8.3 current page (eff 8/1/2017) is the live version after 8.3.1 removal"),
    (1978, 574, "KEEP", None, "Order 21 current page is the live version after Admin Rule 21 dups removed"),
    (1138, 317, None, "2000-03-01", "4.1 pre-repeal text; adoption date not on page (NULL start); repealed 3/1/2000"),
    (1137, 317, "KEEP", None, "4.1 repeal notice is the operative version from 3/1/2000"),
    (1145, 321, None, "2013-03-01", "pre-renumber text (page titled RULE 8.1 RECEIVERS); superseded 3/1/2013"),
    (1251, 354, None, "2000-03-01", "appendix b pre-2000 form (site shows successor's date); NULL start"),
    (1250, 354, "KEEP", None, "appendix b current page is the live version"),
    (1248, 353, "KEEP", None, "appendix a current page takes the full interval; -1 twin deleted"),
]

DELETES = [  # (version_id, provision_id, why)
    (1971, 574, "Admin RULE 21 page (ndsupctadminr/21-1), byte-identical dup of provision 505 v1703"),
    (1972, 574, "Admin RULE 21 page (21-2), dup of 505 v1704"),
    (1975, 574, "Admin RULE 21 page (21-3), dup of 505 v1705"),
    (1977, 574, "Admin RULE 21 page (21-4), dup of 505 v1706"),
    (1979, 574, "Admin RULE 21 page (21), dup of 505 v1707"),
    (1658, 496, "same-date republication twin of v1659 (13-11), byte-identical"),
    (1837, 537, "same-date republication twin of current v1838 (48), ratio 0.909"),
    (1914, 559, "same-date republication twin of v1915 (7-6), ratio 0.820"),
    (1249, 353, "same-date republication twin of current v1248 (appendix-a), ratio 0.999"),
]

CURRENT_REPOINT = {118: 526, 345: 1208, 353: 1248, 354: 1250, 574: 1978, 317: 1137}
STATUS = {317: "repealed"}

print("=== new provisions ===")
for citation, heading, vers, cur, frm in NEW_PROVISIONS:
    print(f"  {citation!r} <- versions {[v[0] for v in vers]} from provision {frm}")
print("=== interval fixes ===")
for vid, pid, ns, ne, why in INTERVAL_FIXES:
    print(f"  v{vid}: start={ns} end={ne} ({why[:60]})")
print("=== deletes ===")
for vid, pid, why in DELETES:
    print(f"  v{vid}: {why[:70]}")

if not apply:
    print("\nDRY RUN — no changes. Run with --apply.")
    sys.exit(0)

for citation, heading, vers, cur, frm in NEW_PROVISIONS:
    cu = conn.execute(
        "INSERT INTO provisions (corpus, citation, cite_key, heading, status, current_version_id) "
        "VALUES ('rule', ?, ?, ?, 'active', ?)", (citation, cite_key(citation), heading, cur))
    new_pid = cu.lastrowid
    for vid, start, end in vers:
        old = conn.execute("SELECT provision_id, effective_start, effective_end, text_content "
                           "FROM provision_versions WHERE id=?", (vid,)).fetchone()
        conn.execute("UPDATE provision_versions SET provision_id=?, effective_start=?, effective_end=? WHERE id=?",
                     (new_pid, start, end, vid))
        fts_delete(vid)
        fts_add(vid, citation, heading, old["text_content"])
        log(new_pid, vid, "version.provision",
            f"provision {frm} [{old['effective_start']},{old['effective_end']}]",
            f"provision {new_pid} ({citation}) [{start},{end}]",
            "page H1 names a distinct instrument; verified against live ndcourts.gov page 2026-06-10")
    log(new_pid, None, "provision.created", "", citation,
        "document was filed inside another rule's version history; now its own provision")

for vid, pid, ns, ne, why in INTERVAL_FIXES:
    old = conn.execute("SELECT effective_start, effective_end FROM provision_versions WHERE id=?", (vid,)).fetchone()
    new_start = old["effective_start"] if ns == "KEEP" else ns
    conn.execute("UPDATE provision_versions SET effective_start=?, effective_end=? WHERE id=?",
                 (new_start, ne, vid))
    log(pid, vid, "version.interval", f"[{old['effective_start']},{old['effective_end']}]",
        f"[{new_start},{ne}]", why)

for vid, pid, why in DELETES:
    fts_delete(vid)
    conn.execute("DELETE FROM provision_versions WHERE id=?", (vid,))
    log(pid, vid, "version.deleted", f"version {vid}", "", why + " (full row in pre-surgery snapshot)")

for pid, vid in CURRENT_REPOINT.items():
    old = conn.execute("SELECT current_version_id FROM provisions WHERE id=?", (pid,)).fetchone()[0]
    conn.execute("UPDATE provisions SET current_version_id=? WHERE id=?", (vid, pid))
    log(pid, None, "current_version_id", old, vid, "repointed after surgery to the end-NULL version")
for pid, st in STATUS.items():
    conn.execute("UPDATE provisions SET status=? WHERE id=?", (st, pid))
    log(pid, None, "status", "active", st, "rule repealed effective 2000-03-01 per page title")

conn.execute("INSERT INTO provenance (operation, command, notes) VALUES (?,?,?)",
             ("rules-version-surgery", "triage/rules_version_surgery_2026-06-10.py --apply",
              f"batch {BATCH}; 5 provisions created, 7 versions relocated, 13 intervals fixed, "
              "9 duplicate/foreign versions deleted; snapshot rules.db.bak-pre-version-surgery-2026-06-10"))
conn.commit()
print("\nAPPLIED.")
