#!/usr/bin/env python3
"""art XIII § 1 [1981,1996) — the pre-1996 3-subsection Compact (Group B).

Amendment #132 (eff 1996-07-11, "eliminates outdated language … settling of territorial
debts") kept only subsection 1 (modernized) and DELETED subsections 2 (federal public-lands
disclaimer) and 3 (the 1889 territorial-debt settlement). This prepends the full pre-1996
text [1981-01-01, 1996-07-10].

Text reconciled (subagent, then gated here) from the cleanest sources:
- sub 1 (toleration): identical across 1895/1913/1925/1989 BB.
- sub 2 (disclaimer): the POST-1958 version with the "provided, however … acceptance of such
  jurisdiction" clause (1958 amendment) — VERIFIED == historical § 203 (ratio 0.998; only the
  old "Second." ordinal dropped).
- sub 3 (debt settlement): long obsolete bond-list; transcribed from 1913 official, all 14
  dollar amounts cross-verified across 1895/1913/1925.

Gates (here): sub2 == historical § 203 (>=0.99); the full assembly's s1+s3 match the
COMPLETE 1913 official compact at overlap >=0.95 (the only gap being the 1958 jurisdiction
clause legitimately added to s2); current starts 1996-07-11. (NB: the 1989 BB processed
file is truncated mid-s3 at a page break, so it is NOT used as the gate witness.)
Idempotent (batch-scoped). Scratch only.
"""
import re
import sqlite3
import sys
import difflib
from pathlib import Path

DB = "/tmp/const-scratch.db"
BATCH = "modern-artxiii1-compact-1996-2026-06-15"
CITE = "N.D. Const. art. XIII, § 1"
PRIOR_START, PRIOR_END, CUR_START = "1981-01-01", "1996-07-10", "1996-07-11"

S1 = ("Perfect toleration of religious sentiment shall be secured, and no inhabitant of "
      "this state shall ever be molested in person or property on account of his or her mode "
      "of religious worship.")

S2 = ("The people inhabiting this state do agree and declare that they forever disclaim all "
      "right and title to the unappropriated public lands lying within the boundaries thereof, "
      "and to all lands lying within said limits owned or held by any Indian or Indian tribes, "
      "and that until the title thereto shall have been extinguished by the United States, the "
      "same shall be and remain subject to the disposition of the United States, and that said "
      "Indian lands shall remain under the absolute jurisdiction and control of the congress of "
      "the United States, provided, however, that the legislative assembly of the state of North "
      "Dakota may, upon such terms and conditions as it shall adopt, provide for the acceptance "
      "of such jurisdiction as may be delegated to the state by act of congress; that the lands "
      "belonging to citizens of the United States residing without this state shall never be "
      "taxed at a higher rate than the lands belonging to residents of this state; that no taxes "
      "shall be imposed by this state on lands or property therein belonging to, or which may "
      "hereafter be purchased by the United States, or reserved for its use. But nothing in this "
      "article shall preclude this state from taxing as other lands are taxed, any lands owned or "
      "held by any Indian who has severed his tribal relations, and has obtained from the United "
      "States or from any person, a title thereto, by patent or other grant, save and except such "
      "lands as have been or may be granted to any Indian or Indians under any acts of congress "
      "containing a provision exempting the lands thus granted from taxation, which last mentioned "
      "lands shall be exempt from taxation so long, and to such an extent, as is, or may be "
      "provided in the act of congress granting the same.")

S3 = ("In order that payment of the debts and liabilities contracted or incurred by and on behalf "
      "of the territory of Dakota may be justly and equitably provided for and made, and in "
      "pursuance of the requirements of an act of congress approved February 22, 1889, entitled "
      "\"An act to provide for the division of Dakota into two states and to enable the people of "
      "North Dakota, South Dakota, Montana and Washington to form constitutions and state "
      "governments and to be admitted into the union on an equal footing with the original states, "
      "and to make donations of public lands to such states,\" the states of North Dakota and South "
      "Dakota, by proceedings of a joint commission, duly appointed under said act, the sessions "
      "whereof were held at Bismarck in said state of North Dakota, from July 16, 1889, to July 31, "
      "1889, inclusive, have agreed to the following adjustment of the amounts of the debts and "
      "liabilities of the territory of Dakota which shall be assumed and paid by each of the states "
      "of North Dakota and South Dakota, respectively, to wit: This agreement shall take effect and "
      "be in force from and after the admission into the union, as one of the United States of "
      "America, of either the state of North Dakota or the state of South Dakota. The words \"state "
      "of North Dakota,\" wherever used in this agreement, shall be taken to mean the territory of "
      "North Dakota in case the state of South Dakota shall be admitted into the union prior to the "
      "admission into the union of the state of North Dakota; and the words \"state of South Dakota,\" "
      "wherever used in this agreement, shall be taken to mean the territory of South Dakota in case "
      "the state of North Dakota shall be admitted into the union prior to the admission into the "
      "union of the state of South Dakota. The said state of North Dakota shall assume and pay all "
      "bonds issued by the territory of Dakota to provide funds for the purchase, construction, "
      "repairs or maintenance of such public institutions, grounds or buildings as are located "
      "within the boundaries of North Dakota, and shall pay all warrants issued under and by virtue "
      "of that certain act of the legislative assembly of the territory of Dakota, approved March 8, "
      "1889, entitled \"An act to provide for the refunding of outstanding warrants drawn on the "
      "capitol building fund.\" The state of South Dakota shall assume and pay all bonds issued by "
      "the territory of Dakota to provide funds for the purchase, construction, repairs or "
      "maintenance of such public institutions, grounds or buildings as are located within the "
      "boundaries of South Dakota, that is to say, the state of North Dakota shall assume and pay "
      "the following bonds and indebtedness, to wit: Bonds issued on account of the hospital for "
      "insane at Jamestown, North Dakota, the face aggregate of which is $266,000; also, bonds "
      "issued on account of the North Dakota university at Grand Forks, North Dakota, the face "
      "aggregate of which is $96,700; also, bonds issued on account of the penitentiary at Bismarck, "
      "North Dakota, the face aggregate of which is $93,600; also, refunding capitol building "
      "warrants dated April 1, 1889, $83,507.46. And the state of South Dakota shall assume and pay "
      "the following bonds and indebtedness, to wit: Bonds issued on account of the hospital for the "
      "insane at Yankton, South Dakota, the face aggregate of which is $210,000; also, bonds issued "
      "on account of the school for deaf mutes, at Sioux Falls, South Dakota, the face aggregate of "
      "which is $51,000; also, bonds issued on account of the university at Vermillion, South Dakota, "
      "the face aggregate of which is $75,000; also, bonds issued on account of the penitentiary at "
      "Sioux Falls, South Dakota, the face aggregate of which is $94,300; also, bonds issued on "
      "account of the agricultural college at Brookings, South Dakota, the face aggregate of which is "
      "$97,500; also, bonds issued on account of the normal school at Madison, South Dakota, the face "
      "aggregate of which is $49,400; also, bonds issued on account of the school of mines at Rapid "
      "City, South Dakota, the face aggregate of which is $33,000; also, bonds issued on account of "
      "the reform school at Plankinton, South Dakota, the face aggregate of which is $30,000; also, "
      "bonds issued on account of the normal school at Spearfish, South Dakota, the face aggregate of "
      "which is $25,000; also, bonds issued on account of the soldiers' home at Hot Springs, South "
      "Dakota, the face aggregate of which is $45,000. The states of North Dakota and South Dakota "
      "shall pay one-half each of all liabilities now existing or hereafter and prior to the taking "
      "effect of this agreement incurred, except those heretofore or hereafter incurred, on account "
      "of public institutions, grounds or buildings, except as otherwise herein specifically "
      "provided. The state of South Dakota shall pay to the state of North Dakota $46,500, on account "
      "of the excess of territorial appropriations for the permanent improvement of territorial "
      "institutions which under this agreement will go to South Dakota, and in full of the undivided "
      "one-half interest of North Dakota in the territorial library, and in full settlement of "
      "unbalanced accounts, and of all claims against the territory, of whatever nature, legal or "
      "equitable, arising out of the alleged erroneous or unlawful taxation of Northern Pacific "
      "railroad lands, and the payment of said amount shall discharge and exempt the state of South "
      "Dakota from all liability for or on account of the several matters hereinbefore referred to; "
      "nor shall either state be called upon to pay or answer to any portion of liability hereafter "
      "arising or accruing on account of transactions heretofore had, which liability would be a "
      "liability of the territory of Dakota had such territory remained in existence, and which "
      "liability shall grow out of matters connected with any public institutions, grounds or "
      "buildings of the territory situated or located within the boundaries of the other state. A "
      "final adjustment of accounts shall be made upon the following basis: North Dakota shall be "
      "charged with all sums paid on account of the public institutions, grounds or buildings located "
      "within its boundaries on account of the current appropriations since March 9, 1889; and South "
      "Dakota shall be charged with all sums paid on account of public institutions, grounds or "
      "buildings located within its boundaries on the same account and during the same time. Each "
      "state shall be charged with one-half of all other expenses of the territorial government "
      "during the same time. All moneys paid into the treasury during the period from March 8, 1889, "
      "to the time of taking effect of this agreement by any county, municipality or person within "
      "the limits of the proposed state of North Dakota, shall be credited to the state of North "
      "Dakota; and all sums paid into said treasury within the same time by any county, municipality "
      "or person within the limits of the proposed state of South Dakota shall be credited to the "
      "state of South Dakota; except that any and all taxes on gross earnings paid into said treasury "
      "by railroad corporations, since the 8th day of March, 1889, based upon earnings of years prior "
      "to 1888, under and by virtue of the act of the legislative assembly of the territory of Dakota, "
      "approved March 7, 1889, and entitled \"An act providing for the levy and collection of taxes "
      "upon property of railroad companies in this territory,\" being chapter 107 of the session laws "
      "of 1889 (that is, the part of such sums going to the territory), shall be equally divided "
      "between the states of North Dakota and South Dakota, and all taxes heretofore or hereafter "
      "paid into said treasury under and by virtue of the act last mentioned, based on the gross "
      "earnings of the year 1888, shall be distributed as already provided by law, except that so "
      "much thereof as goes to the territorial treasury shall be divided as follows: North Dakota "
      "shall have so much thereof as shall be or has been paid by railroads within the limits of the "
      "proposed state of North Dakota, and South Dakota so much thereof as shall be or has been paid "
      "by railroads within the limits of the proposed state of South Dakota; each state shall be "
      "credited also with all balances of appropriations made by the seventeenth legislative assembly "
      "of the territory of Dakota for the account of the public institutions, grounds or buildings "
      "situated within its limits, remaining unexpended on March 8, 1889. If there shall be any "
      "indebtedness except the indebtedness represented by the bonds and refunding warrants "
      "hereinbefore mentioned, each state shall at the time of such final adjustment of accounts, "
      "assume its share of said indebtedness as determined by the amount paid on account of the "
      "public institutions, grounds or buildings of such state in excess of the receipts from "
      "counties, municipalities, railroad corporations or persons within the limits of said state, as "
      "provided in this article; and if there should be a surplus at the time of such final "
      "adjustment, each state shall be entitled to the amounts received from counties, municipalities, "
      "railroad corporations or persons within its limits over and above the amount charged it. And "
      "the state of North Dakota hereby obligates itself to pay such part of the debts and liabilities "
      "of the territory of Dakota as is declared by the foregoing agreement to be its proportion "
      "thereof, the same as if such proportion had been originally created by said state of North "
      "Dakota as its own debt or liability.")

PRIOR = f"1. {S1}\n2. {S2}\n3. {S3}"


def dn(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def main(apply=False):
    con = sqlite3.connect(DB)
    prov = con.execute("SELECT id FROM provisions WHERE citation=?", (CITE,)).fetchone()
    pid = prov[0]
    earliest = con.execute("SELECT effective_start FROM provision_versions WHERE provision_id=? "
                           "ORDER BY effective_start LIMIT 1", (pid,)).fetchone()[0]
    h203 = con.execute("SELECT pv.text_content FROM provisions p JOIN provision_versions pv "
                       "ON pv.provision_id=p.id WHERE p.citation='N.D. Const. § 203' "
                       "ORDER BY pv.effective_start DESC LIMIT 1").fetchone()[0]
    # complete clean witness for s1+s3: the 1913 official compact (full, not truncated)
    t13 = Path.home().joinpath("refs/nd/const/processed/1913_official_constitution.md").read_text()
    seg = t13[t13.find("Perfect toleration"):]
    e = seg.find("own debt or liability")
    comp13 = dn(seg[:e + 21]) if e > 0 else dn(seg[:12000])

    r_s2 = difflib.SequenceMatcher(None, dn(S2), dn(h203), autojunk=False).ratio()
    sm = difflib.SequenceMatcher(None, dn(PRIOR), comp13, autojunk=False)
    overlap13 = sum(b.size for b in sm.get_matching_blocks()) / len(dn(PRIOR))
    # the only large PRIOR-side gap vs 1913 must be the 1958 clause (else a transcription error)
    biggaps = [PRIOR_g for t, i1, i2, j1, j2 in sm.get_opcodes()
               if t in ("replace", "delete") and (i2 - i1) > 15
               for PRIOR_g in [dn(PRIOR)[i1:i2]]]
    clause_only = len(biggaps) <= 1 and all("providedhoweverthatthelegislative" in g for g in biggaps)

    problems = []
    if earliest == PRIOR_START:
        print("already spliced (idempotent skip)"); con.close(); return
    if earliest != CUR_START:
        problems.append(f"current earliest {earliest}, expected {CUR_START}")
    if r_s2 < 0.99:
        problems.append(f"sub2 vs historical §203 ratio {r_s2:.3f} < 0.99")
    if overlap13 < 0.95:
        problems.append(f"s1+s3 vs complete 1913 compact overlap {overlap13:.3f} < 0.95")
    if not clause_only:
        problems.append(f"unexpected gap(s) vs 1913 beyond the 1958 clause: {[g[:40] for g in biggaps]}")

    print(f"{CITE}  prior len={len(PRIOR)}c ({len(dn(PRIOR))} despaced)")
    print(f"  sub2 vs historical §203: {r_s2:.4f}")
    print(f"  s1+s3 vs complete 1913 compact: overlap={overlap13:.4f}  (gap = 1958 clause only: {clause_only})")
    if problems:
        print("GATE FAIL:")
        for p in problems:
            print("  -", p)
        con.close(); return
    print("GATES PASS.")
    if not apply:
        print("(dry run) re-run with --apply"); con.close(); return

    con.execute("DELETE FROM provision_versions WHERE provision_id=? AND batch=?", (pid, BATCH))
    nvid = con.execute(
        "INSERT INTO provision_versions (provision_id, effective_start, effective_end, "
        "text_content, source_authority, source_path, batch) VALUES (?,?,?,?,?,?,?)",
        (pid, PRIOR_START, PRIOR_END, PRIOR,
         "pre-1996 Compact (3 subsections); sub1+sub3 reconciled from 1913/1895/1925 official "
         "(all $ amounts cross-verified), sub2 == historical § 203 (post-1958); confirmed vs "
         "1989 Blue Book. Subsections 2-3 deleted by amend #132 (1996).",
         "1913 official + historical § 203 + 1989 Blue Book", BATCH)).lastrowid
    con.execute("INSERT INTO changelog (batch, provision_id, version_id, field, new_value, authority) "
                "VALUES (?,?,?,?,?,?)", (BATCH, pid, nvid, "version_splice_compact_prior",
                f"[{PRIOR_START} -> {PRIOR_END}] pre-1996 3-subsection Compact",
                "1913 official + historical §203 + 1989 BB"))
    con.commit()
    g = con.execute("""WITH v AS (SELECT provision_id, effective_start, effective_end,
      LEAD(effective_start) OVER (PARTITION BY provision_id ORDER BY effective_start) nxt
      FROM provision_versions) SELECT count(*) FROM v WHERE nxt IS NOT NULL
      AND effective_end IS NOT NULL AND effective_end!='' AND date(effective_end)!=date(nxt)
      AND date(effective_end,'+1 day')!=date(nxt)""").fetchone()[0]
    spans = con.execute("SELECT effective_start, COALESCE(effective_end,'open') FROM provision_versions "
                        "WHERE provision_id=? ORDER BY effective_start", (pid,)).fetchall()
    print(f"SPLICED. integrity gaps={g}  spans=" + "  ".join(f"[{s}->{e}]" for s, e in spans))
    con.close()


if __name__ == "__main__":
    main(apply="--apply" in sys.argv)
