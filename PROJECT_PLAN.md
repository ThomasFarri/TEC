# Project Plan: LOX/LCH4 In-Orbit Transfer Loss Model

Owner: Thomas Farrugia. Target reader: Cédric Dupont, Head of Cryogenic Refueling and Luxembourg Operations, The Exploration Company (TEC). Started 31 Oct 2026. Target completion: 21 Nov 2026. Send date: Thomas's call.

## Goal
Predict how much propellant is lost, and how long it takes, when transferring liquid oxygen and liquid methane between two spacecraft in microgravity. The losses come from chilling down a warm transfer line and receiver tank, followed by a no-vent fill. Validate the method against published NASA hydrogen test data, then apply it to LOX and LCH4, where public data is thin.

## Why it matters to TEC
TEC Luxembourg leads ESA InSPoC-2, which covers in-orbit cryogenic storage, transfer and mating, and targets launch in 2030. Its open roles ask for thermal architectures and fluid management requirements. Chilldown and fill strategy drive both.

## Deliverables
1. A Python package on GitHub with tests and a README.
2. A technical note of 4 to 6 pages, delivered as a doc and a PDF.
3. One LinkedIn post with a key figure.
4. An outreach message to Cédric.

## Model scope
**v1, energy budget (equilibrium).**
- Fluids: O2, CH4, plus H2 for validation. Properties come from CoolProp.
- Materials: temperature-dependent specific heats for 6061 aluminium and 304 stainless steel, using NIST cryogenic fits.
- Line chilldown: propellant mass needed to cool the line wall, bounded between saturated-vapour exit and exit at wall temperature.
- Receiver chilldown, strategy A (charge-hold-vent): repeated charge, equilibrate, vent cycles, limited by the pressure cap on each charge.
- Receiver chilldown, strategy B (continuous flow-through vent).
- No-vent fill: homogeneous equilibrium of fluid plus wall. Output is the achievable fill fraction versus the receiver pressure limit.
- Key outputs: total propellant lost, fill fraction achieved, number of cycles, and sensitivities to wall mass, line length, initial temperature, inlet subcooling and pressure limit.

**v2, time-resolved.**
- Transient line chilldown using published flow-boiling chilldown correlations (Hartwig, NASA Glenn).
- Gives transfer time, not just mass.

## Validation
- NASA NTRS: K-Site and Glenn no-vent fill and chilldown test data, mostly LH2.
- Compare predicted final pressure and fill fraction against those tests, and state the error honestly.
- Equilibrium is a best-case bound: real non-equilibrium tanks reach higher pressure. Say so in the note.

## Timeline
| Week | Dates | Work |
|---|---|---|
| 1 | 31 Oct to 7 Nov | v1 model, tests, first results and figures |
| 2 | 8 to 14 Nov | NTRS validation against LH2 data, v2 transient chilldown |
| 3 | 15 to 21 Nov | Parametric studies, technical note, README, LinkedIn post, outreach draft |
| After | Thomas decides | Review, own every assumption, send |

## Rule
Thomas must be able to explain every assumption and every figure in a 15-minute call without notes. The model is only worth something if he can defend it.
