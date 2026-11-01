"""v2 transient line chilldown: calibration, check and application.

1. Calibrate the film-boiling multiplier C_fb on ONE flight test (F2,
   bare tube, continuous flow, 0.05 g throughout, Hartwig et al. 2022).
2. Check it on the other bare continuous high-flow tests (F1 at 0.38 g,
   F12 accelerated to 1 g near the end) and on the low-flow tests (F5, F8,
   F10, which include high-g periods).
3. Apply it to a 3 m, 1/2 in. 304 SS line for LOX, LCH4 and LN2: chilldown
   time and propellant used versus mass flow (figure 7).

Run from repo root:  python scripts/run_transient.py
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker  # noqa: F401
import numpy as np
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import validate_chilldown as V                       # noqa: E402
from cryotransfer import processes as P              # noqa: E402
from cryotransfer.thermo import Fluid                # noqa: E402
from cryotransfer.transient import Line, chilldown   # noqa: E402

FIG = ROOT / "figures"
RES = ROOT / "results"
T0 = 290.0
TEST_LINE = Line(V.LENGTH, V.OD, V.WALL, "SS304", V.RHO_SS)


def mean_flow(t: dict) -> float:
    """Average flow over the chilldown, from the measured mass and time."""
    return t["m_meas"] / t["t_chill"]


def calibrate(test_id: str = "F2") -> float:
    f = Fluid("Nitrogen")
    t = {r["test"]: r for r in V.load_tests()}[test_id]

    def g(lc):
        r = chilldown(f, TEST_LINE, mean_flow(t), t["p_in"], T0,
                      C_fb=np.exp(lc), dT_step=2.0, t_max=5000)
        return np.log(r.t_chill / t["t_chill"])

    return float(np.exp(brentq(g, np.log(0.5), np.log(50), xtol=0.005)))


def check(C_fb: float) -> list[dict]:
    f = Fluid("Nitrogen")
    rows = []
    for t in V.load_tests():
        if t["coating"] != "bare" or t["pulse"]:
            continue
        md = mean_flow(t)
        r1 = chilldown(f, TEST_LINE, md, t["p_in"], T0, C_fb=1.0,
                       dT_step=2.0, t_max=5000)
        rc = chilldown(f, TEST_LINE, md, t["p_in"], T0, C_fb=C_fb,
                       dT_step=2.0, t_max=5000)
        rows.append(dict(test=t["test"], note=t["note"], g=t["g"],
                         G=md / TEST_LINE.flow_area, t_meas=t["t_chill"],
                         t_uncal=r1.t_chill, t_cal=rc.t_chill,
                         m_meas=t["m_meas"], m_cal=rc.m_used,
                         err_cal=100 * (rc.t_chill / t["t_chill"] - 1)))
    return rows


def application(C_fb: float):
    line = Line(3.0, 0.0127, 0.00089, "SS304", 7900.0)   # as fig 3
    p_line, sub = 400e3, 5.0
    flows = np.geomspace(0.02, 0.5, 8)
    out = []
    for name, label in (("Oxygen", "LOX"), ("Methane", "LCH4"),
                        ("Nitrogen", "LN2")):
        f = Fluid(name)
        h_in = f.inlet_enthalpy(p_line, sub)
        b = P.wall_chilldown_mass(f, "SS304", line.mass, T0,
                                  f.T_sat(p_line) + 5, p_line, h_in)
        for md in flows:
            r = chilldown(f, line, md, p_line, T0, subcooling_K=sub,
                          C_fb=C_fb, n_nodes=30, dT_step=2.0, t_max=5000)
            out.append(dict(fluid=label, mdot=md, t=r.t_chill, m=r.m_used,
                            m_best=b["m_best"], m_worst=b["m_worst"],
                            eta=b["m_best"] / r.m_used, T_wet=r.T_wet))
    return line, out


def main():
    C = calibrate("F2")
    rows = check(C)
    line, app = application(C)
    RES.mkdir(exist_ok=True)
    with open(RES / "transient_check.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["test", "note", "g", "G_kg_m2s", "t_meas_s",
                    "t_model_Cfb1_s", "t_model_cal_s", "err_cal_pct",
                    "m_meas_kg", "m_model_cal_kg"])
        for r in rows:
            w.writerow([r["test"], r["note"], r["g"], round(r["G"], 1),
                        r["t_meas"], round(r["t_uncal"], 1),
                        round(r["t_cal"], 1), round(r["err_cal"], 1),
                        r["m_meas"], round(r["m_cal"], 3)])
        w.writerow([])
        w.writerow(["C_fb calibrated on F2", round(C, 3)])
    with open(RES / "transient_application.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["fluid", "mdot_kg_s", "t_chill_s", "m_used_kg",
                    "m_best_kg", "m_worst_kg", "efficiency_pct", "T_wet_K"])
        for a in app:
            w.writerow([a["fluid"], round(a["mdot"], 4), round(a["t"], 1),
                        round(a["m"], 3), round(a["m_best"], 3),
                        round(a["m_worst"], 3), round(100 * a["eta"], 1),
                        round(a["T_wet"], 1)])

    plt.rcParams.update({"font.size": 10, "axes.grid": True,
                         "grid.alpha": 0.3, "figure.dpi": 150,
                         "savefig.bbox": "tight"})
    colors = {"LOX": "#1f5aa6", "LCH4": "#d9822b", "LN2": "#6b6b6b"}
    fig, axs = plt.subplots(1, 2, figsize=(11.5, 4.4), layout="constrained")
    for lab, c in colors.items():
        sel = [a for a in app if a["fluid"] == lab]
        md = [a["mdot"] for a in sel]
        axs[0].plot(md, [a["t"] for a in sel], "o-", color=c, label=lab)
        axs[1].plot(md, [a["m"] for a in sel], "o-", color=c, label=lab)
        axs[1].axhline(sel[0]["m_best"], color=c, ls=":", lw=1)
    axs[0].set_xscale("log")
    axs[0].set_yscale("log")
    axs[0].set_xlabel("Mass flow [kg/s]")
    axs[0].set_ylabel("Chilldown time [s]")
    axs[0].set_title("3 m, 1/2 in. SS line from 290 K: time")
    axs[0].legend()
    axs[1].set_xscale("log")
    axs[1].set_yscale("log")
    axs[1].set_xlabel("Mass flow [kg/s]")
    axs[1].set_ylabel("Propellant used [kg]")
    axs[1].set_title("Propellant used (dotted: thermodynamic minimum)")
    axs[1].legend()
    for ax in axs:
        ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        ax.set_xticks([0.02, 0.05, 0.1, 0.2, 0.5])
        ax.set_xticklabels(["0.02", "0.05", "0.1", "0.2", "0.5"])
    fig.savefig(FIG / "fig7_transient_line_chilldown.png")
    plt.close(fig)

    print(f"C_fb calibrated on F2: {C:.3f}")
    for r in rows:
        print(r)
    for a in app:
        print({k: (round(v, 4) if isinstance(v, float) else v)
               for k, v in a.items()})
    return C, rows, app


if __name__ == "__main__":
    main()
