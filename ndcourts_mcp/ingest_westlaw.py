"""Ingest Westlaw .doc downloads and compare/correct against database records.

Parses Westlaw opinion format to extract metadata (citation, case name, date,
author, judges) and opinion text, then matches against existing database records
and reports differences.

Usage:
    python -m ndcourts_mcp.ingest_westlaw input-data/batch1/  [--apply] [--db PATH]
"""

import argparse
import re
import subprocess
from datetime import datetime
from pathlib import Path

from .db import DEFAULT_DB_PATH, get_connection

MONTH_MAP = {
    "jan": 1, "feb": 2, "march": 3, "mar": 3, "april": 4, "apr": 4,
    "may": 5, "june": 6, "jun": 6, "july": 7, "jul": 7, "aug": 8,
    "sept": 9, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

# ANSI
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
MAGENTA = "\033[35m"
RESET = "\033[0m"


def _doc_to_text(path: Path) -> str:
    """Convert .doc to plain text using macOS textutil."""
    result = subprocess.run(
        ["textutil", "-convert", "txt", "-stdout", str(path)],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"textutil failed on {path}: {result.stderr}")
    return result.stdout


def _parse_date(text: str) -> str | None:
    """Parse Westlaw date like 'Oct. 20, 1917' or 'Dec. 17, 1892'."""
    m = re.match(r"(\w+)\.?\s+(\d{1,2}),?\s+(\d{4})", text.strip())
    if not m:
        return None
    month_str, day, year = m.group(1).lower().rstrip("."), int(m.group(2)), int(m.group(3))
    month = MONTH_MAP.get(month_str)
    if not month:
        return None
    return f"{year:04d}-{month:02d}-{day:02d}"


def _parse_westlaw_doc(text: str) -> dict | None:
    """Parse a Westlaw opinion text into structured fields."""
    lines = text.splitlines()
    if len(lines) < 10:
        return None

    result = {}

    # First non-empty line should be the citation
    for i, line in enumerate(lines):
        line = line.strip()
        if line and re.match(r"\d+\s+N\.\w", line):
            result["primary_citation"] = line
            break
    else:
        return None

    # Find "All Citations" at end
    all_cites_idx = None
    for j in range(len(lines) - 1, max(len(lines) - 20, 0), -1):
        if lines[j].strip() == "All Citations":
            all_cites_idx = j
            break

    if all_cites_idx and all_cites_idx + 1 < len(lines):
        cite_line = lines[all_cites_idx + 1].strip()
        result["all_citations"] = [c.strip() for c in cite_line.split(",") if c.strip()]

    # Find case name: lines between "v." markers
    # Pattern: PARTY1 \n v. \n PARTY2
    for i, line in enumerate(lines):
        if line.strip() == "v.":
            # Party 1 is the non-empty line(s) before
            party1_lines = []
            for k in range(i - 1, max(i - 5, 0), -1):
                l = lines[k].strip()
                if l and l != "Supreme Court of North Dakota." and not re.match(r"\d+\s+N\.", l):
                    party1_lines.insert(0, l)
                else:
                    break
            # Party 2 is the non-empty line(s) after
            party2_lines = []
            for k in range(i + 1, min(i + 5, len(lines))):
                l = lines[k].strip()
                if l and not _parse_date(l):
                    party2_lines.append(l)
                else:
                    break
            party1 = " ".join(party1_lines)
            party2 = " ".join(party2_lines)
            if party1 and party2:
                result["case_name"] = f"{party1} v. {party2}"
            break

    # Find date — usually a line after the parties like "Oct. 20, 1917."
    for i, line in enumerate(lines[:30]):
        line = line.strip().rstrip(".")
        d = _parse_date(line)
        if d:
            result["date_filed"] = d
            break

    # Find author — "LASTNAME, J." or "LASTNAME, C. J." in Opinion section
    opinion_start = None
    for i, line in enumerate(lines):
        if line.strip() == "Opinion":
            opinion_start = i
            break

    if opinion_start:
        for i in range(opinion_start, min(opinion_start + 5, len(lines))):
            line = lines[i].strip()
            m = re.match(
                r"^([A-Z][A-Z']+(?:\s[A-Z]+)?),\s*(?:C\.\s*J|J)\.",
                line,
            )
            if m:
                name = m.group(1)
                result["author"] = name.title()
                break

    # Find judges from "All concur" or specific concurrence/dissent lines
    # Also look for Synopsis section for judge info
    for i, line in enumerate(lines):
        if "Judge." in line and "District" in line:
            # "Appeal from District Court, X County; JUDGE NAME, Judge."
            pass  # Could extract trial judge if needed

    # Extract opinion text (from "Opinion" header to "All Citations")
    if opinion_start and all_cites_idx:
        opinion_lines = lines[opinion_start + 1 : all_cites_idx]
        result["opinion_text"] = "\n".join(opinion_lines).strip()

    return result


def _find_db_opinion(conn, citations: list[str]) -> dict | None:
    """Find a database opinion matching any of the given citations."""
    for cite in citations:
        cite = re.sub(r"\s+", " ", cite.strip())
        row = conn.execute(
            """SELECT o.* FROM opinions o
               JOIN citations c ON c.opinion_id = o.id
               WHERE c.citation = ?""",
            (cite,),
        ).fetchone()
        if row:
            return dict(row)
    return None


def _normalize_case_name(name: str) -> str:
    """Normalize a case name for comparison, stripping casing, punctuation,
    abbreviations, and party qualifiers."""
    s = name.lower().strip().rstrip(".")
    # Remove trailing footnote markers like "a1", ".1"
    s = re.sub(r"[.a]?\d+$", "", s)
    # Remove common party qualifiers
    for qual in [" et al", " et ux", " et vir"]:
        s = s.replace(qual, "")
    # Remove content in parens
    s = re.sub(r"\s*\(.*?\)", "", s)
    # Normalize punctuation and whitespace
    s = re.sub(r"[.,;:'\"&]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    # Common abbreviation expansions for comparison
    abbrevs = {
        " co ": " company ",
        " cos ": " companies ",
        " corp ": " corporation ",
        " inc ": " incorporated ",
        " r co ": " railroad company ",
        " ry co ": " railway company ",
        " rr co ": " railroad company ",
        " r r co ": " railroad company ",
        " pac ": " pacific ",
        " n pac ": " northern pacific ",
        " mfg ": " manufacturing ",
        " mut ": " mutual ",
        " ins ": " insurance ",
        " nat ": " national ",
        " st ": " saint ",
        " s w ": " southwestern ",
        " s ": " south ",
        " n ": " north ",
        " e ": " east ",
        " w ": " west ",
        " p ": " paul ",
        " ss m ": " sault sainte marie ",
        " s s m ": " sault sainte marie ",
        " ste ": " sainte ",
        " dist ": " district ",
        " cty ": " county ",
        " assn ": " association ",
        " dept ": " department ",
        " elec ": " electric ",
        " tel ": " telephone ",
        " hosp ": " hospital ",
        " bd ": " board ",
        " commrs ": " commissioners ",
        " twp ": " township ",
    }
    # Pad with spaces for word-boundary matching
    padded = f" {s} "
    for abbr, full in abbrevs.items():
        padded = padded.replace(abbr, full)
    return padded.strip()


def _case_names_match(wl_name: str, db_name: str) -> bool:
    """Check if two case names are substantially the same."""
    wl = _normalize_case_name(wl_name)
    db = _normalize_case_name(db_name)
    if wl == db:
        return True
    # Check if one contains the other (handles truncation)
    if wl in db or db in wl:
        return True
    # Check if the core party names match (first v second)
    wl_parts = wl.split(" v ")
    db_parts = db.split(" v ")
    if len(wl_parts) == 2 and len(db_parts) == 2:
        # Compare first few words of each party
        wl_p1 = wl_parts[0].split()[:2]
        wl_p2 = wl_parts[1].split()[:2]
        db_p1 = db_parts[0].split()[:2]
        db_p2 = db_parts[1].split()[:2]
        if wl_p1 == db_p1 and wl_p2 == db_p2:
            return True
    return False


def _compare_fields(westlaw: dict, db: dict) -> list[tuple[str, str, str]]:
    """Compare Westlaw and DB fields. Returns list of (field, westlaw_val, db_val) diffs."""
    diffs = []

    if westlaw.get("case_name") and db.get("case_name"):
        if not _case_names_match(westlaw["case_name"], db["case_name"]):
            diffs.append(("case_name", westlaw["case_name"], db["case_name"]))

    if westlaw.get("date_filed") and db.get("date_filed"):
        if westlaw["date_filed"] != db["date_filed"]:
            diffs.append(("date_filed", westlaw["date_filed"], db["date_filed"]))

    if westlaw.get("author") and db.get("author"):
        if westlaw["author"].lower() != db["author"].lower():
            diffs.append(("author", westlaw["author"], db["author"]))
    elif westlaw.get("author") and not db.get("author"):
        diffs.append(("author", westlaw["author"], "(NULL)"))

    return diffs


def process_batch(
    batch_dir: Path, db_path: Path, apply: bool = False, batch_name: str = "westlaw-batch"
):
    doc_files = sorted(batch_dir.glob("*.doc"))
    if not doc_files:
        print(f"No .doc files found in {batch_dir}")
        return

    conn = get_connection(db_path)

    stats = {"matched": 0, "not_found": 0, "diffs": 0, "corrections": 0, "errors": 0}

    for doc_path in doc_files:
        print(f"\n{BOLD}{doc_path.name}{RESET}")

        try:
            text = _doc_to_text(doc_path)
        except Exception as e:
            print(f"  {YELLOW}Error reading: {e}{RESET}")
            stats["errors"] += 1
            continue

        parsed = _parse_westlaw_doc(text)
        if not parsed:
            print(f"  {YELLOW}Could not parse Westlaw format{RESET}")
            stats["errors"] += 1
            continue

        citations = parsed.get("all_citations", [])
        if parsed.get("primary_citation"):
            citations.insert(0, parsed["primary_citation"])

        print(f"  {DIM}Citation: {parsed.get('primary_citation', '?')}{RESET}")
        print(f"  {DIM}Case: {parsed.get('case_name', '?')}{RESET}")
        print(f"  {DIM}Date: {parsed.get('date_filed', '?')}{RESET}")
        print(f"  {DIM}Author: {parsed.get('author', '?')}{RESET}")

        db_opinion = _find_db_opinion(conn, citations)
        if not db_opinion:
            print(f"  {YELLOW}NOT FOUND in database{RESET}")
            stats["not_found"] += 1
            continue

        stats["matched"] += 1
        diffs = _compare_fields(parsed, db_opinion)

        if not diffs:
            print(f"  {CYAN}Metadata matches{RESET}")
        else:
            stats["diffs"] += 1
            for field, wl_val, db_val in diffs:
                print(f"  {MAGENTA}{field}:{RESET}")
                print(f"    {CYAN}Westlaw:{RESET} {wl_val}")
                print(f"    {YELLOW}DB:     {RESET} {db_val}")

                if apply:
                    new_val = wl_val if wl_val != "(NULL)" else None
                    conn.execute(
                        "INSERT INTO changelog (batch, opinion_id, field, old_value, new_value) "
                        "VALUES (?, ?, ?, ?, ?)",
                        (batch_name, db_opinion["id"], field, db_val, new_val),
                    )
                    conn.execute(
                        f"UPDATE opinions SET {field} = ? WHERE id = ?",
                        (new_val, db_opinion["id"]),
                    )
                    stats["corrections"] += 1
                    print(f"    {CYAN}→ Corrected{RESET}")

    if apply:
        conn.commit()

    conn.close()

    print(f"\n{BOLD}Summary:{RESET}")
    print(f"  Matched: {stats['matched']}")
    print(f"  Not found: {stats['not_found']}")
    print(f"  With differences: {stats['diffs']}")
    if apply:
        print(f"  Corrections applied: {stats['corrections']}")
    print(f"  Errors: {stats['errors']}")


def main():
    parser = argparse.ArgumentParser(description="Ingest Westlaw .doc files")
    parser.add_argument("batch_dir", type=Path, help="Directory of .doc files")
    parser.add_argument("--apply", action="store_true", help="Apply corrections to database")
    parser.add_argument("--batch", default="westlaw-batch", help="Changelog batch name")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    args = parser.parse_args()

    process_batch(args.batch_dir, args.db, apply=args.apply, batch_name=args.batch)


if __name__ == "__main__":
    main()
