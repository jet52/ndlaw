"""Citation-graph footnote-loss detector.

For every `YYYY ND N, ¶ X n.Z` pincite in the corpus, check whether the *cited*
opinion actually has footnote Z (per proofread.footnote_structure). A pincite to
n.Z whose target lacks footnote Z is a candidate footnote loss.

Prints PRESENT/MISSING counts and the MISSING worklist. Read-only.
"""
import re
import sqlite3
import sys

import ndcourts_mcp.proofread as pr

PINCITE = re.compile(
    r"(\d{4})\s+ND\s+(\d+)\s*,?\s*¶+\s*\d+(?:\s*[-–]\s*\d+)?\s*,?\s*nn?\.\s*(\d+)")


def main():
    db = sys.argv[1] if len(sys.argv) > 1 else "opinions.db"
    con = sqlite3.connect(db)
    # map neutral cite -> opinion id
    cite2id = {}
    for oid, c in con.execute(
            "SELECT opinion_id, citation FROM citations WHERE citation LIKE '% ND %'"):
        m = re.match(r"^(\d{4})\s+ND\s+(\d+)$", c.strip())
        if m:
            cite2id.setdefault(f"{m.group(1)} ND {m.group(2)}", oid)

    # gather pincites (cited_cite, fn) -> set of citing cites
    refs = {}
    rows = con.execute("SELECT id, text_content FROM opinions WHERE text_content IS NOT NULL")
    id2cite = {oid: c for c, oid in cite2id.items()}
    for oid, text in rows:
        citing = id2cite.get(oid, str(oid))
        for m in PINCITE.finditer(text):
            cited = f"{m.group(1)} ND {m.group(2)}"
            fn = int(m.group(3))
            refs.setdefault((cited, fn), set()).add(citing)

    present, missing = 0, []
    struct_cache = {}
    for (cited, fn), citers in sorted(refs.items()):
        tid = cite2id.get(cited)
        if tid is None:
            continue  # cited opinion not in corpus
        if tid not in struct_cache:
            t = con.execute("SELECT text_content FROM opinions WHERE id=?", (tid,)).fetchone()
            struct_cache[tid] = pr.footnote_structure(t[0]) if t and t[0] else {"bodies": []}
        nums = {n for n, _, _ in struct_cache[tid]["bodies"]}
        if fn in nums:
            present += 1
        else:
            missing.append((cited, fn, tid, len(citers), sorted(citers)))

    print(f"PRESENT={present}  MISSING={len(missing)}", file=sys.stderr)
    print("cited_cite\tfn\tcited_id\tn_citers\tciting_cites")
    for cited, fn, tid, nc, citers in sorted(missing, key=lambda x: -x[3]):
        print(f"{cited}\t{fn}\t{tid}\t{nc}\t{','.join(citers)}")


if __name__ == "__main__":
    main()
