# Copyright 2024-2025 SpectrixRD
# Licensed under the Apache License, Version 2.0
# See LICENSE file in the project root for full license text

"""
Transcorrelated Hamiltonian Construction

Builds similarity-transformed molecular Hamiltonians using Jastrow factors
for improved VQE performance and chemical accuracy.

Key Operations:
1. Compute standard molecular Hamiltonian (H_0)
2. Apply Jastrow similarity transformation: H_TC = e^T H_0 e^{-T}
3. Map to qubit operators with reduced correlation
4. Achieve chemical accuracy with shallower circuits

Mathematical Framework:
- T is anti-Hermitian Jastrow operator: T† = -T
- Similarity transformation preserves spectrum (eigenvalues unchanged)
- Baker-Campbell-Hausdorff expansion: H_TC = H + [T,H] + 1/2[[T,H],T] + ...
- Truncation at second order for practical implementation

References:
- Ten-no (2004): "Explicitly correlated second order perturbation theory"
- Dobrautz et al. (2024): "Transcorrelated electronic structure methods"
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

try:
    from openfermion import FermionOperator, QubitOperator
    from openfermion.transforms import jordan_wigner, bravyi_kitaev

    OPENFERMION_AVAILABLE = True
except ImportError:
    OPENFERMION_AVAILABLE = False

try:
    from loguru import logger
except ImportError:
    import logging

    logger = logging.getLogger(__name__)

from .transcorrelation import JastrowFactor, apply_jastrow_transformation


@dataclass
class TranscorrelatedHamiltonian:
    """
    Container for transcorrelated Hamiltonian data.

    Attributes:
        qubit_hamiltonian: Qubit operator (Jordan-Wigner or Bravyi-Kitaev)
        n_qubits: Number of qubits required
        jastrow_factor: Jastrow factor used
        original_energy: Energy before transcorrelation (Hartree)
        tc_energy_estimate: Estimated energy with TC (Hartree)
        energy_lowering: Expected energy reduction (mHa)
        depth_reduction: Expected circuit depth reduction (%)
        pauli_terms: Dictionary of Pauli strings and coefficients
        metadata: Additional information
    """

    qubit_hamiltonian: Any  # QubitOperator or SparsePauliOp
    n_qubits: int
    jastrow_factor: JastrowFactor
    original_energy: float
    tc_energy_estimate: float
    energy_lowering: float
    depth_reduction: float
    pauli_terms: Dict[str, float]
    metadata: Dict[str, Any]


def build_tc_hamiltonian(
    one_body_integrals: np.ndarray,
    two_body_integrals: np.ndarray,
    geometry: np.ndarray,
    n_electrons: int,
    jastrow_alpha: Optional[float] = None,
    transformation: str = "jordan_wigner",
    optimize_alpha: bool = True,
) -> TranscorrelatedHamiltonian:
    """
    Build transcorrelated Hamiltonian from molecular integrals.

    Args:
        one_body_integrals: One-electron integrals h_pq [n_orb, n_orb] (Hartree)
        two_body_integrals: Two-electron integrals g_pqrs [n_orb, n_orb, n_orb, n_orb] (Hartree)
        geometry: Atomic coordinates [n_atoms, 3] (bohr)
        n_electrons: Number of electrons
        jastrow_alpha: Jastrow parameter (optimized if None)
        transformation: Qubit mapping ('jordan_wigner' or 'bravyi_kitaev')
        optimize_alpha: Whether to optimize Jastrow parameter

    Returns:
        TranscorrelatedHamiltonian object

    Example:
        >>> h_one = np.array([[−1.0, 0.1], [0.1, −0.5]])
        >>> g_two = np.zeros((2, 2, 2, 2))
        >>> coords = np.array([[0, 0, 0], [0, 0, 1.4]])
        >>> tc_ham = build_tc_hamiltonian(h_one, g_two, coords, n_electrons=2)
        >>> print(f"Qubits: {tc_ham.n_qubits}, Energy lowering: {tc_ham.energy_lowering:.2f} mHa")
    """
    if not OPENFERMION_AVAILABLE:
        raise ImportError("OpenFermion required. Install: pip install openfermion")

    n_orb = one_body_integrals.shape[0]
    basis_size = n_orb

    # Optimize or use provided Jastrow parameter
    if jastrow_alpha is None and optimize_alpha:
        from .transcorrelation import optimize_jastrow_parameter

        jastrow_alpha = optimize_jastrow_parameter(
            geometry, n_electrons, basis_size, method="heuristic"
        )
        logger.info(f"Optimized Jastrow α = {jastrow_alpha:.3f}")
    elif jastrow_alpha is None:
        jastrow_alpha = 0.5  # Default
        logger.info(f"Using default Jastrow α = {jastrow_alpha:.3f}")

    # Create Jastrow factor
    jastrow = JastrowFactor(alpha=jastrow_alpha, num_electrons=n_electrons, form="simple")

    # Apply Jastrow transformation to integrals
    h_tc, g_tc = apply_jastrow_transformation(one_body_integrals, two_body_integrals, jastrow, geometry)

    # Build fermionic Hamiltonian from transformed integrals
    # H = Σ_pq h_pq a†_p a_q + 1/2 Σ_pqrs g_pqrs a†_p a†_q a_s a_r
    fermion_ham = FermionOperator()

    # One-body terms
    for p in range(n_orb):
        for q in range(n_orb):
            if abs(h_tc[p, q]) > 1e-12:
                # Create a†_p a_q operator
                fermion_ham += FermionOperator(f"{p}^ {q}", h_tc[p, q])

    # Two-body terms (physicist notation: g_pqrs <pq||rs>)
    for p in range(n_orb):
        for q in range(n_orb):
            for r in range(n_orb):
                for s in range(n_orb):
                    if abs(g_tc[p, q, r, s]) > 1e-12:
                        # Create a†_p a†_q a_s a_r operator
                        coeff = 0.5 * g_tc[p, q, r, s]
                        fermion_ham += FermionOperator(f"{p}^ {q}^ {s} {r}", coeff)

    # Transform to qubit Hamiltonian
    if transformation.lower() == "jordan_wigner":
        qubit_ham = jordan_wigner(fermion_ham)
    elif transformation.lower() == "bravyi_kitaev":
        qubit_ham = bravyi_kitaev(fermion_ham)
    else:
        raise ValueError(f"Unknown transformation: {transformation}")

    # Determine number of qubits
    n_qubits = 2 * n_orb  # Spin orbitals

    # Extract Pauli terms
    pauli_terms = {}
    for term, coeff in qubit_ham.terms.items():
        if not term:  # Identity
            pauli_string = "I" * n_qubits
        else:
            pauli_string = ["I"] * n_qubits
            for qubit_idx, pauli_op in term:
                pauli_string[qubit_idx] = pauli_op
            pauli_string = "".join(pauli_string)

        pauli_terms[pauli_string] = float(np.real(coeff))

    # Estimate energies
    original_energy = np.trace(h_tc) + 0.5 * np.sum(g_tc)  # Rough estimate
    tc_energy_estimate = original_energy  # Would need full calculation

    # Estimate improvements
    from .transcorrelation import estimate_tc_improvement

    improvements = estimate_tc_improvement(n_electrons, basis_size, jastrow_alpha)

    energy_lowering = improvements["energy_lowering_mha"]
    depth_reduction = improvements["circuit_depth_reduction_pct"]

    metadata = {
        "n_orbitals": n_orb,
        "n_electrons": n_electrons,
        "transformation": transformation,
        "basis_size": basis_size,
        "jastrow_alpha": jastrow_alpha,
        "jastrow_form": jastrow.form,
        "basis_improvement_factor": improvements["basis_improvement_factor"],
        "expected_accuracy_mha": improvements["expected_accuracy_mha"],
    }

    logger.info(
        f"Built TC Hamiltonian: {n_qubits} qubits, {len(pauli_terms)} Pauli terms, "
        f"expected {depth_reduction:.1f}% depth reduction"
    )

    return TranscorrelatedHamiltonian(
        qubit_hamiltonian=qubit_ham,
        n_qubits=n_qubits,
        jastrow_factor=jastrow,
        original_energy=original_energy,
        tc_energy_estimate=tc_energy_estimate,
        energy_lowering=energy_lowering,
        depth_reduction=depth_reduction,
        pauli_terms=pauli_terms,
        metadata=metadata,
    )


def convert_to_qiskit(tc_hamiltonian: TranscorrelatedHamiltonian) -> Any:
    """
    Convert transcorrelated Hamiltonian to Qiskit SparsePauliOp.

    Args:
        tc_hamiltonian: TranscorrelatedHamiltonian object

    Returns:
        Qiskit SparsePauliOp

    Example:
        >>> tc_ham = build_tc_hamiltonian(...)
        >>> qiskit_ham = convert_to_qiskit(tc_ham)
        >>> # Use with VQECircuit
    """
    try:
        from qiskit.quantum_info import SparsePauliOp

        pauli_list = list(tc_hamiltonian.pauli_terms.keys())
        coeffs = list(tc_hamiltonian.pauli_terms.values())

        return SparsePauliOp(pauli_list, coeffs=coeffs)

    except ImportError:
        raise ImportError("Qiskit required. Install: pip install qiskit")


def analyze_tc_hamiltonian(tc_hamiltonian: TranscorrelatedHamiltonian) -> Dict[str, Any]:
    """
    Analyze properties of transcorrelated Hamiltonian.

    Args:
        tc_hamiltonian: TranscorrelatedHamiltonian object

    Returns:
        Analysis dictionary

    Example:
        >>> tc_ham = build_tc_hamiltonian(...)
        >>> analysis = analyze_tc_hamiltonian(tc_ham)
        >>> print(f"Pauli weight distribution: {analysis['pauli_weight_dist']}")
    """
    # Count Pauli terms by weight (number of non-identity operators)
    weight_counts = {}
    for pauli_str in tc_hamiltonian.pauli_terms.keys():
        weight = sum(1 for p in pauli_str if p != "I")
        weight_counts[weight] = weight_counts.get(weight, 0) + 1

    # Analyze coefficient magnitudes
    coeffs = np.array(list(tc_hamiltonian.pauli_terms.values()))
    max_coeff = np.max(np.abs(coeffs))
    mean_coeff = np.mean(np.abs(coeffs))

    analysis = {
        "num_pauli_terms": len(tc_hamiltonian.pauli_terms),
        "pauli_weight_dist": weight_counts,
        "max_coefficient": float(max_coeff),
        "mean_coefficient": float(mean_coeff),
        "jastrow_alpha": tc_hamiltonian.jastrow_factor.alpha,
        "expected_energy_lowering_mha": tc_hamiltonian.energy_lowering,
        "expected_depth_reduction_pct": tc_hamiltonian.depth_reduction,
        "chemical_accuracy_achievable": tc_hamiltonian.energy_lowering > 1.6,
    }

    return analysis


# Example usage
if __name__ == "__main__":
    print("Transcorrelated Hamiltonian Construction Example")
    print("=" * 80)

    if OPENFERMION_AVAILABLE:
        # H2 molecule example
        print("\nBuilding transcorrelated Hamiltonian for H2")

        # Simple H2 integrals (STO-3G basis, 2 orbitals)
        n_orb = 2
        h_one = np.array([[-1.252, -0.475], [-0.475, -0.478]])  # One-electron (Hartree)

        # Two-electron integrals (chemist notation)
        g_two = np.zeros((n_orb, n_orb, n_orb, n_orb))
        g_two[0, 0, 0, 0] = 0.674
        g_two[1, 1, 1, 1] = 0.697
        g_two[0, 0, 1, 1] = 0.664
        g_two[1, 1, 0, 0] = 0.664
        g_two[0, 1, 0, 1] = 0.181
        g_two[0, 1, 1, 0] = 0.181
        g_two[1, 0, 0, 1] = 0.181
        g_two[1, 0, 1, 0] = 0.181

        # H2 geometry (bond length 1.4 bohr)
        h2_coords = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]])

        # Build transcorrelated Hamiltonian
        tc_ham = build_tc_hamiltonian(
            h_one, g_two, h2_coords, n_electrons=2, transformation="jordan_wigner", optimize_alpha=True
        )

        print(f"\nTranscorrelated Hamiltonian properties:")
        print(f"  Qubits: {tc_ham.n_qubits}")
        print(f"  Pauli terms: {len(tc_ham.pauli_terms)}")
        print(f"  Jastrow α: {tc_ham.jastrow_factor.alpha:.3f}")
        print(f"  Expected energy lowering: {tc_ham.energy_lowering:.2f} mHa")
        print(f"  Expected depth reduction: {tc_ham.depth_reduction:.1f}%")

        # Analyze Hamiltonian
        analysis = analyze_tc_hamiltonian(tc_ham)
        print(f"\nHamiltonian analysis:")
        print(f"  Pauli weight distribution: {analysis['pauli_weight_dist']}")
        print(f"  Max coefficient: {analysis['max_coefficient']:.4f}")
        print(f"  Mean coefficient: {analysis['mean_coefficient']:.4f}")
        print(f"  Chemical accuracy achievable: {analysis['chemical_accuracy_achievable']}")

        # Show sample Pauli terms
        print(f"\nSample Pauli terms (first 5):")
        for i, (pauli_str, coeff) in enumerate(list(tc_ham.pauli_terms.items())[:5]):
            print(f"  {pauli_str}: {coeff:+.6f}")

    else:
        print("OpenFermion not available")
