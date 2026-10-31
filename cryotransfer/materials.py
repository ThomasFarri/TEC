"""Temperature-dependent specific heat of tank and line wall materials.

Source: NIST Cryogenic Material Properties database,
https://trc.nist.gov/cryogenics/materials/materialproperties.htm
Fit form: log10(cp) = sum_{i=0}^{8} c_i * (log10 T)^i, cp in J/(kg K).
Valid roughly 4 K to 300 K. Above 300 K the value is held at cp(300 K),
which is a small, conservative-ish approximation for starting temperatures
up to about 350 K.
"""

from __future__ import annotations

import numpy as np

# NIST coefficients, a..i
_COEFFS = {
    "Al6061": [46.6467, -314.292, 866.662, -1298.3, 1162.27,
               -637.795, 210.351, -38.3094, 2.96344],
    "SS304": [22.0061, -127.5528, 303.647, -381.0098, 274.0328,
              -112.9212, 24.7593, -2.239153, 0.0],
}

T_MIN = 4.0
T_MAX_FIT = 300.0
T_MAX = 400.0


def _check_material(material: str) -> None:
    if material not in _COEFFS:
        raise ValueError(
            f"Unknown material '{material}'. Options: {sorted(_COEFFS)}")


def cp(material: str, T):
    """Specific heat [J/(kg K)] at temperature T [K] (scalar or array)."""
    _check_material(material)
    T = np.asarray(T, dtype=float)
    if np.any(T < T_MIN) or np.any(T > T_MAX):
        raise ValueError(f"T must be within [{T_MIN}, {T_MAX}] K, got {T}")
    Tc = np.minimum(T, T_MAX_FIT)
    x = np.log10(Tc)
    y = np.zeros_like(x)
    for i, c in enumerate(_COEFFS[material]):
        y = y + c * x**i
    return 10.0**y


# Pre-tabulated enthalpy for fast lookup, H(T) = integral cp dT from T_MIN.
_TGRID = np.linspace(T_MIN, T_MAX, 4000)
_HTAB = {}
for _m in _COEFFS:
    _cpg = cp(_m, _TGRID)
    _HTAB[_m] = np.concatenate(
        [[0.0], np.cumsum(0.5 * (_cpg[1:] + _cpg[:-1]) * np.diff(_TGRID))])


def enthalpy(material: str, T):
    """Specific enthalpy [J/kg] relative to 4 K."""
    _check_material(material)
    T = np.asarray(T, dtype=float)
    if np.any(T < T_MIN) or np.any(T > T_MAX):
        raise ValueError(f"T must be within [{T_MIN}, {T_MAX}] K")
    return np.interp(T, _TGRID, _HTAB[material])


def temperature_from_enthalpy(material: str, H):
    """Inverse of enthalpy(): temperature [K] for specific enthalpy H [J/kg]."""
    _check_material(material)
    H = np.asarray(H, dtype=float)
    tab = _HTAB[material]
    if np.any(H < tab[0] - 1e-9) or np.any(H > tab[-1] + 1e-9):
        raise ValueError("Enthalpy outside tabulated range")
    return np.interp(H, tab, _TGRID)
