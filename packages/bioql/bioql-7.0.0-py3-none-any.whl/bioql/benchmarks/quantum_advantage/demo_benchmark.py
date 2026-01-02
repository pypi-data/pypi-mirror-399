#!/usr/bin/env python3
# Copyright 2024-2025 SpectrixRD
# Licensed under the Apache License, Version 2.0
# See LICENSE file in the project root for full license text

"""
Demonstration Script for Quantum Advantage Benchmarking Suite

This script demonstrates the complete benchmarking workflow:
1. Run comprehensive benchmarks
2. Analyze performance and accuracy
3. Generate reports
4. Display quantum advantage results
"""

import sys
from pathlib import Path
from loguru import logger

# Configure logging
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add("benchmark_demo.log", level="DEBUG")

from benchmark_suite import BenchmarkSuite, quick_benchmark
from performance_metrics import PerformanceAnalyzer
from accuracy_metrics import AccuracyAnalyzer
from dft_comparison import DFTBenchmark
from results_reporter import BenchmarkReporter


def main():
    """Run demonstration benchmarks."""
    logger.info("=" * 80)
    logger.info("BioQL Quantum Advantage Benchmarking Suite - Demonstration")
    logger.info("=" * 80)
    logger.info("")

    # Step 1: Run comprehensive benchmark suite
    logger.info("STEP 1: Running comprehensive benchmark suite...")
    logger.info("-" * 80)

    suite = BenchmarkSuite()

    # Run all scenarios (use small shots for demo)
    results = suite.run_all_scenarios(backend="simulator", shots=512)

    logger.info(f"\nCompleted {len(results)} benchmark runs")
    logger.info("")

    # Step 2: Performance Analysis
    logger.info("STEP 2: Analyzing performance metrics...")
    logger.info("-" * 80)

    perf_analyzer = PerformanceAnalyzer()
    perf_analyzer.add_results(results)

    # Calculate speedups
    speedups = perf_analyzer.calculate_speedups(
        quantum_method="fmo_vqe",
        classical_method="dft_b3lyp"
    )

    logger.info(f"\nCalculated {len(speedups)} speedup comparisons")

    # Get quantum advantage threshold
    advantage = perf_analyzer.get_quantum_advantage_threshold(
        speedup_threshold=1.0,
        accuracy_threshold=5.0
    )

    logger.info("\nQuantum Advantage Analysis:")
    logger.info(f"  Advantage achieved: {advantage.get('advantage_achieved', False)}")
    if advantage.get('mean_speedup'):
        logger.info(f"  Mean speedup: {advantage['mean_speedup']:.2f}x")
    if advantage.get('max_speedup'):
        logger.info(f"  Max speedup: {advantage['max_speedup']:.2f}x")

    # Generate speedup report
    logger.info("\nSpeedup Report:")
    logger.info("-" * 80)
    print(perf_analyzer.generate_speedup_report())

    # Step 3: Accuracy Analysis
    logger.info("\nSTEP 3: Analyzing accuracy metrics...")
    logger.info("-" * 80)

    acc_analyzer = AccuracyAnalyzer()
    acc_analyzer.add_results(results)

    # Calculate accuracy for all methods
    accuracies = acc_analyzer.calculate_all_accuracies()

    logger.info(f"\nCalculated accuracy for {len(accuracies)} methods")

    # Generate accuracy report
    logger.info("\nAccuracy Report:")
    logger.info("-" * 80)
    print(acc_analyzer.generate_accuracy_report())

    # Step 4: DFT Comparison
    logger.info("\nSTEP 4: Running DFT comparisons...")
    logger.info("-" * 80)

    dft_benchmark = DFTBenchmark()

    # Compare quantum results with DFT
    quantum_results = [r for r in results if r.method == "fmo_vqe"]
    for qr in quantum_results[:3]:  # First 3 for demo
        try:
            comparison = dft_benchmark.compare_with_quantum(
                qr.molecule,
                qr,
                dft_functional="B3LYP"
            )
            logger.info(f"  {qr.molecule}: Speedup = {comparison.speedup:.2f}x")
        except Exception as e:
            logger.warning(f"  {qr.molecule}: Comparison failed - {e}")

    # Generate DFT comparison report
    if dft_benchmark.comparisons:
        logger.info("\nDFT Comparison Report:")
        logger.info("-" * 80)
        print(dft_benchmark.generate_comparison_report())

    # Step 5: Generate Reports
    logger.info("\nSTEP 5: Generating comprehensive reports...")
    logger.info("-" * 80)

    # Save results to JSON
    results_file = suite.save_results("demo_benchmark_results.json")
    logger.info(f"  Saved results to: {results_file}")

    # Generate HTML report
    reporter = BenchmarkReporter()
    reporter.results = [r.to_dict() for r in results]

    html_report = reporter.generate_html_report("demo_benchmark_report.html")
    logger.info(f"  Generated HTML report: {html_report}")

    # Generate summary
    summary = reporter.generate_summary()
    logger.info("\nBenchmark Summary:")
    logger.info(f"  Total runs: {summary.get('total_runs', 0)}")
    logger.info(f"  Success rate: {summary.get('success_rate', 0)*100:.1f}%")
    logger.info(f"  Quantum runs: {summary.get('quantum_runs', 0)}")
    logger.info(f"  Classical runs: {summary.get('classical_runs', 0)}")

    if 'mae' in summary:
        logger.info(f"  Mean Absolute Error: {summary['mae']:.6f} Hartree")
    if 'quantum_mean_time' in summary:
        logger.info(f"  Quantum mean time: {summary['quantum_mean_time']:.4f}s")
    if 'classical_mean_time' in summary:
        logger.info(f"  Classical mean time: {summary['classical_mean_time']:.4f}s")

    # Step 6: Key Findings
    logger.info("\n" + "=" * 80)
    logger.info("KEY FINDINGS - QUANTUM ADVANTAGE DEMONSTRATION")
    logger.info("=" * 80)

    # Find best speedups
    if speedups:
        top_speedups = sorted(speedups, key=lambda s: s.speedup_factor, reverse=True)[:3]
        logger.info("\nTop 3 Speedups:")
        for i, s in enumerate(top_speedups, 1):
            logger.info(f"  {i}. {s.molecule}: {s.speedup_factor:.2f}x speedup")

    # Find best accuracy
    if accuracies:
        best_accuracy = min(accuracies.items(), key=lambda x: x[1].mae)
        logger.info(f"\nBest Accuracy: {best_accuracy[0]}")
        logger.info(f"  MAE: {best_accuracy[1].mae:.6f} Hartree")
        logger.info(f"  Chemical accuracy rate: {best_accuracy[1].chemical_accuracy_rate*100:.1f}%")

    # Success criteria evaluation
    logger.info("\nSUCCESS CRITERIA EVALUATION:")
    logger.info("-" * 80)

    # Criterion 1: Speedup
    mean_speedup = advantage.get('mean_speedup', 0)
    if mean_speedup >= 10:
        logger.info(f"  [PASS] 10-100x speedup achieved: {mean_speedup:.1f}x")
    elif mean_speedup >= 1:
        logger.info(f"  [PARTIAL] Quantum advantage demonstrated: {mean_speedup:.1f}x")
    else:
        logger.info(f"  [PENDING] Speedup target: {mean_speedup:.1f}x")

    # Criterion 2: Chemical accuracy
    passing_methods = sum(1 for acc in accuracies.values() if acc.passes_chemical_accuracy())
    if passing_methods > 0:
        logger.info(f"  [PASS] Chemical accuracy achieved by {passing_methods} method(s)")
    else:
        logger.info(f"  [PENDING] Chemical accuracy not yet achieved")

    # Criterion 3: Large system tractability
    large_system_results = [r for r in results if r.molecule == "SARS-CoV-2 Mpro + Inhibitor"]
    if large_system_results:
        logger.info(f"  [PASS] Large system calculations completed: {len(large_system_results)} runs")
    else:
        logger.info(f"  [INFO] Large system calculations in progress")

    logger.info("\n" + "=" * 80)
    logger.info("DEMONSTRATION COMPLETE")
    logger.info("=" * 80)
    logger.info(f"\nResults and reports saved in: {Path.cwd()}")
    logger.info("  - demo_benchmark_results.json")
    logger.info("  - demo_benchmark_report.html")
    logger.info("  - benchmark_demo.log")
    logger.info("")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nBenchmark interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
