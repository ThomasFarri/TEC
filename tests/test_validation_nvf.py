"""Tests for the no-vent fill validation (scripts/validate_nvf.py)."""

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate_nvf as V  # noqa: E402


@pytest.fixture(scope="module")
def tests():
    return V.load_tests()


def test_table_loaded_and_converted(tests):
    assert len(tests) == 33
    t = {r["test"]: r for r in tests}
    # TM-106018 Fill 18 printed in SI
    assert t["Fill18"]["wall_T"] == pytest.approx(21.7)
    assert t["Fill18"]["p_final"] == pytest.approx(177e3)
    # TM-106293 test 291 printed in US units: 46.0 R, 5.7 psia, 1047 lbm/h
    assert t["291"]["wall_T"] == pytest.approx(46.0 / 1.8)
    assert t["291"]["p_final"] == pytest.approx(5.7 * 6894.757)
    assert t["291"]["flow"] == pytest.approx(1047 * 0.45359237 / 3600)


def test_tank_B_wall_mass_matches_stated_ratio():
    # TM-106293 states 3.41 lbm/ft3 for a 71 ft3 tank
    tk = V.TANKS["B"]
    ratio = tk["wall"] / V.LBM_TO_KG / (tk["volume"] / 0.0283168)
    assert ratio == pytest.approx(3.41, rel=0.01)


def test_cold_wall_prediction_near_inlet_saturation(tests):
    # with a cold wall the equilibrium pressure sits just above
    # p_sat(inlet T): the liquid barely warms
    t = {r["test"]: r for r in tests}["K2227"]
    r = V.predict(t)
    assert r["p_sat_inlet"] < r["p_model"] < 1.1 * r["p_sat_inlet"]


def test_warmer_wall_raises_predicted_pressure(tests):
    t = {r["test"]: r for r in tests}["Fill21"]
    p_cold = V.predict(dict(t, wall_T=30.0))["p_model"]
    p_warm = V.predict(t)["p_model"]
    assert p_warm > p_cold


def test_kSite_agreement_regression(tests):
    """Equilibrium model reproduces the 4.96 m3 tank final pressures
    within 10 % on average (Taylor and Chato report within about 17 kPa)."""
    errs = []
    for t in tests:
        if t["source"] == "A":
            p = V.predict(t)["p_model"]
            errs.append(abs(p - t["p_final"]) / t["p_final"])
    assert np.mean(errs) < 0.10
