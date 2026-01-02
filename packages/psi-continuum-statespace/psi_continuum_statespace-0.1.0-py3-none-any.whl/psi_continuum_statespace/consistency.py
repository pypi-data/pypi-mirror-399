# psi_continuum_statespace/consistency.py

"""
State-space consistency utilities.
"""

from .psi import psi_z


def compute_consistency_bundle(z, lcdm_params, psicdm_param_sets):
    """
    Compute Ψ(z) trajectories for multiple parameter sets.

    Parameters
    ----------
    z : ndarray
    lcdm_params : LCDMParams
    psicdm_param_sets : dict
        label -> PsiCDMParams

    Returns
    -------
    dict
        label -> Ψ(z)
    """
    return {
        label: psi_z(z, lcdm_params, params)
        for label, params in psicdm_param_sets.items()
    }
