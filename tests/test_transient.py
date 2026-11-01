"""Tests for the v2 transient line chilldown model."""

import numpy as np
import pytest

from cryotransfer import materials
from cryotransfer import processes as P
from cryotransfer.thermo import Fluid
from cryotransfer.transient import Line, chilldown

LINE = Line(0.914, 0.0127, 0.00051)
N2 = Fluid("Nitrogen")


@pytest.fixture(scope="module")
def run():
    return chilldown(N2, LINE, 0.05, 550e3, 290.0, C_fb=2.4, n_nodes=15)


def test_line_geometry():
    assert LINE.id == pytest.approx(0.01168)
    assert LINE.mass == pytest.approx(
        P.tube_wall_mass(0.914, 0.0127, 0.00051, 7900.0))
    with pytest.raises(ValueError):
        Line(1.0, 0.01, 0.006)


def test_completes_and_cools_monotonically(run):
    assert run.completed
    Tmax = run.wall_T.max(axis=1)
    assert np.all(np.diff(Tmax) <= 1e-9)
    assert Tmax[-1] <= N2.T_sat(550e3) + 5.0


def test_energy_conserved(run):
    """Heat removed from the wall equals enthalpy gained by the fluid."""
    h_in = N2.inlet_enthalpy(550e3, 0.0)
    dt = np.diff(run.time)
    gain = np.sum(0.05 * (run.exit_h[1:] - h_in) * dt)
    m_node = LINE.mass / run.wall_T.shape[1]
    loss = m_node * np.sum(materials.enthalpy("SS304", run.wall_T[0])
                           - materials.enthalpy("SS304", run.wall_T[-1]))
    assert gain == pytest.approx(loss, rel=0.02)


def test_never_beats_thermodynamic_minimum(run):
    h_in = N2.inlet_enthalpy(550e3, 0.0)
    b = P.wall_chilldown_mass(N2, "SS304", LINE.mass, 290.0,
                              N2.T_sat(550e3) + 5.0, 550e3, h_in)
    assert run.m_used > b["m_best"]


def test_more_flow_is_faster_but_uses_more(run):
    r2 = chilldown(N2, LINE, 0.1, 550e3, 290.0, C_fb=2.4, n_nodes=15)
    assert r2.t_chill < run.t_chill
    assert r2.m_used > run.m_used


def test_mesh_convergence():
    a = chilldown(N2, LINE, 0.05, 550e3, 290.0, C_fb=2.4, n_nodes=10)
    b = chilldown(N2, LINE, 0.05, 550e3, 290.0, C_fb=2.4, n_nodes=30)
    assert a.t_chill == pytest.approx(b.t_chill, rel=0.10)


def test_bad_inputs():
    with pytest.raises(ValueError):
        chilldown(N2, LINE, 0.0, 550e3, 290.0)
    with pytest.raises(ValueError):
        chilldown(N2, LINE, 0.05, 550e3, 90.0)
