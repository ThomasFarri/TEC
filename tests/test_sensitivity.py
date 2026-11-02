"""Tests for the sensitivity study driver (scripts/run_sensitivity.py)."""
import importlib.util
import math
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "run_sensitivity",
    Path(__file__).resolve().parents[1] / "scripts" / "run_sensitivity.py")
rs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rs)


def test_baseline_lox_small_loss():
    r = rs.run_case("Oxygen")
    assert 0.1 < r["chv_pct"] < 2.0
    assert r["ft_best_pct"] <= r["ft_worst_pct"]


def test_methane_costs_more_than_oxygen_at_baseline():
    assert rs.run_case("Methane")["ft_best_pct"] > \
        rs.run_case("Oxygen")["ft_best_pct"]


def test_flow_through_loss_rises_with_start_temperature():
    lo = rs.run_case("Methane", T0=250.0)["ft_worst_pct"]
    hi = rs.run_case("Methane", T0=320.0)["ft_worst_pct"]
    assert hi > lo


def test_more_subcooling_never_hurts():
    a = rs.run_case("Oxygen", subcool=5.0)["chv_pct"]
    b = rs.run_case("Oxygen", subcool=10.0)["chv_pct"]
    assert b <= a


def test_cold_tank_needs_no_chilldown():
    assert rs.run_case("Oxygen", T0=150.0)["chv_pct"] == 0.0


def test_ss_same_thickness_is_costlier_than_same_mass():
    same_mass = rs.run_case("Oxygen", material="SS304")["chv_pct"]
    same_thk = rs.run_case("Oxygen", material="SS304",
                           wall=40 * 8000 / 2700)["chv_pct"]
    assert same_thk > same_mass


def test_infeasible_inlet_gives_nan_not_crash():
    r = rs.run_case("Oxygen", subcool=500.0)
    assert math.isnan(r["chv_pct"])
