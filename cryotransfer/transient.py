"""v2: transient chilldown of a transfer line (1D wall nodes).

Model
-----
The tube is split into N axial wall nodes. Each node is lumped radially
(thin wall, Biot number well below 0.1) and the outer surface is adiabatic
(vacuum jacket or MLI). Axial conduction in the wall is neglected.

Fluid flows at constant mass flow and constant pressure (no pressure drop,
no flashing). At each time step the fluid is marched quasi-steadily from
inlet to outlet: node i passes heat Q_i to the fluid, so

    h_{i+1} = h_i + Q_i / mdot,
    m_i cp(T_i) dT_i/dt = -Q_i,   Q_i = q''_i * pi * D_i * dz.

Heat flux q'' follows a boiling curve built from the correlation set of
Darr and Hartwig (2019), "Two-Phase Convection Heat Transfer Correlations
for Liquid Hydrogen Pipe Chilldown", NTRS 20190029114, Table 1:

* film boiling (T_w > T_wet): dispersed-flow form
      Nu_FB = 0.015 Re_tp^0.8774 Pr_v^0.6112,  q = Nu k_v (T_w - T_sat)/D.
  Here Re_tp = (G D / mu_v) [x + (rho_v/rho_l)(1 - x)], the Dougall and
  Rohsenow two-phase Reynolds number, with x the equilibrium quality
  clipped to [0, 1]. That definition is OUR assumption; the paper's exact
  definition (it uses a non-equilibrium actual quality) was not readable. A multiplier C_fb (default
  1) is exposed so the film-boiling level can be tested against data.
  The inverted-annular term of the paper is omitted.
* rewet temperature: T_wet = 0.844 T_crit (1 + 0.060 We^0.208),
  We = G^2 D / (rho_l sigma).
* nucleate boiling (T_w <= T_DNB = T_sat + 2 K):
      h_NB = 61.6 Re_l^-0.332 Ja^-0.254 h_DB,
      h_DB = 0.023 Re_l^0.8 Pr_l^0.4 k_l / D,  Ja = cp_l (T_w - T_sat)/h_fg.
* transition boiling: linear in T_w between q_NB(T_DNB) and q_FB(T_wet).
* single-phase liquid (subcooled, T_w below T_sat) or vapour (x_e >= 1):
  Dittus-Boelter.

These correlations were fitted to LH2 (and LN2 for T_wet). Using them for
LOX and LCH4 is an extrapolation; see VALIDATION.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import CoolProp.CoolProp as CP
import numpy as np

from . import materials
from .thermo import Fluid


@dataclass
class Line:
    """Straight transfer line."""
    length: float        # m
    od: float            # m
    wall: float          # m
    material: str = "SS304"
    density: float = 7900.0

    def __post_init__(self):
        if min(self.length, self.od, self.wall, self.density) <= 0:
            raise ValueError("Line dimensions must be positive")
        if self.wall >= self.od / 2:
            raise ValueError("Wall thicker than radius")
        materials._check_material(self.material)

    @property
    def id(self) -> float:
        return self.od - 2 * self.wall

    @property
    def flow_area(self) -> float:
        return np.pi / 4 * self.id**2

    @property
    def mass(self) -> float:
        return np.pi / 4 * (self.od**2 - self.id**2) * self.length * self.density


@dataclass
class ChilldownResult:
    t_chill: float            # s, time to reach end criterion (nan if not)
    m_used: float             # kg, mdot * t_chill
    completed: bool
    time: np.ndarray = field(repr=False, default=None)
    wall_T: np.ndarray = field(repr=False, default=None)   # (nt, N)
    exit_h: np.ndarray = field(repr=False, default=None)
    T_wet: float = np.nan
    regime_time: dict = field(default_factory=dict)


class _SatProps:
    """Saturation and vapour properties at fixed pressure."""

    def __init__(self, fluid: Fluid, p: float):
        n = fluid.name
        self.p = p
        self.T_sat = fluid.T_sat(p)
        q0 = lambda k: CP.PropsSI(k, "P", p, "Q", 0, n)   # noqa: E731
        q1 = lambda k: CP.PropsSI(k, "P", p, "Q", 1, n)   # noqa: E731
        self.h_l, self.h_v = q0("H"), q1("H")
        self.h_fg = self.h_v - self.h_l
        self.rho_l, self.rho_v = q0("D"), q1("D")
        self.mu_l, self.mu_v = q0("V"), q1("V")
        self.k_l, self.k_v = q0("L"), q1("L")
        self.cp_l, self.cp_v = q0("C"), q1("C")
        self.Pr_l = self.cp_l * self.mu_l / self.k_l
        self.Pr_v = self.cp_v * self.mu_v / self.k_v
        self.sigma = q0("I")
        self.T_crit = fluid.T_crit
        # superheated vapour table, T_sat+0.2 .. 420 K
        self.Tg = np.linspace(self.T_sat + 0.2, 420.0, 300)
        self.hg = np.array([CP.PropsSI("H", "P", p, "T", T, n)
                            for T in self.Tg])
        self.mug = np.array([CP.PropsSI("V", "P", p, "T", T, n)
                             for T in self.Tg])
        self.kg = np.array([CP.PropsSI("L", "P", p, "T", T, n)
                            for T in self.Tg])
        self.cpg = np.array([CP.PropsSI("C", "P", p, "T", T, n)
                             for T in self.Tg])

    def vapour_T(self, h):
        return np.interp(h, self.hg, self.Tg)


def rewet_temperature(sp: _SatProps, G: float, D: float) -> float:
    """Darr and Hartwig (2019) Eq. 18 form, T_wet in K."""
    We = G**2 * D / (sp.rho_l * sp.sigma)
    return 0.844 * sp.T_crit * (1 + 0.060 * We**0.208)


def heat_flux(Tw, h, sp: _SatProps, G: float, D: float, T_wet: float,
              C_fb: float = 1.0):
    """Wall-to-fluid heat flux [W/m2] and regime code for one node.

    Regime codes: 0 single-phase liquid, 1 nucleate, 2 transition,
    3 film, 4 single-phase vapour, 5 wall colder than fluid (no flux).
    """
    x = (h - sp.h_l) / sp.h_fg
    if x >= 1.0:                                   # superheated vapour
        Tf = sp.vapour_T(h)
        if Tw <= Tf:
            return 0.0, 5
        mu = np.interp(Tf, sp.Tg, sp.mug)
        k = np.interp(Tf, sp.Tg, sp.kg)
        cp = np.interp(Tf, sp.Tg, sp.cpg)
        Re = G * D / mu
        Nu = 0.023 * Re**0.8 * (cp * mu / k)**0.4
        return Nu * k / D * (Tw - Tf), 4
    dT = Tw - sp.T_sat
    Re_l = G * D / sp.mu_l
    h_DB = 0.023 * Re_l**0.8 * sp.Pr_l**0.4 * sp.k_l / D
    if dT <= 0.0:
        if x < 0:                                  # subcooled liquid
            T_liq = sp.T_sat + x * sp.h_fg / sp.cp_l
            return (h_DB * (Tw - T_liq), 0) if Tw > T_liq else (0.0, 5)
        return 0.0, 5

    def q_nb(dt):
        Ja = sp.cp_l * dt / sp.h_fg
        return 61.6 * Re_l**-0.332 * Ja**-0.254 * h_DB * dt

    def q_fb(Tw_):
        xa = min(max(x, 0.0), 1.0)
        Re_tp = G * D / sp.mu_v * (xa + sp.rho_v / sp.rho_l * (1 - xa))
        Nu = 0.015 * Re_tp**0.8774 * sp.Pr_v**0.6112
        return C_fb * Nu * sp.k_v / D * (Tw_ - sp.T_sat)

    T_dnb = sp.T_sat + 2.0
    if Tw >= T_wet:
        return q_fb(Tw), 3
    if Tw <= T_dnb:
        return q_nb(dT), 1
    q1, q2 = q_nb(2.0), q_fb(T_wet)
    return q2 + (q1 - q2) * (Tw - T_wet) / (T_dnb - T_wet), 2


def chilldown(fluid: Fluid, line: Line, mdot: float, p: float, T0: float,
              subcooling_K: float = 0.0, n_nodes: int = 20,
              dT_end: float = 5.0, C_fb: float = 1.0, t_max: float = 3600.0,
              dT_step: float = 1.0, store_every: int = 1
              ) -> ChilldownResult:
    """Transient chilldown of `line` from uniform T0 with inlet flow mdot.

    Ends when every wall node is below T_sat(p) + dT_end. The time step is
    adaptive: no node may change by more than dT_step kelvin per step.
    """
    if mdot <= 0 or p <= 0 or n_nodes < 2:
        raise ValueError("mdot, p must be > 0 and n_nodes >= 2")
    sp = _SatProps(fluid, p)
    if T0 <= sp.T_sat + dT_end:
        raise ValueError("T0 already at or below the end criterion")
    if T0 > materials.T_MAX:
        raise ValueError("T0 above material model range")
    h_in = fluid.inlet_enthalpy(p, subcooling_K)
    D = line.id
    G = mdot / line.flow_area
    T_wet = rewet_temperature(sp, G, D)
    dz = line.length / n_nodes
    m_node = line.mass / n_nodes
    area = np.pi * D * dz
    Tw = np.full(n_nodes, float(T0))
    T_end = sp.T_sat + dT_end

    t = 0.0
    times, walls, exits = [0.0], [Tw.copy()], [np.nan]
    regime_time = {k: 0.0 for k in range(6)}
    step = 0
    while Tw.max() > T_end:
        if t > t_max:
            return ChilldownResult(np.nan, np.nan, False, np.array(times),
                                   np.array(walls), np.array(exits), T_wet,
                                   regime_time)
        h = h_in
        Q = np.empty(n_nodes)
        reg = np.empty(n_nodes, dtype=int)
        for i in range(n_nodes):
            q, reg[i] = heat_flux(Tw[i], h, sp, G, D, T_wet, C_fb)
            Q[i] = q * area
            # second-law cap: the fluid cannot leave a node hotter than
            # the wall, so Q is limited to heating it to T_w
            if Tw[i] > sp.Tg[0]:
                h_cap = float(np.interp(Tw[i], sp.Tg, sp.hg))
                Q[i] = min(Q[i], max(mdot * (h_cap - h), 0.0))
            h = h + Q[i] / mdot
            if h > sp.hg[-1]:
                raise RuntimeError("Fluid enthalpy beyond property table")
        cp = materials.cp(line.material, Tw)
        rate = Q / (m_node * cp)                     # K/s cooling rate
        dt = dT_step / max(rate.max(), 1e-9)
        dt = min(dt, 1.0)
        Tw = Tw - rate * dt
        Tw = np.maximum(Tw, sp.T_sat - subcooling_K)
        t += dt
        for r in reg:
            regime_time[int(r)] += dt / n_nodes
        step += 1
        if step % store_every == 0:
            times.append(t)
            walls.append(Tw.copy())
            exits.append(h)
    times.append(t)
    walls.append(Tw.copy())
    exits.append(h)
    return ChilldownResult(t, mdot * t, True, np.array(times),
                           np.array(walls), np.array(exits), T_wet,
                           regime_time)
