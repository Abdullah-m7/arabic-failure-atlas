# ICLR 2027 Prior-Art Rescan — 2026-09-14

Status: **NOVELTY REPAIR REQUIRED BEFORE EXTERNAL ABSTRACT**

This rescan supersedes any older repository sentence claiming that no prior work uses controlled/matched calendar variants or matched Arabic tool-use pairs.

## 1. SPAN — cross-calendar temporal reasoning

**Miao, Fu, Wei. `SPAN: Benchmarking and Improving Cross-Calendar Temporal Reasoning of Large Language Models`, arXiv:2511.09993 / AAAI 2026.**

Material overlap:

- Explicit benchmark of cross-calendar temporal reasoning.
- Covers Gregorian plus Chinese Lunar, Shaka, Hebrew, Islamic, and Persian calendars.
- Generates dynamic question/code pairs and executable ground truths.
- Reports broad model failure on cross-calendar reasoning (34.5% average across evaluated models/dates).
- Includes a tool-augmented `Time Agent` using code generation and calendar conversion tools, reaching much higher accuracy.

Important differences from Calendar Gap:

- SPAN evaluates a calendar reasoning QA task; Calendar Gap evaluates an **agent action contract** where an Arabic user request must be converted into exact structured tool calls.
- SPAN's main evaluation questions are calendar-conversion questions. Calendar Gap embeds calendar representation inside otherwise identical operational tasks, so the manipulated calendar property is a latent requirement of action rather than the explicit subject of the question.
- Calendar Gap holds the Arabic request template/tool schema/semantics fixed while toggling the date representation for the same underlying real-world date.
- Calendar Gap uses deterministic action-level scoring rather than an LLM judge for reported benchmark outcomes.
- Calendar Gap compares the calendar mechanism with other Arabic-agent mechanisms (numerals, transliteration, serialization) inside the same diagnostic instrument.

Consequence: **we cannot claim that cross-calendar LLM reasoning, Islamic-calendar reasoning, dynamic calendar gold generation, or tool augmentation for calendar conversion is new.**

## 2. MultiTempBench — multilingual / multi-calendar temporal reasoning

**Bhatia, Muhammad Isa, Peyrard, Zhao. `What Really Controls Temporal Reasoning in Large Language Models: Tokenisation or Representation of Time?`, arXiv:2603.19017 (2026).**

Material overlap:

- 15,000 examples across Arabic, English, German, Chinese, and Hausa.
- Includes Gregorian, Hijri, and Chinese Lunar calendar conditions.
- Builds controlled date-format/calendar variants from the same underlying questions.
- Directly studies mechanism-level temporal failure through tokenisation fragmentation and internal temporal geometry.
- Uses a Hijri conversion library to construct calendar variants.

Important differences from Calendar Gap:

- MultiTempBench is zero-shot **direct-answer temporal QA** with no tool use or external action contract.
- Its 750 English seed questions are translated to other languages; Calendar Gap's Arabic tasks are natively authored for the operational setting.
- MultiTempBench evaluates three temporal QA families (date arithmetic, time-zone conversion, temporal relation). Calendar Gap evaluates whether the calendar representation breaks execution of structured API actions.
- MultiTempBench uses GPT-4o as an evaluator (reported 87% agreement with majority human vote); Calendar Gap's outcome scorer is deterministic.
- Calendar Gap's central contrast is not merely date-format robustness: it is whether changing Gregorian-Arabic to Hijri-Arabic inside the same tool-use task causes an action failure while language/tool schema remain fixed.

Consequence: **we cannot claim that controlled Hijri-vs-Gregorian evaluation, Arabic Hijri reasoning, or mechanism-oriented temporal evaluation is new.**

## 3. Paired MSA–Saudi Arabic Tool-Use Test Set

**Abdullah Alsaedi, Zenodo 10.5281/zenodo.21796335, v1.0.3, 2026-08-04.**

Material overlap:

- 150 records / 75 meaning-matched MSA–Saudi Arabic pairs.
- Five deterministic mock tools.
- Designed for controlled evaluation of Arabic tool use.

Important differences:

- The manipulation is language variety (MSA vs Saudi Arabic), not calendar/civic-system representation.
- The dataset reports that each language variety was authored by a different request author, so author style is confounded with variety.
- Calendar Gap's variants are generated under one matched construction protocol and target mechanism toggles inside the same operational structure.

Consequence: **the current manuscript sentence `No study isolates a linguistic mechanism with matched pairs` is no longer defensible and must be deleted/replaced.**

## 4. Other Arabic tool-calling benchmarks

The current manuscript already covers several Arabic function-calling/tool-use benchmarks. A September rescan also surfaced public benchmark artifacts such as `arabic-agent-eval` and `ArabFuncBench`; these should be checked against the existing bibliography during the final related-work rebuild so that the ICLR submission does not rely on a stale August landscape.

## Novelty claim that remains defensible

The strongest defensible contribution is narrower and more interesting:

> **Calendar Gap tests whether a culturally situated calendar representation causes failure inside an otherwise fixed Arabic agentic action task, using matched operational variants and deterministic tool-call scoring, and contrasts that failure with other mechanisms inside the same diagnostic instrument.**

The paper should claim a contribution at the intersection of:

1. Arabic tool-using agents;
2. controlled mechanism isolation inside action tasks;
3. civic-system representation (calendar) as an operational failure source;
4. deterministic execution-level measurement.

It should **not** claim priority over cross-calendar reasoning, Hijri evaluation, controlled date variants in general, or matched-pair Arabic evaluation in general.

## Required manuscript repairs

1. Remove/rewrite: `No study isolates a linguistic mechanism with matched pairs.`
2. Add SPAN as the nearest cross-calendar benchmark and explicitly distinguish direct calendar QA/tool-augmentation from calendar-as-input in a business/API action contract.
3. Add MultiTempBench as the nearest controlled multilingual/Hijri temporal benchmark and distinguish direct-answer QA + translated seeds + LLM judge from native Arabic tool action + deterministic scorer.
4. Add the Paired MSA–Saudi test set as a recent matched Arabic tool-use design and narrow any matched-pair novelty claim.
5. Reframe the contribution from `we discover that Hijri reasoning is weak` to `we localize how calendar representation creates an execution failure inside an Arabic agentic pipeline while language-only and numeral controls remain strong`.
6. Re-run a current-literature check immediately before full-paper freeze because this topic is moving quickly.
