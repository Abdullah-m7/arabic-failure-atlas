# DC1 Re-Scan Checklist — run the day before preprint submission

Purpose: re-verify the kill condition (no benchmark isolates linguistic failure
mechanisms in Arabic agents with matched pairs) against anything published since
the Phase-0 scan (2026-08-02). arXiv moves fast. NO searches now — this file is
the recipe. Log findings in a dated docs/dc1_rescan_<date>.md; update
paper/related_pack.md, refs.bib TODO-verify entries, and the phase0_5 matrix if
any cell changes. If a new source ISOLATES M2, M4, or M6 with matched pairs →
escalate to research lead before submitting (DC1 re-opened).

## Queries (run each on: arXiv full-text search, Google Scholar, ACL Anthology)

Coverage-driven (mechanism × domain):
- [ ] "Arabic function calling" / "Arabic tool calling" / "Arabic tool use benchmark"
- [ ] "Arabic LLM agent" evaluation / benchmark
- [ ] "multilingual function calling" benchmark (2026 onward)
- [ ] "Hijri" OR "Islamic calendar" LLM / language model
- [ ] "Umm al-Qura" LLM
- [ ] transliteration OR romanization consistency LLM agent
- [ ] "code-switching" agent OR tool calling
- [ ] Arabic "language discipline" OR "language leakage" LLM
- [ ] Arabic dialect tool calling / function calling
- [ ] Eastern Arabic numerals LLM
- [ ] agent failure taxonomy (2026 onward — orthogonal-axis line)

Name-collision re-check for the chosen public name:
- [ ] exact-name search on arXiv, GitHub, HuggingFace, Google
- [ ] re-check "AgentAtlas" successors / similar names

TODO-verify completions (refs.bib):
- [ ] kubrak2026arabicprompts — full author names
- [ ] nacar2026language — exact title + author list
- [ ] arabicsurvey2025 (2510.13430) — title + authors
- [ ] cemri2025mast (2503.13657) — title + authors
- [ ] agenterror2025 (2509.25370) — title + authors
- [ ] toolscan — locate identifier, or drop citation
- [ ] agenthallu — locate identifier, or drop citation
- [ ] aegis2025 (2508.19504) — title + authors
- [ ] agentatlas2026 (2605.20530) — title + authors

## Venues to scan by listing (since 2026-08)

- [ ] arXiv cs.CL + cs.AI listings, keyword-filtered on Arabic/agent/tool
- [ ] ACL Anthology: ArabicNLP 2026, ACL/EMNLP/NAACL Findings 2026
- [ ] HuggingFace datasets: search "arabic function calling", "arabic agent"
- [ ] BFCL leaderboard changelog (new multilingual categories?)
- [ ] OALL leaderboard v2+ changes (native-benchmark policy shifts)

## Recording rule

For every hit: paper_id, one-line design summary, and the three-way verdict
per mechanism (COVERED / PARTIAL / ABSENT) with an anchor quote ≤20 words —
same evidence discipline as Phase 0.5. Anything ambiguous goes to the research
lead with the quote, not a paraphrase.
