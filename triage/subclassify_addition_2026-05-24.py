"""Sub-classify the 248 ADDITION residue rows (Westlaw adds detail the DB lacks)
into the established ADDS_DETAIL buckets, and propose a title-cased name for each.

Reuses the bucket logic from triage/subclassify_adds_detail_2026-05-20.py and the
clean proposer from the Phase-1 sweep. Buckets the user previously ratified for
auto-accept: LOCALITY_OF, ROLE_APPOSITIVE, PAREN_PARTY. The rest
(ESTATE_REFRAME, MULTICASE_MISSED, LONG_PLEADING, DOCKET_METADATA,
STATE_EXPANSION, OTHER) were deferred to TUI before — shown here for review.

Dry-run only: writes triage/addition-subclassified-2026-05-24.tsv and prints
the distribution + per-bucket samples. No DB writes.
"""
from __future__ import annotations

import csv
import importlib.util
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, REPO / "triage" / path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_sub = _load("subclassify_adds_detail", "subclassify_adds_detail_2026-05-20.py")
_sweep = _load("residue_sweep", "sweep_residue_patterns_2026-05-24.py")
subclassify = _sub.subclassify
propose = _sweep.propose

ADJ = REPO / "triage" / "residue-adjudication-2026-05-24.tsv"
CLASSIFIED = REPO / "triage" / "casenames-ambig-review-classified-2026-05-20.tsv"
OUT = REPO / "triage" / "addition-subclassified-2026-05-24.tsv"

RATIFIED_ACCEPT = {"LOCALITY_OF", "ROLE_APPOSITIVE", "PAREN_PARTY"}


def main() -> int:
    wlnorm = {r["opinion_id"]: r["wl_norm"]
              for r in csv.DictReader(CLASSIFIED.open(), delimiter="\t")}
    rows = [r for r in csv.DictReader(ADJ.open(), delimiter="\t")
            if r["kind"] == "ADDITION"]

    out = []
    for r in rows:
        oid = r["oid"]
        wln = wlnorm.get(oid, r["wl"])
        sub = subclassify(r["db"], wln)
        out.append(dict(oid=oid, vol=r["vol"], sub=sub,
                        ratified=("YES" if sub in RATIFIED_ACCEPT else ""),
                        db=r["db"], proposed=propose(wln), wl=wln))

    cols = ["oid", "vol", "sub", "ratified", "db", "proposed", "wl"]
    with OUT.open("w") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, delimiter="\t", extrasaction="ignore")
        w.writeheader()
        w.writerows(out)

    counts = Counter(r["sub"] for r in out)
    ratified_n = sum(1 for r in out if r["ratified"])
    print(f"ADDITION rows: {len(out)}  ->  {OUT.relative_to(REPO)}")
    print(f"\nSub-bucket distribution (ratified-accept buckets marked *):")
    for k in sorted(counts, key=lambda x: -counts[x]):
        mark = " *" if k in RATIFIED_ACCEPT else ""
        print(f"  {k:<18} {counts[k]:>4}{mark}")
    print(f"\n  ratified-accept (LOCALITY/ROLE/PAREN) auto-eligible: {ratified_n}")
    print(f"  other (review/TUI): {len(out) - ratified_n}")

    by = defaultdict(list)
    for r in out:
        by[r["sub"]].append(r)
    print("\n--- samples per bucket ---")
    for sub in sorted(by, key=lambda x: -len(by[x])):
        print(f"\n[{sub}]")
        for r in by[sub][:3]:
            print(f"  {r['oid']:>5} v{r['vol']}  {r['db']!r}")
            print(f"         => {r['proposed']!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
