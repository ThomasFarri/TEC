# Lesson 5: Sensitivity studies, or which knobs actually matter

Lessons 1 to 4 built and checked the model. This lesson uses it. A sensitivity study asks: if I change one input and hold the rest, how much does the answer move? It tells you where to spend design effort and, for the interview, which assumptions you must be able to defend hardest.

## 1. Why one-at-a-time sweeps, and what they hide

Take a baseline case (1 m3 tank, 40 kg aluminium wall, wall starts at 290 K, supply liquid 5 K subcooled at 400 kPa, receiver limit 345 kPa, vent down to 50 kPa, 95 % fill target). Change one input over a sensible range, record the output, put it back. Plot the output against the input.

The slope of that curve, normalised, is the local sensitivity: S = (dY/Y) / (dX/X). A large S means the output is touchy about that input.

What this hides: interactions. If the effect of subcooling depends on the pressure limit, a one-at-a-time sweep shows only a slice. For a first study this is the right tool, because you can read each curve by eye. Say in the note that interactions are not explored.

## 2. The output metric

We use chilldown loss as a percentage of the loaded mass, for two strategies.

Charge-hold-vent (CHV): charge liquid until the receiver reaches the pressure limit, let wall and fluid equilibrate, vent down, repeat. Stop when a no-vent fill would reach 95 %. Loss is the vented mass.

Flow-through: cool the wall by continuous flow and vent to the warmest wall temperature from which a no-vent fill still works. Loss is reported as a band, between "vented gas leaves at wall temperature" (best) and "leaves as saturated vapour" (worst), as in lesson 1.

## 3. The physics behind every curve: one energy inequality

A no-vent fill works if the liquid, after absorbing the wall's heat, does not push the pressure over the limit. Roughly, the heat the wall must give up is

Q_wall = m_wall (H_wall(T0) - H_wall(T_final)),

and the cooling the load can supply before the pressure limit is hit is

Q_cool = m_load (h_sat vapour at p_max - h_in).

Everything below is a way of moving one side of this inequality. Because h_in sits in Q_cool, subcooling the inlet raises Q_cool for free.

## 4. The results, read as physics

**Inlet subcooling (top left).** At 0 K subcooling LOX loses 5 % and LCH4 13 % of the load in CHV. At 5 K, 0.44 % and 1.4 %. At 10 K both are zero: the tank fills with no chilldown at all. Why so steep? Subcooling 5 K adds about 8.8 kJ/kg to the LOX cooling capacity (194.6 to 203.3 kJ/kg, from the model), a gain of 4.5 %. That looks small. But the margin in the inequality of section 3 at baseline is itself only a few percent (lesson 1: wall energy is about 3 % of load capacity for LOX), so a few percent of capacity swings the outcome from "needs 1 cycle" to "needs none". A system sitting near a threshold is sensitive. That is the single most useful message for TEC: for oxygen and methane, 5 to 10 K of subcooling on the supply side may remove the need for receiver chilldown.

**Receiver pressure limit (top right).** Raising the limit from 345 to 450 kPa takes losses to zero for both fluids. Two effects act: the saturated vapour enthalpy at the limit rises slightly, and more important, the final equilibrium temperature allowed is higher, so less wall heat has to be removed first. The cost is structural: a higher limit means a heavier tank, which means a larger m_wall. That feedback is not in the sweep, since wall mass is held at 40 kg. Say so.

**Initial wall temperature (bottom left).** If the wall starts at 250 K or below, LOX needs no chilldown. LCH4 needs some from 250 K. Starting at 320 K roughly doubles the LOX loss against 290 K (0.84 % against 0.44 %). The dependence is not linear because the specific heat of aluminium falls strongly with temperature: the first 40 K of cooling from 290 K costs far more energy than the last 40 K above 120 K. This is why a pre-cooled receiver, or an eclipse period that cools it passively, is so valuable.

**Material (bottom right).** Stainless steel has about half the specific heat of aluminium at 290 K (471 against 939 J/(kg K)). So the answer depends on what you hold equal:

- Same mass, 40 kg SS against 40 kg Al: the wall holds about 3.05 MJ against 5.99 MJ between 290 K and 100 K, and SS needs no chilldown at all in this case.
- Same wall thickness: steel is 8000/2700 = 2.96 times denser, so the same shell is 118 kg. Then it holds about 9.0 MJ, 50 % more than aluminium, and loss is 1.4 % for LOX against 0.44 %.

So "stainless is worse" is true at equal thickness, false at equal mass. A real design is neither: stainless is stronger, so the wall can be thinner. The model cannot settle it without a structural sizing, which is outside this project. State the pair of cases and let the reader pick.

## 5. A feature that looks like a bug: the zig-zag in CHV

Look at LOX CHV at 0 K subcooling (5.5 %) and 2 K (9.8 %). Less subcooling gave less loss. This is not physics, it is quantisation. CHV stops after a whole number of cycles. At 0 K subcooling the last cycle happens to stop just after the target is met. At 2 K the model needs four cycles in both cases but the final cycle vents more. The loss is a staircase, not a smooth curve.

The flow-through band does not do this, because the end temperature is found continuously. So when you want a trend, read the band. When you want a plan, read CHV. Also note that near the cliff (at or below about 2 K subcooling for LOX) flow-through is reported as infeasible, since even cooling to just above saturation leaves too little liquid capacity. Gaps in the curves mean "target fill not reachable in this model", not "zero".

## 6. What goes wrong if the assumptions fail

All results here are from the equilibrium model, which is a best case (lesson 2: real tanks ran up to 26 % above its pressure). The cliffs are where this matters most. Near a threshold, a few percent of non-equilibrium error moves the loss from 0 to several percent. So treat "10 K of subcooling needs no chilldown" as "possibly", and the sign of the trend, not the exact threshold, as the robust finding. The sweep also ignores heat leak, sloshing and line chilldown (lesson 3 and 4 give that part, 2.4 to 3.4 kg for a 3 m LOX line).

## 7. Worked example

LOX, baseline. Load 1017 kg. Capacity per kg at 5 K subcooling 203.3 kJ/kg gives 206.8 MJ. Wall energy from 290 K down to 100 K is 5.99 MJ, about 2.9 %. CHV needs one cycle and loses 0.44 %, which is 4.4 kg. Raise T0 to 320 K: two cycles, 0.84 %, 8.5 kg. Drop subcooling to 0 K: capacity falls to 194.6 kJ/kg and the loss rises to 5.5 %, 56 kg (but see the staircase caveat).

## Self-test questions

1. Why does a 4.5 % change in cooling capacity change LOX loss from 5 % to 0.4 %?
2. Why is CHV loss not monotonic in subcooling, and which curve would you quote as a trend?
3. Stainless steel has half the specific heat of aluminium. Why is it still worse at equal wall thickness?
4. Raising the pressure limit to 450 kPa removes chilldown loss in the model. What real-world cost is hidden by holding wall mass at 40 kg?
5. A reviewer says "your zero-loss result at 10 K subcooling is optimistic." Give two reasons they are right.

## Answers

1. The margin between wall energy and cooling capacity is only a few percent, so the system sits near a threshold. Small shifts move the number of CHV cycles, and the last cycle dominates the loss.
2. Because cycles are whole numbers, so the loss is a staircase and the last cycle can vent more or less. The flow-through band is continuous and gives the trend.
3. Density is 2.96 times higher, which outweighs the 0.5 times specific heat: 1.48 times the heat to remove (9.0 against 6.0 MJ).
4. A higher pressure rating needs thicker walls, so more thermal mass and more heat to remove. The sweep does not feed this back.
5. The model is equilibrium, a best case, and real fills ran up to 26 % higher pressure than it predicted. It also ignores heat leak, line chilldown and any residual gas or liquid carry-over during venting.

## Sources

NIST cryogenic materials data for the specific heats. CoolProp for fluid properties. Textbook background: Barron, Cryogenic Heat Transfer, and Incropera, Fundamentals of Heat and Mass Transfer (sensitivity and lumped capacity). Model results: results/sensitivity.csv, figures/fig4_sensitivity.png.
