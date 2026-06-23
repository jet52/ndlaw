"""Westlaw footnote extraction + editorial filter (ingest_westlaw).

Guards the fix for the silent footnote-loss bug: `_parse_westlaw_doc` cut the
opinion at the "All Citations" footer, dropping the trailing Footnotes section.
The fix re-attaches substantive *numbered* court footnotes while filtering West
editorial apparatus (memorandum-decision notes, bare parallel cites, rehearing
status, lettered daggers).
"""
from ndcourts_mcp import ingest_westlaw as iw


def _doc_lines(body_paras, footnotes):
    """Build a minimal Westlaw-export line list: body, All Citations footer,
    then a Footnotes section. `footnotes` is a list of (label, body)."""
    lines = ["604 N.W.2d 453", "Supreme Court of North Dakota.", "Opinion",
             "NEUMANN, Justice.", ""]
    lines += body_paras
    lines += ["", "All Citations", "604 N.W.2d 453, 2000 ND 12", "Footnotes", ""]
    for label, body in footnotes:
        lines += [label, "", body, ""]
    lines += ["End of Document", "© 2026 Thomson Reuters."]
    return lines


def _all_cites_idx(lines):
    return max(i for i, l in enumerate(lines) if l.strip() == "All Citations")


def test_substantive_numbered_footnote_retained():
    lines = _doc_lines(["[¶ 1] Body text.1"],
                       [("1", "This principle is a variation of the general rule.")])
    out = iw._extract_footnotes(lines, _all_cites_idx(lines))
    assert "This principle is a variation" in out
    assert out.startswith("\n\n1\n\n")


def test_reported_in_full_editorial_dropped():
    lines = _doc_lines(["[¶ 1] Body."],
                       [("1", "Reported in full in the New York Supplement; "
                              "reported as a memorandum decision.")])
    assert iw._extract_footnotes(lines, _all_cites_idx(lines)) == ""


def test_bare_parallel_cite_dropped():
    lines = _doc_lines(["[¶ 1] Body."], [("1", "51 N. W. 379.")])
    assert iw._extract_footnotes(lines, _all_cites_idx(lines)) == ""


def test_rehearing_status_dropped():
    lines = _doc_lines(["[¶ 1] Body."], [("1", "Rehearing pending.")])
    assert iw._extract_footnotes(lines, _all_cites_idx(lines)) == ""


def test_lettered_footnote_dropped():
    # a1/A1 labels are West editorial (rehearing daggers etc.), never retained.
    lines = _doc_lines(["[¶ 1] Body."],
                       [("a1", "Rehearing denied October 17, 1904.")])
    assert iw._extract_footnotes(lines, _all_cites_idx(lines)) == ""


def test_mixed_keeps_only_substantive():
    lines = _doc_lines(
        ["[¶ 1] Body.1 More.2"],
        [("1", "Reported in full in the Pacific Reporter."),
         ("2", "The trial court found the agreement ambiguous and we agree.")])
    out = iw._extract_footnotes(lines, _all_cites_idx(lines))
    assert "Reported in full" not in out
    assert "trial court found the agreement ambiguous" in out
    assert out.count("\n\n2\n\n") == 1


def test_is_editorial_footnote_classifier():
    assert iw._is_editorial_footnote("Reported in full in the N. Y. Supplement.")
    assert iw._is_editorial_footnote("13 Am. Rep. 492.")
    assert iw._is_editorial_footnote("Received for publication December 12, 1919.")
    assert iw._is_editorial_footnote("Opinion withdrawn, see 53 S. D. 652.")
    assert not iw._is_editorial_footnote(
        "Note.-Appellant states that the petition was filed May 28, 1906.")
