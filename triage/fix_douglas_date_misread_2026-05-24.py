"""Revert a date misread I introduced in fix-bound-discrepancies-2026-05-24.

Douglas v. Glazier (oid 5774, 9 N.D. 615) was changed 1900-12-08 -> 1900-11-24
from a 150-dpi scan read. Re-reading the bound page at 300 dpi shows "Opinion
filed December 8, 1900" — the original 1900-12-08 was CORRECT. Reverting.

(Wilson 5747 -> 1900-11-13 and Nelson 2169 -> 173 N.W. 475 from that batch are
confirmed correct and are NOT touched. Re-run section10_resequence afterward.)
"""
from __future__ import annotations
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from ndcourts_mcp.db import DEFAULT_DB_PATH, get_connection, log_change  # noqa: E402

BATCH = "fix-douglas-date-misread-2026-05-24"
conn = get_connection(DEFAULT_DB_PATH)
cur = conn.execute("SELECT date_filed FROM opinions WHERE id=5774").fetchone()[0]
if cur != "1900-11-24":
    raise SystemExit(f"guard: oid 5774 date is {cur!r}, expected 1900-11-24 — abort")
conn.execute("UPDATE opinions SET date_filed='1900-12-08' WHERE id=5774")
log_change(conn, BATCH, 5774, "date_filed", "1900-11-24", "1900-12-08",
           authority="bound N.D. vol 9 p.615 @300dpi: 'Opinion filed December 8, 1900'")
conn.commit()
print("Reverted oid 5774 date_filed 1900-11-24 -> 1900-12-08.")
