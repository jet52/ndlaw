# Volume vs date_filed consistency audit (report-only)

Flagged when |date_filed year - reporter-volume median year| >= 3 (volume year derived from the corpus median per volume).

- HIGH confidence (>=6y off): 14
- MEDIUM (3-6y off, reporter): 6
- neutral-cite year != date year: 9

## HIGH (>=6y) (14)
| oid | date_filed | cite (series vol) | vol median yr | off | case_name |
|----:|-----------|-------------------|--------------:|----:|-----------|
| 6417 | 1912-02-16 | 134 N.W.2d 84 (NW2d 134) | 1965.0 | 53.0 | Johnson v. Barton |
| 5888 | 1902-01-09 | 62 N.D. 767 (NDR 62) | 1932.0 | 30.0 | Easton v. Lockhart |
| 5968 | 1902-12-10 | 62 N.D. 771 (NDR 62) | 1932.0 | 30.0 | Prescott v. Brooks |
| 1161 | 1898-11-28 | 146 N.W. 1061 (NW 146) | 1914 | 16 | First Nat. Bank of Hillsboro v. Steenson, Coun |
| 1162 | 1898-12-05 | 146 N.W. 1064 (NW 146) | 1914 | 16 | In re the Appeal of the First National Bank |
| 12623 | 1998-01-21 | 375 N.W.2d 203 (NW2d 375) | 1985 | 13 | State v. Esparza |
| 815 | 1911-10-02 | 50 N.D. 1 (NDR 50) | 1923 | 12 | Schafer v. Olson |
| 985 | 1924-05-21 | 139 N.W. 138 (NW 139) | 1912 | 12 | State Bank of New Salem v. Schultze (Union Far |
| 158 | 1895-11-24 | 14 N.D. 570 (NDR 14) | 1905 | 10 | Hart v. Evanson |
| 16931 | 2007-04-25 | 894 N.W.2d 908 (NW2d 894) | 2017 | 10 | State v. Schnellbach |
| 15985 | 2006-07-05 | 826 N.W.2d 352 (NW2d 826) | 2013.0 | 7.0 | Guardianship and Conservatorship of Johnson |
| 1632 | 1910-05-18 | 34 N.D. 321 (NDR 34) | 1916 | 6 | State ex rel. Marshall v. Blaisdell |
| 4134 | 1925-11-30 | 236 N.W. 242 (NW 236) | 1931 | 6 | Bernier v. Preckel |
| 4724 | 1931-11-13 | 67 N.D. 67 (NDR 67) | 1937.0 | 6.0 | Rufer v. Rufer |

## MEDIUM (3-6y) (6)
| oid | date_filed | cite (series vol) | vol median yr | off | case_name |
|----:|-----------|-------------------|--------------:|----:|-----------|
| 5270 | 1899-05-05 | 58 N.W. 1051 (NW 58) | 1894 | 5 | State v. Hogan |
| 5352 | 1900-11-26 | 64 N.W. 563 (NW 64) | 1895 | 5 | Hawk v. Konouzki |
| 15757 | 2016-12-20 | 808 N.W.2d 205 (NW2d 808) | 2011.5 | 4.5 | Schaffner v. Job Service North Dakota |
| 11760 | 1991-12-19 | 522 N.W.2d 745 (NW2d 522) | 1994.0 | 3.0 | In re a District Judge Vacancy in the Chamber  |
| 16652 | 2013-02-15 | 874 N.W.2d 910 (NW2d 874) | 2016 | 3 | In the Matter of the Application for Transfer  |
| 20474 | 1991-02-21 | 513 N.W.2d 561 (NW2d 513) | 1994.0 | 3.0 | Lang v. Binstock |

## NEUTRAL-cite year mismatch (9)
| oid | date_filed | cite (series vol) | vol median yr | off | case_name |
|----:|-----------|-------------------|--------------:|----:|-----------|
| 13716 | 2003-01-22 | 2002 ND 122 (NEUTRAL 2002) | 2002.0 | 1 | Johnson Farms v. McEnroe |
| 14038 | 2003-06-03 | 2004 ND 108 (NEUTRAL 2004) | 2004.0 | 1 | Kostrzewski v. Frisinger |
| 14645 | 2007-11-07 | 2006 ND 227 (NEUTRAL 2006) | 2006.0 | 1 | State v. Buchholz  (Consol. w/20060061)        |
| 14896 | 2007-01-23 | 2008 ND 14 (NEUTRAL 2008) | 2008.0 | 1 | Wold v. Wold |
| 14941 | 2007-04-17 | 2008 ND 65 (NEUTRAL 2008) | 2008.0 | 1 | State v. Kieper |
| 16020 | 2012-04-05 | 2013 ND 57 (NEUTRAL 2013) | 2013.0 | 1 | K & L Homes, Inc. v. American Family Mutual In |
| 18077 | 2023-02-23 | 2022 ND 178 (NEUTRAL 2022) | 2022.0 | 1 | Queen v. Martel, et al. |
| 18142 | 2022-10-04 | 2023 ND 32 (NEUTRAL 2023) | 2023.0 | 1 | Queen v. Martel, et al. |
| 20180 | 2026-01-28 | 2025 ND 193 (NEUTRAL 2025) | 2025.0 | 1 | Sheila K. Boyda v. Joseph A. Boyda |