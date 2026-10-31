"""Parametric studies for the v1 equilibrium model.

Outputs figures to ../figures and a summary table to ../results/summary.csv.
Run from repo root:  python scripts/run_studies.py
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

from cryotransfer import materials                      # noqa: E402
from cryotransfer import processes as P                # noqa: E402
from cryotransfer.thermo import Fluid, Tank, initial_state  # noqa: E402

FIG = ROOT / "figures"
RES = ROOT / "results"
FIG.mkdir(exist_ok=True)
RES.mkdir(exist_ok=True)

# --- baseline case (documented in README) ----------------------------------
P_SUPPLY = 400e3      # Pa, supply tank pressure
SUBCOOL = 5.0         # K below T_sat(P_SUPPLY)
P_MAX = 345e3         # Pa, receiver pressure limit (50 psia)
P_VENT = 50e3         # Pa, vent-down pressure for CHV
TARGET = 0.95         # target liquid fill fraction
T0 = 290.0            # K, initial wall temperature
VOL = 1.0             # m^3 receiver volume
WALL = 40.0           # kg receiver wall (Al 6061)

FLUIDS = {"Oxygen": "LOX", "Methane": "LCH4", "Hydrogen": "LH2"}
COLORS = {"Oxygen": "#1f5aa6", "Methane": "#d9822b", "Hydrogen": "#6b6b6b"}

plt.rcParams.update({"font.size": 10, "axes.grid": True, "grid.alpha": 0.3,
                     "figure.dpi": 150, "savefig.bbox": "tight"})


def load_mass(f: Fluid) -> float:
    return TARGET * f.rho_sat_liq_T(f.T_sat(P_MAX)) * VOL


def study_fill_pressure_vs_wall_T():
    """Fig 1: equilibrium pressure at 95 % fill vs initial wall temperature."""
    fig, ax = plt.subplots(figsize=(6, 4))
    rows = []
    for name, label in FLUIDS.items():
        f = Fluid(name)
        h_in = f.inlet_enthalpy(P_SUPPLY, SUBCOOL)
        t = Tank(VOL, WALL)
        Ts = np.linspace(f.T_sat(P_VENT) + 2, T0, 30)
        ps = []
        for Tw in Ts:
            s0 = initial_state(f, t, Tw, P_VENT)
            try:
                r = P.no_vent_fill(f, t, s0, h_in, 1e9, TARGET)
                ps.append(r["p_at_target"] / 1e3)
            except (RuntimeError, ValueError):
                ps.append(np.nan)   # target fill unreachable in model range
            rows.append([label, round(Tw, 2), round(ps[-1], 2)])
        ax.plot(Ts, ps, color=COLORS[name], label=label, lw=2)
    ax.axhline(P_MAX / 1e3, color="k", ls="--", lw=1)
    ax.text(100, P_MAX / 1e3 * 1.06, "receiver limit 345 kPa", fontsize=8)
    ax.set_yscale("log")
    ax.set_xlabel("Receiver wall temperature at start of no-vent fill [K]")
    ax.set_ylabel("Equilibrium pressure at 95 % fill [kPa]")
    ax.set_title("No-vent fill: how cold must the tank be?")
    ax.legend()
    fig.savefig(FIG / "fig1_nvf_pressure_vs_wall_T.png")
    plt.close(fig)
    _write("fig1_nvf_pressure_vs_wall_T.csv",
           ["fluid", "wall_T_K", "p_at_95pct_kPa"], rows)


def study_loss_vs_wall_mass():
    """Fig 2: chilldown propellant (% of load) vs wall mass per volume."""
    ratios = np.array([10, 20, 30, 40, 60, 80, 100, 150])
    fig, ax = plt.subplots(figsize=(6, 4))
    rows = []
    for name, label in FLUIDS.items():
        f = Fluid(name)
        h_in = f.inlet_enthalpy(P_SUPPLY, SUBCOOL)
        load = load_mass(f)
        chv, ftb, ftw = [], [], []
        for r_ in ratios:
            t = Tank(VOL, r_ * VOL)
            s0 = initial_state(f, t, T0, P_VENT)
            c = P.charge_hold_vent(f, t, s0, h_in, P_MAX, P_VENT, P_MAX,
                                   TARGET, max_cycles=40)
            ft = P.min_flow_through(f, t, T0, h_in, P_VENT, P_MAX, TARGET)
            chv.append(100 * c.vented_mass / load if c.reached_target
                       else np.nan)
            ftb.append(100 * ft["m_best"] / load if ft["feasible"] else np.nan)
            ftw.append(100 * ft["m_worst"] / load if ft["feasible"]
                       else np.nan)
            rows.append([label, r_, c.cycles, round(c.vented_mass, 3),
                         round(ft.get("m_best", np.nan), 3),
                         round(ft.get("m_worst", np.nan), 3), round(load, 1)])
        ax.plot(ratios, chv, "o-", color=COLORS[name], label=f"{label} CHV")
        ax.fill_between(ratios, ftb, ftw, color=COLORS[name], alpha=0.2,
                        label=f"{label} flow-through band")
    ax.set_xlabel("Receiver wall mass per unit volume [kg/m$^3$]")
    ax.set_ylabel("Chilldown propellant lost [% of loaded mass]")
    ax.set_yscale("log")
    ax.set_title("Receiver chilldown cost, start at 290 K, 95 % fill")
    ax.legend(fontsize=7, ncol=2)
    fig.savefig(FIG / "fig2_loss_vs_wall_mass.png")
    plt.close(fig)
    _write("fig2_loss_vs_wall_mass.csv",
           ["fluid", "wall_kg_per_m3", "chv_cycles", "chv_vented_kg",
            "ft_best_kg", "ft_worst_kg", "load_kg"], rows)


def study_line_chilldown():
    """Fig 3: transfer-line chilldown propellant vs line length."""
    L = np.linspace(1, 10, 10)
    p_line = 150e3
    fig, ax = plt.subplots(figsize=(6, 4))
    rows = []
    for name, label in FLUIDS.items():
        f = Fluid(name)
        h_in = f.inlet_enthalpy(P_SUPPLY, SUBCOOL)
        best, worst = [], []
        for l_ in L:
            mw = P.tube_wall_mass(l_, 0.0127, 0.00089, 8000)  # 1/2" SS304
            r = P.wall_chilldown_mass(f, "SS304", mw, T0,
                                      f.T_sat(p_line) + 5, p_line, h_in)
            best.append(r["m_best"])
            worst.append(r["m_worst"])
            rows.append([label, l_, round(mw, 3), round(r["m_best"], 4),
                         round(r["m_worst"], 4)])
        ax.fill_between(L, best, worst, color=COLORS[name], alpha=0.3,
                        label=label)
        ax.plot(L, worst, color=COLORS[name], lw=1)
    ax.set_xlabel("Transfer line length [m] (1/2 in. 304 SS tube)")
    ax.set_ylabel("Propellant to chill line [kg]")
    ax.set_title("Line chilldown: band between exit-at-wall-T and sat. vapour")
    ax.legend()
    fig.savefig(FIG / "fig3_line_chilldown.png")
    plt.close(fig)
    _write("fig3_line_chilldown.csv",
           ["fluid", "length_m", "line_mass_kg", "m_best_kg", "m_worst_kg"],
           rows)


def energy_ratio_table():
    """Wall energy to remove vs cooling capacity of the propellant load."""
    rows = []
    t = Tank(VOL, WALL)
    dH = WALL * float(materials.enthalpy("Al6061", T0)
                      - materials.enthalpy("Al6061", 120.0))
    for name, label in FLUIDS.items():
        f = Fluid(name)
        h_in = f.inlet_enthalpy(P_SUPPLY, SUBCOOL)
        h_g = f.sat_vapour(P_MAX)["h"]
        cap = load_mass(f) * (h_g - h_in)
        dH_f = WALL * float(materials.enthalpy("Al6061", T0)
                            - materials.enthalpy("Al6061",
                                                 max(f.T_sat(P_MAX), 4.5)))
        rows.append([label, round(load_mass(f), 1), round(dH_f / 1e6, 2),
                     round(cap / 1e6, 1), round(100 * dH_f / cap, 2)])
    _write("energy_ratio.csv", ["fluid", "load_kg", "wall_energy_MJ",
                                "load_cooling_capacity_MJ", "ratio_pct"], rows)
    return rows, dH


def _write(fname, header, rows):
    with open(RES / fname, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)


if __name__ == "__main__":
    print("energy ratio", energy_ratio_table()[0], flush=True)
    study_line_chilldown()
    print("fig3 done", flush=True)
    study_fill_pressure_vs_wall_T()
    print("fig1 done", flush=True)
    study_loss_vs_wall_mass()
    print("fig2 done", flush=True)
