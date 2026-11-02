"""Sensitivity study (Figure 4) for the v1 equilibrium model.

Four one-at-a-time sweeps around the baseline of run_studies.py:
inlet subcooling, receiver pressure limit, initial wall temperature and
tank material. Metric: propellant lost in receiver chilldown as a percent of
the loaded mass, for charge-hold-vent (CHV) and for the flow-through
optimum (best/worst bounds). LOX and LCH4 only.

Run from repo root:  python scripts/run_sensitivity.py
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

from cryotransfer import processes as P                      # noqa: E402
from cryotransfer.thermo import Fluid, Tank, initial_state    # noqa: E402

FIG = ROOT / "figures"
RES = ROOT / "results"

BASE = dict(p_supply=400e3, subcool=5.0, p_max=345e3, p_vent=50e3,
            target=0.95, T0=290.0, vol=1.0, wall=40.0, material="Al6061")
FLUIDS = {"Oxygen": "LOX", "Methane": "LCH4"}
COLORS = {"Oxygen": "#1f5aa6", "Methane": "#d9822b"}

plt.rcParams.update({"font.size": 9, "axes.grid": True, "grid.alpha": 0.3,
                     "figure.dpi": 150, "savefig.bbox": "tight"})


def run_case(name: str, **over) -> dict:
    """Evaluate one parameter set. Returns percentages of loaded mass.

    Infeasible cases give NaN (target fill cannot be reached under the
    pressure limit, or the inlet would be below the triple point).
    """
    c = {**BASE, **over}
    f = Fluid(name)
    out = dict(chv_pct=np.nan, chv_cycles=np.nan, ft_best_pct=np.nan,
               ft_worst_pct=np.nan, ft_T_end=np.nan, load=np.nan)
    try:
        h_in = f.inlet_enthalpy(c["p_supply"], c["subcool"])
        t = Tank(c["vol"], c["wall"], c["material"])
        load = c["target"] * f.rho_sat_liq_T(f.T_sat(c["p_max"])) * c["vol"]
        out["load"] = load
        s0 = initial_state(f, t, c["T0"], c["p_vent"])
        r = P.charge_hold_vent(f, t, s0, h_in, c["p_max"], c["p_vent"],
                               c["p_max"], c["target"], max_cycles=40)
        if r.reached_target:
            out["chv_pct"] = 100 * r.vented_mass / load
            out["chv_cycles"] = r.cycles
        ft = P.min_flow_through(f, t, c["T0"], h_in, c["p_vent"],
                                c["p_max"], c["target"])
        if ft["feasible"]:
            out["ft_best_pct"] = 100 * ft["m_best"] / load
            out["ft_worst_pct"] = 100 * ft["m_worst"] / load
            out["ft_T_end"] = ft["T_end"]
    except (ValueError, RuntimeError):
        pass
    return out


SWEEPS = {
    "subcool": dict(x=np.array([0, 2, 5, 10, 15, 20]), key="subcool",
                    xlabel="Inlet subcooling [K]"),
    "p_max": dict(x=np.array([200, 250, 300, 345, 450, 600]) * 1e3,
                  key="p_max", xlabel="Receiver pressure limit [kPa]",
                  scale=1e-3),
    "T0": dict(x=np.array([150, 200, 250, 290, 320]), key="T0",
               xlabel="Initial wall temperature [K]"),
}


def main():
    rows = []
    fig, axs = plt.subplots(2, 2, figsize=(9, 6.5))
    ax_list = [axs[0, 0], axs[0, 1], axs[1, 0]]
    for ax, (sname, sw) in zip(ax_list, SWEEPS.items()):
        for name, label in FLUIDS.items():
            res = [run_case(name, **{sw["key"]: x}) for x in sw["x"]]
            xs = sw["x"] * sw.get("scale", 1.0)
            ax.plot(xs, [r["chv_pct"] for r in res], "o-", lw=2,
                    color=COLORS[name], label=f"{label} CHV")
            ax.fill_between(xs, [r["ft_best_pct"] for r in res],
                            [r["ft_worst_pct"] for r in res],
                            color=COLORS[name], alpha=0.2,
                            label=f"{label} flow-through")
            for x, r in zip(sw["x"], res):
                rows.append([sname, label, x, r["chv_cycles"],
                             r["chv_pct"], r["ft_best_pct"],
                             r["ft_worst_pct"], r["ft_T_end"], r["load"]])
        ax.set_xlabel(sw["xlabel"])
        ax.set_ylabel("Chilldown loss [% of load]")
        ax.set_ylim(bottom=0)
        ax.set_yscale("symlog", linthresh=0.1)
    axs[0, 0].legend(fontsize=6.5)
    # material panel: equal mass, equal wall thickness (SS 8000/2700 heavier)
    ax = axs[1, 1]
    cases = [("Al, 40 kg", "Al6061", 40.0), ("SS, 40 kg", "SS304", 40.0),
             ("SS, 118 kg\n(same thickness)", "SS304", 40.0 * 8000 / 2700)]
    w = 0.35
    for j, (name, label) in enumerate(FLUIDS.items()):
        vals = []
        for lab, mat, wm in cases:
            r = run_case(name, material=mat, wall=wm)
            vals.append(r["chv_pct"])
            rows.append(["material", label, lab.replace("\n", " "),
                         r["chv_cycles"], r["chv_pct"], r["ft_best_pct"],
                         r["ft_worst_pct"], r["ft_T_end"], r["load"]])
        ax.bar(np.arange(3) + (j - 0.5) * w, vals, w, color=COLORS[name],
               label=f"{label} CHV")
    ax.set_xticks(range(3))
    ax.set_xticklabels([c[0] for c in cases], fontsize=7)
    ax.set_ylabel("CHV loss [% of load]")
    ax.legend(fontsize=7)
    fig.suptitle("Sensitivity of receiver chilldown loss (1 m$^3$ tank, "
                 "baseline: 5 K subcool, 345 kPa limit, 290 K start, 40 kg Al)")
    fig.tight_layout()
    fig.savefig(FIG / "fig4_sensitivity.png")
    with open(RES / "sensitivity.csv", "w", newline="") as fh:
        w_ = csv.writer(fh)
        w_.writerow(["sweep", "fluid", "value", "chv_cycles", "chv_pct",
                     "ft_best_pct", "ft_worst_pct", "ft_T_end_K", "load_kg"])
        for r in rows:
            w_.writerow([round(v, 4) if isinstance(v, float) else v
                         for v in r])


if __name__ == "__main__":
    main()
