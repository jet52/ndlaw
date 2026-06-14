# Proof-widening (option B) — extraction across varied amendment shapes

Read-only. Extends the art. X §21 pilot to 6 more measures of deliberately
varied shape, to surface the hard cases BEFORE committing to ingest architecture.
Plus: validated the extraction-escalation ladder (pdftotext → marker OCR →
Claude direct read).

## Cases examined
| Measure | Shape | Source PDF | pdftotext quality |
|---|---|---|---|
| art. X §21 (pilot) | simple accretion, 3 versions | 1981/1991/1995 CAA | clean except 1995 fi-ligature |
| CX (110) | **create new art. VII + repeal old art. VII** | 1983 CAA | clean (word-split artifacts only) |
| CXIX (119) | **8 new sections to art. IV** (one of several 1985-86 measures rebuilding art. IV) | 1985 CAA | clean |
| CXII (112) | **cross-article**: art. XI §26 + art. IV §46 + art. V §14 in ONE measure | 1983 CAA | clean |
| CXXXV (135) | **create new art. V + repeal old**, 12 sections; non-standard URL format | 1997 SL7CNSTM | clean |
| CLXIII (163) | 2019, art. XIV, newest CAA format | 2019 CAA | clean |
| LXXVIII (78) | **structural**: subsection 6(d) of art. LIV; art. LIV stored as ONE provision | 1965 CMA | clean |

## Headline: extraction is largely SOLVED; the hard problems are STRUCTURAL
- **pdftotext -layout is clean across the modern CAA corpus** (1965–2019), ratio≈0
  suspicious tokens. The only OCR damage found is the 1995 CAA fi-ligature
  (`ftrst`/`ftfty`). Word-split justification artifacts (`c i ty`, `repea l`,
  `December l`) are trivially normalized.
- So OCR escalation is the **exception, not the rule**. Most of the ~96 provisions
  extract cleanly with pdftotext + whitespace/ligature normalization.

## Extraction-escalation ladder (validated)
1. **pdftotext -layout** — default; clean for ~all modern CAAs.
2. **Claude direct read** (Read tool on the page PDF) — the rendered image shows the
   true glyphs. Confirmed on caa-1995-p1: image reads "first"/"fifty" where the text
   layer mis-codes the fi-ligature to "ft". Authoritative tiebreak; use per-page when
   a provision's gate fails on suspicious tokens.
3. **marker OCR** (`marker_single`) — automated image→markdown for bulk recovery when
   a whole PDF's text layer is bad. CONFIRMED on caa-1995-p1: marker output reads
   "used first to replace" / "Up to fifty percent" correctly (reads pixels, not the
   broken text layer). Slow per-invocation (model load ~minutes); use as a one-time
   batch over the handful of ligature-damaged PDFs, not per-provision.

## The real engineering (NOT extraction)
1. **Whole-article create+repeal** (CX, CXXXV): the measure creates an entirely new
   article and repeals the prior one. Reconstruction must (a) split the new article
   into its sections, (b) mark the *prior* article's sections superseded at that date.
2. **Multi-measure provision histories** (art. IV rebuilt by CXIX+CXX+CXII across
   1985–86): a single provision's timeline needs ALL measures touching it, in date
   order. Must group by (provision) across measures, not by measure.
3. **Cross-article measure-splitting** (CXII → art. XI §26 + art. IV §46 + art. V §14):
   the splicer must segment one measure's text by section and route each fragment to
   the correct provision timeline.
4. **Subsection-level amendments + the art. LIV schema problem** (LXXVIII amends
   subsection 6(d); art. LIV is one undivided provision): needs art. LIV subdivided
   into subsection-provisions, or whole-provision snapshots per amendment. This is
   PL-CONST-STRUCTURAL #2 — same blocker, now confirmed at the extraction layer.
5. **Older "described-edit" amendment style** (1960s CMA Ch. 474: "by adding the words
   X / by omitting the words Y") — NOT a reprint; post-amendment text must be computed
   by applying the described edits to the base. Modern CAAs (1981+) all reprint full
   text ("amended and reenacted to read as follows"), so this only bites the structural
   pre-1981 four — but those are exactly the unapplied ones.

## Implication for the ingest design
The locator/splicer needs to recognize, per measure: create-article | amend-reenact-
section | repeal-article | repeal-section | described-edit. Modern (1981+) is dominated
by amend-reenact-section + create-article (both full-text reprints) → tractable. The
described-edit and subsection cases are confined to the structural four → handle those
as bespoke, not in the bulk path.
