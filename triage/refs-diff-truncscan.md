# Corpus-wide PDF-oracle truncation sweep (7200 modern neutral opinions)

DB body vs `pdftotext` of the court PDF. Cutoff ratio < **0.85** → DB_TRUNCATED.

- **DB_CONTENT_BUG**: 403
- **DB_TRUNCATED**: 115
- **PDF_MISFILED**: 123
- **PDF_MISSING**: 163
- **PDF_UNREADABLE**: 11
- **OK**: 6385

## Ratio histogram (oracle-usable opinions)

| db/pdf ratio | count |
|--|--|
| 0.5–0.6 | 6 |
| 0.6–0.7 | 25 |
| 0.7–0.8 | 51 |
| 0.8–0.9 | 67 |
| 0.9–1.0 | 4708 |
| 1.0–1.1 | 1643 |

## DB_TRUNCATED (115) — worst ratio first

| oid | label | case_name | db/pdf words | missing | ratio |
|--|--|--|--|--|--|
| 17100 | 2017 ND 280 | State v. Sabot | 87/161 | 74 | 0.54 |
| 17101 | 2017 ND 276 | State v. De La Cruz | 103/185 | 82 | 0.557 |
| 17091 | 2017 ND 279 | Coppage v. State | 93/166 | 73 | 0.56 |
| 17057 | 2017 ND 237 | State v. Whetsel | 89/153 | 64 | 0.582 |
| 16938 | 2017 ND 131 | State v. Raphael | 97/166 | 69 | 0.584 |
| 16936 | 2017 ND 129 | State v. Smith | 102/171 | 69 | 0.596 |
| 17118 | 2018 ND 74 | State v. Redtomahawk | 96/157 | 61 | 0.611 |
| 13321 | 2000 ND 211 | Syvertson v. Malaktaris, et al. | 175/285 | 110 | 0.614 |
| 13176 | 2000 ND 99 | Peterson v. ND Workers Comp. Bureau | 107/174 | 67 | 0.615 |
| 17095 | 2017 ND 277 | Interest of Jane Doe (CONFIDENTIAL) | 118/191 | 73 | 0.618 |
| 17185 | 2018 ND 125 | State v. Ashford | 100/161 | 61 | 0.621 |
| 16935 | 2017 ND 114 | Buresh v. State | 110/175 | 65 | 0.629 |
| 17044 | 2017 ND 224 | State v. Duchaine | 102/162 | 60 | 0.63 |
| 17097 | 2017 ND 273 | State v. Palacio (consolidated w/20170181) | 146/231 | 85 | 0.632 |
| 13359 | 2001 ND 39 | Runge v. Runge | 139/218 | 79 | 0.638 |
| 14161 | 2004 ND 222 | State v. Bates | 119/183 | 64 | 0.65 |
| 16965 | 2017 ND 151 | Brown v. WSI | 138/212 | 74 | 0.651 |
| 17037 | 2017 ND 228 | Interest of Jane Doe (CONFIDENTIAL) | 124/189 | 65 | 0.656 |
| 17124 | 2018 ND 73 | State v. Mbulu | 127/189 | 62 | 0.672 |
| 17079 | 2017 ND 268 | State v. Montgomery | 115/171 | 56 | 0.673 |
| 17373 | 2019 ND 38 | State v. Cody | 134/199 | 65 | 0.673 |
| 17098 | 2017 ND 275 | State v. Vann | 163/242 | 79 | 0.674 |
| 16962 | 2017 ND 150 | Jasmann v. State | 133/197 | 64 | 0.675 |
| 14163 | 2004 ND 220 | City of Mandan v. Cordova | 153/224 | 71 | 0.683 |
| 17254 | 2018 ND 208 | State v. Kibble | 137/200 | 63 | 0.685 |
| 17155 | 2018 ND 104 | State v. Parks | 149/217 | 68 | 0.687 |
| 17368 | 2019 ND 34 | State v. Brakke | 122/177 | 55 | 0.689 |
| 17107 | 2018 ND 65 | Carroll v. Carroll (cross-reference w/20160190 | 143/207 | 64 | 0.691 |
| 17205 | 2018 ND 148 | RAD Development-Main Street, LLC v. Leunguen-K | 147/212 | 65 | 0.693 |
| 13691 | 2002 ND 195 | Greybull v. Harlan | 124/178 | 54 | 0.697 |
| 17266 | 2018 ND 209 | State v. Hussein | 180/258 | 78 | 0.698 |
| 17183 | 2018 ND 127 | Interest of Hoff | 140/200 | 60 | 0.7 |
| 14017 | 2004 ND 88 | State v. Helm | 171/244 | 73 | 0.701 |
| 17064 | 2017 ND 257 | State v. Hojian | 162/231 | 69 | 0.701 |
| 16929 | 2017 ND 115 | Jessop v. Levi | 139/198 | 59 | 0.702 |
| 13423 | 2001 ND 134 | Name Change of State Bar Board to Board of Law | 204/290 | 86 | 0.703 |
| 17314 | 2018 ND 252 | State v. Hebert | 196/279 | 83 | 0.703 |
| 17380 | 2019 ND 33 | Smith v. State | 146/206 | 60 | 0.709 |
| 17203 | 2018 ND 161 | Butts v. State | 145/204 | 59 | 0.711 |
| 17058 | 2017 ND 238 | Clark v. State | 163/228 | 65 | 0.715 |
| 17042 | 2017 ND 227 | State v. Osier (consolidated w/20170042)(cross | 204/285 | 81 | 0.716 |
| 16786 | 2016 ND 186 | State v. Washburn | 349/486 | 137 | 0.718 |
| 17043 | 2017 ND 226 | State v. Doornek (Consolidated w/20170027) | 255/355 | 100 | 0.718 |
| 17073 | 2017 ND 236 | Wisham v. State | 174/241 | 67 | 0.722 |
| 17375 | 2019 ND 40 | State v. Christie | 154/213 | 59 | 0.723 |
| 17393 | 2019 ND 60 | Miles v. Holznagel, et al. | 158/218 | 60 | 0.725 |
| 17280 | 2018 ND 220 | Tamba v. State | 189/260 | 71 | 0.727 |
| 17201 | 2018 ND 159 | Adoption of B.A.T. (CONFIDENTIAL) | 140/192 | 52 | 0.729 |
| 17210 | 2018 ND 163 | Odom v. State | 164/225 | 61 | 0.729 |
| 16930 | 2017 ND 116 | State v. Cox | 188/255 | 67 | 0.737 |
| 17202 | 2018 ND 150 | Oien v. State | 220/297 | 77 | 0.741 |
| 17339 | 2019 ND 2 | DeLong v. Shields, et al. | 180/243 | 63 | 0.741 |
| 17176 | 2018 ND 129 | Beeter v. State | 178/240 | 62 | 0.742 |
| 17271 | 2018 ND 230 | State v. Schlieve | 175/236 | 61 | 0.742 |
| 17041 | 2017 ND 225 | State v. Wagner | 199/268 | 69 | 0.743 |
| 17426 | 2019 ND 91 | State v. Johnson | 158/212 | 54 | 0.745 |
| 17297 | 2018 ND 249 | State v. Mejia | 167/223 | 56 | 0.749 |
| 17040 | 2017 ND 223 | Phillips v. State (cross-reference w/20130151) | 203/270 | 67 | 0.752 |
| 17072 | 2017 ND 235 | Wisham v. State | 164/218 | 54 | 0.752 |
| 17450 | 2019 ND 116 | Keller v. State | 187/247 | 60 | 0.757 |
| 17483 | 2019 ND 150 | Schatz v. N.D. Dep't of Transportation | 193/255 | 62 | 0.757 |
| 17573 | 2019 ND 232 | Interest of Hoff | 172/227 | 55 | 0.758 |
| 14246 | 2005 ND 94 | Glasow v. E.I. Dupont De Nemours and Company,  | 947/1246 | 299 | 0.76 |
| 14159 | 2004 ND 209 | State v. Whitetail | 178/233 | 55 | 0.764 |
| 17096 | 2017 ND 278 | State v. Todd | 235/307 | 72 | 0.765 |
| 14160 | 2004 ND 219 | Engwicht v. Lako | 208/271 | 63 | 0.768 |
| 17484 | 2019 ND 148 | Blackcloud v. State | 199/259 | 60 | 0.768 |
| 12747 | 1998 ND 171 | Albert 'Rusty' Kouba v. Febco, Inc., Robert D. | 1201/1557 | 356 | 0.771 |
| 17094 | 2017 ND 274 | State v. Anderson | 264/342 | 78 | 0.772 |
| 17431 | 2019 ND 93 | Horst v. Horst | 173/224 | 51 | 0.772 |
| 13587 | 2002 ND 105 | State v. Jackson    (Consolidated w/20010299) | 256/331 | 75 | 0.773 |
| 16987 | 2017 ND 180 | Ritter v. Ritter (Cross-reference w/20150202) | 199/256 | 57 | 0.777 |
| 17399 | 2019 ND 63 | Gonzales v. WSI | 175/225 | 50 | 0.778 |
| 16937 | 2017 ND 130 | Junas v.  N.D. Dep't of Transportation | 203/260 | 57 | 0.781 |
| 17452 | 2019 ND 120 | Curtiss v. State | 221/283 | 62 | 0.781 |
| 13523 | 2002 ND 21 | Mau, et al. v. National Union Fire Ins. Co. of | 276/351 | 75 | 0.786 |
| 15469 | 2010 ND 129 | State v. Everett | 269/342 | 73 | 0.787 |
| 17048 | 2017 ND 239 | State of North Dakota v. Abdirahman Pashir Sah | 260/329 | 69 | 0.79 |
| 17111 | 2018 ND 66 | Yahnke v. State | 215/270 | 55 | 0.796 |
| 17485 | 2019 ND 152 | State v. Taylor | 215/270 | 55 | 0.796 |
| 13289 | 2001 ND 1 | Petition for Change of Designation of Judgeshi | 496/622 | 126 | 0.797 |
| 13505 | 2002 ND 8 | City of Fargo v. Tipler | 293/367 | 74 | 0.798 |
| 17401 | 2019 ND 62 | White v. State | 261/325 | 64 | 0.803 |
| 17296 | 2018 ND 248 | Sorlie v. Sorlie | 203/252 | 49 | 0.806 |
| 17311 | 2018 ND 251 | Sabot v. State | 238/295 | 57 | 0.807 |
| 17337 | 2019 ND 6 | State v. Simundson | 255/316 | 61 | 0.807 |
| 17586 | 2020 ND 6 | McDougall, et al. v. AgCountry Farm Credit Ser | 3667/4535 | 868 | 0.809 |
| 18157 | 2023 ND 51 | Rath v. Rath, et al. | 1099/1358 | 259 | 0.809 |
| 17063 | 2017 ND 258 | State v. Toure (consolidated w/20170039 & 2017 | 298/368 | 70 | 0.81 |
| 17453 | 2019 ND 119 | Lavallie v. State | 218/269 | 51 | 0.81 |
| 17346 | 2019 ND 15 | Kieson v. Kieson | 244/300 | 56 | 0.813 |
| 13309 | 2001 ND 18 | Barrera v. State                             ( | 310/379 | 69 | 0.818 |
| 17451 | 2019 ND 121 | Ali v. State | 257/314 | 57 | 0.818 |
| 13077 | 2000 ND 19 | Strom-Sell v. Council for Concerned Citizens,  | 317/387 | 70 | 0.819 |
| 13472 | 2001 ND 180 | Chadwick v. N.D. Dept. of Transportation | 299/365 | 66 | 0.819 |
| 16518 | 2015 ND 175 | Gonzalez v. State (consolidated w/20150051) | 404/493 | 89 | 0.819 |
| 13065 | 2000 ND 8 | GreyBull v. State   (Cross-reference w/970216) | 350/427 | 77 | 0.82 |
| 13562 | 2002 ND 54 | Petition to Change Resident Chambers for Distr | 1467/1784 | 317 | 0.822 |
| 17152 | 2018 ND 103 | Interest of K.S.D. and J.S.D. | 352/428 | 76 | 0.822 |
| 15657 | 2011 ND 58 | Nelson v. State | 285/346 | 61 | 0.824 |
| 17264 | 2018 ND 215 | State v. Seidel | 249/301 | 52 | 0.827 |
| 17336 | 2019 ND 4 | Schwab v. State | 268/324 | 56 | 0.827 |
| 13132 | 2000 ND 84 | Bank Center First v. Kostelecky | 381/460 | 79 | 0.828 |
| 17340 | 2019 ND 5 | Lunde v. Paulson | 242/292 | 50 | 0.829 |
| 17204 | 2018 ND 149 | Matthews v. State | 319/383 | 64 | 0.833 |
| 17390 | 2019 ND 55 | In the Matter of Aaron J. Kulink | 241/289 | 48 | 0.834 |
| 13126 | 2000 ND 81 | State v. Reamann | 313/375 | 62 | 0.835 |
| 14162 | 2004 ND 221 | State v. Ernst | 309/370 | 61 | 0.835 |
| 17209 | 2018 ND 154 | Chase v. State | 283/339 | 56 | 0.835 |
| 14380 | 2005 ND 221 | Petition to Change Resident Chambers from Stan | 2107/2521 | 414 | 0.836 |
| 13093 | 2000 ND 35 | Judicial Vacancy in Judgeship No. 2, NE Centra | 601/717 | 116 | 0.838 |
| 16787 | 2016 ND 183 | State v. Kordonowy | 402/479 | 77 | 0.839 |
| 13203 | 2000 ND 141 | Disciplinary Board v. Keller | 577/685 | 108 | 0.842 |
| 16788 | 2016 ND 182 | State v. Birchfield | 446/526 | 80 | 0.848 |
| 17454 | 2019 ND 117 | State v. Johnson | 343/404 | 61 | 0.849 |

## DB_CONTENT_BUG (403) — DB body is the wrong/contaminated case

| oid | label | case_name | label_in_body | db/pdf words |
|--|--|--|--|--|
| 12782 | 1998 ND 206 | In the Matter of a Disciplinary Action Against | False | 255/664 |
| 19532 | 2020 ND 246 | State v. Richardson | False | 180/364 |
| 16971 | 2017 ND 164 | Interest of A.F.L. (CONFIDENTIAL) | True | 141/203 |
| 17160 | 2018 ND 106 | Interest of R.C. (CONFIDENTIAL) | True | 177/252 |
| 17159 | 2018 ND 107 | Interest of F.M.G. (CONFIDENTIAL) | True | 145/205 |
| 19750 | 2023 ND 165 | Buller v. Buller | False | 222/311 |
| 17258 | 2018 ND 207 | Interest of I.N. (CONFIDENTIAL) | True | 173/241 |
| 17319 | 2018 ND 250 | Interest of D.V.A. (Confidential) | True | 163/224 |
| 17275 | 2018 ND 222 | Interest of S.R. (CONFIDENTIAL) | True | 162/221 |
| 17175 | 2018 ND 126 | Interest of K.B. (CONFIDENTIAL) | True | 200/271 |
| 17088 | 2017 ND 281 | Interest of M.R. (CONFIDENTIAL) (consolidated  | True | 303/408 |
| 17163 | 2018 ND 105 | Interest of A.H. (CONFIDENTIAL) | True | 186/249 |
| 17241 | 2018 ND 193 | Interest of E.P. (CONFIDENTIAL) | True | 180/241 |
| 16974 | 2017 ND 166 | Interest of M.M.C. (CONFIDENTIAL)(consolidated | True | 405/526 |
| 20064 | 2024 ND 89 | State v. Eggl | False | 220/281 |
| 20066 | 2024 ND 90 | Rivera-Rieffel v. State | False | 182/232 |
| 20068 | 2024 ND 92 | Interest of S.M.F. | False | 309/393 |
| 17238 | 2018 ND 190 | Interest of A.T. (Confidential) | True | 238/299 |
| 17398 | 2019 ND 61 | Interest of C.H. (CONFIDENTIAL) (CONSOLIDATED  | True | 353/434 |
| 17419 | 2019 ND 88 | Interest of D.M.H. (CONFIDENTIAL) | True | 308/378 |
| 17345 | 2019 ND 8 | Interest of D.M.W. (CONFIDENTIAL) | True | 325/389 |
| 19533 | 2020 ND 247 | State v. Conry | False | 1324/1533 |
| 17433 | 2019 ND 92 | Interest of C.D.C. (CONFIDENTIAL) | True | 484/541 |
| 14083 | 2004 ND 159 | Interest of J.S.   (CONFIDENTIAL) | True | 672/747 |
| 17127 | 2018 ND 76 | Interest of T.S.C. (CONFIDENTIAL)(Consolidated | True | 1005/1113 |
| 13119 | 2000 ND 63 | Roe v. Rothe-Seeger, et al. | True | 942/1036 |
| 13195 | 2000 ND 130 | Interest of A.R.         (CONFIDENTIAL) | True | 773/850 |
| 14334 | 2005 ND 156 | Interest of K.G.          (Confidential) | True | 800/880 |
| 15565 | 2011 ND 9 | Matter of T.O. (CONFIDENTIAL) (cross-reference | True | 723/795 |
| 14352 | 2005 ND 177 | Interest of L.D.M.   (CONFIDENTIAL) | True | 960/1045 |
| 17038 | 2017 ND 230 | Interest of F.S. (CONFIDENTIAL) (consolidated  | True | 1031/1122 |
| 13887 | 2003 ND 162 | Interest of R.F.     (CONFIDENTIAL) | True | 436/473 |
| 15460 | 2010 ND 135 | Interest of M.W.      (CONFIDENTIAL) | True | 934/1011 |
| 13503 | 2002 ND 7 | Interest of J.S.  (CONFIDENTIAL)               | True | 968/1044 |
| 14373 | 2005 ND 201 | Interest of P.B. (CONFIDENTIAL) | True | 1056/1131 |
| 13078 | 2000 ND 27 | Interest of C.J.C.      (CONFIDENTIAL) | True | 1012/1081 |
| 15178 | 2009 ND 75 | Matter of D.V.A. (CONFIDENTIAL) | True | 1239/1322 |
| 13234 | 2000 ND 174 | Interest of E.T.         (CONFIDENTIAL) | True | 1119/1190 |
| 14277 | 2005 ND 130 | Interest of C.H.    (CONFIDENTIAL) | True | 1080/1149 |
| 13010 | 1999 ND 195 | Interest of A.M., et al.           (CONFIDENTI | True | 1351/1436 |
| 13860 | 2003 ND 138 | Interest of J.S.        (CONFIDENTIAL)         | True | 1126/1194 |
| 13931 | 2004 ND 8 | Interest of W.O.   (CONFIDENTIAL) (cross-refer | True | 1407/1487 |
| 14319 | 2005 ND 138 | Interest of B.J.K.          (Confidential) | True | 1912/2018 |
| 14549 | 2006 ND 143 | Interest of J.S. (CONFIDENTIAL) | True | 1351/1427 |
| 14961 | 2008 ND 89 | Interest of I.B.A. and C.B.A. (CONFIDENTIAL)(C | True | 1924/2032 |
| 13213 | 2000 ND 161 | Interest of S.F., et al.   (CONFIDENTIAL) | True | 1594/1681 |
| 14386 | 2005 ND 216 | Interest of A.B., et al.  (CONFIDENTIAL) | True | 972/1024 |
| 15572 | 2011 ND 25 | Interest of L.D.M. (CONFIDENTIAL) | True | 1230/1296 |
| 17321 | 2018 ND 257 | Interest of A.L.E. (CONFIDENTIAL) | True | 1684/1775 |
| 13654 | 2002 ND 154 | Interest of R.O.      (CONFIDENTIAL) | True | 1736/1828 |
| 17018 | 2017 ND 208 | Interest of M.S. (CONFIDENTIAL)  (cross-refere | True | 1089/1145 |
| 13323 | 2001 ND 37 | Interest of C.H., et al.     (CONFIDENTIAL) | True | 2737/2871 |
| 13546 | 2002 ND 50 | Interest of J.D.    (CONFIDENTIAL) | True | 1947/2040 |
| 15720 | 2011 ND 189 | Interest of A.L.(CONFIDENTIAL) (consolidated w | True | 1935/2028 |
| 13592 | 2002 ND 111 | Interest of R.K.    (CONFIDENTIAL) | True | 1783/1867 |
| 15496 | 2010 ND 172 | Interest of S.L.W. (CONFIDENTIAL) | True | 1561/1634 |
| 16740 | 2016 ND 136 | Interest of G.A.S. (CONFIDENTIAL) | True | 1642/1719 |
| 16766 | 2016 ND 156 | Interest of D.W. (CONFIDENTIAL) | True | 1817/1903 |
| 14926 | 2008 ND 51 | Interest of B.B.  (CONFIDENTIAL)  (Cross-ref.  | True | 2242/2345 |
| 15973 | 2012 ND 256 | Interest of J.N. (Confidential) (consolidated  | True | 1625/1700 |
| 19693 | 2022 ND 236 | Interest of J.J.G., M.K.G. & O.J.G. (CONFIDENT | False | 1931/2019 |
| 13570 | 2002 ND 78 | Interest of J.R. and L.R.   (CONFIDENTIAL) | True | 2511/2623 |
| 13976 | 2004 ND 57 | Interest of D.V.A.  (CONFIDENTIAL) | True | 1808/1889 |
| 16396 | 2015 ND 12 | Interest of L.B. (CONFIDENTIAL) | True | 1386/1448 |
| 15592 | 2011 ND 51 | Interest of L.T. (CONFIDENTIAL) | True | 1420/1482 |
| 16347 | 2014 ND 172 | Interest of T.R.C. (CONFIDENTIAL) | True | 1562/1630 |
| 13729 | 2003 ND 25 | Interest of T.M.H.           (CONFIDENTIAL) | True | 1434/1496 |
| 13487 | 2001 ND 205 | Interest of M.C.H.    (CONFIDENTIAL)           | True | 1801/1876 |
| 15285 | 2009 ND 174 | State v. O'Toole | True | 2055/2141 |
| 17232 | 2018 ND 176 | Interest of G.L. (CONFIDENTIAL) | True | 1989/2072 |
| 17449 | 2019 ND 115 | Interest of T.A.G. (CONFIDENTIAL) | True | 1426/1485 |
| 17443 | 2019 ND 110 | Interest of K.S.D. (CONFIDENTIAL) (consolidate | True | 1948/2028 |
| 15689 | 2011 ND 142 | Interest of D.J.  (CONFIDENTIAL) | True | 2790/2901 |
| 14125 | 2004 ND 202 | Interest of E.R.  (CONFIDENTIAL) | True | 1914/1987 |
| 14051 | 2004 ND 138 | Interest of T.T.   (CONFIDENTIAL) | True | 3294/3416 |
| 14465 | 2006 ND 47 | Interest of F.F., et al.   (CONFIDENTIAL) | True | 2988/3099 |
| 16362 | 2014 ND 196 | Interest of J.A.H. (Consolidated w/20140146) | True | 2287/2373 |
| 17174 | 2018 ND 139 | Interest of B.A.K. (CONFIDENTIAL) | True | 1667/1729 |
| 13479 | 2001 ND 203 | Interest of D.P.   (Confidential) | True | 2180/2259 |
| 15597 | 2011 ND 52 | Interest of G.L.D. (CONFIDENTIAL) | True | 2224/2304 |
| 14252 | 2005 ND 102 | Interest of R.F.   (CONFIDENTIAL)              | True | 1990/2061 |
| 14383 | 2005 ND 220 | Interest of L.B.B.  (CON. W/20050253 & 2005025 | True | 1873/1939 |
| 14508 | 2006 ND 103 | Interest of K.L.    (Confidential) | True | 1960/2029 |
| 15479 | 2010 ND 149 | S.H.B. v. T.A.H. (CONFIDENTIAL) | False | 1723/1783 |
| 16142 | 2013 ND 205 | Interest of C.N. (CONFIDENTIAL) | True | 1993/2064 |
| 17055 | 2017 ND 247 | Interest of B.A.C. (CONFIDENTIAL) | True | 2235/2314 |
| 13432 | 2001 ND 142 | Interest of H.G.        (CONFIDENTIAL) | True | 2441/2523 |
| 14267 | 2005 ND 116 | Interest of D.A.     (CONFIDENTIAL) | True | 1969/2036 |
| 14738 | 2007 ND 62 | Interest of D.M., a child          CONFIDENTIA | True | 2839/2937 |
| 15913 | 2012 ND 168 | Matter of S.E. (Confidential) | True | 2370/2452 |
| 15998 | 2013 ND 26 | Matter of J.G. (CONFIDENTIAL) (cross-ref. w/20 | True | 1964/2030 |
| 14621 | 2006 ND 188 | Interest of B.L.S.            (Confidential) | True | 2384/2464 |
| 15634 | 2011 ND 120 | In the Interest of L.T., a child (CONFIDENTIAL | True | 3246/3352 |
| 13303 | 2001 ND 10 | Interest of J.S. (CONFIDENTIAL-M.H.) | True | 2395/2472 |
| 13338 | 2001 ND 59 | Interest of A.L. and J.L.     (CONSOLIDATED w/ | True | 3208/3311 |
| 13466 | 2001 ND 183 | Interest of D.R., et al.  (CONFIDENTIAL)(Conso | True | 2675/2762 |
| 13218 | 2000 ND 158 | Interest of  S.J.F.   (CONFIDENTIAL) (CONSOLID | True | 2486/2562 |
| 12978 | 1999 ND 182 | Interest of J.K.  (CONFIDENTIAL) | True | 2766/2850 |
| 14633 | 2006 ND 210 | Interest of T.A., et al.  (CONFIDENTIAL) | True | 2407/2480 |
| 16211 | 2014 ND 32 | Interest of G.R. (Confidential) | True | 2871/2958 |
| 13388 | 2001 ND 111 | Interest of A.B.         (CONFIDENTIAL) | True | 1513/1556 |
| 16036 | 2013 ND 75 | Interest of S.R.B. (Confidential) | True | 2762/2842 |
| 17342 | 2019 ND 12 | Interest of E.S. (CONFIDENTIAL) | True | 2198/2261 |
| 20072 | 2024 ND 96 | State v. Rangel | False | 1414/1455 |
| 13254 | 2000 ND 208 | Interest of W.E., et al. (CONFIDENTIAL)(Consol | True | 3443/3537 |
| 13657 | 2002 ND 164 | Interest of K.S. and A.S.  (CONFIDENTIAL) | True | 4054/4167 |
| 15980 | 2013 ND 11 | Interest of J.M. (CONFIDENTIAL) | True | 2339/2403 |
| 17102 | 2017 ND 289 | Interest of K.S.D. (CONFIDENTIAL) (consolidate | True | 4514/4637 |
| 13608 | 2002 ND 132 | Interest of D.Z.   (CONFIDENTIAL) | True | 2397/2461 |
| 14888 | 2008 ND 9 | Interest of J.S., et al.    (CONFIDENTIAL) | True | 2848/2924 |
| 14958 | 2008 ND 86 | Interest of T.E.  (Confidential) | True | 2947/3025 |
| 15179 | 2009 ND 71 | Ude v. State (Consolidated w/20080304, 2008030 | True | 2139/2195 |
| 15641 | 2011 ND 115 | G.K.T. v. T.L.T., et al. (CONFIDENTIAL) | True | 2525/2592 |
| 19393 | 2019 ND 247 | Interest of G.T. (CONFIDENTIAL)(consol. w/2019 | True | 368/378 |
| 13169 | 2000 ND 101 | State ex rel. D.D., et al. v. G.K.    (CONFIDE | True | 1074/1102 |
| 13430 | 2001 ND 143 | Interest of N.H., et al.   (CONFIDENTIAL) | True | 3198/3280 |
| 13816 | 2003 ND 101 | Interest of I.K.   (CONFIDENTIAL) | True | 3058/3138 |
| 15785 | 2012 ND 12 | Interest of W.J.C.A. (Confidential) | True | 2577/2642 |
| 15968 | 2012 ND 261 | Matter of M.D. (CONFIDENTIAL)(cross-ref. w/200 | True | 2740/2810 |
| 13686 | 2002 ND 188 | Interest of D.Q., et al.   (Confidential) (Con | True | 4152/4255 |
| 14400 | 2006 ND 22 | Interest of B.V.         (CONFIDENTIAL) | True | 2891/2961 |
| 14640 | 2006 ND 218 | Interest of B.L.S.          (Confidential) | True | 3231/3310 |
| 16029 | 2013 ND 61 | Interest of M.H.P. (CONFIDENTIAL) | True | 2463/2523 |
| 12950 | 1999 ND 152 | Interest of T.J.K.           (Confidential) | True | 3069/3140 |
| 13408 | 2001 ND 127 | Interest of T.K. (Consolidated w/20000329) | True | 3299/3378 |
| 14046 | 2004 ND 120 | T.E.J. v. T.S., et al.    (CONFIDENTIAL) | True | 3029/3099 |
| 15481 | 2010 ND 157 | Interest of M.G. (CONFIDENTIAL) | True | 2771/2836 |
| 13102 | 2000 ND 46 | Interest of S.R.A.        (CONFIDENTIAL) | True | 1299/1328 |
| 13281 | 2000 ND 222 | Interest of C.R.H.      (CONFIDENTIAL) | True | 2850/2915 |
| 15208 | 2009 ND 101 | Matter of R. A. S.   (Confidential) | True | 2821/2883 |
| 13029 | 1999 ND 216 | Interest of D.F.G. and E.K.B. (CONFIDENTIAL) | True | 3278/3349 |
| 13701 | 2002 ND 201 | Wanner v. N.D. Workers Comp. Bureau | False | 7613/7775 |
| 14785 | 2007 ND 111 | Interest of J.C.            (Confidential) | True | 3147/3215 |
| 14852 | 2007 ND 186 | Interest of B.D.K. (CONFIDENTIAL) | True | 3211/3279 |
| 15429 | 2010 ND 103 | Interest of D.H. (CONFIDENTIAL) | True | 4411/4507 |
| 17246 | 2018 ND 201 | Interest of D.D. (CONFIDENTIAL) | True | 3074/3139 |
| 13951 | 2004 ND 25 | Interest of J.P. and D.P. (CONFIDENTIAL)(Conso | True | 4078/4163 |
| 14914 | 2008 ND 39 | Interest of R.P.  (CONFIDENTIAL) | True | 3553/3626 |
| 14996 | 2008 ND 107 | B.L.L., et al. v. W.D.C.    (CONFIDENTIAL) | True | 2205/2249 |
| 15483 | 2010 ND 154 | Matter of A.M.W.   (CONFIDENTIAL) | True | 2864/2922 |
| 14410 | 2006 ND 19 | Interest of M.B., et al.     (CONFIDENTIAL) | True | 3991/4068 |
| 15365 | 2010 ND 46 | Interest of K.J., et al.   (CONFIDENTIAL) (con | True | 3333/3396 |
| 15643 | 2011 ND 119 | Interest of R.A.  (CONFIDENTIAL) | True | 4684/4775 |
| 16692 | 2016 ND 67 | Matter of K.J.C. (Confidential) | True | 3584/3653 |
| 19776 | 2023 ND 19 | Interest of G.V. (CONFIDENTIAL) (consolidated  | False | 2783/2836 |
| 15218 | 2009 ND 116 | Interest of A.B.    (CONFIDENTIAL) | True | 3921/3991 |
| 15967 | 2012 ND 253 | D.E. v. K.F., et al. (CONFIDENTIAL) | True | 3588/3649 |
| 16679 | 2016 ND 57 | Martire' v. Martire' (cross ref 20110253, 2011 | True | 3556/3614 |
| 14476 | 2006 ND 55 | Sisk v. Sisk | False | 7893/8014 |
| 15405 | 2010 ND 84 | Interest of A.R. (CONFIDENTIAL) | True | 3036/3079 |
| 15317 | 2009 ND 218 | Interest of W.K. (Confidential) | True | 4592/4655 |
| 15750 | 2011 ND 231 | Matter of J.T.N.  (CONFIDENTIAL) | True | 6631/6726 |
| 17219 | 2018 ND 165 | Interest of J.J.T. (CONFIDENTIAL) | True | 4196/4255 |
| 15310 | 2009 ND 209 | Matter of T.O.  (CONFIDENTIAL) | True | 2210/2240 |
| 13808 | 2003 ND 88 | K.L.B., et al. v. S.B.   (CONFIDENTIAL) | True | 1562/1581 |
| 14066 | 2004 ND 142 | Interest of T.J.L.    (CONFIDENTIAL) | True | 1529/1546 |
| 15079 | 2008 ND 208 | Matter of M.D.  (CONFIDENTIAL) | True | 2784/2814 |
| 15168 | 2009 ND 43 | Interest of J.S.L.   (CONFIDENTIAL) | True | 6864/6938 |
| 15941 | 2012 ND 197 | Martire' v. Martire' | True | 7391/7471 |
| 16270 | 2014 ND 82 | Matter of G.K.G. (Confidential) | True | 2742/2772 |
| 14198 | 2005 ND 54 | Interest of R.F.          (CONFIDENTIAL) | True | 3270/3302 |
| 14503 | 2006 ND 96 | Interest of J.M.           (CONFIDENTIAL) | True | 3250/3284 |
| 15202 | 2009 ND 104 | Matter of A.M.       (CONFIDENTIAL) | True | 2660/2686 |
| 15513 | 2010 ND 195 | R.F. v. M.M., et al. (CONFIDENTIAL) | True | 4001/4040 |
| 19381 | 2019 ND 235 | Interest of G.D-M. (CONFIDENTIAL) (consol. w/  | True | 306/309 |
| 19612 | 2021 ND 202 | Interest of J.M. (CONFIDENTIAL) (consolidated  | True | 498/503 |
| 19828 | 2023 ND 73 | Interest of K.B. (CONFIDENTIAL) | True | 196/198 |
| 13320 | 2001 ND 33 | K.L.G v. S.L.N.      (CONFIDENTIAL) | True | 2657/2682 |
| 13973 | 2004 ND 52 | Interest of K.P.    (CONFIDENTIAL)             | True | 4216/4253 |
| 15007 | 2008 ND 131 | Interest of K.L. and M.S. (CONFIDENTIAL)(conso | True | 4832/4878 |
| 15083 | 2008 ND 194 | P.A. v. A.H.O.   (CONFIDENTIAL) | True | 3176/3204 |
| 16566 | 2015 ND 207 | Matter of J.G. (CONFIDENTIAL)(cross-reference  | True | 4836/4880 |
| 19786 | 2023 ND 199 | Interest of E.E.J.-C. (Confidential) | True | 232/234 |
| 19825 | 2023 ND 60 | Interest of D.H. (CONFIDENTIAL) | True | 209/211 |
| 13362 | 2001 ND 83 | Interest of C.R.C. (CONFIDENTIAL) | True | 5285/5330 |
| 14187 | 2005 ND 39 | Interest of D.P.O.                       (Cros | True | 2221/2240 |
| 14360 | 2005 ND 180 | L.C.V. v. D.E.G. (CONFIDENTIAL) | True | 3075/3099 |
| 19715 | 2023 ND 107 | Interest of T.H.P.B. (CONFIDENTIAL) | True | 236/238 |
| 19822 | 2023 ND 52 | Matter of O.H.W. (CONFIDENTIAL) | True | 241/243 |
| 14833 | 2007 ND 166 | Interest of T. E.  (Confidential) | True | 3425/3449 |
| 15402 | 2010 ND 66 | State v. Loh    (CONSOLIDATED W/20090099) | True | 3257/3280 |
| 15304 | 2009 ND 194 | Matter of O.H.W. (Confidential) | True | 2594/2613 |
| 19808 | 2023 ND 238 | Interest of J.M.M. (CONFIDENTIAL) | True | 288/290 |
| 15160 | 2009 ND 46 | Interest of J.K.      (Confidential) | True | 4197/4224 |
| 15468 | 2010 ND 131 | Interest of C.H. (Confidential) | True | 4204/4231 |
| 17950 | 2022 ND 24 | Divide County v. Stateline Service, et al. (co | False | 1060/1066 |
| 18314 | 1999 ND 100 | Interest of D.S.A.  (CONFIDENTIAL - M.H.) | True | 167/168 |
| 18552 | 2006 ND 130 | Interest of K.G. (Confidential) | True | 179/180 |
| 18880 | 2012 ND 200 | Interest of B.K. (CONFIDENTIAL) | True | 175/176 |
| 19401 | 2019 ND 255 | Interest of K.V. (CONFIDENTIAL) | True | 3302/3323 |
| 19574 | 2020 ND 84 | Interest of F.M.G. (Confidential) | True | 163/164 |
| 19597 | 2021 ND 156 | Interest of G.J.E.P. (CONFIDENTIAL) (consolida | True | 311/313 |
| 19610 | 2021 ND 197 | Interest of S.A. (CONFIDENTIAL) (consolidated  | True | 338/340 |
| 19615 | 2021 ND 211 | Interest of C.E. (CONFIDENTIAL) | True | 478/481 |
| 19632 | 2021 ND 67 | Interest of A.G. (CONFIDENTIAL) | True | 329/331 |
| 19770 | 2023 ND 184 | Interest of P.R.-K. (CONFIDENTIAL)(consolidate | True | 355/357 |
| 13350 | 2001 ND 68 | Interest of M.S.  (CONFIDENTIAL) | True | 3660/3679 |
| 14678 | 2006 ND 258 | Interest of R.F. (CONFIDENTIAL) | True | 188/189 |
| 18418 | 2002 ND 123 | Interest of N.S.    (CONFIDENTIAL) | True | 204/205 |
| 18486 | 2004 ND 182 | Interest of K.G.   (CONFIDENTIAL) | True | 219/220 |
| 18571 | 2006 ND 252 | Interest of C.L.           (Confidential) | True | 188/189 |
| 18756 | 2010 ND 190 | Matter of M.D. (CONFIDENTIAL) | True | 185/186 |
| 18749 | 2010 ND 178 | Interest of B.B. (CONFIDENTIAL) | True | 212/213 |
| 18799 | 2011 ND 105 | Matter of J.M. (CONFIDENTIAL) | True | 213/214 |
| 18845 | 2011 ND 73 | Matter of J.G. (CONFIDENTIAL) | True | 196/197 |
| 18868 | 2012 ND 132 | Matter of D.A. (CONFIDENTIAL) | True | 192/193 |
| 18931 | 2012 ND 94 | Matter of C.S. (CONFIDENTIAL) | True | 204/205 |
| 18960 | 2013 ND 206 | Interest of H.D. (Confidential) | True | 184/185 |
| 19007 | 2014 ND 118 | Interest of J.M. (CONFIDENTIAL)(cross-ref. w/2 | True | 199/200 |
| 19069 | 2015 ND 165 | Interest of C.S. (CONFIDENTIAL) (cross-ref 201 | True | 219/220 |
| 19074 | 2015 ND 186 | Interest of B.E. (CONFIDENTIAL) | True | 220/221 |
| 19077 | 2015 ND 2 | Interest of E.L. (CONFIDENTIAL) | True | 198/199 |
| 19091 | 2015 ND 245 | Interest of B.K. (CONFIDENTIAL) | True | 197/198 |
| 19092 | 2015 ND 246 | Interest of W.M. (Confidential) | True | 203/204 |
| 19096 | 2015 ND 258 | In the Interest of A.S. (CONFIDENTIAL) | True | 208/209 |
| 19135 | 2015 ND 84 | Interest of D.V.A. (CONFIDENTIAL) (cross-ref 2 | True | 197/198 |
| 19136 | 2015 ND 85 | Interest of M.T.  (CONFIDENTIAL) | True | 208/209 |
| 19140 | 2015 ND 91 | Interest of T.J.S. (CONFIDENTIAL)(consolidated | True | 219/220 |
| 19186 | 2016 ND 239 | Interest of R.F. (CONFIDENTIAL) | True | 208/209 |
| 19341 | 2018 ND 90 | Interest of R.F. (CONFIDENTIAL) | True | 197/198 |
| 19399 | 2019 ND 253 | Interest of D.V.A. (Confidential) | True | 221/222 |
| 19558 | 2020 ND 44 | Interest of E.K. (CONFIDENTIAL) | True | 204/205 |
| 19565 | 2020 ND 60 | Interest of R.S. (CONFIDENTIAL) | True | 186/187 |
| 19575 | 2020 ND 86 | Interest of A.T. (CONFIDENTIAL) | True | 219/220 |
| 14230 | 2005 ND 64 | Interest of A.M.S. (Consolidated w/20040269 &  | True | 2237/2247 |
| 15492 | 2010 ND 163 | Matter of A.M. (CONFIDENTIAL) | True | 4068/4083 |
| 18397 | 2001 ND 25 | Interest of J.S. (CONFIDENTIAL-M.H.) | True | 264/265 |
| 18487 | 2004 ND 183 | Interest of R.R.  (CONFIDENTIAL) | True | 262/263 |
| 18488 | 2004 ND 197 | R.R. v. G. H., et al.  (CONFIDENTIAL) (Cross-R | True | 256/257 |
| 18514 | 2005 ND 181 | Interest of C.R. and S.R.  (CONFIDENTIAL) | True | 235/236 |
| 18515 | 2005 ND 182 | Interest of L.J.   (CONFIDENTIAL) | True | 245/246 |
| 18518 | 2005 ND 185 | Interest of E.I., Jr.       (Confidential) | True | 228/229 |
| 18543 | 2005 ND 78 | Interest of B.M., et al.  (CONFIDENTIAL) | True | 282/283 |
| 18592 | 2007 ND 1 | Interest of J.H. (CONFIDENTIAL) | True | 228/229 |
| 18642 | 2007 ND 95 | Interest of C.R., a child       CONFIDENTIAL | True | 256/257 |
| 18699 | 2009 ND 185 | Matter of E.W.F.      (CONFIDENTIAL) | True | 249/250 |
| 18687 | 2009 ND 100 | Interest of I.W. & D.A.    (CONFIDENTIAL) | True | 247/248 |
| 18758 | 2010 ND 192 | Interest of D.V.A.   (CONFIDENTIAL) (Cross-Ref | True | 269/270 |
| 18803 | 2011 ND 129 | Interest of A.S. (CONFIDENTIAL) (CONSOL. W/ 20 | True | 249/250 |
| 18831 | 2011 ND 220 | Interest of J.G. & D.M. (CONFIDENTIAL) | True | 247/248 |
| 18850 | 2011 ND 89 | Interest of T.B.  (CONFIDENTIAL) | True | 243/244 |
| 18939 | 2013 ND 140 | Interest of M.S. (CONFIDENTIAL) | True | 229/230 |
| 19046 | 2014 ND 73 | Matter of D.J.D. (CONFIDENTIAL) | True | 257/258 |
| 19059 | 2015 ND 142 | Interest of B.E. (CONFIDENTIAL) | True | 252/253 |
| 19081 | 2015 ND 226 | Interest of E.V. (Confidential) | True | 230/231 |
| 19114 | 2015 ND 3 | Interest of M.S. (CONFIDENTIAL) (cross-ref w/  | True | 236/237 |
| 19162 | 2016 ND 198 | In the Matter of A.J.S. and N.J.S. (Confidenti | True | 238/239 |
| 19169 | 2016 ND 206 | Interest of S.J. (CONFIDENTIAL) | True | 256/257 |
| 19191 | 2016 ND 25 | Interest of G.L.D. (CONFIDENTIAL)(cross-refere | True | 226/227 |
| 19192 | 2016 ND 26 | Interest of G.L.D. (CONFIDENTIAL)(cross-refere | True | 240/241 |
| 19200 | 2016 ND 50 | Interest of C.S. (Confidential) | True | 228/229 |
| 19218 | 2017 ND 39 | Interest of D.V.A.(Confidential-Cross-ref.w/20 | True | 228/229 |
| 19223 | 2017 ND 44 | Interest of A.D. (Confidential) | True | 252/253 |
| 19280 | 2018 ND 236 | Interest of G.F. (CONFIDENTIAL) | True | 276/277 |
| 19418 | 2019 ND 272 | Interest of J.T.L.D. (CONFIDENTIAL) | True | 270/271 |
| 19423 | 2019 ND 277 | Matter of O.H.W. (CONFIDENTIAL) | True | 244/245 |
| 19585 | 2021 ND 115 | Interest of K.C. (CONFIDENTIAL) (consolidated  | True | 498/500 |
| 19592 | 2021 ND 129 | Matter of O.H.W. (CONFIDENTIAL) | True | 232/233 |
| 19598 | 2021 ND 157 | Interest of T.L.E. (CONFIDENTIAL) | True | 231/232 |
| 19607 | 2021 ND 184 | Interest of K.H. (CONFIDENTIAL) (consolidated  | True | 453/455 |
| 19682 | 2022 ND 194 | Interest of K.L.B. (CONFIDENTIAL) | True | 249/250 |
| 19827 | 2023 ND 72 | Interest of J.S. (CONFIDENTIAL) | True | 242/243 |
| 19839 | 2023 ND 99 | Interest of G.L.D. (CONFIDENTIAL) | True | 1078/1082 |
| 17803 | 2021 ND 79 | Interest of K.V. (CONFIDENTIAL) | True | 5302/5316 |
| 18448 | 2002 ND 90 | Interest of T.J.R.                    (NOTE:   | True | 366/367 |
| 18531 | 2005 ND 28 | Interest of T.C.R.  (CONFIDENTIAL) | True | 326/327 |
| 18581 | 2006 ND 7 | Interest of E.S., et al.  (CONFIDENTIAL) | True | 307/308 |
| 18689 | 2009 ND 121 | Interest of B.K. and D.K. (CONFIDENTIAL) | True | 286/287 |
| 18736 | 2009 ND 95 | Interest of S.J., et al.  (CONFIDENTIAL) (Cons | True | 299/300 |
| 18796 | 2011 ND 102 | Interest of C.L.(CONFIDENTIAL) | True | 293/294 |
| 18806 | 2011 ND 14 | Interest of J.W., a child (CONFIDENTIAL) | True | 364/365 |
| 18827 | 2011 ND 208 | Matter of L.D.M. (CONFIDENTIAL)(Cross-referenc | True | 324/325 |
| 18911 | 2012 ND 49 | Interest of I.D. (CONFIDENTIAL) | True | 330/331 |
| 19112 | 2015 ND 293 | Interest of A.C. (CONFIDENTIAL)(Consolidated w | True | 334/335 |
| 19239 | 2017 ND 88 | Interest of J.J.A.M. (Confidential) | True | 375/376 |
| 19293 | 2018 ND 27 | Interest of C.B. (CONFIDENTIAL) | True | 2371/2377 |
| 19329 | 2018 ND 6 | Interest of Z.B. (Confidential) | True | 289/290 |
| 19404 | 2019 ND 258 | Interest of J.B. (CONFIDENTIAL) | True | 2335/2342 |
| 19365 | 2019 ND 171 | W.C. v. J.H., et al. (CONFIDENTIAL) | True | 1671/1676 |
| 19451 | 2019 ND 304 | Interest of G.L.D. (CONFIDENTIAL) | True | 2038/2044 |
| 19503 | 2020 ND 169 | Interest of K.V. (CONFIDENTIAL) | True | 1894/1899 |
| 19568 | 2020 ND 72 | Interest of A.P.D.S.P.-G. (CONFIDENTIAL) | True | 888/891 |
| 19572 | 2020 ND 82 | Interest of M.M. (CONFIDENTIAL) | True | 317/318 |
| 19583 | 2021 ND 106 | Interest of K.B. (CONFIDENTIAL) (CONSOLIDATED  | True | 4382/4393 |
| 19605 | 2021 ND 178 | Interest of D.H.H. (CONFIDENTIAL) | True | 322/323 |
| 19608 | 2021 ND 189 | Interest of A.S.F. (CONFIDENTIAL) | True | 1956/1961 |
| 19611 | 2021 ND 201 | Interest of L.L.D.R. (CONFIDENTIAL) | True | 339/340 |
| 19613 | 2021 ND 205 | Interest of A.D. (CONFIDENTIAL) | True | 3563/3572 |
| 19617 | 2021 ND 218 | State v. S.J.H., et al. (Confidential) | True | 1860/1865 |
| 19634 | 2021 ND 76 | Interest of J.O. (CONFIDENTIAL) | True | 2005/2011 |
| 19645 | 2022 ND 127 | Interest of A.G. (CONFIDENTIAL) (consolidated  | True | 324/325 |
| 19712 | 2023 ND 100 | Interest of P.S. (CONFIDENTIAL) | True | 2285/2293 |
| 19716 | 2023 ND 109 | O'Neal v. State | True | 1521/1526 |
| 19790 | 2023 ND 203 | Interest of A.I. (CONFIDENTIAL) | True | 1621/1626 |
| 19817 | 2023 ND 39 | Interest of A.P. (CONFIDENTIAL) | True | 2388/2394 |
| 20029 | 2024 ND 57 | Interest of J.D. (CONFIDENTIAL) | True | 296/297 |
| 15568 | 2011 ND 21 | Matter of G.R.H. (CONFIDENTIAL) | True | 5662/5675 |
| 15767 | 2012 ND 17 | Interest of G.K.S. (CONFIDENTIAL) | True | 1189/1191 |
| 18383 | 2001 ND 129 | Interest of P.M., et al. (CONFIDENTIAL) | True | 404/405 |
| 18635 | 2007 ND 74 | Interest of L.J. and G.J.        (Confidential | True | 438/439 |
| 18743 | 2010 ND 160 | Matter of J.D.F. (CONFIDENTIAL) | True | 4049/4059 |
| 19187 | 2016 ND 24 | Interest of N.C. (CONFIDENTIAL) | True | 423/424 |
| 19364 | 2019 ND 169 | Matter of R.A.S. (Confidential) | True | 1694/1698 |
| 19584 | 2021 ND 113 | Interest of C.G. (CONFIDENTIAL)(consolidated w | True | 409/410 |
| 19692 | 2022 ND 235 | Interest of N.L. (CONFIDENTIAL) (consolidated  | True | 3032/3038 |
| 19734 | 2023 ND 137 | Interest of B.R. (CONFIDENTIAL) (consolidated  | True | 595/596 |
| 19742 | 2023 ND 157 | Interest of A.B. (CONFIDENTIAL) (consolidated  | True | 460/461 |
| 15062 | 2008 ND 185 | Matter of R.A.S.        (Confidential) | True | 1803/1804 |
| 15325 | 2010 ND 9 | Interest of B.B.  (CONFIDENTIAL) (Cross Ref w/ | True | 5577/5581 |
| 19361 | 2019 ND 16 | S.E.L. v. J.A.P., et al. (CONFIDENTIAL) | True | 4309/4313 |
| 19683 | 2022 ND 200 | Interest of E.H. (CONFIDENTIAL)(consol. w/2022 | True | 763/764 |
| 19823 | 2023 ND 56 | State v. K.J.A. (Confidential) | True | 1203/1204 |
| 20014 | 2024 ND 43 | Interest of A.P. (CONFIDENTIAL) | True | 2394/2396 |
| 14671 | 2006 ND 253 | Interest of R.S. (Confidential) | True | 4033/4032 |
| 14899 | 2008 ND 17 | Disciplinary Board v. O'Donnell (cross ref. 20 | True | 411/411 |
| 15172 | 2009 ND 53 | Interest of B.F.    (CONFIDENTIAL) | True | 3991/3991 |
| 17991 | 2022 ND 58 | Interest of T.H. (CONFIDENTIAL) (consolidated  | True | 624/624 |
| 18519 | 2005 ND 194 | Interest of J.F.   (CONFIDENTIAL) | True | 264/264 |
| 18505 | 2005 ND 100 | R.R. v. G.H. (CONFIDENTIAL)             (Cross | True | 179/179 |
| 18509 | 2005 ND 161 | M.S.B. v. J.M.B. (CONFIDENTIAL) | True | 171/171 |
| 18556 | 2006 ND 199 | Interest of K.S., et al.   (Consolidated w/200 | True | 332/332 |
| 18682 | 2008 ND 81 | Interest of C.J., S.J., and K.W. (CONFIDENTIAL | True | 361/361 |
| 18711 | 2009 ND 25 | Interest of R.M. (CONFIDENTIAL) | True | 273/273 |
| 18765 | 2010 ND 207 | Interest of R.J. (CONFIDENTIAL)(CONS. w/201002 | True | 286/286 |
| 18896 | 2012 ND 233 | Interest of G.L.D. (CONFIDENTIAL) (cross-refer | True | 200/200 |
| 18897 | 2012 ND 235 | Interest of A.J.L.H. (Confidential) (consolida | True | 344/344 |
| 19033 | 2014 ND 212 | Interest of B.B.P. (Confidential)(consolidated | True | 333/333 |
| 19078 | 2015 ND 20 | Interest of J.A.H. (Consolidated w/20140146) | True | 339/339 |
| 19085 | 2015 ND 24 | Interest of D.D. (CONFIDENTIAL)(Cons. w/201404 | True | 372/372 |
| 19153 | 2016 ND 143 | Interest of E.P. (CONFIDENTIAL)(consolidated w | True | 359/359 |
| 19159 | 2016 ND 188 | Interest of C.S., a child (CONFIDENTIAL)(CONSO | True | 254/254 |
| 19252 | 2018 ND 151 | Interest of Z.F.T. (CONFIDENTIAL)(consolidated | True | 487/487 |
| 19253 | 2018 ND 152 | Interest of A.C. (CONFIDENTIAL)(CONSOLIDATED W | True | 274/274 |
| 19259 | 2018 ND 160 | Interest of N.F.F. (CONFIDENTIAL) (consolidate | True | 365/365 |
| 19271 | 2018 ND 191 | Interest of M.S.H. (CONFIDENTIAL)(consolidated | True | 366/366 |
| 19310 | 2018 ND 42 | Interest of L.S. (CONFIDENTIAL)(consolidated w | True | 255/255 |
| 19339 | 2018 ND 89 | Interest of S.B. (Consolidated w/20180057)(CON | True | 286/286 |
| 19446 | 2019 ND 3 | Interest of P.T.D. (CONFIDENTIAL) (consolidate | True | 395/395 |
| 19454 | 2019 ND 35 | Interest of H.B. (CONFIDENTIAL) (CONSOLIDATED  | True | 407/407 |
| 19816 | 2023 ND 31 | Interest of V.C. (CONFIDENTIAL) | True | 459/459 |
| 14493 | 2006 ND 82 | Interest of P.F.       (CONFIDENTIAL) | True | 3160/3156 |
| 17651 | 2020 ND 124 | State v. Powley (consolidated w/ 20190324) | False | 2551/2548 |
| 19015 | 2014 ND 167 | Interest of C.S.K. (Confidential) (consolidate | True | 599/598 |
| 19743 | 2023 ND 158 | Interest of A.M. (CONFIDENTIAL)(consolidated w | True | 500/499 |
| 13713 | 2002 ND 157 | J.B. v. M.R.       (CONFIDENTIAL) | True | 334/333 |
| 14053 | 2004 ND 126 | Interest of T.F., et al.  (CONFIDENTIAL) | True | 6832/6810 |
| 14566 | 2006 ND 156 | Interest of K.H.    (CONFIDENTIAL) | True | 2016/2010 |
| 18987 | 2013 ND 65 | Interest of J.P. (Confidential) (consolidated  | True | 652/650 |
| 17786 | 2021 ND 42 | State v. Martinez | False | 11889/11845 |
| 18887 | 2012 ND 212 | Interest of T.M. (CONFIDENTIAL) (consolidated  | True | 283/282 |
| 14764 | 2007 ND 102 | Interest of D.C.S.H.C. (CONFIDENTIAL)(CONSOLID | True | 3995/3974 |
| 15633 | 2011 ND 118 | Interest of T.S. (CONFIDENTIAL) | True | 3461/3444 |
| 17647 | 2020 ND 98 | Brossart, et al. v. Janke, et al. | False | 4533/4510 |
| 17659 | 2020 ND 132 | Kremer v. State | False | 3087/3073 |
| 13869 | 2003 ND 151 | Interest of Z.C.B.  (CONFIDENTIAL) | True | 3871/3844 |
| 16061 | 2013 ND 109 | Interest of S.R.B. (Confidential) | True | 3897/3868 |
| 19804 | 2023 ND 231 | State v. Bearce | False | 2421/2405 |
| 20065 | 2024 ND 9 | Interest of J.C. (CONFIDENTIAL)(consolidated w | True | 2907/2887 |
| 13820 | 2003 ND 98 | Interest of A.B. (CONFIDENTIAL) | True | 6485/6425 |
| 17632 | 2020 ND 75 | Joyce v. Joyce | False | 4833/4792 |
| 17736 | 2020 ND 235 | State, et al. v. P.K. (Confidential) | True | 2099/2078 |
| 15010 | 2008 ND 130 | Matter of E.W.F.      (Confidential) | True | 2892/2861 |
| 17995 | 2022 ND 68 | Interest of M.R. (CONFIDENTIAL) | True | 1969/1948 |
| 19832 | 2023 ND 85 | E.R.J. v. T.L.B. (CONFIDENTIAL) | False | 5656/5592 |
| 17250 | 2018 ND 200 | Interest of J.B. (CONFIDENTIAL) | True | 3678/3630 |
| 16835 | 2017 ND 13 | Matter of C.D.G.E. (Confidential) | True | 1872/1846 |
| 18224 | 2023 ND 154 | Estate of Froemke | False | 6703/6613 |
| 15794 | 2012 ND 38 | Interest of T.H. (CONFIDENTIAL)(cross referenc | True | 4091/4032 |
| 19679 | 2022 ND 182 | Northern Oil & Gas v. EOG Resources, et al. | False | 4538/4455 |
| 17810 | 2021 ND 90 | Interest of J.B. (CONFIDENTIAL) | True | 1186/1163 |
| 14645 | 2006 ND 227 | State v. Buchholz  (Consol. w/20060061)        | False | 3189/3123 |
| 16720 | 2016 ND 91 | Interest of N.A. (Confidential) | True | 3135/3072 |
| 19651 | 2022 ND 137 | Brock James Baker v. LuAnn Erickson aka Thiel | False | 2564/2512 |
| 18214 | 2023 ND 148 | Interest of D.M.H. (CONFIDENTIAL) | True | 909/888 |
| 13615 | 2002 ND 136 | Roe v. Doe        (CONFIDENTIAL) | True | 8734/8515 |
| 15969 | 2012 ND 254 | Interest of T.H. (CONFIDENTIAL)(cross referenc | True | 4228/4105 |
| 18044 | 2022 ND 131 | Interest of A.P. (CONFIDENTIAL) (consolidated  | True | 761/739 |
| 19740 | 2023 ND 151 | Wootan v. State | False | 1703/1648 |
| 19688 | 2022 ND 214 | Fercho v. Fercho, et al. | False | 9047/8738 |
| 20069 | 2024 ND 93 | State v. Castleman | False | 1237/1193 |
| 17749 | 2021 ND 10 | Interest of M.M. (CONFIDENTIAL) (consolidated  | True | 481/461 |
| 18052 | 2022 ND 169 | Interest of A.C. (CONFIDENTIAL) | True | 497/476 |
| 17769 | 2021 ND 40 | Interest of L.T.D. (CONFIDENTIAL)  (consolidat | True | 485/464 |
| 17617 | 2020 ND 55 | Interest of D.M.D. (CONFIDENTIAL) | True | 432/411 |
| 20073 | 2024 ND 97 | Armitage v. Armitage | False | 1830/1742 |
| 18048 | 2022 ND 167 | Interest of J.G. (CONFIDENTIAL) (consolidated  | True | 427/406 |
| 12902 | 1999 ND 117 | Interest of M.S.  (CONFIDENTIAL - M.H.) | True | 1025/971 |
| 17727 | 2020 ND 239 | Interest of K.R.C.W. (CONFIDENTIAL) | True | 432/409 |
| 17789 | 2021 ND 64 | Interest of S.R. (CONFIDENTIAL)(consolidated w | True | 335/315 |
| 17800 | 2021 ND 77 | Interest of P.F. (CONFIDENTIAL) (consolidated  | True | 328/308 |
| 17752 | 2021 ND 15 | Interest of A.R.S. (CONFIDENTIAL)(consolidated | True | 340/319 |
| 18200 | 2023 ND 110 | Interest of I.X.F. (CONFIDENTIAL) | True | 331/310 |
| 17691 | 2020 ND 195 | Interest of J.F. (CONFIDENTIAL)(consolidated w | True | 308/288 |
| 17083 | 2017 ND 248 | Interest of P.T.D. (CONFIDENTIAL)(cons. w/ 201 | True | 2496/2310 |
| 18045 | 2022 ND 133 | Interest of T.E. (CONFIDENTIAL) | True | 258/238 |
| 18070 | 2022 ND 174 | Interest of T.L.E. (CONFIDENTIAL) | True | 267/246 |
| 17976 | 2022 ND 48 | Interest of R.S. (CONFIDENTIAL) | True | 239/219 |
| 18094 | 2022 ND 209 | Interest of A.M.K. (CONFIDENTIAL) | True | 251/230 |
| 18122 | 2023 ND 5 | Interest of S.M.B. (CONFIDENTIAL) | True | 225/204 |
| 17791 | 2021 ND 65 | Interest of F.M.G. (CONFIDENTIAL) | True | 196/175 |
| 19661 | 2022 ND 149 | State v. Pendleton | False | 4297/3764 |
| 19623 | 2021 ND 31 | Burr v. N.D. State Board of Dental Examiners | False | 2000/1646 |
| 20044 | 2024 ND 70 | In the Interest of H.J.J.N., a Child | False | 854/378 |
