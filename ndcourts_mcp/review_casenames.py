"""Review case-name diffs deferred from Westlaw ingest.

Every `ingest_westlaw process` run used `--case-names skip`, leaving
several hundred deferred diffs across vols 1-79. This tool re-extracts
those diffs from the archived .doc files, suppresses the case-only
"diffs" (DB title-case vs. Westlaw all-caps with decorative period),
and surfaces the genuinely substantive ones in a single-keystroke TUI.

Usage:
    python -m ndcourts_mcp.review_casenames --volumes 1-10
    python -m ndcourts_mcp.review_casenames --volumes 5 --summary
"""

import argparse
import json
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

from .db import DEFAULT_DB_PATH, get_connection
from .ingest_westlaw import _doc_to_text, _find_db_opinion, _parse_westlaw_doc

REFS_BASE = Path.home() / "refs/nd/opin"
STATE_FILE = Path("triage/casenames-state.json")

# Patterns to strip from Westlaw case names for normalization
_DOCKET_SUFFIX = re.compile(
    r"\s*(?:Crim\.\s+)?(?:Civ\.\s+)?No\.\s*\d+[A-Za-z]?\.?\s*\|?\s*$",
    re.IGNORECASE,
)
_TRAIL_FOOTNOTE = re.compile(r"\.\d+\s*$")  # "RANSOM COUNTY.1"
_TRAIL_PIPE = re.compile(r"\s*\|\s*$")
_TRAIL_PERIOD = re.compile(r"\s*\.\s*$")
_ET_AL = re.compile(r",?\s+et\s+al\.?", re.IGNORECASE)
_TRAIL_ROLE = re.compile(
    r",\s*(?:District\s+Judge|State\s+Auditor|Attorney\s+General"
    r"|Secretary\s+of\s+State|Governor|Mayor|County\s+Auditor"
    r"|Sheriff|Treasurer|Tax\s+Commissioner|State's\s+Attorney"
    r"|Judge|Trustee)s?\.?\s*$",
    re.IGNORECASE,
)


def normalize_westlaw_name(name: str) -> str:
    """Normalize a Westlaw case name for equivalence comparison."""
    s = name.strip()
    # Iteratively strip trailing decorations
    for _ in range(5):
        prev = s
        s = _DOCKET_SUFFIX.sub("", s)
        s = _TRAIL_FOOTNOTE.sub("", s)
        s = _TRAIL_PIPE.sub("", s)
        s = _TRAIL_ROLE.sub("", s)
        s = _TRAIL_PERIOD.sub("", s)
        if s == prev:
            break
    s = _ET_AL.sub("", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _equivalent(db_name: str, wl_norm: str) -> bool:
    """True if DB and normalized Westlaw differ only in case/spacing."""
    a = re.sub(r"\s+", " ", (db_name or "").strip()).lower()
    b = re.sub(r"\s+", " ", (wl_norm or "").strip()).lower()
    return bool(a) and a == b


def _smart_titlecase(s: str) -> str:
    """Title-case a name while keeping legal connectives lowercase."""
    lowercase_tokens = {"v.", "v", "ex", "rel.", "rel", "and", "of", "the",
                        "in", "re", "et", "al.", "for", "to"}
    out = []
    for word in s.split(" "):
        if word.lower() in lowercase_tokens and out:  # never lowercase the first word
            out.append(word.lower())
        elif word.isupper() and len(word) > 1:
            # Preserve common all-caps abbreviations like "U.S." but title-case names
            if re.fullmatch(r"[A-Z]\.(?:[A-Z]\.)+", word):
                out.append(word)
            else:
                out.append(word.title().replace("'S", "'s"))
        else:
            out.append(word)
    return " ".join(out)


def _load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"schema_version": 1, "kept_db": {}}


def _save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")


def parse_volumes(spec: str) -> list[int]:
    """Parse '5' or '1-10' or '5,7,9-12' into a sorted list of ints."""
    out = set()
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            lo, hi = part.split("-", 1)
            out.update(range(int(lo), int(hi) + 1))
        else:
            out.add(int(part))
    return sorted(out)


def extract_diffs(conn: sqlite3.Connection, volume: int, kept_db: set[int]) -> list[dict]:
    """Re-derive case-name diffs for one N.D. volume from archived .docs."""
    vol_dir = REFS_BASE / "N.D." / str(volume)
    if not vol_dir.is_dir():
        return []

    diffs = []
    for f in sorted(vol_dir.glob("*.doc")):
        try:
            parsed = _parse_westlaw_doc(_doc_to_text(f))
        except Exception:
            continue
        if not parsed:
            continue
        cites = list(parsed.get("all_citations") or [])
        if parsed.get("primary_citation"):
            cites.insert(0, parsed["primary_citation"])
        op = _find_db_opinion(conn, cites)
        if not op:
            continue
        if op["id"] in kept_db:
            continue
        db_name = (op["case_name"] or "").strip()
        wl_raw = (parsed.get("case_name") or "").strip()
        if not db_name or not wl_raw or db_name == wl_raw:
            continue
        wl_norm = normalize_westlaw_name(wl_raw)
        wl_titled = _smart_titlecase(wl_norm)
        equivalent = _equivalent(db_name, wl_norm)
        diffs.append({
            "volume": volume,
            "opinion_id": op["id"],
            "primary_citation": parsed.get("primary_citation"),
            "doc_path": str(f),
            "db_name": db_name,
            "wl_raw": wl_raw,
            "wl_norm": wl_norm,
            "wl_titled": wl_titled,
            "equivalent": equivalent,
        })
    return diffs


def _print_diff(d: dict, idx: int, total: int) -> None:
    print()
    print(f"=== Vol {d['volume']}  ({idx + 1}/{total})  ===")
    print(f"{d['primary_citation'] or '?':<14}  opinion_id {d['opinion_id']}")
    print(f"  doc: {d['doc_path']}")
    print()
    print(f"  DB:           {d['db_name']}")
    print(f"  Westlaw raw:  {d['wl_raw']}")
    if d["wl_titled"] != d["wl_raw"]:
        print(f"  Westlaw norm: {d['wl_titled']}")
    print()


def _prompt() -> str:
    print(
        "  [k] keep DB     [w] use Westlaw raw     [t] use Westlaw title-cased\n"
        "  [e] edit        [s] skip (decide later)     [q] save & quit"
    )
    while True:
        try:
            choice = input("> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return "q"
        if choice in {"k", "w", "t", "e", "s", "q"}:
            return choice
        print("  ?")


def _apply_decision(
    conn: sqlite3.Connection, d: dict, new_value: str, batch: str
) -> None:
    conn.execute(
        "UPDATE opinions SET case_name = ? WHERE id = ?",
        (new_value, d["opinion_id"]),
    )
    conn.execute(
        "INSERT INTO changelog (batch, opinion_id, field, old_value, new_value) "
        "VALUES (?, ?, 'case_name', ?, ?)",
        (batch, d["opinion_id"], d["db_name"], new_value),
    )
    conn.commit()


def review_volume(
    conn: sqlite3.Connection, volume: int, diffs: list[dict], state: dict
) -> str:
    """Run the TUI for one volume's ambiguous diffs. Returns 'continue' or 'quit'."""
    batch = f"westlaw-nd-vol{volume}-casenames"
    total = len(diffs)
    print(f"\n--- Reviewing vol {volume}: {total} ambiguous diff(s) ---")
    for idx, d in enumerate(diffs):
        _print_diff(d, idx, total)
        choice = _prompt()
        if choice == "q":
            _save_state(state)
            print(f"  Saved state. Resume with `--volumes {volume}` (or higher).")
            return "quit"
        if choice == "s":
            continue
        if choice == "k":
            state.setdefault("kept_db", {})[str(d["opinion_id"])] = {
                "volume": volume,
                "db_name": d["db_name"],
                "wl_raw": d["wl_raw"],
                "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
            _save_state(state)
            print(f"  ✓ kept DB ({d['db_name']!r})")
            continue
        if choice == "w":
            new_value = d["wl_raw"]
        elif choice == "t":
            new_value = d["wl_titled"]
        elif choice == "e":
            try:
                new_value = input("  edit > ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n  cancelled")
                continue
            if not new_value:
                print("  empty input, skipping")
                continue
        else:
            continue
        _apply_decision(conn, d, new_value, batch)
        print(f"  ✓ updated → {new_value!r}")
    print(f"--- Vol {volume} complete ---")
    return "continue"


def run(volumes: list[int], db_path: Path, summary_only: bool) -> None:
    conn = get_connection(db_path)
    state = _load_state()
    kept_db = {int(k) for k in state.get("kept_db", {}).keys()}

    per_volume = {}
    for vol in volumes:
        diffs = extract_diffs(conn, vol, kept_db)
        per_volume[vol] = diffs

    print("\nVolume summary:")
    print(f"  {'vol':>4}  {'raw':>5}  {'equiv':>6}  {'review':>7}")
    total_review = 0
    for vol in volumes:
        diffs = per_volume[vol]
        eq = sum(1 for d in diffs if d["equivalent"])
        ambig = len(diffs) - eq
        total_review += ambig
        print(f"  {vol:>4}  {len(diffs):>5}  {eq:>6}  {ambig:>7}")
    print(f"  Total ambiguous to review: {total_review}")

    if summary_only or total_review == 0:
        return

    try:
        ans = input(f"\nStart review of {total_review} ambiguous diff(s)? [Y/n] ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return
    if ans not in {"", "y", "yes"}:
        return

    for vol in volumes:
        ambig_diffs = [d for d in per_volume[vol] if not d["equivalent"]]
        if not ambig_diffs:
            continue
        outcome = review_volume(conn, vol, ambig_diffs, state)
        if outcome == "quit":
            break


def main() -> None:
    parser = argparse.ArgumentParser(description="Review deferred Westlaw case-name diffs")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--volumes", required=True,
                        help="Volume(s) to review: '5', '1-10', '5,7,9-12'")
    parser.add_argument("--summary", action="store_true",
                        help="Print per-volume diff counts and exit")
    args = parser.parse_args()
    volumes = parse_volumes(args.volumes)
    run(volumes, args.db, args.summary)


if __name__ == "__main__":
    main()
