# ICLR 2027 Readiness Gate — The Calendar Gap

Status: **P0 INTERNAL PREPARATION — NOT SUBMITTED**

Branch: `iclr-2027-prep`

Canonical scientific source remains the repository evidence on `main`. This branch is an ICLR adaptation surface only. Nothing in this directory authorizes OpenReview registration, abstract submission, paper submission, outreach, spending, or publication.

## Venue deadlines and hard constraints

- Genuine abstract deadline: **2026-09-18 23:59 AoE**.
- Full paper deadline: **2026-09-25 23:59 AoE**.
- No new authors may be added after the abstract deadline.
- Submission is double blind; author identity must not appear in paper or supplementary material.
- Main text limit at submission: **9 pages**, excluding references; appendix may follow references.
- A mandatory AI-use disclosure is required and is outside the page limit.
- Parallel submission of substantially similar work to another archival conference or journal is not allowed.

## Candidate decision

**Primary ICLR candidate: `The Calendar Gap: Mechanism-Level Diagnosis of Arabic Agentic Failures`.**

Rationale:

1. A complete manuscript, claims ledger, figures, statistical outputs, deterministic scorer, and paper gate already exist.
2. The paper contains an empirical five-arm study rather than a protocol-only or synthetic-only result.
3. The central result is mechanism-isolating: Arabic-language performance remains high under Gregorian dates and Eastern numerals while Hijri-calendar reasoning collapses across all tested arms.
4. The methodological contribution — matched variants that toggle one mechanism while holding language/tool structure fixed — is broader than the Arabic case study and fits evaluation of learned systems.

Projects not selected for this deadline:

- `human-agent-intelligence`: publication-level generalization remains HOLD and the later LLM development stage found no eligible confirmatory pair.
- `taqti`: Stage 005 is frozen for execution but the decisive scale-balanced GPU experiment has not run.
- `science-of-ai-systems`: main included behavioral trials have not started.
- `arabic-frontier-ai-audit`: confirmatory inference has not run.
- `ai-contingency-fossilization`: mechanistic pilot only.
- `transformer-perturbation-susceptibility`: repository evidence refers to an already submitted journal manuscript, so it is excluded from parallel ICLR submission unless that archival submission state changes through an explicit PI decision.

## Blocking scientific issue: D36 raw-log loss

The current repository discloses that historical `results/raw/` transcripts were gitignored and were lost when the original execution container was recycled. Preserved evidence includes the 107 task records and golds, frozen scorer, scored per-record outputs for the four open arms, summaries, forensics, the 50-record audit sample with verbatim transcripts, `numbers.json`, and DC3 reports.

This invalidates any manuscript sentence claiming that the frozen historical run can still be regenerated from stored raw logs.

### Required recovery before full submission

Preferred path, already designated by the repository record:

1. Re-execute the frozen task/model protocol using the pinned roster where the exact model interfaces remain available.
2. Commit fresh raw outputs in the same evidence push as summaries.
3. Produce an agreement report against the frozen `numbers.json` and scorer version.
4. Distinguish **exact reproduction** from **temporal replication** if a provider/model endpoint has changed since the frozen run.
5. Never silently overwrite the historical result; retain both frozen derived evidence and the fresh recovery archive.

If exact re-execution is impossible for a model, the manuscript must state that limitation explicitly and must not claim raw-level reproducibility for that arm.

No provider calls are authorized by this readiness file. Execution requires a separately authorized compute/provider action.

## Second scientific weakness: scorer-audit ceiling

The preregistered full-scorer human-consensus gate did not pass: the amended scorer reached approximately 0.91 against a 0.95 threshold. This must remain visible rather than being rhetorically minimized.

The ICLR main-text claim should therefore be narrower:

- The strongest headline is the calendar mechanism M2, for which scorer/human consensus agreement was complete on the reported consensus sample.
- Broader claims about transliteration and serialization should be presented as secondary diagnostic findings with the scorer-audit limitation attached.
- Do not turn the failed global gate into a post-hoc pass by changing thresholds.

## ICLR paper architecture

Target a 9-page main paper with the following priority order:

1. **Problem and gap** — aggregate multilingual benchmarks identify a gap but cannot localize its cause.
2. **Matched-mechanism design** — one controlled property changes while tools/semantics are held fixed.
3. **Deterministic measurement** — calendar oracle, tool-call scorer, contamination controls, frozen hypotheses.
4. **Main empirical result** — Gregorian-Arabic high performance vs. severe Hijri collapse across five arms.
5. **Forensics** — attempted conversion vs. exactness, error magnitude, and contrast with transliteration/serialization failures.
6. **Robustness and audit** — scorer audit, sensitivity across scorer versions, exact tests/CIs, limitations.
7. **Implication** — language capability and civic-system competence are separable; evaluation should isolate operational mechanisms rather than report one multilingual aggregate.

Move to appendix:

- full eleven-mechanism taxonomy detail;
- complete task construction rules;
- all per-record/scorer audit anatomy;
- full sensitivity tables;
- extended literature review;
- governance chronology and reproducibility details;
- secondary mechanism tables not needed for the central causal story.

## Submission-risk gates

Before any external abstract submission, all of the following must be true:

- [ ] Genuine title + abstract frozen enough for reviewer bidding.
- [ ] Final author set known; every author has an up-to-date OpenReview profile.
- [ ] No concurrent archival submission of substantially similar work.
- [ ] Double-blind title/abstract/manuscript surface contains no author-identifying text.
- [ ] D36 recovery status is known and manuscript reproducibility claims match reality.
- [ ] AI-use disclosure reflects the actual research workflow.

Before full-paper submission:

- [ ] Main text <= 9 ICLR pages.
- [ ] ICLR 2027 style files used without forbidden formatting changes.
- [ ] All numerical claims trace to committed evidence.
- [ ] Recovery/replication results are frozen or explicitly marked unavailable.
- [ ] Scorer-audit failure and author-annotator limitation remain disclosed.
- [ ] References and related-work claims are source-verified.
- [ ] Code/data availability wording matches the private/pre-release state.
- [ ] Ethics and AI-use statements reviewed.
- [ ] Final anonymization audit passes for main paper and supplement.

## Working schedule

### Sep 14
- Candidate locked to Calendar Gap.
- ICLR prep branch and readiness gate established.
- Draft genuine abstract and AI-use disclosure.
- Inspect recovery path and provider reproducibility without executing paid/credentialed calls.

### Sep 15–16
- Execute D36 recovery only if separately authorized and credentials/versions are verified.
- Build 9-page ICLR cut from the canonical manuscript.
- Re-run mechanical claim/number/anonymity gates against the ICLR cut.

### Sep 17
- Adversarial scientific review: novelty, causal language, scorer ceiling, external validity, and related work.
- Freeze title, abstract, author set, subject areas, and keywords.

### Sep 18 AoE gate
- PI review of abstract packet.
- External OpenReview submission only under exact PI authorization.

### Sep 19–24
- Full-paper compression, figure optimization, appendix, reproducibility recovery, citations, AI/ethics disclosure, reviewer-style red team.

### Sep 25 AoE gate
- Final PDF/evidence/anonymity audit.
- External paper submission only under exact PI authorization.
