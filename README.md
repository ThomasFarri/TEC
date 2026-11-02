# cryotransfer

Energy-budget model for in-orbit cryogenic propellant transfer: transfer-line chilldown, receiver tank chilldown (charge-hold-vent or flow-through), and no-vent fill. Built to compare liquid oxygen and liquid methane against liquid hydrogen, where most published test data exists.

Author: Thomas Farrugia, MEng Aerospace Engineering, University of Bristol.

## What it answers

1. How much propellant does it cost to chill a warm transfer line?
2. How cold must a receiver tank be before a no-vent fill can reach 95 % without exceeding its pressure limit?
3. How much propellant is lost getting it there, and how does that scale with tank wall mass?

## Key v1 result

The wall energy that must be removed, as a share of the cooling capacity of the propellant load, is about 3 % for LOX and LCH4 but about 24 % for LH2 (1 m³ aluminium receiver, 40 kg wall, cooled from 290 K). That ratio drives everything below it.

For this baseline case, the equilibrium model gives:
- **LOX:** receiver pre-chill costs about 0.4 % of the load.
- **LCH4:** about 1.4 %.
- **LH2:** about 2.7 %, and it climbs steeply with wall mass.

Per kilogram loaded, methane costs roughly three times more than oxygen, because of its low liquid density.

Thermodynamically, methalox transfer is forgiving. So the hard engineering problem is not the energy budget. It is the non-equilibrium behaviour the energy budget ignores: stratification, heat-transfer rate during fill, and venting liquid in microgravity.

## Validation and v2 (1 Nov)

- **No-vent fill vs NASA LH2 tests** (32 fills, two tanks): mean absolute error 7 % in final pressure, worst 26 %. Figure 5. Details in VALIDATION.md.
- **Line chilldown vs NASA LN2 flight tests** (28 tests): every test uses more than the v1 thermodynamic minimum, as it must. Real efficiency is 3 to 69 %; a bare tube at high flow is about 4 %. Figure 6.
- **v2 transient line chilldown** (`cryotransfer/transient.py`): 1D wall nodes with a film, transition and nucleate boiling curve. One film-boiling factor calibrated on one test; the other high-flow tests agree within 17 %. Not valid below a mass flux of about 300 kg/m2 s. A 3 m half-inch LOX line from 290 K needs about 2.4 to 3.4 kg. Figure 7.

## Assumptions (v1)

- Fluid and wall are in thermal equilibrium and the fluid is homogeneous. This is a best case: real tanks stratify and reach higher pressure.
- Rigid tank, no environmental heat leak during transfer, no line pressure drop.
- Venting releases vapour only. In microgravity, liquid can be vented, which raises losses.
- Line chilldown is bounded between vapour leaving saturated (worst case) and vapour leaving at local wall temperature (best case).
- Properties: CoolProp (HEOS) for fluids, NIST cryogenic fits for Al 6061 and 304 SS.

## Baseline case

| Parameter | Value |
|---|---|
| Supply | 400 kPa, inlet 5 K subcooled |
| Receiver pressure limit | 345 kPa |
| Vent pressure | 50 kPa |
| Target fill | 95 % |
| Receiver | 1 m³, 6061 Al, 40 kg wall, initially 290 K |
| Transfer line | 1/2 in. 304 SS tube, 0.89 mm wall |

## Use

```
pip install CoolProp scipy matplotlib pytest
python -m pytest -q
python scripts/run_studies.py      # writes figures/ and results/
```

## Status

- v1 equilibrium model: done.
- Validation against NASA LH2 no-vent fill and chilldown data: in progress.
- v2 transient line chilldown with flow-boiling correlations: planned.

Update 2 Nov: sensitivity study (figure 4), technical note draft (notes/technical_note.md), defend-this sheet, outreach drafts (not sent) and lessons 5 to 8 added.
