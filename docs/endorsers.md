# Endorser contact extraction (offline, from refs/ PDFs only)

Source discipline: everything below comes from the already-downloaded PDFs
in `refs/` (author blocks / correspondence footnotes) or, where noted, from
`paper/refs.bib` Phase-0 cards. No network access was used; nothing was sent.
Extraction: the pre-extracted `refs/*.txt` sidecars, grepped for `@` patterns
across full text (headers, footnotes, acknowledgments).

## PDF availability

| paper | PDF in refs/ | emails found |
|---|---|---|
| P1 (kubrak2026arabicprompts) | NOT PRESENT — carded from Phase-0 scan, never downloaded | n/a |
| P2 (ersoy2025toolcalling, QCRI) | refs/p2.pdf | yes — 4, first page |
| P3 (nacar2026language) | NOT PRESENT — carded from Phase-0 scan, never downloaded | n/a |
| P4 (bariah2026telcoagent) | refs/p4.pdf | yes — 6, first page |
| S1 (kulkarni2025massive) | refs/massive_agents.pdf | yes — 5, correspondence footnote |

## Ranked contact table

| rank | name | paper | email | why-them |
|---|---|---|---|---|
| 1 | Kubrak (+ El-Moselhy, Alsulami, Altuwaim, Fawaz, Alsaby — first names TODO-verify per refs.bib) | P1 | NO PDF in refs/ — email pattern findable via the paper's IEEE / arXiv (2601.05101) page — flag for the research lead's web session | P1 corresponding authors — our paper directly answers their stated future work (native Arabic tool-calling benchmark + root-cause investigation) |
| 2 | Nacar (+ 24 co-authors, Tuwaiq Academy et al.) | P3 | NO PDF in refs/ — email pattern findable via the paper's arXiv (2603.16901) page — flag for the research lead's web session | P3 corresponding author — their date-format semantic-drift observation is the un-isolated smoke our M2 isolates |
| 3 | Kareem Darwish | P2 (QCRI) | kdarwish@hbku.edu.qa | backup tier — senior author of the closest published signal to our M6 (Translation Discrepancy class); QCRI anchors Arabic NLP evaluation |
| 4 | Asim Ersoy | P2 (QCRI) | aersoy@hbku.edu.qa | backup tier — P2 first author |
| 5 | Enes Altinisik | P2 (QCRI) | ealtinisik@hbku.edu.qa | backup tier — P2 co-author |
| 6 | Husrev Taha Sencar | P2 (QCRI) | hsencar@hbku.edu.qa | backup tier — P2 co-author |

## Extracted but outside the requested ranking (for completeness)

| name | paper | email | note |
|---|---|---|---|
| Lina Bariah | P4 | lina.bariah@ku.ac.ae | P4 first author (Khalifa University) |
| Brahim Mefgouda | P4 | brahim.mefgouda@ku.ac.ae | P4 co-author |
| Mérouane Debbah | P4 | merouane.debbah@ku.ac.ae | P4 senior author |
| Farbod Tavakkoli | P4 | farbod.tavakkoli@att.com | P4 co-author (AT&T CDO) |
| Enrique Molero | P4 | emolero@gsma.com | P4 co-author (GSMA) |
| Louis Powell | P4 | lpowell@gsma.com | P4 co-author (GSMA) |
| Mayank Kulkarni | S1 | maykul@amazon.com | S1 correspondence line (MASSIVE-Agents) |
| Vittorio Mazzia | S1 | vmazzia@amazon.com | S1 correspondence line |
| Judith Gaspers | S1 | gaspers@amazon.com | S1 correspondence line |
| Christopher Hench | S1 | henchc@amazon.com | S1 correspondence line |
| Jack FitzGerald | S1 | jgmf@amazon.com | S1 correspondence line |

## Per-paper notes

- **P1 — no PDF in refs/**: only the Phase-0 card exists (refs.bib, surnames
  only, first names flagged TODO-verify). Email pattern findable via the
  paper's IEEE BigData workshop / arXiv page — flag for the research lead's
  web session.
- **P2** — all four author emails printed on page 1 as a brace group
  `{aersoy,ealtinisik,hsencar,kdarwish}@hbku.edu.qa`; expanded above. No
  explicit corresponding-author marker; Darwish is listed last (senior).
- **P3 — no PDF in refs/**: Phase-0 card only ("Nacar and others", 25
  authors). Email pattern findable via the paper's arXiv page — flag for
  the research lead's web session.
- **P4** — emails printed on page 1 (`Emails:` line); brace groups expanded
  above. No explicit corresponding-author marker.
- **S1** — explicit `Correspondence:` footnote on page 1; expanded above.

Nothing was sent to anyone; this file is contact extraction only.
