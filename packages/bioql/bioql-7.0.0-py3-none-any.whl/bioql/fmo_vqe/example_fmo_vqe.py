#!/usr/bin/env python3
# Copyright 2024-2025 SpectrixRD
# Licensed under the Apache License, Version 2.0
# See LICENSE file in the project root for full license text

"""
FMO-VQE Example: Aspirin Molecule
==================================

Complete workflow demonstrating Fragment Molecular Orbital VQE for aspirin.

Workflow:
1. Fragment aspirin molecule (C9H8O4, ~25 atoms → 50 qubits)
2. Solve each fragment with VQE
3. Assemble total molecular energy
4. Validate results and estimate error

Expected Results:
- 2-3 fragments with <20 qubits each
- Total energy: ~-500 to -600 Hartree (approximate)
- Error: <0.1 Hartree

Author: BioQL Team
Version: 1.0.0
"""

import time
from pathlib import Path

from bioql.fmo_vqe import (
    FMOFragmentor,
    FragmentVQESolver,
    FragmentAssembler,
)


def main():
    """Run complete FMO-VQE workflow for aspirin."""
    print("=" * 80)
    print("FMO-VQE EXAMPLE: ASPIRIN MOLECULE")
    print("=" * 80)
    print()

    # Aspirin SMILES
    aspirin_smiles = "CC(=O)Oc1ccccc1C(=O)O"

    print("Molecule: Aspirin (C9H8O4)")
    print(f"SMILES: {aspirin_smiles}")
    print()

    # =========================================================================
    # STEP 1: FRAGMENTATION
    # =========================================================================
    print("-" * 80)
    print("STEP 1: MOLECULAR FRAGMENTATION")
    print("-" * 80)

    fragmentor = FMOFragmentor(
        max_fragment_qubits=20,      # Max 20 qubits per fragment
        max_fragment_atoms=8,         # Max 8 heavy atoms per fragment
        overlap_atoms=2,              # 2 atoms overlap between fragments
        fragmentation_strategy="ADAPTIVE",
        bond_cutting_strategy="MIN_COUPLING",
    )

    print("Fragmentor settings:")
    print(f"  Max qubits per fragment: {fragmentor.max_fragment_qubits}")
    print(f"  Max atoms per fragment: {fragmentor.max_fragment_atoms}")
    print(f"  Overlap atoms: {fragmentor.overlap_atoms}")
    print()

    start_time = time.time()
    fragments = fragmentor.fragment_molecule(aspirin_smiles, generate_3d=True)
    frag_time = time.time() - start_time

    print(f"Fragmentation completed in {frag_time:.3f}s")
    print()

    # Display fragmentation summary
    print(fragmentor.visualize_fragmentation(fragments))

    # =========================================================================
    # STEP 2: FRAGMENT VQE SOLVING
    # =========================================================================
    print("-" * 80)
    print("STEP 2: VQE OPTIMIZATION FOR EACH FRAGMENT")
    print("-" * 80)

    solver = FragmentVQESolver(
        ansatz="RealAmplitudes",      # Ansatz type
        optimizer="COBYLA",            # Classical optimizer
        num_layers=2,                  # Ansatz depth
        shots=1024,                    # Measurement shots
        maxiter=100,                   # Max optimization iterations
        use_cache=True,                # Enable result caching
    )

    print("VQE solver settings:")
    print(f"  Ansatz: {solver.ansatz}")
    print(f"  Optimizer: {solver.optimizer}")
    print(f"  Layers: {solver.num_layers}")
    print(f"  Shots: {solver.shots}")
    print(f"  Max iterations: {solver.maxiter}")
    print()

    print("Solving fragments...")
    start_time = time.time()
    fragment_results = solver.solve_fragments(fragments, parallel=False)
    solve_time = time.time() - start_time

    print(f"\nVQE solving completed in {solve_time:.2f}s")
    print()

    # Display fragment results
    print("Fragment VQE Results:")
    print("-" * 80)
    for res in fragment_results:
        status = "✓" if res.success else "✗"
        cache_str = " (from cache)" if res.cache_hit else ""
        print(
            f"{status} Fragment {res.fragment_id}: "
            f"E = {res.ground_state_energy:>10.6f} Hartree, "
            f"Qubits = {res.num_qubits:2d}, "
            f"Time = {res.computation_time:>6.2f}s{cache_str}"
        )

    print()

    # =========================================================================
    # STEP 3: ENERGY ASSEMBLY
    # =========================================================================
    print("-" * 80)
    print("STEP 3: ENERGY ASSEMBLY WITH COUPLING CORRECTIONS")
    print("-" * 80)

    assembler = FragmentAssembler(
        coupling_method="electrostatic",   # Use electrostatic coupling
        include_three_body=False,          # Skip 3-body terms (faster)
        coupling_threshold=10.0,           # 10 Å coupling cutoff
    )

    print("Assembler settings:")
    print(f"  Coupling method: {assembler.coupling_method}")
    print(f"  Three-body terms: {assembler.include_three_body}")
    print(f"  Coupling threshold: {assembler.coupling_threshold} Å")
    print()

    start_time = time.time()
    assembled = assembler.assemble_energy(fragment_results, fragments)
    assembly_time = time.time() - start_time

    print(f"Assembly completed in {assembly_time:.3f}s")
    print()

    # Display assembly report
    report = assembler.generate_report(assembled, fragment_results)
    print(report)

    # =========================================================================
    # STEP 4: RESULTS SUMMARY
    # =========================================================================
    print()
    print("=" * 80)
    print("FINAL RESULTS SUMMARY")
    print("=" * 80)
    print()

    total_time = frag_time + solve_time + assembly_time

    print(f"Total Molecular Energy: {assembled.total_energy:.6f} ± "
          f"{assembled.error_estimate:.6f} Hartree")
    print()
    print("Performance Metrics:")
    print(f"  Fragmentation time:  {frag_time:>8.3f}s")
    print(f"  VQE solving time:    {solve_time:>8.2f}s")
    print(f"  Assembly time:       {assembly_time:>8.3f}s")
    print(f"  Total time:          {total_time:>8.2f}s")
    print()

    print("Fragment Statistics:")
    print(f"  Number of fragments: {assembled.num_fragments}")
    print(f"  Average qubits/frag: {sum(f.num_qubits for f in fragments) / len(fragments):.1f}")
    print(f"  Max qubits/fragment: {max(f.num_qubits for f in fragments)}")
    print()

    print("Energy Breakdown:")
    print(f"  Sum of fragments:    {sum(assembled.fragment_energies):>12.6f} Ha")
    print(f"  Coupling correction: {sum(assembled.coupling_energies.values()):>12.6f} Ha")
    print(f"  Total energy:        {assembled.total_energy:>12.6f} Ha")
    print(f"  Estimated error:     {assembled.error_estimate:>12.6f} Ha")
    print()

    # Success criteria
    success_criteria = [
        ("All fragments solved", all(r.success for r in fragment_results)),
        ("Max qubits < 20", max(f.num_qubits for f in fragments) <= 20),
        ("Error < 0.1 Ha", assembled.error_estimate < 0.1),
        ("Solve time < 5 min/frag", solve_time / len(fragments) < 300),
    ]

    print("Success Criteria:")
    for criterion, passed in success_criteria:
        status = "✓" if passed else "✗"
        print(f"  {status} {criterion}")

    all_passed = all(passed for _, passed in success_criteria)
    print()

    if all_passed:
        print("✓ ALL SUCCESS CRITERIA MET!")
    else:
        print("✗ SOME SUCCESS CRITERIA NOT MET")

    print()
    print("=" * 80)

    return assembled


if __name__ == "__main__":
    result = main()
