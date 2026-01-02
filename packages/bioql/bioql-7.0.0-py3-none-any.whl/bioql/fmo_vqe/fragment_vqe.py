# Copyright 2024-2025 SpectrixRD
# Licensed under the Apache License, Version 2.0
# See LICENSE file in the project root for full license text

"""
Fragment VQE Solver Module
===========================

VQE solver for individual molecular fragments with caching and optimization.

Key Features:
------------
- Fragment-specific Hamiltonian construction
- VQE optimization with multiple ansatz options
- Result caching to avoid recomputation
- Parallel fragment solving (optional)

Author: BioQL Team
Version: 1.0.0
"""

import hashlib
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from qiskit.quantum_info import SparsePauliOp
from rdkit import Chem
from rdkit.Chem import AllChem

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from ..circuits.algorithms.vqe import VQECircuit, VQEResult
from .fragmentor import MolecularFragment


@dataclass
class FragmentVQEResult:
    """
    Result from VQE calculation on a single fragment.

    Attributes:
        fragment_id: Fragment identifier
        success: Whether VQE converged
        ground_state_energy: Fragment ground state energy (Hartree)
        vqe_result: Full VQE optimization result
        hamiltonian: Fragment Hamiltonian
        num_qubits: Qubits used
        computation_time: Time taken (seconds)
        cache_hit: Whether result was from cache
    """
    fragment_id: int
    success: bool
    ground_state_energy: float
    vqe_result: VQEResult
    hamiltonian: SparsePauliOp
    num_qubits: int
    computation_time: float
    cache_hit: bool = False
    metadata: Optional[Dict] = None


class FragmentHamiltonianBuilder:
    """
    Builds quantum Hamiltonians for molecular fragments.

    Uses simplified quantum chemistry approximations suitable for fragments:
    - STO-3G minimal basis set
    - Jordan-Wigner transformation
    - Active space reduction
    """

    def __init__(
        self,
        basis: str = "sto-3g",
        frozen_core: bool = True,
        active_space_reduction: bool = True,
    ):
        """
        Initialize Hamiltonian builder.

        Args:
            basis: Quantum chemistry basis set
            frozen_core: Freeze core orbitals
            active_space_reduction: Reduce to active orbitals only
        """
        self.basis = basis
        self.frozen_core = frozen_core
        self.active_space_reduction = active_space_reduction

    def build_hamiltonian(
        self,
        fragment: MolecularFragment,
    ) -> Tuple[SparsePauliOp, int]:
        """
        Build Hamiltonian for a molecular fragment.

        Args:
            fragment: Molecular fragment

        Returns:
            (hamiltonian, num_qubits)

        Example:
            >>> builder = FragmentHamiltonianBuilder()
            >>> hamiltonian, num_qubits = builder.build_hamiltonian(fragment)
        """
        logger.debug(
            f"Building Hamiltonian for fragment {fragment.fragment_id} "
            f"({fragment.num_atoms} atoms)"
        )

        # Try using PySCF for accurate Hamiltonian (if available)
        try:
            hamiltonian, num_qubits = self._build_with_pyscf(fragment)
            logger.debug(f"Built Hamiltonian with PySCF: {num_qubits} qubits")
            return hamiltonian, num_qubits
        except (ImportError, Exception) as e:
            logger.warning(f"PySCF not available or failed: {e}")

        # Fallback: simplified Hamiltonian
        hamiltonian, num_qubits = self._build_simplified(fragment)
        logger.debug(f"Built simplified Hamiltonian: {num_qubits} qubits")
        return hamiltonian, num_qubits

    def _build_with_pyscf(
        self,
        fragment: MolecularFragment,
    ) -> Tuple[SparsePauliOp, int]:
        """Build Hamiltonian using PySCF (accurate quantum chemistry)."""
        try:
            from pyscf import gto, scf
            from qiskit_nature.second_q.drivers import PySCFDriver
            from qiskit_nature.second_q.mappers import JordanWignerMapper
            from qiskit_nature.second_q.transformers import ActiveSpaceTransformer
        except ImportError:
            raise ImportError("PySCF or qiskit-nature not available")

        # Convert RDKit mol to PySCF format
        atom_string = self._mol_to_pyscf_string(fragment.mol)

        # Build PySCF molecule
        mol = gto.M(
            atom=atom_string,
            basis=self.basis,
            charge=0,
            spin=0,
        )

        # Run Hartree-Fock
        mf = scf.RHF(mol)
        mf.kernel()

        # Get molecular Hamiltonian
        driver = PySCFDriver.from_molecule(mol)
        problem = driver.run()

        # Active space reduction
        if self.active_space_reduction:
            num_electrons = fragment.num_electrons
            num_orbitals = fragment.num_atoms

            # Simple active space: use valence orbitals only
            num_active_electrons = min(num_electrons, num_orbitals * 2)
            num_active_orbitals = (num_active_electrons + 1) // 2

            transformer = ActiveSpaceTransformer(
                num_electrons=num_active_electrons,
                num_spatial_orbitals=num_active_orbitals,
            )
            problem = transformer.transform(problem)

        # Map to qubits using Jordan-Wigner
        mapper = JordanWignerMapper()
        hamiltonian = mapper.map(problem.second_q_ops()[0])

        num_qubits = hamiltonian.num_qubits

        return hamiltonian, num_qubits

    def _mol_to_pyscf_string(self, mol: Chem.Mol) -> str:
        """Convert RDKit molecule to PySCF atom string."""
        if mol.GetNumConformers() == 0:
            # Generate 3D coordinates
            AllChem.EmbedMolecule(mol, randomSeed=42)
            AllChem.MMFFOptimizeMolecule(mol)

        conf = mol.GetConformer()
        atom_lines = []

        for atom in mol.GetAtoms():
            idx = atom.GetIdx()
            symbol = atom.GetSymbol()
            pos = conf.GetAtomPosition(idx)
            atom_lines.append(f"{symbol} {pos.x:.6f} {pos.y:.6f} {pos.z:.6f}")

        return "; ".join(atom_lines)

    def _build_simplified(
        self,
        fragment: MolecularFragment,
    ) -> Tuple[SparsePauliOp, int]:
        """
        Build simplified Hamiltonian using Huckel theory.

        This is a fallback when PySCF is not available.
        Uses extended Huckel theory for π-systems.
        """
        mol = fragment.mol
        num_atoms = mol.GetNumAtoms()

        # Estimate number of molecular orbitals
        num_orbitals = num_atoms
        num_qubits = min(num_orbitals * 2, fragment.num_qubits)

        # Build one-electron integral matrix
        h_matrix = np.zeros((num_orbitals, num_orbitals))

        for i, atom in enumerate(mol.GetAtoms()):
            # Diagonal: ionization potential (simplified)
            z = atom.GetAtomicNum()
            h_matrix[i, i] = -z * 0.5  # Approximate IP in Hartree

            # Off-diagonal: resonance integrals
            for bond in atom.GetBonds():
                j = bond.GetOtherAtomIdx(i)
                if i < j < num_orbitals:
                    # Resonance integral (distance-dependent)
                    h_matrix[i, j] = -2.4 / 27.2114  # ~-0.088 Hartree
                    h_matrix[j, i] = h_matrix[i, j]

        # Convert to Pauli operators using Jordan-Wigner
        pauli_terms = self._jordan_wigner_transform(h_matrix, num_qubits)

        # Build SparsePauliOp
        if not pauli_terms:
            # Empty Hamiltonian - use identity
            pauli_terms = {"I" * num_qubits: 0.0}

        pauli_list = list(pauli_terms.keys())
        coeffs = list(pauli_terms.values())

        hamiltonian = SparsePauliOp(pauli_list, coeffs=coeffs)

        return hamiltonian, num_qubits

    def _jordan_wigner_transform(
        self,
        h_matrix: np.ndarray,
        num_qubits: int,
    ) -> Dict[str, float]:
        """
        Jordan-Wigner transformation for one-electron integrals.

        Maps fermionic operators to Pauli operators:
        a†_p a_q → (1/2) Σ_σ [X_pX_q + Y_pY_q] (with Z string)
        """
        pauli_terms = {}
        n_orbitals = len(h_matrix)

        for p in range(min(n_orbitals, num_qubits)):
            for q in range(min(n_orbitals, num_qubits)):
                if abs(h_matrix[p, q]) < 1e-10:
                    continue

                coeff = h_matrix[p, q] / 2.0

                if p == q:
                    # Number operator: (I - Z)/2
                    pauli_str = "I" * p + "Z" + "I" * (num_qubits - p - 1)
                    pauli_terms[pauli_str] = pauli_terms.get(pauli_str, 0.0) - coeff

                    pauli_str = "I" * num_qubits
                    pauli_terms[pauli_str] = pauli_terms.get(pauli_str, 0.0) + coeff
                else:
                    # Hopping terms: XX + YY
                    pauli_str_xx = list("I" * num_qubits)
                    pauli_str_xx[p] = "X"
                    pauli_str_xx[q] = "X"
                    for i in range(min(p, q) + 1, max(p, q)):
                        pauli_str_xx[i] = "Z"
                    pauli_terms["".join(pauli_str_xx)] = \
                        pauli_terms.get("".join(pauli_str_xx), 0.0) + coeff

                    pauli_str_yy = list("I" * num_qubits)
                    pauli_str_yy[p] = "Y"
                    pauli_str_yy[q] = "Y"
                    for i in range(min(p, q) + 1, max(p, q)):
                        pauli_str_yy[i] = "Z"
                    pauli_terms["".join(pauli_str_yy)] = \
                        pauli_terms.get("".join(pauli_str_yy), 0.0) + coeff

        return pauli_terms


class FragmentVQESolver:
    """
    VQE solver for molecular fragments.

    Features:
    - Automatic Hamiltonian construction
    - Result caching
    - Multiple ansatz support
    - Parallel execution (optional)
    """

    def __init__(
        self,
        ansatz: str = "RealAmplitudes",
        optimizer: str = "COBYLA",
        num_layers: int = 2,
        shots: int = 1024,
        maxiter: int = 100,
        cache_dir: Optional[str] = None,
        use_cache: bool = True,
    ):
        """
        Initialize fragment VQE solver.

        Args:
            ansatz: VQE ansatz type
            optimizer: Classical optimizer
            num_layers: Ansatz depth
            shots: Measurement shots per evaluation
            maxiter: Maximum optimization iterations
            cache_dir: Directory for caching results
            use_cache: Enable result caching
        """
        self.ansatz = ansatz
        self.optimizer = optimizer
        self.num_layers = num_layers
        self.shots = shots
        self.maxiter = maxiter
        self.use_cache = use_cache

        # Setup cache
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path.home() / ".bioql" / "fmo_vqe_cache"

        if use_cache:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.hamiltonian_builder = FragmentHamiltonianBuilder()

        logger.info(
            f"Initialized FragmentVQESolver: "
            f"ansatz={ansatz}, optimizer={optimizer}, "
            f"cache={use_cache}"
        )

    def solve_fragment(
        self,
        fragment: MolecularFragment,
    ) -> FragmentVQEResult:
        """
        Solve a single fragment with VQE.

        Args:
            fragment: Molecular fragment

        Returns:
            FragmentVQEResult with optimization results

        Example:
            >>> solver = FragmentVQESolver()
            >>> result = solver.solve_fragment(fragment)
            >>> print(f"Energy: {result.ground_state_energy:.6f} Hartree")
        """
        import time
        start_time = time.time()

        logger.info(
            f"Solving fragment {fragment.fragment_id} "
            f"({fragment.num_atoms} atoms, {fragment.num_qubits} qubits)"
        )

        # Check cache
        if self.use_cache:
            cached_result = self._load_from_cache(fragment)
            if cached_result is not None:
                logger.info(f"Cache hit for fragment {fragment.fragment_id}")
                cached_result.cache_hit = True
                return cached_result

        # Build Hamiltonian
        hamiltonian, num_qubits = self.hamiltonian_builder.build_hamiltonian(fragment)

        # Run VQE
        vqe = VQECircuit(
            hamiltonian=hamiltonian,
            ansatz=self.ansatz,
            optimizer=self.optimizer,
            num_layers=self.num_layers,
        )

        vqe_result = vqe.optimize(shots=self.shots, maxiter=self.maxiter)

        computation_time = time.time() - start_time

        # Create result
        result = FragmentVQEResult(
            fragment_id=fragment.fragment_id,
            success=vqe_result.success,
            ground_state_energy=vqe_result.optimal_energy,
            vqe_result=vqe_result,
            hamiltonian=hamiltonian,
            num_qubits=num_qubits,
            computation_time=computation_time,
            metadata={
                "fragment_smiles": fragment.smiles,
                "num_atoms": fragment.num_atoms,
                "capping_atoms": len(fragment.capping_atoms),
            },
        )

        # Save to cache
        if self.use_cache:
            self._save_to_cache(fragment, result)

        logger.info(
            f"Fragment {fragment.fragment_id} solved: "
            f"energy={result.ground_state_energy:.6f} Hartree, "
            f"time={computation_time:.2f}s"
        )

        return result

    def solve_fragments(
        self,
        fragments: List[MolecularFragment],
        parallel: bool = False,
    ) -> List[FragmentVQEResult]:
        """
        Solve multiple fragments.

        Args:
            fragments: List of fragments
            parallel: Use parallel execution (experimental)

        Returns:
            List of FragmentVQEResult objects

        Example:
            >>> results = solver.solve_fragments(fragments)
            >>> total_energy = sum(r.ground_state_energy for r in results)
        """
        logger.info(f"Solving {len(fragments)} fragments")

        if parallel:
            # Parallel execution (requires joblib)
            try:
                from joblib import Parallel, delayed
                results = Parallel(n_jobs=-1)(
                    delayed(self.solve_fragment)(frag)
                    for frag in fragments
                )
            except ImportError:
                logger.warning("joblib not available - using sequential execution")
                results = [self.solve_fragment(frag) for frag in fragments]
        else:
            # Sequential execution
            results = [self.solve_fragment(frag) for frag in fragments]

        successful = sum(1 for r in results if r.success)
        logger.info(f"Solved {successful}/{len(fragments)} fragments successfully")

        return results

    def _get_cache_key(self, fragment: MolecularFragment) -> str:
        """Generate cache key for fragment."""
        # Hash based on SMILES and VQE parameters
        key_data = {
            "smiles": fragment.smiles,
            "ansatz": self.ansatz,
            "optimizer": self.optimizer,
            "num_layers": self.num_layers,
            "maxiter": self.maxiter,
        }
        key_str = str(sorted(key_data.items()))
        return hashlib.md5(key_str.encode()).hexdigest()

    def _load_from_cache(
        self,
        fragment: MolecularFragment,
    ) -> Optional[FragmentVQEResult]:
        """Load result from cache."""
        cache_key = self._get_cache_key(fragment)
        cache_file = self.cache_dir / f"{cache_key}.pkl"

        if cache_file.exists():
            try:
                with open(cache_file, "rb") as f:
                    result = pickle.load(f)
                return result
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")

        return None

    def _save_to_cache(
        self,
        fragment: MolecularFragment,
        result: FragmentVQEResult,
    ) -> None:
        """Save result to cache."""
        cache_key = self._get_cache_key(fragment)
        cache_file = self.cache_dir / f"{cache_key}.pkl"

        try:
            with open(cache_file, "wb") as f:
                pickle.dump(result, f)
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")


# Example usage
if __name__ == "__main__":
    from .fragmentor import FMOFragmentor

    print("=" * 80)
    print("Fragment VQE Solver - Test Cases")
    print("=" * 80)

    # Test 1: Single fragment (water)
    print("\nTest 1: Water molecule")
    fragmentor = FMOFragmentor()
    fragments = fragmentor.fragment_molecule("O")

    solver = FragmentVQESolver(maxiter=50)
    result = solver.solve_fragment(fragments[0])

    print(f"Fragment ID: {result.fragment_id}")
    print(f"Success: {result.success}")
    print(f"Ground state energy: {result.ground_state_energy:.6f} Hartree")
    print(f"Num qubits: {result.num_qubits}")
    print(f"Time: {result.computation_time:.2f}s")

    # Test 2: Multiple fragments (aspirin)
    print("\nTest 2: Aspirin (fragmented)")
    fragmentor = FMOFragmentor(max_fragment_qubits=16, max_fragment_atoms=6)
    fragments = fragmentor.fragment_molecule("CC(=O)Oc1ccccc1C(=O)O")

    results = solver.solve_fragments(fragments)

    print(f"\nResults:")
    for res in results:
        print(
            f"  Fragment {res.fragment_id}: "
            f"E={res.ground_state_energy:.6f} Ha, "
            f"success={res.success}"
        )

    print("\n" + "=" * 80)
    print("Fragment VQE solver tests completed!")
    print("=" * 80)
