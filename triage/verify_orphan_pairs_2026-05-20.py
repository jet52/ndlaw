"""Compute jaccard(.doc body, correct OID's text_content) to confirm the
ORPHAN_SIBLING re-pairing before registering sources / applying case_names.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from ndcourts_mcp.db import get_connection, DEFAULT_DB_PATH  # noqa: E402
from ndcourts_mcp.ingest_westlaw import _doc_to_text  # noqa: E402

PAIRS = [
    ("/Users/jerod/refs/nd/opin/N.D./20/0372-Fitzmaurice-v-Willis.doc", 680),
    ("/Users/jerod/refs/nd/opin/N.D./20/0412-Stoltze-v-Hurd.doc", 692),
    ("/Users/jerod/refs/nd/opin/N.D./21/0348-Heard-v-Holbrook.doc", 767),
    ("/Users/jerod/refs/nd/opin/N.D./23/0352-Bismarck-Water-Supply-Co-v-City-of-Bismarck.doc", 937),
    ("/Users/jerod/refs/nd/opin/N.D./24/0395-McCarty-v-Kepreta.doc", 1007),
    ("/Users/jerod/refs/nd/opin/N.D./32/0373-Sundahl-v-First-State-Bank-of-Edmunds.doc", 1487),
    ("/Users/jerod/refs/nd/opin/N.D./34/0601-Mercer-County-State-Bank-of-Manhaven-v-Hayes.doc", 1641),
]

WORD = re.compile(r"[a-z]{4,}")
STOP = {
    "court", "case", "cause", "appeal", "appellant", "appellee", "respondent",
    "plaintiff", "plaintiffs", "defendant", "defendants", "judgment", "order",
    "motion", "trial", "term", "north", "dakota", "supreme", "syllabus",
    "opinion", "filed", "this", "that", "with", "from", "have", "were", "been",
    "their", "they", "such", "which", "upon", "said", "shall", "would", "where",
    "there", "thereof", "therein", "thereto", "wherein", "whether", "before",
    "after", "above", "under", "must", "made", "make", "also", "found", "find",
    "held", "hold",
}


def toks(s: str) -> set[str]:
    return {w for w in WORD.findall((s or "").lower()) if w not in STOP}


def main() -> int:
    conn = get_connection(DEFAULT_DB_PATH)
    for doc_path, oid in PAIRS:
        body = _doc_to_text(Path(doc_path))
        row = conn.execute(
            "SELECT case_name, text_content FROM opinions WHERE id = ?", (oid,)
        ).fetchone()
        if not row:
            print(f"oid {oid}: NOT FOUND")
            continue
        a, b = toks(body), toks(row["text_content"] or "")
        jac = len(a & b) / len(a | b) if (a and b) else 0.0
        print(f"oid {oid:>5}  jac={jac:.3f}  {row['case_name']}  ({Path(doc_path).name})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
