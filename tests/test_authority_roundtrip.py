"""Resolution guards for ND primary-law citation queries.

The core invariant: **every citation string the search layer emits must itself
resolve via lookup_authority back to the same provision**, and the common input
*variants* a user (or jetcite) would type must resolve too. That second clause is
where every resolution bug here has lived — the Sup. Ct. Admin. Rules (spaced vs
compact), N.D. Admin. Code (4-segment cites truncated), the constitution
("article" spelled out). These tests are layered:

  * ``TestParser*``                – pure-function pins, run even with no DBs.
  * ``TestEmittedCitationsRoundTrip`` – exhaustive: every stored citation resolves.
  * ``TestVariantResolution``      – mechanical input variants of every stored
                                     citation (despaced, pinpointed) resolve.
  * ``TestSearchToLookupRoundTrip``– the invariant against the *real* emitter.
  * ``Test*InputForms`` / ``TestAsOfDate`` / ``TestNegative`` – curated cases
    through the full MCP tool path (lookup_authority / get_authority_history).

Run: ``.venv/bin/python -m unittest tests.test_authority_roundtrip``
(pytest-discoverable). Corpora that aren't installed are skipped per-test, so the
parser unit tests still give signal in a data-less CI.
"""

from __future__ import annotations

import re
import unittest

from ndcourts_mcp import corpus, research, server

ALL_CORPORA = ("const", "rule", "ndcc", "admin")


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #

def _open_corpus(name):
    path = corpus.resolve_corpus_db_path(name)
    if not path.exists():
        return None
    return corpus.get_corpus_connection(path, must_exist=True, read_only=True)


def _resolve_in(conn, citation, as_of_date=None):
    """Resolve a citation against a directly-opened corpus DB via the same
    helpers the MCP tools use (normalize_authority -> _best_cite ->
    lookup_provision_version). Returns the landed citation or None."""
    spec = research.normalize_authority(citation)
    if spec["kind"] is None:
        return None
    lookup_cite = server._best_cite(conn, "main", spec, citation)
    row = corpus.lookup_provision_version(conn, "main", lookup_cite, as_of_date)
    return row["citation"] if row else None


def _tool(name):
    fn = getattr(server, name)
    return getattr(fn, "fn", fn)  # unwrap FastMCP tool if wrapped


def _sample(conn, stride):
    """Deterministic representative sample of a corpus's citations."""
    rows = conn.execute("SELECT citation FROM provisions ORDER BY id").fetchall()
    return [r["citation"] for i, r in enumerate(rows) if i % stride == 0]


# --------------------------------------------------------------------------- #
# pure-function pins (no DB)
# --------------------------------------------------------------------------- #

class TestParserClassification(unittest.TestCase):
    """normalize_authority must route each shape to the right corpus kind."""

    CASES = [
        ("N.D. Sup. Ct. Admin. R. 22", "court_rule"),
        ("N.D.Sup.Ct.Admin.R. 22", "court_rule"),
        ("Admin. R. 22", "court_rule"),
        ("Administrative Rule 22", "court_rule"),
        ("AR 22", "court_rule"),
        ("N.D.R.Civ.P. 56", "court_rule"),
        ("Rule 56 NDRCivP", "court_rule"),
        ("N.D.R.Ct. 8.3.1", "court_rule"),
        ("N.D. Const. art. I, § 8", "constitution"),
        ("N.D. Const. article I, § 8", "constitution"),
        ("N.D.C.C. § 12.1-20-03", "statute"),
        ("12.1-20-03", "statute"),
        ("N.D.A.C. § 10-01-01-01", "admin"),
        ("N.D. Admin. Code § 10-01-01-01", "admin"),
        ("10-01-01-01", "admin"),          # 4-segment bare → admin, not ndcc
        ("nonsense words here", None),
        ("", None),
    ]

    def test_kinds(self):
        for cite, want in self.CASES:
            got = research.normalize_authority(cite)["kind"]
            self.assertEqual(got, want, f"{cite!r} -> kind {got!r}, want {want!r}")

    def test_canonical_exact_forms(self):
        # The parser's canonical reconstruction, used to rescue alias/word-order
        # variants the raw form can't match.
        for cite, want in [
            ("AR 22", "N.D. Sup. Ct. Admin. R. 22"),
            ("Administrative Rule 22", "N.D. Sup. Ct. Admin. R. 22"),
            ("Rule 56 NDRCivP", "N.D.R.Civ.P. 56"),
            ("N.D. Admin. Code § 10-01-01-01", "N.D.A.C. § 10-01-01-01"),
            ("10-01-01-01", "N.D.A.C. § 10-01-01-01"),
        ]:
            self.assertEqual(research.normalize_authority(cite)["exact"], want, cite)


class TestCiteKeyInvariants(unittest.TestCase):
    """cite_key must be insensitive to abbreviation spacing and to the
    spelled-out 'article', since those are how the same cite varies by source."""

    def test_space_insensitive_after_collapse(self):
        a = corpus.cite_key("N.D.R.Civ.P. 56").replace(" ", "")
        b = corpus.cite_key("N.D. R. Civ. P. 56").replace(" ", "")
        self.assertEqual(a, b)

    def test_article_normalizes_to_art(self):
        self.assertEqual(
            corpus.cite_key("N.D. Const. article I, § 1"),
            corpus.cite_key("N.D. Const. art. I, § 1"),
        )

    def test_decimal_dots_preserved(self):
        # Numbering dots carry meaning and must survive.
        self.assertIn("12.1-20-03", corpus.cite_key("N.D.C.C. § 12.1-20-03"))


# --------------------------------------------------------------------------- #
# corpus-level resolution (fast: one connection, no opinions.db)
# --------------------------------------------------------------------------- #

class TestEmittedCitationsRoundTrip(unittest.TestCase):
    """Exhaustive: every stored citation in every installed corpus resolves to
    itself. The floor guard — catches any regression that breaks the canonical
    (search-emitted) form anywhere in the corpus."""

    def _check(self, name):
        conn = _open_corpus(name)
        if conn is None:
            self.skipTest(f"corpus {name!r} not installed")
        try:
            cites = [r["citation"] for r in conn.execute("SELECT citation FROM provisions")]
            self.assertGreater(len(cites), 0)
            fails = [(c, _resolve_in(conn, c)) for c in cites]
            fails = [(c, g) for c, g in fails if g != c]
            self.assertEqual(fails, [], f"{len(fails)}/{len(cites)} {name} failed; e.g. {fails[:5]}")
        finally:
            conn.close()

    def test_const(self): self._check("const")
    def test_rule(self): self._check("rule")
    def test_ndcc(self): self._check("ndcc")
    def test_admin(self): self._check("admin")


class TestVariantResolution(unittest.TestCase):
    """Mechanical input variants of stored citations resolve to the same
    provision. Generalizes the hand-picked form tests across the whole corpus,
    so future abbreviation/spacing drift anywhere is caught — and auto-covers
    any rule set added later. All of the small corpora; a stride sample of the
    large ones (kept fast by running at the corpus layer)."""

    STRIDE = {"const": 1, "rule": 1, "ndcc": 53, "admin": 47}

    @staticmethod
    def _variants(name, citation):
        # Despacing is a universal invariant (exercises the space-insensitive
        # key path). A "§ 3(c)" pinpoint is only meaningful for court rules —
        # for const/N.D.C.C./admin the "§ N" is the section identifier itself,
        # so appending another would denote a different (deeper) cite.
        yield "despaced", re.sub(r"\s+", "", citation)
        if name == "rule" and citation.rstrip().endswith(tuple("0123456789")):
            yield "pinpoint", citation + ", § 3(c)"

    def _check(self, name):
        conn = _open_corpus(name)
        if conn is None:
            self.skipTest(f"corpus {name!r} not installed")
        try:
            fails = []
            for canon in _sample(conn, self.STRIDE[name]):
                for label, variant in self._variants(name, canon):
                    got = _resolve_in(conn, variant)
                    if got != canon:
                        fails.append((label, variant, canon, got))
            self.assertEqual(fails, [], f"{len(fails)} {name} variant(s) failed; e.g. {fails[:5]}")
        finally:
            conn.close()

    def test_const(self): self._check("const")
    def test_rule(self): self._check("rule")
    def test_ndcc(self): self._check("ndcc")
    def test_admin(self): self._check("admin")


# --------------------------------------------------------------------------- #
# full MCP tool path (opens opinions.db + attaches corpora)
# --------------------------------------------------------------------------- #

class TestSearchToLookupRoundTrip(unittest.TestCase):
    """THE stated invariant, against the real emitter: every citation
    search_authority returns must resolve via lookup_authority to that same
    citation. (The exhaustive test proves it for the DB universe; this proves
    search actually emits resolvable strings.)"""

    QUERIES = ["court", "state", "person", "notice", "time", "evidence", "rule"]

    def test_emitted_results_resolve(self):
        if not any(corpus.resolve_corpus_db_path(c).exists() for c in ALL_CORPORA):
            self.skipTest("no corpora installed")
        search = _tool("search_authority")
        lookup = _tool("lookup_authority")
        checked = 0
        for q in self.QUERIES:
            res = search(query=q, limit=15)
            for hit in res.get("results", []):
                emitted = hit["citation"]
                r = lookup(citation=emitted)
                self.assertTrue(r.get("found"),
                                f"search emitted {emitted!r} but lookup failed: {r.get('error')}")
                self.assertEqual(r["citation"], emitted,
                                 f"search emitted {emitted!r}; lookup landed on {r.get('citation')!r}")
                checked += 1
        self.assertGreater(checked, 0, "search returned no results to round-trip")


class TestAsOfDate(unittest.TestCase):
    """The point-in-time (as_of_date) branch resolves, and returns different
    versions for different dates — including from a variant input form."""

    def _pick_multiversion(self, name):
        conn = _open_corpus(name)
        if conn is None:
            return None
        try:
            row = conn.execute(
                """SELECT p.citation, MIN(v.effective_start) lo, MAX(v.effective_start) hi,
                          COUNT(v.id) n
                   FROM provisions p JOIN provision_versions v ON v.provision_id = p.id
                   WHERE v.effective_start IS NOT NULL
                   GROUP BY p.id HAVING n > 1 ORDER BY n DESC LIMIT 1""").fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def test_dated_lookup_returns_distinct_versions(self):
        pick = next((self._pick_multiversion(c) for c in ("rule", "const")
                     if self._pick_multiversion(c)), None)
        if not pick:
            self.skipTest("no multi-version provision available")
        lookup = _tool("lookup_authority")
        early = lookup(citation=pick["citation"], as_of_date=pick["lo"])
        late = lookup(citation=pick["citation"], as_of_date=pick["hi"])
        self.assertTrue(early.get("found") and late.get("found"))
        self.assertEqual(early["citation"], pick["citation"])
        self.assertNotEqual(early["effective_start"], late["effective_start"],
                            "as_of_date returned the same version for min and max dates")
        # And the dated path must also work from a variant (despaced) input.
        despaced = re.sub(r"\s+", "", pick["citation"])
        v = lookup(citation=despaced, as_of_date=pick["hi"])
        self.assertTrue(v.get("found"), f"dated lookup of variant {despaced!r} failed")
        self.assertEqual(v["effective_start"], late["effective_start"])


class TestNegativeInputs(unittest.TestCase):
    """Bad input fails cleanly: no exception, no false match."""

    def test_unparseable_returns_error(self):
        r = _tool("lookup_authority")(citation="the quick brown fox")
        self.assertIn("error", r)
        self.assertFalse(r.get("found"))

    def test_parseable_but_nonexistent_not_found(self):
        for bogus in ("N.D.C.C. § 99-99-99", "N.D. Sup. Ct. Admin. R. 9999",
                      "N.D.A.C. § 99-99-99-99"):
            if not corpus.resolve_corpus_db_path(
                    {"N": "ndcc"}.get("x", server.KIND_TO_CORPUS.get(
                        research.normalize_authority(bogus)["kind"], "ndcc"))).exists():
                continue
            r = _tool("lookup_authority")(citation=bogus)
            self.assertFalse(r.get("found"), f"{bogus!r} unexpectedly matched {r.get('citation')!r}")
            self.assertNotIn("Traceback", str(r))

    def test_history_unparseable_returns_error(self):
        r = _tool("get_authority_history")(citation="not a citation at all")
        self.assertIn("error", r)


# --------------------------------------------------------------------------- #
# curated full-path cases (the originally reported bug + its twins)
# --------------------------------------------------------------------------- #

class TestCourtRuleInputForms(unittest.TestCase):
    """The reported bug's input matrix, end-to-end through the MCP tool."""

    CANON = "N.D. Sup. Ct. Admin. R. 22"
    FORMS = ["N.D. Sup. Ct. Admin. R. 22", "N.D.Sup.Ct.Admin.R. 22", "Admin. R. 22",
             "Administrative Rule 22", "AR 22", "A.R. 22"]

    @classmethod
    def setUpClass(cls):
        if not corpus.resolve_corpus_db_path("rule").exists():
            raise unittest.SkipTest("rule corpus not installed")

    def test_all_forms_same_full_text(self):
        texts = set()
        for form in self.FORMS:
            r = _tool("lookup_authority")(citation=form)
            self.assertTrue(r.get("found"), f"{form!r}: {r.get('error')}")
            self.assertEqual(r["citation"], self.CANON)
            self.assertGreater(len(r["text"]), 280)  # full text, not search excerpt
            texts.add(r["text"])
        self.assertEqual(len(texts), 1)

    def test_pinpoint_returns_full_rule_with_note(self):
        r = _tool("lookup_authority")(citation="N.D. Sup. Ct. Admin. R. 22, § 3(c)")
        self.assertTrue(r.get("found"))
        self.assertEqual(r["citation"], self.CANON)
        self.assertIn("note", r)
        self.assertIn("Subsection", r["note"])

    def test_history_from_variant_forms(self):
        for form in ("N.D.Sup.Ct.Admin.R. 22", "AR 22"):
            h = _tool("get_authority_history")(citation=form)
            self.assertTrue(h.get("found"), f"{form!r}: {h.get('error')}")
            self.assertEqual(h["citation"], self.CANON)

    def test_other_rule_sets(self):
        for form, want in [("N.D.R.Civ.P. 56", "N.D.R.Civ.P. 56"),
                           ("Rule 56 NDRCivP", "N.D.R.Civ.P. 56"),
                           ("N.D.R.App.P. 2.1", "N.D.R.App.P. 2.1"),
                           ("N.D.R.Ct. 8.3.1", "N.D.R.Ct. 8.3.1")]:
            r = _tool("lookup_authority")(citation=form)
            self.assertTrue(r.get("found"), f"{form!r}: {r.get('error')}")
            self.assertEqual(r["citation"], want)


class TestCrossCorpusInputForms(unittest.TestCase):
    """Statute / admin / constitution variant forms (rules-bug twins)."""

    def _assert(self, citation, want_corpus, want_cite=None):
        if not corpus.resolve_corpus_db_path(want_corpus).exists():
            self.skipTest(f"corpus {want_corpus!r} not installed")
        r = _tool("lookup_authority")(citation=citation)
        self.assertTrue(r.get("found"), f"{citation!r}: {r.get('error')}")
        self.assertEqual(r["corpus"], want_corpus)
        if want_cite:
            self.assertEqual(r["citation"], want_cite)

    def test_admin_four_segment(self):
        conn = _open_corpus("admin")
        if conn is None:
            self.skipTest("admin corpus not installed")
        try:
            canon = conn.execute("SELECT citation FROM provisions LIMIT 1").fetchone()["citation"]
        finally:
            conn.close()
        sec = re.search(r"(\d[\d.\-]*\d)", canon).group(1)
        for form in (canon, f"N.D. Admin. Code § {sec}", f"NDAC {sec}", sec):
            self._assert(form, "admin", canon)

    def test_constitution_article(self):
        for form in ("N.D. Const. art. I, § 1", "N.D. Const. article I, § 1",
                     "N.D. Const. Article I, Section 1"):
            self._assert(form, "const", "N.D. Const. art. I, § 1")

    def test_statute_forms(self):
        for form in ("N.D.C.C. § 1-01-01", "1-01-01", "NDCC 1-01-01", "section 1-01-01"):
            self._assert(form, "ndcc", "N.D.C.C. § 1-01-01")


if __name__ == "__main__":
    unittest.main(verbosity=2)
