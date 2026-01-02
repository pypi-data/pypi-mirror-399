# Copyright 2024-2025 SpectrixRD
# Licensed under the Apache License, Version 2.0
# See LICENSE file in the project root for full license text

"""
BioQL Quantum Advantage Benchmarking Suite

Production-grade benchmarking system to demonstrate quantum advantage vs classical methods.

Features:
- Comprehensive performance and accuracy metrics
- Comparison against DFT (PySCF), AutoDock Vina, and Schrodinger
- Multiple test scenarios (small/medium/large molecules)
- Automated benchmark execution and reporting
- Statistical analysis and visualization

Modules:
- benchmark_suite: Main orchestrator for running benchmarks
- performance_metrics: Speedup validation and cost analysis
- accuracy_metrics: Chemical accuracy validation
- dft_comparison: Compare vs Gaussian/ORCA DFT
- vina_comparison: Docking benchmarks
- schrodinger_comparison: Industry standard comparison
- automated_runner: Nightly benchmark execution
- results_reporter: Generate reports and dashboards

Example:
    >>> from bioql.benchmarks.quantum_advantage import BenchmarkSuite
    >>> suite = BenchmarkSuite()
    >>> results = suite.run_all_scenarios()
    >>> suite.generate_report("benchmark_results.html")
"""

from .benchmark_suite import BenchmarkSuite, TestScenario
from .performance_metrics import PerformanceAnalyzer, SpeedupMetrics
from .accuracy_metrics import AccuracyAnalyzer, ChemicalAccuracy

__all__ = [
    "BenchmarkSuite",
    "TestScenario",
    "PerformanceAnalyzer",
    "SpeedupMetrics",
    "AccuracyAnalyzer",
    "ChemicalAccuracy",
]

__version__ = "1.0.0"
