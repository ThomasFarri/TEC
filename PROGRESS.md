PROJECT COMPLETE (2 Nov 2026). All backlog items done. Remaining work is Thomas's: review, check every number, export the note to PDF, decide whether to send.

# Progress log

Read PROJECT_PLAN.md first. Pick the first unchecked item in the backlog, finish it, then tick it and add a dated log entry.

## Backlog (in order)
- [x] v1 equilibrium model, tests, three figures (31 Oct)
- [x] Validation 1 (1 Nov): find NASA LH2 no-vent fill test data (K-Site, NASA Lewis/Glenn, early 1990s, e.g. Moran, Nyland, Driscoll; also Chato's charge-hold-vent work) via NTRS abstract pages. Extract test conditions (tank volume, wall mass, initial wall T, inlet T, final fill, final pressure). Write scripts/validate_nvf.py comparing model vs test. Record sources in VALIDATION.md. If data are only in PDFs that cannot be fetched, list the exact papers in VALIDATION.md under "Thomas to download".
- [x] Validation 2 (1 Nov): line chilldown vs Hartwig / NASA Glenn LN2 and LH2 chilldown tests (mass of propellant to chill a line), same approach.
- [x] v2 (1 Nov): transient line chilldown (1D wall nodes, flow-boiling correlations from Hartwig et al.), giving chilldown time. New module cryotransfer/transient.py with tests.
- [x] Sensitivity study (2 Nov): inlet subcooling, receiver pressure limit, initial wall temperature, tank material (Al vs SS). Figure 4.
- [x] Technical note draft (2 Nov) (notes/technical_note.md, 4 to 6 pages): problem, method, validation, results, limitations, questions for TEC.
- [x] "Defend this" sheet (2 Nov) for Thomas (notes/defend_this.md): key assumptions and likely interview questions with short answers.
- [x] LinkedIn post draft and outreach message draft (2 Nov) (notes/outreach.md). Do NOT send anything.

## Theory lessons (every run)
For every backlog item completed, write a lecture-style lesson in notes/lessons/NN_topic.md for Thomas (final-year aerospace MEng student). Teach like his lecturer: start from first principles, explain why each equation holds and what each assumption means physically, use one worked example with real numbers from this model, show what goes wrong if an assumption fails, and end with 3 to 5 self-test questions with answers hidden under a "Answers" heading. Cite textbooks or papers with links where possible. Plain prose, no long dashes.

## Rules for every run
- Run `python -m pytest -q` before committing. Never commit failing tests.
- Small commits with clear messages. Push to main.
- Never contact anyone, post anything, or make the repo public.
- Write plainly. No long dashes in prose.

## Log
- 2026-10-31: v1 model done. Key result: wall energy / load cooling capacity is ~3 % for LOX and LCH4 vs ~24 % for LH2 (1 m3 Al tank, 40 kg wall, from 290 K).
- 2026-11-01: Validation 1, Validation 2 and v2 done (lessons 02 to 04). No-vent fill: equilibrium model vs 32 NASA LH2 fills (TM-106018, TM-106293), mean absolute error 7 % in final pressure, max 26 % (warm-inlet spray-bar runs, non-equilibrium). Line chilldown: no flight test beats the thermodynamic minimum; real efficiency 3 to 69 % (bare tube at high flow about 4 %). v2 transient model, film boiling calibrated on one test (C_fb = 2.41), other high-flow tests within 17 %; fails at low flow (3 to 6 times too slow), range limit stated. 3 m LOX line: 2.4 to 3.4 kg. Push from the scheduled run was refused (403), so Thomas pushes these commits by hand. Next: sensitivity study (figure 4).
- 2026-11-02: Sensitivity study done (lesson 05, figures/fig4_sensitivity.png, scripts/run_sensitivity.py). Key result: LOX CHV loss falls from 5.5 % of load at 0 K inlet subcooling to 0.44 % at 5 K and 0 at 10 K (LCH4: 13 % to 1.4 % to 0); the receiver limit and start temperature act the same way, because wall energy is only about 3 % of load cooling capacity so the system sits near a threshold. SS304 is better than Al at equal mass but worse (1.4 % vs 0.44 % LOX) at equal wall thickness. CHV is a staircase in whole cycles, so read the flow-through band for trends. Next: technical note draft.
- 2026-11-02 (later): Technical note drafted (notes/technical_note.md, about 1800 words, four figures, lesson 06). Structure: problem, method, validation, results, limitations, questions for TEC. Thomas must read it fully and check every number against the results files. PDF/doc export not done (no converter run yet). Next: defend-this sheet.
- 2026-11-02 (later): Defend-this sheet done (notes/defend_this.md, lesson 07). Assumption ledger with bias direction, 14 likely questions, numbers to memorise. Next: outreach drafts.
- 2026-11-02 (later): Outreach drafts done (notes/outreach.md, lesson 08). Nothing sent or posted. Backlog complete. Thomas to do: (1) read the technical note against results files, (2) export it to doc and PDF (not done here), (3) read the Thomas-to-download list in VALIDATION.md, (4) decide on sending.
