# Volume↔date flags quarantined for 2nd-source / human review

From the `volume_date_check` audit (batch `fix-volume-date-2026-05-27` applied the
clear ones). These 11 are ambiguous: the date is probably wrong but the exact
correct date isn't recoverable from the served text, or the cite is shared, or
the text-date agrees with the DB while only the neutral cite is off. **No change
applied.** Resolve against Westlaw / the bound reporter.

## Date likely wrong, exact date not in text (two independent reporter cites agree on a different year than DB date)
These pre-1953 N.D.-Reports-era rows have NO "Decided" line; the synthetic neutral
was derived from the (suspect) `date_filed`, so it isn't independent. Two reporter
cites point to a later year. Confirm the true filing date from the reporter.

| oid | DB date | reporter cites (imply) | case | likely true year |
|----:|---------|------------------------|------|-----------------|
| 158 | 1895-11-24 | 14 N.D. 570 + 105 N.W. 942 (~1905) | Hart v. Evanson | ~1905 |
| 1161 | 1898-11-28 | 25 N.D. 629 + 146 N.W. 1061 (~1913) | First Nat. Bank of Hillsboro v. Steenson | ~1913 |
| 1162 | 1898-12-05 | 25 N.D. 635 + 146 N.W. 1064 (~1913) | In re Appeal of First Nat. Bank | ~1913 |
| 1632 | 1910-05-18 | 34 N.D. 321 + 159 N.W. 401 (~1916) | State ex rel. Marshall v. Blaisdell | ~1916 |
| 4134 | 1925-11-30 | 236 N.W. 242 + 60 N.D. 547 (~1931) | Bernier v. Preckel | ~1931 |
| 4724 | 1931-11-13 | 269 N.W. 741 + 67 N.D. 67 (~1936) | Rufer v. Rufer | ~1936 |

## Date vs single reporter cite, or shared cite — need to confirm which is wrong
| oid | DB date | flagged cite | shared? | note |
|----:|---------|--------------|---------|------|
| 11760 | 1991-12-19 | 522 N.W.2d 745 (~1994) | shared by 2 | judicial-vacancy order; shared page — could be date or a Table-page mis-attach |
| 16652 | 2013-02-15 | 874 N.W.2d 910 (~2016) | shared by 2 | text "Decided 2013" + neutral 2013 ND 21 say 2013, so the N.W.2d cite looks wrong, but it's shared — verify the other holder |
| 20474 | 1991-02-21 | 513 N.W.2d 561 (~1994) | no | Lang v. Binstock; 513 N.W.2d 561 is a 1994 page — date may be 1994 (neutral 1991 ND 30 is synthetic) |

## Text-date agrees with DB, only the neutral cite is off-by-one — verify the neutral
| oid | DB date | neutral | other | note |
|----:|---------|---------|-------|------|
| 13716 | 2003-01-22 | 2002 ND 122 | 656 N.W.2d 1; text Decided 2003-01-22 | date+text say 2003 but neutral says 2002 — possible wrong neutral, or a 2002 decision with a 2003 rehearing date |
| 20180 | 2026-01-28 | 2025 ND 193 | Filed 01/28/26 | Filed-stamp says 2026 but neutral says 2025 — late-2025 opinion released Jan 2026, or a wrong neutral |
