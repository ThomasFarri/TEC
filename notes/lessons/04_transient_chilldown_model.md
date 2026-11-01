# Lesson 4: Building a transient chilldown model

Lessons 1 to 3 gave limits. This lesson builds the first model that predicts time, and with it the real propellant used. It is also your first real encounter with calibration: we had to tune one number, and we must be honest about what that means.

## 1. What we want and what it costs

We want T_wall(z, t): wall temperature along the line and in time. From it follow the chilldown time, the propellant used (flow times time) and the efficiency against the thermodynamic minimum.

A full model would solve the two-phase flow (mass, momentum, energy for liquid and vapour), the boiling at the wall, and conduction in the wall in 2D or 3D. That is a research code. We make three simplifications, each justified by a number.

## 2. Simplification 1: the wall is lumped radially (Biot number)

Heat leaves the inner wall surface into the fluid. Is the wall nearly uniform in temperature through its thickness, or is there a steep gradient? Compare the resistance to conduction through the wall with the resistance to convection at the surface. Their ratio is the Biot number:

Bi = h t / k

where h is the heat transfer coefficient, t the wall thickness and k the wall conductivity. If Bi is much less than 0.1, conduction is fast compared with what convection can take away, so the wall is effectively at one temperature through its thickness.

For the NASA test tube at the start of chilldown: the model's film-boiling flux at 290 K is about 61 kW/m2 for a superheat of 195 K, so h is about 315 W/(m2 K). With t = 0.51 mm and k about 15 W/(m K) for stainless steel at room temperature,

Bi = 315 × 0.00051 / 15 ≈ 0.01.

So the wall is lumped radially. This would fail for a thick flange or a valve body, which is why real lines chill fastest in the thin tube and slowest at the fittings.

## 3. Simplification 2: no axial conduction in the wall

Stainless steel is a poor conductor and the wall is thin, so heat conducted along the tube is small compared with heat convected into the fluid. We neglect it. For aluminium or copper lines this would be less true, and the chilldown front would be smeared.

## 4. Simplification 3: the fluid is quasi-steady

The fluid crosses the tube much faster than the wall cools, so at each instant we can treat the fluid as if it were in steady flow past the current wall temperatures.

Check: for test F2, G = 557 kg/(m2 s) and the liquid density is 717 kg/m3, so the liquid velocity is about 0.78 m/s and it crosses 0.914 m in about 1.2 s. The chilldown takes 14.6 s. The ratio is about 12. That is enough to be a reasonable approximation but not a large margin. It also ignores that vapour generation accelerates the flow and can briefly reverse it, which is what you see in flow visualisation.

## 5. The equations

Split the tube into N nodes of length dz. Node i has wall mass m_i = m_tube / N.

**Wall energy:**

m_i cp(T_i) dT_i/dt = -Q_i

**Fluid energy, marched from inlet to outlet at each instant:**

h_{i+1} = h_i + Q_i / mdot

**Heat transfer:**

Q_i = q''(T_i, h_i) × π D dz

All the physics is in q'', the boiling curve from lesson 3. The model picks the regime from the local wall temperature and fluid state:

- Fluid subcooled liquid or wall below saturation: single-phase convection (Dittus-Boelter, Nu = 0.023 Re^0.8 Pr^0.4).
- Wall above the rewet temperature T_wet: film boiling, Nu = 0.015 Re_tp^0.8774 Pr_v^0.6112 (Darr and Hartwig 2019).
- Wall within 2 K of saturation: nucleate boiling, a Dittus-Boelter coefficient multiplied by 61.6 Re_l^-0.332 Ja^-0.254.
- In between: transition boiling, linear in wall temperature between the two.
- Fluid fully vaporised: single-phase vapour convection.

**Second-law cap.** One more rule: the fluid can never leave a node hotter than the wall. Without it, a large step can push the fluid enthalpy past the wall temperature, which would mean heat flowing from cold to hot. The code limits Q_i to what it takes to heat the fluid to T_i. Writing physical limits explicitly into a numerical model is a good habit.

## 6. Time stepping

The wall equation is integrated with the explicit (forward) Euler method:

T_i(t + dt) = T_i(t) - Q_i dt / (m_i cp)

Explicit methods are simple but can go unstable if dt is too large. The rule here is adaptive: choose dt so that no node changes by more than 2 K per step. Fast cooling means small steps, slow cooling means big ones. Two checks show the answer is not an artefact of the numerics:

- **Mesh convergence.** 10, 20, 30 and 60 nodes give 17.21, 17.22, 17.26 and 17.26 s for the same case. The answer has converged.
- **Step convergence.** A 0.5 K step limit gives 17.21 s against 17.24 s for 2 K.
- **Energy conservation.** The test suite checks that the enthalpy gained by the fluid equals the heat lost by the wall to within 2 %.

## 7. Worked example: one node at the start of test F2

Take a node at 290 K with fluid that is just two-phase at 550 kPa. The model gives a film-boiling flux of 61 kW/m2.

Per metre of tube, the wall heat capacity is (0.141 kg / 0.914 m) × 471 J/(kg K) ≈ 73 J/(K m). The heat flow per metre is q × π D = 61,000 × π × 0.01168 ≈ 2,240 W/m. So the node starts cooling at about 2,240 / 73 ≈ 31 K/s.

That rate does not last. As the wall cools, the superheat falls, so the film-boiling flux falls nearly in proportion: at 140 K it is only 14 kW/m2. The wall's cp falls too, which partly compensates. The time constant m cp / (h A) is about 6 s at the start of film boiling, and most of the chilldown time is spent crawling down towards the rewet temperature (133 K in this case). Once a node rewets, it drops to saturation in a second or two. This is why chilldown looks like a "quench front" moving down the tube.

## 8. Calibration, honestly

With the correlations exactly as published (C_fb = 1), the model was twice too slow at high flow. There are good reasons for this: we had to guess one definition (the two-phase Reynolds number) and dropped one term (inverted annular film boiling), because those parts of the paper were not readable.

So the film-boiling coefficient has one multiplier, C_fb, fitted to ONE test (F2, the cleanest: 0.05 g throughout, continuous flow, bare tube). It came out at 2.41. Then the model was run, without further tuning, on the other tests:

| Test | Measured | Model | Error |
|---|---|---|---|
| F1, 0.38 g | 15.1 s | 12.5 s | -17 % |
| F12, ends in 1 g | 21.1 s | 19.1 s | -9 % |
| F5, F8, F10 (low flow) | 71 to 172 s | 272 to 948 s | +260 to +450 % |

This is the honest picture. Calibrating on one point and checking on others is the minimum standard. Fitting on all of them and reporting the fit would hide the low-flow failure. The low-flow failure is the most useful thing we learned: the film-boiling form scales with Re to the power 0.88, which drops too steeply at low flow, where other mechanisms (gravity-driven film flow, liquid contact through instabilities) take over.

So the model has a stated range: G above about 300 kg/(m2 s). Inside it, expect ±20 % on time. Outside it, do not use it.

## 9. What v2 says for TEC

For a 3 m half-inch stainless line from 290 K at 400 kPa with 5 K subcooling:

- LOX: 2.4 to 3.4 kg, 7 to 118 s over flows of 0.02 to 0.5 kg/s.
- LCH4: 0.9 to 1.5 kg, 3 to 45 s.
- Efficiency 6 to 9 %, consistent with the measured 4 to 6 % for the bare tube at high flow in lesson 3.

Two trade-offs are visible. More flow means shorter chilldown but more propellant. And methane chills the line with about a third of the mass of oxygen, because its latent heat per kilogram is about 2.4 times larger (about 510 kJ/kg against 213 kJ/kg at 1 atm). Per kilogram of methane loaded, though, the receiver tank cost is still higher (lesson 1), so the two effects pull in opposite directions.

## Self-test questions

1. Compute the Biot number for the same tube if the wall were 5 mm thick aluminium (k about 200 W/(m K)) and h = 2,000 W/(m2 K) in nucleate boiling. Is lumping still valid?
2. Why does the fluid march from inlet to outlet within each time step, rather than having its own time derivative?
3. What would happen physically, and in the code, without the second-law cap?
4. Why calibrate on one test and check on others, instead of fitting all six?
5. A colleague runs v2 at G = 50 kg/(m2 s) for a slow transfer and quotes the result. What do you tell them?

## Answers

1. Bi = 2000 × 0.005 / 200 = 0.05. Still below 0.1, so lumping is acceptable, though less comfortably than for the thin steel tube.
2. Because the fluid transit time (about 1 s) is short compared with the wall cooling time (about 15 s), the fluid reaches a steady profile almost instantly for any given wall state. This quasi-steady assumption removes a stiff equation.
3. Physically, heat would flow from the colder wall into the hotter fluid, breaking the second law. In the code the fluid enthalpy could overshoot the property table and the wall would be over-cooled, giving a falsely short chilldown time.
4. Fitting all six would hide the systematic failure at low flow and give a misleading average error. Fitting one and predicting the rest tests whether the model generalises.
5. That G is far below the calibrated range (above about 300). The checked tests at G of 9 to 35 were overpredicted by 3 to 6 times. The result is not trustworthy until checked against low-flow data.

## Further reading

- Incropera et al., "Fundamentals of Heat and Mass Transfer", chapter 5 (lumped capacitance and Biot number) and chapter 10 (boiling).
- Darr, S.R., Hartwig, J.W., "Two-Phase Convection Heat Transfer Correlations for Liquid Hydrogen Pipe Chilldown", 2019: https://ntrs.nasa.gov/citations/20190029114
- Hartwig, J., Vera, J., "Numerical Modeling of the Transient Chilldown Process of a Cryogenic Propellant Transfer Line": https://ntrs.nasa.gov/citations/20150011065 (a full network solver, GFSSP, for comparison).
- Dougall, R.S. and Rohsenow, W.M., "Film boiling on the inside of vertical tubes with upward flow of the fluid at low vapor qualities", MIT report 9079-26, 1963 (the two-phase Reynolds number used here).
