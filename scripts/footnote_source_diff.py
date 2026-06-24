"""Phase 2a: deterministic source-vs-DB footnote diff engine.

For each footnote-signal opinion, extract the TRUE footnote set from its
authoritative source and compare to what the DB stores. Emits a discrepancy
report (TSV) that routes opinions to the agent-judgment batches.

Source extractors (best-first):
  - archive HTML  : ``name="FN_N_"`` anchors; body = the longest text following an
                    FN_N_ anchor (bounded by the next FN anchor / back-link).
  - West .doc      : via ``textutil``; footnote bodies are standalone "N" lines in
                    the zone before the "All Citations" footer.  (best-effort count)
DB side: ``proofread.footnote_structure`` detected count + a scan for present-but-
malformed bodies (digit-abutting / nbsp / number-less period orphan).

status: MATCH (src==detected, clean) | SRC_MORE (footnotes missing/malformed in DB)
        | DB_MORE (DB has more than source — possible spurious) | NO_AUTO_SOURCE
        | EXTRACT_FAIL. Read-only.
"""
import html as H
import os
import re
import subprocess
import sys
from collections import defaultdict

import ndcourts_mcp.proofread as pr

REFS = os.path.expanduser("~/refs/nd/opin")
TRIAGE = "triage/footnote-corpus-triage-2026-06-23.tsv"
FN_ANCHOR = re.compile(r'name="FN_(\d+)_"')
RETURN_LINK = re.compile(r'href="#(?:FN)?N?\d')


def _clean(s):
    s = H.unescape(re.sub(r"<[^>]+>", " ", s))
    return re.sub(r"\s+", " ", s).strip()


def extract_archive(path):
    """-> {num: body_text} from archive HTML FN_N_ anchors."""
    h = open(path, encoding="latin-1").read()
    anchors = [(int(m.group(1)), m.start(), m.end()) for m in FN_ANCHOR.finditer(h)]
    if not anchors:
        return {}
    bodies = {}
    starts = sorted(a[1] for a in anchors)
    for num, s, e in anchors:  # document order; the body def is the LAST occurrence
        nxt = min([p for p in starts if p > s] + [len(h)])
        seg = _clean(h[e:nxt])
        seg = re.sub(r"^[\(\[]?\d+[\)\]]?\.?\s*", "", seg)  # drop leading "N." / "(N)"
        if seg:
            bodies[num] = seg
    return bodies


def extract_westdoc(path):
    """-> {num: body_text} from a West .doc.

    The .doc files are RTF; Westlaw encodes footnotes as bookmarked table rows,
    which is authoritative. The old textutil ``N\\nbody`` heuristic over-counted
    badly (e.g. 1893 ND 17 "36" phantom footnotes). Delegates to
    ``westdoc_footnotes.extract_westdoc_rtf``.
    """
    from westdoc_footnotes import extract_westdoc_rtf
    return extract_westdoc_rtf(path)


def db_footnotes(text):
    st = pr.footnote_structure(text)
    detected = sorted(n for n, _, _ in st["bodies"])
    # present-but-malformed signals
    malformed = (len(re.findall(r"\n\n[ \xa0]?\d{1,2}[A-Za-z]", text))
                 + len(re.findall(r"\xa0\d{1,2}\n", text)))
    orphan = len(re.findall(r"(?<!\d)\n\n ?\. [A-Z\"“]", text))
    return detected, malformed, orphan


def pick_source(vs):
    for tag in ("archive", "westlaw_doc", "pdf", "nw_scan"):
        for part in vs.split(" | "):
            if part.startswith(tag + ":"):
                return tag, part.split(":", 1)[1]
    return None, None


def main():
    import sqlite3
    db = sys.argv[1] if len(sys.argv) > 1 else "opinions.db"
    only = sys.argv[2] if len(sys.argv) > 2 else None  # optional bucket filter
    con = sqlite3.connect(db)
    print("\t".join(["id", "cite", "bucket", "src", "src_n", "db_det", "db_mal",
                     "db_orph", "status", "src_nums"]))
    from collections import Counter
    stat = Counter()
    for ln in open(TRIAGE):
        p = ln.rstrip("\n").split("\t")
        if len(p) < 12 or p[0] == "id" or p[3] == "CLEAN" and only != "CLEAN":
            continue
        oid, cite, bucket, vs = int(p[0]), p[1], p[3], p[11]
        if only and bucket != only:
            continue
        tag, sp = pick_source(vs)
        text = con.execute("SELECT text_content FROM opinions WHERE id=?", (oid,)).fetchone()[0]
        det, mal, orph = db_footnotes(text)
        srcfn = {}
        status = "NO_AUTO_SOURCE"
        if tag == "archive":
            path = os.path.join(REFS, sp)
            if os.path.exists(path):
                srcfn = extract_archive(path)
                status = "EXTRACT_FAIL" if not srcfn else "?"
        elif tag == "westlaw_doc":
            path = sp if os.path.isabs(sp) else os.path.join(REFS, sp)
            if os.path.exists(path):
                r = extract_westdoc(path)
                srcfn = r or {}
                status = "EXTRACT_FAIL" if not srcfn else "?"
        if status == "?":
            sn = len(srcfn)
            if sn == len(det) and mal == 0 and orph == 0:
                status = "MATCH"
            elif sn > len(det):
                status = "SRC_MORE"
            elif sn < len(det):
                status = "DB_MORE"
            else:  # equal count but malformed/orphan present
                status = "CHECK_MARKERS"
        stat[status] += 1
        print("\t".join([str(oid), cite, bucket, tag or "-", str(len(srcfn)),
                         str(len(det)), str(mal), str(orph), status,
                         ",".join(map(str, sorted(srcfn))) or "-"]))
    for s, n in stat.most_common():
        print(f"# {s}\t{n}", file=sys.stderr)


if __name__ == "__main__":
    main()
