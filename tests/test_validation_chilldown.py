"""Tests for the line chilldown validation (scripts/validate_chilldown.py)."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate_chilldown as V  # noqa: E402


@pytest.fixture(scope="module")
def tests():
    return V.load_tests()


def test_table_loaded(tests):
    assert len(tests) == 28
    t = {r["test"]: r for r in tests}
    assert t["F1"]["m_meas"] == pytest.approx(1.08)
    assert t["F27"]["coating"] == "4L"
    assert t["F3"]["pulse"] and not t["F1"]["pulse"]


def test_tube_mass_hand_calc():
    # pi/4 (OD^2 - ID^2) L rho with OD 12.7 mm, wall 0.51 mm, L 0.914 m
    assert V.tube_mass() == pytest.approx(0.141, rel=0.01)


def test_no_test_beats_thermodynamic_limit(tests):
    """Second-law style sanity check: no measured chilldown can use less
    propellant than the best-case energy bound."""
    cache = {}
    for t in tests:
        if t["p_in"] not in cache:
            cache[t["p_in"]] = V.bounds(t["p_in"])["m_best"]
        assert t["m_meas"] > cache[t["p_in"]]


def test_warmer_start_needs_more(tests):
    b250 = V.bounds(550e3, T0=250.0)["m_best"]
    b300 = V.bounds(550e3, T0=300.0)["m_best"]
    assert b300 > b250
