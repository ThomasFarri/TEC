# Lesson 1: The energy budget of cryogenic transfer

This lesson covers everything behind the v1 model. If you understand it, you can defend every number in the README.

## 1. Why cryogenic transfer is hard at all

Start with what a cryogen is. Liquid oxygen boils at 90 K at one atmosphere, liquid methane at 112 K and liquid hydrogen at 20 K. Everything around them in space (tanks, pipes, valves) sits much warmer: typically 250 to 300 K before a transfer, depending on sun exposure and thermal control.

When the cold liquid meets warm metal, heat flows from the metal into the liquid. The liquid absorbs that heat by boiling. Boiling makes vapour, and vapour in a closed tank raises the pressure. Every flight tank has a maximum operating pressure, set by its wall thickness and safety factors, so you cannot let that pressure grow without limit.

On the ground the fix is easy: open a vent valve at the top of the tank, where gravity has put the vapour, and let it escape. In orbit there is no "top". Surface tension and wetting decide where liquid sits, and in a tank that is boiling violently you do not know whether the vent port is touching gas or liquid. Venting liquid wastes propellant and can freeze valves. That single fact is why in-orbit transfer is its own discipline, called cryogenic fluid management (CFM).

So the questions are:
1. How much propellant do you spend cooling the hardware down?
2. Can you fill the tank without exceeding its pressure limit?

## 2. The first law for an open system

The whole model is the first law of thermodynamics written for a control volume, meaning a fixed region of space, here the tank, that mass can enter and leave.

For a rigid tank with no work done on it and no heat from outside, the change in stored energy equals what enters minus what leaves:

dU_total = h_in dm_in - h_out dm_out

Three things here are worth understanding properly.

First, why enthalpy h and not internal energy u for the flowing mass? When a kilogram of liquid is pushed into the tank, the fluid behind it does work pushing it in, called flow work, equal to p times v per kilogram. Enthalpy is h = u + pv, so it bundles the energy the mass carries with the work needed to push it across the boundary. The stored energy inside the tank stays as u, because nothing is crossing the boundary there. Any thermodynamics textbook covers this; Cengel and Boles, "Thermodynamics: An Engineering Approach", chapter 5, is the standard reference.

Second, U_total includes the wall. The tank metal stores heat, and that heat is exactly what you are trying to remove. So U_total = m_fluid u_fluid + m_wall H_wall(T). For a solid, internal energy and enthalpy are effectively the same, because solids barely expand.

Third, no heat leak. Real tanks absorb heat through their insulation from the sun and Earth. Over a transfer of an hour or so with multilayer insulation, that leak is small compared with the wall heat. Over days of storage it dominates, which is a different problem: boil-off.

## 3. Why the wall's specific heat matters so much

Specific heat c_p is how much energy it takes to raise one kilogram by one kelvin. At room temperature aluminium is about 950 J/kg K. It is tempting to say "40 kg of aluminium cooled by 200 K is 40 x 950 x 200 = 7.6 MJ". That is wrong, and the reason is physics worth knowing.

At low temperature, heat in a solid is stored in lattice vibrations, called phonons. Quantum mechanics says those vibrations can only take discrete energy steps. As the temperature falls, fewer vibration modes can be excited, so the solid can hold less heat per kelvin. The Debye model predicts c_p falls roughly as T cubed at very low temperature. The model's NIST data show it: aluminium drops from 954 J/kg K at 300 K to 348 at 77 K and about 9 at 20 K.

So the correct heat removed is the integral:

Q = m_wall times the integral of c_p(T) dT from T_final to T_initial

For 40 kg of Al 6061 from 290 K down to the boiling point of LOX at 345 kPa (about 104 K), the model gives 5.9 MJ. The naive constant c_p estimate would give about 7 MJ. Using the constant room-temperature value overestimates the wall heat. That error is conservative, but it is still wrong.

The practical consequence is a good one. Most of the wall heat sits in the warm part of the range. Cooling from 290 K to 150 K removes far more energy than cooling from 150 K to 90 K. That is why "partly chilled" tanks are so much easier to fill.

## 4. Phase change and the two-phase dome

Inside the tank, the fluid can be liquid, vapour or a mixture. In the mixture region (the "dome" on a pressure-volume or temperature-entropy diagram), pressure and temperature are locked together. At a given temperature there is exactly one saturation pressure. Raise the temperature and the pressure must rise along the saturation curve.

This is the key to the no-vent fill. If the mixed tank contents settle at temperature T, the tank pressure is p_sat(T). So keeping the pressure below 345 kPa means keeping the equilibrium temperature below T_sat(345 kPa): about 104 K for oxygen and 129 K for methane. The question "can I fill without venting?" becomes "can the incoming cold liquid absorb all the wall heat and its own heat without the mixture rising above that temperature?".

Subcooling is why the answer can be yes. The supply liquid enters 5 K colder than its own boiling point at the supply pressure. Every kilogram can therefore absorb some heat as sensible warming before it has to boil. Over a 1000 kg LOX load that spare capacity adds up.

## 5. The equilibrium (homogeneous) assumption, and why it is the best case

The solver assumes the fluid is perfectly mixed and at the same temperature as the wall. Given mass and total energy, there is one temperature that makes the energy balance, and the solver finds it with Brent's method, a robust root-finding algorithm.

Why is this a best case? Consider what really happens. Liquid enters, hits warm wall, and flashes to vapour. That warm vapour does not instantly mix with the cold liquid. It collects as a warm layer, called thermal stratification, and the pressure is set by the warmest liquid surface in contact with the vapour, not the average. So a real tank reaches higher pressure than the equilibrium prediction for the same amount of propellant.

NASA's no-vent fill tests used spray nozzles to force mixing, precisely to push real tanks toward equilibrium. A good spray system gets close to the equilibrium prediction. A poor one, or a simple bottom fill, does much worse. That is the honest framing for Cédric: "equilibrium tells you what is thermodynamically possible; the engineering is in how close your injection and mixing hardware gets you."

## 6. The two chilldown strategies

**Charge-hold-vent.** You inject a small charge of liquid with the vent closed. It boils against the wall, absorbing heat, and the pressure rises. You hold while things settle, then vent the warm vapour. Then you repeat.

The vented gas is warm, so each kilogram vented carries away a lot of heat. It entered as cold liquid and left as warm gas, picking up both latent heat and sensible heat. That makes it efficient, but it takes several cycles and needs the vent to see vapour only.

**Flow-through.** Liquid runs continuously through the tank and out of the vent. It is fast and simple, but the outgoing fluid may leave barely warmed, close to saturated vapour, because it does not have time to pick up heat. The model gives a band. The best case is gas leaving at wall temperature; the worst is gas leaving just saturated.

The worst-case formula is just the energy balance: m = Q_wall divided by (h_sat_vapour - h_in). The best case integrates, because the gas leaving gets colder as the wall cools.

The model compares strategies by asking a sharper question than "how cold?". It asks for the minimum chilldown that still lets the no-vent fill succeed. You never chill further than needed, because every extra kelvin costs propellant.

## 7. The headline number, derived

The most useful single result is the ratio of wall heat to the cooling capacity of the load:

ratio = Q_wall / [m_load (h_sat_vapour - h_in)]

The denominator is how much heat the whole load could absorb if every kilogram boiled. Here are the model's numbers for a 1 m³ tank, 40 kg aluminium wall, from 290 K:

| Fluid | Load at 95 % fill | Wall heat | Load capacity | Ratio |
|---|---|---|---|---|
| LOX | 1017 kg | 5.9 MJ | 207 MJ | 2.9 % |
| LCH4 | 376 kg | 5.3 MJ | 182 MJ | 2.9 % |
| LH2 | 61 kg | 6.7 MJ | 28 MJ | 24 % |

Why is hydrogen so much worse? Liquid hydrogen is about 15 times less dense than LOX. The same 1 m³ holds only 61 kg, and its latent heat per kilogram, while larger than oxygen's, does not make up the difference. The wall heat, by contrast, barely depends on the fluid. So hydrogen's wall heat is a quarter of what the whole load can absorb, while for LOX it is a rounding error.

Methane and oxygen tie on this ratio, but they differ per kilogram loaded, and that difference is what the methalox point rests on. Methane's low density means about 2.7 times less mass in the same tank, so the chilldown losses per kilogram loaded are higher. On a methalox vehicle, the methane side will dominate the chilldown cost per kilogram delivered.

## 8. Line chilldown, worked example

Take a 3 m transfer line of half-inch 304 stainless tube with a 0.89 mm wall. Its mass is:

m = (pi/4)(D_o² - D_i²) L rho = (pi/4)(0.0127² - 0.01092²)(3)(8000) ≈ 0.79 kg

Cooling it from 290 K to about 5 K above LOX saturation at 150 kPa removes about 61 kJ, using the integral of stainless c_p. Each kilogram of LOX can absorb (h_sat_vapour - h_in) if it just boils, giving the worst case of about 0.31 kg. If the gas leaves at wall temperature, it absorbs more per kilogram, giving the best case of about 0.21 kg.

So the line costs a few hundred grams. That is small next to a 1000 kg load, which tells you where not to spend design effort. Unless the line is long or chilled many times, the receiver tank dominates.

## 9. What goes wrong if the assumptions fail

**Stratification.** Pressure rises faster than predicted, so fills stop early or need venting. Effect: lower fill fraction, more propellant lost.

**Liquid venting in microgravity.** Losses can be several times larger, and the charge-hold-vent advantage vanishes. Real systems use propellant management devices, such as screen channels or vanes, so the vent sees vapour.

**Heat leak during a long transfer.** Adds to the wall heat. Matters most for slow, small-flow transfers.

**Pressure drop in the line.** Liquid flashes partway along the line, two-phase flow chokes, and transfer slows. This is what the v2 transient model starts to address.

## Self-test questions

1. Why does the open-system energy balance use enthalpy for mass crossing the boundary but internal energy for mass inside the tank?
2. Why is the true wall heat from 290 K to 104 K less than m c_p(300 K) ΔT?
3. Explain in one sentence why the equilibrium model is a best case for no-vent fill.
4. A colleague says "methane and oxygen have the same wall-to-capacity ratio, so they are equally easy". What is missing from that argument?
5. Why can a ground tank simply vent, while an orbital tank needs charge-hold-vent or special hardware?

## Answers

1. Mass crossing the boundary carries its internal energy plus the flow work pv needed to push it in or out, which is exactly h. Mass staying inside does no flow work, so only u is stored.
2. Specific heat falls strongly with temperature, as lattice vibration modes freeze out, so the integral of c_p dT is smaller than room-temperature c_p times ΔT.
3. It assumes perfect mixing at a single temperature, while real tanks stratify, and the pressure follows the warmest surface rather than the average.
4. Mass per tank. Methane's lower liquid density means far less propellant per cubic metre, so the chilldown loss per kilogram delivered is roughly three times worse.
5. On the ground gravity puts vapour at the top, so the vent sees only gas. In orbit the liquid position is uncertain, so venting may expel liquid.

## Further reading
- Cengel and Boles, "Thermodynamics: An Engineering Approach", chapters 4 and 5 (control-volume energy balance).
- Barron, "Cryogenic Systems", Oxford University Press (cryogenic properties and heat capacity at low temperature).
- NIST Cryogenic Material Properties: https://trc.nist.gov/cryogenics/materials/materialproperties.htm
- CoolProp documentation: http://www.coolprop.org
- NASA Technical Reports Server, search "no-vent fill" and "cryogenic transfer line chilldown": https://ntrs.nasa.gov
