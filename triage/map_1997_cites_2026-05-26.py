"""READ-ONLY: map the 1997 native-neutral rows by LABEL cite vs CONTENT cite.

For every 1997 ND n row, extract the content's own neutral cite (first
`YYYY ND n` in the body header window). Then cross-tabulate to classify the
flagged (label != content) rows and find which real opinions are MISSING
(a cite that is some row's label but NO row holds as content).
"""
from __future__ import annotations

from ndcourts_mcp.db import get_connection
from ndcourts_mcp.detect_cite_swap import _body, _neutral_cites, _norm_cite


def main():
    conn = get_connection()
    rows = conn.execute(
        "SELECT o.id, o.source_path, length(o.text_content) tlen, "
        "       substr(o.text_content,1,6000) head, "
        "       (SELECT citation FROM citations WHERE opinion_id=o.id AND reporter='ND-neutral' LIMIT 1) cite "
        "FROM opinions o WHERE EXISTS(SELECT 1 FROM citations WHERE opinion_id=o.id "
        "  AND reporter='ND-neutral' AND citation LIKE '1997 ND %')"
    ).fetchall()

    by_label = {}       # cite -> [(oid, body_cite, tlen, src)]
    content_cites = {}  # body_cite -> [oids]
    recs = []
    for r in rows:
        label = _norm_cite(r["cite"])
        cites = _neutral_cites(_body(r["head"] or "")[:1200])
        body = cites[0] if cites else "(none)"
        recs.append((label, r["id"], body, r["tlen"], r["source_path"]))
        by_label.setdefault(label, []).append((r["id"], body, r["tlen"], r["source_path"]))
        if cites:
            content_cites.setdefault(body, []).append(r["id"])

    flagged = [x for x in recs if x[2] != x[0] and x[2] != "(none)"]
    flagged.sort(key=lambda x: int(x[0].split()[-1]))

    print(f"1997 native-neutral rows: {len(rows)};  flagged (label!=content): {len(flagged)}\n")
    print(f"{'label':<12}{'oid':>6} {'content':<12}{'len':>7}  content_held_correctly_by  label_real_opinion_present?")
    for label, oid, body, tlen, src in flagged:
        # who correctly holds this content cite (a row whose LABEL == body)?
        correct_home = [o for (o, b, t, s) in by_label.get(body, []) if b == body]
        # is the label's real opinion present (a row whose CONTENT == label)?
        label_content_rows = content_cites.get(label, [])
        print(f"{label:<12}{oid:>6} {body:<12}{tlen:>7}  "
              f"home={correct_home or 'NONE'}  label_content_rows={label_content_rows or 'MISSING'}")

    # Which label cites among the flagged are content-MISSING (no row holds them as content)?
    print("\n=== flagged label cites whose REAL opinion is MISSING (no row has that content) ===")
    missing = sorted({label for (label, o, b, t, s) in flagged if not content_cites.get(label)},
                     key=lambda c: int(c.split()[-1]))
    print(missing or "none")
    conn.close()


if __name__ == "__main__":
    main()
