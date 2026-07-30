"""Citation-URL web interface — ndlaw.org/<citation> (PLAN-web-interface.md).

Phase A: opinions. Mounts on the same FastMCP app that serves ``/mcp`` via
``@mcp.custom_route`` (fastmcp registers ``/mcp`` first, so nothing here can
shadow it). Zero new dependencies; read-only connections per request.

URL scheme (canonical = the opinion's primary citation):

    /2020ND30            neutral cite (1997+); /2024NDApp5 for the COA
    /ND/13/359           N.D. Reports primary (pre-1954)
    /NW2d/604/458        N.W.2d primary (1953-1996)
    /NW/{vol}/{page}     N.W. 1st-series primary (4 opinions)
    /{canonical}/citing  paginated citing list (50/page); /cited likewise
    /cite/{free text}    resolver -> 301 to canonical (also /cite?q=)

Loose forms (case, hyphens, spaces, parallel cites, pre-1997 synthetic
neutral cites) 301-redirect to canonical. Shared reporter pages render a
disambiguation page; each candidate links ``?id=<opinion id>``.

Every response carries ``X-Robots-Tag: noindex, nofollow`` (unlisted policy)
and ``Cache-Control``/``ETag`` keyed on the DB build stamp.
"""
from __future__ import annotations

import html
import os
import re
import sqlite3

from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse, Response

from . import corpus, proofread, web_templates
from .db import DEFAULT_DB_PATH, get_connection

PAGE_SIZE = 50

# set by register(); ETag stamp is the DB mtime at process start (the corpus
# only changes via the weekly self-update, which restarts the service).
_DB_PATH = DEFAULT_DB_PATH
_STAMP = "dev"

_NEUTRAL_TOKEN = re.compile(r"^(\d{4})[\s_-]*nd[\s_-]*(app)?[\s_-]*(\d{1,4})$",
                            re.IGNORECASE)
_ND_LOOSE = re.compile(r"^(\d{1,2})\s*n\.?\s*d\.?\s*(\d{1,4})$", re.IGNORECASE)
_NW_LOOSE = re.compile(r"^(\d{1,4})\s*n\.?\s*w\.?\s*(2d|3d)?\.?\s*(\d{1,4})$",
                       re.IGNORECASE)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _conn() -> sqlite3.Connection:
    return get_connection(_DB_PATH, read_only=True)


def _headers(*, max_age: int = 86400, etag_key: str | None = None) -> dict:
    h = {"X-Robots-Tag": "noindex, nofollow",
         "Cache-Control": f"public, max-age={max_age}"}
    if etag_key is not None:
        h["ETag"] = f'"{_STAMP}:{etag_key}"'
    return h


def _maybe_304(request: Request, etag_key: str) -> Response | None:
    inm = request.headers.get("if-none-match")
    if inm and inm.strip() == f'"{_STAMP}:{etag_key}"':
        return Response(status_code=304, headers=_headers(etag_key=etag_key))
    return None


def _html(request: Request, content: str, *, status: int = 200,
          max_age: int = 86400) -> Response:
    key = request.url.path + (f"?{request.url.query}" if request.url.query else "")
    not_mod = _maybe_304(request, key)
    if not_mod:
        return not_mod
    return HTMLResponse(content, status_code=status,
                        headers=_headers(max_age=max_age, etag_key=key))


def _redirect(path: str) -> Response:
    return RedirectResponse(path, status_code=301,
                            headers=_headers(max_age=86400))


def token_to_cite(token: str) -> str | None:
    """Loose URL token -> exact DB citation string, or None."""
    t = token.strip()
    m = _NEUTRAL_TOKEN.match(t)
    if m and 1889 <= int(m.group(1)) <= 2099:
        y, app, n = m.group(1), m.group(2), int(m.group(3))
        return f"{y} ND App {n}" if app else f"{y} ND {n}"
    return None


def free_text_to_cite(q: str) -> str | None:
    """Free text (the /cite resolver) -> exact DB citation string."""
    t = re.sub(r"\s+", " ", q).strip()
    cite = token_to_cite(t)
    if cite:
        return cite
    m = _NW_LOOSE.match(t)
    if m:
        series = {"2d": "N.W.2d", "3d": "N.W.3d", None: "N.W."}[
            m.group(2).lower() if m.group(2) else None]
        return f"{m.group(1)} {series} {m.group(3)}"
    m = _ND_LOOSE.match(t)
    if m:
        return f"{m.group(1)} N.D. {m.group(2)}"
    extracted = proofread.extract_cite(t)
    if extracted:
        return extracted
    return None


def canonical_path(conn, opinion_id: int) -> str:
    """Canonical URL path for an opinion (its primary citation)."""
    row = conn.execute(
        "SELECT citation, reporter FROM citations "
        "WHERE opinion_id = ? AND is_primary = 1", (opinion_id,)).fetchone()
    if row is None:                      # defensive; invariant guarantees one
        return f"/cite/id{opinion_id}"
    c, rep = row["citation"], row["reporter"]
    if rep == "ND-neutral":
        m = re.match(r"^(\d{4}) ND (\d+)$", c)
        return f"/{m.group(1)}ND{m.group(2)}"
    if rep == "ND-App-neutral":
        m = re.match(r"^(\d{4}) ND App (\d+)$", c)
        return f"/{m.group(1)}NDApp{m.group(2)}"
    m = re.match(r"^(\d+) N\.(D|W)\.(?:(2d|3d))? ?(\d+)$", c.replace("  ", " "))
    if m:
        fam = {"D": "ND", "W": "NW"}[m.group(2)] + (m.group(3) or "")
        return f"/{fam}/{m.group(1)}/{m.group(4)}"
    return f"/cite/id{opinion_id}"


def _rows_for_cite(conn, cite: str) -> list[sqlite3.Row]:
    return conn.execute(
        """SELECT o.* FROM opinions o JOIN citations c ON c.opinion_id = o.id
           WHERE c.citation = ? ORDER BY o.id""", (cite,)).fetchall()


# ---------------------------------------------------------------------------
# page assembly
# ---------------------------------------------------------------------------

def _official_url(row) -> str:
    """The document's own official URL (ndcourts.gov opinion page) when it
    has one; the corpus landing page otherwise. Feeds the footer
    disclaimer's 'an official source' link."""
    url = row["opinion_url"] if "opinion_url" in row.keys() else None
    return url or web_templates.OFFICIAL_FALLBACK["opinions"]


_NDCC_SECTION = re.compile(
    r"^(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?[a-z]?)$")


def _ndcc_official_url(section: str) -> str:
    """ndlegis.gov Century Code deep link — the same pattern jetcite emits
    into text_citations.url (t12-1c20.pdf#nameddest=12p1-20-03p1: dots
    become dashes in the title/chapter path, 'p' in the nameddest)."""
    m = _NDCC_SECTION.match(section)
    if not m:
        return web_templates.OFFICIAL_FALLBACK["ndcc"]
    title, chapter, _ = m.groups()
    return (f"https://ndlegis.gov/cencode/t{title.replace('.', '-')}"
            f"c{chapter.replace('.', '-')}.pdf"
            f"#nameddest={section.replace('.', 'p')}")



_ROMAN = re.compile(r"^[IVXLC]+$", re.IGNORECASE)
_RULE_SETS = {"civ": "N.D.R.Civ.P.", "crim": "N.D.R.Crim.P.",
              "app": "N.D.R.App.P.", "ev": "N.D.R.Ev.",
              "ct": "N.D.R.Ct.", "juv": "N.D.R.Juv.P."}


def _prov_link(corpus_name: str, citation: str) -> str:
    """Cross-reference list item: link corpora that have pages."""
    esc = html.escape(citation)
    if corpus_name == "ndcc" and citation.startswith("N.D.C.C. § "):
        return (f'<a href="/ndcc/{html.escape(citation[11:])}">{esc}</a>')
    if corpus_name == "admin" and citation.startswith("N.D.A.C. § "):
        return (f'<a href="/ndac/{html.escape(citation[11:])}">{esc}</a>')
    m = re.match(r"^N\.D\. Const\. art\. ([IVXLC]+), § (.+)$", citation)
    if corpus_name == "const" and m:
        return (f'<a href="/const/{m.group(1)}/{html.escape(m.group(2))}">'
                f"{esc}</a>")
    for slug, prefix in _RULE_SETS.items():
        if corpus_name == "rule" and citation.startswith(prefix + " "):
            num = citation[len(prefix) + 1:]
            return (f'<a href="/rule/{slug}/{html.escape(num)}">{esc}</a>')
    return esc


def _ndac_official_url(section: str) -> str:
    """ndlegis.gov Admin Code chapter PDF (acdata/pdf/75-02-04.1.pdf) —
    the chapter is the section minus its last component."""
    parts = section.rsplit("-", 1)
    if len(parts) != 2:
        return web_templates.OFFICIAL_FALLBACK["ndac"]
    return f"https://ndlegis.gov/information/acdata/pdf/{parts[0]}.pdf"


def _rule_official_fn(ver):
    """Rules versions carry per-rule ndcourts.gov source URLs."""
    if ver is not None and ver["source_url"] and \
            ver["source_url"].startswith("https://www.ndcourts.gov/"):
        return ver["source_url"]
    return web_templates.OFFICIAL_FALLBACK["rule"]


def _prov_spec(kind: str, params: dict):
    """(corpus_name, citation, canon, official_fn) for a provision URL,
    or None when the URL can't name a provision."""
    if kind == "ndcc":
        sec = params["section"]
        return ("ndcc", f"N.D.C.C. § {sec}", f"/ndcc/{sec}",
                lambda ver, s=sec: _ndcc_official_url(s))
    if kind == "ndac":
        sec = params["section"]
        return ("admin", f"N.D.A.C. § {sec}", f"/ndac/{sec}",
                lambda ver, s=sec: _ndac_official_url(s))
    if kind == "const":
        art = params["art"].upper()
        if not _ROMAN.match(art):
            return None
        sec = params["sec"]
        return ("const", f"N.D. Const. art. {art}, § {sec}",
                f"/const/{art}/{sec}",
                lambda ver: web_templates.OFFICIAL_FALLBACK["const"])
    if kind == "rule":
        prefix = _RULE_SETS.get(params["set"].lower())
        if not prefix:
            return None
        num = params["num"]
        return ("rule", f"{prefix} {num}",
                f"/rule/{params['set'].lower()}/{num}", _rule_official_fn)
    return None


def _document_page(request: Request, kind: str, number: str) -> Response:
    """AG / JEAC opinion page: immutable dated document with its
    court-citations list; footer links the authoritative source PDF."""
    from . import ag_corpus, jeac_corpus
    conn = _conn()
    try:
        if kind == "ag":
            ok = ag_corpus.attach_ag(conn, read_only=True)
            tbl, bk, fk = "ag.ag_opinions", "ag.ag_cited_by_court", \
                "ag_opinion_id"
            cite_col, fallback = "ag_cite", "ag"
        else:
            ok = jeac_corpus.attach_jeac(conn, read_only=True)
            tbl, bk, fk = "jeac.jeac_opinions", "jeac.jeac_cited_by_court", \
                "jeac_opinion_id"
            cite_col, fallback = "jeac_cite", "jeac"
        if not ok:
            return _not_found(request, f"{kind}/{number}")
        row = conn.execute(
            f"SELECT * FROM {tbl} WHERE opinion_number=? "
            "OR cite_key=?", (number, number)).fetchone()
        if not row or not row["text_content"]:
            return _not_found(request, f"{kind}/{number}")
        meta = []
        if row["date_issued"]:
            meta.append(f"<b>Issued</b> {html.escape(row['date_issued'])}")
        for col, label in (("issued_to", "Issued to"),
                           ("opinion_type", "Type"), ("status", "Status"),
                           ("digest", "Digest")):
            if col in row.keys() and row[col]:
                meta.append(f"<b>{label}</b> {html.escape(str(row[col]))}")
        citers = [r[0] for r in conn.execute(
            f"""SELECT DISTINCT cb.court_opinion_id FROM {bk} cb
                JOIN opinions o ON o.id = cb.court_opinion_id
                WHERE cb.{fk} = ?
                ORDER BY o.date_filed DESC""", (row["id"],))]
        cited = (f"<h2>Cited by the court</h2>{_link_list(conn, citers)}"
                 if citers else "")
        paras = "".join(f"<p>{html.escape(ln)}</p>"
                        for ln in row["text_content"].split("\n")
                        if ln.strip())
        body = (f'<p class="meta">{" · ".join(meta)}</p>'
                f'<div class="prov">{paras}</div>{cited}')
        official = (row["source_url"]
                    or web_templates.OFFICIAL_FALLBACK[fallback])
        title = row[cite_col]
        return _html(request, web_templates.page(
            title, body, h1=title, official_url=official))
    finally:
        conn.close()


def _prov_page(request: Request, name: str, citation: str, canon: str,
               official_fn) -> Response:
    """Phase B provision page (PLAN-web-interface §4.2) — version text
    with ?as_of handling, effective window, amendment history,
    xref/construing counts linked to subpages. Thin wrappers over corpus
    queries; 404s when the corpus DB is not installed. ``official_fn``
    maps the selected version row to the footer official-source URL."""
    conn = _conn()
    try:
        try:
            attached = corpus.attach_corpora(conn, read_only=True)
        except sqlite3.Error:
            attached = []
        if name not in attached:        # corpus NAMES, not ATTACH aliases
            return _not_found(request, citation)
        al = corpus.CORPORA[name]["alias"]
        prov = conn.execute(
            f"SELECT id, citation, heading, status FROM {al}.provisions "
            "WHERE corpus=? AND citation=?", (name, citation)).fetchone()
        if not prov:
            return _not_found(request, citation)
        versions = conn.execute(
            f"""SELECT id, effective_start, effective_end,
                       source_authority, source_url
               FROM {al}.provision_versions WHERE provision_id=?
               ORDER BY effective_start""", (prov["id"],)).fetchall()
        if not versions:
            return _not_found(request, citation)
        as_of = request.query_params.get("as_of", "")
        ver = None
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", as_of):
            for v in versions:
                if (v["effective_start"] or "") <= as_of and \
                        (v["effective_end"] is None
                         or as_of < v["effective_end"]):
                    ver = v
                    break
        if ver is None:
            ver = next((v for v in versions if v["effective_end"] is None),
                       versions[-1])
        text = conn.execute(
            f"SELECT text_content FROM {al}.provision_versions "
            "WHERE id=?", (ver["id"],)).fetchone()[0]
        construing = conn.execute(
            "SELECT COUNT(DISTINCT opinion_id) FROM text_citations "
            "WHERE normalized=?", (citation,)).fetchone()[0]
        try:
            xrefs_out = conn.execute(
                f"SELECT COUNT(*) FROM {al}.provision_xrefs "
                "WHERE version_id=?", (ver["id"],)).fetchone()[0]
        except sqlite3.OperationalError:
            xrefs_out = 0

        window = (f"effective {ver['effective_start'] or '(unknown)'} – "
                  f"{ver['effective_end'] or 'current'}")
        meta = [f"<b>{html.escape(window)}</b>"]
        if prov["status"] != "active":
            meta.append(f"<b>Status</b> {html.escape(prov['status'])}")
        history = ""
        if len(versions) > 1:
            hrows = "".join(
                f"<tr><td>{html.escape(v['effective_start'] or '?')}</td>"
                f"<td>{html.escape(v['effective_end'] or 'current')}</td>"
                f"<td>{html.escape(v['source_authority'] or '')}</td></tr>"
                for v in versions)
            history = (f"<h2>History</h2><table class=\"meta\">"
                       f"<tr><th>from</th><th>to</th><th>authority</th>"
                       f"</tr>{hrows}</table>")
        paras = web_templates.render_provision_body(text)
        body = f"""
<p class="meta">{' · '.join(meta)}</p>
<div class="counts">
  Construed by <a href="{canon}/construing">{construing} opinion{'s' if construing != 1 else ''}</a>
  · <a href="{canon}/xrefs">{xrefs_out} cross-reference{'s' if xrefs_out != 1 else ''}</a>
</div>
<div class="prov">{paras}</div>
{history}
"""
        h1 = citation + (f" — {prov['heading']}" if prov["heading"] else "")
        return _html(request, web_templates.page(
            citation, body, h1=h1, official_url=official_fn(ver)))
    finally:
        conn.close()


def _prov_sub(request: Request, name: str, citation: str, canon: str,
              official_fn, sub: str) -> Response:
    """{canon}/construing (paginated citing opinions) and {canon}/xrefs
    (outbound + inbound provision cross-refs)."""
    if sub not in ("construing", "xrefs"):
        return _not_found(request, f"{canon}/{sub}")
    conn = _conn()
    try:
        try:
            attached = corpus.attach_corpora(conn, read_only=True)
        except sqlite3.Error:
            attached = []
        if name not in attached:
            return _not_found(request, citation)
        al = corpus.CORPORA[name]["alias"]
        prov = conn.execute(
            f"SELECT id, citation, heading FROM {al}.provisions "
            "WHERE corpus=? AND citation=?", (name, citation)).fetchone()
        if not prov:
            return _not_found(request, citation)
        back = (f'<p class="meta"><a href="{canon}">'
                f"← {html.escape(citation)}</a></p>")

        if sub == "construing":
            total = conn.execute(
                "SELECT COUNT(DISTINCT opinion_id) FROM text_citations "
                "WHERE normalized=?", (citation,)).fetchone()[0]
            pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
            try:
                pageno = int(request.query_params.get("page", "1"))
            except ValueError:
                pageno = 0
            if not (1 <= pageno <= pages):
                return _not_found(request, f"{citation} construing page")
            oids = [r[0] for r in conn.execute(
                """SELECT DISTINCT tc.opinion_id FROM text_citations tc
                   JOIN opinions o ON o.id = tc.opinion_id
                   WHERE tc.normalized=?
                   ORDER BY o.date_filed DESC, o.id
                   LIMIT ? OFFSET ?""",
                (citation, PAGE_SIZE, (pageno - 1) * PAGE_SIZE))]
            pager = ""
            if pages > 1:
                parts = []
                if pageno > 1:
                    parts.append(f'<a href="{canon}/construing'
                                 f'?page={pageno-1}">← newer</a>')
                parts.append(f"page {pageno} of {pages}")
                if pageno < pages:
                    parts.append(f'<a href="{canon}/construing'
                                 f'?page={pageno+1}">older →</a>')
                pager = f'<p class="pager">{" · ".join(parts)}</p>'
            body = (back + f'<p class="meta">{total} total</p>'
                    + _link_list(conn, oids) + pager)
            title = f"Opinions construing {citation}"
        else:
            cur = conn.execute(
                f"""SELECT id, effective_start, effective_end, source_url
                   FROM {al}.provision_versions
                   WHERE provision_id=? AND effective_end IS NULL
                   ORDER BY effective_start DESC LIMIT 1""",
                (prov["id"],)).fetchone()
            items = []
            xrows = []
            if cur:
                try:
                    xrows = conn.execute(
                        f"""SELECT to_corpus, to_citation, raw_text
                           FROM {al}.provision_xrefs WHERE version_id=?
                           ORDER BY to_citation""",
                        (cur["id"],)).fetchall()
                except sqlite3.OperationalError:
                    xrows = []
            if True:
                for r in xrows:
                    items.append(f"<li>{_prov_link(r['to_corpus'], r['to_citation'])}</li>")
            out_html = ("<h2>References out</h2>"
                        + (f"<ul>{''.join(items)}</ul>" if items
                           else "<p class=\"meta\">none</p>"))
            inbound = []
            alias_by_name = {n: m["alias"]
                            for n, m in corpus.CORPORA.items()}
            for name in attached:
                al = alias_by_name[name]
                try:
                    rows = conn.execute(
                        f"""SELECT p.corpus, p.citation
                            FROM {al}.provision_xrefs x
                            JOIN {al}.provisions p ON p.id = x.provision_id
                            JOIN {al}.provision_versions v
                                 ON v.id = x.version_id
                                 AND v.effective_end IS NULL
                            WHERE x.to_citation = ?
                            ORDER BY p.citation""",
                        (citation,)).fetchall()
                except sqlite3.OperationalError:
                    continue            # corpus without xref tables
                for r in rows:
                    inbound.append(f"<li>{_prov_link(r['corpus'], r['citation'])}</li>")
            in_html = ("<h2>Referenced by</h2>"
                       + (f"<ul>{''.join(inbound)}</ul>" if inbound
                          else "<p class=\"meta\">none</p>"))
            body = back + out_html + in_html
            title = f"Cross-references — {citation}"
        return _html(request, web_templates.page(
            title, body, h1=title,
            official_url=official_fn(None)))
    finally:
        conn.close()


def _cites_line(conn, oid: int) -> str:
    rows = [dict(r) for r in conn.execute(
        "SELECT citation, reporter, is_primary FROM citations "
        "WHERE opinion_id = ?", (oid,))]
    ordered, synthetic = proofread.order_citations(rows)
    parts = [html.escape(r["citation"]) for r in ordered]
    parts += [html.escape(s) for s in synthetic]
    return " · ".join(parts)


def _opinion_page(conn, request: Request, row) -> Response:
    oid = row["id"]
    cited_by_n = conn.execute(
        "SELECT COUNT(*) FROM cited_by WHERE cited_opinion_id = ?",
        (oid,)).fetchone()[0]
    cites_out_n = conn.execute(
        "SELECT COUNT(*) FROM cited_by WHERE citing_opinion_id = ?",
        (oid,)).fetchone()[0]
    canon = canonical_path(conn, oid)

    def col(name):
        try:
            return row[name]
        except (IndexError, KeyError):
            return None

    meta = []
    date_line = f"<b>Filed</b> {html.escape(row['date_filed'])}"
    if col("date_rehearing"):
        date_line += (f" · <b>On rehearing</b> "
                      f"{html.escape(col('date_rehearing'))}")
    meta.append(date_line)
    if row["author"]:
        meta.append(f"<b>Author</b> {html.escape(row['author'])}")
    if row["per_curiam"]:
        meta.append("<b>Per curiam</b>")
    if col("all_justices"):
        try:
            import json as _json
            meta.append("<b>Panel</b> " + html.escape(
                ", ".join(_json.loads(col("all_justices")))))
        except Exception:
            pass
    if row["docket_number"]:
        meta.append(f"<b>Docket</b> {html.escape(row['docket_number'])}")
    if col("disposition"):
        meta.append(f"<b>Disposition</b> {html.escape(col('disposition'))}")
    if col("precedential_status"):
        meta.append(f"<b>Status</b> {html.escape(col('precedential_status'))}")

    srcs = []
    if col("opinion_url"):
        srcs.append(f'<a href="{html.escape(col("opinion_url"), quote=True)}">'
                    "Original PDF (ndcourts.gov)</a>")
    if col("absolute_url"):
        url = col("absolute_url")
        if not url.startswith("http"):
            url = "https://www.courtlistener.com" + url
        srcs.append(f'<a href="{html.escape(url, quote=True)}">CourtListener</a>')

    body = f"""
<p class="meta cites">{_cites_line(conn, oid)}</p>
<p class="meta">{' · '.join(meta)}</p>
<div class="counts">
  Cited by <a href="{canon}/citing">{cited_by_n} opinion{'s' if cited_by_n != 1 else ''}</a>
  · Cites <a href="{canon}/cited">{cites_out_n} authorit{'ies' if cites_out_n != 1 else 'y'}</a>
</div>
{web_templates.render_body(row['text_content'])}
{f'<p class="srcs">Source: {" · ".join(srcs)}</p>' if srcs else ''}
"""
    title = f"{row['case_name']}"
    return _html(request, web_templates.page(
        title, body, h1=row["case_name_full"] or row["case_name"],
        official_url=_official_url(row)))


def _disambiguation(conn, request: Request, cite: str, rows) -> Response:
    items = []
    for r in rows:
        canon = canonical_path(conn, r["id"])
        items.append(
            f'<li><a href="{canon}?id={r["id"]}">'
            f'{html.escape(r["case_name"])}</a> '
            f'<span class="meta">({html.escape(r["date_filed"])})</span></li>')
    body = (f"<p>More than one opinion is printed at "
            f"<b>{html.escape(cite)}</b> (a shared reporter page):</p>"
            f'<ul class="candidates">{"".join(items)}</ul>')
    return _html(request, web_templates.page(
        f"{cite} — multiple opinions", body, h1=cite), max_age=3600)


def _not_found(request: Request, token: str) -> Response:
    body = f"""
<p>Nothing in the corpus answers to <b>{html.escape(token[:80])}</b>.</p>
<p>Accepted citation forms:</p>
<p><code>2020 ND 30</code> · <code>604 N.W.2d 458</code> ·
<code>13 N.D. 359</code> — as URLs: <code>/2020ND30</code>,
<code>/NW2d/604/458</code>, <code>/ND/13/359</code>, or
<code>/cite/&lt;citation&gt;</code>.</p>
"""
    return _html(request, web_templates.page("Not found", body, h1="Not found"),
                 status=404, max_age=3600)


def _serve_cite(request: Request, cite: str, current_path: str) -> Response:
    """Resolve an exact citation string and serve/redirect appropriately."""
    conn = _conn()
    try:
        rows = _rows_for_cite(conn, cite)
        if not rows:
            return _not_found(request, cite)
        want_id = request.query_params.get("id")
        if want_id and want_id.isdigit():
            picked = [r for r in rows if r["id"] == int(want_id)]
            if picked:
                return _opinion_page(conn, request, picked[0])
        if len(rows) > 1:
            return _disambiguation(conn, request, cite, rows)
        row = rows[0]
        canon = canonical_path(conn, row["id"])
        if current_path != canon:
            return _redirect(canon)
        return _opinion_page(conn, request, row)
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# citing / cited subpages
# ---------------------------------------------------------------------------

def _link_list(conn, oids: list[int]) -> str:
    items = []
    for oid in oids:
        r = conn.execute(
            "SELECT id, case_name, date_filed FROM opinions WHERE id = ?",
            (oid,)).fetchone()
        if r is None:
            continue
        canon = canonical_path(conn, r["id"])
        items.append(f'<li><a href="{canon}">{html.escape(r["case_name"])}</a> '
                     f'<span class="meta">({html.escape(r["date_filed"])}) — '
                     f'{_cites_line(conn, r["id"])}</span></li>')
    return f'<ul class="candidates">{"".join(items)}</ul>'


def _sub_page(request: Request, cite: str, direction: str) -> Response:
    conn = _conn()
    try:
        rows = _rows_for_cite(conn, cite)
        if not rows:
            return _not_found(request, cite)
        row = rows[0]
        oid = row["id"]
        canon = canonical_path(conn, oid)
        if direction == "citing":
            col_match, col_get = "cited_opinion_id", "citing_opinion_id"
            label = "Opinions citing"
        else:
            col_match, col_get = "citing_opinion_id", "cited_opinion_id"
            label = "Authorities cited by"
        total = conn.execute(
            f"SELECT COUNT(*) FROM cited_by WHERE {col_match} = ?",
            (oid,)).fetchone()[0]
        pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
        try:
            pageno = int(request.query_params.get("page", "1"))
        except ValueError:
            pageno = 0
        if not (1 <= pageno <= pages):
            return _not_found(request, f"{cite} {direction} page")
        oids = [r[0] for r in conn.execute(
            f"""SELECT cb.{col_get} FROM cited_by cb
                JOIN opinions o ON o.id = cb.{col_get}
                WHERE cb.{col_match} = ?
                ORDER BY o.date_filed DESC, o.id
                LIMIT ? OFFSET ?""",
            (oid, PAGE_SIZE, (pageno - 1) * PAGE_SIZE))]
        pager = ""
        if pages > 1:
            parts = []
            if pageno > 1:
                parts.append(f'<a href="{canon}/{direction}?page={pageno-1}">← newer</a>')
            parts.append(f"page {pageno} of {pages}")
            if pageno < pages:
                parts.append(f'<a href="{canon}/{direction}?page={pageno+1}">older →</a>')
            pager = f'<p class="pager">{" · ".join(parts)}</p>'
        body = (f'<p class="meta"><a href="{canon}">'
                f"← {html.escape(row['case_name'])}</a> · {total} total</p>"
                + _link_list(conn, oids) + pager)
        return _html(request, web_templates.page(
            f"{label} {row['case_name']}", body,
            h1=f"{label} {row['case_name']}",
            official_url=_official_url(row)))
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# route registration
# ---------------------------------------------------------------------------

def _build_stamp(db_path) -> str:
    """ETag stamp: BOTH the data build (DB mtime) and the code version —
    a code-only deploy must invalidate cached renders (stale-HTML 304s
    caught by JT 2026-07-30)."""
    try:
        from importlib.metadata import version
        code_v = version("ndlaw-mcp")
    except Exception:
        code_v = "dev"
    try:
        return f"{int(os.path.getmtime(db_path))}-{code_v}"
    except OSError:
        return f"dev-{code_v}"


def register(mcp, db_path=None) -> None:
    """Attach the web routes to the FastMCP app. Called from server.main()."""
    global _DB_PATH, _STAMP
    if db_path is not None:
        _DB_PATH = db_path
    _STAMP = _build_stamp(_DB_PATH)

    async def _resolve_free(request: Request, q: str) -> Response:
        cite = free_text_to_cite(q)
        if cite is None:
            return _not_found(request, q)
        conn = _conn()
        try:
            rows = _rows_for_cite(conn, cite)
            if not rows:
                return _not_found(request, cite)
            if len(rows) > 1:
                return _disambiguation(conn, request, cite, rows)
            return _redirect(canonical_path(conn, rows[0]["id"]))
        finally:
            conn.close()

    @mcp.custom_route("/cite/{free:path}", methods=["GET"])
    async def cite_path(request: Request) -> Response:
        return await _resolve_free(request, request.path_params["free"])

    @mcp.custom_route("/cite", methods=["GET"])
    async def cite_query(request: Request) -> Response:
        return await _resolve_free(request, request.query_params.get("q", ""))

    def _prov_routes(kind, *segs):
        path = "/" + kind + "".join("/{%s}" % g for g in segs)

        async def prov(request: Request) -> Response:
            spec = _prov_spec(kind, request.path_params)
            if spec is None:
                return _not_found(request, request.url.path)
            return _prov_page(request, *spec)

        async def prov_sub(request: Request) -> Response:
            spec = _prov_spec(kind, request.path_params)
            if spec is None:
                return _not_found(request, request.url.path)
            return _prov_sub(request, *spec,
                             request.path_params["sub"])

        mcp.custom_route(path, methods=["GET"])(prov)
        mcp.custom_route(path + "/{sub}", methods=["GET"])(prov_sub)

    _prov_routes("ndcc", "section")
    _prov_routes("ndac", "section")
    _prov_routes("const", "art", "sec")
    _prov_routes("rule", "set", "num")

    @mcp.custom_route("/ag/{number}", methods=["GET"])
    async def ag_doc(request: Request) -> Response:
        return _document_page(request, "ag", request.path_params["number"])

    @mcp.custom_route("/jeac/{number}", methods=["GET"])
    async def jeac_doc(request: Request) -> Response:
        return _document_page(request, "jeac",
                              request.path_params["number"])

    @mcp.custom_route("/robots.txt", methods=["GET"])
    async def robots(request: Request) -> Response:
        # unlisted policy (§7): landing page findable, content disallowed.
        # In production Apache serves the static copy; this covers local runs.
        return Response("User-agent: *\nAllow: /$\nDisallow: /\n",
                        media_type="text/plain",
                        headers=_headers(max_age=86400))

    for fam in ("ND", "NW", "NW2d"):
        series = {"ND": "N.D.", "NW": "N.W.", "NW2d": "N.W.2d"}[fam]

        def _mk(series=series, fam=fam):
            async def reporter_page(request: Request) -> Response:
                vol = request.path_params["vol"]
                pg = request.path_params["page"]
                if not (vol.isdigit() and pg.isdigit()):
                    return _not_found(request, f"{fam}/{vol}/{pg}")
                cite = f"{int(vol)} {series} {int(pg)}"
                return _serve_cite(request, cite, request.url.path)

            async def reporter_sub(request: Request) -> Response:
                vol = request.path_params["vol"]
                pg = request.path_params["page"]
                sub = request.path_params["sub"]
                if not (vol.isdigit() and pg.isdigit()) or sub not in (
                        "citing", "cited"):
                    return _not_found(request, f"{fam}/{vol}/{pg}/{sub}")
                cite = f"{int(vol)} {series} {int(pg)}"
                return _sub_page(request, cite, sub)
            return reporter_page, reporter_sub

        rp, rs = _mk()
        mcp.custom_route(f"/{fam}/{{vol}}/{{page}}", methods=["GET"])(rp)
        mcp.custom_route(f"/{fam}/{{vol}}/{{page}}/{{sub}}", methods=["GET"])(rs)

    @mcp.custom_route("/{token}", methods=["GET"])
    async def bare_token(request: Request) -> Response:
        token = request.path_params["token"]
        cite = token_to_cite(token)
        if cite is None:
            return _not_found(request, token)
        return _serve_cite(request, cite, request.url.path)

    @mcp.custom_route("/{token}/{sub}", methods=["GET"])
    async def bare_token_sub(request: Request) -> Response:
        token = request.path_params["token"]
        sub = request.path_params["sub"]
        cite = token_to_cite(token)
        if cite is None or sub not in ("citing", "cited"):
            return _not_found(request, f"{token}/{sub}")
        return _sub_page(request, cite, sub)
