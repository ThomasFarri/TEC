# Validation

This file records every piece of test data used to check the model, where it came from, how it was used, and how well the model did. No test numbers are invented. Where a value was not in a source, the assumption made is stated.

## Validation 1: no-vent fill against NASA Lewis LH2 tests

Script: `scripts/validate_nvf.py`. Data: `data/nvf_lh2_tests.csv`. Results: `results/validation_nvf*.csv`, `figures/fig5_validation_nvf.png`. Tests: `tests/test_validation_nvf.py`.

### Sources used

| ID | Report | NTRS | What was taken |
|---|---|---|---|
| A | Taylor, W.J. and Chato, D.J., "Comparing the Results of an Analytical Model of the No-Vent Fill Process With No-Vent Fill Test Results for a 4.96 m3 (175 ft3) Tank", NASA TM-106018, 1993 (28th Joint Propulsion Conference, 1992) | [19930017966](https://ntrs.nasa.gov/citations/19930017966) | Table I, 11 fills: initial wall T, inlet T, flow, final pressure, final fill (94 %). Tank 4.96 m3, 2219 Al, 149.63 kg. Heat leak 4.66 W. |
| B | Chato, D.J., "Ground Testing for the No-Vent Fill of Cryogenic Tanks: Results of Tests for a 71 Cubic Foot Tank", NASA TM-106293, AIAA-93-1967, 1993 | [19940013013](https://ntrs.nasa.gov/citations/19940013013) | Table 1, 22 fills (12 spray bar, 10 bottom orifice), printed in R, lbm/hr, psia. Tank 71 ft3, 2219 Al, 243 lb, stated 3.41 lb/ft3. |

Both PDFs were read in full on NTRS (OCR text). Table values were transcribed as printed.

Other reports found and read but not used for the quantitative comparison:

- Chato, Moran, Nyland, "Initial experimentation on the nonvented fill of a 0.14 m3 (5 ft3) dewar with nitrogen and hydrogen", NASA TM-103155, AIAA-90-1681, 1990, NTRS [19900016962](https://ntrs.nasa.gov/citations/19900016962). Five LH2 runs (Table II), but the receiver wall mass is not given, so the equilibrium model cannot be run without guessing it.
- Moran, Nyland, Driscoll, "Hydrogen no-vent fill testing in a 1.2 cubic foot (34 liter) tank", NASA TM-105273, 1991, NTRS [19920004183](https://ntrs.nasa.gov/citations/19920004183). 42 runs, but the run table in Appendix C and the wall mass (7.89 lbm, possibly) could not be read reliably from the OCR. Not used until checked by hand (see below).
- Chato, "Ground Testing on the Nonvented Fill Method of Orbital Propellant Transfer: Results of Initial Test Series", NASA TM-104444, AIAA-91-2326, 1991, NTRS [19910015234](https://ntrs.nasa.gov/citations/19910015234). Same 4.96 m3 tank as source A. Its Appendix A runs were affected by a burst-disk leak and the authors say the absolute pressures are "not to be trusted", so they are excluded.
- Moran, Nyland, Papell, NASA TM-102572, 1990, NTRS [19900011979](https://ntrs.nasa.gov/citations/19900011979). Abstract only.

### Method

For each test, the model takes the tank volume and whole wall mass at the measured initial wall temperature, with hydrogen vapour in the ullage, and adds inlet liquid at the measured average inlet temperature until the measured final fill level. The output is the equilibrium pressure at that fill, compared with the measured final pressure.

Assumptions:

1. Fluid is para-hydrogen (CoolProp `ParaHydrogen`). Normal hydrogen gives pressures about 3 % lower; both are in the results CSV.
2. Inlet enthalpy is saturated liquid at the measured inlet temperature. The reports give only time-averaged inlet temperature.
3. Wall cp uses the NIST Al 6061 fit as a stand-in for Al 2219. Both are aluminium alloys and their cp curves are close, but this has not been checked against a 2219 dataset.
4. Initial ullage pressure is not tabulated. 7 kPa is assumed, capped below saturation at the wall temperature. Changing it to 1 kPa moves the prediction by -0.4 % to -2.4 %; changing it to 50 kPa moves it by +3 % to +15 %, the largest effect being on the low-pressure tank B runs (`results/validation_nvf_sensitivity.csv`).
5. Heat leak: 4.66 W for tank A (from source A), over the fill time (load mass / flow, 40 to 50 minutes). It adds about 12 kJ, against roughly 3 MJ of wall energy for a 100 K wall. None for tank B (not reported).
6. Test 330 (tank B, 129 K wall) failed in the test. The pressure spike during the initial wall cooldown exceeded the supply pressure, so the fill never started properly. It is kept in the table but left out of the error statistics.

### Results

| Set | Runs | Mean error | Mean absolute error | Max absolute error | Mean absolute error |
|---|---|---|---|---|---|
| A, 4.96 m3 | 11 | +2.7 % | 7.7 % | 20.0 % | 16.0 kPa |
| B, 2.01 m3 | 21 | -5.0 % | 6.6 % | 26.3 % | 9.9 kPa |
| All | 32 | -2.3 % | 7.0 % | 26.3 % | 12.0 kPa |

Error is (model minus test) / test, for final pressure at the measured final fill.

For comparison, source A reports that its own equilibrium model ran "within 0.0345 MPa (5 psia) for most cases" and that predicted final pressures for bottom spray were "within 0.0172 MPa (2.5 psia)". Our mean absolute error of 16 kPa on the same tank is consistent with that.

### What the errors say

- **Inlet temperature dominates.** The model's final pressure always sits just above the saturation pressure of the inlet liquid. The sensitivity is about 50 kPa per kelvin of inlet temperature for LH2 near 23 K. A ±0.5 K inlet uncertainty, which source A quotes in its error budget, moves the prediction by +12 % to +21 % (warmer) or -11 % to -18 % (colder). So most of the scatter is within the input uncertainty.
- **Wall temperature matters less than expected for LH2 at these wall masses.** Even a 126 K wall (Fill 20) adds only about 80 kPa above inlet saturation, and the model gets that run to 2 %.
- **The biggest misses are underpredictions with the spray bar and warm inlet liquid** (tank B tests 286, 324, 337 and 339, inlet 20.6 to 21.8 K, errors -16 % to -26 %). The bottom-orifice runs at the same inlet temperatures agree within 10 %. This is the signature of non-equilibrium: with warm inlet liquid there is little subcooling to condense ullage vapour, and the spray bar mixed the ullage less well than the orifice jet in these runs. The equilibrium model cannot see injection hardware, so it underpredicts. This matches the physics in lesson 1: equilibrium is a best case.
- **The two largest overpredictions** (Fill 19, +18 %; K2091, +20 %) are both top spray in tank A, with the warmest inlet liquid in that set (23.0 and 23.4 K). The likeliest explanation is that the time-averaged inlet temperature overstates the liquid temperature for most of the fill. This is a guess and is not checked.
- **Failed test 330.** The model says a 95 % fill would end at 114 kPa, well inside the limit. The test failed anyway, because the pressure spike during the first seconds of wall cooldown exceeded the supply pressure and stopped inflow. An equilibrium model cannot predict this transient. Source B says the same about its own equilibrium code: good agreement "with the exception of the initial wall cooldown". This is the strongest argument for the v2 transient model.

### Honest limits

- The comparison is only for final pressure at final fill. The pressure history during the fill (including the initial spike) is not compared, because it is only in figures.
- All validation is LH2 at wall masses of 30 to 55 kg/m3. LOX and LCH4 have much smaller wall-to-load energy ratios (lesson 1), so the equilibrium model should be at least as good for them on final pressure. That is an argument, not a validation.
- Tank B results for warm inlet with the spray bar show that the model can underpredict final pressure by about a quarter. A design margin of that order on pressure is advisable before relying on equilibrium predictions.

## Thomas to download

These would strengthen Validation 1. Please download the PDFs from NTRS and drop them in a `refs/` folder (not committed if large).

1. Moran, M.E., Nyland, T.W., Driscoll, S.L., "Hydrogen No-Vent Fill Testing in a 1.2 Cubic Foot (34 Liter) Tank", NASA TM-105273, 1991, NTRS 19920004183. Needed: the Appendix B wall mass of the small receiver and the Appendix C run table (pages 39 to 40), checked by eye, because the OCR is garbled. This would add 42 small-tank runs with a very different wall-to-volume ratio.
2. Chato, D.J., Moran, M.E., Nyland, T.W., NASA TM-103155, 1990, NTRS 19900016962. Needed: the receiver wall mass (not stated in the text, perhaps in a drawing or a companion report).
3. Taylor, W.J., Chato, D.J., NASA TM-104492, 1991, on improved thermodynamic modelling of the no-vent fill process (cited by source A; exact title not yet confirmed). Describes the equilibrium model used at Lewis.
4. Chato, D.J., NASA TM-102039, 1989, analysis of the 4.96 m3 tank no-vent fill. Cited by source A.
