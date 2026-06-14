# Proposal — Multi-agent redline-read campaign for modern constitution point-in-time

## Goal
Reconstruct the pre-amendment ("prior") text of the ~80 modern (1981–present)
constitution provisions that have post-1981 amendments, so each becomes a proper
point-in-time version timeline (matching the now-complete historical layer). The
work is gated on reading **legislative redlines** (struck = deleted, underline =
added) in the session-law Constitutional Amendment Act PDFs — which pdftotext and
marker both flatten, so only visual reading resolves them. That read is the
bottleneck; this campaign parallelizes it across a team of subagents while the
main context (me) verifies every result against an independent witness.

## Why multi-agent
Each provision is independent: read one measure → produce one prior text. 8–10
high-capability agents reading in parallel ≈ 8–10× throughput. The dangerous part
(hand-reading redlines has a measured ~40% error rate — the 1981-Blue-Book gate
caught 2 of 5 in earlier solo work) is contained by **main-context verification**:
no agent output is trusted until it passes the independent gates below.

## Architecture
1. **Prep (main):** for each provision, resolve its CAA PDF, locate the measure
   page(s), render to high-DPI PNG, and assemble a per-provision task record
   (citation, verbatim current DB text, amendment date/number, PNG paths,
   pdftotext hint). Split into N batches.
2. **Read (agents, parallel):** each agent processes one batch (~7 provisions).
   For each, it visually reads the rendered measure, identifies every struck and
   underlined span, and returns the exact prior text + a minimal edit list +
   classification + confidence + flags. **Structured output only.**
3. **Verify (main):** for each returned prior, run three independent gates
   (below). Accept → splice into scratch with provenance. Reject/flag → re-read.
4. **Report:** coverage `N of 96`, plus the residual (heavy multi-subsection →
   native source; anything that failed gates → re-read queue).

## Agent task spec (each agent is given this verbatim)
For each provision in your batch:
1. **Read the rendered measure image(s).** Find the operative reprint of the
   assigned section ("Section N. …" after "amended and reenacted as follows:").
2. **Classify:** `REDLINE` (strike/underline markup) | `CLEAN_REPRINT` (no markup
   — the printed text already = the amended text) | `CREATE_SECTION` ("created and
   enacted" / "adding … a new …" — provision is NEW at this date, no prior) |
   `SUBSECTION_PARTIAL` (measure reprints only some subsections of a larger
   section) | `UNREADABLE`.
3. **For REDLINE / CLEAN_REPRINT:** produce the **prior text** = the section's
   text immediately *before* this amendment. For a redline that means: keep struck
   text, drop underlined text. For a clean reprint of a single-amendment provision,
   the prior is NOT visible (the reprint shows the after-text) → return
   `prior_text:null`, `classification:CLEAN_REPRINT`, and flag `needs-base-source`.
4. **Produce a minimal edit list** `[[after_phrase, before_phrase], …]` that
   transforms the **current text** (provided) into the prior text. Every
   `after_phrase` MUST be a substring that occurs **exactly once** in the current
   text. `before_phrase` is what it was before the amendment (use `""` to delete an
   added span). Keep phrases short but uniquely anchored.

## Output spec (strict — return a single JSON array, nothing else)
```json
[{
  "citation": "N.D. Const. art. XI, § 16",
  "amendment_date": "2006-08-01",
  "classification": "REDLINE",
  "prior_text": "<verbatim full prior-version section text, or null>",
  "edit_list": [["after phrase (unique in current)","before phrase"], ...],
  "n_changes": 6,
  "confidence": "high|medium|low",
  "flags": ["multi-page" | "needs-base-source" | "ocr-ambiguous" | "subsection-only" | ...],
  "notes": "anything the verifier should know; cite specific struck/added words"
}]
```

## Quality requirements (non-negotiable — this is authoritative legal text)
- **Verbatim.** Preserve original spelling, punctuation, capitalization, and any
  typos exactly. Do not modernize or normalize.
- **Reversibility.** `apply(edit_list, current_text)` must equal `prior_text`
  exactly (whitespace-normalized). The verifier checks this mechanically.
- **Unique anchors.** Each `after_phrase` occurs exactly once in current text.
- **No guessing.** If a struck/underlined span is illegible or ambiguous, set
  `confidence:low` and describe the ambiguity in `notes` — do not invent text.
- **Distinguish strike vs underline carefully.** The single most common error is
  keeping an *added* (underlined) span in the prior. Re-check every change.

## Main-context verification gates (I run all three before accepting)
1. **Mechanical:** `apply(edit_list, current) == prior_text` (token-normalized);
   every anchor unique. Fail → reject.
2. **Independent witness (1981 Blue Book):** for single-amendment carried
   provisions, the prior `[1981, d1)` text must match the 1981 BB section
   (normalized substring / ≥0.97 fuzzy) where the BB article is clean. This is the
   gate that caught the 40% error rate. BB-degraded article → fall to gate 3 + a
   second agent read.
2b. **Structural:** no markup-flatten artifacts (`departmentbranches`,
   doubled function words); plausible length vs current; classification consistent.
3. **Cross-check:** similarity of prior vs current is consistent with the
   described changes (small edits → high similarity; whole rewrites flagged).
Accepted provisions are spliced into `/tmp/const-scratch.db` with a changelog row;
rejected/low-confidence go to a re-read queue (a second agent, then me).

## Batching & scale
~80 provisions needing reads. First wave: the single-amendment redline set
(~68 after excluding the 6 already done), split across 9 agents (~7–8 each).
Multi-amendment (22, need intermediate reprints) and heavy multi-subsection
(~4 → native source) are later waves. Coverage is reported cumulatively.

## Models / effort
High-capability subagents (default to the strongest available); no effort cap —
end-state quality is the only objective. Every result is independently gated;
ambiguous results get a second independent read before main-context adjudication.
