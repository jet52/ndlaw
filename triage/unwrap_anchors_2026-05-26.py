"""Unwrap the two genuine <a href> anchors to plain text (closes the last has_html).

20116 Axvig and 20290 Hirsch Trust each embed one real anchor of the form
<a href="URL">URL</a> (inner text == href) around a URL the Court cited
(Merriam-Webster's "specification" entry; the ND Courts Legal Self-Help Center).
Replace each anchor span with its inner text, leaving the bare URL — no substance
lost, markup removed.

Run with --apply to write; default dry-run. Logged to changelog for revert.
"""
from __future__ import annotations
import argparse, re, sqlite3

BATCH = "unwrap-anchors-2026-05-26"
OIDS = [20116, 20290]
ANCHOR = re.compile(r'<a\b[^>]*>(.*?)</a>', re.I | re.S)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    conn = sqlite3.connect("opinions.db")
    for oid in OIDS:
        old = conn.execute("SELECT text_content FROM opinions WHERE id=?", (oid,)).fetchone()[0]
        n = len(ANCHOR.findall(old))
        new = ANCHOR.sub(lambda m: m.group(1), old)
        # no anchor markup must remain
        assert n == 1, f"{oid}: expected 1 anchor, found {n}"
        assert not re.search(r'</?a\b[^>]*>', new, re.I), f"{oid}: residual anchor tag"
        assert len(old) - len(new) == sum(len(m.group(0)) - len(m.group(1))
                                          for m in ANCHOR.finditer(old))
        print(f"{oid}: unwrapped {n} anchor(s), len {len(old)} -> {len(new)}")
        if args.apply:
            conn.execute("INSERT INTO changelog (batch, opinion_id, field, old_value, new_value) "
                         "VALUES (?,?, 'text_content', ?, ?)",
                         (BATCH, oid, "<a href>…</a> anchor markup", "unwrapped to bare URL"))
            conn.execute("UPDATE opinions SET text_content=? WHERE id=?", (new, oid))
    if args.apply:
        conn.commit(); print("APPLIED")
    else:
        print("DRY RUN")
    conn.close()


if __name__ == "__main__":
    main()
