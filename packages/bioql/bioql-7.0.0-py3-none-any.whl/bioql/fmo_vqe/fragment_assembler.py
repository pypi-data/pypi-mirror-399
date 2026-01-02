# Copyright 2024-2025 SpectrixRD
# Licensed under the Apache License, Version 2.0
# See LICENSE file in the project root for full license text

"""
Fragment Assembler Module
==========================

Assembles fragment energies into total molecular energy with coupling corrections.

FMO-VQE Energy Assembly:
-----------------------
E_total = Σ E_i + Σ ΔE_ij + higher_order_terms

Where:
- E_i: Fragment i ground state energy
- ΔE_ij: Pair coupling correction between fragments i,j
- higher_order_terms: Three-body and higher corrections (optional)

Reference:
- Scientific Reports (2024) - FMO-VQE methodology
- Fedorov, D.G. & Kitaura, K. (2007) The Fragment Molecular Orbital Method

Author: BioQL Team
Version: 1.0.0
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from .fragment_vqe import FragmentVQEResult
from .fragmentor import MolecularFragment


@dataclass
class FragmentCoupling:
    """
    Represents coupling between two fragments.

    Attributes:
        fragment_i: First fragment ID
        fragment_j: Second fragment ID
        coupling_energy: Coupling energy correction (Hartree)
        method: Method used to compute coupling
        distance: Distance between fragment centers (Angstrom)
    """
    fragment_i: int
    fragment_j: int
    coupling_energy: float
    method: str
    distance: Optional[float] = None


@dataclass
class AssembledResult:
    """
    Result from fragment energy assembly.

    Attributes:
        total_energy: Total molecular energy (Hartree)
        fragment_energies: Individual fragment energies
        coupling_energies: Pairwise coupling corrections
        num_fragments: Number of fragments
        error_estimate: Estimated error in total energy
        success: Whether assembly succeeded
        metadata: Additional information
    """
    total_energy: float
    fragment_energies: List[float]
    coupling_energies: Dict[Tuple[int, int], float]
    num_fragments: int
    error_estimate: Optional[float] = None
    success: bool = True
    metadata: Optional[Dict] = None

    def __repr__(self) -> str:
        return (
            f"AssembledResult(E_total={self.total_energy:.6f} Ha, "
            f"fragments={self.num_fragments}, "
            f"error~{self.error_estimate:.6f} Ha)"
        )


class FragmentAssembler:
    """
    Assembles fragment VQE results into total molecular energy.

    Uses FMO (Fragment Molecular Orbital) methodology to combine
    fragment energies with coupling corrections.
    """

    def __init__(
        self,
        coupling_method: str = "electrostatic",
        include_three_body: bool = False,
        coupling_threshold: float = 10.0,
    ):
        """
        Initialize fragment assembler.

        Args:
            coupling_method: Method for computing coupling
                - 'electrostatic': Electrostatic approximation
                - 'dimer': Full dimer calculation (expensive)
                - 'screening': Include screening effects
            include_three_body: Include three-body corrections
            coupling_threshold: Distance threshold for coupling (Angstrom)
        """
        self.coupling_method = coupling_method
        self.include_three_body = include_three_body
        self.coupling_threshold = coupling_threshold

        logger.info(
            f"Initialized FragmentAssembler: "
            f"method={coupling_method}, "
            f"three_body={include_three_body}"
        )

    def assemble_energy(
        self,
        fragment_results: List[FragmentVQEResult],
        fragments: Optional[List[MolecularFragment]] = None,
    ) -> AssembledResult:
        """
        Assemble total molecular energy from fragment results.

        Args:
            fragment_results: List of fragment VQE results
            fragments: Optional list of fragment objects (for coupling)

        Returns:
            AssembledResult with total energy and breakdown

        Example:
            >>> assembler = FragmentAssembler()
            >>> result = assembler.assemble_energy(fragment_results)
            >>> print(f"Total energy: {result.total_energy:.6f} Hartree")
        """
        logger.info(f"Assembling energy from {len(fragment_results)} fragments")

        # Extract fragment energies
        fragment_energies = [
            res.ground_state_energy for res in fragment_results
        ]

        # Sum fragment energies
        sum_fragment_energies = sum(fragment_energies)

        logger.debug(
            f"Sum of fragment energies: {sum_fragment_energies:.6f} Hartree"
        )

        # Compute coupling corrections
        coupling_energies = {}

        if fragments is not None:
            couplings = self._compute_couplings(
                fragment_results, fragments
            )

            for coupling in couplings:
                key = (coupling.fragment_i, coupling.fragment_j)
                coupling_energies[key] = coupling.coupling_energy

        sum_coupling = sum(coupling_energies.values())

        logger.debug(
            f"Sum of coupling corrections: {sum_coupling:.6f} Hartree "
            f"({len(coupling_energies)} pairs)"
        )

        # Total energy
        total_energy = sum_fragment_energies + sum_coupling

        # Error estimate
        error_estimate = self._estimate_error(
            fragment_results, coupling_energies
        )

        logger.info(
            f"Assembled total energy: {total_energy:.6f} ± "
            f"{error_estimate:.6f} Hartree"
        )

        return AssembledResult(
            total_energy=total_energy,
            fragment_energies=fragment_energies,
            coupling_energies=coupling_energies,
            num_fragments=len(fragment_results),
            error_estimate=error_estimate,
            success=all(res.success for res in fragment_results),
            metadata={
                "sum_fragments": sum_fragment_energies,
                "sum_couplings": sum_coupling,
                "coupling_method": self.coupling_method,
            },
        )

    def _compute_couplings(
        self,
        fragment_results: List[FragmentVQEResult],
        fragments: List[MolecularFragment],
    ) -> List[FragmentCoupling]:
        """
        Compute pairwise coupling corrections between fragments.

        Methods:
        1. Electrostatic: Coulombic interaction between fragments
        2. Dimer: Full VQE calculation of fragment dimer
        3. Screening: Include polarization screening
        """
        couplings = []

        # Build fragment lookup
        frag_lookup = {f.fragment_id: f for f in fragments}
        result_lookup = {r.fragment_id: r for r in fragment_results}

        # Compute couplings for neighboring fragments
        for frag in fragments:
            for neighbor_id in frag.neighbor_fragments:
                if frag.fragment_id >= neighbor_id:
                    continue  # Avoid duplicates

                neighbor = frag_lookup.get(neighbor_id)
                if neighbor is None:
                    continue

                # Compute coupling
                if self.coupling_method == "electrostatic":
                    coupling_energy = self._electrostatic_coupling(
                        frag, neighbor
                    )
                elif self.coupling_method == "dimer":
                    coupling_energy = self._dimer_coupling(
                        frag, neighbor,
                        result_lookup.get(frag.fragment_id),
                        result_lookup.get(neighbor_id),
                    )
                else:
                    coupling_energy = 0.0

                # Compute distance between fragments
                distance = self._fragment_distance(frag, neighbor)

                # Apply distance threshold
                if distance > self.coupling_threshold:
                    logger.debug(
                        f"Coupling {frag.fragment_id}-{neighbor_id} "
                        f"beyond threshold ({distance:.2f} Å)"
                    )
                    continue

                coupling = FragmentCoupling(
                    fragment_i=frag.fragment_id,
                    fragment_j=neighbor_id,
                    coupling_energy=coupling_energy,
                    method=self.coupling_method,
                    distance=distance,
                )

                couplings.append(coupling)

                logger.debug(
                    f"Coupling {frag.fragment_id}-{neighbor_id}: "
                    f"{coupling_energy:.6f} Hartree (d={distance:.2f} Å)"
                )

        return couplings

    def _electrostatic_coupling(
        self,
        frag_i: MolecularFragment,
        frag_j: MolecularFragment,
    ) -> float:
        """
        Compute electrostatic coupling between fragments.

        Uses Coulomb's law with atomic partial charges:
        E_coupling = k Σ_i Σ_j (q_i * q_j / r_ij)
        """
        if frag_i.coordinates_3d is None or frag_j.coordinates_3d is None:
            logger.warning("No 3D coordinates - using zero coupling")
            return 0.0

        # Constants
        COULOMB_CONSTANT = 332.0636  # kcal/(mol·Å·e²)
        HARTREE_TO_KCALMOL = 627.509  # kcal/mol per Hartree
        DIELECTRIC = 4.0  # Protein-like dielectric

        coupling_energy = 0.0

        # Simplified: uniform charge distribution
        charge_i = -1.0 / frag_i.num_atoms  # Distribute charge
        charge_j = -1.0 / frag_j.num_atoms

        for coord_i in frag_i.coordinates_3d:
            for coord_j in frag_j.coordinates_3d:
                r_ij = np.linalg.norm(coord_i - coord_j)

                if r_ij < 0.5:
                    r_ij = 0.5  # Avoid singularity

                # Coulomb interaction
                coulomb = COULOMB_CONSTANT * charge_i * charge_j / (DIELECTRIC * r_ij)
                coupling_energy += coulomb

        # Convert to Hartree
        coupling_energy /= HARTREE_TO_KCALMOL

        return coupling_energy

    def _dimer_coupling(
        self,
        frag_i: MolecularFragment,
        frag_j: MolecularFragment,
        result_i: Optional[FragmentVQEResult],
        result_j: Optional[FragmentVQEResult],
    ) -> float:
        """
        Compute coupling using dimer calculation.

        ΔE_ij = E(i+j) - E(i) - E(j)

        Note: This requires a full VQE calculation on the dimer,
        which can be expensive.
        """
        logger.warning(
            "Dimer coupling calculation not yet implemented - "
            "using electrostatic approximation"
        )
        return self._electrostatic_coupling(frag_i, frag_j)

    def _fragment_distance(
        self,
        frag_i: MolecularFragment,
        frag_j: MolecularFragment,
    ) -> float:
        """Compute distance between fragment centers."""
        if frag_i.coordinates_3d is None or frag_j.coordinates_3d is None:
            return 0.0

        center_i = np.mean(frag_i.coordinates_3d, axis=0)
        center_j = np.mean(frag_j.coordinates_3d, axis=0)

        return float(np.linalg.norm(center_i - center_j))

    def _estimate_error(
        self,
        fragment_results: List[FragmentVQEResult],
        coupling_energies: Dict[Tuple[int, int], float],
    ) -> float:
        """
        Estimate total error in assembled energy.

        Error sources:
        1. VQE convergence error (from convergence history)
        2. Fragmentation error (neglected higher-order terms)
        3. Coupling approximation error
        """
        # VQE convergence error
        vqe_errors = []
        for result in fragment_results:
            if len(result.vqe_result.convergence_history) > 5:
                # Estimate error from convergence stability
                history = result.vqe_result.convergence_history[-5:]
                std_dev = np.std(history)
                vqe_errors.append(std_dev)

        vqe_error = np.sqrt(sum(e**2 for e in vqe_errors)) if vqe_errors else 0.0

        # Fragmentation error (heuristic: ~1% of coupling energy)
        coupling_error = 0.01 * abs(sum(coupling_energies.values()))

        # Three-body error (neglected terms)
        three_body_error = 0.0
        if not self.include_three_body:
            # Heuristic: ~0.1% of total fragment energy
            total_frag_energy = sum(r.ground_state_energy for r in fragment_results)
            three_body_error = 0.001 * abs(total_frag_energy)

        # Total error (combine in quadrature)
        total_error = np.sqrt(
            vqe_error**2 + coupling_error**2 + three_body_error**2
        )

        return float(total_error)

    def generate_report(
        self,
        result: AssembledResult,
        fragment_results: List[FragmentVQEResult],
    ) -> str:
        """
        Generate detailed report of energy assembly.

        Args:
            result: Assembled result
            fragment_results: Individual fragment results

        Returns:
            Formatted report string
        """
        lines = []
        lines.append("=" * 80)
        lines.append("FMO-VQE ENERGY ASSEMBLY REPORT")
        lines.append("=" * 80)
        lines.append("")

        # Summary
        lines.append("SUMMARY")
        lines.append("-" * 80)
        lines.append(f"Total Energy:        {result.total_energy:>12.6f} Hartree")
        lines.append(f"Error Estimate:      {result.error_estimate:>12.6f} Hartree")
        lines.append(f"Number of Fragments: {result.num_fragments:>12}")
        lines.append(f"Coupling Method:     {self.coupling_method:>12}")
        lines.append("")

        # Fragment breakdown
        lines.append("FRAGMENT ENERGIES")
        lines.append("-" * 80)
        for i, (energy, res) in enumerate(zip(result.fragment_energies, fragment_results)):
            lines.append(
                f"Fragment {i:2d}: {energy:>12.6f} Ha  "
                f"({res.num_qubits:2d} qubits, "
                f"{res.computation_time:>6.2f}s, "
                f"{'✓' if res.success else '✗'})"
            )

        sum_fragments = sum(result.fragment_energies)
        lines.append("-" * 80)
        lines.append(f"Sum:         {sum_fragments:>12.6f} Ha")
        lines.append("")

        # Coupling corrections
        lines.append("COUPLING CORRECTIONS")
        lines.append("-" * 80)
        if result.coupling_energies:
            for (i, j), energy in sorted(result.coupling_energies.items()):
                lines.append(f"Fragments {i:2d}-{j:2d}: {energy:>12.6f} Ha")

            sum_couplings = sum(result.coupling_energies.values())
            lines.append("-" * 80)
            lines.append(f"Sum:              {sum_couplings:>12.6f} Ha")
        else:
            lines.append("No coupling corrections computed")

        lines.append("")

        # Totals
        lines.append("TOTAL ENERGY BREAKDOWN")
        lines.append("-" * 80)
        lines.append(f"Fragment Energies:     {sum_fragments:>12.6f} Ha")
        lines.append(f"Coupling Corrections:  {sum(result.coupling_energies.values()):>12.6f} Ha")
        lines.append("-" * 80)
        lines.append(f"TOTAL:                 {result.total_energy:>12.6f} Ha")
        lines.append(f"                       ± {result.error_estimate:>10.6f} Ha")
        lines.append("")

        lines.append("=" * 80)

        return "\n".join(lines)


# Example usage
if __name__ == "__main__":
    from .fragmentor import FMOFragmentor
    from .fragment_vqe import FragmentVQESolver

    print("=" * 80)
    print("Fragment Assembler - Test Cases")
    print("=" * 80)

    # Test 1: Water (single fragment)
    print("\nTest 1: Water molecule (single fragment)")
    fragmentor = FMOFragmentor()
    fragments = fragmentor.fragment_molecule("O")

    solver = FragmentVQESolver(maxiter=50)
    results = solver.solve_fragments(fragments)

    assembler = FragmentAssembler()
    assembled = assembler.assemble_energy(results, fragments)

    print(assembler.generate_report(assembled, results))

    # Test 2: Aspirin (multiple fragments)
    print("\nTest 2: Aspirin (fragmented)")
    fragmentor = FMOFragmentor(max_fragment_qubits=16, max_fragment_atoms=6)
    fragments = fragmentor.fragment_molecule("CC(=O)Oc1ccccc1C(=O)O")

    results = solver.solve_fragments(fragments)
    assembled = assembler.assemble_energy(results, fragments)

    print(assembler.generate_report(assembled, results))

    print("\n" + "=" * 80)
    print("Fragment assembler tests completed!")
    print("=" * 80)
