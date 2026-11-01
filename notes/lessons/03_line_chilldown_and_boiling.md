# Lesson 3: Line chilldown, the boiling curve, and why real chilldown wastes propellant

Lesson 1 gave a band for how much propellant it takes to chill a line. This lesson tests that band against NASA flight data and finds that real chilldowns use between 1.5 and 30 times the thermodynamic minimum. Understanding why takes us through the boiling curve, the most important picture in cryogenic heat transfer.

## 1. The energy balance gives a floor, not a prediction

The v1 model says the propellant needed to cool a wall is the wall's heat divided by how much heat each kilogram of propellant picks up:

m = Q_wall / (h_out - h_in)

Everything hinges on h_out, the enthalpy of the fluid as it leaves. The model brackets it:

- **Best case**: the fluid leaves as vapour at the local wall temperature. Each kilogram has boiled and then warmed up as far as the wall allows. This is the most heat a kilogram can possibly carry away, so it gives the least propellant. No real process can beat it, for the same reason no engine beats Carnot: it is a limit set by thermodynamics, not by hardware.
- **Saturated vapour case**: the fluid leaves just boiled, with no superheat.

But nothing in thermodynamics forces the liquid to boil at all. If liquid runs straight through the line and out the end still liquid, h_out is close to h_in and the propellant used can be any amount. The energy balance cannot tell you how much liquid escapes without doing its job. Only heat transfer, meaning how fast heat moves from wall to fluid, can.

## 2. The test data

Hartwig and colleagues at NASA Glenn and the University of Florida flew an LN2 chilldown rig on parabolic flights (npj Microgravity, 2022). The test section was a 0.914 m length of 304 stainless tube, 12.7 mm outside diameter with a 0.51 mm wall. They flew a bare tube and tubes with 4 and 7 layers of a thin Teflon (FEP) coating, about 15 micrometres per layer, using continuous and pulsed flow. For 28 tests they report the total LN2 used to chill the tube.

## 3. Worked example: test F1

**Tube mass.** m = (π/4)(D_o² - D_i²) L ρ = (π/4)(0.0127² - 0.01168²)(0.914)(7900) = 0.141 kg.

**Wall heat.** Integrating the stainless steel cp from 290 K down to 97 K (2 K above the saturation temperature at the 550 kPa inlet pressure) gives 10.9 kJ.

**Saturated vapour case.** The inlet liquid is saturated at 550 kPa, which is 95.2 K. It leaves at about 1 atm, where saturated vapour has an enthalpy 161 kJ/kg higher. So m = 10.9 / 161 = 0.067 kg.

Notice something here. The latent heat of nitrogen at 1 atm is 199 kJ/kg, but each kilogram only picks up 161 kJ. Why? The inlet liquid is saturated at 550 kPa, so it is 18 K warmer than liquid at 1 atm. As it drops in pressure along the line, part of it flashes to vapour using its own sensible heat. That flashing does no useful cooling. This is why designers subcool the supply: subcooled liquid can absorb heat before it boils, and does not waste capacity flashing.

**Best case.** Vapour leaving at the wall temperature carries extra sensible heat, so m drops to 0.039 kg.

**Measurement.** Test F1 used 1.08 kg. The efficiency, m_best / m_measured, is 3.6 %. More than 96 % of the liquid's cooling capacity went out of the end of the tube unused.

## 4. The boiling curve

To understand why, plot the heat flux from a hot surface into a liquid against the wall superheat, ΔT = T_wall - T_sat. This is the Nukiyama boiling curve (1934), and you will find it in any heat transfer textbook (Incropera, "Fundamentals of Heat and Mass Transfer", chapter 10). Read it from right to left, because during chilldown the wall starts hot and cools.

**Film boiling (large ΔT).** At 290 K, the wall is about 200 K above the saturation temperature of LN2. Liquid that approaches the wall vaporises instantly and forms a continuous vapour film between wall and liquid. Nitrogen vapour near 80 K conducts heat roughly twenty times worse than the liquid. So heat has to cross an insulating blanket. The heat flux is low, and most of the liquid core flows past without touching the wall. This is the Leidenfrost effect, the same thing that makes a water drop skate on a very hot pan.

**Minimum heat flux and the rewet (Leidenfrost) temperature.** As the wall cools, the film thins and becomes unstable. At the rewet temperature, T_wet, liquid starts touching the wall. For nitrogen, correlations give T_wet near 0.84 T_critical, roughly 106 K, plus a flow-dependent term (Darr et al. 2019).

**Transition boiling.** Below T_wet, liquid contacts the wall intermittently. Heat flux rises steeply as the wall cools, because more of the wall is wetted each second.

**Critical heat flux.** The peak of the curve. Liquid is wetting the wall almost everywhere, and bubbles leave as fast as they form.

**Nucleate boiling (small ΔT).** Bubbles form at surface pits and detach, stirring the liquid next to the wall. This is the most effective heat transfer mode, with heat transfer coefficients tens of times higher than film boiling.

**Single-phase convection.** Once the wall is barely above saturation, boiling stops and the wall is chilled.

The key fact for chilldown: **the wall spends most of the time in film boiling, the slowest mode.** Hartwig et al. (2015) report that more than 75 % of the chilldown time in low-Re LN2 flows is film boiling. While the wall sits there, liquid flows past wasted.

## 5. Why faster flow is less efficient

At high flow, the liquid core moves quickly through a tube still blanketed by vapour. Heat per second goes up, so chilldown is faster, but heat per kilogram goes down. The data show this plainly: the bare tube at Re around 70,000 with continuous flow has 3 to 4 % efficiency, while at Re around 1,000 it reaches 13 to 24 %.

So there is a trade-off, time against propellant. A transfer operation that must finish in a fixed window will pay propellant for speed.

## 6. Why pulse flow helps

Pulse flow opens the valve for a fraction of each cycle (for example, 10 % of a 2 s period). During the off period, the liquid already in the tube sits against the wall and has time to boil fully, instead of being pushed out by the next liquid behind it. For the bare tube at high Re, pulsing raised efficiency from about 3.8 % to about 6.2 %. It costs time, since the tube chills more slowly per second.

## 7. Why a thin coating helps so much

This is the counter-intuitive result. Wrapping a cold line in insulation would make it chill more slowly, surely? The answer depends on where the insulation is and how thick it is.

The coating is on the inside surface, and it is only 60 to 110 micrometres thick. Its job is not to stop heat flow. It is to change the temperature the liquid sees.

Picture the inner surface. Heat must flow from the steel, through the coating, into the fluid. Teflon conducts roughly 50 to 70 times worse than stainless steel at these temperatures. So the outer surface of the coating cools very quickly, much faster than the steel behind it, because there is little thermal mass in a thin plastic layer and the steel cannot resupply heat to it quickly. When that surface drops below T_wet, liquid rewets it, and the tube jumps from film boiling into transition and nucleate boiling while the steel underneath is still warm. The tube now spends most of the chilldown in the efficient boiling modes.

There is an optimum. Too thin and the surface tracks the steel; too thick and the coating blocks the heat. The 4-layer tube at moderate flow gave the best test of all, 69 % efficiency, and coated tubes averaged about 20 % against 9.5 % for bare tubes.

## 8. What this means for the model and for TEC

The v1 band was correct as a limit: no test went below it. But as a prediction it was optimistic by a factor of 1.5 to 30. For a 3 m half-inch line, v1 says 0.2 to 0.3 kg; with the efficiencies measured here a real line might need roughly 1.5 to 6 kg. On a 1000 kg LOX transfer that is under 1 %, so the receiver tank still dominates. But for methane, for repeated transfers, or for a long line on a depot, it adds up.

The v2 transient model has to capture film boiling, rewet and nucleate boiling to predict efficiency instead of borrowing it. The Darr and Hartwig correlation set (NTRS 20190029114) is the starting point.

A good question for Cédric: "Do you plan to coat or pulse the transfer line, or is chilldown time the binding constraint?"

## Self-test questions

1. Why is the best-case chilldown mass a hard lower limit, while the saturated-vapour case is not an upper limit?
2. For test F1, explain why each kilogram of LN2 only picks up 161 kJ even though the latent heat at 1 atm is 199 kJ/kg. What would you change in the supply to fix it?
3. Sketch the boiling curve and mark the region where a 290 K stainless tube starts, the rewet temperature, critical heat flux and nucleate boiling.
4. Why does higher flow rate shorten chilldown time but lower efficiency?
5. Explain, in terms of surface temperature, why a 100 micrometre Teflon coating speeds up chilldown.

## Answers

1. The best case assumes every kilogram leaves as vapour at the wall temperature, which is the most heat it can carry; no process can do better. The saturated-vapour case assumes every kilogram at least boils. Real flow can carry liquid out unboiled, so real use can exceed it by any amount.
2. The inlet liquid is saturated at 550 kPa (95 K). On expansion to 1 atm, part of it flashes using its own sensible heat (about 38 kJ/kg), which does no cooling of the wall. Subcooling the supply below saturation at the line outlet pressure fixes it.
3. The tube starts in film boiling far to the right (wall superheat about 200 K). Moving left: minimum heat flux at the rewet temperature (about 106 K wall for nitrogen, a superheat of about 30 K at 1 atm), transition boiling rising to critical heat flux at a few kelvin of superheat, then nucleate boiling, then single-phase convection.
4. More flow means more heat removed per second, so faster cooling, but in film boiling most of the extra liquid passes through the core without touching the wall, so heat removed per kilogram falls.
5. The thin coating has very little heat capacity and conducts poorly, so its exposed surface cools to below the rewet temperature quickly while the steel behind it is still warm. Liquid then wets the surface and the tube switches from film boiling to the much more effective transition and nucleate boiling modes early.

## Further reading

- Hartwig, J. et al., "Nitrogen flow boiling and chilldown experiments in microgravity using pulse flow and low-thermally conductive coatings", npj Microgravity 8:33 (2022): https://pmc.ncbi.nlm.nih.gov/articles/PMC9363417/
- Darr, S.R., Hartwig, J.W., "Two-Phase Convection Heat Transfer Correlations for Liquid Hydrogen Pipe Chilldown", 2019: https://ntrs.nasa.gov/citations/20190029114
- Incropera, DeWitt, Bergman, Lavine, "Fundamentals of Heat and Mass Transfer", chapter 10 (boiling and condensation).
- Barron, "Cryogenic Heat Transfer", Taylor and Francis (film boiling of cryogens).
- Hartwig, J. et al., "Comparison of cryogenic flow boiling in liquid nitrogen and liquid hydrogen chilldown experiments", Int. J. Heat Mass Transfer 88 (2015).
