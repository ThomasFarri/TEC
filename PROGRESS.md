# Progress log

Read PROJECT_PLAN.md first. Pick the first unchecked item in the backlog, finish it, then tick it and add a dated log entry.

## Backlog (in order)
- [x] v1 equilibrium model, tests, three figures (31 Oct)
- [ ] Validation 1: find NASA LH2 no-vent fill test data (K-Site, NASA Lewis/Glenn, early 1990s, e.g. Moran, Nyland, Driscoll; also Chato's charge-hold-vent work) via NTRS abstract pages. Extract test conditions (tank volume, wall mass, initial wall T, inlet T, final fill, final pressure). Write scripts/validate_nvf.py comparing model vs test. Record sources in VALIDATION.md. If data are only in PDFs that cannot be fetched, list the exact papers in VALIDATION.md under "Thomas to download".
- [ ] Validation 2: line chilldown vs Hartwig / NASA Glenn LN2 and LH2 chilldown tests (mass of propellant to chill a line), same approach.
- [ ] v2: transient line chilldown (1D wall nodes, flow-boiling correlations from Hartwig et al.), giving chilldown time. New module cryotransfer/transient.py with tests.
- [ ] Sensitivity study: inlet subcooling, receiver pressure limit, initial wall temperature, tank material (Al vs SS). Figure 4.
- [ ] Technical note draft (notes/technical_note.md, 4 to 6 pages): problem, method, validation, results, limitations, questions for TEC.
- [ ] "Defend this" sheet for Thomas (notes/defend_this.md): key assumptions and likely interview questions with short answers.
- [ ] LinkedIn post draft and outreach message draft (notes/outreach.md). Do NOT send anything.

## Rules for every run
- Run `python -m pytest -q` before committing. Never commit failing tests.
- Small commits with clear messages. Push to main.
- Never contact anyone, post anything, or make the repo public.
- Write plainly. No long dashes in prose.

## Log
- 2026-10-31: v1 model done. Key result: wall energy / load cooling capacity is ~3 % for LOX and LCH4 vs ~24 % for LH2 (1 m3 Al tank, 40 kg wall, from 290 K).
