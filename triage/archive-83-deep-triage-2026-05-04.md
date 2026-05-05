# Deep triage: 83 archive pairs at <0.20 similarity (post fix-archive-pairings batch)

After the 2026-05-04 fix-archive-pairings batch, the multi-source diff audit still flags **83 archive pairs** below 0.20 similarity. Their archive titles all match the linked opinion's citations (so the title-check passes), but the body texts disagree by >80%. Four distinct failure modes:

## Category breakdown

| Category | Count | Cause | Recommended action |
|----------|------:|-------|--------------------|
| secondary_truncated | 30 | archive HTML body has < 30% the word count of the DB primary; HTML download was truncated | re-scrape from archive.ndcourts.gov via `scrape_archive --reprocess` |
| primary_short | 26 | DB's primary text is shorter than archive (often DB has only the initial publication while archive includes rehearing/modification) — 2 of these have `Rehearing`/`Modified` markers in archive | review case-by-case: prefer the longer archive version where it's the canonical full opinion |
| primary_tiny | 14 | DB primary < 100 words (summary affirmances). Archive has more because of HTML chrome inflating the word count | not a bug — relax audit threshold for short opinions; no action |
| Type Y (contaminated cites) | 5 | DB row has 2+ neutral cites including the archive's actual cite as a stray. The archive is for a DIFFERENT opinion that should have its own row. | (1) insert new opinion row for the supplemental publication, (2) remove stray citations from contaminated row, (3) detach the wrong archive linkage |
| genuinely_unclear | 8 | Both texts substantial and titles match but content differs — possibly OCR/formatting drift past the audit threshold | individual inspection |

## Type Y / contaminated citations

These DB rows have an extra neutral cite that doesn't belong — the cite came from a supplemental publication or per-curiam follow-on at a different N.W. parallel cite, and ingest mis-attributed it.

| oid | DB citations (note 2 neutral cites) | archive title parallel | archive_path |
|----:|--------------------------------------|------------------------|--------------|
| 13202 | 2000 ND 141, 613 N.W.2d 510, 2000 ND 138 | 613 N.W.2d 511 | `archive/2000/20000189.htm` |
| 15805 | 2012 ND 27, 812 N.W.2d 455, 2012 ND 31 | 812 N.W.2d 467 | `archive/2012/20110159.htm` |
| 15807 | 2012 ND 31, 812 N.W.2d 467, 2012 ND 27 | 812 N.W.2d 455 | `archive/2012/20110213.htm` |
| 16488 | 2013 ND 18, 863 N.W.2d 843, 2013 ND 19 | 826 N.W.2d 620 | `archive/2013/20130018.htm` |
| 16829 | 2017 ND 1, 889 N.W.2d 399, 2017 ND 255 | 903 N.W.2d 280 | `archive/2017/20170034.htm` |

## Sample: secondary_truncated (30 total)

- oid=13130, 609 N.W.2d 455, _State v. Farok_ — primary_words=1980, secondary_words=252, sim=0.013, archive=`archive/2000/990326.htm`
- oid=13527, 639 N.W.2d 706, _Farmers Elevator, Inc. of Grace City v. Custom Pro_ — primary_words=5306, secondary_words=348, sim=0.006, archive=`archive/2001/20010059.htm`
- oid=13552, 642 N.W.2d 532, _Piatz v. ND Dept. of Transportation_ — primary_words=1624, secondary_words=212, sim=0.021, archive=`archive/2002/20010232.htm`
- … and 27 more

## Sample: primary_short (26 total)

- oid=13290, 621 N.W.2d 314, _Logan v. Bush_ — primary_words=297, secondary_words=5811, sim=0.005, archive=`archive/2000/20000090.htm`
- oid=13635, 650 N.W.2d 812, _In the Matter of Petition to Change the Resident C_ — primary_words=192, secondary_words=1805, sim=0.044, archive=`archive/2002/20020048.htm`
- oid=14196, 692 N.W.2d 784, _Johnson v. State_ — primary_words=79, secondary_words=333, sim=0.005, archive=`archive/2005/20040203.htm`
- … and 23 more

## Sample: primary_tiny (14 total)

- oid=14416, 709 N.W.2d 21, _State v. White Mountain_ — primary_words=74, secondary_words=243, sim=0.018, archive=`archive/2005/20050157.htm`
- oid=14483, 711 N.W.2d 606, _State v. Smith_ — primary_words=77, secondary_words=222, sim=0.015, archive=`archive/2006/20050181.htm`
- oid=14585, 719 N.W.2d 759, _In Re Nb_ — primary_words=71, secondary_words=217, sim=0.008, archive=`archive/2006/20060031.htm`
- … and 11 more
