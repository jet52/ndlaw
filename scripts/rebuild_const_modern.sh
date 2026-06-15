#!/usr/bin/env bash
# Reproducibly rebuild the modern (1981-present) point-in-time layer onto a fresh
# base constitution.db. This is the upstream propagation step for the modern
# reconstruction campaign (HANDOFF §2/§7): every reconstruction lives in a committed
# splice script, and running them in order against a copy of the served base DB
# regenerates the full validated point-in-time layer (44 provisions / +52 versions
# + the in-place renumber/second-read fixes).
#
# It operates on /tmp/const-scratch.db (the splice scripts' hardcoded target). It does
# NOT re-fetch ndconst.org and does NOT touch constitution.db — promotion is a separate,
# explicit copy after the diff/verify gates pass.
#
# Usage:
#   scripts/rebuild_const_modern.sh            # backup validated scratch, rebuild, verify
# Then, only if reproducibility holds and you intend to promote:
#   cp /tmp/const-scratch.db constitution.db   # (after backing up constitution.db)
set -euo pipefail
cd "$(dirname "$0")/.."
PY=.venv/bin/python
SCRATCH=/tmp/const-scratch.db
BASE=constitution.db

[ -f "$BASE" ] || { echo "ERROR: $BASE not found" >&2; exit 1; }

# Preserve whatever validated scratch exists so we can diff against it / restore.
if [ -f "$SCRATCH" ]; then
  cp "$SCRATCH" "${SCRATCH}.validated.bak"
  echo "[0] preserved current scratch -> ${SCRATCH}.validated.bak"
fi

echo "[1] fresh base: cp $BASE -> $SCRATCH"
cp "$BASE" "$SCRATCH"

run() { echo; echo ">>> $*"; "$@"; }

# Order matters; mirrors HANDOFF §2. Base already carries the ingest overlays
# (amend-167 mapping, source/date corrections), so x26's gate passes here and the
# standalone fix_amend167 is idempotent.
run $PY triage/const-pilot-2026-06-14/apply_markup.py --apply
run $PY triage/const-modern-batch/verify_and_splice.py --apply
run $PY triage/const-modern-batch/splice_wave2.py
run $PY triage/const-modern-batch/splice_multichain.py --apply
run $PY triage/const-modern-batch/splice_x26_2011.py --apply
run $PY triage/const-modern-batch/reconstruct_ix_stale.py --db "$SCRATCH" --chain --apply
run $PY scripts/fix_amend167_legacyfund_2024.py "$SCRATCH" --apply
run $PY scripts/apply_modern_text_corrections.py "$SCRATCH" --apply
run $PY triage/const-modern-batch/splice_xii_corporations_2006.py --apply
run $PY triage/const-modern-batch/fix_artiv_renumber_1986.py --apply
run $PY triage/const-modern-batch/splice_artiv_crosswalk_1981.py --apply
run $PY triage/const-modern-batch/splice_groupa_clean_2026.py --apply
run $PY triage/const-modern-batch/splice_artxiii_1_1996.py --apply
run $PY triage/const-modern-batch/splice_artv_pre1997.py --apply
run $PY triage/const-modern-batch/splice_artv_chains_1986.py --apply
run $PY triage/const-modern-batch/fix_ix7_head_secondread.py --apply

echo
echo "[2] rebuild complete. verifying..."
$PY - "$SCRATCH" "${SCRATCH}.validated.bak" <<'PYEOF'
import sqlite3, sys, hashlib
rebuilt, bak = sys.argv[1], sys.argv[2]

def integrity(db):
    c = sqlite3.connect(db)
    g = c.execute("""WITH v AS (SELECT provision_id, effective_start, effective_end,
      LEAD(effective_start) OVER (PARTITION BY provision_id ORDER BY effective_start) nxt
      FROM provision_versions) SELECT count(*) FROM v WHERE nxt IS NOT NULL
      AND effective_end IS NOT NULL AND effective_end!='' AND date(effective_end)!=date(nxt)
      AND date(effective_end,'+1 day')!=date(nxt)""").fetchone()[0]
    qc = c.execute("PRAGMA quick_check").fetchone()[0]
    p = c.execute("SELECT COUNT(*) FROM provisions").fetchone()[0]
    v = c.execute("SELECT COUNT(*) FROM provision_versions").fetchone()[0]
    c.close(); return g, qc, p, v

def versig(db):
    # content signature of the point-in-time layer, independent of row id / insert order
    c = sqlite3.connect(db)
    rows = c.execute("""SELECT p.citation, pv.effective_start, COALESCE(pv.effective_end,''),
      pv.text_content FROM provision_versions pv JOIN provisions p ON pv.provision_id=p.id""").fetchall()
    c.close()
    norm = sorted((cite, s, e, " ".join((t or "").split())) for cite, s, e, t in rows)
    return hashlib.sha256(repr(norm).encode()).hexdigest(), len(norm)

g, qc, p, v = integrity(rebuilt)
print(f"  rebuilt: integrity gaps={g}  quick_check={qc}  provisions={p}  versions={v}")
import os
if os.path.exists(bak):
    h1, n1 = versig(rebuilt); h2, n2 = versig(bak)
    print(f"  version-content signature: rebuilt={h1[:16]} ({n1})  validated={h2[:16]} ({n2})")
    print("  REPRODUCIBLE: " + ("YES — rebuilt == validated scratch ✓" if h1 == h2
          else "NO — DIFFERS from validated scratch (investigate before promoting)"))
PYEOF
echo
echo "[3] snapshot-diff:"
$PY triage/const-modern-batch/snapshot_diff_modern.py 2>&1 | grep -E "SNAPSHOT-DIFF|MISMATCH |match-or-near"
echo
echo "Done. To promote: back up $BASE then  cp $SCRATCH $BASE"
