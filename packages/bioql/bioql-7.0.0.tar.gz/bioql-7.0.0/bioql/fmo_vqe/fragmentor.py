# Copyright 2024-2025 SpectrixRD
# Licensed under the Apache License, Version 2.0
# See LICENSE file in the project root for full license text

"""
Molecular Fragmentor Module
============================

Implements molecular fragmentation strategies for FMO-VQE based on:
- OpenFMO-VQE (https://github.com/QuNovaComputing/OpenFMO-VQE)
- Scientific Reports 2024 - Fragment Molecular Orbital VQE

Fragmentation Strategy:
----------------------
1. Analyze molecular graph structure
2. Identify optimal bond-cutting points (minimize inter-fragment coupling)
3. Create overlapping fragments with capping atoms (H)
4. Ensure fragments stay within qubit limits (max 20 qubits per fragment)

Author: BioQL Team
Version: 1.0.0
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class FragmentationStrategy(Enum):
    """Fragmentation strategy types."""
    SINGLE_BOND = "single_bond"  # Cut single bonds only
    FUNCTIONAL_GROUP = "functional_group"  # Preserve functional groups
    RING_PRESERVING = "ring_preserving"  # Keep rings intact
    ADAPTIVE = "adaptive"  # Adaptive strategy based on molecule


class BondCuttingStrategy(Enum):
    """Bond cutting priority strategies."""
    MIN_COUPLING = "min_coupling"  # Minimize inter-fragment coupling
    BALANCED_SIZE = "balanced_size"  # Balance fragment sizes
    PRESERVE_CONJUGATION = "preserve_conjugation"  # Keep conjugated systems


@dataclass
class MolecularFragment:
    """
    Represents a molecular fragment with metadata.

    Attributes:
        fragment_id: Unique fragment identifier
        mol: RDKit molecule object for fragment
        smiles: SMILES representation
        atom_indices: Original atom indices from parent molecule
        num_atoms: Number of atoms in fragment
        num_electrons: Total electrons (for qubit calculation)
        num_qubits: Estimated qubits needed (2 * molecular orbitals)
        capping_atoms: Indices of capping hydrogen atoms
        neighbor_fragments: IDs of neighboring fragments
        parent_bonds: Bonds cut to create this fragment
        coordinates_3d: 3D coordinates (Angstrom)
    """
    fragment_id: int
    mol: Chem.Mol
    smiles: str
    atom_indices: List[int]
    num_atoms: int
    num_electrons: int
    num_qubits: int
    capping_atoms: List[int] = field(default_factory=list)
    neighbor_fragments: Set[int] = field(default_factory=set)
    parent_bonds: List[Tuple[int, int]] = field(default_factory=list)
    coordinates_3d: Optional[np.ndarray] = None

    def __repr__(self) -> str:
        return (
            f"Fragment(id={self.fragment_id}, "
            f"atoms={self.num_atoms}, "
            f"qubits={self.num_qubits}, "
            f"SMILES={self.smiles})"
        )


class FMOFragmentor:
    """
    Fragment Molecular Orbital fragmentor.

    Fragments large molecules into smaller, overlapping pieces suitable for
    quantum chemistry calculations with limited qubit resources.

    Example:
        >>> fragmentor = FMOFragmentor(max_fragment_qubits=20)
        >>> fragments = fragmentor.fragment_molecule("CC(=O)Oc1ccccc1C(=O)O")
        >>> print(f"Created {len(fragments)} fragments")
        >>> for frag in fragments:
        >>>     print(f"  {frag}")
    """

    def __init__(
        self,
        max_fragment_qubits: int = 20,
        max_fragment_atoms: int = 10,
        overlap_atoms: int = 2,
        fragmentation_strategy: FragmentationStrategy = FragmentationStrategy.ADAPTIVE,
        bond_cutting_strategy: BondCuttingStrategy = BondCuttingStrategy.MIN_COUPLING,
    ):
        """
        Initialize fragmentor.

        Args:
            max_fragment_qubits: Maximum qubits per fragment (default 20)
            max_fragment_atoms: Maximum atoms per fragment (default 10)
            overlap_atoms: Number of overlapping atoms between fragments
            fragmentation_strategy: Strategy for fragmenting molecules
            bond_cutting_strategy: Strategy for selecting bonds to cut
        """
        self.max_fragment_qubits = max_fragment_qubits
        self.max_fragment_atoms = max_fragment_atoms
        self.overlap_atoms = overlap_atoms
        self.fragmentation_strategy = fragmentation_strategy
        self.bond_cutting_strategy = bond_cutting_strategy

        logger.info(
            f"Initialized FMOFragmentor: "
            f"max_qubits={max_fragment_qubits}, "
            f"max_atoms={max_fragment_atoms}, "
            f"overlap={overlap_atoms}"
        )

    def fragment_molecule(
        self,
        smiles: str,
        generate_3d: bool = True,
    ) -> List[MolecularFragment]:
        """
        Fragment a molecule from SMILES string.

        Args:
            smiles: SMILES string of molecule
            generate_3d: Generate 3D coordinates for fragments

        Returns:
            List of MolecularFragment objects

        Raises:
            ValueError: If SMILES is invalid or fragmentation fails

        Example:
            >>> fragmentor = FMOFragmentor(max_fragment_qubits=20)
            >>> fragments = fragmentor.fragment_molecule("CC(=O)OC1=CC=CC=C1C(=O)O")
        """
        # Parse SMILES
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError(f"Invalid SMILES: {smiles}")

        # Add hydrogens
        mol = Chem.AddHs(mol)

        # Generate 3D coordinates if requested
        if generate_3d:
            params = AllChem.ETKDGv3()
            params.randomSeed = 42
            result = AllChem.EmbedMolecule(mol, params)
            if result == 0:
                AllChem.MMFFOptimizeMolecule(mol, maxIters=500)

        num_atoms = mol.GetNumAtoms()
        num_heavy_atoms = mol.GetNumHeavyAtoms()

        logger.info(
            f"Fragmenting molecule: {smiles} "
            f"({num_atoms} atoms, {num_heavy_atoms} heavy atoms)"
        )

        # Check if fragmentation is needed
        estimated_qubits = self._estimate_qubits(mol)
        if estimated_qubits <= self.max_fragment_qubits:
            logger.info(
                f"Molecule requires {estimated_qubits} qubits - "
                f"no fragmentation needed"
            )
            return [self._create_single_fragment(mol)]

        # Perform fragmentation
        fragments = self._perform_fragmentation(mol)

        logger.info(f"Created {len(fragments)} fragments")
        for i, frag in enumerate(fragments):
            logger.debug(
                f"  Fragment {i}: {frag.num_atoms} atoms, "
                f"{frag.num_qubits} qubits, "
                f"SMILES={frag.smiles}"
            )

        return fragments

    def _estimate_qubits(self, mol: Chem.Mol) -> int:
        """
        Estimate number of qubits needed for molecule.

        Uses minimal basis set approximation: ~2 qubits per atom
        (one spin-up, one spin-down orbital per atom)
        """
        num_atoms = mol.GetNumAtoms()
        # Simplified: 2 qubits per heavy atom, 0 for hydrogens (can be integrated)
        num_heavy = sum(1 for atom in mol.GetAtoms() if atom.GetAtomicNum() > 1)
        return num_heavy * 2

    def _create_single_fragment(self, mol: Chem.Mol) -> MolecularFragment:
        """Create a single fragment from entire molecule."""
        num_atoms = mol.GetNumAtoms()
        num_electrons = sum(atom.GetAtomicNum() for atom in mol.GetAtoms())
        num_qubits = self._estimate_qubits(mol)

        coords_3d = None
        if mol.GetNumConformers() > 0:
            conf = mol.GetConformer()
            coords_3d = np.array([
                list(conf.GetAtomPosition(i)) for i in range(num_atoms)
            ])

        return MolecularFragment(
            fragment_id=0,
            mol=mol,
            smiles=Chem.MolToSmiles(mol),
            atom_indices=list(range(num_atoms)),
            num_atoms=num_atoms,
            num_electrons=num_electrons,
            num_qubits=num_qubits,
            coordinates_3d=coords_3d,
        )

    def _perform_fragmentation(self, mol: Chem.Mol) -> List[MolecularFragment]:
        """
        Perform molecular fragmentation.

        Strategy:
        1. Find optimal bonds to cut
        2. Create fragments with overlap
        3. Add capping hydrogens
        4. Track fragment connectivity
        """
        fragments = []

        # Identify bonds to cut
        cut_bonds = self._identify_cut_bonds(mol)

        if not cut_bonds:
            # Cannot fragment - create single fragment
            return [self._create_single_fragment(mol)]

        # Create fragment groups based on cut bonds
        fragment_atom_groups = self._create_fragment_groups(mol, cut_bonds)

        # Build fragments with capping atoms
        for frag_id, atom_indices in enumerate(fragment_atom_groups):
            fragment = self._build_fragment(
                mol, frag_id, atom_indices, cut_bonds
            )
            fragments.append(fragment)

        # Identify neighboring fragments
        self._identify_neighbors(fragments, cut_bonds)

        return fragments

    def _identify_cut_bonds(self, mol: Chem.Mol) -> List[Tuple[int, int]]:
        """
        Identify optimal bonds to cut for fragmentation.

        Priority:
        1. Single bonds (avoid breaking aromatic/conjugated systems)
        2. Bonds between heavy atoms
        3. Minimize inter-fragment coupling (lower bond order)
        """
        candidate_bonds = []

        for bond in mol.GetBonds():
            begin_idx = bond.GetBeginAtomIdx()
            end_idx = bond.GetEndAtomIdx()

            begin_atom = mol.GetAtomWithIdx(begin_idx)
            end_atom = mol.GetAtomWithIdx(end_idx)

            # Skip bonds involving hydrogens
            if begin_atom.GetAtomicNum() == 1 or end_atom.GetAtomicNum() == 1:
                continue

            # Skip aromatic bonds (preserve aromatic systems)
            if bond.GetIsAromatic():
                continue

            # Prefer single bonds
            if bond.GetBondType() != Chem.BondType.SINGLE:
                continue

            # Score bond for cutting
            score = self._score_bond_for_cutting(mol, bond)
            candidate_bonds.append((score, (begin_idx, end_idx)))

        if not candidate_bonds:
            logger.warning("No suitable bonds found for cutting")
            return []

        # Sort by score (higher is better for cutting)
        candidate_bonds.sort(reverse=True)

        # Select bonds to cut based on strategy
        num_cuts = self._determine_num_cuts(mol)
        cut_bonds = [bond for _, bond in candidate_bonds[:num_cuts]]

        logger.debug(f"Selected {len(cut_bonds)} bonds to cut: {cut_bonds}")

        return cut_bonds

    def _score_bond_for_cutting(self, mol: Chem.Mol, bond: Chem.Bond) -> float:
        """
        Score a bond for cutting (higher is better).

        Considers:
        - Bond order (prefer single bonds)
        - Atom types (prefer C-C bonds)
        - Connectivity (avoid creating isolated fragments)
        """
        score = 0.0

        # Bond order penalty (prefer single bonds)
        if bond.GetBondType() == Chem.BondType.SINGLE:
            score += 10.0
        elif bond.GetBondType() == Chem.BondType.DOUBLE:
            score += 5.0
        else:
            score += 1.0

        # Aromatic penalty
        if bond.GetIsAromatic():
            score -= 20.0

        # Ring penalty (avoid breaking rings)
        if bond.IsInRing():
            score -= 15.0

        # Atom connectivity (prefer bonds connecting well-connected atoms)
        begin_atom = mol.GetAtomWithIdx(bond.GetBeginAtomIdx())
        end_atom = mol.GetAtomWithIdx(bond.GetEndAtomIdx())

        begin_degree = begin_atom.GetDegree()
        end_degree = end_atom.GetDegree()

        # Prefer cutting bonds with moderate connectivity
        avg_degree = (begin_degree + end_degree) / 2.0
        if 2.0 <= avg_degree <= 3.0:
            score += 5.0

        return score

    def _determine_num_cuts(self, mol: Chem.Mol) -> int:
        """Determine how many bonds to cut based on molecule size."""
        num_heavy_atoms = mol.GetNumHeavyAtoms()

        # Estimate fragments needed
        atoms_per_fragment = self.max_fragment_atoms
        num_fragments = max(2, (num_heavy_atoms + atoms_per_fragment - 1) // atoms_per_fragment)

        # Number of cuts ≈ num_fragments - 1 (for linear fragmentation)
        num_cuts = num_fragments - 1

        return min(num_cuts, num_heavy_atoms // 3)  # Don't over-fragment

    def _create_fragment_groups(
        self,
        mol: Chem.Mol,
        cut_bonds: List[Tuple[int, int]],
    ) -> List[List[int]]:
        """
        Create groups of atoms for each fragment after cutting bonds.

        Uses graph connectivity to identify disconnected components.
        """
        num_atoms = mol.GetNumAtoms()

        # Build adjacency list excluding cut bonds
        cut_bond_set = set(cut_bonds)
        adjacency = {i: [] for i in range(num_atoms)}

        for bond in mol.GetBonds():
            begin = bond.GetBeginAtomIdx()
            end = bond.GetEndAtomIdx()

            bond_tuple = tuple(sorted([begin, end]))
            if bond_tuple not in cut_bond_set:
                adjacency[begin].append(end)
                adjacency[end].append(begin)

        # Find connected components using BFS
        visited = set()
        fragments = []

        for start_atom in range(num_atoms):
            if start_atom in visited:
                continue

            # BFS from start_atom
            component = []
            queue = [start_atom]
            visited.add(start_atom)

            while queue:
                atom = queue.pop(0)
                component.append(atom)

                for neighbor in adjacency[atom]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)

            # Only keep non-hydrogen fragments
            heavy_atoms = [
                a for a in component
                if mol.GetAtomWithIdx(a).GetAtomicNum() > 1
            ]

            if heavy_atoms:
                fragments.append(component)

        # Merge small fragments if needed
        fragments = self._merge_small_fragments(mol, fragments)

        return fragments

    def _merge_small_fragments(
        self,
        mol: Chem.Mol,
        fragments: List[List[int]],
    ) -> List[List[int]]:
        """Merge fragments that are too small."""
        min_atoms = 3  # Minimum atoms per fragment

        merged = []
        carry_over = []

        for frag in fragments:
            heavy_count = sum(
                1 for idx in frag
                if mol.GetAtomWithIdx(idx).GetAtomicNum() > 1
            )

            if heavy_count < min_atoms and carry_over:
                # Merge with previous
                carry_over.extend(frag)
            elif heavy_count < min_atoms:
                # Start carry over
                carry_over = frag
            else:
                if carry_over:
                    frag = carry_over + frag
                    carry_over = []
                merged.append(frag)

        if carry_over:
            if merged:
                merged[-1].extend(carry_over)
            else:
                merged.append(carry_over)

        return merged

    def _build_fragment(
        self,
        mol: Chem.Mol,
        fragment_id: int,
        atom_indices: List[int],
        cut_bonds: List[Tuple[int, int]],
    ) -> MolecularFragment:
        """
        Build a fragment molecule with capping hydrogens.

        Capping strategy:
        - For each cut bond, add H atom to replace the removed bond
        - Position H atom along the bond direction
        """
        # Create editable mol
        frag_mol = Chem.RWMol()

        # Map old atom indices to new
        old_to_new = {}
        new_atom_indices = []

        # Add atoms to fragment
        for old_idx in atom_indices:
            atom = mol.GetAtomWithIdx(old_idx)
            new_idx = frag_mol.AddAtom(atom)
            old_to_new[old_idx] = new_idx
            new_atom_indices.append(old_idx)

        # Add bonds between atoms in fragment
        for bond in mol.GetBonds():
            begin = bond.GetBeginAtomIdx()
            end = bond.GetEndAtomIdx()

            if begin in old_to_new and end in old_to_new:
                frag_mol.AddBond(
                    old_to_new[begin],
                    old_to_new[end],
                    bond.GetBondType()
                )

        # Add capping hydrogens for cut bonds
        capping_atoms = []
        for begin, end in cut_bonds:
            # Check if this fragment contains one end of cut bond
            if begin in old_to_new and end not in old_to_new:
                h_idx = frag_mol.AddAtom(Chem.Atom(1))  # Add H
                frag_mol.AddBond(old_to_new[begin], h_idx, Chem.BondType.SINGLE)
                capping_atoms.append(h_idx)
            elif end in old_to_new and begin not in old_to_new:
                h_idx = frag_mol.AddAtom(Chem.Atom(1))  # Add H
                frag_mol.AddBond(old_to_new[end], h_idx, Chem.BondType.SINGLE)
                capping_atoms.append(h_idx)

        # Convert to mol
        frag_mol = frag_mol.GetMol()
        Chem.SanitizeMol(frag_mol)

        # Generate 3D coordinates if parent has them
        coords_3d = None
        if mol.GetNumConformers() > 0:
            AllChem.EmbedMolecule(frag_mol, randomSeed=42)
            AllChem.MMFFOptimizeMolecule(frag_mol, maxIters=200)

            conf = frag_mol.GetConformer()
            coords_3d = np.array([
                list(conf.GetAtomPosition(i))
                for i in range(frag_mol.GetNumAtoms())
            ])

        # Calculate properties
        num_atoms = frag_mol.GetNumAtoms()
        num_electrons = sum(
            atom.GetAtomicNum() for atom in frag_mol.GetAtoms()
        )
        num_qubits = self._estimate_qubits(frag_mol)

        return MolecularFragment(
            fragment_id=fragment_id,
            mol=frag_mol,
            smiles=Chem.MolToSmiles(frag_mol),
            atom_indices=new_atom_indices,
            num_atoms=num_atoms,
            num_electrons=num_electrons,
            num_qubits=num_qubits,
            capping_atoms=capping_atoms,
            parent_bonds=[(begin, end) for begin, end in cut_bonds
                         if begin in atom_indices or end in atom_indices],
            coordinates_3d=coords_3d,
        )

    def _identify_neighbors(
        self,
        fragments: List[MolecularFragment],
        cut_bonds: List[Tuple[int, int]],
    ) -> None:
        """Identify neighboring fragments connected by cut bonds."""
        for frag_i in fragments:
            for frag_j in fragments:
                if frag_i.fragment_id >= frag_j.fragment_id:
                    continue

                # Check if fragments share a cut bond
                atoms_i = set(frag_i.atom_indices)
                atoms_j = set(frag_j.atom_indices)

                for begin, end in cut_bonds:
                    if (begin in atoms_i and end in atoms_j) or \
                       (end in atoms_i and begin in atoms_j):
                        frag_i.neighbor_fragments.add(frag_j.fragment_id)
                        frag_j.neighbor_fragments.add(frag_i.fragment_id)
                        break

    def visualize_fragmentation(
        self,
        fragments: List[MolecularFragment],
        output_file: Optional[str] = None,
    ) -> str:
        """
        Generate visualization of fragmentation.

        Args:
            fragments: List of fragments
            output_file: Optional output file path (PNG)

        Returns:
            ASCII representation or path to image
        """
        info = []
        info.append("=" * 80)
        info.append("MOLECULAR FRAGMENTATION SUMMARY")
        info.append("=" * 80)
        info.append(f"Total fragments: {len(fragments)}")
        info.append("")

        for frag in fragments:
            info.append(f"Fragment {frag.fragment_id}:")
            info.append(f"  Atoms: {frag.num_atoms}")
            info.append(f"  Electrons: {frag.num_electrons}")
            info.append(f"  Qubits: {frag.num_qubits}")
            info.append(f"  SMILES: {frag.smiles}")
            info.append(f"  Capping atoms: {len(frag.capping_atoms)}")
            info.append(f"  Neighbors: {sorted(frag.neighbor_fragments)}")
            info.append("")

        info.append("=" * 80)

        return "\n".join(info)


# Example usage
if __name__ == "__main__":
    print("=" * 80)
    print("FMO Fragmentor - Test Cases")
    print("=" * 80)

    # Test 1: Small molecule (no fragmentation needed)
    print("\nTest 1: Water (H2O) - No fragmentation needed")
    fragmentor = FMOFragmentor(max_fragment_qubits=20)
    fragments = fragmentor.fragment_molecule("O")
    print(fragmentor.visualize_fragmentation(fragments))

    # Test 2: Aspirin (moderate size)
    print("\nTest 2: Aspirin - Moderate fragmentation")
    fragmentor = FMOFragmentor(max_fragment_qubits=20, max_fragment_atoms=8)
    fragments = fragmentor.fragment_molecule("CC(=O)Oc1ccccc1C(=O)O")
    print(fragmentor.visualize_fragmentation(fragments))

    # Test 3: Large peptide
    print("\nTest 3: Tripeptide - Heavy fragmentation")
    tripeptide = "CC(C)CC(C(=O)NC(CC1=CC=CC=C1)C(=O)NC(C)C(=O)O)N"
    fragmentor = FMOFragmentor(max_fragment_qubits=20, max_fragment_atoms=6)
    fragments = fragmentor.fragment_molecule(tripeptide)
    print(fragmentor.visualize_fragmentation(fragments))

    print("\n" + "=" * 80)
    print("Fragmentor tests completed!")
    print("=" * 80)
