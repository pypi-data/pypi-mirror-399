# Copyright 2024-2025 SpectrixRD
# Licensed under the Apache License, Version 2.0
# See LICENSE file in the project root for full license text

"""
Unit Tests for Quantum Advantage Benchmarking Suite
"""

import unittest
import tempfile
from pathlib import Path

from .benchmark_suite import BenchmarkSuite, TestScenario, ScenarioType, MethodType
from .performance_metrics import PerformanceAnalyzer, SpeedupMetrics
from .accuracy_metrics import AccuracyAnalyzer, ChemicalAccuracy
from .dft_comparison import DFTBenchmark
from .results_reporter import BenchmarkReporter
from .automated_runner import BenchmarkScheduler


class TestBenchmarkSuite(unittest.TestCase):
    """Test BenchmarkSuite functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.suite = BenchmarkSuite()

    def test_initialization(self):
        """Test suite initialization."""
        self.assertIsNotNone(self.suite)
        self.assertGreater(len(self.suite.scenarios), 0)
        self.assertEqual(len(self.suite.results), 0)

    def test_scenario_setup(self):
        """Test that scenarios are properly set up."""
        scenario_names = [s.name for s in self.suite.scenarios]
        self.assertIn("Small Molecules Validation", scenario_names)
        self.assertIn("Drug-Like Molecules Performance", scenario_names)
        self.assertIn("Large Complexes Scalability", scenario_names)

    def test_run_scenario(self):
        """Test running a single scenario."""
        scenario = self.suite.scenarios[0]  # Small molecules
        results = self.suite.run_scenario(scenario, backend="simulator", shots=100)

        self.assertIsNotNone(results)
        self.assertGreater(len(results), 0)

        # Check result structure
        result = results[0]
        self.assertIn('scenario', result.__dict__ or vars(result))
        self.assertIn('molecule', result.__dict__ or vars(result))
        self.assertIn('method', result.__dict__ or vars(result))

    def test_save_and_load_results(self):
        """Test saving and loading results."""
        # Run a small benchmark
        scenario = self.suite.scenarios[0]
        self.suite.run_scenario(scenario, backend="simulator", shots=100)

        # Save results
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_results.json"
            self.suite.output_dir = Path(tmpdir)
            saved_file = self.suite.save_results("test_results.json")

            self.assertTrue(Path(saved_file).exists())

            # Load results
            new_suite = BenchmarkSuite()
            new_suite.load_results(saved_file)

            self.assertEqual(len(new_suite.results), len(self.suite.results))

    def test_summary_statistics(self):
        """Test summary statistics calculation."""
        # Run a small benchmark
        scenario = self.suite.scenarios[0]
        self.suite.run_scenario(scenario, backend="simulator", shots=100)

        stats = self.suite.get_summary_statistics()

        self.assertIn('total_runs', stats)
        self.assertIn('successful_runs', stats)
        self.assertGreater(stats['total_runs'], 0)


class TestPerformanceMetrics(unittest.TestCase):
    """Test PerformanceAnalyzer functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = PerformanceAnalyzer()
        self.suite = BenchmarkSuite()

    def test_initialization(self):
        """Test analyzer initialization."""
        self.assertIsNotNone(self.analyzer)
        self.assertEqual(len(self.analyzer.results), 0)

    def test_speedup_calculation(self):
        """Test speedup calculation."""
        # Run benchmark to get results
        scenario = self.suite.scenarios[0]
        results = self.suite.run_scenario(scenario, backend="simulator", shots=100)

        # Add to analyzer
        self.analyzer.add_results(results)

        # Calculate speedups
        speedups = self.analyzer.calculate_speedups(
            quantum_method="fmo_vqe",
            classical_method="dft_b3lyp"
        )

        if speedups:
            self.assertGreater(len(speedups), 0)
            self.assertIsInstance(speedups[0], SpeedupMetrics)

    def test_cost_analysis(self):
        """Test cost analysis."""
        scenario = self.suite.scenarios[0]
        results = self.suite.run_scenario(scenario, backend="simulator", shots=100)

        self.analyzer.add_results(results)
        analyses = self.analyzer.calculate_cost_analyses()

        self.assertGreater(len(analyses), 0)
        self.assertIsNotNone(analyses[0].estimated_cloud_cost)


class TestAccuracyMetrics(unittest.TestCase):
    """Test AccuracyAnalyzer functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = AccuracyAnalyzer()
        self.suite = BenchmarkSuite()

    def test_initialization(self):
        """Test analyzer initialization."""
        self.assertIsNotNone(self.analyzer)
        self.assertEqual(len(self.analyzer.results), 0)

    def test_accuracy_calculation(self):
        """Test accuracy calculation."""
        scenario = self.suite.scenarios[0]  # Small molecules with exact energies
        results = self.suite.run_scenario(scenario, backend="simulator", shots=100)

        self.analyzer.add_results(results)

        # Find a method that was run
        methods = set(r.method for r in results if r.success)
        if methods:
            method = list(methods)[0]
            accuracy = self.analyzer.calculate_accuracy(method)

            self.assertIsInstance(accuracy, ChemicalAccuracy)
            self.assertGreater(accuracy.num_samples, 0)
            self.assertIsNotNone(accuracy.mae)
            self.assertIsNotNone(accuracy.rmse)

    def test_method_comparison(self):
        """Test method comparison."""
        scenario = self.suite.scenarios[0]
        results = self.suite.run_scenario(scenario, backend="simulator", shots=100)

        self.analyzer.add_results(results)

        methods = list(set(r.method for r in results if r.success))
        if len(methods) >= 2:
            comparison = self.analyzer.compare_methods(methods[0], methods[1])
            self.assertIsNotNone(comparison)
            self.assertIn(comparison.winner, [methods[0], methods[1], 'tie'])


class TestDFTComparison(unittest.TestCase):
    """Test DFT comparison functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.benchmark = DFTBenchmark()

    def test_initialization(self):
        """Test DFT benchmark initialization."""
        self.assertIsNotNone(self.benchmark)
        self.assertGreater(len(self.benchmark.test_molecules), 0)

    def test_dft_calculation(self):
        """Test DFT calculation (simulation mode)."""
        result = self.benchmark.run_dft("H2", functional="B3LYP", basis="6-31G", use_pyscf=False)

        self.assertIsNotNone(result)
        self.assertEqual(result.molecule, "H2")
        self.assertEqual(result.functional, "B3LYP")
        self.assertTrue(result.converged)
        self.assertIsNotNone(result.total_energy)

    def test_functional_comparison(self):
        """Test comparing multiple functionals."""
        functionals = ['B3LYP', 'PBE']
        results = self.benchmark.run_functional_comparison("H2", functionals, basis="STO-3G")

        self.assertEqual(len(results), len(functionals))
        for functional in functionals:
            self.assertIn(functional, results)


class TestBenchmarkReporter(unittest.TestCase):
    """Test BenchmarkReporter functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.reporter = BenchmarkReporter()
        self.suite = BenchmarkSuite()

    def test_initialization(self):
        """Test reporter initialization."""
        self.assertIsNotNone(self.reporter)

    def test_html_generation(self):
        """Test HTML report generation."""
        # Run small benchmark
        scenario = self.suite.scenarios[0]
        results = self.suite.run_scenario(scenario, backend="simulator", shots=100)

        self.reporter.results = [r.to_dict() for r in results]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_report.html"
            self.reporter.generate_html_report(str(output_path))

            self.assertTrue(output_path.exists())
            self.assertGreater(output_path.stat().st_size, 0)

    def test_summary_generation(self):
        """Test summary generation."""
        scenario = self.suite.scenarios[0]
        results = self.suite.run_scenario(scenario, backend="simulator", shots=100)

        self.reporter.results = [r.to_dict() for r in results]
        summary = self.reporter.generate_summary()

        self.assertIn('total_runs', summary)
        self.assertIn('success_rate', summary)


class TestAutomatedRunner(unittest.TestCase):
    """Test BenchmarkScheduler functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.tmpdir = tempfile.TemporaryDirectory()
        db_path = Path(self.tmpdir.name) / "test_benchmarks.db"
        self.scheduler = BenchmarkScheduler(db_path=str(db_path))

    def tearDown(self):
        """Clean up test fixtures."""
        self.tmpdir.cleanup()

    def test_initialization(self):
        """Test scheduler initialization."""
        self.assertIsNotNone(self.scheduler)
        self.assertTrue(Path(self.scheduler.db_path).exists())

    def test_database_storage(self):
        """Test storing results in database."""
        suite = BenchmarkSuite()
        scenario = suite.scenarios[0]
        suite.run_scenario(scenario, backend="simulator", shots=100)

        summary = self.scheduler._store_results(suite, duration=10.0)

        self.assertIn('run_id', summary)
        self.assertGreater(summary['run_id'], 0)


def run_tests():
    """Run all tests."""
    unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == '__main__':
    run_tests()
