"""Fluid properties and closed-tank equilibrium solver.

All units SI: K, Pa, kg, m^3, J, J/kg.

Core assumption (v1): fluid and tank wall are in thermal equilibrium and
the fluid is homogeneous (no stratification). That makes this a best-case
bound: real tanks stratify and reach higher pressure for the same mass.
"""

from __future__ import annotations

from dataclasses import dataclass

import CoolProp.CoolProp as CP
from scipy.optimize import brentq

from . import materials

SUPPORTED_FLUIDS = ("Oxygen", "Methane", "Hydrogen", "Nitrogen")


class Fluid:
    """Thin wrapper around a CoolProp HEOS AbstractState."""

    def __init__(self, name: str):
        if name not in SUPPORTED_FLUIDS:
            raise ValueError(f"Fluid must be one of {SUPPORTED_FLUIDS}")
        self.name = name
        self._as = CP.AbstractState("HEOS", name)
        self.T_triple = self._as.Ttriple()
        self.T_crit = self._as.T_critical()
        self.p_triple = CP.PropsSI("P", "T", self.T_triple, "Q", 0, name)
        self.p_crit = self._as.p_critical()
        self.M = self._as.molar_mass()

    # --- state evaluations -------------------------------------------------
    def _update_DT(self, rho: float, T: float):
        if rho <= 0 or T <= 0:
            raise ValueError(f"Non-physical state rho={rho}, T={T}")
        self._as.update(CP.DmassT_INPUTS, rho, T)
        return self._as

    def u_DT(self, rho, T):
        return self._update_DT(rho, T).umass()

    def p_DT(self, rho, T):
        return self._update_DT(rho, T).p()

    def h_DT(self, rho, T):
        return self._update_DT(rho, T).hmass()

    def quality_DT(self, rho, T):
        """Vapour quality; -1 if single phase (CoolProp convention)."""
        return self._update_DT(rho, T).Q()

    def h_PT(self, p, T):
        self._as.update(CP.PT_INPUTS, p, T)
        return self._as.hmass()

    def T_sat(self, p):
        self._check_p(p)
        self._as.update(CP.PQ_INPUTS, p, 0.0)
        return self._as.T()

    def p_sat(self, T):
        self._as.update(CP.QT_INPUTS, 0.0, T)
        return self._as.p()

    def sat_liquid(self, p):
        self._check_p(p)
        self._as.update(CP.PQ_INPUTS, p, 0.0)
        return dict(T=self._as.T(), rho=self._as.rhomass(),
                    h=self._as.hmass(), u=self._as.umass())

    def sat_vapour(self, p):
        self._check_p(p)
        self._as.update(CP.PQ_INPUTS, p, 1.0)
        return dict(T=self._as.T(), rho=self._as.rhomass(),
                    h=self._as.hmass(), u=self._as.umass())

    def rho_sat_liq_T(self, T):
        self._as.update(CP.QT_INPUTS, 0.0, T)
        return self._as.rhomass()

    def rho_sat_vap_T(self, T):
        self._as.update(CP.QT_INPUTS, 1.0, T)
        return self._as.rhomass()

    def h_sat_vap_T(self, T):
        self._as.update(CP.QT_INPUTS, 1.0, T)
        return self._as.hmass()

    def _check_p(self, p):
        if not (self.p_triple < p < self.p_crit):
            raise ValueError(
                f"{self.name}: pressure {p:.0f} Pa outside "
                f"({self.p_triple:.0f}, {self.p_crit:.0f}) Pa")

    def inlet_enthalpy(self, p_supply: float, subcooling_K: float) -> float:
        """Enthalpy of supply liquid at p_supply, `subcooling_K` below T_sat."""
        if subcooling_K < 0:
            raise ValueError("subcooling_K must be >= 0")
        Ts = self.T_sat(p_supply)
        T = Ts - subcooling_K
        if T <= self.T_triple + 0.5:
            raise ValueError("Subcooling takes inlet below triple point")
        if subcooling_K < 1e-6:
            return self.sat_liquid(p_supply)["h"]
        return self.h_PT(p_supply, T)


@dataclass
class Tank:
    """Rigid receiver tank: internal volume and wall thermal mass."""
    volume: float          # m^3
    wall_mass: float       # kg
    material: str = "Al6061"

    def __post_init__(self):
        if self.volume <= 0 or self.wall_mass < 0:
            raise ValueError("Tank volume must be > 0 and wall mass >= 0")
        materials._check_material(self.material)


@dataclass
class TankState:
    """Equilibrium state of fluid + wall in a closed tank."""
    m_fluid: float   # kg
    U_total: float   # J, fluid internal energy + wall enthalpy
    T: float         # K, common temperature
    p: float         # Pa

    def fill_fraction(self, fluid: Fluid, tank: Tank) -> float:
        """Liquid volume / tank volume (0 if no liquid)."""
        rho = self.m_fluid / tank.volume
        if self.T >= fluid.T_crit:
            return 0.0
        rl = fluid.rho_sat_liq_T(self.T)
        rv = fluid.rho_sat_vap_T(self.T)
        if rho >= rl:
            return 1.0
        if rho <= rv:
            return 0.0
        # lever rule on specific volume
        x = (1 / rho - 1 / rl) / (1 / rv - 1 / rl)
        v_liq = self.m_fluid * (1 - x) / rl
        return v_liq / tank.volume


def solve_equilibrium(fluid: Fluid, tank: Tank, m_fluid: float,
                      U_total: float) -> TankState:
    """Common temperature T such that m*u(rho,T) + m_w*H_w(T) = U_total."""
    if m_fluid <= 0:
        raise ValueError("m_fluid must be > 0")
    rho = m_fluid / tank.volume
    T_lo = fluid.T_triple + 0.2
    T_hi = materials.T_MAX - 1.0

    def resid(T):
        return (m_fluid * fluid.u_DT(rho, T)
                + tank.wall_mass * float(materials.enthalpy(tank.material, T))
                - U_total)

    r_lo, r_hi = resid(T_lo), resid(T_hi)
    if r_lo > 0:
        raise RuntimeError("Equilibrium below triple point: fluid would freeze")
    if r_hi < 0:
        raise RuntimeError("Equilibrium above model range (400 K)")
    T = brentq(resid, T_lo, T_hi, xtol=1e-6, maxiter=200)
    return TankState(m_fluid, U_total, T, fluid.p_DT(rho, T))


def initial_state(fluid: Fluid, tank: Tank, T0: float, p0: float) -> TankState:
    """Warm tank holding residual gas at (p0, T0)."""
    fluid._as.update(CP.PT_INPUTS, p0, T0)
    rho = fluid._as.rhomass()
    u = fluid._as.umass()
    m = rho * tank.volume
    U = m * u + tank.wall_mass * float(materials.enthalpy(tank.material, T0))
    return TankState(m, U, T0, p0)
