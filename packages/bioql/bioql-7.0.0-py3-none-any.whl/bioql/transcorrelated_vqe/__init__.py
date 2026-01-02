# Copyright 2024-2025 SpectrixRD
# Licensed under the Apache License, Version 2.0
# See LICENSE file in the project root for full license text

"""
Transcorrelated VQE Module

Implements transcorrelated VQE (JCTC 2024) for achieving chemical accuracy
with shallower quantum circuits using Jastrow correlation factors.

Key Features:
- Jastrow factor similarity transformation: H_TC = e^T H e^{-T}
- 50% reduction in circuit depth vs standard VQE
- Chemical accuracy (<1.6 mHa error) with smaller basis sets
- Automatic α parameter optimization for Jastrow factor

Physics:
- Jastrow factor explicitly captures electron correlation
- Transformation reduces strong correlation in Hamiltonian
- Enables accurate results with fewer ansatz parameters
- Better basis set convergence

Components:
- transcorrelation: Jastrow factor application and optimization
- tc_hamiltonian: Similarity-transformed Hamiltonian construction
- tc_vqe: Transcorrelated VQE solver with shallow circuits

References:
- Dobrautz et al., JCTC (2024): "Transcorrelated Selected Configuration Interaction"
- Cohen & Alavi, JCP (2020): "Transcorrelation in Many-Fermion Systems"
- Boys & Handy, Proc. Royal Soc. (1969): "Determination of Energies and Wavefunctions"
"""

from .transcorrelation import JastrowFactor, apply_jastrow_transformation
from .tc_hamiltonian import TranscorrelatedHamiltonian, build_tc_hamiltonian
from .tc_vqe import TranscorrelatedVQE, TCVQEResult

__all__ = [
    "JastrowFactor",
    "apply_jastrow_transformation",
    "TranscorrelatedHamiltonian",
    "build_tc_hamiltonian",
    "TranscorrelatedVQE",
    "TCVQEResult",
]

__version__ = "1.0.0"
