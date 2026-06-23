"""Phase 0 of the corpus footnote pass: classify EVERY opinion by footnote
health + lineage + best verification source. Deterministic, read-only. Drives the
source-vs-DB reconciliation batches (agents propose, harness applies).

Emits a TSV: one row per opinion with its bucket, signal flags, and the on-disk
authoritative source(s) an agent should diff against.

Buckets (primary, by priority):
  WEST_HEADNOTE   - carries West key-number [N] brackets to strip (lineage-gated)
  MALFORMED       - footnote body present but marker broken (NCapital / nbsp+digit)
  PERIOD_ORPHAN   - number-less ". Body" orphan(s) (ambiguous: fn vs heading/ellipsis)
  NOTES_SECTION   - has NOTES/FOOTNOTES section
  CLEAN           - parser detects footnotes, no broken signals
  NONE            - no footnote signal
An opinion may carry several flags; `bucket` is the highest-priority repair need.
`verify_sources` lists existing source files (archive/westlaw/nw_scan/pdf) for the
Phase-2 source-vs-DB diff.
"""
import os
import re
import sqlite3
import sys

import ndcourts_mcp.proofread as pr

REFS = os.path.expanduser("~/refs/nd/opin")
NEUTRAL = re.compile(r"^(\d{4})\s+ND\s+(\d+)$")
KEYNUM = re.compile(r"\[\d{1,3}\]")
# A true number-less period orphan: "\n\n. Body" NOT preceded by a bare-number
# line (those are already-numbered footnote bodies "N\n\n. Body").
PERIOD_ORPHAN = re.compile(r"(?<!\d)\n\n ?\. [A-Z\"“]")
MALFORMED = re.compile(r"\n\n[ \xa0]?\d{1,2}[A-Za-z]")    # digit immediately abutting body
NBSP_MARK = re.compile(r"\xa0\d{1,2}\n")
NOTES_HDR = re.compile(r"\n[ \t]*(NOTES|FOOTNOTES)[ \t]*\n")


def lineage(sp):
    if not sp:
        return "none"
    if sp.endswith(".doc"):
        return "westlaw_doc"
    if sp.startswith("markdown/"):
        return "markdown"
    if sp.startswith("NW2d/") or sp.startswith("NW/"):
        return "nw_scan"
    if sp.startswith("archive/"):
        return "archive"
    if sp.startswith("N.D./"):
        return "nd_doc"
    return "other"


def main():
    db = sys.argv[1] if len(sys.argv) > 1 else "opinions.db"
    con = sqlite3.connect(db)
    # all source files per opinion
    srcs = {}
    for oid, sp in con.execute("SELECT opinion_id, source_path FROM opinion_sources"):
        srcs.setdefault(oid, []).append(sp)
    # neutral cite per opinion (first ND cite)
    cite = {}
    for oid, c in con.execute("SELECT opinion_id, citation FROM citations WHERE citation LIKE '% ND %'"):
        m = NEUTRAL.match(c.strip())
        if m and oid not in cite:
            cite[oid] = f"{m.group(1)} ND {m.group(2)}"

    out = ["\t".join(["id", "cite", "lineage", "bucket", "det_nums", "contig",
                      "n_orphan", "n_malformed", "n_nbsp", "west_brackets",
                      "notes_hdr", "verify_sources"])]
    from collections import Counter
    bcount = Counter()
    for oid, sp, t in con.execute(
            "SELECT id, source_path, text_content FROM opinions WHERE text_content IS NOT NULL"):
        lin = lineage(sp)
        st = pr.footnote_structure(t)
        nums = sorted(n for n, _, _ in st["bodies"])
        contig = "y" if nums and nums == list(range(1, len(nums) + 1)) else ("n" if nums else "-")
        n_orphan = len(PERIOD_ORPHAN.findall(t))
        n_mal = len(MALFORMED.findall(t))
        n_nbsp = len(NBSP_MARK.findall(t))
        # West key-number brackets only count in non-markdown lineages (markdown [N]
        # are footnote calls); require a clustered/line-adjacent shape to reduce
        # statutory-ref noise.
        wb = 0
        if lin in ("westlaw_doc", "nw_scan", "other", "nd_doc"):
            wb = len(re.findall(r"(?m)(?:^|\n)\s*\[\d{1,3}\](?:\s*\[\d{1,3}\])*\s*\[?¶?", t))
        notes = bool(NOTES_HDR.search(t))

        if wb > 0:
            bucket = "WEST_HEADNOTE"
        elif n_mal > 0 or n_nbsp > 0:
            bucket = "MALFORMED"
        elif n_orphan > 0:
            bucket = "PERIOD_ORPHAN"
        elif notes:
            bucket = "NOTES_SECTION"
        elif nums:
            bucket = "CLEAN"
        else:
            bucket = "NONE"
        bcount[bucket] += 1

        # verification sources that exist on disk, best-first
        vs = []
        for s in srcs.get(oid, []):
            p = os.path.join(REFS, s)
            tag = lineage(s)
            if os.path.exists(p):
                vs.append(f"{tag}:{s}")
        if oid in cite:
            y, n = cite[oid].split(" ND ")
            pdf = f"pdfs/{y}/{y}ND{n}.pdf"
            if os.path.exists(os.path.join(REFS, pdf)):
                vs.append(f"pdf:{pdf}")

        if bucket != "NONE":
            out.append("\t".join([str(oid), cite.get(oid, ""), lin, bucket,
                                   ",".join(map(str, nums)) or "-", contig,
                                   str(n_orphan), str(n_mal), str(n_nbsp), str(wb),
                                   "y" if notes else "-", " | ".join(vs) or "NO_SOURCE"]))
    print("\n".join(out))
    for b, n in bcount.most_common():
        print(f"# {b}\t{n}", file=sys.stderr)


if __name__ == "__main__":
    main()
