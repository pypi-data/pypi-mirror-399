# psi_continuum_statespace/plotting.py

"""
Plotting utilities for the Psi–Continuum state-space representation.

This module provides simple visualization tools for the macroscopic
state coordinate Psi(z).
"""

import numpy as np
import matplotlib.pyplot as plt

from .psi import psi_z


def plot_psi_z(
    z,
    lcdm_params,
    psicdm_params,
    outfile="psi_z.png",
    show=False,
):
    """
    Plot the state-space coordinate Psi(z).

    Parameters
    ----------
    z : array_like
        Redshift grid.
    lcdm_params : LCDMParams
        Reference ΛCDM parameters.
    psicdm_params : PsiCDMParams
        ΨCDM parameters (including ε₀).
    outfile : str, optional
        Output filename for the figure.
    show : bool, optional
        Whether to display the figure interactively.
    """
    z = np.asarray(z, dtype=float)
    Psi = psi_z(z, lcdm_params, psicdm_params)

    plt.figure(figsize=(6, 4))
    plt.plot(z, 100.0 * Psi, lw=2)

    plt.xlabel(r"Redshift $z$")
    plt.ylabel(r"State-space deviation $\Psi(z)\;[\%]$")
    plt.title(r"Psi–Continuum state-space coordinate")

    plt.axhline(0.0, color="k", lw=0.8, ls="--", alpha=0.6)
    plt.xlim(z.min(), z.max())

    plt.tight_layout()
    plt.savefig(outfile, dpi=300)

    if show:
        plt.show()

    plt.close()


def plot_consistency(z, psi_bundle, percent=True, filename=None):
    """
    Plot state-space consistency trajectories.

    Parameters
    ----------
    z : ndarray
    psi_bundle : dict
        label -> Ψ(z)
    percent : bool
        Plot in percent units.
    filename : str or None
        Save figure if provided.
    """
    plt.figure(figsize=(6, 4))
    for label, psi in psi_bundle.items():
        y = 100.0 * psi if percent else psi
        plt.plot(z, y, label=label)

    plt.axhline(0.0, color="gray", ls="--", lw=1)

    plt.xlabel("Redshift z")
    plt.ylabel("State-space deviation Ψ(z) [%]" if percent else "Ψ(z)")
    plt.title("Ψ–Continuum state-space consistency")
    plt.legend(frameon=False)
    plt.tight_layout()

    if filename:
        plt.savefig(filename, dpi=300)

    plt.show()
    plt.close()


def plot_state_space_differences(
    z,
    psi_bundle,
    reference="Joint",
    outfile="psi_delta.png",
    show=True,
):
    """
    Plot absolute state-space differences |ΔΨ(z)| relative to a reference.

    Parameters
    ----------
    z : array_like
        Redshift grid.
    psi_bundle : dict
        label -> Psi(z)
    reference : str
        Reference trajectory label.
    outfile : str
        Output filename.
    show : bool
        Show plot interactively.
    """
    z = np.asarray(z, dtype=float)
    ref = psi_bundle[reference]

    plt.figure(figsize=(6, 4))

    for label, psi in psi_bundle.items():
        if label == reference:
            continue

        delta = 100.0 * np.abs(psi - ref)
        plt.plot(z, delta, lw=2, label=f"|{label} − {reference}|")

    plt.xlabel(r"Redshift $z$")
    plt.ylabel(r"$|\Delta\Psi(z)|\;[\%]$")
    plt.title(f"State-space deviation relative to {reference}")

    plt.xlim(z.min(), z.max())
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(outfile, dpi=300)

    if show:
        plt.show()

    plt.close()

