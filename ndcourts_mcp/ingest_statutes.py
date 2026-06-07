"""Ingest the N.D.C.C. (statutes) from the local code-mirror into a corpus DB.

Source: ~/refs/statute/NDCC (produced by ~/code/code-mirror/scrape_nd_code.py
from ndlegis.gov PDFs), organized as title-<N>/chapter-<T>-<C>.md with sections
as ``### § 12.1-20-03. Heading.`` blocks. This output is **current text only**
(as published ~2025-07-01); it carries inline repeal notes ("Repealed by S.L.
2007, ch. 131, § 4.") but no per-section effective dates or prior versions.

So this is a current-text v1: one provision per section, one provision_version
whose effective_start is the publication date. Point-in-time queries before that
date correctly surface lookup_authority's "historical text not captured"
warning. The versioned schema accommodates back-filling prior editions later.

Usage:
    python -m ndcourts_mcp.ingest_statutes                    # dry run summary
    python -m ndcourts_mcp.ingest_statutes --apply            # build statutes.db
    python -m ndcourts_mcp.ingest_statutes --apply --limit-titles 2
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import corpus

DEFAULT_SRC = Path("/Users/jerod/refs/statute/NDCC")
# ndlegis.gov source last-modified ~2025-07-01; treat as the "as published" date.
PUB_DATE = "2025-07-01"

_TITLE_RE = re.compile(r"^#\s+Title\s+([0-9.]+)\s+[—-]\s+(.*)$", re.M)
_CHAPTER_RE = re.compile(r"^##\s+Chapter\s+([0-9.\-]+)\s+[—-]\s+(.*)$", re.M)
# ### § 12.1-20-03. Gross sexual imposition - Penalty.   (heading may be "[Repealed]")
_SECTION_RE = re.compile(r"^###\s+§?\s*([0-9.\-]+[A-Za-z]?)\.\s*(.*?)\s*$", re.M)
_REPEAL_RE = re.compile(r"Repealed by\s+(.+?)(?:\.|$)", re.I)


def load_chapter_urls(src: Path) -> dict[str, str]:
    """Map chapter_num -> source PDF URL from .manifest.json (provenance)."""
    mf = src / ".manifest.json"
    urls: dict[str, str] = {}
    if mf.exists():
        try:
            data = json.loads(mf.read_text())
            for url, meta in data.items():
                ch = meta.get("chapter_num")
                if ch:
                    urls[ch] = url
        except Exception:
            pass
    return urls


def parse_chapter(text: str) -> tuple[str | None, str | None, str | None, str | None, list[dict]]:
    """Return (title_num, title_name, chapter_num, chapter_name, sections)."""
    tm = _TITLE_RE.search(text)
    cm = _CHAPTER_RE.search(text)
    title_num = tm.group(1) if tm else None
    title_name = tm.group(2).strip() if tm else None
    chapter_num = cm.group(1) if cm else None
    chapter_name = cm.group(2).strip() if cm else None

    sections: list[dict] = []
    matches = list(_SECTION_RE.finditer(text))
    for i, m in enumerate(matches):
        sec_num = m.group(1)
        heading = m.group(2).strip().rstrip(".")
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        repealed = "[repealed]" in heading.lower() or bool(
            re.match(r"(?i)^\s*repealed\b", body)
        )
        repeal_auth = None
        rm = _REPEAL_RE.search(body if body else heading)
        if rm:
            repeal_auth = rm.group(1).strip()
        sections.append({
            "sec_num": sec_num,
            "heading": None if heading.lower().startswith("[repealed") else (heading or None),
            "text": body or heading,  # repealed stub may have empty body
            "repealed": repealed,
            "repeal_auth": repeal_auth,
        })
    return title_num, title_name, chapter_num, chapter_name, sections


def build(db_path: Path, src: Path, *, limit_titles: int | None, batch: str) -> dict:
    conn = corpus.get_corpus_connection(db_path, must_exist=False)
    corpus.create_corpus_schema(conn)
    chapter_urls = load_chapter_urls(src)

    titles = sorted(
        (d for d in src.glob("title-*") if d.is_dir()),
        key=lambda p: p.name,
    )
    if limit_titles:
        titles = titles[:limit_titles]

    n_prov = n_ver = n_amend = 0
    for tdir in titles:
        chapters = sorted(tdir.glob("chapter-*.md"))
        t_count = 0
        for cf in chapters:
            tnum, tname, cnum, cname, sections = parse_chapter(cf.read_text())
            url = chapter_urls.get(cnum or "")
            for sec in sections:
                citation = f"N.D.C.C. § {sec['sec_num']}"
                status = "repealed" if sec["repealed"] else "active"
                hierarchy = json.dumps({
                    "title": tnum, "title_name": tname,
                    "chapter": cnum, "chapter_name": cname,
                    "section": sec["sec_num"],
                })
                try:
                    pid = conn.execute(
                        "INSERT INTO provisions (corpus, citation, cite_key, hierarchy, heading, status) "
                        "VALUES (?,?,?,?,?,?)",
                        ("ndcc", citation, corpus.cite_key(citation), hierarchy,
                         sec["heading"], status),
                    ).lastrowid
                except Exception:
                    # duplicate section number across files (shouldn't happen); skip
                    continue
                n_prov += 1
                t_count += 1
                src_auth = (
                    f"Repealed by {sec['repeal_auth']}" if sec["repeal_auth"]
                    else f"current text (N.D.C.C., ndlegis.gov, as of {PUB_DATE})"
                )
                vid = conn.execute(
                    "INSERT INTO provision_versions "
                    "(provision_id, effective_start, effective_end, text_content, "
                    " source_authority, source_url, batch) VALUES (?,?,?,?,?,?,?)",
                    (pid, PUB_DATE, None, sec["text"], src_auth, url, batch),
                ).lastrowid
                n_ver += 1
                conn.execute("UPDATE provisions SET current_version_id=? WHERE id=?", (vid, pid))
                corpus.index_version_fts(conn, vid, citation, sec["heading"], sec["text"])
                if sec["repealed"]:
                    conn.execute(
                        "INSERT OR IGNORE INTO amendments "
                        "(provision_id, version_id, action, effective_date, raw_date, "
                        " authority, source_url, raw) VALUES (?,?,?,?,?,?,?,?)",
                        (pid, vid, "repealed", None, None, sec["repeal_auth"], url,
                         f"Repealed by {sec['repeal_auth']}" if sec["repeal_auth"] else "Repealed"),
                    )
                    n_amend += 1
        conn.commit()
        print(f"  {tdir.name}: {t_count} sections")

    conn.execute(
        "INSERT INTO provenance (operation, command, source_paths, rows_affected, notes) "
        "VALUES (?,?,?,?,?)",
        ("ingest_statutes", batch, str(src), n_prov,
         f"{n_prov} sections (current text as of {PUB_DATE}); {n_amend} repeals"),
    )
    conn.commit()
    conn.close()
    return {"sections": n_prov, "versions": n_ver, "repeals": n_amend}


def main() -> None:
    ap = argparse.ArgumentParser(description="Ingest N.D.C.C. statutes (current text)")
    ap.add_argument("--apply", action="store_true", help="write the DB (default: dry run)")
    ap.add_argument("--src", type=Path, default=DEFAULT_SRC, help="NDCC markdown root")
    ap.add_argument("--db", type=Path, default=None, help="output DB path")
    ap.add_argument("--limit-titles", type=int, default=None, help="first N titles only")
    args = ap.parse_args()

    if not args.src.is_dir():
        sys.exit(f"NDCC source not found: {args.src}")

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    batch = f"statutes-ingest-{stamp}"

    if not args.apply:
        titles = sorted(d for d in args.src.glob("title-*") if d.is_dir())
        sample = next(args.src.glob("title-12.1/chapter-12.1-20.md"), None)
        print(f"NDCC root {args.src}: {len(titles)} titles")
        if sample:
            tnum, tname, cnum, cname, secs = parse_chapter(sample.read_text())
            print(f"Sample {sample.name}: title {tnum} '{tname}', chapter {cnum} '{cname}', "
                  f"{len(secs)} sections")
            for s in secs[:3]:
                print(f"  § {s['sec_num']} [{s['heading']}] repealed={s['repealed']} "
                      f"{len(s['text'])} chars")
        print("\nDry run only. Re-run with --apply to build the DB.")
        return

    db_path = args.db or corpus.resolve_corpus_db_path("ndcc")
    print(f"Building statutes corpus → {db_path}")
    stats = build(db_path, args.src, limit_titles=args.limit_titles, batch=batch)
    print(f"Done: {stats}")


if __name__ == "__main__":
    main()
