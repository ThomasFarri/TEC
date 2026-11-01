"""Validation 2: line chilldown energy bounds vs NASA LN2 flight tests.

Compares the v1 line chilldown bounds (wall_chilldown_mass) with the
measured total LN2 mass to chill a 0.914 m SS304 tube in reduced gravity
(Hartwig et al. 2022, npj Microgravity 8:33, Table 1). Data and source in
data/chilldown_ln2_flight_tests.csv.

The equilibrium bounds are thermodynamic limits: no real chilldown can use
less than m_best. The ratio m_best / m_measured is therefore a chilldown
efficiency, and it is the useful output of this comparison.

Assumptions (stated in VALIDATION.md):
- Initial wall temperature T0 = 290 K (not given in the paper; tubes were
  reheated with warm gas between tests). Band 250 to 300 K reported.
- Inlet is saturated liquid at the test-section inlet pressure.
- Vapour leaves at 101 kPa (outlet pressure not reported).
- End of chilldown: wall at T_sat(inlet pressure) + 2 K.
- Only the test-section tube is counted; the FEP coating mass is ignored
  (about 60 to 110 um of polymer, under 2 % of the wall heat capacity).
- The measured mass may include fluid that cooled plumbing downstream of
  the test section before the gas meter; that can only make the measured
  value larger, so efficiencies here are lower bounds on the true ones.

Run from repo root:  python scripts/validate_chilldown.py
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cryotransfer import processes as P   # noqa: E402
from cryotransfer.thermo import Fluid      # noqa: E402

DATA = ROOT / "data" / "chilldown_ln2_flight_tests.csv"
FIG = ROOT / "figures"
RES = ROOT / "results"

# Test section, Hartwig et al. 2022, Methods
LENGTH = 0.914
OD = 0.0127
WALL = 0.00051
RHO_SS = 7900.0     # kg/m3, 304 SS
T0 = 290.0
P_OUT = 101.325e3


def tube_mass() -> float:
    return P.tube_wall_mass(LENGTH, OD, WALL, RHO_SS)


def load_tests(path: Path = DATA) -> list[dict]:
    with open(path) as fh:
        lines = [ln for ln in fh if not ln.startswith("#")]
    rows = []
    for r in csv.DictReader(lines):
        rows.append(dict(
            test=r["test"], p_in=float(r["p_in_kPa"]) * 1e3,
            pulse=r["period_s"] != "", duty=float(r["duty_pct"]),
            g=float(r["g_level"]), coating=r["coating"],
            t_chill=float(r["t_chill_s"]), m_meas=float(r["m_chill_kg"]),
            Re=float(r["Re_steady"]), G=float(r["G_steady"]),
            note=r["note"]))
    return rows


def bounds(p_in: float, T0: float = T0, p_out: float = P_OUT,
           fluid: Fluid | None = None) -> dict:
    """Thermodynamic bounds on LN2 mass to chill the test section."""
    f = fluid or Fluid("Nitrogen")
    h_in = f.sat_liquid(p_in)["h"]
    T_end = f.T_sat(p_in) + 2.0
    return P.wall_chilldown_mass(f, "SS304", tube_mass(), T0, T_end, p_out,
                                 h_in)


def main():
    f = Fluid("Nitrogen")
    tests = load_tests()
    cache = {}
    out = []
    for t in tests:
        key = t["p_in"]
        if key not in cache:
            cache[key] = dict(
                base=bounds(key, fluid=f),
                cold=bounds(key, T0=250.0, fluid=f),
                warm=bounds(key, T0=300.0, fluid=f))
        b = cache[key]
        out.append(dict(**t, m_best=b["base"]["m_best"],
                        m_worst=b["base"]["m_worst"],
                        m_best_250=b["cold"]["m_best"],
                        m_best_300=b["warm"]["m_best"],
                        eta=b["base"]["m_best"] / t["m_meas"],
                        eta_sat=b["base"]["m_worst"] / t["m_meas"]))

    RES.mkdir(exist_ok=True)
    with open(RES / "validation_chilldown.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["test", "p_in_kPa", "flow", "coating", "g", "Re",
                    "t_chill_s", "m_meas_kg", "m_best_kg", "m_worst_kg",
                    "m_best_T0_250K", "m_best_T0_300K", "eta_best_pct",
                    "eta_satvap_pct", "note"])
        for o in out:
            w.writerow([o["test"], round(o["p_in"] / 1e3), "pulse"
                        if o["pulse"] else "continuous", o["coating"],
                        o["g"], round(o["Re"]), o["t_chill"], o["m_meas"],
                        round(o["m_best"], 4), round(o["m_worst"], 4),
                        round(o["m_best_250"], 4), round(o["m_best_300"], 4),
                        round(100 * o["eta"], 1), round(100 * o["eta_sat"], 1),
                        o["note"]])

    plt.rcParams.update({"font.size": 10, "axes.grid": True,
                         "grid.alpha": 0.3, "figure.dpi": 150,
                         "savefig.bbox": "tight"})
    fig, axs = plt.subplots(1, 2, figsize=(11.5, 4.4), layout="constrained")
    col = {"bare": "#6b6b6b", "4L": "#d9822b", "7L": "#1f5aa6"}
    ax = axs[0]
    for c in col:
        for pulse, mk in ((False, "o"), (True, "^")):
            sel = [o for o in out if o["coating"] == c and o["pulse"] == pulse]
            if sel:
                ax.scatter([o["Re"] for o in sel],
                           [o["m_meas"] for o in sel], color=col[c],
                           marker=mk, edgecolor="k",
                           label=f"{c}, {'pulse' if pulse else 'continuous'}")
    mb = np.mean([o["m_best"] for o in out])
    mw = np.mean([o["m_worst"] for o in out])
    ax.axhspan(min(o["m_best"] for o in out), max(o["m_worst"] for o in out),
               color="green", alpha=0.15,
               label="v1 thermodynamic band (290 K start)")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Steady-state Reynolds number")
    ax.set_ylabel("LN2 mass to chill test section [kg]")
    ax.set_title("Measured chilldown mass vs thermodynamic band")
    ax.legend(fontsize=7)

    ax = axs[1]
    for c in col:
        for pulse, mk in ((False, "o"), (True, "^")):
            sel = [o for o in out if o["coating"] == c and o["pulse"] == pulse]
            if sel:
                ax.scatter([o["Re"] for o in sel],
                           [100 * o["eta"] for o in sel], color=col[c],
                           marker=mk, edgecolor="k")
    ax.set_xscale("log")
    ax.set_xlabel("Steady-state Reynolds number")
    ax.set_ylabel("Chilldown efficiency m$_{best}$ / m$_{measured}$ [%]")
    ax.set_title("How close real chilldown gets to the limit")
    fig.savefig(FIG / "fig6_validation_chilldown.png")
    plt.close(fig)

    print(f"tube mass {tube_mass():.4f} kg; mean band {mb:.4f} to {mw:.4f} kg")
    for o in out:
        print(f"{o['test']:>4} p={o['p_in']/1e3:4.0f} {o['coating']:>4} "
              f"{'P' if o['pulse'] else 'C'} Re={o['Re']:7.0f} "
              f"m={o['m_meas']:6.3f} best={o['m_best']:.4f} "
              f"worst={o['m_worst']:.4f} eta={100*o['eta']:5.1f}%")
    return out


if __name__ == "__main__":
    main()
