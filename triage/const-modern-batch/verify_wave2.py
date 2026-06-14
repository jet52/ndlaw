#!/usr/bin/env python3
"""Verify Wave-2 agent outputs + the independent second reads.

Gates (no agent output trusted until it passes):
  MECH  : every edit_list after-anchor occurs exactly once in current_text and
          apply(edit_list, current_text) == agent prior_text (whitespace-norm).
  AGREE : (second reads only) the second agent's reconstructed prior equals the
          Wave-1 agent's reconstructed prior (normalized). Agreement promotes a
          Wave-1 'needs-2nd-read' provision to confirmed.
  BB    : where the article is clean in the 1981 Blue Book (VIII/X/XI), the prior
          must appear (normalized substring / fuzzy). None of these redlines are
          in clean-BB articles, so they rely on MECH (+ AGREE for the ten).
"""
import json, re, glob, difflib, importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Wave-1 edit_lists (the first independent read) live in verify_and_splice.RESULTS
spec = importlib.util.spec_from_file_location("vs", HERE / "verify_and_splice.py")
VS = importlib.util.module_from_spec(spec); spec.loader.exec_module(VS)
W1 = VS.RESULTS                      # {cite: (d1, edit_list)}
W1_CUR = VS.current_texts()          # {cite: current_text} from original batch-*.json


def norm(s):
    return re.sub(r"\s+", " ", s or "").strip()


def keynorm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def apply_edits(text, edits):
    for after, before in edits:
        c = text.count(after)
        if c != 1:
            raise ValueError(f"anchor x{c}: {after[:45]!r}")
        text = text.replace(after, before)
    return text


def load_inputs():
    cur = {}
    for f in glob.glob(str(HERE / "wave2-batch-*.json")) + [str(HERE / "secondread-batch.json")]:
        for t in json.loads(Path(f).read_text()):
            cur[t["citation"]] = norm(t["current_text"])
    return cur


def main():
    cur = load_inputs()
    results = {}   # cite -> dict(prior, d1, mech, agree, source)
    for f in sorted(glob.glob(str(HERE / "out" / "*.json"))):
        is_sr = f.endswith("secondread.json")
        for o in json.loads(Path(f).read_text()):
            if o["classification"] != "REDLINE":
                continue
            cite = o["citation"]; d1 = o["amendment_date"]
            c = cur.get(cite)
            rec = {"d1": d1, "src": "2nd-read" if is_sr else "wave2", "flags": o.get("flags", [])}
            # MECH gate
            try:
                recomputed = apply_edits(c, [tuple(e) for e in o["edit_list"]])
                rec["mech"] = (keynorm(recomputed) == keynorm(o.get("prior_text")))
                rec["prior"] = norm(o.get("prior_text"))
            except Exception as e:
                rec["mech"] = False; rec["prior"] = None; rec["mech_err"] = str(e)
            # AGREE gate (second reads vs Wave-1)
            if is_sr and cite in W1:
                w1_prior = apply_edits(W1_CUR[cite], W1[cite][1])
                rec["agree"] = (keynorm(w1_prior) == keynorm(rec.get("prior")))
            results[cite] = rec

    print("=== WAVE-2 + SECOND-READ VERIFICATION ===\n")
    print("Second reads (AGREE = matches Wave-1 independent read):")
    for cite, r in sorted(results.items()):
        if r["src"] != "2nd-read":
            continue
        ag = r.get("agree")
        tag = "AGREE" if ag else ("DISAGREE" if ag is False else "—")
        print(f"  {cite.replace('N.D. Const. ',''):16} MECH={'ok' if r['mech'] else 'FAIL':4} "
              f"{tag:9} {r.get('mech_err','')}")
    print("\nNew Wave-2 redlines (no clean-BB witness -> scratch + needs-2nd-read):")
    for cite, r in sorted(results.items()):
        if r["src"] == "wave2":
            print(f"  {cite.replace('N.D. Const. ',''):16} MECH={'ok' if r['mech'] else 'FAIL':4} "
                  f"flags={r['flags']} {r.get('mech_err','')}")
    # persist for the splice step
    (HERE / "wave2-verified.json").write_text(json.dumps(
        {c: {k: v for k, v in r.items() if k != "prior"} | {"prior": r.get("prior")}
         for c, r in results.items()}, ensure_ascii=False, indent=2))
    n_agree = sum(1 for r in results.values() if r.get("agree"))
    n_mech = sum(1 for r in results.values() if r["mech"])
    print(f"\nMECH ok: {n_mech}/{len(results)}   AGREE (of 10 second reads): {n_agree}")


if __name__ == "__main__":
    main()
