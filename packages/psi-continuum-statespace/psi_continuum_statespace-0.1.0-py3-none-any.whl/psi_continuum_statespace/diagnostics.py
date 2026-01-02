# psi_continuum_statespace/diagnostics.py

"""
Diagnostic utilities for the Psi–Continuum state-space framework.

This module provides quantitative measures of consistency between
different Psi(z) state-space trajectories.
"""

import numpy as np


def delta_psi(psi_a, psi_b, percent=True):
    """
    Difference between two Psi(z) trajectories.

    Parameters
    ----------
    psi_a, psi_b : array_like
        Psi(z) trajectories.
    percent : bool
        Return result in percent units.

    Returns
    -------
    delta : ndarray
        Psi_a - Psi_b
    """
    psi_a = np.asarray(psi_a, dtype=float)
    psi_b = np.asarray(psi_b, dtype=float)

    delta = psi_a - psi_b
    return 100.0 * delta if percent else delta


def abs_delta_psi(psi_a, psi_b, percent=True):
    """
    Absolute difference |Psi_a - Psi_b|.
    """
    return np.abs(delta_psi(psi_a, psi_b, percent=percent))


def integrated_distance(z, psi_a, psi_b):
    """
    Integrated state-space distance:

        D = ∫ |Psi_a(z) - Psi_b(z)| dz

    Parameters
    ----------
    z : array_like
        Redshift grid.
    psi_a, psi_b : array_like
        Psi(z) trajectories.

    Returns
    -------
    float
        Integrated distance.
    """
    z = np.asarray(z, dtype=float)
    dpsi = np.abs(np.asarray(psi_a) - np.asarray(psi_b))

    return np.trapezoid(dpsi, z)


def max_deviation(psi_a, psi_b, percent=True):
    """
    Maximum absolute deviation.
    """
    dpsi = abs_delta_psi(psi_a, psi_b, percent=percent)
    return float(np.max(dpsi))
