#!/usr/bin/env python3
"""Verify agent outputs and splice the passing ones into scratch.

Independent gates (no agent output trusted until it passes):
 1. mechanical: each edit_list after-anchor unique in current_text; applying
    edit_list to current yields the agent's prior (we recompute prior ourselves).
 2. 1981 Blue Book witness: where the article is clean in the BB, the prior must
    appear (normalized substring / high fuzzy). Articles III/VI/IX/XII/XIII are
    OCR-degraded in the BB -> no witness -> flagged 'needs-2nd-read', spliced to
    SCRATCH only (never live) pending an independent second read.
"""
import json, re, sqlite3, difflib
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB = "/tmp/const-scratch.db"
BB = (Path.home() / "refs/nd/const/processed/1981_blue-book_constitution.md").read_text()
BBN = re.sub(r"[^a-z0-9]", "", BB.lower())

# agent edit_lists (REDLINE, high confidence). current_text pulled from batch files.
RESULTS = {
 "N.D. Const. art. III, § 5": ("2015-01-01", [["less than one hundred twenty days before","less than ninety days before"]]),
 "N.D. Const. art. X, § 9": ("1982-12-02", [["assembly may provide for the levy","assembly may by law provide for the levy"],["a tax upon lands within the state for the purpose","a tax upon such lands as may be provided by law of the state for the purpose"],["losses by hail. The legislative assembly may classify lands within the state, and divide","losses by hail; provided, that such tax shall not affect the tax of four mills levied by the constitution. The legislative assembly may classify such lands of the state as may be provided by law, and divide"],["burden of the tax among the owners of such lands.","burden of such tax among the owners of such land as may be provided by law."]]),
 "N.D. Const. art. III, § 6": ("2015-01-01", [["and if the secretary of state finds it insufficient","and if he finds it insufficient"],["insufficient, the secretary of state shall notify","insufficient, he shall notify"],["twenty days for correction. All","twenty days for correction or amendment. All"],["in regard to any petition are subject","in regard to any such petition shall be subject"],["sufficiency of the petition is being","sufficiency of such petition is being"],["invalidate the measure if it is at the election","invalidate such measure if it is at such election"],["the burden of proof is upon the party attacking it and the proceedings must be filed with the supreme court no later than seventy-five days before the date of the statewide election at which the measure is to be voted upon.","the burden of proof shall be upon the party attacking it."]]),
 "N.D. Const. art. X, § 17": ("1984-07-12", [["the state is valid unless it has endorsed","the state shall be valid unless the same shall have endorsed"],["subdivision is valid unless it has endorsed","subdivision shall be valid unless the same shall have endorsed"],["signed by the officer authorized","signed by the county auditor, or other officer authorized"],["stating that said bond or evidence of debt is issued","stating that said bond, or evidence of debt, is issued"]]),
 "N.D. Const. art. III, § 7": ("2015-01-01", [[" A proceeding to review a decision of the secretary of state must be filed with the supreme court no later than seventy- five days before the date of the statewide election at which the measure is to be voted upon.",""],["If the decision of the secretary of state is being reviewed","If his decision is being reviewed"],["prepared, the secretary of state shall place","prepared, he shall place"]]),
 "N.D. Const. art. XI, § 25": ("2002-12-05", [["whatever. However, the legislative assembly shall authorize the state of North Dakota to join a multi-state lottery for the benefit of the state of North Dakota, and, the legislative assembly may authorize","whatever. However, the legislative assembly may authorize"]]),
 "N.D. Const. art. VI, § 13": ("1998-07-09", [["1. A judicial nominating committee must be established","A judicial nominating committee shall be established"],["by law. The governor shall fill any vacancy in the office of supreme court justice or district court judge by appointment from a list","by law. Any vacancy in the office of supreme court justice or district court judge shall be filled by appointment by the governor from a list"],["the term. Except as provided in subsection 2, an appointment must continue until the next general election, when the office must be filled by election for the remainder of the term. 2. An appointment must continue for at least two years. If the term of the appointed judgeship expires before the judge has served at least two years, the judge shall continue in the position until the next general election immediately following the service of at least two years. 3. Notwithstanding sections 7 and 9 of this article, the term of the judge elected at the subsequent general election provided for in subsection 2 is reduced to the number of years remaining in the subsequent term after the appointee has served at least two years. ])]","the term. An appointment shall continue until the next general election, when the office shall be filled by election for the remainder of the term."]]),
 "N.D. Const. art. XII, § 2": ("2006-07-01", [["All corporations existing","No charter of incorporation shall be granted, changed or amended by special law, except in the case of such municipal, charitable, educational, penal or reformatory corporations as may be under the control of the state; but the All corporations existing"],["The legislative assembly may provide","The legislative assembly shall provide"],["for the organization and regulation of corporations, and any law, so enacted, is subject to future repeal or amendment.","for the organization of all corporations hereafter to be created, and any such law, so passed, shall be subject to future repeal or alteration."]]),
 "N.D. Const. art. IX, § 4": ("1984-07-12", [["public officers designated by law","county superintendent of common schools, the chairman of the county board, and the county auditor"]]),
 "N.D. Const. art. XII, § 6": ("2006-07-01", [["Unless otherwise provided in the articles of incorporation, in all","In all"],["the whole number of the member's or shareholder's votes","the whole number of his votes"],["as the member or shareholder may prefer","as he may prefer"]]),
 "N.D. Const. art. IX, § 6": ("1986-07-10", [["school lands, including state coal mineral interests, may, with","school lands, may, with"],["be exchanged for lands and coal mineral interests of the United States","be exchanged for lands of the United States"],["in land so transferred, except coal mineral interests approved for exchange by the board of university and school lands under this section.","in land so transferred."]]),
 "N.D. Const. art. IX, § 10": ("1982-12-02", [["assembly may provide","assembly shall have authority to provide"],["have been, or","have been heretofore, or"],["set forth in article","set forth and named in article"],["section 1. The legislative","section 1, and section 159. And the. The legislative"],["the appraisal, sale","the appraisement, sale"],["rental, and disposal","rental and disposal"],["limitations of article IX, sections 1 through 11.","limitations of this article."]]),
 "N.D. Const. art. XIII, § 2": ("1996-07-11", [["Fort Pembina, and","Fort Pembina and"],["state, extends over those","state, shall extend over such"],["limits of those reservations","limits of such reservations"],[" The legislative assembly may provide, upon the terms and conditions it adopts, for the acceptance of any jurisdiction as may be delegated to the state by act of Congress.",""]]),
}
# clean BB articles (bold single-line format); others are letter-spacing-degraded.
BB_CLEAN_ARTS = {"VIII", "X", "XI"}


def current_texts():
    out = {}
    for f in sorted(HERE.glob("batch-*.json")):
        for t in json.loads(f.read_text()):
            out[t["citation"]] = t["current_text"]
    return out


def apply_edits(text, edits):
    for after, before in edits:
        if text.count(after) != 1:
            raise ValueError(f"anchor x{text.count(after)}: {after[:40]!r}")
        text = text.replace(after, before)
    return text


def main(apply=False):
    cur = current_texts()
    con = sqlite3.connect(DB)
    ok, fail, splice = [], [], []
    for cite, (d1, edits) in RESULTS.items():
        c = " ".join(cur[cite].split())
        try:
            prior = apply_edits(c, edits)
        except ValueError as e:
            fail.append((cite, f"MECH FAIL: {e}")); continue
        art = re.search(r"art\.\s+([IVXL]+)", cite).group(1)
        pn = re.sub(r"[^a-z0-9]", "", prior.lower())
        if art in BB_CLEAN_ARTS:
            if pn in BBN:
                bb = "BB-PASS"
            else:
                sm = difflib.SequenceMatcher(None, pn, BBN, autojunk=False)
                r = sum(b.size for b in sm.get_matching_blocks()) / len(pn)
                bb = f"BB-NEAR({r:.2f})" if r >= 0.92 else f"BB-CHECK({r:.2f})"
        else:
            bb = "no-clean-BB-witness"
        ok.append((cite, d1, bb, len(prior)))
        if not bb.startswith("BB-CHECK"):
            splice.append((cite, d1, prior, bb))

    print(f"=== VERIFICATION ({len(RESULTS)} REDLINE results) ===")
    for cite, d1, bb, n in ok:
        print(f"  OK  {cite:<26} d1={d1}  {bb}  prior={n}c")
    for cite, why in fail:
        print(f"  XX  {cite:<26} {why}")

    if apply:
        B = "modern-redline-agent-2026-06-14"
        for cite, d1, prior, bb in splice:
            row = con.execute("SELECT p.id, p.current_version_id FROM provisions p WHERE p.citation=?", (cite,)).fetchone()
            pid, vid = row
            con.execute("DELETE FROM provision_versions WHERE provision_id=? AND batch=?", (pid, B))
            con.execute("UPDATE provision_versions SET effective_start=? WHERE id=?", (d1, vid))
            end = (date.fromisoformat(d1) - timedelta(days=1)).isoformat()
            nvid = con.execute("INSERT INTO provision_versions (provision_id, effective_start, effective_end, "
                "text_content, source_authority, batch) VALUES (?,?,?,?,?,?)",
                (pid, "1981-01-01", end, prior, f"agent-read redline ({bb})", B)).lastrowid
            con.execute("INSERT INTO changelog (batch, provision_id, version_id, field, new_value, authority) "
                "VALUES (?,?,?,?,?,?)", (B, pid, nvid, "version_splice_agent_redline",
                f"[1981-01-01 → {end}] prior reconstructed by agent ({bb})", "multi-agent redline campaign"))
        con.commit()
        print(f"\nSPLICED {len(splice)} to scratch (batch {B}); "
              f"{sum(1 for _,_,_,b in splice if b.startswith('BB'))} BB-witnessed.")
        # integrity
        g = con.execute("""WITH v AS (SELECT provision_id, effective_start, effective_end,
          LEAD(effective_start) OVER (PARTITION BY provision_id ORDER BY effective_start) nxt FROM provision_versions)
          SELECT count(*) FROM v WHERE nxt IS NOT NULL AND effective_end IS NOT NULL AND effective_end!=''
          AND date(effective_end)!=date(nxt) AND date(effective_end,'+1 day')!=date(nxt)""").fetchone()[0]
        print(f"integrity gaps/overlaps: {g}")
    con.close()


if __name__ == "__main__":
    import sys
    main(apply="--apply" in sys.argv)
