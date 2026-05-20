"""Dump the 2,053 ambiguous case-name diffs (vols 16-79) to TSV for analysis.

Reuses review_casenames.extract_diffs but writes everything to disk
instead of running the interactive TUI. Skips entries marked equivalent
(already silenced) and mispaired (diverted to the mispaired TSV).
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from ndcourts_mcp.db import DEFAULT_DB_PATH, get_connection  # noqa: E402
from ndcourts_mcp.review_casenames import extract_diffs, _load_state  # noqa: E402

OUT = REPO / "triage" / "casenames-ambig-review-2026-05-20.tsv"
VOLUMES = list(range(16, 80))


def main() -> int:
    conn = get_connection(DEFAULT_DB_PATH)
    state = _load_state()
    kept_db = {int(k) for k in state.get("kept_db", {}).keys()}

    out_rows = []
    for vol in VOLUMES:
        # Pass empty mispaired list — we don't want to overwrite the canonical one;
        # extract_diffs writes to MISPAIRED_REPORT itself only via `run()`.
        mispaired: list[dict] = []
        diffs = extract_diffs(conn, vol, kept_db, mispaired)
        for d in diffs:
            if d["equivalent"]:
                continue
            out_rows.append(d)
        if vol % 5 == 0:
            print(f"  vol {vol}: cumulative {len(out_rows)}")

    cols = ["volume", "opinion_id", "primary_citation", "db_name",
            "wl_raw", "wl_norm", "wl_titled", "doc_path"]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, delimiter="\t",
                           extrasaction="ignore")
        w.writeheader()
        for d in out_rows:
            w.writerow(d)
    print(f"\nWrote {len(out_rows)} rows to {OUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
