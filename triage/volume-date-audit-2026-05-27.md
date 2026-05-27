# Volume vs date_filed consistency audit (report-only)

Flagged when |date_filed year - reporter-volume median year| >= 3 (volume year derived from the corpus median per volume).

- HIGH confidence (>=6y off): 6
- MEDIUM (3-6y off, reporter): 3
- neutral-cite year != date year: 2

## HIGH (>=6y) (6)
| oid | date_filed | cite (series vol) | vol median yr | off | case_name |
|----:|-----------|-------------------|--------------:|----:|-----------|
| 1161 | 1898-11-28 | 146 N.W. 1061 (NW 146) | 1914 | 16 | First Nat. Bank of Hillsboro v. Steenson, Coun |
| 1162 | 1898-12-05 | 146 N.W. 1064 (NW 146) | 1914 | 16 | In re the Appeal of the First National Bank |
| 158 | 1895-11-24 | 14 N.D. 570 (NDR 14) | 1905 | 10 | Hart v. Evanson |
| 1632 | 1910-05-18 | 34 N.D. 321 (NDR 34) | 1916 | 6 | State ex rel. Marshall v. Blaisdell |
| 4134 | 1925-11-30 | 236 N.W. 242 (NW 236) | 1931 | 6 | Bernier v. Preckel |
| 4724 | 1931-11-13 | 67 N.D. 67 (NDR 67) | 1937.0 | 6.0 | Rufer v. Rufer |

## MEDIUM (3-6y) (3)
| oid | date_filed | cite (series vol) | vol median yr | off | case_name |
|----:|-----------|-------------------|--------------:|----:|-----------|
| 11760 | 1991-12-19 | 522 N.W.2d 745 (NW2d 522) | 1994.0 | 3.0 | In re a District Judge Vacancy in the Chamber  |
| 16652 | 2013-02-15 | 874 N.W.2d 910 (NW2d 874) | 2016 | 3 | In the Matter of the Application for Transfer  |
| 20474 | 1991-02-21 | 513 N.W.2d 561 (NW2d 513) | 1994.0 | 3.0 | Lang v. Binstock |

## NEUTRAL-cite year mismatch (2)
| oid | date_filed | cite (series vol) | vol median yr | off | case_name |
|----:|-----------|-------------------|--------------:|----:|-----------|
| 13716 | 2003-01-22 | 2002 ND 122 (NEUTRAL 2002) | 2002.0 | 1 | Johnson Farms v. McEnroe |
| 20180 | 2026-01-28 | 2025 ND 193 (NEUTRAL 2025) | 2025.0 | 1 | Sheila K. Boyda v. Joseph A. Boyda |