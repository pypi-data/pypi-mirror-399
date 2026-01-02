# Copyright 2024-2025 SpectrixRD
# Licensed under the Apache License, Version 2.0
# See LICENSE file in the project root for full license text

"""
DFT Comparison Module

Compare quantum methods against classical DFT calculations using PySCF.
Supports multiple functionals: B3LYP, ω-B97X-D, PBE, M06-2X
"""

import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from loguru import logger


@dataclass
class DFTResult:
    """Result from a DFT calculation."""
    molecule: str
    functional: str
    basis_set: str

    # Energy results
    total_energy: float  # Hartree
    scf_energy: float  # Hartree
    correlation_energy: Optional[float] = None  # Hartree

    # Computational metrics
    wall_time: float = 0.0  # seconds
    scf_iterations: int = 0
    converged: bool = True

    # Molecular properties
    num_electrons: int = 0
    num_basis_functions: int = 0
    multiplicity: int = 1

    # Metadata
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class QuantumVsDFTComparison:
    """Comparison between quantum method and DFT."""
    molecule: str
    quantum_method: str
    dft_functional: str

    # Energy comparison
    quantum_energy: float
    dft_energy: float
    energy_difference: float  # quantum - dft
    relative_difference: float  # percentage

    # Performance comparison
    quantum_time: float
    dft_time: float
    speedup: float  # dft_time / quantum_time

    # Accuracy comparison (if reference available)
    quantum_error: Optional[float] = None
    dft_error: Optional[float] = None
    quantum_more_accurate: Optional[bool] = None

    # Resource comparison
    quantum_qubits: Optional[int] = None
    dft_basis_size: Optional[int] = None

    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class DFTBenchmark:
    """
    DFT benchmarking against quantum methods.

    Supports PySCF calculations with multiple functionals and basis sets.

    Example:
        >>> from bioql.benchmarks.quantum_advantage import DFTBenchmark
        >>> benchmark = DFTBenchmark()
        >>> result = benchmark.run_dft("H2", functional="B3LYP", basis="6-31G")
        >>> print(f"Energy: {result.total_energy:.6f} Hartree")
    """

    def __init__(self):
        """Initialize DFT benchmark."""
        self.results: List[DFTResult] = []
        self.comparisons: List[QuantumVsDFTComparison] = []

        # Standard test molecules with geometries (Angstroms)
        self.test_molecules = {
            'H2': {
                'atoms': 'H 0 0 0; H 0 0 0.735',
                'charge': 0,
                'spin': 0,
                'exact_energy': -1.137  # FCI/STO-3G
            },
            'LiH': {
                'atoms': 'Li 0 0 0; H 0 0 1.596',
                'charge': 0,
                'spin': 0,
                'exact_energy': -7.882
            },
            'H2O': {
                'atoms': 'O 0 0 0; H 0.758 0.587 0; H -0.758 0.587 0',
                'charge': 0,
                'spin': 0,
                'exact_energy': -76.0
            },
            'NH3': {
                'atoms': 'N 0 0 0; H 0 0.937 0.383; H 0.811 -0.469 0.383; H -0.811 -0.469 0.383',
                'charge': 0,
                'spin': 0,
                'exact_energy': -56.2
            },
            'CH4': {
                'atoms': 'C 0 0 0; H 0.628 0.628 0.628; H -0.628 -0.628 0.628; H -0.628 0.628 -0.628; H 0.628 -0.628 -0.628',
                'charge': 0,
                'spin': 0,
                'exact_energy': -40.2
            }
        }

    def run_dft(
        self,
        molecule: str,
        functional: str = "B3LYP",
        basis: str = "6-31G",
        use_pyscf: bool = True
    ) -> DFTResult:
        """
        Run DFT calculation on a molecule.

        Args:
            molecule: Molecule name (must be in test_molecules)
            functional: DFT functional (B3LYP, wb97x-d, PBE, M06-2X)
            basis: Basis set (STO-3G, 6-31G, 6-31G*, cc-pVDZ, etc.)
            use_pyscf: Use PySCF for actual calculation (requires PySCF installed)

        Returns:
            DFTResult object
        """
        logger.info(f"Running DFT: {molecule} with {functional}/{basis}")

        if molecule not in self.test_molecules:
            raise ValueError(f"Molecule {molecule} not in test set. Available: {list(self.test_molecules.keys())}")

        mol_data = self.test_molecules[molecule]

        start_time = time.time()

        if use_pyscf:
            try:
                result = self._run_pyscf_dft(molecule, mol_data, functional, basis)
            except ImportError:
                logger.warning("PySCF not available, using simulation mode")
                result = self._simulate_dft(molecule, mol_data, functional, basis)
        else:
            result = self._simulate_dft(molecule, mol_data, functional, basis)

        result.wall_time = time.time() - start_time
        self.results.append(result)

        logger.info(f"DFT complete: E = {result.total_energy:.6f} Ha in {result.wall_time:.2f}s")
        return result

    def _run_pyscf_dft(
        self,
        molecule: str,
        mol_data: Dict,
        functional: str,
        basis: str
    ) -> DFTResult:
        """Run actual PySCF DFT calculation."""
        try:
            from pyscf import gto, dft

            # Build molecule
            mol = gto.M(
                atom=mol_data['atoms'],
                basis=basis,
                charge=mol_data['charge'],
                spin=mol_data['spin']
            )

            # Run DFT
            mf = dft.RKS(mol)
            mf.xc = functional.lower()
            total_energy = mf.kernel()

            converged = mf.converged
            scf_iterations = getattr(mf, 'scf_iterations', 0)

            return DFTResult(
                molecule=molecule,
                functional=functional,
                basis_set=basis,
                total_energy=total_energy,
                scf_energy=total_energy,
                converged=converged,
                scf_iterations=scf_iterations,
                num_electrons=mol.nelectron,
                num_basis_functions=mol.nao_nr(),
                multiplicity=mol_data['spin'] + 1,
                metadata={'pyscf': True, 'mol_data': mol_data}
            )

        except Exception as e:
            logger.error(f"PySCF calculation failed: {e}")
            raise

    def _simulate_dft(
        self,
        molecule: str,
        mol_data: Dict,
        functional: str,
        basis: str
    ) -> DFTResult:
        """Simulate DFT calculation (for demonstration)."""
        # Estimate energy based on exact energy and functional accuracy
        exact_energy = mol_data['exact_energy']

        # Typical DFT errors by functional (rough estimates)
        functional_errors = {
            'B3LYP': 0.05,  # ~5% typical error
            'wb97x-d': 0.03,  # Better for dispersion
            'PBE': 0.07,
            'M06-2X': 0.04,
            'HF': 0.10  # Hartree-Fock for comparison
        }

        error_factor = functional_errors.get(functional.upper(), 0.05)
        noise = np.random.normal(0, error_factor * abs(exact_energy))
        total_energy = exact_energy + noise

        # Estimate basis set size
        basis_sizes = {
            'STO-3G': 5,
            '6-31G': 9,
            '6-31G*': 15,
            'cc-pVDZ': 14,
            'cc-pVTZ': 30
        }
        num_basis = basis_sizes.get(basis, 10)

        # Estimate number of electrons
        atom_electrons = {'H': 1, 'Li': 3, 'Be': 4, 'C': 6, 'N': 7, 'O': 8}
        atoms = mol_data['atoms'].split(';')
        num_electrons = sum(
            atom_electrons.get(atom.strip().split()[0], 0)
            for atom in atoms
        )

        # Estimate SCF iterations (scales with system size)
        scf_iterations = 10 + num_electrons // 2

        return DFTResult(
            molecule=molecule,
            functional=functional,
            basis_set=basis,
            total_energy=total_energy,
            scf_energy=total_energy,
            converged=True,
            scf_iterations=scf_iterations,
            num_electrons=num_electrons,
            num_basis_functions=num_basis * len(atoms),
            multiplicity=mol_data['spin'] + 1,
            metadata={'simulated': True, 'mol_data': mol_data}
        )

    def compare_with_quantum(
        self,
        molecule: str,
        quantum_result: Any,
        dft_functional: str = "B3LYP",
        dft_basis: str = "6-31G"
    ) -> QuantumVsDFTComparison:
        """
        Compare quantum method result with DFT.

        Args:
            molecule: Molecule name
            quantum_result: BenchmarkResult from quantum calculation
            dft_functional: DFT functional to use
            dft_basis: Basis set for DFT

        Returns:
            QuantumVsDFTComparison object
        """
        logger.info(f"Comparing quantum vs DFT for {molecule}")

        # Run DFT if not already done
        dft_result = self.run_dft(molecule, dft_functional, dft_basis)

        # Energy comparison
        quantum_energy = quantum_result.computed_value
        dft_energy = dft_result.total_energy
        energy_diff = quantum_energy - dft_energy
        rel_diff = (energy_diff / abs(dft_energy)) * 100 if dft_energy != 0 else 0

        # Performance comparison
        speedup = dft_result.wall_time / quantum_result.wall_time if quantum_result.wall_time > 0 else 0

        # Accuracy comparison (if reference available)
        reference = quantum_result.reference_value
        quantum_error = None
        dft_error = None
        quantum_more_accurate = None

        if reference is not None:
            quantum_error = abs(quantum_energy - reference)
            dft_error = abs(dft_energy - reference)
            quantum_more_accurate = quantum_error < dft_error

        comparison = QuantumVsDFTComparison(
            molecule=molecule,
            quantum_method=quantum_result.method,
            dft_functional=dft_functional,
            quantum_energy=quantum_energy,
            dft_energy=dft_energy,
            energy_difference=energy_diff,
            relative_difference=rel_diff,
            quantum_time=quantum_result.wall_time,
            dft_time=dft_result.wall_time,
            speedup=speedup,
            quantum_error=quantum_error,
            dft_error=dft_error,
            quantum_more_accurate=quantum_more_accurate,
            quantum_qubits=quantum_result.qubits_used,
            dft_basis_size=dft_result.num_basis_functions,
            metadata={
                'quantum_result': quantum_result.to_dict(),
                'dft_result': dft_result.__dict__
            }
        )

        self.comparisons.append(comparison)
        return comparison

    def run_functional_comparison(
        self,
        molecule: str,
        functionals: List[str] = None,
        basis: str = "6-31G"
    ) -> Dict[str, DFTResult]:
        """
        Compare multiple DFT functionals on same molecule.

        Args:
            molecule: Molecule name
            functionals: List of functionals (default: common ones)
            basis: Basis set to use

        Returns:
            Dictionary mapping functional to DFTResult
        """
        if functionals is None:
            functionals = ['B3LYP', 'wb97x-d', 'PBE', 'M06-2X']

        logger.info(f"Comparing {len(functionals)} functionals for {molecule}")

        results = {}
        for functional in functionals:
            try:
                result = self.run_dft(molecule, functional, basis)
                results[functional] = result
            except Exception as e:
                logger.error(f"Failed {functional}: {e}")

        return results

    def generate_comparison_report(self) -> str:
        """
        Generate report comparing quantum methods vs DFT.

        Returns:
            Formatted report string
        """
        lines = []
        lines.append("=" * 80)
        lines.append("QUANTUM VS DFT COMPARISON REPORT")
        lines.append("=" * 80)
        lines.append("")

        if not self.comparisons:
            lines.append("No comparisons available. Run compare_with_quantum() first.")
            return "\n".join(lines)

        # Summary statistics
        quantum_wins = sum(1 for c in self.comparisons if c.quantum_more_accurate)
        total_with_ref = sum(1 for c in self.comparisons if c.quantum_more_accurate is not None)

        lines.append("SUMMARY:")
        lines.append("-" * 80)
        lines.append(f"Total comparisons: {len(self.comparisons)}")
        if total_with_ref > 0:
            lines.append(f"Quantum more accurate: {quantum_wins}/{total_with_ref} ({100*quantum_wins/total_with_ref:.1f}%)")

        speedups = [c.speedup for c in self.comparisons]
        lines.append(f"Mean speedup: {np.mean(speedups):.2f}x")
        lines.append(f"Median speedup: {np.median(speedups):.2f}x")
        lines.append("")

        # Detailed comparisons
        lines.append("DETAILED COMPARISONS:")
        lines.append("-" * 80)
        lines.append(f"{'Molecule':<15} {'Q-Method':<20} {'DFT':<15} {'Q-Error':<12} {'DFT-Error':<12} {'Winner'}")
        lines.append("-" * 80)

        for c in self.comparisons:
            if c.quantum_error is not None and c.dft_error is not None:
                winner = "QUANTUM" if c.quantum_more_accurate else "DFT"
                lines.append(
                    f"{c.molecule:<15} {c.quantum_method:<20} {c.dft_functional:<15} "
                    f"{c.quantum_error:>10.6f}  {c.dft_error:>10.6f}  {winner}"
                )

        lines.append("")
        lines.append("=" * 80)

        return "\n".join(lines)


# Convenience functions

def quick_dft_comparison(
    molecule: str = "H2",
    quantum_method: str = "fmo_vqe",
    quantum_results: List[Any] = None
) -> Dict[str, Any]:
    """
    Quick comparison of quantum method vs DFT.

    Args:
        molecule: Molecule to compare
        quantum_method: Quantum method name
        quantum_results: List of quantum benchmark results

    Returns:
        Comparison summary dictionary
    """
    benchmark = DFTBenchmark()

    # Find quantum result
    if quantum_results:
        qr = next((r for r in quantum_results if r.molecule == molecule and r.method == quantum_method), None)
        if qr:
            comparison = benchmark.compare_with_quantum(molecule, qr)
            return {
                'molecule': molecule,
                'quantum_method': quantum_method,
                'quantum_energy': comparison.quantum_energy,
                'dft_energy': comparison.dft_energy,
                'speedup': comparison.speedup,
                'quantum_more_accurate': comparison.quantum_more_accurate
            }

    # Just run DFT
    dft_result = benchmark.run_dft(molecule)
    return {
        'molecule': molecule,
        'dft_energy': dft_result.total_energy,
        'dft_time': dft_result.wall_time
    }


__all__ = [
    "DFTBenchmark",
    "DFTResult",
    "QuantumVsDFTComparison",
    "quick_dft_comparison",
]
