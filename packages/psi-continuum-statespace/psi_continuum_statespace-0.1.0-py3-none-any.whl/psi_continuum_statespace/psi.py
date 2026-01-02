# psi_continuum_statespace/psi.py

"""
psi.py

State-space utilities for the Psi–Continuum framework.

This module defines the macroscopic state coordinate Psi(z),
constructed as a relative deformation of the reference ΛCDM
background expansion history.

The implementation is strictly diagnostic and does not modify
any cosmological dynamics or likelihoods.
"""

import numpy as np

from psi_continuum_v2.cosmology.background.lcdm import H_lcdm
from psi_continuum_v2.cosmology.background.psicdm import H_psicdm


def psi_from_H(H_model, H_ref):
    """
    Compute the state-space coordinate Psi from two Hubble functions.

    Parameters
    ----------
    H_model : array_like
        H(z) for the tested model.
    H_ref : array_like
        Reference H(z), typically ΛCDM.

    Returns
    -------
    Psi : ndarray
        Dimensionless state-space coordinate:
            Psi = H_model / H_ref - 1
    """
    H_model = np.asarray(H_model, dtype=float)
    H_ref = np.asarray(H_ref, dtype=float)

    if np.any(H_ref <= 0.0):
        raise ValueError("Reference H(z) must be positive.")

    return H_model / H_ref - 1.0


def psi_z(z, lcdm_params, psicdm_params):
    """
    Compute Psi(z) using the ΛCDM and ΨCDM background models from v2.

    Parameters
    ----------
    z : array_like
        Redshift values.
    lcdm_params : LCDMParams
        Parameters defining the reference ΛCDM background.
    psicdm_params : PsiCDMParams
        Parameters defining the ΨCDM background (including ε₀).

    Returns
    -------
    Psi : ndarray
        State-space coordinate Psi(z).
    """
    z = np.asarray(z, dtype=float)

    H_ref = H_lcdm(z, lcdm_params)
    H_mod = H_psicdm(z, psicdm_params)

    return psi_from_H(H_mod, H_ref)


def dpsi_dz(z, lcdm_params, psicdm_params):
    """
    Numerical derivative dPsi/dz.

    This quantity may be used as an auxiliary diagnostic indicator
    of the variation of the state-space coordinate with redshift.
    No physical interpretation is implied at this stage.

    Parameters
    ----------
    z : array_like
        Redshift grid (must be ordered).

    Returns
    -------
    dPsi_dz : ndarray
        Numerical derivative of Psi with respect to z.
    """
    z = np.asarray(z, dtype=float)
    Psi = psi_z(z, lcdm_params, psicdm_params)

    return np.gradient(Psi, z)
