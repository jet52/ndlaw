"""Interactive author review tool.

Presents opinions with suspect author values for quick manual validation.
Shows case metadata, judges field, and opinion text excerpt with auto-detected
author suggestion. Corrections are logged through the changelog table.

Usage:
    python -m ndcourts_mcp.review                    Review unrecognized authors
    python -m ndcourts_mcp.review --author "Chas"    Review specific author value
    python -m ndcourts_mcp.review --flagged           Review flagged items
    python -m ndcourts_mcp.review --min-count 3       Only authors with 3+ opinions
"""

import argparse
import json
import re
import sys
from pathlib import Path

from .db import DEFAULT_DB_PATH, get_connection
from .justices import JUSTICE_BY_LAST_NAME, KNOWN_LAST_NAMES

# ANSI colors — avoiding red/green for colorblind accessibility
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
WHITE = "\033[37m"
RESET = "\033[0m"


def _detect_author_from_text(text: str, date_year: int | None = None) -> str | None:
    """Try to find the opinion author from text patterns.

    Looks for patterns like:
      - "Spalding, J."  /  "VandeWalle, Chief Justice."
      - "Justice Tufte writing"
      - "SANDSTROM, J." (all caps variant)
    in the first ~3000 characters.
    """
    head = text[:3000]

    # Pattern: "LastName, J." or "LastName, C.J." or "LastName, Chief Justice."
    # Usually appears on its own line near the top
    for line in head.splitlines():
        line = line.strip()
        m = re.match(
            r"^([A-Z][A-Za-z']+(?:\s[A-Z][A-Za-z']+)?),\s+"
            r"(?:C\.?\s*J\.?|Chief Justice|J\.?|Justice)\.?\s*$",
            line,
        )
        if m:
            name = m.group(1)
            if name.lower() in KNOWN_LAST_NAMES:
                return name.title() if name.isupper() else name

    # Pattern: "Justice LastName" or "Chief Justice LastName"
    m = re.search(
        r"(?:Chief\s+)?Justice\s+([A-Z][A-Za-z']+)",
        head,
    )
    if m:
        name = m.group(1)
        if name.lower() in KNOWN_LAST_NAMES:
            return name.title() if name.isupper() else name

    # Pattern: "Per Curiam" / "PER CURIAM"
    if re.search(r"[Pp][Ee][Rr]\s+[Cc][Uu][Rr][Ii][Aa][Mm]", head[:1000]):
        return "_per_curiam"

    return None


def _get_court_justices(year: int) -> list[str]:
    """Return justices who served in a given year."""
    result = []
    for last_name, entries in JUSTICE_BY_LAST_NAME.items():
        for full_name, start, end in entries:
            end_y = end or 2100
            if start <= year <= end_y:
                result.append(last_name)
    return sorted(set(result))


def _format_opinion(row, suggestion: str | None, court_justices: list[str]) -> str:
    """Format an opinion for display."""
    lines = []
    lines.append(f"{BOLD}{'═' * 78}{RESET}")
    lines.append(
        f"{BOLD}{CYAN}{row['case_name']}{RESET}"
    )
    if row["case_name_full"]:
        lines.append(f"{DIM}{row['case_name_full']}{RESET}")
    lines.append("")

    lines.append(f"  {BOLD}Date:{RESET}    {row['date_filed']}")
    lines.append(f"  {BOLD}Author:{RESET}  {YELLOW}{row['author']}{RESET}")
    lines.append(f"  {BOLD}Judges:{RESET}  {row['judges'] or '(none)'}")
    if row["docket_number"]:
        lines.append(f"  {BOLD}Docket:{RESET}  {row['docket_number']}")
    lines.append(f"  {BOLD}Source:{RESET}  {row['source_reporter']} — {row['source_path']}")

    year = int(row["date_filed"][:4]) if row["date_filed"] else None
    if court_justices:
        lines.append(f"  {BOLD}Court:{RESET}   {', '.join(court_justices)}")

    lines.append("")

    # Show first ~25 lines of opinion text, skipping YAML frontmatter
    text_lines = row["text_head"].splitlines()
    in_frontmatter = False
    display_lines = []
    for tl in text_lines:
        if tl.strip() == "---" and not in_frontmatter:
            in_frontmatter = True
            continue
        if in_frontmatter:
            if tl.strip() == "---":
                in_frontmatter = False
            continue
        display_lines.append(tl)
        if len(display_lines) >= 25:
            break

    lines.append(f"  {DIM}── Opinion text ──{RESET}")
    for dl in display_lines:
        lines.append(f"  {DIM}│{RESET} {dl}")

    lines.append("")

    if suggestion == "_per_curiam":
        lines.append(
            f"  {MAGENTA}Suggestion:{RESET} {BOLD}Per Curiam{RESET} "
            f"(set author→NULL, per_curiam→1)"
        )
    elif suggestion:
        lines.append(f"  {MAGENTA}Suggestion:{RESET} {BOLD}{suggestion}{RESET}")
    else:
        lines.append(f"  {MAGENTA}Suggestion:{RESET} {DIM}(none){RESET}")

    return "\n".join(lines)


def _prompt_action(suggestion: str | None) -> tuple[str, str | None]:
    """Prompt for action. Returns (action, value).

    Actions: 'accept', 'type', 'null', 'skip', 'flag', 'quit'
    """
    parts = []
    if suggestion:
        parts.append(f"{BOLD}y{RESET}=accept")
    parts.append(f"{BOLD}t{RESET}=type")
    parts.append(f"{BOLD}0{RESET}=set NULL")
    parts.append(f"{BOLD}n{RESET}=skip")
    parts.append(f"{BOLD}f{RESET}=flag")
    parts.append(f"{BOLD}q{RESET}=quit")

    prompt = f"  [{' | '.join(parts)}] "

    while True:
        try:
            ch = input(prompt).strip().lower()
        except (EOFError, KeyboardInterrupt):
            return "quit", None

        if ch == "q":
            return "quit", None
        elif ch == "n" or ch == "":
            return "skip", None
        elif ch == "f":
            return "flag", None
        elif ch == "y" and suggestion:
            return "accept", suggestion
        elif ch == "0":
            return "null", None
        elif ch == "t":
            try:
                val = input(f"  {BOLD}New author:{RESET} ").strip()
            except (EOFError, KeyboardInterrupt):
                return "quit", None
            if val:
                return "type", val
            continue
        elif ch == "y" and not suggestion:
            print(f"  {DIM}No suggestion to accept — type 't' to enter a name{RESET}")


def review(
    db_path: Path,
    author_filter: str | None = None,
    flagged_only: bool = False,
    min_count: int = 1,
    batch_name: str = "manual-review",
):
    conn = get_connection(db_path)

    # Ensure flag table exists
    conn.execute("""
        CREATE TABLE IF NOT EXISTS review_flags (
            opinion_id INTEGER PRIMARY KEY REFERENCES opinions(id),
            flagged_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now')),
            note TEXT
        )
    """)
    conn.commit()

    # Build query
    if flagged_only:
        query = """
            SELECT o.*, substr(o.text_content, 1, 3000) as text_head
            FROM opinions o
            JOIN review_flags rf ON rf.opinion_id = o.id
            ORDER BY o.date_filed
        """
        params: list = []
    elif author_filter:
        query = """
            SELECT o.*, substr(o.text_content, 1, 3000) as text_head
            FROM opinions o WHERE o.author = ?
            ORDER BY o.date_filed
        """
        params = [author_filter]
    else:
        # Get unrecognized authors with min_count threshold
        authors = conn.execute(
            """SELECT author, COUNT(*) as n FROM opinions
               WHERE author IS NOT NULL
               GROUP BY author HAVING n >= ?
               ORDER BY n DESC""",
            (min_count,),
        ).fetchall()

        unrecognized = [
            r["author"]
            for r in authors
            if r["author"].lower() not in KNOWN_LAST_NAMES
        ]

        if not unrecognized:
            print("No unrecognized authors found.")
            return

        # Process one author value at a time (all opinions with that value)
        placeholders = ",".join("?" * len(unrecognized))
        query = f"""
            SELECT o.*, substr(o.text_content, 1, 3000) as text_head
            FROM opinions o WHERE o.author IN ({placeholders})
            ORDER BY o.author, o.date_filed
        """
        params = unrecognized

    rows = conn.execute(query, params).fetchall()

    if not rows:
        print("No opinions to review.")
        return

    total = len(rows)
    reviewed = 0
    corrected = 0
    flagged = 0
    skipped = 0

    current_author = None

    for i, row in enumerate(rows):
        # Show header when author value changes
        if row["author"] != current_author:
            current_author = row["author"]
            author_count = sum(1 for r in rows if r["author"] == current_author)
            print(f"\n{BOLD}{BLUE}── Author: \"{current_author}\" "
                  f"({author_count} opinions) ──{RESET}")

        year = int(row["date_filed"][:4]) if row["date_filed"] else None
        court_justices = _get_court_justices(year) if year else []
        suggestion = _detect_author_from_text(row["text_head"], year)

        print()
        print(f"  {DIM}[{i + 1}/{total}]{RESET}")
        print(_format_opinion(row, suggestion, court_justices))

        action, value = _prompt_action(suggestion)

        if action == "quit":
            break
        elif action == "skip":
            skipped += 1
            continue
        elif action == "flag":
            conn.execute(
                "INSERT OR REPLACE INTO review_flags (opinion_id) VALUES (?)",
                (row["id"],),
            )
            conn.commit()
            flagged += 1
            continue
        elif action == "accept":
            if value == "_per_curiam":
                conn.execute(
                    "INSERT INTO changelog (batch, opinion_id, field, old_value, new_value) "
                    "VALUES (?, ?, 'author', ?, NULL)",
                    (batch_name, row["id"], row["author"]),
                )
                conn.execute(
                    "INSERT INTO changelog (batch, opinion_id, field, old_value, new_value) "
                    "VALUES (?, ?, 'per_curiam', ?, '1')",
                    (batch_name, row["id"], str(row["per_curiam"])),
                )
                conn.execute(
                    "UPDATE opinions SET author = NULL, per_curiam = 1 WHERE id = ?",
                    (row["id"],),
                )
            else:
                conn.execute(
                    "INSERT INTO changelog (batch, opinion_id, field, old_value, new_value) "
                    "VALUES (?, ?, 'author', ?, ?)",
                    (batch_name, row["id"], row["author"], value),
                )
                conn.execute(
                    "UPDATE opinions SET author = ? WHERE id = ?",
                    (value, row["id"]),
                )
            conn.commit()
            corrected += 1
        elif action == "type":
            if value.lower() == "null" or value == "":
                conn.execute(
                    "INSERT INTO changelog (batch, opinion_id, field, old_value, new_value) "
                    "VALUES (?, ?, 'author', ?, NULL)",
                    (batch_name, row["id"], row["author"]),
                )
                conn.execute(
                    "UPDATE opinions SET author = NULL WHERE id = ?",
                    (row["id"],),
                )
            else:
                conn.execute(
                    "INSERT INTO changelog (batch, opinion_id, field, old_value, new_value) "
                    "VALUES (?, ?, 'author', ?, ?)",
                    (batch_name, row["id"], row["author"], value),
                )
                conn.execute(
                    "UPDATE opinions SET author = ? WHERE id = ?",
                    (value, row["id"]),
                )
            conn.commit()
            corrected += 1
        elif action == "null":
            conn.execute(
                "INSERT INTO changelog (batch, opinion_id, field, old_value, new_value) "
                "VALUES (?, ?, 'author', ?, NULL)",
                (batch_name, row["id"], row["author"]),
            )
            conn.execute(
                "UPDATE opinions SET author = NULL WHERE id = ?",
                (row["id"],),
            )
            conn.commit()
            corrected += 1

        reviewed += 1

    print(f"\n{BOLD}Done.{RESET} Reviewed {reviewed}, "
          f"corrected {corrected}, flagged {flagged}, skipped {skipped}.")


def main():
    parser = argparse.ArgumentParser(
        description="Interactive author review tool"
    )
    parser.add_argument(
        "--author", help="Review opinions with this specific author value"
    )
    parser.add_argument(
        "--flagged", action="store_true", help="Review flagged items"
    )
    parser.add_argument(
        "--min-count",
        type=int,
        default=1,
        help="Only review author values with at least N opinions (default 1)",
    )
    parser.add_argument(
        "--batch",
        default="manual-review",
        help="Batch name for changelog (default: manual-review)",
    )
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    args = parser.parse_args()

    review(
        args.db,
        author_filter=args.author,
        flagged_only=args.flagged,
        min_count=args.min_count,
        batch_name=args.batch,
    )


if __name__ == "__main__":
    main()
