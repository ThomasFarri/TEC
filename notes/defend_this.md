# Defend this: assumptions and likely questions

For the 15-minute call with Cédric. Read the note first, then this. Each answer is short on purpose. If you cannot explain an answer in your own words, reread the matching lesson (numbers in brackets).

## A. The assumptions, one line each

| Assumption | Why it was made | Which way it biases the answer | Lesson |
|---|---|---|---|
| Fluid and wall at one temperature, fluid homogeneous | Makes the problem a single energy balance | Optimistic: real tanks stratify and reach higher pressure | 1, 2 |
| No heat leak from the environment | Transfer is fast, minutes to hours | Slightly optimistic; small against wall energy | 1 |
| Venting releases vapour only | Simplest case | Optimistic: venting liquid in microgravity loses more | 1 |
| Line chilldown given as a band | Bounds without a flow model | Minimum is a true limit; real use is 1.5 to 30 times higher | 3 |
| Wall lumped radially, no axial conduction, quasi-steady fluid (v2) | Biot about 0.01, thin steel wall, fluid crosses tube in about 1 s vs 15 s chilldown | Fails for flanges, valves, aluminium lines | 4 |
| One film-boiling factor C_fb = 2.41 calibrated on one LN2 test | Absorbs our own correlation choices | Unknown for LOX and LCH4 | 4 |
| Al 6061 cp used for the Al 2219 test tanks | Both aluminium alloys, close curves | Small, not checked against a 2219 dataset | 2 |
| Initial wall 290 K in the line tests | Paper does not give it | 250 K lowers the minimum 19 %; 300 K raises it 4 % | 3 |
| Properties from CoolProp | Standard reference equations | Negligible against the other errors | 1 |

## B. Likely questions and short answers

**1. Why equilibrium? Real tanks are not in equilibrium.**
It is a bound. Equilibrium gives the lowest pressure for a given mass and energy, so it is a best case. On 32 LH2 fills the mean absolute error was 7 % and the worst underprediction 26 %, for spray-bar runs with warm inlet liquid. I advise a margin of that order. [2]

**2. How do you know this applies to LOX and LCH4 when you validated on hydrogen?**
I do not know, and I say so. The argument is that the wall energy is about 3 % of load cooling capacity for LOX and LCH4 against 24 % for LH2, so the wall matters less and equilibrium should be closer. That is an argument, not a validation. Real validation needs LOX or LCH4 data, which I could not find in public sources. [1, 2]

**3. What is the key number?**
Receiver chilldown loss of about 0.4 % (LOX) and 1.4 % (LCH4) of the load for a 1 m3 aluminium receiver with a 40 kg wall from 290 K, at 5 K inlet subcooling. And that 10 K subcooling takes both to zero in this model. [5]

**4. Why is methane three times worse per kilogram than oxygen?**
Saturated liquid at 345 kPa is about 0.40 g/cm3 for methane against 1.07 g/cm3 for oxygen. A tank of the same volume holds 376 kg of methane and 1017 kg of oxygen, but the wall energy is about the same, so the loss per kilogram loaded is larger. [1]

**5. Why is CHV loss non-monotonic?**
Cycles are whole numbers. The loss is a staircase, and the last cycle can vent more or less. The flow-through band gives the smooth trend. [5]

**6. Why does 5 K subcooling matter so much?**
It adds about 4.5 % to the cooling capacity per kg, and the system sits near a threshold because wall energy is only about 3 % of the load capacity. [5]

**7. Your transient model is calibrated on one test. Why trust it?**
Partly I do not. Calibration was F2; F1 and F12 then agree within 17 % and 9 %. At low flow (G below about 40 kg/(m2 s)) it is 3 to 6 times too slow. I restrict it to G above about 300 kg/(m2 s). It is LN2 calibrated and used on LOX and LCH4 by extrapolation. [4]

**8. Why is chilldown efficiency only 4 to 9 %?**
A vapour film insulates the hot wall (film boiling, Leidenfrost effect), so much of the liquid passes through unevaporated. Measured LN2 flight tests show 3 to 69 %, best with coatings or pulse flow. [3]

**9. Why are line and receiver treated separately?**
Different physics and different data. The line is a flow-boiling problem with a transient; the receiver is a closed-volume energy problem. Combined effects are not modelled. [3, 4]

**10. What about microgravity?**
The equilibrium model does not depend on gravity. The line tests were flown at 0.05 g and 0.38 g. What changes in microgravity is liquid location, venting and mixing, which this model cannot represent. [1, 3]

**11. Stainless or aluminium?**
Equal mass: stainless holds half the energy. Equal wall thickness: it is 2.96 times denser, so it holds about 50 % more. The answer needs structural sizing, which I have not done. [5]

**12. What is the biggest weakness?**
Equilibrium plus no LOX or LCH4 validation. Followed by the transient model's low-flow failure.

**13. What would you do next with data?**
Run the line model against LOX or LCH4 chilldown tests, add liquid carry-over in venting, and compare the final pressure against a spray-bar test with warm inlet to calibrate a non-equilibrium correction.

**14. Why a pressure limit of 345 kPa?**
It is the 50 psia limit of the NASA test tank, used as a baseline. A real receiver may differ, and the results are sensitive to it. This is one of the questions in the note.

## C. Numbers to have in your head

- Wall energy to load capacity: 2.9 % LOX, 2.9 % LCH4, 24 % LH2.
- Baseline CHV loss: LOX 4.4 kg (0.44 %), LCH4 5.2 kg (1.4 %).
- Validation 1: 32 fills, 7 % mean absolute error, 26 % worst, 12 kPa mean.
- Validation 2: 28 tests, 3.3 to 69 % efficiency, bare tube high flow about 4 %.
- v2: C_fb = 2.41; other high-flow tests -17 % and -9 %; unusable below about 300 kg/(m2 s).
- 3 m LOX line: 0.2 kg minimum, 2.4 to 3.4 kg modelled.

## D. Things you must not say

- "The model predicts X" without the error bar.
- "Validated for LOX": it is not.
- Any statement about TEC's design, which you do not know.
