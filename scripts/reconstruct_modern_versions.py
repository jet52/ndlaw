#!/usr/bin/env python3
"""Reconstruct modern (1981-present) constitution point-in-time versions.

TODO-const-history-validation.md item #0. Design:
data/design-modern-const-versions-2026-06-14.md.

The modern reorg layer has one version per provision (stamped at its latest
amendment date); the post-1981 amendment chronology is recorded but never
spliced into the timeline. This step fetches each amendment's session-law CAA
PDF, extracts the enacted section text, GATES the latest extraction against the
current DB text, and (on pass) splices the prior versions.

PHASE 1: amend-reenact-section only (single-section measures that reprint the
full amended section "...amended and reenacted to read as follows: Section N.").
create-article / cross-article / described-edit are out of scope (phases 2-3).

Default = dry run + report (gate pass-rate). --apply writes versions + changelog.
Default --db is a scratch copy, never the live DB, unless --db is given.
"""
import argparse
import re
import sqlite3
import subprocess
import sys
import urllib.request
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REFS = Path.home() / "refs" / "nd" / "sess"
CACHE = ROOT / "triage" / "const-pilot-2026-06-14" / "caa-cache"
REORG = "1981-01-01"

# fi-ligature OCR class observed in some CAA text layers (e.g. 1995).
LIG = {"ftrst": "first", "ftfty": "fifty", "ftrm": "firm", "ftnd": "find",
       "ftle": "file", "ftnal": "final", "ftscal": "fiscal", "ftve": "five"}
WORD = re.compile(r"[a-z0-9]+")


# ---- source resolution ----------------------------------------------------

def resolve_pdf(source_url: str) -> Path | None:
    """On-disk refs CAA/CMA first (naming varies: CAA.pdf, SL9CAA.pdf,
    SL7CNSTM.pdf, CMA.pdf); else download the source_url into CACHE."""
    base = source_url.split("#")[0]
    m = re.search(r"(19|20)\d{2}", base)
    year = m.group(0) if m else None
    if year:
        d = REFS / f"{year}_sl"
        if d.is_dir():
            # CAA (amendments approved) preferred; CNSTM/CMA for odd years.
            for pat in ("*CAA*.pdf", "*CNSTM*.pdf", "*CMA*.pdf"):
                hits = [h for h in sorted(d.glob(pat)) if "CAP" not in h.name.upper()]
                if hits:
                    return hits[0]
        # 2021+ sessions are stored as a single whole-session PDF, not a _sl/ dir
        for cand in (REFS / f"sl{year}.pdf", REFS / f"sl{year}ss.pdf"):
            if cand.exists():
                return cand
    # download fallback
    CACHE.mkdir(parents=True, exist_ok=True)
    key = re.sub(r"[^A-Za-z0-9]+", "_", base.split("legis.nd.gov/")[-1]) + ".pdf"
    dest = CACHE / key
    if not dest.exists():
        try:
            urllib.request.urlretrieve(base, dest)
        except Exception as e:  # noqa
            print(f"    download FAIL {base}: {e}", file=sys.stderr)
            return None
    return dest


_pdfcache: dict[Path, str] = {}

def pdftext(pdf: Path) -> str:
    if pdf not in _pdfcache:
        out = subprocess.run(["pdftotext", "-layout", str(pdf), "-"],
                             capture_output=True, text=True)
        _pdfcache[pdf] = out.stdout
    return _pdfcache[pdf]


# ---- locator (amend-reenact-section) --------------------------------------

ROMAN_RE = r"[IVXLC]+"

def strip_running_headers(text: str) -> str:
    keep = []
    for ln in text.splitlines():
        s = ln.strip()
        if re.match(r"^\d{3,4}\b", s):           # page number line
            continue
        if re.search(r"CONSTITUTIONAL (AMENDMENTS|MEASURES)", s, re.I):
            continue
        if re.match(r"^Chapter \d+\b", s):
            continue
        keep.append(ln)
    return "\n".join(keep)


def extract_reenact(full: str, roman: str, secnum: str) -> str | None:
    """Return the reprinted body of `Section <secnum>` of article <roman>
    from an amend-and-reenact measure, or None if not located."""
    # Find the operative preamble naming this exact section+article.
    pre = re.compile(
        rf"(?:amendment of |amend )?section\s+{re.escape(secnum)}\s+of\s+article\s+{roman}\b",
        re.I)
    # Locate the "...as follows:" that introduces the reprint after such a preamble.
    for pm in pre.finditer(full):
        tail = full[pm.end(): pm.end() + 12000]
        fm = re.search(r"(?:reenacted\s+(?:to\s+read\s+)?as\s+follows:|"
                       r"amended\s+and\s+reenacted\s+as\s+follows:|as\s+follows:)",
                       tail, re.I)
        if not fm:
            continue
        body = tail[fm.end():]
        sm = re.search(rf"Section\s+{re.escape(secnum)}\.?\s", body)
        if sm:
            body = body[sm.start():]
        # terminate at next structural marker
        body = re.split(r"\n\s*SECTION\s+\d|\bEFFECTIVE\s+DATE\b|\n\s*Approved\b|"
                        r"\n\s*NOTE:|\n\s*CHAPTER\s+\d|\n\s*SECTION\s+1\.\s+AMENDMENT",
                        body)[0]
        body = strip_running_headers(body)
        body = re.sub(r"^Section\s+\d+[A-Za-z]?\.?\s*", "", body.strip())
        return body.strip() or None
    return None


# ---- normalization + gate -------------------------------------------------

def tokens(t: str) -> list[str]:
    t = t.lower()
    for k, v in LIG.items():
        t = t.replace(k, v)
    return WORD.findall(t)


def classify(extracted: str, current: str) -> str:
    """CLEAN: exact token match (clean reprint, splice-ready).
    MARKUP: current ⊆ extracted (strike/underline reprint pdftotext can't
            separate — needs marker/Claude-read for clean prior text).
    MISMATCH: neither (wrong section, truncation, or heavy divergence)."""
    a, b = tokens(extracted), tokens(current)
    if a == b:
        return "CLEAN"
    if set(b) <= set(a):
        return "MARKUP"
    return "MISMATCH"


# ---- DB ops ---------------------------------------------------------------

def load_scope(con):
    rows = con.execute("""
        SELECT p.id, p.citation, v.id, v.effective_start, v.text_content
        FROM provisions p JOIN provision_versions v ON v.id=p.current_version_id
        WHERE p.corpus='const' AND p.citation LIKE '%art.%' AND p.citation NOT LIKE '%amend%'
    """).fetchall()
    provs = {}
    for pid, cite, vid, vstart, vtext in rows:
        provs[pid] = dict(pid=pid, cite=cite, vid=vid, vstart=vstart, text=vtext)
    for pid in provs:
        amds = con.execute("""
            SELECT effective_date, source_url, amendment_number, affected, raw
            FROM amendments WHERE provision_id=? AND effective_date>=?
            ORDER BY effective_date
        """, (pid, REORG)).fetchall()
        provs[pid]["amds"] = [dict(eff=a[0], url=a[1], num=a[2], affected=a[3], raw=a[4])
                              for a in amds if a[1]]
    return {pid: p for pid, p in provs.items() if p["amds"]}


def parse_cite(cite):
    m = re.search(r"art\.\s+([IVXLC]+),\s+§\s+(\w+)", cite)
    return (m.group(1), m.group(2)) if m else (None, None)


def is_pure_single(p):
    """Phase-1 gate: every amendment single-section, none create/new-article."""
    for a in p["amds"]:
        if (a["affected"] or "").count(";") >= 1:
            return False
        if re.search(r"new article|creat", (a["raw"] or ""), re.I):
            return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", type=Path, default=Path("/tmp/const-scratch.db"))
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--batch", default="modern-versions-2026-06-14")
    args = ap.parse_args()

    con = sqlite3.connect(args.db)
    scope = load_scope(con)
    pure = {pid: p for pid, p in scope.items()
            if is_pure_single(p) and not p["text"].strip().lower().startswith("repealed")}
    repealed = sum(1 for p in scope.values()
                   if is_pure_single(p) and p["text"].strip().lower().startswith("repealed"))
    print(f"DB: {args.db}")
    print(f"modern provisions with linked post-1981 amendments: {len(scope)}")
    print(f"phase-1 pure single-section scope: {len(pure)} "
          f"(+{repealed} repealed-current → repeal handling, deferred)\n")

    targets = list(pure.values())
    if args.limit:
        targets = targets[:args.limit]

    # Classify the LATEST amendment per provision (anchors the chain to current text).
    cls_count = {"CLEAN": 0, "MARKUP": 0, "MISMATCH": 0, "LOCATE_FAIL": 0}
    rows = []          # (cite, latest_class, per-amendment classes)
    splices = []       # auto-splice-eligible: latest CLEAN and all priors located
    for p in targets:
        roman, secnum = parse_cite(p["cite"])
        if not roman:
            continue
        extracts, per = {}, []
        for a in p["amds"]:
            pdf = resolve_pdf(a["url"])
            txt = extract_reenact(pdftext(pdf), roman, secnum) if pdf else None
            extracts[a["eff"]] = txt
            per.append("LOCATE_FAIL" if txt is None else classify(txt, p["text"]))
        last_txt = extracts[p["amds"][-1]["eff"]]
        latest_cls = "LOCATE_FAIL" if last_txt is None else classify(last_txt, p["text"])
        cls_count[latest_cls] += 1
        rows.append((p["cite"], latest_cls, per))
        # auto-splice only when EVERY amendment extracts CLEAN — never write a
        # markup-mangled prior. (Priors can't be gated vs current; require clean.)
        if latest_cls == "CLEAN" and all(x == "CLEAN" for x in per):
            splices.append((p, extracts, per))

    print(f"=== PHASE-1 RESULTS over {len(targets)} provisions "
          f"(classified by LATEST amendment) ===")
    for k in ("CLEAN", "MARKUP", "MISMATCH", "LOCATE_FAIL"):
        print(f"  latest = {k:<12} {cls_count[k]}")
    print(f"  auto-splice-eligible (latest CLEAN + all priors located): {len(splices)}")
    print("\n  --- per-provision (latest | all-amendment classes) ---")
    for cite, lc, per in sorted(rows, key=lambda r: r[1]):
        print(f"    {cite:<28} {lc:<12} {per}")

    if args.apply and splices:
        apply_splices(con, [(p, ex) for p, ex, _ in splices], args.batch)
        con.commit()
        print(f"\nAPPLIED {len(splices)} provision timelines (batch {args.batch})")
        run_integrity(con)
    elif splices:
        print(f"\n(dry run) would splice {len(splices)} provisions; sample timelines:")
        for p, ex, _ in splices[:4]:
            show_timeline(p, ex)
    con.close()


def build_intervals(p, extracts):
    """Return ordered [(start, end, text, amd)] for a provision's timeline."""
    amds = p["amds"]
    out = []
    for i, a in enumerate(amds):
        start = a["eff"]
        end = (date.fromisoformat(amds[i + 1]["eff"]) - timedelta(days=1)).isoformat() \
            if i + 1 < len(amds) else None
        # latest version uses the clean current DB text; priors use CAA extract
        text = p["text"] if i == len(amds) - 1 else extracts[a["eff"]]
        out.append((start, end, text, a))
    return out


def show_timeline(p, extracts):
    print(f"  {p['cite']}  (was 1 version @ {p['vstart']})")
    for start, end, text, a in build_intervals(p, extracts):
        print(f"    [{start} → {end or 'open'}]  {a['num'] or '?':<8} {len(tokens(text))} tok")


def apply_splices(con, splices, batch):
    for p, extracts in splices:
        ivals = build_intervals(p, extracts)
        # idempotency: drop prior reconstructed versions for this provision
        con.execute("DELETE FROM provision_versions WHERE provision_id=? AND batch=?",
                    (p["pid"], batch))
        last_vid = None
        for start, end, text, a in ivals:
            if end is None:
                # update the existing current version's start; keep its text
                con.execute("UPDATE provision_versions SET effective_start=? WHERE id=?",
                            (start, p["vid"]))
                last_vid = p["vid"]
            else:
                vid = con.execute(
                    "INSERT INTO provision_versions (provision_id, effective_start, "
                    "effective_end, text_content, source_authority, source_url, "
                    "source_path, batch) VALUES (?,?,?,?,?,?,?,?)",
                    (p["pid"], start, end, text,
                     f"amend. {a['num']} (session law)", a["url"], None, batch)).lastrowid
                con.execute(
                    "INSERT INTO changelog (batch, provision_id, version_id, field, "
                    "old_value, new_value, authority) VALUES (?,?,?,?,?,?,?)",
                    (batch, p["pid"], vid, "version_splice", None,
                     f"[{start} → {end}] amend. {a['num']}", a["url"]))


def run_integrity(con):
    gaps = con.execute("""
        WITH v AS (SELECT provision_id, effective_start, effective_end,
          LEAD(effective_start) OVER (PARTITION BY provision_id ORDER BY effective_start) nxt
          FROM provision_versions)
        SELECT count(*) FROM v WHERE nxt IS NOT NULL AND effective_end IS NOT NULL
          AND effective_end!='' AND date(effective_end)!=date(nxt)
          AND date(effective_end,'+1 day')!=date(nxt)""").fetchone()[0]
    multi = con.execute("""
        SELECT count(*) FROM (SELECT p.id FROM provisions p
          JOIN provision_versions v ON v.provision_id=p.id
          WHERE p.corpus='const' AND (v.effective_end IS NULL OR v.effective_end='')
          GROUP BY p.id HAVING count(*)>1)""").fetchone()[0]
    print(f"  integrity: gaps/overlaps={gaps}  >1-open={multi}  (expect 0/0)")


if __name__ == "__main__":
    main()
