# Westlaw-receive manual queue (2026-05-16) — §6 dedup-blocked remainder

Batch westlaw-receive-2026-05-16: 506 docs, 442 auto-promoted; 64 ambiguous.
**18 resolved this round** — 12 surname clear-wins + 6 hand-adjudicated
(355 N.W.2d 798 Patzer/Allegree, 418 N.W.2d 789 Teevens/Montgomery,
356 N.W.2d 897 Bauer→9241, 79 N.D. 550 Littlejohn→12694).

**46 remaining, ALL §6 DUPLICATE-ROW PAIRS** (Task #21). Each cite's
two DB rows are the SAME opinion under two CL naming conventions (parties vs
"In re Estate of X"), row-to-row text jaccard shown (all ≥0.55). The Westlaw
doc matches BOTH rows, so promoting now would just fill one of a dup pair and
leave the duplicate. After §6 collapses each pair to a canonical oid, a receive
re-run auto-resolves these. Listed here with both oids for the §6 pass.

---

### 101 N.W.2d 557 — row-jaccard 0.95
- doc: In the Matter of ESTATE of George BERZEL, Deceased. Mary FISH, Appellant in District Court; Respondent, v. Mary BERZEL, 
- oid 6088: Fish v. Berzel | 1960-02-17 | 37469 ch
- oid 6089: In Re Berzel's Estate | 1960-02-17 | 37375 ch

### 102 N.W.2d 9 — row-jaccard 0.95
- doc: In re ESTATE of Gerald C. RYAN, also known as G. C. Ryan, Deceased. STATE of North Dakota and County of Grand Forks, App
- oid 6099: State v. First National Bank of Minneapolis | 1960-03-04 | 20711 ch
- oid 6100: In Re Ryan's Estate | 1960-03-04 | 20734 ch

### 119 N.W.2d 478 — row-jaccard 0.91
- doc: In the Matter of the ESTATE of Minnie GRAF, also known as Wilhelmina Graf, Deceased. Irvin BUCK and Herbert Lundin, and 
- oid 6251: Buck v. Buck | 1963-01-21 | 10005 ch
- oid 6252: In Re Graf's Estate | 1963-01-21 | 10099 ch

### 136 N.W.2d 823 — row-jaccard 0.92
- doc: In the Matter of the ESTATE of Brit TONNESON, Deceased. Helen K. EDWARDS et al., Petitioners and Appellants, v. Albert C
- oid 6445: Edwards v. Christenson | 1965-08-31 | 16326 ch
- oid 6446: In Re Tonneson's Estate | 1965-08-31 | 16467 ch

### 167 N.W.2d 537 — row-jaccard 0.88
- doc: Application of UNITED STATES CRUDE OIL PURCHASING CO. for an Order Designating a Depository with whom certain monies may
- oid 6777: Schwartz v. Lee | 1969-04-18 | 6609 ch
- oid 6778: Application of United States Crude Oil Purchas | 1969-04-18 | 6482 ch

### 175 N.W.2d 574 — row-jaccard 0.93
- doc: In the Matter of the ESTATE of Oscar A. BRUDEVIG, a/k/a Oscar Brudevig, Deceased. Eli LOE and Clara Loe, Petitioners, v.
- oid 6834: Loe v. Ovind | 1970-02-18 | 13370 ch
- oid 6835: In Re Estate of Brudevig | 1970-02-18 | 13312 ch

### 178 N.W.2d 738 — row-jaccard 0.92
- doc: ?
- oid 6861: In re Application for Disciplinary Action Agai | 1970-07-09 | 13493 ch
- oid 6862: In Re Peterson | 1970-07-09 | 13529 ch

### 191 N.W.2d 578 — row-jaccard 0.95
- doc: In the Matter of the ESTATE of Meta THOMPSON, Deceased. Herman GETZLAFF, Petitioner and Respondent, v. Elsie JOHNSON, Re
- oid 7014: Getzlaff v. Johnson | 1971-11-12 | 16540 ch
- oid 7015: In Re Estate of Thompson | 1971-11-12 | 16657 ch

### 214 N.W.2d 525 — row-jaccard 0.95
- doc: In the Matter of the ESTATE of Erick RASK, Deceased. Myrtle ATHEY, Appellant, v. Theodore RASK et al., Appellees. Civ. N
- oid 7244: Athey v. Rask | 1974-02-01 | 15609 ch
- oid 7245: In Re Estate of Rask | 1974-02-01 | 15725 ch

### 219 N.W.2d 815 — row-jaccard 0.94
- doc: In the Matter of the ESTATE of Edward M. BLANK, Deceased. Viola M. WOLFGRAM, Petitioner and Appellee, v. Julia L. BLANK 
- oid 7294: Wolfgram v. Blank | 1974-06-27 | 24741 ch
- oid 7295: In Re Estate of Blank | 1974-06-27 | 24934 ch

### 234 N.W.2d 867 — row-jaccard 0.91
- doc: ?
- oid 7465: In re Disciplinary Action against Fosaaen | 1975-10-23 | 10827 ch
- oid 7466: Matter of Fosaaen | 1975-10-23 | 10822 ch

### 250 N.W.2d 256 — row-jaccard 0.85
- doc: In the Interest (CUSTODY) OF J. O., a child. D. A. O., Plaintiff and Appellee, v. V. A. O., Defendant and Appellant. Civ
- oid 7650: O. v. O. | 1977-01-27 | 7322 ch
- oid 7651: In Interest [Custody] of Jo | 1977-01-27 | 7477 ch

### 271 N.W.2d 588 — row-jaccard 0.94
- doc: In the Matter of the Application for Disciplinary Action Against Thomas B. JELLIFF, a Member of the Bar of the State of 
- oid 7931: Disciplinary Board of Supreme Court v. Jelliff | 1978-11-02 | 18987 ch
- oid 7932: In Re Jelliff | 1978-11-02 | 19047 ch

### 283 N.W.2d 179 — row-jaccard 0.92
- doc: In the Matter of the APPLICATION FOR DISCIPLINARY ACTION AGAINST Robert N. LEE, a Member of the Bar of the State of Nort
- oid 8077: Disciplinary Board of Supreme Court v. Lee | 1979-08-06 | 17013 ch
- oid 8078: Matter of Application, Discip. Action Against  | 1979-08-06 | 17030 ch

### 289 N.W.2d 791 — row-jaccard 0.95
- doc: In the Interest of R. H., D. D. H., M. L. H., N. N. H., all minors under the age of 14 years. Roland WEISENBURGER, Direc
- oid 8168: Weisenburger v. R. H. | 1980-03-13 | 18273 ch
- oid 8169: In Interest of RH | 1980-03-13 | 18146 ch

### 299 N.W.2d 557 — row-jaccard 0.92
- doc: STATE of North Dakota ex rel. W. R. HJELLE, Highway Commissioner, Plaintiff and Appellee, v. A MOTOR VEHICLE DESCRIBED A
- oid 8284: State ex rel. Hjelle v. A Motor Vehicle Descri | 1980-11-03 | 17359 ch
- oid 8285: State Ex Rel. Hjelle v. a MOTOR VEHICLE, ETC. | 1980-11-03 | 17352 ch

### 301 N.W.2d 387 — row-jaccard 0.93
- doc: In the Interest of B. L., a Child. Robert G. HOY, Petitioner and Appellee, v. P. L. and P. L., Respondents, and B. L., R
- oid 8346: Hoy v. P. L. | 1981-01-23 | 18734 ch
- oid 8347: In Interest of BL | 1981-01-23 | 19012 ch

### 305 N.W.2d 38 — row-jaccard 0.92
- doc: In the Interest of R. R., a child. Lannon V. SERRANO, Petitioner and Appellee, v. R. R., child; F. R. and I. R., parents
- oid 8417: Serano v. R. R. | 1981-04-23 | 20015 ch
- oid 8418: In Interest of RR | 1981-04-23 | 20111 ch

### 311 N.W.2d 167 — row-jaccard 0.85
- doc: In the Matter of the Appeal From an Order of the State Board of Public School Education of the State of North Dakota App
- oid 8503: McKenzie County School District No. 1 v. State | 1981-10-15 | 8611 ch
- oid 8504: McKENZIE COUNTY, ETC. v. STATE BD. OF PUB., ET | 1981-10-15 | 8333 ch

### 335 N.W.2d 321 — row-jaccard 0.86
- doc: In the Interest of B.M., A Child. L.J. BERNHARDT, Director, Stark County Social Service Board, Petitioner and Appellee, 
- oid 8898: Bernhardt v. S.M. | 1983-06-24 | 7810 ch
- oid 8899: In Interest of BM | 1983-06-24 | 8015 ch

### 339 N.W.2d 567 — row-jaccard 0.60
- doc: STATE of North Dakota, Plaintiff and Appellee, v. Robert JENKINS, Defendant and Appellant. Cr. No. 936. |
- oid 8987: State v. Jenkins | 1983-10-31 | 1408 ch
- oid 8988: State v. Jenkins | 1983-10-31 | 1545 ch

### 356 N.W.2d 99 — row-jaccard 0.87
- doc: In the Matter of the Application of Milton ZIMBELMAN, d/b/a Bud’s Mobile Home Towing, Bismarck, North Dakota, for an Ext
- oid 9246: Barrett Mobile Home Transport, Inc. v. Zimbelm | 1984-10-23 | 10167 ch
- oid 9247: Application of Zimbelman | 1984-10-23 | 10271 ch

### 387 N.W.2d 499 — row-jaccard 0.87
- doc: In the Interest of V.J.R., A Child Julie VERNON, Petitioner and Appellee, v. K.R., a.k.a. K.L., Respondent and Appellant
- oid 9639: Vernon v. K.R. | 1986-05-15 | 9040 ch
- oid 9640: In Interest of VJR | 1986-05-15 | 9261 ch

### 395 N.W.2d 162 — row-jaccard 0.84
- doc: In the Matter of the ESTATE OF Guy KJORVESTAD, Sr., Deceased. In the Matter of the ESTATE OF Selma KJORVESTAD, Deceased.
- oid 9758: First Trust Co. of North Dakota v. Conway | 1986-10-28 | 7479 ch
- oid 9759: Matter of Estate of Kjorvestad | 1986-10-28 | 7664 ch

### 401 N.W.2d 694 — row-jaccard 0.96
- doc: In the Interest of D.J.H., a Child. S.H., Petitioner and Appellant, v. Mrs. Virginia PETERSEN, Program Supervisor, Child
- oid 9839: S.H. v. Petersen | 1987-03-02 | 41943 ch
- oid 9840: In Interest of DJH | 1987-03-02 | 42181 ch

### 413 N.W.2d 355 — row-jaccard 0.90
- doc: STATE of North Dakota ex rel. the INDUSTRIAL COMMISSION and the Board of University and School Lands, Plaintiff and Appe
- oid 9975: State ex rel. Industrial Commission v. Harlan | 1987-09-29 | 11062 ch
- oid 9976: STATE EX REL. INDUS. COM'N v. Harlan | 1987-09-29 | 11080 ch

### 417 N.W.2d 846 — row-jaccard 0.90
- doc: In the Interest of C.S., J.S. and A.S., Children. Bernard J. HAUGEN, Juvenile Supervisor for Ransom County, Petitioner a
- oid 10024: Haugen v. C.S. | 1988-01-12 | 11901 ch
- oid 10025: In Interest of CS | 1988-01-12 | 11876 ch

### 419 N.W.2d 915 — row-jaccard 0.88
- doc: In the Matter of the ESTATE OF Donald L. NELSON, Deceased. Norlin NELSON and Carol Roberts, Appellants, v. Ardella HEFTA
- oid 10060: Nelson v. Hefta | 1988-02-26 | 11282 ch
- oid 10061: Matter of Estate of Nelson | 1988-02-26 | 11453 ch

### 429 N.W.2d 425 — row-jaccard 0.92
- doc: J.S.S., as Guardian ad Litem of the minor child, G.M.F., also known as G.M.Z., DOB: xx/xx/xxxx, Petitioner, R.A.F., Peti
- oid 10209: R.A.F. v. P.M.Z. | 1988-09-20 | 13855 ch
- oid 10210: Jss v. Pmz | 1988-09-20 | 14023 ch

### 461 N.W.2d 105 — row-jaccard 0.95
- doc: In the Matter of the Application for DISCIPLINARY ACTION AGAINST the Honorable Bert L. WILSON, Judge of the District Cou
- oid 10725: Judicial Conduct Commission of the Supreme Cou | 1990-10-02 | 28862 ch
- oid 10726: Disciplinary Action Against Wilson | 1990-10-02 | 28721 ch

### 463 N.W.2d 918 — row-jaccard 0.87
- doc: In the Interest of D.R. and M.R., Children. Melody R.J. JENSEN, Petitioner and Appellee, v. DIRECTOR, CASS COUNTY SOCIAL
- oid 10779: Jensen v. Director, Cass County Social Service | 1990-12-17 | 6420 ch
- oid 10780: In Interest of DR | 1990-12-17 | 6508 ch

### 473 N.W.2d 439 — row-jaccard 0.91
- doc: In the Interest of C.J.A., a child. Robert R. EASTBURN, Petitioner and Appellee v. C.J.A., Respondent and Appellant W.A.
- oid 10935: Eastburn v. C.J.A. | 1991-07-31 | 11600 ch
- oid 10936: In Interest of CJA | 1991-07-31 | 11716 ch

### 496 N.W.2d 31 — row-jaccard 0.89
- doc: In the Interest of B.S., a Child. Rick SHIREY, Petitioner and Appellee, v. B.S., a child, and R.S. and B.S., his parents
- oid 11319: Shirey v. B.S. | 1993-02-23 | 10506 ch
- oid 11320: In Interest of BS | 1993-02-23 | 10666 ch

### 507 N.W.2d 900 — row-jaccard 0.86
- doc: In the Interest of C.L.L., a Child. Mark GADDIS, Petitioner and Appellee, v. C.L.L., Child, Respondent and Appellant, De
- oid 11516: Gaddis v. C.L.L. | 1993-11-10 | 5167 ch
- oid 11517: In the Interest of Cll | 1993-11-10 | 5306 ch

### 512 N.W.2d 441 — row-jaccard 0.88
- doc: In the Interest of T.M., a Child. James T. ODEGARD, State’s Attorney, Petitioner and Appellee, v. T.M., a Child, Respond
- oid 11583: Odegard v. T.M. | 1994-02-23 | 7400 ch
- oid 11584: In Interest of TM | 1994-02-23 | 7543 ch

### 515 N.W.2d 444 — row-jaccard 0.93
- doc: In the Matter of the Ward County State’s Attorney’s Inquiry Commenced on September 7, 1993, in re the CONTEMPT OF Valeri
- oid 11642: Grajedas v. Holum | 1994-04-20 | 24441 ch
- oid 11643: Matter of Contempt of Grajedas | 1994-04-20 | 23923 ch

### 524 N.W.2d 358 — row-jaccard 0.89
- doc: In the Matter of the GUARDIANSHIP and CONSERVATORSHIP of John, James III, and Jamie NORMAN, Minor Children, James E. Nor
- oid 11781: Mund v. Leingang | 1994-11-21 | 12927 ch
- oid 11782: Matter of Norman | 1994-11-21 | 13049 ch

### 531 N.W.2d 303 — row-jaccard 0.94
- doc: In the Interest of N.W., A Child. GOLDEN VALLEY COUNTY SOCIAL SERVICES, Petitioner and Appellee, v. P.G.S., Respondent, 
- oid 11908: Golden Valley County Social Services v. P.G.S. | 1995-05-09 | 19529 ch
- oid 11909: In Interest of NW | 1995-05-09 | 19640 ch

### 536 N.W.2d 367 — row-jaccard 0.87
- doc: James Howard PETERSON, Petitioner and Appellee, v. DIRECTOR, NORTH DAKOTA DEPARTMENT OF TRANSPORTATION, Respondent and A
- oid 11974: Peterson v. Director, North Dakota Department  | 1995-08-29 | 9063 ch
- oid 11975: Peterson v. DIR., ND DEPT. OF TRANSP. | 1995-08-29 | 9256 ch

### 552 N.W.2d 324 — row-jaccard 0.92
- doc: In the Interest of C.R.M., a child. Stephen R. DAWSON, Petitioner and Appellee, v. Hector MARTINEZ, Anna Martinez, and C
- oid 12246: Dawson v. Martinez | 1996-06-27 | 17394 ch
- oid 12247: In Interest of CRM | 1996-06-27 | 17443 ch

### 556 N.W.2d 657 — row-jaccard 0.93
- doc: In the Interest of P.L.P. WAYNE P., Petitioner and Appellee, v. P.L.P., Respondent and Appellant. Civil No. 960343. |
- oid 12327: Wayne v. P.L.P. | 1996-12-04 | 14889 ch
- oid 12328: Interest of Plp | 1996-12-04 | 15088 ch

### 557 N.W.2d 229 — row-jaccard 0.93
- doc: In the Interest of J.K.M., a Minor Child. Paul OGDEN, Petitioner and Appellant, v. J.K.M., Tim Moe, and Arliss Moe, Resp
- oid 12332: Ogden v. J.K.M. | 1996-12-20 | 20695 ch
- oid 12333: In Interest of JKM | 1996-12-20 | 20797 ch

### 85 N.W.2d 553 — row-jaccard 0.96
- doc: Matter of the Trust Created by the WILL of Charles Grandison REYNOLDS, Deceased. SECURITY-FIRST NATIONAL BANK OF LOS ANG
- oid 16322: Security-First National Bank of Los Angeles v. | 1957-10-21 | 35476 ch
- oid 16323: In Re Reynolds'will | 1957-10-21 | 35475 ch

### 86 N.W.2d 522 — row-jaccard 0.90
- doc: In the Matter of the ESTATE of D. G. HILLESLAND, Deceased. Wm. JOHNSON, as County Auditor of Burke County, North Dakota,
- oid 16428: Johnson v. Hillesland | 1957-11-27 | 8974 ch
- oid 16429: In Re Hillesland's Estate | 1957-11-27 | 9027 ch

### 87 N.W.2d 50 — row-jaccard 0.91
- doc: Matter of the GUARDIANSHIP of Bennie O. JOHNSON, Incompetent. Winifred Margaret JOHNSON, Petitioner and Appellee, v. Ine
- oid 16587: Johnson v. Kuchenbecker | 1957-12-20 | 9923 ch
- oid 16588: In Re Johnson's Guardianship | 1957-12-20 | 9938 ch

### 89 N.W.2d 112 — row-jaccard 0.91
- doc: In the Matter of the Estate of Katherine R. FOSTER, Deceased. Earl H. BOLINSKE and William A. Bolinske, Petitioners and 
- oid 16846: Bolinske v. Harris | 1958-03-31 | 11080 ch
- oid 16847: In Re Foster's Estate | 1958-03-31 | 11004 ch
