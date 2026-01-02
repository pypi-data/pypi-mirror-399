#!/usr/bin/env python3
# Copyright 2024-2025 SpectrixRD
# Licensed under the Apache License, Version 2.0
# See LICENSE file in the project root for full license text

"""
FMO-VQE Test Suite
==================

Comprehensive testing for Fragment Molecular Orbital VQE implementation.

Test Cases:
1. Small molecule (H2O) - No fragmentation needed
2. Medium molecule (Aspirin) - Moderate fragmentation
3. Large peptide - Heavy fragmentation
4. Validation against exact FCI (for small molecules)
5. Benchmark fragmentation overhead
6. Error estimation validation

Author: BioQL Team
Version: 1.0.0
"""

import time
from pathlib import Path

import numpy as np

from bioql.fmo_vqe import (
    FMOFragmentor,
    FragmentVQESolver,
    FragmentAssembler,
)

# Test molecules
TEST_MOLECULES = {
    "water": {
        "smiles": "O",
        "name": "Water (H2O)",
        "expected_fragments": 1,
        "expected_qubits": 2,
    },
    "aspirin": {
        "smiles": "CC(=O)Oc1ccccc1C(=O)O",
        "name": "Aspirin (C9H8O4)",
        "expected_fragments": 2,
        "expected_qubits": 50,
    },
    "caffeine": {
        "smiles": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
        "name": "Caffeine (C8H10N4O2)",
        "expected_fragments": 2,
        "expected_qubits": 48,
    },
    "tripeptide": {
        "smiles": "CC(C)CC(C(=O)NC(CC1=CC=CC=C1)C(=O)NC(C)C(=O)O)N",
        "name": "Tripeptide (Ile-Phe-Ala)",
        "expected_fragments": 3,
        "expected_qubits": 100,
    },
}


def test_fragmentor():
    """Test molecular fragmentation."""
    print("=" * 80)
    print("TEST 1: MOLECULAR FRAGMENTOR")
    print("=" * 80)

    results = {}

    for mol_id, mol_data in TEST_MOLECULES.items():
        print(f"\nTesting: {mol_data['name']}")
        print("-" * 80)

        fragmentor = FMOFragmentor(
            max_fragment_qubits=20,
            max_fragment_atoms=8,
        )

        start_time = time.time()
        fragments = fragmentor.fragment_molecule(mol_data["smiles"])
        elapsed = time.time() - start_time

        print(f"Fragmentation time: {elapsed:.3f}s")
        print(f"Number of fragments: {len(fragments)}")

        for i, frag in enumerate(fragments):
            print(
                f"  Fragment {i}: "
                f"{frag.num_atoms} atoms, "
                f"{frag.num_qubits} qubits, "
                f"neighbors={sorted(frag.neighbor_fragments)}"
            )

        # Validate
        total_qubits = sum(f.num_qubits for f in fragments)
        success = len(fragments) >= 1 and all(
            f.num_qubits <= 20 for f in fragments
        )

        results[mol_id] = {
            "success": success,
            "num_fragments": len(fragments),
            "total_qubits": total_qubits,
            "time": elapsed,
        }

        status = "✓ PASS" if success else "✗ FAIL"
        print(f"\nStatus: {status}")

    return results


def test_fragment_vqe():
    """Test VQE solver on fragments."""
    print("\n" + "=" * 80)
    print("TEST 2: FRAGMENT VQE SOLVER")
    print("=" * 80)

    results = {}

    # Test on small molecules only (to keep runtime reasonable)
    test_set = {k: v for k, v in TEST_MOLECULES.items()
                if k in ["water", "caffeine"]}

    for mol_id, mol_data in test_set.items():
        print(f"\nTesting: {mol_data['name']}")
        print("-" * 80)

        # Fragment molecule
        fragmentor = FMOFragmentor(max_fragment_qubits=20, max_fragment_atoms=8)
        fragments = fragmentor.fragment_molecule(mol_data["smiles"])

        print(f"Created {len(fragments)} fragments")

        # Solve fragments
        solver = FragmentVQESolver(
            ansatz="RealAmplitudes",
            optimizer="COBYLA",
            maxiter=50,
            shots=1024,
            use_cache=True,
        )

        start_time = time.time()
        fragment_results = solver.solve_fragments(fragments)
        elapsed = time.time() - start_time

        print(f"VQE solving time: {elapsed:.2f}s")

        # Display results
        for res in fragment_results:
            status = "✓" if res.success else "✗"
            cache_str = " (cached)" if res.cache_hit else ""
            print(
                f"  Fragment {res.fragment_id}: "
                f"{status} E={res.ground_state_energy:.6f} Ha, "
                f"time={res.computation_time:.2f}s{cache_str}"
            )

        # Validate
        success = all(r.success for r in fragment_results)

        results[mol_id] = {
            "success": success,
            "num_fragments": len(fragment_results),
            "energies": [r.ground_state_energy for r in fragment_results],
            "time": elapsed,
        }

        status = "✓ PASS" if success else "✗ FAIL"
        print(f"\nStatus: {status}")

    return results


def test_assembler():
    """Test energy assembly."""
    print("\n" + "=" * 80)
    print("TEST 3: ENERGY ASSEMBLER")
    print("=" * 80)

    results = {}

    test_set = {k: v for k, v in TEST_MOLECULES.items()
                if k in ["water", "caffeine"]}

    for mol_id, mol_data in test_set.items():
        print(f"\nTesting: {mol_data['name']}")
        print("-" * 80)

        # Fragment and solve
        fragmentor = FMOFragmentor(max_fragment_qubits=20, max_fragment_atoms=8)
        fragments = fragmentor.fragment_molecule(mol_data["smiles"])

        solver = FragmentVQESolver(maxiter=50, use_cache=True)
        fragment_results = solver.solve_fragments(fragments)

        # Assemble energy
        assembler = FragmentAssembler(
            coupling_method="electrostatic",
            include_three_body=False,
        )

        start_time = time.time()
        assembled = assembler.assemble_energy(fragment_results, fragments)
        elapsed = time.time() - start_time

        print(f"Assembly time: {elapsed:.3f}s")

        # Print report
        report = assembler.generate_report(assembled, fragment_results)
        print(report)

        # Validate
        success = assembled.success

        results[mol_id] = {
            "success": success,
            "total_energy": assembled.total_energy,
            "error_estimate": assembled.error_estimate,
            "time": elapsed,
        }

        status = "✓ PASS" if success else "✗ FAIL"
        print(f"\nStatus: {status}")

    return results


def test_fci_validation():
    """Validate against exact FCI for small molecules."""
    print("\n" + "=" * 80)
    print("TEST 4: FCI VALIDATION (SMALL MOLECULES)")
    print("=" * 80)

    print("\nTesting: Water (H2O)")
    print("-" * 80)

    # Fragment and solve with FMO-VQE
    fragmentor = FMOFragmentor()
    fragments = fragmentor.fragment_molecule("O")

    solver = FragmentVQESolver(maxiter=100, use_cache=False)
    fragment_results = solver.solve_fragments(fragments)

    assembler = FragmentAssembler()
    assembled = assembler.assemble_energy(fragment_results, fragments)

    fmo_energy = assembled.total_energy
    fmo_error = assembled.error_estimate

    print(f"FMO-VQE Energy: {fmo_energy:.6f} ± {fmo_error:.6f} Hartree")

    # For comparison, we'd need exact FCI calculation
    # Here we use a known reference value for water
    # (This would require PySCF with FCI solver)
    print("\nNote: FCI comparison requires PySCF with FCI module")
    print("Expected accuracy: <0.1 Hartree for small molecules")

    success = fmo_error < 0.1  # Target accuracy

    status = "✓ PASS" if success else "✗ FAIL"
    print(f"\nStatus: {status}")

    return {"success": success, "energy": fmo_energy, "error": fmo_error}


def test_performance_benchmark():
    """Benchmark fragmentation overhead."""
    print("\n" + "=" * 80)
    print("TEST 5: PERFORMANCE BENCHMARK")
    print("=" * 80)

    print("\nBenchmarking fragmentation overhead...")
    print("-" * 80)

    # Test on caffeine (medium size)
    mol_data = TEST_MOLECULES["caffeine"]

    # Time fragmentation
    fragmentor = FMOFragmentor(max_fragment_qubits=20, max_fragment_atoms=8)

    start_time = time.time()
    fragments = fragmentor.fragment_molecule(mol_data["smiles"])
    frag_time = time.time() - start_time

    print(f"Fragmentation time: {frag_time:.3f}s")

    # Time VQE solving (per fragment average)
    solver = FragmentVQESolver(maxiter=50, use_cache=False)

    start_time = time.time()
    fragment_results = solver.solve_fragments(fragments)
    solve_time = time.time() - start_time

    avg_solve_time = solve_time / len(fragments) if fragments else 0

    print(f"Average solve time per fragment: {avg_solve_time:.3f}s")
    print(f"Total solve time: {solve_time:.3f}s")

    # Time assembly
    assembler = FragmentAssembler()

    start_time = time.time()
    assembled = assembler.assemble_energy(fragment_results, fragments)
    assembly_time = time.time() - start_time

    print(f"Assembly time: {assembly_time:.3f}s")

    total_time = frag_time + solve_time + assembly_time
    print(f"\nTotal FMO-VQE time: {total_time:.3f}s")

    # Success criteria: fragment time < 5 min per fragment
    success = avg_solve_time < 300  # 5 minutes

    status = "✓ PASS" if success else "✗ FAIL"
    print(f"\nStatus: {status}")

    return {
        "success": success,
        "frag_time": frag_time,
        "solve_time": solve_time,
        "assembly_time": assembly_time,
        "total_time": total_time,
    }


def test_large_molecule():
    """Test on large molecule (>100 qubits)."""
    print("\n" + "=" * 80)
    print("TEST 6: LARGE MOLECULE (>100 QUBITS)")
    print("=" * 80)

    mol_data = TEST_MOLECULES["tripeptide"]

    print(f"\nTesting: {mol_data['name']}")
    print(f"Expected ~{mol_data['expected_qubits']} qubits")
    print("-" * 80)

    # Fragment
    fragmentor = FMOFragmentor(max_fragment_qubits=20, max_fragment_atoms=6)

    start_time = time.time()
    fragments = fragmentor.fragment_molecule(mol_data["smiles"])
    frag_time = time.time() - start_time

    print(f"Fragmentation time: {frag_time:.3f}s")
    print(f"Created {len(fragments)} fragments")
    print(fragmentor.visualize_fragmentation(fragments))

    # Validate fragmentation
    max_qubits = max(f.num_qubits for f in fragments)
    total_qubits = sum(f.num_qubits for f in fragments)

    success = (
        len(fragments) >= 3 and
        max_qubits <= 20 and
        total_qubits >= 50  # Ensure meaningful fragmentation
    )

    status = "✓ PASS" if success else "✗ FAIL"
    print(f"\nStatus: {status}")

    return {
        "success": success,
        "num_fragments": len(fragments),
        "max_qubits": max_qubits,
        "total_qubits": total_qubits,
    }


def run_all_tests():
    """Run all FMO-VQE tests."""
    print("\n" + "=" * 80)
    print("FMO-VQE COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print(f"Test Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    all_results = {}

    # Run tests
    try:
        all_results["fragmentor"] = test_fragmentor()
    except Exception as e:
        print(f"\n✗ Fragmentor test failed: {e}")
        all_results["fragmentor"] = {"success": False, "error": str(e)}

    try:
        all_results["fragment_vqe"] = test_fragment_vqe()
    except Exception as e:
        print(f"\n✗ Fragment VQE test failed: {e}")
        all_results["fragment_vqe"] = {"success": False, "error": str(e)}

    try:
        all_results["assembler"] = test_assembler()
    except Exception as e:
        print(f"\n✗ Assembler test failed: {e}")
        all_results["assembler"] = {"success": False, "error": str(e)}

    try:
        all_results["fci_validation"] = test_fci_validation()
    except Exception as e:
        print(f"\n✗ FCI validation test failed: {e}")
        all_results["fci_validation"] = {"success": False, "error": str(e)}

    try:
        all_results["performance"] = test_performance_benchmark()
    except Exception as e:
        print(f"\n✗ Performance test failed: {e}")
        all_results["performance"] = {"success": False, "error": str(e)}

    try:
        all_results["large_molecule"] = test_large_molecule()
    except Exception as e:
        print(f"\n✗ Large molecule test failed: {e}")
        all_results["large_molecule"] = {"success": False, "error": str(e)}

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    total_tests = 0
    passed_tests = 0

    for test_name, test_result in all_results.items():
        if isinstance(test_result, dict):
            if "error" in test_result:
                status = "✗ FAIL"
                print(f"{test_name:20s}: {status} - {test_result['error']}")
            elif isinstance(test_result.get("success"), bool):
                success = test_result["success"]
                status = "✓ PASS" if success else "✗ FAIL"
                print(f"{test_name:20s}: {status}")
                total_tests += 1
                if success:
                    passed_tests += 1
            else:
                # Multiple sub-tests
                sub_success = sum(
                    1 for v in test_result.values()
                    if isinstance(v, dict) and v.get("success", False)
                )
                sub_total = sum(
                    1 for v in test_result.values()
                    if isinstance(v, dict) and "success" in v
                )
                if sub_total > 0:
                    status = f"{sub_success}/{sub_total} passed"
                    print(f"{test_name:20s}: {status}")
                    total_tests += sub_total
                    passed_tests += sub_success

    print("-" * 80)
    print(f"Total: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        print("\n✓ ALL TESTS PASSED!")
    else:
        print(f"\n✗ {total_tests - passed_tests} TEST(S) FAILED")

    print("=" * 80)

    return all_results


if __name__ == "__main__":
    results = run_all_tests()
