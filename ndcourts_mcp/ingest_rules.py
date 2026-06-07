"""Ingest ND court rules from the local rules git repo into a versioned corpus.

The rules repo (~/refs/rule, produced by ~/code/rules-scraper) stores each rule
as a markdown file whose **git history is the amendment history**: every commit
is a version and the commit's author date is that version's effective date.
Commit bodies carry the source URL and Explanatory Notes; "Silent correction"
commits fix text without changing the effective date.

This maps directly onto the versioned-provision model: one provision per rule,
one provision_version per real (non-silent) commit, with effective_start =
commit date and effective_end = the next version's start. Court rules are the
higher-provenance-bar corpus, so every version records its source URL and
enacting/explanatory authority.

Usage:
    python -m ndcourts_mcp.ingest_rules                         # dry run summary
    python -m ndcourts_mcp.ingest_rules --apply                 # build rules.db
    python -m ndcourts_mcp.ingest_rules --apply --category ndrcivp   # one rule set
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import corpus

DEFAULT_REPO = Path("/Users/jerod/refs/rule")

# Category directory -> canonical citation prefix. The first six match jetcite's
# normalized court-rule forms, so opinions cross-link by exact citation.
PREFIXES: dict[str, str] = {
    "ndrappp": "N.D.R.App.P.",
    "ndrcivp": "N.D.R.Civ.P.",
    "ndrcrimp": "N.D.R.Crim.P.",
    "ndrev": "N.D.R.Ev.",
    "ndrjuvp": "N.D.R.Juv.P.",
    "ndrct": "N.D.R.Ct.",
    "ndrprofconduct": "N.D.R. Prof. Conduct",
    "ndcodejudconduct": "N.D. Code Jud. Conduct",
    "ndrlawyerdiscipl": "N.D.R. Lawyer Discipl.",
    "admissiontopracticer": "Admission to Practice R.",
    "ndrcontinuinglegaled": "N.D.R. Continuing Legal Educ.",
    "ndstdsimposinglawyersanctions": "N.D. Stds. Imposing Lawyer Sanctions",
    "ndsupctadminr": "N.D. Sup. Ct. Admin. R.",
    "ndsupctadminorder": "N.D. Sup. Ct. Admin. Order",
    "rjudconductcomm": "R. Jud. Conduct Comm.",
    "ndrprocr": "N.D.R. Proc. R.",
    "ndrlocalctpr": "N.D.R. Local Ct. Pr.",
    "local": "N.D. Local Ct. R.",
    "rltdpracticeoflawbylawstudents": "Ltd. Practice of Law by Law Students R.",
}

_OBSOLETE_LINE_RE = re.compile(r"^\s*\*\*Obsolete Date:\*\*.*$", re.M)
_H1_RE = re.compile(r"^#\s+(.*)$", re.M)
_RULE_TITLE_RE = re.compile(r"^(?:RULE|Rule)\s+[0-9A-Za-z.\-]+\.?\s*(.*)$")
_SOURCE_RE = re.compile(r"^Source:\s*(\S+)", re.M)
_NOTES_RE = re.compile(r"Explanatory Notes:\s*(.+)\Z", re.S)
_REPEALED_RE = re.compile(r"\b(repealed|abrogated|superseded and removed)\b", re.I)


def git(repo: Path, *args: str) -> str:
    out = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, text=True, check=True,
    )
    return out.stdout


def rule_number(filename: str) -> str:
    """'rule-56.md' -> '56', 'rule-1.0.md' -> '1.0', 'rule-Table-B.md' -> 'Table B'."""
    stem = filename[len("rule-"):-len(".md")]
    if re.fullmatch(r"[0-9.]+", stem):
        return stem
    return stem.replace("-", " ")


def parse_heading(text: str) -> str | None:
    m = _H1_RE.search(text)
    if not m:
        return None
    head = m.group(1).strip()
    tm = _RULE_TITLE_RE.match(head)
    return (tm.group(1).strip() if tm and tm.group(1).strip() else head) or None


def clean_text(raw: str) -> str:
    t = _OBSOLETE_LINE_RE.sub("", raw)
    # drop the leading H1 (the heading is stored separately)
    t = _H1_RE.sub("", t, count=1)
    return re.sub(r"\n{3,}", "\n\n", t).strip()


def commit_meta(body: str) -> tuple[str | None, str | None]:
    """(source_url, explanatory_notes) from a commit message body."""
    url = _SOURCE_RE.search(body)
    notes = _NOTES_RE.search(body)
    note_txt = notes.group(1).strip() if notes else None
    return (url.group(1) if url else None), note_txt


# Record separators unlikely to appear in commit text.
_REC, _FLD = "\x1e", "\x1f"


def file_versions(repo: Path, relpath: str) -> list[dict]:
    """Chronological version list for one rule file, with silent corrections
    merged into the preceding version."""
    fmt = f"%H{_FLD}%aI{_FLD}%s{_FLD}%b{_REC}"
    log = git(repo, "log", "--reverse", f"--format={fmt}", "--", relpath)
    versions: list[dict] = []
    for rec in log.split(_REC):
        rec = rec.strip("\n")
        if not rec.strip():
            continue
        h, date_iso, subject, body = (rec.split(_FLD) + ["", "", "", ""])[:4]
        content = git(repo, "show", f"{h}:{relpath}")
        text = clean_text(content)
        if not text:
            continue
        silent = "silent correction" in subject.lower()
        url, notes = commit_meta(body)
        if silent and versions:
            # update text/heading of the standing version; keep its effective date
            versions[-1]["text"] = text
            versions[-1]["heading"] = parse_heading(content) or versions[-1]["heading"]
            versions[-1].setdefault("corrections", []).append(date_iso[:10])
            continue
        versions.append({
            "effective_start": date_iso[:10],
            "text": text,
            "heading": parse_heading(content),
            "source_url": url,
            "notes": notes,
            "subject": subject,
            "repealed": bool(_REPEALED_RE.search(text[:200])),
        })
    # set effective_end = next version's start
    for i in range(len(versions) - 1):
        versions[i]["effective_end"] = versions[i + 1]["effective_start"]
    if versions:
        versions[-1]["effective_end"] = None
    return versions


def build(db_path: Path, repo: Path, *, only: str | None, limit: int | None,
          batch: str) -> dict:
    conn = corpus.get_corpus_connection(db_path, must_exist=False)
    corpus.create_corpus_schema(conn)

    cats = [only] if only else [c for c in PREFIXES if (repo / c).is_dir()]
    n_prov = n_ver = n_amend = 0
    for cat in cats:
        cdir = repo / cat
        if not cdir.is_dir():
            print(f"  skip {cat}: no dir", file=sys.stderr)
            continue
        prefix = PREFIXES.get(cat, cat)
        files = sorted(p.name for p in cdir.glob("rule-*.md"))
        if limit:
            files = files[:limit]
        cat_prov = 0
        for fname in files:
            relpath = f"{cat}/{fname}"
            versions = file_versions(repo, relpath)
            if not versions:
                continue
            num = rule_number(fname)
            citation = f"{prefix} {num}"
            cur = versions[-1]
            status = "repealed" if cur["repealed"] else "active"
            heading = next((v["heading"] for v in reversed(versions) if v["heading"]), None)
            pid = conn.execute(
                "INSERT INTO provisions (corpus, citation, cite_key, heading, status) "
                "VALUES (?,?,?,?,?)",
                ("rule", citation, corpus.cite_key(citation), heading, status),
            ).lastrowid
            n_prov += 1
            cat_prov += 1
            current_vid = None
            for i, v in enumerate(versions):
                vid = conn.execute(
                    "INSERT INTO provision_versions "
                    "(provision_id, effective_start, effective_end, text_content, "
                    " source_authority, source_url, batch) VALUES (?,?,?,?,?,?,?)",
                    (pid, v["effective_start"], v["effective_end"], v["text"],
                     v["notes"] or v["subject"], v["source_url"], batch),
                ).lastrowid
                n_ver += 1
                if v["effective_end"] is None:
                    current_vid = vid
                corpus.index_version_fts(conn, vid, citation, v["heading"], v["text"])
                action = "adopted" if i == 0 else ("repealed" if v["repealed"] else "amended")
                conn.execute(
                    "INSERT OR IGNORE INTO amendments "
                    "(provision_id, version_id, action, effective_date, raw_date, "
                    " authority, source_url, raw) VALUES (?,?,?,?,?,?,?,?)",
                    (pid, vid, action, v["effective_start"], v["effective_start"],
                     v["notes"], v["source_url"], v["subject"]),
                )
                n_amend += 1
            conn.execute("UPDATE provisions SET current_version_id=? WHERE id=?",
                         (current_vid, pid))
        conn.commit()
        print(f"  {cat}: {cat_prov} rules")

    conn.execute(
        "INSERT INTO provenance (operation, command, source_paths, rows_affected, notes) "
        "VALUES (?,?,?,?,?)",
        ("ingest_rules", batch, str(repo), n_prov,
         f"{n_prov} rules, {n_ver} versions, {n_amend} amendment events"),
    )
    conn.commit()
    conn.close()
    return {"rules": n_prov, "versions": n_ver, "amendments": n_amend}


def main() -> None:
    ap = argparse.ArgumentParser(description="Ingest ND court rules from the git repo")
    ap.add_argument("--apply", action="store_true", help="write the DB (default: dry run)")
    ap.add_argument("--repo", type=Path, default=DEFAULT_REPO, help="rules git repo")
    ap.add_argument("--db", type=Path, default=None, help="output DB path")
    ap.add_argument("--category", default=None, help="ingest only this category dir")
    ap.add_argument("--limit", type=int, default=None, help="first N rule files per category")
    args = ap.parse_args()

    if not (args.repo / ".git").is_dir():
        sys.exit(f"not a git repo: {args.repo}")

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    batch = f"rules-ingest-{stamp}"

    if not args.apply:
        cat = args.category or "ndrcivp"
        files = sorted(p.name for p in (args.repo / cat).glob("rule-*.md"))
        print(f"Repo {args.repo} | category {cat}: {len(files)} rule files")
        for fname in files[:3]:
            vs = file_versions(args.repo, f"{cat}/{fname}")
            num = rule_number(fname)
            print(f"  {PREFIXES.get(cat, cat)} {num}: {len(vs)} version(s) "
                  f"{[v['effective_start'] for v in vs]}  heading={vs[-1]['heading'] if vs else None!r}")
        print("\nDry run only. Re-run with --apply to build the DB.")
        return

    db_path = args.db or corpus.resolve_corpus_db_path("rule")
    print(f"Building court-rules corpus → {db_path}")
    stats = build(db_path, args.repo, only=args.category, limit=args.limit, batch=batch)
    print(f"Done: {stats}")


if __name__ == "__main__":
    main()
