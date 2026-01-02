# Copyright 2024-2025 SpectrixRD
# Licensed under the Apache License, Version 2.0
# See LICENSE file in the project root for full license text

"""
Fragment Molecular Orbital VQE (FMO-VQE) Module
================================================

Implementation of Fragment Molecular Orbital VQE based on:
- Scientific Reports (2024) - FMO-VQE methodology
- OpenFMO-VQE framework (https://github.com/QuNovaComputing/OpenFMO-VQE)

This module enables quantum chemistry calculations for large molecules (100-1000 qubits)
by fragmenting them into smaller, manageable pieces and using VQE on each fragment.

Key Components:
--------------
- fragmentor: Molecular fragmentation with bond-cutting strategies
- fragment_vqe: VQE solver for individual fragments
- fragment_assembler: Energy assembly and error estimation

Usage Example:
-------------
>>> from bioql.fmo_vqe import FMOFragmentor, FragmentVQESolver, FragmentAssembler
>>>
>>> # Fragment molecule
>>> fragmentor = FMOFragmentor(max_fragment_qubits=20)
>>> fragments = fragmentor.fragment_molecule("CC(=O)Oc1ccccc1C(=O)O")  # Aspirin
>>>
>>> # Solve each fragment with VQE
>>> solver = FragmentVQESolver(ansatz='RealAmplitudes')
>>> fragment_results = solver.solve_fragments(fragments)
>>>
>>> # Assemble total energy
>>> assembler = FragmentAssembler()
>>> total_energy = assembler.assemble_energy(fragment_results)
>>> print(f"Total molecular energy: {total_energy:.6f} Hartree")

Author: BioQL Team
Version: 1.0.0
"""

from .fragmentor import (
    FMOFragmentor,
    MolecularFragment,
    FragmentationStrategy,
    BondCuttingStrategy,
)
from .fragment_vqe import (
    FragmentVQESolver,
    FragmentVQEResult,
    FragmentHamiltonianBuilder,
)
from .fragment_assembler import (
    FragmentAssembler,
    FragmentCoupling,
    AssembledResult,
)

__all__ = [
    # Fragmentor
    "FMOFragmentor",
    "MolecularFragment",
    "FragmentationStrategy",
    "BondCuttingStrategy",
    # Fragment VQE
    "FragmentVQESolver",
    "FragmentVQEResult",
    "FragmentHamiltonianBuilder",
    # Assembler
    "FragmentAssembler",
    "FragmentCoupling",
    "AssembledResult",
]

__version__ = "1.0.0"
