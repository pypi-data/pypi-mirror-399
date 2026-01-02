# Copyright 2024-2025 SpectrixRD
# Licensed under the Apache License, Version 2.0
# See LICENSE file in the project root for full license text

"""
Accuracy Metrics and Chemical Accuracy Validation

Comprehensive accuracy analysis including:
- MAE, RMSE, R², Spearman correlation
- Chemical accuracy validation (1 kcal/mol threshold)
- Statistical significance testing
- Comparison to experimental data
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from scipy import stats
from loguru import logger


# Constants
CHEMICAL_ACCURACY_HARTREE = 0.0016  # 1 kcal/mol in Hartree
CHEMICAL_ACCURACY_KCAL = 1.0  # kcal/mol
HARTREE_TO_KCAL = 627.509  # Conversion factor


@dataclass
class ChemicalAccuracy:
    """Chemical accuracy metrics for a method."""
    method: str
    num_samples: int

    # Error metrics
    mae: float  # Mean Absolute Error
    rmse: float  # Root Mean Square Error
    max_error: float
    min_error: float
    std_dev: float

    # Correlation metrics
    r_squared: float  # Coefficient of determination
    pearson_r: float  # Pearson correlation coefficient
    spearman_rho: float  # Spearman rank correlation

    # Success rates
    chemical_accuracy_rate: float  # % within 1 kcal/mol
    tight_accuracy_rate: float  # % within 0.5 kcal/mol
    relaxed_accuracy_rate: float  # % within 2 kcal/mol

    # Optional fields with defaults
    kendall_tau: Optional[float] = None  # Kendall's tau
    p_value: Optional[float] = None
    confidence_interval_95: Optional[Tuple[float, float]] = None
    units: str = "Hartree"
    reference_method: str = "Experimental"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def passes_chemical_accuracy(self) -> bool:
        """Check if method achieves chemical accuracy on average."""
        threshold = CHEMICAL_ACCURACY_HARTREE if self.units == "Hartree" else CHEMICAL_ACCURACY_KCAL
        return self.mae <= threshold

    def to_dict(self) -> Dict[str, Any]:
        return {
            'method': self.method,
            'num_samples': self.num_samples,
            'mae': self.mae,
            'rmse': self.rmse,
            'max_error': self.max_error,
            'min_error': self.min_error,
            'std_dev': self.std_dev,
            'r_squared': self.r_squared,
            'pearson_r': self.pearson_r,
            'spearman_rho': self.spearman_rho,
            'kendall_tau': self.kendall_tau,
            'chemical_accuracy_rate': self.chemical_accuracy_rate,
            'tight_accuracy_rate': self.tight_accuracy_rate,
            'relaxed_accuracy_rate': self.relaxed_accuracy_rate,
            'p_value': self.p_value,
            'confidence_interval_95': self.confidence_interval_95,
            'units': self.units,
            'reference_method': self.reference_method,
            'passes_chemical_accuracy': self.passes_chemical_accuracy(),
            'metadata': self.metadata
        }


@dataclass
class AccuracyComparison:
    """Comparison of accuracy between two methods."""
    method_a: str
    method_b: str
    num_samples: int

    # Relative performance
    mae_improvement: float  # Percentage improvement
    rmse_improvement: float
    correlation_improvement: float  # R² improvement

    # Statistical tests
    paired_t_statistic: float
    paired_t_pvalue: float
    significantly_different: bool  # p < 0.05

    # Winner determination
    winner: str  # method_a or method_b
    confidence: float  # 0-1 confidence in winner

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'method_a': self.method_a,
            'method_b': self.method_b,
            'num_samples': self.num_samples,
            'mae_improvement': self.mae_improvement,
            'rmse_improvement': self.rmse_improvement,
            'correlation_improvement': self.correlation_improvement,
            'paired_t_statistic': self.paired_t_statistic,
            'paired_t_pvalue': self.paired_t_pvalue,
            'significantly_different': self.significantly_different,
            'winner': self.winner,
            'confidence': self.confidence,
            'metadata': self.metadata
        }


class AccuracyAnalyzer:
    """
    Comprehensive accuracy analysis for quantum chemistry calculations.

    Example:
        >>> from bioql.benchmarks.quantum_advantage import AccuracyAnalyzer
        >>> analyzer = AccuracyAnalyzer()
        >>> analyzer.add_results(benchmark_results)
        >>> accuracy = analyzer.calculate_accuracy("fmo_vqe")
        >>> print(f"MAE: {accuracy.mae:.4f} Hartree")
        >>> print(f"Chemical accuracy: {accuracy.passes_chemical_accuracy()}")
    """

    def __init__(self):
        """Initialize accuracy analyzer."""
        self.results: List[Any] = []
        self.accuracy_metrics: Dict[str, ChemicalAccuracy] = {}
        self.comparisons: List[AccuracyComparison] = []

    def add_results(self, results: List[Any]):
        """
        Add benchmark results for analysis.

        Args:
            results: List of BenchmarkResult objects
        """
        self.results.extend(results)
        logger.info(f"Added {len(results)} results for accuracy analysis")

    def calculate_accuracy(
        self,
        method: str,
        reference_field: str = "reference_value",
        computed_field: str = "computed_value",
        units: str = "Hartree"
    ) -> ChemicalAccuracy:
        """
        Calculate comprehensive accuracy metrics for a method.

        Args:
            method: Method name to analyze
            reference_field: Field name for reference values
            computed_field: Field name for computed values
            units: Units of energy values

        Returns:
            ChemicalAccuracy object with all metrics
        """
        logger.info(f"Calculating accuracy metrics for {method}")

        # Filter results for this method with valid reference values
        method_results = [
            r for r in self.results
            if r.method == method and r.success
            and getattr(r, reference_field, None) is not None
            and getattr(r, computed_field, None) is not None
        ]

        if not method_results:
            raise ValueError(f"No valid results found for method {method}")

        # Extract values
        reference_values = np.array([getattr(r, reference_field) for r in method_results])
        computed_values = np.array([getattr(r, computed_field) for r in method_results])

        # Calculate errors
        errors = np.abs(computed_values - reference_values)
        squared_errors = (computed_values - reference_values) ** 2

        mae = float(np.mean(errors))
        rmse = float(np.sqrt(np.mean(squared_errors)))
        max_error = float(np.max(errors))
        min_error = float(np.min(errors))
        std_dev = float(np.std(errors))

        # Calculate correlation metrics
        if len(computed_values) > 1:
            # Pearson correlation
            pearson_r, p_value = stats.pearsonr(reference_values, computed_values)
            r_squared = pearson_r ** 2

            # Spearman correlation (rank-based)
            spearman_rho, _ = stats.spearmanr(reference_values, computed_values)

            # Kendall's tau (optional, more robust)
            try:
                kendall_tau, _ = stats.kendalltau(reference_values, computed_values)
            except:
                kendall_tau = None

            # Confidence interval for MAE (bootstrap)
            ci_95 = self._bootstrap_confidence_interval(errors, statistic=np.mean)
        else:
            pearson_r = 1.0
            r_squared = 1.0
            spearman_rho = 1.0
            kendall_tau = None
            p_value = None
            ci_95 = None

        # Calculate success rates
        threshold = CHEMICAL_ACCURACY_HARTREE if units == "Hartree" else CHEMICAL_ACCURACY_KCAL
        chemical_accuracy_rate = float(np.sum(errors <= threshold) / len(errors))
        tight_accuracy_rate = float(np.sum(errors <= threshold * 0.5) / len(errors))
        relaxed_accuracy_rate = float(np.sum(errors <= threshold * 2) / len(errors))

        accuracy = ChemicalAccuracy(
            method=method,
            num_samples=len(method_results),
            mae=mae,
            rmse=rmse,
            max_error=max_error,
            min_error=min_error,
            std_dev=std_dev,
            r_squared=r_squared,
            pearson_r=pearson_r,
            spearman_rho=spearman_rho,
            kendall_tau=kendall_tau,
            chemical_accuracy_rate=chemical_accuracy_rate,
            tight_accuracy_rate=tight_accuracy_rate,
            relaxed_accuracy_rate=relaxed_accuracy_rate,
            p_value=p_value,
            confidence_interval_95=ci_95,
            units=units,
            metadata={
                'reference_values': reference_values.tolist(),
                'computed_values': computed_values.tolist(),
                'errors': errors.tolist()
            }
        )

        self.accuracy_metrics[method] = accuracy
        logger.info(f"Accuracy calculated: MAE={mae:.4f}, R²={r_squared:.4f}")

        return accuracy

    def _bootstrap_confidence_interval(
        self,
        data: np.ndarray,
        statistic: callable = np.mean,
        n_bootstrap: int = 1000,
        confidence: float = 0.95
    ) -> Tuple[float, float]:
        """
        Calculate bootstrap confidence interval.

        Args:
            data: Input data
            statistic: Function to calculate statistic
            n_bootstrap: Number of bootstrap samples
            confidence: Confidence level (default: 0.95)

        Returns:
            (lower_bound, upper_bound) tuple
        """
        bootstrap_stats = []
        n = len(data)

        for _ in range(n_bootstrap):
            # Resample with replacement
            sample = np.random.choice(data, size=n, replace=True)
            bootstrap_stats.append(statistic(sample))

        # Calculate percentiles
        alpha = 1 - confidence
        lower = np.percentile(bootstrap_stats, 100 * alpha / 2)
        upper = np.percentile(bootstrap_stats, 100 * (1 - alpha / 2))

        return (float(lower), float(upper))

    def compare_methods(
        self,
        method_a: str,
        method_b: str,
        reference_field: str = "reference_value"
    ) -> AccuracyComparison:
        """
        Statistically compare accuracy of two methods.

        Args:
            method_a: First method name
            method_b: Second method name
            reference_field: Field name for reference values

        Returns:
            AccuracyComparison object
        """
        logger.info(f"Comparing methods: {method_a} vs {method_b}")

        # Get results for both methods on same molecules
        results_a = [r for r in self.results if r.method == method_a and r.success]
        results_b = [r for r in self.results if r.method == method_b and r.success]

        # Find common molecules
        molecules_a = {r.molecule for r in results_a}
        molecules_b = {r.molecule for r in results_b}
        common_molecules = molecules_a & molecules_b

        if not common_molecules:
            raise ValueError(f"No common molecules between {method_a} and {method_b}")

        # Extract paired errors
        errors_a = []
        errors_b = []

        for molecule in common_molecules:
            ra = next(r for r in results_a if r.molecule == molecule)
            rb = next(r for r in results_b if r.molecule == molecule)

            if ra.absolute_error is not None and rb.absolute_error is not None:
                errors_a.append(ra.absolute_error)
                errors_b.append(rb.absolute_error)

        errors_a = np.array(errors_a)
        errors_b = np.array(errors_b)

        # Calculate improvement metrics
        mae_a = np.mean(errors_a)
        mae_b = np.mean(errors_b)
        mae_improvement = ((mae_b - mae_a) / mae_b) * 100 if mae_b > 0 else 0

        rmse_a = np.sqrt(np.mean(errors_a ** 2))
        rmse_b = np.sqrt(np.mean(errors_b ** 2))
        rmse_improvement = ((rmse_b - rmse_a) / rmse_b) * 100 if rmse_b > 0 else 0

        # Get correlation improvement if available
        if method_a in self.accuracy_metrics and method_b in self.accuracy_metrics:
            r2_a = self.accuracy_metrics[method_a].r_squared
            r2_b = self.accuracy_metrics[method_b].r_squared
            correlation_improvement = ((r2_a - r2_b) / (1 - r2_b)) * 100 if r2_b < 1 else 0
        else:
            correlation_improvement = 0

        # Paired t-test
        t_stat, p_value = stats.ttest_rel(errors_a, errors_b)
        significantly_different = p_value < 0.05

        # Determine winner
        if mae_a < mae_b:
            winner = method_a
            confidence = 1 - p_value if significantly_different else 0.5
        elif mae_b < mae_a:
            winner = method_b
            confidence = 1 - p_value if significantly_different else 0.5
        else:
            winner = "tie"
            confidence = 0.5

        comparison = AccuracyComparison(
            method_a=method_a,
            method_b=method_b,
            num_samples=len(errors_a),
            mae_improvement=mae_improvement,
            rmse_improvement=rmse_improvement,
            correlation_improvement=correlation_improvement,
            paired_t_statistic=float(t_stat),
            paired_t_pvalue=float(p_value),
            significantly_different=significantly_different,
            winner=winner,
            confidence=confidence,
            metadata={
                'mae_a': float(mae_a),
                'mae_b': float(mae_b),
                'rmse_a': float(rmse_a),
                'rmse_b': float(rmse_b),
                'common_molecules': list(common_molecules)
            }
        )

        self.comparisons.append(comparison)
        return comparison

    def generate_accuracy_report(self) -> str:
        """
        Generate human-readable accuracy report.

        Returns:
            Formatted report string
        """
        lines = []
        lines.append("=" * 80)
        lines.append("CHEMICAL ACCURACY VALIDATION REPORT")
        lines.append("=" * 80)
        lines.append("")

        if not self.accuracy_metrics:
            lines.append("No accuracy data available. Run calculate_accuracy() first.")
            return "\n".join(lines)

        # Summary table
        lines.append("ACCURACY SUMMARY BY METHOD:")
        lines.append("-" * 80)
        lines.append(f"{'Method':<25} {'MAE':<12} {'RMSE':<12} {'R²':<10} {'Success%':<10} {'Status'}")
        lines.append("-" * 80)

        for method, acc in sorted(self.accuracy_metrics.items(), key=lambda x: x[1].mae):
            status = "PASS" if acc.passes_chemical_accuracy() else "FAIL"
            lines.append(
                f"{method:<25} {acc.mae:>10.6f}  {acc.rmse:>10.6f}  {acc.r_squared:>8.4f}  "
                f"{acc.chemical_accuracy_rate*100:>8.1f}%  {status}"
            )

        lines.append("")

        # Detailed statistics for each method
        lines.append("DETAILED ACCURACY STATISTICS:")
        lines.append("-" * 80)

        for method, acc in self.accuracy_metrics.items():
            lines.append(f"\n{method}:")
            lines.append(f"  Samples: {acc.num_samples}")
            lines.append(f"  MAE: {acc.mae:.6f} {acc.units}")
            lines.append(f"  RMSE: {acc.rmse:.6f} {acc.units}")
            lines.append(f"  Max Error: {acc.max_error:.6f} {acc.units}")
            lines.append(f"  Min Error: {acc.min_error:.6f} {acc.units}")
            lines.append(f"  Std Dev: {acc.std_dev:.6f} {acc.units}")
            lines.append(f"  R²: {acc.r_squared:.4f}")
            lines.append(f"  Pearson r: {acc.pearson_r:.4f}")
            lines.append(f"  Spearman ρ: {acc.spearman_rho:.4f}")
            lines.append(f"  Chemical accuracy rate: {acc.chemical_accuracy_rate*100:.1f}%")
            lines.append(f"  Tight accuracy rate: {acc.tight_accuracy_rate*100:.1f}%")
            if acc.confidence_interval_95:
                lines.append(f"  95% CI: [{acc.confidence_interval_95[0]:.6f}, {acc.confidence_interval_95[1]:.6f}]")

        lines.append("")

        # Method comparisons
        if self.comparisons:
            lines.append("METHOD COMPARISONS:")
            lines.append("-" * 80)

            for comp in self.comparisons:
                lines.append(f"\n{comp.method_a} vs {comp.method_b}:")
                lines.append(f"  Samples: {comp.num_samples}")
                lines.append(f"  MAE improvement: {comp.mae_improvement:+.2f}%")
                lines.append(f"  RMSE improvement: {comp.rmse_improvement:+.2f}%")
                lines.append(f"  Paired t-test: t={comp.paired_t_statistic:.3f}, p={comp.paired_t_pvalue:.4f}")
                lines.append(f"  Significantly different: {comp.significantly_different}")
                lines.append(f"  Winner: {comp.winner} (confidence: {comp.confidence:.2f})")

        lines.append("")
        lines.append("=" * 80)
        lines.append(f"Legend: Chemical accuracy = {CHEMICAL_ACCURACY_KCAL} kcal/mol = {CHEMICAL_ACCURACY_HARTREE} Hartree")
        lines.append("=" * 80)

        return "\n".join(lines)

    def calculate_all_accuracies(self, units: str = "Hartree") -> Dict[str, ChemicalAccuracy]:
        """
        Calculate accuracy metrics for all methods in results.

        Args:
            units: Units for energy values

        Returns:
            Dictionary mapping method names to ChemicalAccuracy objects
        """
        methods = set(r.method for r in self.results if r.success)

        for method in methods:
            try:
                self.calculate_accuracy(method, units=units)
            except Exception as e:
                logger.warning(f"Could not calculate accuracy for {method}: {e}")

        return self.accuracy_metrics

    def rank_methods_by_accuracy(self) -> List[Tuple[str, float]]:
        """
        Rank methods by MAE (lower is better).

        Returns:
            List of (method_name, mae) tuples sorted by MAE
        """
        if not self.accuracy_metrics:
            self.calculate_all_accuracies()

        rankings = [(method, acc.mae) for method, acc in self.accuracy_metrics.items()]
        rankings.sort(key=lambda x: x[1])

        return rankings


# Convenience functions

def quick_accuracy_check(results: List[Any], method: str) -> Dict[str, Any]:
    """
    Quick accuracy check for a method.

    Args:
        results: List of benchmark results
        method: Method name to check

    Returns:
        Dictionary with accuracy summary
    """
    analyzer = AccuracyAnalyzer()
    analyzer.add_results(results)
    accuracy = analyzer.calculate_accuracy(method)

    return {
        'method': method,
        'mae': accuracy.mae,
        'rmse': accuracy.rmse,
        'r_squared': accuracy.r_squared,
        'passes_chemical_accuracy': accuracy.passes_chemical_accuracy(),
        'success_rate': accuracy.chemical_accuracy_rate,
        'summary': f"MAE: {accuracy.mae:.4f}, R²: {accuracy.r_squared:.4f}, Success: {accuracy.chemical_accuracy_rate*100:.1f}%"
    }


__all__ = [
    "AccuracyAnalyzer",
    "ChemicalAccuracy",
    "AccuracyComparison",
    "quick_accuracy_check",
    "CHEMICAL_ACCURACY_HARTREE",
    "CHEMICAL_ACCURACY_KCAL",
]
