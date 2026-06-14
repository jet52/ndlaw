#!/usr/bin/env python3
"""Markup (Claude-direct-read) splice step.

For redline measures pdftotext/marker cannot resolve, a human (Claude) reads the
rendered page and records the small per-amendment EDIT LIST as (after_phrase,
before_phrase) pairs. This script reverse-applies those edits to the clean
current DB text to derive each prior version FAITHFULLY (no bulk re-transcription
of authoritative text), gates, and splices — idempotent, with integrity check.

Why edit-list not full transcription: the after-text is gate-checkable against
the DB; a hand-typed before-text would be unverified. Reverse-applying a handful
of read-with-high-confidence edits to the verified current text keeps every
prior version anchored to authoritative text + a reviewable diff.

transcriptions.json schema:
{
  "<citation>": {
     "<eff_date>": {"edits": [["after_phrase","before_phrase"], ...]},
     ...   # oldest..newest; after(newest) == current DB text
  }
}
The newest amendment's edits transform current→its-prior; the next-older's edits
transform that prior→its-prior; etc. Each edit's after_phrase must be UNIQUE in
the text it is applied to (asserted).
"""
import argparse, json, sqlite3, importlib.util, re
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "recon", HERE.parent.parent / "scripts" / "reconstruct_modern_versions.py")
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)


import re as _re
_BB = None

def bb_norm(t):
    return _re.sub(r"[^a-z0-9]", "", t.lower())

def bb_gate(prior_text):
    """Independent witness: does the reconstructed [1981,d1) prior appear
    (near-verbatim) in the 1981 Blue Book? Returns 'PASS'/'CHECK'/'NA'.
    The BB carries the renumbered constitution as of Jan 1981, so a
    single-amendment-since-1981 provision's earliest prior must match it."""
    global _BB
    if _BB is None:
        p = Path.home() / "refs/nd/const/processed/1981_blue-book_constitution.md"
        _BB = bb_norm(p.read_text()) if p.exists() else ""
    if not _BB:
        return "NA"
    n = bb_norm(prior_text)
    if n in _BB:
        return "PASS"
    # large sections won't exact-match OCR'd BB; allow high fuzzy ratio on the
    # best-aligned window (handles scattered BB OCR char errors).
    import difflib
    sm = difflib.SequenceMatcher(None, n, _BB)
    m = sm.find_longest_match(0, len(n), 0, len(_BB))
    b0 = max(0, m.b - m.a)
    win = _BB[b0:b0 + len(n)]
    r = difflib.SequenceMatcher(None, n, win).ratio()
    return f"NEAR({r:.3f})" if r >= 0.97 else f"CHECK({r:.3f})"


def reverse_apply(text, edits):
    """Apply (after→before) edits to `text`, asserting each after_phrase is
    present exactly once. Returns the prior-version text."""
    for after, before in edits:
        n = text.count(after)
        if n != 1:
            raise ValueError(f"edit not unique ({n}x): {after!r}")
        text = text.replace(after, before)
    return text


def ocr_quality(text):
    """Cheap OCR-degradation signal for a base_text sourced from an OCR'd
    compilation: fraction of 1-char alpha tokens (letter-spacing) + obvious
    junk. >0.15 = too degraded for the authoritative bar → needs native source."""
    toks = re.findall(r"[A-Za-z]+", text)
    if not toks:
        return 1.0
    singles = sum(1 for t in toks if len(t) == 1)
    return singles / len(toks)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", type=Path, default=Path("/tmp/const-scratch.db"))
    ap.add_argument("--trans", type=Path, default=HERE / "transcriptions.json")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--batch", default="modern-versions-markup-2026-06-14")
    args = ap.parse_args()

    trans = json.loads(args.trans.read_text())
    con = sqlite3.connect(args.db)
    scope = {p["cite"]: p for p in R.load_scope(con).values()}

    plans = []
    for cite, amds in trans.items():
        p = scope[cite]
        # build version texts newest→oldest by reverse-applying edits.
        # normalize current-text whitespace (ndconst.org line-wraps are artifacts)
        # so single-spaced edit phrases match; priors store single-spaced.
        dates = sorted(d for d in amds if not d.startswith("_"))  # oldest..newest
        cur = " ".join(p["text"].split())
        texts = {}                                   # eff_date -> after-text of that amendment
        running = cur
        ocr = 0.0
        for d in reversed(dates):                    # newest first
            texts[d] = running                       # after-text of amendment d
            ent = amds[d]
            if "base_text" in ent:                   # BB-as-base path: prior given directly
                running = " ".join(ent["base_text"].split())
                ocr = ocr_quality(running)           # flag OCR-degraded BB source
            else:
                running = reverse_apply(running, ent["edits"])  # -> prior (before d)
        base_text = running                          # text before the oldest amendment
        # gate: newest after-text == current (consistency; vacuous for 1 amendment)
        newest = dates[-1]
        ok = R.tokens(texts[newest]) == R.tokens(cur)
        bb = bb_gate(base_text) if ocr < 0.15 else f"OCR-DEGRADED({ocr:.2f})"
        ok = ok and not bb.startswith(("CHECK", "OCR"))
        plans.append((p, dates, texts, base_text, ok, bb))

    print(f"DB: {args.db}   markup provisions: {len(plans)}")
    for p, dates, texts, base, ok, bb in plans:
        print(f"\n  {p['cite']}  consistency={'ok' if ok else 'FAIL'}  "
              f"1981-BB={bb}  was 1 version @ {p['vstart']}")
        # show resulting intervals: base + one per amendment
        bounds = [R.REORG] + dates
        for i, d in enumerate(dates):
            start = R.REORG if i == 0 else dates[i - 1]
            txt = base if i == 0 else texts[dates[i - 1]]
            end = (date.fromisoformat(d) - timedelta(days=1)).isoformat()
            print(f"    [{start} → {end}]  {len(R.tokens(txt))} tok  (before amd {d})")
        print(f"    [{dates[-1]} → open]  {len(R.tokens(texts[dates[-1]]))} tok  (current)")

    if args.apply:
        n = 0
        for p, dates, texts, base, ok, bb in plans:
            if not ok:
                print(f"  SKIP (gate fail: consistency/BB) {p['cite']}"); continue
            con.execute("DELETE FROM provision_versions WHERE provision_id=? AND batch=?",
                        (p["pid"], args.batch))
            # current version: set start to newest amendment date
            con.execute("UPDATE provision_versions SET effective_start=? WHERE id=?",
                        (dates[-1], p["vid"]))
            for i, d in enumerate(dates):
                start = R.REORG if i == 0 else dates[i - 1]
                txt = base if i == 0 else texts[dates[i - 1]]
                end = (date.fromisoformat(d) - timedelta(days=1)).isoformat()
                vid = con.execute(
                    "INSERT INTO provision_versions (provision_id, effective_start, "
                    "effective_end, text_content, source_authority, batch) "
                    "VALUES (?,?,?,?,?,?)",
                    (p["pid"], start, end, txt, f"prior to amend. (markup read)",
                     args.batch)).lastrowid
                con.execute("INSERT INTO changelog (batch, provision_id, version_id, "
                            "field, new_value) VALUES (?,?,?,?,?)",
                            (args.batch, p["pid"], vid, "version_splice_markup",
                             f"[{start} → {end}]"))
            n += 1
        con.commit()
        print(f"\nAPPLIED {n} markup reconstructions")
        R.run_integrity(con)
    con.close()


if __name__ == "__main__":
    main()
