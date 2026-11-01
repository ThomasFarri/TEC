"""Validation 1: equilibrium no-vent fill vs NASA Lewis LH2 tests.

Compares the v1 model's equilibrium pressure at the measured final fill
level against the measured final pressure, for two NASA Lewis tanks:
  A: 4.96 m3 K-Site tank (Taylor and Chato, NASA TM-106018, Table I)
  B: 2.01 m3 (71 ft3) tank (Chato, NASA TM-106293, Table 1)
Test data live in data/nvf_lh2_tests.csv with their sources.

Modelling choices (all stated in VALIDATION.md):
- Fluid: ParaHydrogen (CoolProp). The liquid supply is essentially
  equilibrium para-hydrogen at 20 to 23 K. Normal hydrogen is run as a
  sensitivity check.
- Inlet enthalpy: saturated liquid at the measured average inlet
  temperature (the reports give time-averaged inlet T only).
- Wall: whole tank mass at the measured initial wall temperature, using
  the Al 6061 cp fit as a stand-in for 2219 Al.
- Initial ullage: hydrogen vapour at the wall temperature and P0_BASE
  (initial pressure is not tabulated), capped below saturation.
- Heat leak: 4.66 W for tank A over the fill duration (TM-106018);
  none for tank B (not reported). Fill duration = load mass / flow.

Run from repo root:  python scripts/validate_nvf.py
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

from cryotransfer import processes as P                     # noqa: E402
from cryotransfer.thermo import Fluid, Tank, TankState, initial_state  # noqa: E402

DATA = ROOT / "data" / "nvf_lh2_tests.csv"
FIG = ROOT / "figures"
RES = ROOT / "results"

R_TO_K = 1 / 1.8
LBM_TO_KG = 0.45359237
PSI_TO_PA = 6894.757

TANKS = {
    # volume m3, wall kg, heat leak W
    "A": dict(volume=4.96, wall=149.63, q_leak=4.66,
              label="4.96 m$^3$ K-Site tank (TM-106018)"),
    "B": dict(volume=71 * 0.0283168, wall=243 * LBM_TO_KG, q_leak=0.0,
              label="2.01 m$^3$ tank (TM-106293)"),
}
P0_BASE = 7e3     # Pa (about 1 psia) assumed initial ullage pressure


def load_tests(path: Path = DATA) -> list[dict]:
    """Read the test table and convert everything to SI."""
    rows = []
    with open(path) as fh:
        lines = [ln for ln in fh if not ln.startswith("#")]
    for r in csv.DictReader(lines):
        si = r["units"] == "SI"
        if r["units"] not in ("SI", "US"):
            raise ValueError(f"Unknown units '{r['units']}' in {r['test']}")
        k = 1.0 if si else R_TO_K
        rows.append(dict(
            source=r["source"], test=r["test"], injection=r["injection"],
            wall_T=float(r["wall_T"]) * k,
            inlet_T=float(r["inlet_T"]) * k,
            flow=float(r["flow"]) / 3600 * (1.0 if si else LBM_TO_KG),
            p_final=float(r["p_final"]) * (1e3 if si else PSI_TO_PA),
            fill=float(r["fill_final_pct"]) / 100,
        ))
    return rows


def predict(test: dict, fluid_name: str = "ParaHydrogen",
            p0: float = P0_BASE, include_leak: bool = True) -> dict:
    """Equilibrium pressure at the measured final fill for one test."""
    f = Fluid(fluid_name)
    tk = TANKS[test["source"]]
    tank = Tank(tk["volume"], tk["wall"], "Al6061")
    Tw = test["wall_T"]
    # initial ullage must be vapour at the wall temperature
    if Tw < f.T_crit:
        p0 = min(p0, 0.9 * f.p_sat(Tw))
    s0 = initial_state(f, tank, Tw, p0)
    # a failed run (fill 0) is evaluated at its 95 % target
    target = test["fill"] if test["fill"] > 0 else 0.95
    h_in = f.sat_liquid(f.p_sat(test["inlet_T"]))["h"]
    m_load = target * f.rho_sat_liq_T(test["inlet_T"]) * tank.volume
    t_fill = m_load / test["flow"]
    Q = tk["q_leak"] * t_fill if include_leak else 0.0
    s0 = TankState(s0.m_fluid, s0.U_total + Q, s0.T, s0.p)
    r = P.no_vent_fill(f, tank, s0, h_in, 1e9, target)
    return dict(p_model=r["p_at_target"], T_model=r["state"].T,
                t_fill=t_fill, Q_leak=Q,
                p_sat_inlet=f.p_sat(test["inlet_T"]))


def main():
    tests = load_tests()
    out = []
    for t in tests:
        pr = predict(t)
        pn = predict(t, fluid_name="Hydrogen")["p_model"]
        failed = t["fill"] <= 0
        err = np.nan if failed else 100 * (pr["p_model"] - t["p_final"]) / t["p_final"]
        out.append(dict(**t, **pr, p_model_normal=pn, err_pct=err,
                        failed=failed))

    # sensitivity to assumed initial ullage pressure and inlet T (+-0.5 K)
    sens = []
    for t in tests:
        if t["fill"] <= 0:
            continue
        p_lo = predict(t, p0=1e3)["p_model"]
        p_hi = predict(t, p0=50e3)["p_model"]
        tp = dict(t, inlet_T=t["inlet_T"] + 0.5)
        tm = dict(t, inlet_T=t["inlet_T"] - 0.5)
        sens.append(dict(test=t["test"], p_p0_1kPa=p_lo, p_p0_50kPa=p_hi,
                         p_inlet_plus=predict(tp)["p_model"],
                         p_inlet_minus=predict(tm)["p_model"]))

    RES.mkdir(exist_ok=True)
    with open(RES / "validation_nvf.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["source", "test", "injection", "wall_T_K", "inlet_T_K",
                    "flow_kg_s", "fill", "p_test_kPa", "p_model_kPa",
                    "p_model_normalH2_kPa", "p_sat_inlet_kPa", "err_pct",
                    "T_model_K", "t_fill_s", "failed"])
        for o in out:
            w.writerow([o["source"], o["test"], o["injection"],
                        round(o["wall_T"], 2), round(o["inlet_T"], 2),
                        round(o["flow"], 4), o["fill"],
                        round(o["p_final"] / 1e3, 1),
                        round(o["p_model"] / 1e3, 1),
                        round(o["p_model_normal"] / 1e3, 1),
                        round(o["p_sat_inlet"] / 1e3, 1),
                        round(o["err_pct"], 1), round(o["T_model"], 3),
                        round(o["t_fill"]), o["failed"]])
    with open(RES / "validation_nvf_sensitivity.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["test", "p_p0_1kPa", "p_p0_50kPa", "p_inlet_plus0.5K",
                    "p_inlet_minus0.5K"])
        for s in sens:
            w.writerow([s["test"]] + [round(s[k] / 1e3, 1) for k in
                                      ("p_p0_1kPa", "p_p0_50kPa",
                                       "p_inlet_plus", "p_inlet_minus")])

    # summary statistics
    ok = [o for o in out if not o["failed"]]
    summary = {}
    for src in ("A", "B", "all"):
        e = np.array([o["err_pct"] for o in ok if src in ("all", o["source"])])
        de = np.array([(o["p_model"] - o["p_final"]) / 1e3 for o in ok
                       if src in ("all", o["source"])])
        summary[src] = dict(n=len(e), mean_err=e.mean(),
                            mean_abs_err=np.abs(e).mean(),
                            max_abs_err=np.abs(e).max(),
                            mean_abs_kPa=np.abs(de).mean())
    with open(RES / "validation_nvf_summary.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["set", "n", "mean_err_pct", "mean_abs_err_pct",
                    "max_abs_err_pct", "mean_abs_err_kPa"])
        for k, v in summary.items():
            w.writerow([k, v["n"], round(v["mean_err"], 1),
                        round(v["mean_abs_err"], 1),
                        round(v["max_abs_err"], 1),
                        round(v["mean_abs_kPa"], 1)])

    # figure 5: parity plot
    plt.rcParams.update({"font.size": 10, "axes.grid": True,
                         "grid.alpha": 0.3, "figure.dpi": 150,
                         "savefig.bbox": "tight"})
    fig, axs = plt.subplots(1, 2, figsize=(11.5, 4.4),
                            layout="constrained")
    ax = axs[0]
    mk = {"A": "o", "B": "s"}
    for src, tk in TANKS.items():
        sel = [o for o in ok if o["source"] == src]
        sc = ax.scatter([o["p_final"] / 1e3 for o in sel],
                        [o["p_model"] / 1e3 for o in sel],
                        c=[o["wall_T"] for o in sel], cmap="viridis",
                        vmin=15, vmax=130, marker=mk[src], edgecolor="k",
                        label=tk["label"])
    lim = [0, 300]
    ax.plot(lim, lim, "k-", lw=1)
    ax.fill_between(lim, [0.8 * x for x in lim], [1.2 * x for x in lim],
                    color="grey", alpha=0.15, label="$\\pm$20 %")
    ax.set_xlim(lim)
    ax.set_ylim(lim)
    ax.set_xlabel("Measured final pressure [kPa]")
    ax.set_ylabel("Equilibrium model pressure [kPa]")
    ax.set_title("No-vent fill, LH2: model vs NASA tests")
    ax.legend(fontsize=7, loc="upper left")
    fig.colorbar(sc, ax=ax, label="Initial wall temperature [K]")

    ax = axs[1]
    for src, tk in TANKS.items():
        sel = [o for o in ok if o["source"] == src]
        sc2 = ax.scatter([o["wall_T"] for o in sel],
                         [o["err_pct"] for o in sel], c=[o["inlet_T"] for o in sel],
                         cmap="coolwarm", vmin=17, vmax=23.5, marker=mk[src],
                         edgecolor="k", label=tk["label"])
    ax.axhline(0, color="k", lw=1)
    ax.set_xlabel("Initial wall temperature [K]")
    ax.set_ylabel("Model minus test [% of measured pressure]")
    ax.set_title("Error vs initial wall temperature")
    ax.legend(fontsize=7)
    fig.colorbar(sc2, ax=ax, label="Inlet liquid temperature [K]")
    fig.savefig(FIG / "fig5_validation_nvf.png")
    plt.close(fig)

    for k, v in summary.items():
        print(k, {kk: round(vv, 1) for kk, vv in v.items()})
    for o in out:
        print(f"{o['source']} {o['test']:>7} Tw={o['wall_T']:6.1f} "
              f"Tin={o['inlet_T']:5.2f} fill={o['fill']:.2f} "
              f"p_test={o['p_final']/1e3:6.1f} p_mod={o['p_model']/1e3:6.1f} "
              f"psat_in={o['p_sat_inlet']/1e3:6.1f} err={o['err_pct']:6.1f}%")
    return out, summary, sens


if __name__ == "__main__":
    main()
