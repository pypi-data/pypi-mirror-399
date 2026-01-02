# Copyright 2024-2025 SpectrixRD
# Licensed under the Apache License, Version 2.0
# See LICENSE file in the project root for full license text

"""
Performance Metrics and Speedup Analysis

Comprehensive analysis of quantum vs classical performance including:
- Speedup calculations (wall-clock, CPU, theoretical)
- Scalability analysis
- Cost-benefit analysis
- Resource utilization metrics
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from loguru import logger


@dataclass
class SpeedupMetrics:
    """Metrics for quantum speedup analysis."""
    molecule: str
    quantum_method: str
    classical_method: str

    # Time metrics
    quantum_time: float  # seconds
    classical_time: float  # seconds
    speedup_factor: float  # classical_time / quantum_time

    # Theoretical complexity
    quantum_complexity: str = "O(N^4)"  # Example for VQE
    classical_complexity: str = "O(N^7)"  # Example for CCSD(T)

    # Scalability metrics
    num_atoms: int = 0
    num_qubits: Optional[int] = None
    circuit_depth: Optional[int] = None

    # Resource metrics
    quantum_memory: Optional[float] = None  # MB
    classical_memory: Optional[float] = None  # MB
    memory_speedup: Optional[float] = None

    # Cost metrics
    quantum_cost: Optional[float] = None  # USD
    classical_cost: Optional[float] = None  # USD
    cost_efficiency: Optional[float] = None  # speedup / cost_ratio

    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_quantum_advantage(self, threshold: float = 1.0) -> bool:
        """
        Check if quantum method demonstrates advantage.

        Args:
            threshold: Minimum speedup factor for advantage (default: 1.0)

        Returns:
            True if speedup_factor > threshold
        """
        return self.speedup_factor > threshold

    def to_dict(self) -> Dict[str, Any]:
        return {
            'molecule': self.molecule,
            'quantum_method': self.quantum_method,
            'classical_method': self.classical_method,
            'quantum_time': self.quantum_time,
            'classical_time': self.classical_time,
            'speedup_factor': self.speedup_factor,
            'quantum_complexity': self.quantum_complexity,
            'classical_complexity': self.classical_complexity,
            'num_atoms': self.num_atoms,
            'num_qubits': self.num_qubits,
            'circuit_depth': self.circuit_depth,
            'quantum_memory': self.quantum_memory,
            'classical_memory': self.classical_memory,
            'memory_speedup': self.memory_speedup,
            'quantum_cost': self.quantum_cost,
            'classical_cost': self.classical_cost,
            'cost_efficiency': self.cost_efficiency,
            'metadata': self.metadata
        }


@dataclass
class CostAnalysis:
    """Cost-benefit analysis for quantum vs classical."""
    molecule: str
    method: str

    # Computational costs
    wall_time: float  # seconds
    cpu_hours: float
    estimated_cloud_cost: float  # USD

    # Accuracy achieved
    absolute_error: Optional[float] = None
    relative_error: Optional[float] = None  # percentage

    # Cost efficiency metrics
    cost_per_second: Optional[float] = None  # USD/s
    cost_per_accuracy: Optional[float] = None  # USD per 1% accuracy improvement
    time_per_accuracy: Optional[float] = None  # seconds per 1% accuracy

    # Resource details
    backend: str = "simulator"
    shots: int = 1024
    qubits_used: Optional[int] = None

    def calculate_efficiency(self):
        """Calculate cost efficiency metrics."""
        if self.wall_time > 0:
            self.cost_per_second = self.estimated_cloud_cost / self.wall_time

        if self.relative_error is not None and self.relative_error > 0:
            self.cost_per_accuracy = self.estimated_cloud_cost / (100 - self.relative_error)
            self.time_per_accuracy = self.wall_time / (100 - self.relative_error)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'molecule': self.molecule,
            'method': self.method,
            'wall_time': self.wall_time,
            'cpu_hours': self.cpu_hours,
            'estimated_cloud_cost': self.estimated_cloud_cost,
            'absolute_error': self.absolute_error,
            'relative_error': self.relative_error,
            'cost_per_second': self.cost_per_second,
            'cost_per_accuracy': self.cost_per_accuracy,
            'time_per_accuracy': self.time_per_accuracy,
            'backend': self.backend,
            'shots': self.shots,
            'qubits_used': self.qubits_used
        }


class PerformanceAnalyzer:
    """
    Analyze performance and speedup of quantum vs classical methods.

    Example:
        >>> from bioql.benchmarks.quantum_advantage import PerformanceAnalyzer
        >>> analyzer = PerformanceAnalyzer()
        >>> analyzer.add_results(benchmark_results)
        >>> speedups = analyzer.calculate_speedups()
        >>> analyzer.generate_speedup_report()
    """

    def __init__(self):
        """Initialize performance analyzer."""
        self.results: List[Any] = []
        self.speedup_metrics: List[SpeedupMetrics] = []
        self.cost_analyses: List[CostAnalysis] = []

        # Pricing (USD per hour)
        self.pricing = {
            'ibm_torino': 1.60,  # IBM Quantum premium
            'ionq': 0.30,  # Per minute
            'aws_braket_simulator': 0.075,
            'aws_braket_dm1': 0.30,
            'classical_hpc': 0.50,  # Typical HPC cost
            'classical_cloud': 0.10,  # Cloud CPU instance
        }

    def add_results(self, results: List[Any]):
        """
        Add benchmark results for analysis.

        Args:
            results: List of BenchmarkResult objects
        """
        self.results.extend(results)
        logger.info(f"Added {len(results)} results for performance analysis")

    def calculate_speedups(
        self,
        quantum_method: str = "fmo_vqe",
        classical_method: str = "dft_b3lyp"
    ) -> List[SpeedupMetrics]:
        """
        Calculate speedup metrics comparing quantum to classical methods.

        Args:
            quantum_method: Quantum method to analyze
            classical_method: Classical method to compare against

        Returns:
            List of SpeedupMetrics
        """
        logger.info(f"Calculating speedups: {quantum_method} vs {classical_method}")

        speedups = []

        # Group results by molecule
        molecules = set(r.molecule for r in self.results)

        for molecule in molecules:
            quantum_results = [
                r for r in self.results
                if r.molecule == molecule and r.method == quantum_method and r.success
            ]
            classical_results = [
                r for r in self.results
                if r.molecule == molecule and r.method == classical_method and r.success
            ]

            if not quantum_results or not classical_results:
                continue

            # Use first result (or average if multiple runs)
            qr = quantum_results[0]
            cr = classical_results[0]

            speedup_factor = cr.wall_time / qr.wall_time if qr.wall_time > 0 else 0

            # Calculate memory speedup if available
            memory_speedup = None
            if qr.memory_peak and cr.memory_peak and qr.memory_peak > 0:
                memory_speedup = cr.memory_peak / qr.memory_peak

            # Estimate costs
            quantum_cost = self._estimate_cost(qr)
            classical_cost = self._estimate_cost(cr)
            cost_efficiency = speedup_factor / (quantum_cost / classical_cost) if classical_cost > 0 else None

            metrics = SpeedupMetrics(
                molecule=molecule,
                quantum_method=quantum_method,
                classical_method=classical_method,
                quantum_time=qr.wall_time,
                classical_time=cr.wall_time,
                speedup_factor=speedup_factor,
                num_atoms=qr.metadata.get('num_atoms', 0),
                num_qubits=qr.qubits_used,
                circuit_depth=qr.circuit_depth,
                quantum_memory=qr.memory_peak,
                classical_memory=cr.memory_peak,
                memory_speedup=memory_speedup,
                quantum_cost=quantum_cost,
                classical_cost=classical_cost,
                cost_efficiency=cost_efficiency,
                metadata={
                    'quantum_result': qr.to_dict(),
                    'classical_result': cr.to_dict()
                }
            )

            speedups.append(metrics)
            self.speedup_metrics.append(metrics)

        logger.info(f"Calculated {len(speedups)} speedup comparisons")
        return speedups

    def _estimate_cost(self, result: Any) -> float:
        """
        Estimate computational cost in USD.

        Args:
            result: BenchmarkResult

        Returns:
            Estimated cost in USD
        """
        backend = result.backend.lower()

        # Get hourly rate
        if 'ibm' in backend:
            rate_per_hour = self.pricing.get('ibm_torino', 1.60)
        elif 'ionq' in backend:
            rate_per_hour = self.pricing.get('ionq', 0.30) * 60  # Convert per-minute to per-hour
        elif 'simulator' in backend:
            rate_per_hour = self.pricing.get('aws_braket_simulator', 0.075)
        elif result.qubits_used:  # Quantum method
            rate_per_hour = self.pricing.get('ibm_torino', 1.60)
        else:  # Classical method
            rate_per_hour = self.pricing.get('classical_cloud', 0.10)

        # Calculate cost based on wall time
        hours = result.wall_time / 3600
        cost = hours * rate_per_hour

        # Add shot-based cost for quantum (example: $0.0001 per 1000 shots)
        if result.qubits_used and result.shots:
            shot_cost = (result.shots / 1000) * 0.0001
            cost += shot_cost

        return cost

    def analyze_scalability(
        self,
        method: str = "fmo_vqe"
    ) -> Dict[str, Any]:
        """
        Analyze scalability of a method with respect to system size.

        Args:
            method: Method to analyze

        Returns:
            Scalability analysis dictionary
        """
        logger.info(f"Analyzing scalability for {method}")

        method_results = [
            r for r in self.results
            if r.method == method and r.success
        ]

        if not method_results:
            return {}

        # Extract size metrics
        sizes = []
        times = []
        for r in method_results:
            num_atoms = r.metadata.get('num_atoms', 0)
            if num_atoms > 0:
                sizes.append(num_atoms)
                times.append(r.wall_time)

        if len(sizes) < 2:
            return {
                'method': method,
                'data_points': len(sizes),
                'insufficient_data': True
            }

        # Fit scaling curve (log-log for power law)
        log_sizes = np.log(sizes)
        log_times = np.log(times)
        coeffs = np.polyfit(log_sizes, log_times, 1)
        exponent = coeffs[0]

        # Determine complexity class
        if exponent < 2:
            complexity_class = "Subquadratic"
        elif exponent < 3:
            complexity_class = "Polynomial (N^2 to N^3)"
        elif exponent < 4:
            complexity_class = "Polynomial (N^3 to N^4)"
        else:
            complexity_class = "High-order polynomial or exponential"

        return {
            'method': method,
            'data_points': len(sizes),
            'size_range': (min(sizes), max(sizes)),
            'time_range': (min(times), max(times)),
            'scaling_exponent': exponent,
            'complexity_class': complexity_class,
            'equation': f"T ≈ N^{exponent:.2f}",
            'fit_quality': float(np.corrcoef(log_sizes, log_times)[0, 1])
        }

    def calculate_cost_analyses(self) -> List[CostAnalysis]:
        """
        Calculate detailed cost analyses for all results.

        Returns:
            List of CostAnalysis objects
        """
        logger.info("Calculating cost analyses for all results")

        analyses = []
        for result in self.results:
            if not result.success:
                continue

            # Estimate CPU hours (assume 1 CPU for simplicity)
            cpu_hours = result.cpu_time / 3600 if result.cpu_time else result.wall_time / 3600

            analysis = CostAnalysis(
                molecule=result.molecule,
                method=result.method,
                wall_time=result.wall_time,
                cpu_hours=cpu_hours,
                estimated_cloud_cost=self._estimate_cost(result),
                absolute_error=result.absolute_error,
                relative_error=result.relative_error,
                backend=result.backend,
                shots=result.shots,
                qubits_used=result.qubits_used
            )

            analysis.calculate_efficiency()
            analyses.append(analysis)
            self.cost_analyses.append(analysis)

        logger.info(f"Calculated {len(analyses)} cost analyses")
        return analyses

    def get_quantum_advantage_threshold(
        self,
        speedup_threshold: float = 1.0,
        accuracy_threshold: float = 5.0  # percentage error
    ) -> Dict[str, Any]:
        """
        Determine at what system size quantum advantage is achieved.

        Args:
            speedup_threshold: Minimum speedup for quantum advantage
            accuracy_threshold: Maximum acceptable error percentage

        Returns:
            Analysis of quantum advantage thresholds
        """
        logger.info("Analyzing quantum advantage thresholds")

        # Find speedups that meet criteria
        qualifying_speedups = [
            s for s in self.speedup_metrics
            if s.speedup_factor >= speedup_threshold
        ]

        if not qualifying_speedups:
            return {
                'advantage_achieved': False,
                'message': f"No speedups >= {speedup_threshold}x found"
            }

        # Analyze by molecule size
        sizes = [s.num_atoms for s in qualifying_speedups if s.num_atoms > 0]
        speedups = [s.speedup_factor for s in qualifying_speedups if s.num_atoms > 0]

        if not sizes:
            return {
                'advantage_achieved': True,
                'num_cases': len(qualifying_speedups),
                'mean_speedup': float(np.mean([s.speedup_factor for s in qualifying_speedups])),
                'max_speedup': float(max(s.speedup_factor for s in qualifying_speedups))
            }

        return {
            'advantage_achieved': True,
            'num_cases': len(qualifying_speedups),
            'molecule_size_range': (min(sizes), max(sizes)),
            'speedup_range': (min(speedups), max(speedups)),
            'mean_speedup': float(np.mean(speedups)),
            'max_speedup': float(max(speedups)),
            'threshold_size': min(sizes),  # Minimum size for advantage
            'scaling_trend': 'increasing' if np.corrcoef(sizes, speedups)[0, 1] > 0 else 'decreasing'
        }

    def generate_speedup_report(self) -> str:
        """
        Generate human-readable speedup report.

        Returns:
            Formatted report string
        """
        lines = []
        lines.append("=" * 80)
        lines.append("QUANTUM ADVANTAGE PERFORMANCE REPORT")
        lines.append("=" * 80)
        lines.append("")

        if not self.speedup_metrics:
            lines.append("No speedup data available. Run calculate_speedups() first.")
            return "\n".join(lines)

        # Summary statistics
        speedups = [s.speedup_factor for s in self.speedup_metrics]
        lines.append("SUMMARY STATISTICS:")
        lines.append("-" * 80)
        lines.append(f"Total comparisons: {len(self.speedup_metrics)}")
        lines.append(f"Mean speedup: {np.mean(speedups):.2f}x")
        lines.append(f"Median speedup: {np.median(speedups):.2f}x")
        lines.append(f"Max speedup: {max(speedups):.2f}x")
        lines.append(f"Min speedup: {min(speedups):.2f}x")
        lines.append(f"Quantum advantage cases (>1x): {sum(1 for s in speedups if s > 1)} ({100*sum(1 for s in speedups if s > 1)/len(speedups):.1f}%)")
        lines.append(f"Significant advantage cases (>10x): {sum(1 for s in speedups if s > 10)} ({100*sum(1 for s in speedups if s > 10)/len(speedups):.1f}%)")
        lines.append("")

        # Individual speedup details
        lines.append("DETAILED SPEEDUP ANALYSIS:")
        lines.append("-" * 80)
        lines.append(f"{'Molecule':<30} {'Q-Time(s)':<12} {'C-Time(s)':<12} {'Speedup':<12} {'Status'}")
        lines.append("-" * 80)

        for s in sorted(self.speedup_metrics, key=lambda x: x.speedup_factor, reverse=True):
            status = "ADVANTAGE" if s.speedup_factor > 1 else "SLOWER"
            if s.speedup_factor > 10:
                status = "MAJOR ADVANTAGE"
            elif s.speedup_factor > 100:
                status = "BREAKTHROUGH"

            lines.append(
                f"{s.molecule:<30} {s.quantum_time:>10.4f}  {s.classical_time:>10.4f}  "
                f"{s.speedup_factor:>10.2f}x  {status}"
            )

        lines.append("")
        lines.append("=" * 80)

        return "\n".join(lines)

    def generate_cost_report(self) -> str:
        """
        Generate cost-benefit analysis report.

        Returns:
            Formatted report string
        """
        lines = []
        lines.append("=" * 80)
        lines.append("COST-BENEFIT ANALYSIS REPORT")
        lines.append("=" * 80)
        lines.append("")

        if not self.cost_analyses:
            lines.append("No cost data available. Run calculate_cost_analyses() first.")
            return "\n".join(lines)

        # Summary
        total_quantum_cost = sum(c.estimated_cloud_cost for c in self.cost_analyses if 'vqe' in c.method.lower() or 'qaoa' in c.method.lower())
        total_classical_cost = sum(c.estimated_cloud_cost for c in self.cost_analyses if 'vqe' not in c.method.lower() and 'qaoa' not in c.method.lower())

        lines.append("SUMMARY:")
        lines.append("-" * 80)
        lines.append(f"Total quantum cost: ${total_quantum_cost:.4f}")
        lines.append(f"Total classical cost: ${total_classical_cost:.4f}")
        if total_classical_cost > 0:
            lines.append(f"Cost ratio (Q/C): {total_quantum_cost/total_classical_cost:.2f}")
        lines.append("")

        # Top cost-efficient methods
        lines.append("TOP COST-EFFICIENT CALCULATIONS:")
        lines.append("-" * 80)
        lines.append(f"{'Molecule':<25} {'Method':<20} {'Cost($)':<12} {'Error%':<10} {'$/Accuracy'}")
        lines.append("-" * 80)

        sorted_analyses = sorted(
            [c for c in self.cost_analyses if c.cost_per_accuracy is not None],
            key=lambda x: x.cost_per_accuracy
        )[:10]

        for c in sorted_analyses:
            lines.append(
                f"{c.molecule:<25} {c.method:<20} ${c.estimated_cloud_cost:>10.6f}  "
                f"{c.relative_error:>8.2f}%  ${c.cost_per_accuracy:.6f}"
            )

        lines.append("")
        lines.append("=" * 80)

        return "\n".join(lines)


# Convenience functions

def analyze_speedup(quantum_results: List[Any], classical_results: List[Any]) -> Dict[str, Any]:
    """
    Quick speedup analysis between quantum and classical results.

    Args:
        quantum_results: List of quantum benchmark results
        classical_results: List of classical benchmark results

    Returns:
        Speedup analysis dictionary
    """
    analyzer = PerformanceAnalyzer()
    analyzer.add_results(quantum_results + classical_results)

    if quantum_results and classical_results:
        q_method = quantum_results[0].method
        c_method = classical_results[0].method
        analyzer.calculate_speedups(q_method, c_method)

    return {
        'speedup_metrics': [s.to_dict() for s in analyzer.speedup_metrics],
        'summary': analyzer.get_quantum_advantage_threshold(),
        'report': analyzer.generate_speedup_report()
    }


__all__ = [
    "PerformanceAnalyzer",
    "SpeedupMetrics",
    "CostAnalysis",
    "analyze_speedup",
]
