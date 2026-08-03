# Related-Work Pack

Machine-assembled from refs/ (full-text where held), docs/phase0.md (frozen
snapshot), and docs/phase0_5_findings.md. Anchor quotes are the previously
verified ones — no new claims. Entries whose metadata came only from the
Phase-0 scan (not a full read in this repo) are marked **[VERIFY AT RE-SCAN]**
and are on the DC1 re-scan checklist. BibTeX keys ↔ paper/refs.bib.

---

## P1 — Arabic Prompts with English Tools: A Benchmark  `[kubrak2026arabicprompts]`
- **Citation:** Kubrak, El-Moselhy, Alsulami, Altuwaim, Fawaz, Alsaby.
  arXiv:2601.05101, 8 Jan 2026. LLMs4All Workshop @ IEEE BigData 2025 (Macau).
  Code: github.com/kubrak94/gorilla (BFCL fork).
- **Summary:** Adapts BFCL to Arabic via automated translation and runs 784
  experiments over a 2^4 design (system-prompt lang × invocation style × query
  lang × function-description lang) on five open-weight models. Documents the
  aggregate collapse (350 EN wins / 10 AR wins) and shows full localization of
  function descriptions makes things worse.
- **Anchors:** "comparing the Abstract Syntax Tree (AST) of the model's
  generated function call" (§III-E); "80-90% accuracy with English prompts...
  plummet to 40-60%" (§IV-C1); "internal logic for tool-use is fundamentally
  English-centric" (§IV-D); §V calls for "native Arabic tool-calling benchmarks
  and datasets, developed from scratch" and "deeper investigation into the root
  causes... tokenization inefficiencies, biases in pre-training data".
- **Relation to Atlas:** NEAR-NEIGHBOR — the aggregate gap whose mechanism
  decomposition we provide; also the source of the M10 English-schema constant.
  **[VERIFY AT RE-SCAN]** (carded in Phase 0; full text not re-read in this repo).

## P2 — Tool Calling for Arabic LLMs: Data Strategies and Instruction Tuning  `[ersoy2025toolcalling]`
- **Citation:** Ersoy, Altinisik, Sencar, Darwish (QCRI). ArabicNLP 2025
  (2025.arabicnlp-main.28); arXiv:2509.20957. Full text read (refs/p2.pdf).
- **Summary:** Machine-translates Glaive and xLAM into Arabic (Gemini-2.5-Flash)
  and runs five fine-tuning configurations on Fanar-1-9B to study cross-lingual
  transfer, general SFT effects, and tool-specific FT. Error analysis attributes
  most Arabic argument failures to wrong-language argument values.
- **Anchors:** "we translated them into Arabic using Gemini-2.5-Flash" (§3);
  "Translation Discrepancy (T), making up 38.2% of errors" and "the leading
  cause of failure (53.1% of all Arabic errors)" (§5.5); normalization includes
  "standardization of date formats and numerical representations" (§4.3).
- **Relation to Atlas:** METHODOLOGY-ADJACENT EVIDENCE — its post-hoc
  Translation-Discrepancy category motivates M6 but is not a designed
  isolation (phase0_5 §6); its normalization protocol erases M2/M3/M7.

## P3 — From Language to Action in Arabic (AISA-AR-FunctionCall)  `[nacar2026language]`
- **Citation:** Nacar et al. (25 authors), Tuwaiq Academy + Tahakom, Wakeb,
  Qatmeer, NCGR, Vision Bank. arXiv:2603.16901, 4 Mar 2026. CC BY-SA 4.0.
- **Summary:** Fine-tuning study (FunctionGemma 270M) on the repaired
  HeshamHaroon Arabic function-calling dataset across five Arabic varieties;
  baseline shows >87% structural parse failure, FT shifts errors "from
  structural collapse to semantic misalignment". No English control set.
- **Anchors:** "50,810 samples spanning 36 tools, five major Arabic dialects"
  (§3.2); "More than 87% of outputs fail to produce a valid structured function
  call" (§4); "argument values exhibit semantic drift (e.g., normalized date
  formats, lexical variations)" (§4.2).
- **Relation to Atlas:** NEAR-NEIGHBOR — dialect-aggregate coverage (canonical
  M5) and the qualitative M2/M3 smoke we isolate. **[VERIFY AT RE-SCAN]**
  (carded in Phase 0; full text not re-read in this repo).

## P4 — TelcoAgent-Bench  `[bariah2026telcoagent]`
- **Citation:** Bariah, Mefgouda, Tavakkoli, Molero, Powell, Debbah. Khalifa
  University / AT&T / GSMA. arXiv:2604.06209. Full text read (refs/p4.pdf).
- **Summary:** Bilingual (EN/AR) telecom troubleshooting benchmark: 15 intents,
  49 blueprints, ~1,470 synthetic dialogues; metrics for intent recognition,
  ordered tool execution (LCS-based), resolution accuracy, and stability across
  scenario variations. IRA and RA use embedding cosine similarity.
- **Anchors:** "designed to operate in both English and Arabic" (Abstract);
  "15 intents, 49 blueprints, and ∼1,470 dialogues" (§II); "embedding-based
  semantic similarity approach" (§III-A1).
- **Relation to Atlas:** METHODOLOGY IMPORT (stability-across-variations idea)
  + EXCLUDED-BY-DESIGN EVIDENCE (its headline metrics are model-based; the
  Atlas is deterministic-only).

## S1 — MASSIVE-Agents  `[kulkarni2025massive]`
- **Citation:** Kulkarni, Mazzia, Gaspers, Hench, FitzGerald (Amazon AGI).
  Findings of the ACL: EMNLP 2025, pp. 20193–20215. Full text held
  (refs/massive_agents.pdf).
- **Summary:** Reformats the human-localized MASSIVE corpus into BFCL-style
  function calling across 52 languages (47,020 samples); AST/FSA evaluation of
  21 models shows large cross-lingual disparities (ar-SA 36.13% vs en-US 57.37%
  best-model AST). Prompt/description translation ablations prefer English.
- **Anchors:** "47,020 samples with an average of 904 samples per language"
  (Abstract); "we do not post-process any date timestamps" (§2.4); ablation
  results "suggesting a preference for English instructions".
- **Relation to Atlas:** NEAR-NEIGHBOR (multilingual aggregate) + double anchor
  for M10; its verbatim-date rule is direct evidence M2 is excluded by design
  in prior work.

## S2 — Arabic LLM Evaluation Survey  `[arabicsurvey2025]`
- **Citation:** arXiv:2510.13430. **[VERIFY AT RE-SCAN — author list not
  re-verified in this repo.]**
- **Summary:** Surveys Arabic LLM evaluation practice; records the OALL v2 move
  to native benchmarks and the lack of validation for Arabic LLM-as-judge.
- **Anchors (as recorded in Phase 0):** community consensus "against translated
  content"; LLM-judge validation gaps; circular-evaluation risk.
- **Relation to Atlas:** DESIGN-MANDATE SOURCE — native authorship +
  deterministic scoring.

## MAST  `[cemri2025mast]`
- **Citation:** Cemri et al., arXiv:2503.13657. **[VERIFY AT RE-SCAN]**
- **Summary (as recorded in Phase 0):** 14 agent failure modes over 1,600+
  annotated traces with κ=0.88 inter-annotator agreement.
- **Relation to Atlas:** METHODOLOGY IMPORT — the annotation-rigor anchor for
  our DC3 human-audit gate.

## AgentErrorTaxonomy / AgentErrorBench  `[agenterror2025]`
- **Citation:** arXiv:2509.25370. **[VERIFY AT RE-SCAN]**
- **Summary (as recorded in Phase 0):** 200 annotated failure trajectories
  from ALFWorld/GAIA/WebShop focused on error propagation.
- **Relation to Atlas:** ORTHOGONAL-AXIS CONTRAST — classifies WHAT failed;
  the Atlas classifies WHICH linguistic property caused it.

## ToolScan  `[toolscan]`
- **Citation:** **[VERIFY AT RE-SCAN — identifier not recorded in Phase 0.]**
- **Summary (as recorded in Phase 0):** "seven error patterns in tool-use
  tasks" — outcome categories (wrong tool, bad args).
- **Relation to Atlas:** ORTHOGONAL-AXIS CONTRAST (outcome taxonomy, not
  linguistic causes).

## AgentHallu  `[agenthallu]`
- **Citation:** **[VERIFY AT RE-SCAN — identifier not recorded in Phase 0.]**
- **Summary (as recorded in Phase 0):** 693 trajectories, 5 hallucination
  categories; frontier models at 41.1% step localization.
- **Relation to Atlas:** ORTHOGONAL-AXIS CONTRAST.

## Aegis  `[aegis2025]`
- **Citation:** arXiv:2508.19504. **[VERIFY AT RE-SCAN]**
- **Summary (as recorded in Phase 0):** agent-environment failure taxonomy.
- **Relation to Atlas:** ORTHOGONAL-AXIS CONTRAST.

## AgentAtlas  `[agentatlas2026]`
- **Citation:** arXiv:2605.20530, May 2026. **[VERIFY AT RE-SCAN]**
- **Summary (as recorded in Phase 0):** control-decision + trajectory-failure
  taxonomies with a benchmark coverage audit.
- **Relation to Atlas:** NAME-COLLISION EVIDENCE — forced the public rename
  (Phase 0 D4 adjustment 2); also an orthogonal-axis taxonomy.
