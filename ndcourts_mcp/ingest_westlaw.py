"""Ingest Westlaw .doc downloads and compare/correct against database records.

Parses Westlaw opinion format to extract metadata (citation, case name, date,
author, judges) and opinion text, then matches against existing database records
and reports differences.

Usage:
    python -m ndcourts_mcp.ingest_westlaw process input-data/vol8/ --volume 8 --apply
    python -m ndcourts_mcp.ingest_westlaw status
    python -m ndcourts_mcp.ingest_westlaw export 11 12
"""

import argparse
import re
import shutil
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


# Words that stay lowercase in case names (unless first word)
_LOWERCASE_WORDS = {
    "v", "ex", "rel", "of", "the", "in", "on", "and", "for", "a", "an",
    "at", "by", "to", "et", "al", "ux", "vir",
}

# Words/abbreviations that have specific capitalization in case names
_CASE_NAME_ABBREVS = {
    "co": "Co.", "cos": "Cos.", "corp": "Corp.", "inc": "Inc.",
    "ltd": "Ltd.", "llc": "LLC", "llp": "LLP",
    "ry": "Ry.", "rr": "R.R.",
    "ins": "Ins.", "mfg": "Mfg.", "mfrs": "Mfrs.",
    "nat": "Nat.", "natl": "Nat'l",
    "assn": "Ass'n", "assoc": "Assoc.",
    "dept": "Dep't", "dist": "Dist.",
    "cty": "Cty.", "twp": "Twp.",
    "commrs": "Comm'rs", "commn": "Comm'n",
    "hosp": "Hosp.", "univ": "Univ.",
    "elec": "Elec.", "tel": "Tel.",
    "bd": "Bd.",
    "st": "St.", "ss": "S.S.",
    "pac": "Pac.", "sw": "S.W.",
    "nw": "N.W.", "ne": "N.E.", "se": "S.E.",
    "no": "No.", "nos": "Nos.",
}


def _titlecase_case_name(name: str) -> str:
    """Convert a Westlaw ALL CAPS case name to our title case standard.

    Handles: party names, 'v.', abbreviations, 'ex rel.', 'et al.',
    and preserves particles like 'Mc', 'Mac', 'De', 'Van'.
    """
    # Strip trailing periods and footnote markers
    name = name.strip().rstrip(".")
    name = re.sub(r"[.a]?\d+$", "", name).strip()

    parts = name.split()
    result = []

    for i, word in enumerate(parts):
        low = word.lower().rstrip(".,;:")
        trailing = word[len(low):]  # preserve trailing punctuation

        # "v." stays as-is
        if low == "v" or word == "v.":
            result.append("v.")
            continue

        # Check abbreviation table
        if low in _CASE_NAME_ABBREVS:
            result.append(_CASE_NAME_ABBREVS[low] + trailing.lstrip("."))
            continue

        # Lowercase particles (not at start of a party name)
        if low in _LOWERCASE_WORDS and i > 0 and (not result or result[-1] != "v."):
            result.append(low + trailing)
            continue

        # Title-case the word
        titled = word.capitalize()

        # Handle Mc/Mac prefixes: McCANNA → McCanna
        mc = re.match(r"(Mc|Mac)([a-z])", titled, re.IGNORECASE)
        if mc:
            titled = mc.group(1) + mc.group(2).upper() + titled[len(mc.group(0)):]

        # Handle O' prefix: O'TOOLE → O'Toole (straight or curly apostrophe)
        opre = re.match(r"(O['\u2019])(\w)(.*)", titled, re.IGNORECASE)
        if opre:
            titled = "O'" + opre.group(2).upper() + opre.group(3).lower()

        # Strip stray trailing period from footnote-marker cleanup
        if titled.endswith(".") and not any(titled.endswith(a) for a in
                ("Co.", "Corp.", "Inc.", "Ltd.", "Ry.", "Ins.", "Mfg.", "Nat.",
                 "Assoc.", "Dist.", "Cty.", "Twp.", "Hosp.", "Univ.", "Elec.",
                 "Tel.", "Bd.", "St.", "Pac.", "No.", "Nos.", "Jr.", "Sr.",
                 "v.", "R.R.", "S.W.", "N.W.", "N.E.", "S.E.", "S.S.",
                 "Ass'n", "Dep't", "Comm'rs", "Comm'n", "Nat'l",
                 "Mfrs.", "Cos.",)):
            titled = titled.rstrip(".")

        result.append(titled)

    return " ".join(result)


def _compare_fields(westlaw: dict, db: dict) -> list[tuple[str, str, str]]:
    """Compare Westlaw and DB fields. Returns list of (field, westlaw_val, db_val) diffs."""
    diffs = []

    if westlaw.get("case_name") and db.get("case_name"):
        wl_title = _titlecase_case_name(westlaw["case_name"])
        if not _case_names_match(wl_title, db["case_name"]):
            diffs.append(("case_name", wl_title, db["case_name"]))

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
    batch_dir: Path, db_path: Path, apply: bool = False, batch_name: str = "westlaw-batch",
    case_name_mode: str = "ask", volume: int | None = None,
):
    doc_files = sorted(batch_dir.glob("*.doc"))
    if not doc_files:
        print(f"No .doc files found in {batch_dir}")
        return

    if volume is not None:
        print(f"{BOLD}Processing N.D. Reports vol {volume}{RESET}")

    conn = get_connection(db_path)

    stats = {"matched": 0, "not_found": 0, "diffs": 0, "corrections": 0, "errors": 0}
    not_found_log: list[str] = []

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
            cite = parsed.get("primary_citation", "?")
            name = parsed.get("case_name", "?")
            not_found_log.append(f"{cite}\t{name}\t{doc_path.name}")
            continue

        stats["matched"] += 1
        opinion_id = db_opinion["id"]

        # Record Westlaw as a source for this opinion
        if apply:
            archive_path = _archive_single_doc(doc_path, parsed, volume)
            existing = conn.execute(
                "SELECT id FROM opinion_sources WHERE opinion_id = ? AND source_reporter = 'westlaw'",
                (opinion_id,),
            ).fetchone()
            if not existing:
                conn.execute(
                    """INSERT INTO opinion_sources
                       (opinion_id, source_reporter, source_path, text_length, is_primary, added_at)
                       VALUES (?, 'westlaw', ?, ?, 0, strftime('%Y-%m-%dT%H:%M:%S', 'now'))""",
                    (opinion_id, str(archive_path), len(parsed.get("text", ""))),
                )

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
                    if field == "case_name":
                        if case_name_mode == "skip":
                            print(f"    {DIM}→ Skipped (--case-names=skip){RESET}")
                            continue
                        elif case_name_mode == "westlaw":
                            new_val = wl_val
                        elif case_name_mode == "db":
                            print(f"    {DIM}→ Keeping DB value{RESET}")
                            continue
                        else:
                            # Interactive prompt
                            print(f"    {BOLD}Pick case name:{RESET}")
                            print(f"      [1] {CYAN}{wl_val}{RESET}")
                            print(f"      [2] {YELLOW}{db_val}{RESET}")
                            print(f"      [s] skip")
                            choice = input(f"    Choice [1/2/s]: ").strip().lower()
                            if choice == "1":
                                new_val = wl_val
                            elif choice == "2":
                                print(f"    {DIM}→ Keeping DB value{RESET}")
                                continue
                            else:
                                print(f"    {DIM}→ Skipped{RESET}")
                                continue
                    else:
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

    total_files = len(doc_files)
    print(f"\n{BOLD}Summary:{RESET}")
    print(f"  Files: {total_files}")
    print(f"  Matched: {stats['matched']}")
    print(f"  Not found: {stats['not_found']}")
    print(f"  With differences: {stats['diffs']}")
    if apply:
        print(f"  Corrections applied: {stats['corrections']}")
    print(f"  Errors: {stats['errors']}")

    # Log unmatched opinions for investigation
    if not_found_log:
        log_path = batch_dir / "unmatched.txt"
        with open(log_path, "w") as f:
            for entry in not_found_log:
                f.write(f"{entry}\n")
        print(f"  Unmatched log: {log_path}")

    # Record progress and archive files if volume specified
    if volume is not None and apply:
        progress_conn = get_connection(db_path)
        progress_conn.execute(
            """INSERT INTO westlaw_progress
               (volume, opinions_total, opinions_matched, opinions_not_found,
                corrections_applied, source_path)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (volume, total_files, stats["matched"], stats["not_found"],
             stats["corrections"], str(batch_dir)),
        )
        progress_conn.commit()
        progress_conn.close()
        print(f"  Recorded progress for vol {volume}")

        # Archive .doc files to ~/refs/nd/opin/N.D./{volume}/
        _archive_westlaw_docs(batch_dir, volume)

    return stats


REFS_BASE = Path.home() / "refs" / "nd" / "opin"


def _archive_single_doc(doc_path: Path, parsed: dict, volume: int | None) -> Path:
    """Archive a single .doc file to ~/refs/nd/opin/{reporter}/{vol}/{page}-{Name}.doc.

    Determines the reporter directory (N.D., NW2d, NW) and volume/page from
    the opinion's citations. Volume downloads are handled by the batch
    archiver (_archive_westlaw_docs) instead.
    """
    if volume is not None:
        # Volume-based: batch archiver handles these
        return doc_path

    all_cites = parsed.get("all_citations", [])
    if parsed.get("primary_citation"):
        all_cites = [parsed["primary_citation"]] + all_cites

    # Find a citation we can parse into volume/page for filing
    dest_dir = None
    page = None
    for cite in all_cites:
        m = re.match(r"(\d+)\s+N\.D\.\s+(\d+)", cite)
        if m:
            vol_num, page = int(m.group(1)), int(m.group(2))
            dest_dir = REFS_BASE / "N.D." / str(vol_num)
            break
        m = re.match(r"(\d+)\s+N\.W\.2d\s+(\d+)", cite)
        if m:
            vol_num, page = int(m.group(1)), int(m.group(2))
            dest_dir = REFS_BASE / "NW2d" / str(vol_num)
            break
        m = re.match(r"(\d+)\s+N\.W\.\s+(\d+)", cite)
        if m:
            vol_num, page = int(m.group(1)), int(m.group(2))
            dest_dir = REFS_BASE / "NW" / str(vol_num)
            break

    if dest_dir is None or page is None:
        # Can't determine volume/page — keep in batch dir
        return doc_path

    dest_dir.mkdir(parents=True, exist_ok=True)

    # Build case name slug from Westlaw filename
    name_m = re.match(r"\d+\s*-\s*(.+)\.doc$", doc_path.name)
    case_slug = name_m.group(1).strip().replace(" ", "-") if name_m else doc_path.stem.replace(" ", "-")

    dest_path = dest_dir / f"{page:04d}-{case_slug}.doc"
    if not dest_path.exists():
        shutil.copy2(doc_path, dest_path)

    return dest_path


def _archive_westlaw_docs(batch_dir: Path, volume: int) -> None:
    """Copy .doc files to ~/refs/nd/opin/N.D./{volume}/ with standardized names.

    Renames from Westlaw format "NNN - Case Name.doc" to "{page:04d}-{Case-Name}.doc"
    using the N.D. page number extracted from the opinion text.
    """
    dest = REFS_BASE / "N.D." / str(volume)
    dest.mkdir(parents=True, exist_ok=True)

    doc_files = sorted(batch_dir.glob("*.doc"))
    archived = 0
    for f in doc_files:
        # Extract page number from opinion text
        try:
            text = _doc_to_text(f)
        except Exception:
            shutil.copy2(f, dest / f.name)
            archived += 1
            continue

        m = re.search(rf'{volume}\s+N\.D\.\s+(\d+)', text)
        if m:
            page = int(m.group(1))
        else:
            # Fallback: keep original name
            shutil.copy2(f, dest / f.name)
            archived += 1
            continue

        # Build case name from filename
        name_m = re.match(r'\d+\s*-\s*(.+)\.doc$', f.name)
        case_name = name_m.group(1).strip().replace(' ', '-') if name_m else f.stem.replace(' ', '-')

        new_name = f"{page:04d}-{case_name}.doc"
        dest_path = dest / new_name
        if not dest_path.exists():
            shutil.copy2(f, dest_path)
        archived += 1

    print(f"  Archived {archived} files to {dest}")


def show_status(db_path: Path = DEFAULT_DB_PATH) -> None:
    """Show Westlaw download progress and suggest next volume."""
    conn = get_connection(db_path)
    rows = conn.execute(
        "SELECT * FROM westlaw_progress ORDER BY volume"
    ).fetchall()
    conn.close()

    if not rows:
        print("No Westlaw volumes processed yet.")
        return

    print(f"{BOLD}Westlaw N.D. Reports Progress{RESET}\n")
    print(f"  {'Vol':>4}  {'Total':>5}  {'Match':>5}  {'NotFnd':>6}  {'Fixed':>5}  {'Date':>10}  Notes")
    print(f"  {'─'*4}  {'─'*5}  {'─'*5}  {'─'*6}  {'─'*5}  {'─'*10}  {'─'*20}")
    for r in rows:
        notes = (r["notes"] or "")[:30]
        print(
            f"  {r['volume']:>4}  {r['opinions_total'] or '?':>5}  "
            f"{r['opinions_matched'] or '?':>5}  {r['opinions_not_found'] or '?':>6}  "
            f"{r['corrections_applied'] or 0:>5}  {r['processed_at'][:10]:>10}  {notes}"
        )

    last_vol = max(r["volume"] for r in rows)
    print(f"\n  {CYAN}Next volume to process: {last_vol + 1}{RESET}")


def export_citations(
    db_path: Path, volume_from: int, volume_to: int, reporter: str = "N.D.",
) -> None:
    """Export N.D. citations for a volume range (for Westlaw Quick Check lookup)."""
    conn = get_connection(db_path)
    # Map reporter text to citation pattern
    if reporter == "N.D.":
        pattern = "% N.D. %"
        reporter_code = "NDold"
    else:
        print(f"Unsupported reporter: {reporter}")
        return

    rows = conn.execute("""
        SELECT c.citation FROM citations c
        WHERE c.reporter = ?
          AND CAST(SUBSTR(c.citation, 1, INSTR(c.citation, ' ') - 1) AS INTEGER) BETWEEN ? AND ?
        ORDER BY CAST(SUBSTR(c.citation, 1, INSTR(c.citation, ' ') - 1) AS INTEGER),
                 CAST(SUBSTR(c.citation, INSTR(c.citation, '. ') + 2) AS INTEGER)
    """, (reporter_code, volume_from, volume_to)).fetchall()
    conn.close()

    print(f"# {len(rows)} citations from {volume_from}–{volume_to} {reporter}")
    for r in rows:
        print(r["citation"])


def main():
    parser = argparse.ArgumentParser(description="Ingest Westlaw .doc files")
    sub = parser.add_subparsers(dest="command")

    # Default: process batch
    proc = sub.add_parser("process", help="Process a batch of .doc files")
    proc.add_argument("batch_dir", type=Path, help="Directory of .doc files")
    proc.add_argument("--apply", action="store_true", help="Apply corrections to database")
    proc.add_argument("--batch", default="westlaw-batch", help="Changelog batch name")
    proc.add_argument("--volume", type=int, default=None, help="N.D. Reports volume number")
    proc.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    proc.add_argument(
        "--case-names", choices=["ask", "skip", "westlaw", "db"],
        default="ask", help="How to handle case name diffs (default: ask interactively)",
    )

    # Status
    status = sub.add_parser("status", help="Show Westlaw download progress")
    status.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)

    # Export citations
    export = sub.add_parser("export", help="Export citations for Westlaw Quick Check")
    export.add_argument("volume_from", type=int, help="Start volume")
    export.add_argument("volume_to", type=int, help="End volume")
    export.add_argument("--reporter", default="N.D.", help="Reporter (default: N.D.)")
    export.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)

    args = parser.parse_args()

    if args.command == "status":
        show_status(args.db)
    elif args.command == "export":
        export_citations(args.db, args.volume_from, args.volume_to, args.reporter)
    elif args.command == "process" or args.command is None:
        # Backward compat: if no subcommand, treat positional as batch_dir
        if args.command is None:
            # Re-parse with old-style args
            parser2 = argparse.ArgumentParser()
            parser2.add_argument("batch_dir", type=Path)
            parser2.add_argument("--apply", action="store_true")
            parser2.add_argument("--batch", default="westlaw-batch")
            parser2.add_argument("--volume", type=int, default=None)
            parser2.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
            parser2.add_argument("--case-names", choices=["ask", "skip", "westlaw", "db"], default="ask")
            args = parser2.parse_args()
        process_batch(
            args.batch_dir, args.db, apply=args.apply, batch_name=args.batch,
            case_name_mode=args.case_names, volume=args.volume,
        )


if __name__ == "__main__":
    main()
