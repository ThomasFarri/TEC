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

## Validation 2: line chilldown against NASA LN2 flight tests

Script: `scripts/validate_chilldown.py`. Data: `data/chilldown_ln2_flight_tests.csv`. Results: `results/validation_chilldown.csv`, `figures/fig6_validation_chilldown.png`. Tests: `tests/test_validation_chilldown.py`.

### Source used

Hartwig, J., Chung, J.N., Dong, J., Han, B., Wang, H., Darr, S., Taliaferro, M., Jain, S., Doherty, M., "Nitrogen flow boiling and chilldown experiments in microgravity using pulse flow and low-thermally conductive coatings", npj Microgravity 8:33 (2022), doi:10.1038/s41526-022-00220-9, open access at https://pmc.ncbi.nlm.nih.gov/articles/PMC9363417/. Full text read.

Taken: Table 1, 28 parabolic-flight tests (0.05 g and 0.38 g) giving inlet pressure, continuous or pulse flow, coating, chilldown time, total chilldown mass and steady Reynolds number. Test section from the Methods: "0.914 m (36 in) long, 0.051 cm wall thickness, 1.27 cm outer diameter SS304". The bare tube and tubes with 4 and 7 layers of FEP (Teflon) coating, about 15 um per layer, were flown. The paper states 2.5 % uncertainty on mass consumed.

### Method

The v1 function `wall_chilldown_mass` gives two thermodynamic bounds on the LN2 needed to cool the tube: the best case, where vapour leaves at the local wall temperature, and the saturated-vapour case. The best case is a true lower limit: no test can use less. So this comparison does not ask "does the model match?" but "how close do real chilldowns get to the limit?". The ratio m_best / m_measured is called the chilldown efficiency here.

Assumptions:

1. Initial wall temperature 290 K. The paper does not give it, only that tubes were reheated with warm gas between tests. Using 250 K or 300 K changes m_best by -19 % or +4 %.
2. Inlet is saturated liquid at the measured inlet pressure (inlet temperature is not given numerically).
3. Vapour leaves at 101 kPa (outlet pressure not given numerically).
4. Chilldown ends with the wall at T_sat(inlet) + 2 K.
5. Only the 0.141 kg test-section tube is counted (304 SS density 7900 kg/m3). The paper does not say how much plumbing downstream of the test section, before the gas meter, was also cooled by the metered flow. Any extra metal makes the measured mass larger, so the efficiencies below are lower bounds.

### Results

The thermodynamic band for this tube is 0.039 to 0.067 kg (best case to saturated vapour). The measured masses run from 0.056 kg to 1.17 kg. Every test uses more than the best-case limit, as it must; this is checked in the test suite.

| Group | Tests | Efficiency range | Mean |
|---|---|---|---|
| All | 28 | 3.3 to 69 % | 15.5 % |
| Bare tube, Re above 20,000, continuous | 3 | 3.3 to 4.4 % | 3.8 % |
| Bare tube, Re above 20,000, pulse | 4 | 6.0 to 6.5 % | 6.2 % |
| Bare tube, all | 12 | 3.3 to 24 % | 9.5 % |
| Coated tubes, all | 16 | 6.6 to 69 % | 20 % |

### What this says

- **The v1 line chilldown band is a limit, not a prediction.** Real chilldowns used 1.5 to 30 times the best-case mass. A bare tube chilled fast with continuous flow is the worst, at about 4 % efficiency: most of the liquid runs straight through, because a vapour film insulates the wall (film boiling) and the liquid has no time to pick up heat.
- **Pulse flow roughly doubles efficiency for a bare tube at high Re** (3.8 % to 6.2 %), and **coatings help more**. The best tests (69 % for a 4-layer tube at Re about 8,000, and 43 to 45 % for 7-layer tubes at Re about 9,000 to 11,000) combine a coating with moderate flow. A thin insulating layer makes the surface cool quickly, which collapses the vapour film early and moves the tube into nucleate boiling, where heat transfer is far better.
- **Consequence for the v1 results.** Lesson 1 and figure 3 give 0.2 to 0.3 kg to chill a 3 m half-inch line. Using the 4 to 15 % efficiencies measured here, a real line could need roughly 1.5 to 6 kg. That is still small against a 1000 kg LOX load, but it is no longer negligible if the line is chilled many times. The v2 transient model is needed to predict this efficiency rather than borrow it.

### Honest limits

- LN2 only. The LH2 line chilldown reports found (below) give geometry and flow, but no per-test chilldown mass in the readable text.
- Initial wall temperature, inlet temperature and outlet pressure are assumed, not taken from the paper.
- The efficiency depends on where the meter integration starts and how much downstream metal it includes, neither of which is stated.

### Other chilldown sources found

- Darr, S.R., Hartwig, J.W., "Two-Phase Convection Heat Transfer Correlations for Liquid Hydrogen Pipe Chilldown", Space Cryogenics Workshop 2019, NTRS [20190029114](https://ntrs.nasa.gov/citations/20190029114). Read. Gives the LH2 correlation set (film, transition, nucleate boiling, rewet temperature) to be used in v2. Mean absolute wall-temperature error 19.5 K.
- Hartwig, J., Vera, J., "Numerical Modeling of the Transient Chilldown Process of a Cryogenic Propellant Transfer Line", NTRS [20150011065](https://ntrs.nasa.gov/citations/20150011065). LH2, 1.27 cm OD line, 3.42 kg and 1.61 m warm section, flows 0.0023 to 0.036 kg/s. No per-test chilldown mass.
- Rame, E., Hartwig, J.W., McQuillen, J.B., "Flow visualization of liquid hydrogen line chilldown tests", AIAA 2014, NTRS [20140008545](https://ntrs.nasa.gov/citations/20140008545). Reports cumulative pulse-flow mass about 30 % of trickle flow.
- Darr, S.R., Dong, J., Glikin, N., Hartwig, J.W., Chung, J.N., "Rewet Temperature Correlations for Liquid-Nitrogen Boiling Pipe Flows Across Varying Flow Conditions and Orientations", J. Thermal Sci. Eng. Appl. 11(5), doi:10.1115/1.4042857, NTRS [20200000632](https://ntrs.nasa.gov/citations/20200000632).
- Hartwig, J., Hu, H., Styborski, J., Chung, J.N., "Comparison of cryogenic flow boiling in liquid nitrogen and liquid hydrogen chilldown experiments", Int. J. Heat Mass Transfer 88 (2015), doi:10.1016/j.ijheatmasstransfer.2015.04.102, NTRS [20190007959](https://ntrs.nasa.gov/citations/20190007959). Abstract only.

## Thomas to download

These would strengthen Validation 1. Please download the PDFs from NTRS and drop them in a `refs/` folder (not committed if large).

1. Moran, M.E., Nyland, T.W., Driscoll, S.L., "Hydrogen No-Vent Fill Testing in a 1.2 Cubic Foot (34 Liter) Tank", NASA TM-105273, 1991, NTRS 19920004183. Needed: the Appendix B wall mass of the small receiver and the Appendix C run table (pages 39 to 40), checked by eye, because the OCR is garbled. This would add 42 small-tank runs with a very different wall-to-volume ratio.
2. Chato, D.J., Moran, M.E., Nyland, T.W., NASA TM-103155, 1990, NTRS 19900016962. Needed: the receiver wall mass (not stated in the text, perhaps in a drawing or a companion report).
3. Taylor, W.J., Chato, D.J., NASA TM-104492, 1991, on improved thermodynamic modelling of the no-vent fill process (cited by source A; exact title not yet confirmed). Describes the equilibrium model used at Lewis.
4. Chato, D.J., NASA TM-102039, 1989, analysis of the 4.96 m3 tank no-vent fill. Cited by source A.
5. Hartwig, J., Hu, H., Styborski, J., Chung, J.N., "Comparison of cryogenic flow boiling in liquid nitrogen and liquid hydrogen chilldown experiments", Int. J. Heat Mass Transfer 88 (2015), doi:10.1016/j.ijheatmasstransfer.2015.04.102 (NTRS 20190007959 has no download). Needed: per-test LH2 and LN2 chilldown time and mass, for an LH2 version of Validation 2.
6. Hartwig, J., Darr, S., Asencio, A., "Assessment of existing two phase heat transfer coefficient and critical heat flux correlations for cryogenic flow boiling in pipe quenching experiments", Int. J. Heat Mass Transfer 93 (2016) 441 to 463. Cited as the basis of the correlation choice for v2. Title as cited in secondary sources; check it.
7. The npj Microgravity 2022 paper above: Figure 2 time histories, to check where the metered mass integration starts.
