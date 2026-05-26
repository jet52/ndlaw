"""READ-ONLY: classify the 10 Group B PDF-era CITE flags before reading PDFs.

For each: label cite, body header cite, date; whether the label cite appears
ANYWHERE in the full text (if yes, likely a false positive = self-cite just past
the header window); whether the body cite is held by another row (a 'correct home'
=> mislabel/dup/swap); and whether scraped PDFs exist for the label & body cites.
"""
from __future__ import annotations
from pathlib import Path
from ndcourts_mcp.db import get_connection
from ndcourts_mcp.detect_cite_swap import _body, _neutral_cites, _norm_cite

REFS = Path("/Users/jerod/refs/nd/opin")
OIDS = [19290, 19429, 19433, 19599, 19652, 19690, 19711, 19736, 19877, 19988]


def holders(conn, cite):
    return [r[0] for r in conn.execute(
        "SELECT opinion_id FROM citations WHERE citation=? AND reporter='ND-neutral'",
        (cite,)).fetchall()]


def pdf_path(cite):
    y, n = cite.split(" ND ")
    return f"pdfs/{y}/{y}ND{n}.pdf"


def main():
    conn = get_connection()
    for oid in OIDS:
        r = conn.execute("SELECT date_filed, source_path, text_content, "
                         "(SELECT citation FROM citations WHERE opinion_id=? AND reporter='ND-neutral' LIMIT 1) cite "
                         "FROM opinions WHERE id=?", (oid, oid)).fetchone()
        label = _norm_cite(r["cite"])
        full = _body(r["text_content"] or "")
        body = (_neutral_cites(full[:1200]) or ["(none)"])[0]
        label_anywhere = label in _neutral_cites(full)
        body_home = [h for h in holders(conn, body) if h != oid]
        label_home = [h for h in holders(conn, label) if h != oid]
        lpdf = (REFS / pdf_path(label)).exists()
        bpdf = (REFS / pdf_path(body)).exists() if body != "(none)" else False
        print(f"oid {oid}  label={label:<12} body={body:<12} date={r['date_filed']}")
        print(f"    label_appears_in_full_text={label_anywhere}  body_held_by={body_home or '-'}  label_held_by={label_home or '-'}")
        print(f"    pdf[label]={'Y' if lpdf else '-'} ({pdf_path(label)})   pdf[body]={'Y' if bpdf else '-'} ({pdf_path(body) if body!='(none)' else '-'})")
    conn.close()


if __name__ == "__main__":
    main()
