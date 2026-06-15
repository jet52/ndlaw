#!/usr/bin/env python3
"""Prep the MULTI-amendment wave: provisions with >1 post-1981 amendment need a
version CHAIN (one version per amendment), not a single redline. For each such
provision, resolve + render EVERY amendment's measure, grouped per amendment.

Chain model (see art X §21 in const-pilot transcriptions.json):
  version[d_k, now) = current_text (known).
  For each amendment d_i (latest -> earliest), reverse its redline against the
  version just AFTER it to get the version just BEFORE it. Stop at a CREATE
  (the chain head is the created text; no earlier version). For a carried
  provision the earliest reversal yields the [1981, d_1) head, gated vs 1981 BB.

Excludes: art X §21 (done); art VIII §6 (heavy multi-subsection -> native source).
"""
import json, re, sqlite3, importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("prep", HERE / "prep.py")
P = importlib.util.module_from_spec(spec); spec.loader.exec_module(P)
DB = "/tmp/const-scratch.db"
NBATCH = 6
EXCLUDE = {"N.D. Const. art. X, § 21",      # done (pilot)
           "N.D. Const. art. VIII, § 6",     # heavy multi-subsection -> native source
           # 2024-amendment data is unreliable: bill-doc 23-3092 (amend 167, DB-linked
           # to art XVI) actually amends art X §26 (legacy fund). The 2024 source_url/
           # affected mappings need review before reconstruction. Defer these 6.
           "N.D. Const. art. XVI, § 1", "N.D. Const. art. XVI, § 2",
           "N.D. Const. art. XVI, § 3", "N.D. Const. art. XVI, § 4",
           "N.D. Const. art. XVI, § 5", "N.D. Const. art. IX, § 13"}


def main():
    con = sqlite3.connect(DB)
    rows = con.execute("""
        SELECT p.id, p.citation, v.text_content
        FROM provisions p JOIN provision_versions v ON v.id=p.current_version_id
        WHERE p.corpus='const' AND p.citation LIKE '%art.%' AND p.citation NOT LIKE '%amend%'
          AND (SELECT count(*) FROM amendments a WHERE a.provision_id=p.id
               AND a.effective_date>='1981-01-01')>1
          AND (SELECT count(*) FROM provision_versions vv WHERE vv.provision_id=p.id)=1
    """).fetchall()

    tasks, skipped = [], []
    for pid, cite, cur in rows:
        if cite in EXCLUDE:
            skipped.append({"citation": cite, "reason": "excluded (done / native-source)"}); continue
        amds = con.execute("""SELECT effective_date, amendment_number, source_url, affected
            FROM amendments WHERE provision_id=? AND effective_date>='1981-01-01'
            ORDER BY effective_date""", (pid, )).fetchall()
        amd_records, unresolved = [], []
        for d, num, url, affected in amds:
            n_sec = (affected or "").count(";") + 1
            pdf = P.R.resolve_pdf(url) if url else None
            pgs = P.choose_pages(pdf, url, n_sec) if pdf else None
            pngs = [x for x in (P.render(pdf, pg) for pg in pgs) if x] if pgs else []
            if not pngs:
                unresolved.append(f"{d}({num})")
            amd_records.append({"effective_date": d, "amendment_number": num,
                                "source_url": url, "pdf": pdf.name if pdf else None,
                                "n_affected_sections": n_sec, "page_numbers": pgs or [],
                                "png_paths": pngs})
        rec = {"citation": cite, "current_text": " ".join(cur.split()),
               "n_amendments": len(amds), "amendments": amd_records}
        if unresolved:
            rec["unresolved_measures"] = unresolved
        tasks.append(rec)
    con.close()

    # one provision per task; balance provisions across batches
    batches = [[] for _ in range(NBATCH)]
    for i, t in enumerate(sorted(tasks, key=lambda r: r["n_amendments"], reverse=True)):
        min(batches, key=len).append(t)
    for i, b in enumerate(batches, 1):
        if b:
            (HERE / f"multi-batch-{i}.json").write_text(json.dumps(b, ensure_ascii=False, indent=2))
    (HERE / "multi-skipped.json").write_text(json.dumps(skipped, ensure_ascii=False, indent=2))

    print(f"prepped {len(tasks)} multi-amendment provisions across {NBATCH} batches; "
          f"{len(skipped)} excluded")
    for i, b in enumerate(batches, 1):
        if not b:
            continue
        print(f"  multi-batch-{i}: {len(b)} provisions")
        for t in b:
            u = f"  UNRESOLVED={t['unresolved_measures']}" if t.get("unresolved_measures") else ""
            print(f"     {t['citation'].replace('N.D. Const. ',''):16} "
                  f"{t['n_amendments']} amds, "
                  f"{sum(len(a['png_paths']) for a in t['amendments'])} pngs{u}")
    print("\n  excluded:", [s["citation"].replace("N.D. Const. ", "") for s in skipped])


if __name__ == "__main__":
    main()
