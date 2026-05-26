"""READ-ONLY: for each flagged 1997 row, confirm its linked archive HTML holds
the row's LABEL cite (i.e. the archive source is correct; only text_content leaked).
If archive_cite == label_cite for all, the fix is uniform: re-derive
text_content/case_name/docket from the archive HTML, detach the misnamed markdown.
"""
from __future__ import annotations
import re
from pathlib import Path
from ndcourts_mcp.db import get_connection
from ndcourts_mcp.detect_cite_swap import _norm_cite, _neutral_cites

REFS = Path("/Users/jerod/refs/nd/opin")
FLAGGED = [18248, 18249, 18250, 18251, 18252, 18270, 18271, 18272, 18274,
           18275, 18276, 18277, 18278, 18279, 18280, 12476]


def archive_text(p: str) -> str:
    f = REFS / p
    if not f.exists():
        return ""
    h = f.read_text(encoding="utf-8", errors="replace")
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h))


def main():
    conn = get_connection()
    print(f"{'oid':>6} {'label':<12}{'content_now':<12}{'archive_src':<28}{'archive_cite':<12} ok?")
    all_ok = True
    for oid in FLAGGED:
        r = conn.execute(
            "SELECT (SELECT citation FROM citations WHERE opinion_id=? AND reporter='ND-neutral' LIMIT 1) cite, "
            "(SELECT source_path FROM opinion_sources WHERE opinion_id=? AND source_reporter='archive' LIMIT 1) arch, "
            "substr(text_content,1,1200) head FROM opinions WHERE id=?",
            (oid, oid, oid)).fetchone()
        label = _norm_cite(r["cite"])
        body = (_neutral_cites(r["head"] or "") or ["(none)"])[0]
        arch = r["arch"] or ""
        at = archive_text(arch)
        acites = _neutral_cites(at)
        acite = acites[0] if acites else "(none)"
        ok = (acite == label)
        all_ok = all_ok and ok and bool(arch)
        print(f"{oid:>6} {label:<12}{body:<12}{arch:<28}{acite:<12} {'OK' if ok else 'MISMATCH'}"
              + ("" if arch else "  <NO ARCHIVE SRC>"))
    print(f"\nUniform-fix hypothesis holds for all 16: {all_ok}")
    conn.close()


if __name__ == "__main__":
    main()
