"""Basic physics and consistency tests. Run: python -m pytest -q"""

import numpy as np
import pytest

from cryotransfer import materials
from cryotransfer import processes as P
from cryotransfer.thermo import Fluid, Tank, initial_state, solve_equilibrium


# --- materials --------------------------------------------------------------

@pytest.mark.parametrize("mat,T,expected,tol", [
    ("Al6061", 300, 900, 0.08),   # handbook ~ 896 J/kgK
    ("SS304", 300, 477, 0.05),    # handbook ~ 477 J/kgK
    ("SS304", 77, 200, 0.10),
])
def test_cp_reference_values(mat, T, expected, tol):
    assert float(materials.cp(mat, T)) == pytest.approx(expected, rel=tol)


def test_enthalpy_monotonic_and_invertible():
    T = np.linspace(10, 390, 50)
    for mat in ("Al6061", "SS304"):
        H = materials.enthalpy(mat, T)
        assert np.all(np.diff(H) > 0)
        assert np.allclose(materials.temperature_from_enthalpy(mat, H), T,
                           atol=0.05)


def test_material_bad_inputs():
    with pytest.raises(ValueError):
        materials.cp("Copper", 100)
    with pytest.raises(ValueError):
        materials.cp("Al6061", 500)


# --- equilibrium ------------------------------------------------------------

@pytest.mark.parametrize("name", ["Oxygen", "Methane", "Hydrogen"])
def test_initial_state_roundtrip(name):
    f = Fluid(name)
    t = Tank(1.0, 40.0)
    s0 = initial_state(f, t, 280.0, 100e3)
    s1 = solve_equilibrium(f, t, s0.m_fluid, s0.U_total)
    assert s1.T == pytest.approx(280.0, abs=1e-3)
    assert s1.p == pytest.approx(100e3, rel=1e-4)


def test_charge_conserves_energy():
    f = Fluid("Oxygen")
    t = Tank(1.0, 40.0)
    h_in = f.inlet_enthalpy(400e3, 5.0)
    s0 = initial_state(f, t, 290.0, 50e3)
    s1, dm = P.charge_to_pressure(f, t, s0, h_in, 345e3)
    assert s1.p == pytest.approx(345e3, rel=1e-6)
    assert s1.m_fluid == pytest.approx(s0.m_fluid + dm)
    assert s1.U_total == pytest.approx(s0.U_total + dm * h_in)


def test_vent_lowers_pressure_and_mass():
    f = Fluid("Methane")
    t = Tank(1.0, 40.0)
    h_in = f.inlet_enthalpy(400e3, 5.0)
    s0 = initial_state(f, t, 290.0, 50e3)
    s1, _ = P.charge_to_pressure(f, t, s0, h_in, 345e3)
    s2, dv = P.vent_to_pressure(f, t, s1, 50e3)
    assert s2.p == pytest.approx(50e3, rel=1e-5)
    assert 0 < dv < s1.m_fluid
    assert s2.T < s1.T          # venting cools the tank


# --- processes --------------------------------------------------------------

@pytest.mark.parametrize("name", ["Oxygen", "Methane"])
def test_line_chilldown_bounds(name):
    f = Fluid(name)
    h_in = f.inlet_enthalpy(400e3, 5.0)
    mw = P.tube_wall_mass(3.0, 0.0127, 0.00089, 8000)
    r = P.wall_chilldown_mass(f, "SS304", mw, 290, f.T_sat(150e3) + 5,
                              150e3, h_in)
    assert 0 < r["m_best"] < r["m_worst"]
    # worst case is an exact energy balance
    h_g = f.sat_vapour(150e3)["h"]
    assert r["m_worst"] * (h_g - h_in) == pytest.approx(r["dH_wall"])


def test_colder_wall_lowers_fill_pressure():
    f = Fluid("Oxygen")
    t = Tank(1.0, 40.0)
    h_in = f.inlet_enthalpy(400e3, 5.0)
    p = []
    for T0 in (290, 200, 120):
        s0 = initial_state(f, t, T0, 50e3)
        p.append(P.no_vent_fill(f, t, s0, h_in, 2e6, 0.95)["p_at_target"])
    assert p[0] > p[1] > p[2]


def test_zero_wall_mass_tank():
    f = Fluid("Oxygen")
    t = Tank(1.0, 0.0)
    h_in = f.inlet_enthalpy(400e3, 5.0)
    s0 = initial_state(f, t, 290.0, 50e3)
    r = P.no_vent_fill(f, t, s0, h_in, 345e3, 0.95)
    assert r["success"]


def test_bad_pressure_rejected():
    f = Fluid("Oxygen")
    with pytest.raises(ValueError):
        f.T_sat(10e6)
