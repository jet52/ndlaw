"""Apply auto-classifications from casenames-ambig-review-classified-2026-05-20.tsv.

  - ACCEPT_WL_OCR_FIX / ACCEPT_WL_ENCODING_FIX (47): UPDATE case_name
    under batch 'fix-casenames-vol16-79-autorev-2026-05-20'. Westlaw
    wl_norm is re-title-cased here using the fixed Mc/Mac/'s/'rs rules
    (review_casenames._smart_titlecase has known bugs).
  - KEEP_DB_PURE_ABBREV / KEEP_DB_HAS_REL (695): record in
    triage/casenames-state.json kept_db so the interactive TUI skips
    these. No DB change.

Dry-run by default. --apply commits.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from ndcourts_mcp.db import DEFAULT_DB_PATH, get_connection  # noqa: E402

INPUT = REPO / "triage" / "casenames-ambig-review-classified-2026-05-20.tsv"
STATE = REPO / "triage" / "casenames-state.json"
BATCH = "fix-casenames-vol16-79-autorev-2026-05-20"


def norm_unicode(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = s.replace("’", "'").replace("‘", "'")
    s = s.replace("“", '"').replace("”", '"')
    s = re.sub(r"[̀-ͯ]", "", s)
    return s


def smart_titlecase(s: str) -> str:
    """Title-case a case name. Handles Mc/Mac mixed-case + all-caps, O'
    prefix, 's possessive, 'rs/'r abbreviation."""
    s = norm_unicode(s)
    lowercase_tokens = {"v.", "v", "ex", "rel.", "rel", "and", "of", "the",
                        "in", "re", "et", "al.", "for", "to", "&"}
    out = []
    for word in s.split(" "):
        wl = word.lower()
        if wl in lowercase_tokens and out:
            out.append(wl)
            continue
        # Mixed-case Mc/Mac (e.g. "McKEE'S")
        mm = re.match(r"^(Mc|Mac)([A-Z]+)(.*)$", word)
        if mm and mm.group(2):
            pre, body, tail = mm.groups()
            first, rest = body[0], body[1:]
            tail = tail.title()
            tail = re.sub(r"'S(?=\W|$)", "'s", tail)
            tail = re.sub(r"'Rs(?=\W|$)", "'rs", tail)
            tail = re.sub(r"'R(?=\W|$)", "'r", tail)
            out.append(f"{pre}{first}{rest.lower()}{tail}")
            continue
        if word.isupper() and len(word) > 1:
            if re.fullmatch(r"[A-Z]\.(?:[A-Z]\.)+", word):
                out.append(word)
                continue
            mm2 = re.match(r"^(Mc|Mac)([A-Z])([A-Z]+)(.*)$", word)
            if mm2:
                pre, first, rest, tail = mm2.groups()
                tail = tail.title()
                tail = re.sub(r"'S(?=\W|$)", "'s", tail)
                tail = re.sub(r"'Rs(?=\W|$)", "'rs", tail)
                out.append(f"{pre}{first}{rest.lower()}{tail}")
                continue
            om = re.match(r"^O'([A-Z])([A-Z]*)(.*)$", word)
            if om:
                first, rest, tail = om.groups()
                tail = tail.title()
                tail = re.sub(r"'S(?=\W|$)", "'s", tail)
                out.append(f"O'{first}{rest.lower()}{tail}")
                continue
            titled = word.title()
            titled = re.sub(r"'S(?=\W|$)", "'s", titled)
            titled = re.sub(r"'Rs(?=\W|$)", "'rs", titled)
            titled = re.sub(r"'R(?=\W|$)", "'r", titled)
            out.append(titled)
        else:
            out.append(word)
    return " ".join(out)


def load_state() -> dict:
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"schema_version": 1, "kept_db": {}}


def save_state(state: dict) -> None:
    STATE.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    rows = list(csv.DictReader(INPUT.open(), delimiter="\t"))
    # csv.DictReader leaves trailing \r on the last column; strip.
    for r in rows:
        for k, v in list(r.items()):
            if isinstance(v, str):
                r[k] = v.rstrip("\r")

    accept_rows = [r for r in rows if r["verdict"] in
                   ("ACCEPT_WL_OCR_FIX", "ACCEPT_WL_ENCODING_FIX")]
    keep_rows = [r for r in rows if r["verdict"] in
                 ("KEEP_DB_PURE_ABBREV", "KEEP_DB_HAS_REL")]

    print(f"=== ACCEPT_WL (DB updates): {len(accept_rows)} ===")
    conn = get_connection(DEFAULT_DB_PATH)
    cur = conn.cursor()
    applied = 0
    for r in accept_rows:
        oid = int(r["opinion_id"])
        old = cur.execute(
            "SELECT case_name FROM opinions WHERE id = ?", (oid,)
        ).fetchone()
        if not old:
            print(f"  oid {oid}: missing, skipping")
            continue
        new = smart_titlecase(r["wl_norm"])
        if old["case_name"] == new:
            continue
        print(f"  oid {oid:>6}  {old['case_name']!r}  ->  {new!r}")
        if args.apply:
            cur.execute(
                "UPDATE opinions SET case_name = ? WHERE id = ?", (new, oid)
            )
            cur.execute(
                "INSERT INTO changelog (batch, opinion_id, field, old_value, "
                "new_value) VALUES (?, ?, 'case_name', ?, ?)",
                (BATCH, oid, old["case_name"], new),
            )
            applied += 1

    print(f"\n=== KEEP_DB (state.json only): {len(keep_rows)} ===")
    state = load_state()
    kept = state.setdefault("kept_db", {})
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    added_state = 0
    for r in keep_rows:
        oid = str(r["opinion_id"])
        if oid in kept:
            continue
        entry = {
            "volume": int(r["volume"]),
            "db_name": r["db_name"],
            "wl_raw": r["wl_raw"],
            "ts": now,
            "source": BATCH,
            "verdict": r["verdict"],
        }
        if args.apply:
            kept[oid] = entry
            added_state += 1

    if args.apply:
        conn.commit()
        save_state(state)
        print(f"\nApplied:")
        print(f"  {applied} case_name UPDATE(s) under batch '{BATCH}'")
        print(f"  {added_state} kept_db entries added to {STATE.relative_to(REPO)}")
        print(f"  revert UPDATEs: python -m ndcourts_mcp.cleanup revert {BATCH}")
    else:
        print(f"\nDry-run:")
        print(f"  would apply {len(accept_rows)} case_name update(s)")
        print(f"  would add ~{len(keep_rows)} state.json kept_db entries")
        print(f"  run with --apply to commit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
