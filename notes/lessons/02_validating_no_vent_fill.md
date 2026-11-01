# Lesson 2: Validating the no-vent fill model against NASA hydrogen tests

Lesson 1 built the equilibrium model. This lesson asks the question any reviewer will ask first: how do you know it is right? We answer it with 32 liquid hydrogen fills run at NASA Lewis (now Glenn) in the early 1990s, and along the way learn why one input, the inlet liquid temperature, controls almost everything.

## 1. What validation means, and what it does not

There are two different checks, and engineers often mix them up.

**Verification** asks "did I solve the equations correctly?". The unit tests from lesson 1 do this: energy is conserved on a charge, venting lowers pressure, a zero-mass wall fills easily. Verification can be done with no experiments at all.

**Validation** asks "are these the right equations for the real world?". Only experiment can answer it. You run the model with the test's inputs, compare its output with the test's measurements, and quantify the difference.

Three rules make a validation honest:

1. Use every test in the data set, not the ones that agree. We kept all 33 runs, including the one that failed.
2. Fix your assumptions before you look at the errors. Tuning a parameter until the errors vanish is calibration, not validation.
3. Compare the error with the input uncertainty. If your inputs are only known to ±10 % in their effect, a 7 % mean error is as good as you can show.

A good textbook treatment is Oberkampf and Roy, "Verification and Validation in Scientific Computing", Cambridge University Press, 2010, chapters 1 and 12.

## 2. The tests

NASA Lewis ran no-vent fills of liquid hydrogen into two aluminium tanks at the K-Site facility in Plum Brook:

| | Tank A | Tank B |
|---|---|---|
| Report | Taylor and Chato, NASA TM-106018 | Chato, NASA TM-106293 |
| Volume | 4.96 m3 (175 ft3) | 2.01 m3 (71 ft3) |
| Wall | 2219 Al, 149.6 kg | 2219 Al, 110.2 kg |
| Wall per volume | 30 kg/m3 | 55 kg/m3 |
| Injection | top spray, bottom spray | spray bar, bottom orifice |
| Runs used | 11 | 21 (plus one failure) |

Each run started with a tank at some wall temperature between 16 K and 130 K and filled until about 94 to 97 % liquid by volume, with the vent shut. The reports tabulate the initial wall temperature, average inlet liquid temperature, average flow, and final pressure at the final fill. That is exactly what our model needs as inputs and gives as output.

Notice what the tests chose to vary: wall temperature, inlet temperature and injection method. Those are the three things a designer controls.

## 3. Unit conversions you will meet in every NASA report

Tank B is in US units, and you must be fluent in them to read the NASA literature.

- Rankine to kelvin: T[K] = T[R] / 1.8. Rankine is an absolute scale with Fahrenheit-sized degrees. 37.0 R is 20.6 K.
- psia to kPa: multiply by 6.894757. "psia" means absolute pressure; "psig" means gauge, relative to atmosphere. Never confuse them. 20.8 psia is 143.4 kPa.
- lbm/hr to kg/s: multiply by 0.45359237 and divide by 3600.
- ft3 to m3: multiply by 0.0283168. 71 ft3 is 2.01 m3.

The script keeps the table exactly as printed and converts in code, so anyone can check the transcription against the report.

## 4. Para-hydrogen, and why the choice of fluid matters

Hydrogen molecules come in two spin states. In ortho-hydrogen the two proton spins are parallel; in para-hydrogen they are opposed. At room temperature the equilibrium mix is 75 % ortho ("normal hydrogen"). At 20 K the equilibrium is almost pure para. Liquid hydrogen from a production plant is converted to para with a catalyst, because the ortho to para conversion releases heat (more than the latent heat of vaporisation) and would boil the stored liquid away over days.

So the right model fluid for liquid hydrogen tests is para-hydrogen. CoolProp has both. At 22.2 K the saturation pressure is 172 kPa for para and 168 kPa for normal hydrogen, a 3 % difference. Small, but it is a systematic bias, and systematic biases are what validation should remove before it starts.

## 5. Running the model on one test: a worked example

Take Fill 19 in tank A: wall at 104.4 K, inlet liquid at 23.0 K, filled to 94 %.

**Step 1, the load.** Saturated liquid para-hydrogen at 23.0 K has a density of 67.4 kg/m3. At 94 % of 4.96 m3 that is 314 kg.

**Step 2, the wall energy.** Integrating the aluminium cp from 23 K to 104.4 K and multiplying by 149.6 kg gives 3.07 MJ. Lesson 1 explains why this is less than m cp ΔT with a room-temperature cp.

**Step 3, where that energy goes.** The liquid has a specific heat of about 11.6 kJ/(kg K) at 23 K. If all the wall energy simply warmed 314 kg of liquid, the rise would be

ΔT = 3.07e6 / (314 × 11,600) ≈ 0.84 K.

The model's full answer is a final temperature of 24.06 K, a rise of 1.06 K. The extra 0.2 K comes from two places the hand estimate ignores: the vapour that must evaporate to fill the 6 % ullage at the higher pressure, which needs latent heat, and 12 kJ of heat leak over the 45-minute fill.

**Step 4, temperature to pressure.** The tank is two-phase, so its pressure is the saturation pressure at 24.06 K, which is 268 kPa. The test measured 227 kPa. The model is 18 % high on this run.

Now look at the size of each step. The wall energy raised the liquid by about 1 K. The inlet temperature itself was measured to about ±0.5 K. So on this test, the uncertainty in the inlet temperature is about half the whole effect of the wall. That is the central lesson of this validation.

## 6. Why inlet temperature dominates: Clausius-Clapeyron

Why does 1 K matter so much? The slope of the saturation curve is given by the Clausius-Clapeyron equation. It comes from equating the Gibbs free energy of liquid and vapour along the saturation line:

dp/dT = h_fg / (T (v_g - v_f))

where h_fg is the latent heat and v_g, v_f are the specific volumes of vapour and liquid. If the vapour is roughly an ideal gas and much less dense than the liquid, v_g - v_f ≈ R_s T / p, giving

dp/dT ≈ h_fg p / (R_s T²).

For para-hydrogen at 23 K: h_fg = 428 kJ/kg, p = 210 kPa, R_s = 8.314 / 0.002016 = 4124 J/(kg K). So

dp/dT ≈ 428,000 × 210,000 / (4124 × 529) ≈ 41 kPa/K.

The real-fluid value from CoolProp is about 51 kPa/K. The ideal-gas estimate is low because at 23 K and 0.2 MPa hydrogen vapour is close to its critical point (33 K, 1.3 MPa) and is not ideal. Either way, half a kelvin of inlet temperature moves the final pressure by 20 to 25 kPa, about 10 % of the answer. NASA's own error budget in TM-106018 says the same: ±0.5 K on inlet temperature gives about 4 psia (28 kPa) or 14 %.

For LOX and LCH4 the same equation applies with their own h_fg, p and T. The sensitivity study later in the backlog will put numbers on inlet subcooling for both.

## 7. Results

Across 32 runs, the mean error in final pressure is -2.3 % and the mean absolute error is 7.0 % (12 kPa). The largest single error is 26 %. NASA's own equilibrium model on tank A was reported within 17 kPa (2.5 psia) for bottom spray runs, and our 16 kPa mean on tank A is consistent with that.

Figure 5 shows a parity plot (model against measurement, with a 1:1 line) and the error against wall temperature, coloured by inlet temperature. Parity plots are the standard way to show validation: points on the diagonal are perfect, and any pattern in how they leave it tells you about missing physics.

## 8. Reading the errors as physics

Random scatter means noisy inputs. A pattern means the model is missing something. There is one clear pattern here.

**Warm inlet liquid with the spray bar in tank B is underpredicted by 16 to 26 %** (tests 286, 324, 337, 339). The same inlet temperatures through the bottom orifice agree within 10 %.

Why? A no-vent fill only works because cold incoming liquid condenses the vapour in the ullage. Condensation needs the vapour to touch liquid that is colder than saturation. With warm inlet liquid, the subcooling is small, so every bit of contact counts. If the injector does not stir the ullage well, a warm vapour layer sits above the liquid, the interface warms to saturation at a higher temperature, and the pressure rises above the equilibrium value. That is thermal stratification, which lesson 1 predicted would make equilibrium a best case.

The equilibrium model has no idea which injector you used. Source A says it plainly: "The equilibrium model results are independent of the tank geometry and the liquid inlet configuration." That is both its strength (simple, general) and its limit (it cannot rank injectors).

## 9. The failure the model could not predict

Test 330 started with the wall at 129 K. The model says a 95 % fill would finish at 114 kPa, well within limits. The real test failed. Chato reports that "the initial wall cooldown produced a pressure transient which exceeded the supply pressure". In the first seconds the incoming liquid hit a warm wall and flashed to vapour faster than the spray could condense it. The tank pressure briefly rose above the supply pressure, so liquid stopped flowing in.

The final state was never reached, so the final state cannot tell you whether you will get there. This is the strongest argument for a time-resolved model: the risk in a no-vent fill is in the first minute, not the last.

For Cédric, this is the line to remember: "Equilibrium tells you whether the end state is allowed. It cannot tell you whether you can get there without a pressure spike. That needs the transient model, or a pre-chill."

## 10. What this validation does and does not cover

It covers final pressure at final fill, for LH2, in two aluminium tanks of 2 to 5 m3, with walls from 16 K to 126 K.

It does not cover the pressure history, LOX or LCH4, steel tanks, or microgravity. In 1 g, buoyancy separates liquid and vapour and helps the injector. In orbit the vapour can be anywhere. The equilibrium answer is unchanged by gravity, but how close a real tank gets to it is not.

## Self-test questions

1. What is the difference between verification and validation? Give one example of each from this project.
2. Convert test 324 of tank B (wall 155.5 R, inlet 37.0 R, final 29.7 psia) to SI units.
3. Using Clausius-Clapeyron with the ideal-gas approximation, estimate how much the final pressure of Fill 19 would change if the inlet were 0.5 K colder. Why is your answer smaller than the CoolProp result?
4. Why does the equilibrium model underpredict, rather than overpredict, pressure when mixing is poor?
5. Test 330 had a model prediction well within limits but failed. What physical process caused this, and what would you change in the operation to avoid it?

## Answers

1. Verification checks the equations are solved correctly, for example the test that charge_to_pressure conserves energy exactly. Validation checks the equations represent reality, for example comparing predicted and measured final pressure for the 32 NASA fills.
2. 155.5 / 1.8 = 86.4 K wall; 37.0 / 1.8 = 20.6 K inlet; 29.7 × 6.894757 = 204.8 kPa.
3. dp/dT ≈ 41 kPa/K, so about 20 kPa lower. CoolProp gives about 25 kPa because hydrogen vapour near 23 K and 0.2 MPa is not an ideal gas and its specific volume is smaller than R_s T / p, which makes the true slope steeper.
4. Poor mixing leaves a warm vapour layer at the interface. Pressure is set by the saturation temperature at the interface, which is warmer than the average, so the real pressure is higher than the mixed-average equilibrium value.
5. Flash boiling against the warm wall in the first seconds produced vapour faster than the spray could condense it, so tank pressure exceeded supply pressure and inflow stopped. Options: pre-chill the wall with a charge-hold-vent cycle first, start with a low flow to limit the boiling rate, or raise the supply pressure.

## Further reading

- Taylor, W.J. and Chato, D.J., NASA TM-106018, 1993: https://ntrs.nasa.gov/citations/19930017966
- Chato, D.J., NASA TM-106293, 1993: https://ntrs.nasa.gov/citations/19940013013
- Chato, D.J., Moran, M.E., Nyland, T.W., NASA TM-103155, 1990: https://ntrs.nasa.gov/citations/19900016962
- Cengel and Boles, "Thermodynamics: An Engineering Approach", chapter 12 (Clausius-Clapeyron).
- Oberkampf, W.L. and Roy, C.J., "Verification and Validation in Scientific Computing", Cambridge University Press, 2010.
- Leachman, J.W. et al., "Fundamental equations of state for parahydrogen, normal hydrogen, and orthohydrogen", J. Phys. Chem. Ref. Data 38, 721 (2009). This is the equation of state CoolProp uses for hydrogen.
