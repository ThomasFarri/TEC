"""Transfer processes: line chilldown, charge-hold-vent, flow-through
chilldown and no-vent fill.

Energy accounting for a rigid open tank with equilibrium fluid + wall:
    dU_total = h_in * dm_in - h_out * dm_out
No heat leak from the environment in v1 (fast operation assumption).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq

from . import materials
from .thermo import Fluid, Tank, TankState, solve_equilibrium

# ---------------------------------------------------------------------------
# Line / wall chilldown with continuous venting
# ---------------------------------------------------------------------------


def wall_chilldown_mass(fluid: Fluid, material: str, wall_mass: float,
                        T0: float, T_end: float, p_vent: float,
                        h_in: float) -> dict:
    """Propellant needed to cool a wall from T0 to T_end by flow-through.

    Two bounds on the vented fluid enthalpy:
      'worst': fluid leaves as saturated vapour at p_vent (least heat
               absorbed per kg, so most propellant used). Also covers
               liquid carry-over being ignored, so it is not a strict
               upper bound if liquid is vented.
      'best' : fluid leaves superheated to the local wall temperature
               (maximum heat pickup per kg).
    """
    if T_end >= T0:
        raise ValueError("T_end must be below T0")
    T_sat = fluid.T_sat(p_vent)
    if T_end <= T_sat:
        raise ValueError(
            f"T_end ({T_end:.1f} K) must exceed T_sat at vent pressure "
            f"({T_sat:.1f} K) for flow-through cooling")
    dH_wall = wall_mass * float(materials.enthalpy(material, T0)
                                - materials.enthalpy(material, T_end))
    h_g = fluid.sat_vapour(p_vent)["h"]
    if h_g <= h_in:
        raise ValueError("Inlet enthalpy above saturated vapour enthalpy")
    m_worst = dH_wall / (h_g - h_in)

    def integrand(T):
        return (wall_mass * float(materials.cp(material, T))
                / (fluid.h_PT(p_vent, T) - h_in))

    m_best, _ = quad(integrand, T_end, T0, limit=200)
    return dict(m_best=m_best, m_worst=m_worst, dH_wall=dH_wall)


def tube_wall_mass(length: float, od: float, wall: float,
                   density: float) -> float:
    """Mass of a straight tube [kg]."""
    if min(length, od, wall, density) <= 0 or wall >= od / 2:
        raise ValueError("Invalid tube geometry")
    return np.pi / 4 * (od**2 - (od - 2 * wall)**2) * length * density


# ---------------------------------------------------------------------------
# Closed-tank steps
# ---------------------------------------------------------------------------


def charge_to_pressure(fluid: Fluid, tank: Tank, state: TankState,
                       h_in: float, p_max: float) -> tuple[TankState, float]:
    """Add inlet fluid until equilibrium pressure reaches p_max.

    Returns (new state, mass added). If p_max is reached with zero mass
    added, returns the input state.
    """
    if state.p >= p_max:
        return state, 0.0

    def p_after(dm):
        s = solve_equilibrium(fluid, tank, state.m_fluid + dm,
                              state.U_total + dm * h_in)
        return s.p - p_max

    # bracket: grow the upper bound until pressure is exceeded
    rho_l_max = fluid.rho_sat_liq_T(fluid.T_triple + 1)
    dm_hi = max(1e-3, 0.01 * rho_l_max * tank.volume)
    m_cap = 1.2 * rho_l_max * tank.volume
    while p_after(dm_hi) < 0:
        dm_hi *= 2
        if state.m_fluid + dm_hi > m_cap:
            raise RuntimeError("Could not reach p_max: tank liquid-full")
    dm = brentq(p_after, 0.0, dm_hi, xtol=1e-7, rtol=1e-9, maxiter=200)
    s = solve_equilibrium(fluid, tank, state.m_fluid + dm,
                          state.U_total + dm * h_in)
    return s, dm


def vent_to_pressure(fluid: Fluid, tank: Tank, state: TankState,
                     p_vent: float, n_steps: int = 200
                     ) -> tuple[TankState, float]:
    """Quasi-static vent of vapour until equilibrium pressure falls to p_vent.

    Vented enthalpy is saturated vapour if two-phase, otherwise the bulk
    gas enthalpy. Venting liquid (possible in microgravity) is NOT modelled
    and would make losses larger.
    """
    if p_vent <= fluid.p_triple * 1.05:
        raise ValueError("p_vent too close to triple point (freezing risk)")
    if state.p <= p_vent:
        return state, 0.0
    m0 = state.m_fluid
    s = state
    vented = 0.0
    # step on mass fraction, refine as we approach p_vent
    dm_base = m0 / n_steps
    for _ in range(50 * n_steps):
        rho = s.m_fluid / tank.volume
        q = fluid.quality_DT(rho, s.T)
        h_out = (fluid.h_sat_vap_T(s.T) if 0.0 <= q <= 1.0
                 else fluid.h_DT(rho, s.T))
        dm = min(dm_base, 0.5 * s.m_fluid)
        trial = solve_equilibrium(fluid, tank, s.m_fluid - dm,
                                  s.U_total - dm * h_out)
        if trial.p < p_vent:
            # bisect the final partial step
            def f(d):
                return solve_equilibrium(fluid, tank, s.m_fluid - d,
                                         s.U_total - d * h_out).p - p_vent
            d = brentq(f, 0.0, dm, xtol=1e-9)
            s = solve_equilibrium(fluid, tank, s.m_fluid - d,
                                  s.U_total - d * h_out)
            vented += d
            return s, vented
        s = trial
        vented += dm
    raise RuntimeError("Vent did not converge")


def no_vent_fill(fluid: Fluid, tank: Tank, state: TankState, h_in: float,
                 p_max: float, target_fill: float = 0.95) -> dict:
    """No-vent fill toward `target_fill` (liquid volume fraction).

    The fill succeeds if the equilibrium pressure at target fill is at or
    below p_max. If not, the fill stops at p_max and the achieved fill is
    reported. Keys: success, fill, p_at_target, m_added, state.
    """
    if not (0 < target_fill < 1):
        raise ValueError("target_fill must be in (0, 1)")

    def state_after(dm):
        return solve_equilibrium(fluid, tank, state.m_fluid + dm,
                                 state.U_total + dm * h_in)

    def g(dm):
        return state_after(dm).fill_fraction(fluid, tank) - target_fill

    # upper bracket: liquid-full mass at a cold temperature
    rho_l = fluid.rho_sat_liq_T(fluid.T_triple + 2)   # densest liquid
    dm_hi = max(rho_l * tank.volume - state.m_fluid, 1e-6)
    p_at_target = np.nan
    try:
        if g(dm_hi) <= 0:
            raise RuntimeError
        dm_t = brentq(g, 0.0, dm_hi, xtol=1e-6, rtol=1e-9, maxiter=300)
        s_t = state_after(dm_t)
        p_at_target = s_t.p
    except (RuntimeError, ValueError):
        s_t = None

    if s_t is not None and s_t.p <= p_max:
        return dict(success=True, fill=target_fill, p_at_target=p_at_target,
                    m_added=dm_t, state=s_t)

    s, dm = charge_to_pressure(fluid, tank, state, h_in, p_max)
    return dict(success=False, fill=s.fill_fraction(fluid, tank),
                p_at_target=p_at_target, m_added=dm, state=s)


# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------


@dataclass
class CHVResult:
    cycles: int
    vented_mass: float
    charged_mass: float
    wall_T_history: list = field(default_factory=list)
    vented_history: list = field(default_factory=list)
    fill_if_stop_history: list = field(default_factory=list)
    final_fill: float = 0.0
    final_state: TankState | None = None
    reached_target: bool = False


def charge_hold_vent(fluid: Fluid, tank: Tank, state0: TankState,
                     h_in: float, p_charge: float, p_vent: float,
                     p_fill_max: float, target_fill: float,
                     max_cycles: int = 30) -> CHVResult:
    """Charge-hold-vent chilldown followed by a no-vent fill.

    After each cycle, check what a no-vent fill would achieve from the
    current state. Stop as soon as it reaches `target_fill`, so the result
    is the minimum number of cycles under this model.
    """
    if not (0 < target_fill < 1):
        raise ValueError("target_fill must be in (0, 1)")
    if p_vent >= p_charge:
        raise ValueError("p_vent must be below p_charge")
    res = CHVResult(0, 0.0, 0.0)
    s = state0
    for k in range(max_cycles + 1):
        fill = no_vent_fill(fluid, tank, s, h_in, p_fill_max, target_fill)
        res.wall_T_history.append(s.T)
        res.vented_history.append(res.vented_mass)
        res.fill_if_stop_history.append(fill["fill"])
        if fill["success"]:
            res.cycles = k
            res.final_fill = fill["fill"]
            res.final_state = fill["state"]
            res.reached_target = True
            return res
        if k == max_cycles:
            break
        s, dm_c = charge_to_pressure(fluid, tank, s, h_in, p_charge)
        res.charged_mass += dm_c
        s, dm_v = vent_to_pressure(fluid, tank, s, p_vent)
        res.vented_mass += dm_v
    res.cycles = max_cycles
    res.final_fill = res.fill_if_stop_history[-1]
    res.final_state = s
    return res


def flow_through_then_fill(fluid: Fluid, tank: Tank, T0: float,
                           T_end: float, h_in: float, p_vent: float,
                           p_fill_max: float,
                           target_fill: float = 0.95) -> dict:
    """Continuous flow-through chilldown of the tank wall to T_end, then
    a no-vent fill starting from vapour at (p_vent, T_end)."""
    from .thermo import initial_state
    chill = wall_chilldown_mass(fluid, tank.material, tank.wall_mass, T0,
                                T_end, p_vent, h_in)
    s0 = initial_state(fluid, tank, T_end, p_vent)
    fill = no_vent_fill(fluid, tank, s0, h_in, p_fill_max, target_fill)
    return dict(m_best=chill["m_best"], m_worst=chill["m_worst"],
                success=fill["success"], fill=fill["fill"],
                p_at_target=fill["p_at_target"], state=fill["state"])


def min_flow_through(fluid: Fluid, tank: Tank, T0: float, h_in: float,
                     p_vent: float, p_fill_max: float,
                     target_fill: float = 0.95) -> dict:
    """Warmest wall end-temperature that still allows a successful no-vent
    fill, and the flow-through propellant to reach it. Stopping chilldown
    early saves propellant, so this is the optimum for strategy B."""
    T_floor = fluid.T_sat(p_vent) + 0.5

    def ok(T_end):
        return flow_through_then_fill(fluid, tank, T0, T_end, h_in, p_vent,
                                      p_fill_max, target_fill)["success"]

    if not ok(T_floor):
        return dict(feasible=False)
    if ok(T0 - 0.5):
        return dict(feasible=True, T_end=T0, m_best=0.0, m_worst=0.0)
    lo, hi = T_floor, T0 - 0.5          # ok(lo) True, ok(hi) False
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if ok(mid):
            lo = mid
        else:
            hi = mid
        if hi - lo < 0.05:
            break
    r = flow_through_then_fill(fluid, tank, T0, lo, h_in, p_vent,
                               p_fill_max, target_fill)
    return dict(feasible=True, T_end=lo, m_best=r["m_best"],
                m_worst=r["m_worst"], p_at_target=r["p_at_target"])
