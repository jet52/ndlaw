# West-sourcing audit — modern opinions (run 2026-06-24)

**Question:** how many DB opinions store the West `.doc` rendering as `text_content`
when an authoritative court source (markdown/PDF) exists? (Triggered by the H.J.J.N.
provenance finding.)

## Findings

- **7,297** opinions total have `source_reporter='westlaw'`. The vast majority are
  pre-1997 N.D. Reports opinions where the West `.doc` is the only/best source —
  **legitimate**.
- **63** are **modern (date_filed ≥ 1997)** — the neutral-cite era where court PDFs
  exist. Every one inspected carries West-rendering markers (star-pages `*NNN`,
  `Attorneys and Law Firms` / `Opinion` section labels, West citation forms). These are
  the anomalies: the ingest used West text instead of the court source.

### Disposition of the 63

| Disposition | Count | Notes |
|---|---|---|
| `rederive-from-court-pdf` | 43 | docket-matched to a court markdown **and** PDF; re-derivable |
| `rederive-after-misfile-fix` | 2 | H.J.J.N. pair (id 20044 = 2024 ND 70, id 19877 = 2024 ND 132); PDFs misfiled/swapped — fix names first |
| `no-court-source` | 15 | all **1997** (1997 ref coverage is partial: 245 md / 85 pdf); West `.doc` likely the best available — probably acceptable |
| `no-match-investigate` | 3 | Pailing 2019 (id 19429), Buchholz 2006 (id 14645), a 1998 disciplinary (id 12782) — docket-format/consolidation mismatch, check manually |

Year distribution of the **45 re-derivable**: 2024 ×18, 2019 ×10, 2022 ×5, 2023 ×5,
2020 ×3, 2003/2004/2018/2021 ×1 each.

### Critical caveat for remediation

**All 45 re-derivable opinions already carry logged `changelog` corrections.** A naive
`text_content := court-markdown` replacement would silently revert every prior correction
(West-headnote stripping, proofing-fleet fixes, this session's edits, etc.). Remediation
must be **correction-aware**:

1. derive clean text from the correct court PDF/markdown,
2. re-apply the opinion's logged content corrections on top (or diff-and-merge),
3. update `source_reporter` / `is_primary` to the court source,
4. for the H.J.J.N. pair, first correct the swapped PDF/markdown filenames.

This is a dedicated gated pass, not an inline edit. Worklist (with per-opinion
`court_md`, `court_pdf`, `disposition`, `has_logged_corrections`) is in
`triage/westdoc-modern-audit.json`.

## Recommendation

Run a gated, correction-aware re-derivation over the 43 + 2 set (prioritize the 2024 and
2019 clusters) before the next public release — these are recent, high-traffic opinions
where the published text should be the court's, not West's. Leave the 15 × 1997 as-is
unless clean 1997 court sources are obtained. Investigate the 3 oddballs individually.
