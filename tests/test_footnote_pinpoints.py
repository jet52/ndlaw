"""Footnote-aware pinpoint resolution (proofread.py).

Regression guard for the bug where a quotation living in a footnote body was
attributed to the body's preceding ``[¶]`` marker (usually the last/signature
paragraph) instead of the paragraph carrying the footnote call. See
``~/2025-cases/20250367/ndcourts-mcp-BUG-footnote-pinpoints.md``.

The structural fixtures are synthetic so the test does not depend on the DB; a
DB-backed check against Lyon, 2000 ND 12 runs only when opinions.db is present.
"""
import os
import sqlite3

import pytest

from ndcourts_mcp import proofread

# A minimal opinion mirroring the West/CL-OCR footnote layout: a call marker in
# ¶ 2, body text through ¶ 4, then the footnote body (period form) parked before
# the signature ¶ 5 — exactly the shape that mis-mapped to ¶ 4 before the fix.
SYNTH = (
    "[¶ 1] Opening paragraph.\n\n"
    "[¶ 2] A party who voluntarily pays a judgment waives the right to appeal.\n\n"
    " 1\n\n"
    "See Some Case, 1 N.W.2d 1 (N.D. 1900).\n\n"
    "[¶ 3] More analysis here at *123 page break.\n\n"
    "[¶ 4] Final reasoning paragraph.\n\n"
    " 1\n\n"
    ". This footnote explains the acceptance-of-benefits rule in detail.\n\n"
    "[¶ 5] THE JUSTICES concur.\n"
)


def test_footnote_quote_maps_to_call_paragraph():
    loc = proofread.locate_quote(SYNTH, "the acceptance-of-benefits rule in detail")
    assert loc["found"] is True
    assert loc["in_footnote"] is True
    assert loc["footnote"] == 1
    assert loc["paragraph"] == 2  # call site, NOT ¶4 (the preceding marker)


def test_footnote_quote_never_maps_to_signature_paragraph():
    loc = proofread.locate_quote(SYNTH, "acceptance-of-benefits rule in detail")
    assert loc["paragraph"] != 5
    assert proofread.pinpoint_suffix(loc) == "¶ 2 n.1"


def test_body_text_not_flagged_as_footnote():
    loc = proofread.locate_quote(SYNTH, "A party who voluntarily pays a judgment")
    assert loc["in_footnote"] is False
    assert loc["footnote"] is None
    assert loc["paragraph"] == 2


def test_star_page_pinpoint():
    # "Final reasoning" sits after the *123 marker -> reporter page 123.
    loc = proofread.locate_quote(SYNTH, "Final reasoning paragraph")
    assert loc["reporter_page"] == 123
    cite_rows = [{"citation": "604 N.W.2d 453", "reporter": "NW2d"}]
    assert proofread.reporter_pinpoint(cite_rows, loc["reporter_page"]) == "604 N.W.2d at 123"


def test_ocr_artifact_flagged_not_verbatim_failure():
    # Stored text carries an OCR substitution (ti -> cl); the quote is correct.
    text = ("[¶ 1] Even though the acceptance-of-benefits rule of waiver is "
            "conceptually related to the voluntary-payment-or-satisfaclion-of-"
            "judgment rule of waiver, we have sharply limited it.\n")
    loc = proofread.locate_quote(
        text,
        "the voluntary-payment-or-satisfaction-of-judgment rule of waiver, "
        "we have sharply limited")
    assert loc["found"] is False
    assert loc.get("likely_ocr_artifact") is True


# ndcourts-markdown NOTES form: inline [N] call + trailing "NOTES\n[N] body".
SYNTH_NOTES = (
    "[¶ 1] Opening paragraph.\n\n"
    "[¶ 2] The defendant was advised of his rights[1] before questioning.\n\n"
    "[¶ 3] He later waived them.\n\n"
    "[¶ 4] THE JUSTICES concur.\n\n"
    "NOTES\n"
    "[1] See Miranda v. Arizona, 384 U.S. 436 (1966).\n\n"
    "[2] An uncalled note.\n"
)

# ndcourts-markdown FOOTNOTES form: "FOOTNOTES\n\nN:\n\nbody" (call doesn't survive).
SYNTH_FOOTNOTES = (
    "[¶ 1] Opening paragraph.\n\n"
    "[¶ 2] We affirm the judgment.\n\n"
    "[¶ 3] THE JUSTICES concur.\n\n"
    "FOOTNOTES\n\n"
    "1:\n\n"
    "Canon 2 of the Code of Judicial Conduct provides in part as follows.\n"
)


def test_notes_format_links_to_call_paragraph():
    loc = proofread.locate_quote(SYNTH_NOTES, "See Miranda v. Arizona")
    assert loc["in_footnote"] is True
    assert loc["footnote"] == 1
    assert loc["paragraph"] == 2  # the [1] call sits in ¶ 2, not ¶ 4
    assert proofread.pinpoint_suffix(loc) == "¶ 2 n.1"


def test_notes_format_body_not_misattributed():
    # A quote from ¶ 2 body (not the footnote) stays a plain paragraph hit.
    loc = proofread.locate_quote(SYNTH_NOTES, "advised of his rights")
    assert loc["in_footnote"] is False
    assert loc["paragraph"] == 2


def test_footnotes_format_retains_text_no_false_paragraph():
    loc = proofread.locate_quote(SYNTH_FOOTNOTES, "Canon 2 of the Code of Judicial Conduct")
    assert loc["found"] and loc["verbatim"]
    assert loc["in_footnote"] is True
    assert loc["footnote"] == 1
    assert loc["paragraph"] is None  # call marker lost in this lineage
    assert proofread.pinpoint_suffix(loc) == "n.1"


# Modern (1997+) inline-[N] call in the standalone lineage: no NOTES/FOOTNOTES
# header, an inline [1] call in the prose, and the body parked period-form at the
# end of the opinion (modern-footnote-recover convention). The standalone parser
# resolves call_para from the unique inline [N].
SYNTH_INLINE_STANDALONE = (
    "[¶ 1] Opening paragraph.\n\n"
    "[¶ 2] The operative statute,[1] which governs the motion, applies here.\n\n"
    "[¶ 3] THE JUSTICES concur.\n\n"
    " 1\n\n"
    ". The statute was amended in 2023 to codify the new procedure.\n"
)

# Same, but a second bracketed [1] (a quote alteration) makes the inline call
# ambiguous -> the guard declines to resolve a paragraph (suffix stays n.1).
SYNTH_INLINE_AMBIG = (
    "[¶ 1] Opening paragraph.\n\n"
    "[¶ 2] The operative statute,[1] which governs the motion, applies here.\n\n"
    "[¶ 3] The court quoted “[1] the first subdivision” of the statute.\n\n"
    "[¶ 4] THE JUSTICES concur.\n\n"
    " 1\n\n"
    ". The statute was amended in 2023 to codify the new procedure.\n"
)


def test_inline_call_standalone_links_to_call_paragraph():
    loc = proofread.locate_quote(SYNTH_INLINE_STANDALONE, "amended in 2023 to codify")
    assert loc["in_footnote"] is True
    assert loc["footnote"] == 1
    assert loc["paragraph"] == 2  # resolved from inline [1], not the body marker
    assert proofread.pinpoint_suffix(loc) == "¶ 2 n.1"


def test_inline_call_ambiguous_bracket_not_resolved():
    # Two [1] occurrences -> the call paragraph is not inferred (no false hit on
    # the bracketed quote alteration); the footnote is still recognized.
    loc = proofread.locate_quote(SYNTH_INLINE_AMBIG, "amended in 2023 to codify")
    assert loc["in_footnote"] is True
    assert loc["footnote"] == 1
    assert loc["paragraph"] is None
    assert proofread.pinpoint_suffix(loc) == "n.1"


def test_pinpoint_suffix_forms():
    assert proofread.pinpoint_suffix({"paragraph": 7, "footnote": 1}) == "¶ 7 n.1"
    assert proofread.pinpoint_suffix({"paragraph": None, "footnote": 1}) == "n.1"
    assert proofread.pinpoint_suffix({"paragraph": 18, "footnote": None}) == "¶ 18"
    assert proofread.pinpoint_suffix({"paragraph": None, "footnote": None}) is None


_DB = os.path.expanduser("~/code/ndcourts-mcp/opinions.db")


def _text_for_cite(cite):
    conn = sqlite3.connect(_DB)
    try:
        row = conn.execute(
            "SELECT o.text_content FROM opinions o JOIN citations c "
            "ON c.opinion_id=o.id WHERE c.citation=?", (cite,)
        ).fetchone()
    finally:
        conn.close()
    return row[0] if row else None


@pytest.mark.skipif(not os.path.exists(_DB), reason="opinions.db not present")
def test_lyon_acceptance_of_benefits_resolves_to_para7_n1():
    conn = sqlite3.connect(_DB)
    try:
        row = conn.execute(
            "SELECT text_content FROM opinions WHERE id=13068"
        ).fetchone()
    finally:
        conn.close()
    assert row is not None
    loc = proofread.locate_quote(
        row[0], "we have sharply limited the acceptance-of-benefits rule"
    )
    assert loc["in_footnote"] is True
    assert loc["footnote"] == 1
    assert loc["paragraph"] == 7  # bug produced 18


# Footnote-bearing opinions across eras. 1997+ carry [¶] markers so footnote
# quotes resolve to ¶ N n.X; pre-1953 (no markers) is a retention check — the
# footnote text must be present and verbatim, with no false ¶.
_ERA_FOOTNOTES = [
    # cite,          quote,                                          fn,  para
    ("1998 ND 9", "NDCC 28-32-12.1, enacted by N.D. Laws 1991", 1, 5),     # multi-fn
    ("1998 ND 9", "The requirement of a written specification of issues", 3, 15),
    ("2010 ND 5", "The Legislature amended N.D.C.C. ch. 14-09", 1, 4),
    ("2016 ND 150", "Kuhn made no argument regarding the ordinances", 1, 7),
    ("2016 ND 249", "The regulations now plainly state", 1, 4),
    ("1999 ND 134", "See Miranda v. Arizona", 1, 2),    # NOTES[N] format, real opinion
    # inline-[N] standalone recovery (batch modern-footnote-recover-2026-06-23)
    ("2024 ND 99", "was amended effective Aug. 1, 2023, to codify summary disposition", 1, 6),
    ("2022 ND 136", "was amended effective August 1, 2021, to provide that", 1, 6),
    ("2024 ND 147", "It appears the district court applied the amended version", 1, 32),
]


@pytest.mark.skipif(not os.path.exists(_DB), reason="opinions.db not present")
@pytest.mark.parametrize("cite,quote,fn,para", _ERA_FOOTNOTES)
def test_footnote_pinpoint_across_eras(cite, quote, fn, para):
    text = _text_for_cite(cite)
    assert text is not None, f"{cite} not in DB"
    loc = proofread.locate_quote(text, quote)
    assert loc["found"] and loc["verbatim"], f"{cite}: {loc}"
    assert loc["in_footnote"] is True
    assert loc["footnote"] == fn
    assert loc["paragraph"] == para


@pytest.mark.skipif(not os.path.exists(_DB), reason="opinions.db not present")
@pytest.mark.parametrize("cite,quote", [
    ("43 N.D. 156", "the original not being here, shows the date May 28, 1905"),
    ("69 N.D. 290", "the measure was passed by a vote of 95 to 1"),
])
def test_pre1953_footnote_text_retained(cite, quote):
    # Restored Westlaw footnotes (batch westlaw-footnote-restore-2026-06-22).
    # No [¶] markers pre-1953, so the value is retention: text present, verbatim,
    # and no false paragraph attribution.
    text = _text_for_cite(cite)
    assert text is not None, f"{cite} not in DB"
    loc = proofread.locate_quote(text, quote)
    assert loc["found"] and loc["verbatim"]
    assert loc["paragraph"] is None
