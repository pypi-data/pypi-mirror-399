# Copyright 2024-2025 SpectrixRD
# Licensed under the Apache License, Version 2.0
# See LICENSE file in the project root for full license text

"""
Results Reporter

Generate comprehensive HTML/PDF reports and dashboards from benchmark results.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
from loguru import logger


class BenchmarkReporter:
    """
    Generate comprehensive benchmark reports.

    Example:
        >>> from bioql.benchmarks.quantum_advantage import BenchmarkReporter
        >>> reporter = BenchmarkReporter()
        >>> reporter.load_results("benchmark_results.json")
        >>> reporter.generate_html_report("report.html")
        >>> reporter.generate_dashboard("dashboard.html")
    """

    def __init__(self, results: Optional[List[Any]] = None):
        """
        Initialize reporter.

        Args:
            results: Optional list of BenchmarkResult objects
        """
        self.results = results or []
        self.metadata = {}

    def load_results(self, filepath: str):
        """Load results from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)

        self.metadata = data.get('metadata', {})
        self.results = data.get('results', [])

        logger.info(f"Loaded {len(self.results)} results from {filepath}")

    def generate_html_report(self, output_path: str):
        """
        Generate comprehensive HTML report.

        Args:
            output_path: Path for output HTML file
        """
        logger.info(f"Generating HTML report: {output_path}")

        html = self._build_html_report()

        with open(output_path, 'w') as f:
            f.write(html)

        logger.info(f"HTML report saved to {output_path}")
        return output_path

    def _build_html_report(self) -> str:
        """Build HTML report content."""
        html = []

        # Header
        html.append("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BioQL Quantum Advantage Benchmark Report</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .summary-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .card h3 {
            margin-top: 0;
            color: #667eea;
        }
        .metric {
            font-size: 32px;
            font-weight: bold;
            color: #333;
        }
        .metric-label {
            color: #666;
            font-size: 14px;
        }
        table {
            width: 100%;
            background: white;
            border-collapse: collapse;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        th {
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
        }
        td {
            padding: 12px;
            border-bottom: 1px solid #eee;
        }
        tr:hover {
            background: #f9f9f9;
        }
        .success { color: #10b981; font-weight: bold; }
        .failure { color: #ef4444; font-weight: bold; }
        .advantage { background: #d1fae5; }
        .footer {
            text-align: center;
            color: #666;
            margin-top: 40px;
            padding: 20px;
        }
    </style>
</head>
<body>
""")

        # Title
        html.append(f"""
    <div class="header">
        <h1>Quantum Advantage Benchmark Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Total Results: {len(self.results)}</p>
    </div>
""")

        # Summary cards
        html.append(self._build_summary_cards())

        # Results table
        html.append(self._build_results_table())

        # Performance comparison
        html.append(self._build_performance_section())

        # Accuracy comparison
        html.append(self._build_accuracy_section())

        # Footer
        html.append("""
    <div class="footer">
        <p>BioQL Quantum Advantage Benchmarking Suite v1.0</p>
        <p>SpectrixRD &copy; 2024-2025</p>
    </div>
</body>
</html>
""")

        return ''.join(html)

    def _build_summary_cards(self) -> str:
        """Build summary statistics cards."""
        if not self.results:
            return ""

        successful = sum(1 for r in self.results if r.get('success', True))
        quantum_methods = {'fmo_vqe', 'dc_qaoa', 'standard_vqe', 'transcorrelated_vqe'}
        quantum_results = [r for r in self.results if r.get('method', '') in quantum_methods]
        classical_results = [r for r in self.results if r.get('method', '') not in quantum_methods]

        # Calculate average speedup
        avg_speedup = "N/A"
        if quantum_results and classical_results:
            q_times = [r.get('wall_time', 0) for r in quantum_results if r.get('wall_time')]
            c_times = [r.get('wall_time', 0) for r in classical_results if r.get('wall_time')]
            if q_times and c_times:
                avg_speedup = f"{np.mean(c_times) / np.mean(q_times):.1f}x"

        # Calculate average accuracy
        avg_error = "N/A"
        results_with_error = [r for r in self.results if r.get('absolute_error') is not None]
        if results_with_error:
            errors = [r['absolute_error'] for r in results_with_error]
            avg_error = f"{np.mean(errors):.4f} Ha"

        html = f"""
    <div class="summary-cards">
        <div class="card">
            <h3>Success Rate</h3>
            <div class="metric">{100 * successful / len(self.results):.1f}%</div>
            <div class="metric-label">{successful}/{len(self.results)} passed</div>
        </div>
        <div class="card">
            <h3>Average Speedup</h3>
            <div class="metric">{avg_speedup}</div>
            <div class="metric-label">Quantum vs Classical</div>
        </div>
        <div class="card">
            <h3>Average Error</h3>
            <div class="metric">{avg_error}</div>
            <div class="metric-label">Mean Absolute Error</div>
        </div>
        <div class="card">
            <h3>Quantum Runs</h3>
            <div class="metric">{len(quantum_results)}</div>
            <div class="metric-label">vs {len(classical_results)} classical</div>
        </div>
    </div>
"""
        return html

    def _build_results_table(self) -> str:
        """Build detailed results table."""
        if not self.results:
            return ""

        html = ['<h2>Detailed Results</h2>']
        html.append('<table>')
        html.append('<thead><tr>')
        html.append('<th>Scenario</th><th>Molecule</th><th>Method</th>')
        html.append('<th>Time (s)</th><th>Error</th><th>Status</th>')
        html.append('</tr></thead>')
        html.append('<tbody>')

        for r in self.results:
            status_class = 'success' if r.get('success', True) else 'failure'
            status_text = 'PASS' if r.get('success', True) else 'FAIL'

            error_text = 'N/A'
            if r.get('absolute_error') is not None:
                error_text = f"{r['absolute_error']:.6f}"

            html.append(f"<tr class='{status_class if r.get('success') else ''}'>")
            html.append(f"<td>{r.get('scenario', 'N/A')}</td>")
            html.append(f"<td>{r.get('molecule', 'N/A')}</td>")
            html.append(f"<td>{r.get('method', 'N/A')}</td>")
            html.append(f"<td>{r.get('wall_time', 0):.4f}</td>")
            html.append(f"<td>{error_text}</td>")
            html.append(f"<td class='{status_class}'>{status_text}</td>")
            html.append('</tr>')

        html.append('</tbody></table>')
        return ''.join(html)

    def _build_performance_section(self) -> str:
        """Build performance comparison section."""
        html = ['<h2>Performance Analysis</h2>']
        html.append('<div class="card">')
        html.append('<p>Quantum vs Classical speedup comparison</p>')
        html.append('</div>')
        return ''.join(html)

    def _build_accuracy_section(self) -> str:
        """Build accuracy comparison section."""
        html = ['<h2>Accuracy Analysis</h2>']
        html.append('<div class="card">')
        html.append('<p>Chemical accuracy validation results</p>')
        html.append('</div>')
        return ''.join(html)

    def generate_dashboard(self, output_path: str):
        """Generate interactive dashboard."""
        logger.info(f"Generating dashboard: {output_path}")

        # For now, use same HTML report
        # In production, could integrate with Plotly, Chart.js, etc.
        return self.generate_html_report(output_path)

    def generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics."""
        if not self.results:
            return {}

        successful = [r for r in self.results if r.get('success', True)]
        quantum_methods = {'fmo_vqe', 'dc_qaoa', 'standard_vqe', 'transcorrelated_vqe'}

        quantum_results = [r for r in successful if r.get('method', '') in quantum_methods]
        classical_results = [r for r in successful if r.get('method', '') not in quantum_methods]

        summary = {
            'total_runs': len(self.results),
            'successful_runs': len(successful),
            'success_rate': len(successful) / len(self.results) if self.results else 0,
            'quantum_runs': len(quantum_results),
            'classical_runs': len(classical_results),
        }

        # Timing statistics
        if quantum_results:
            q_times = [r['wall_time'] for r in quantum_results if 'wall_time' in r]
            if q_times:
                summary['quantum_mean_time'] = float(np.mean(q_times))
                summary['quantum_median_time'] = float(np.median(q_times))

        if classical_results:
            c_times = [r['wall_time'] for r in classical_results if 'wall_time' in r]
            if c_times:
                summary['classical_mean_time'] = float(np.mean(c_times))
                summary['classical_median_time'] = float(np.median(c_times))

        # Accuracy statistics
        results_with_error = [r for r in successful if r.get('absolute_error') is not None]
        if results_with_error:
            errors = [r['absolute_error'] for r in results_with_error]
            summary['mae'] = float(np.mean(errors))
            summary['rmse'] = float(np.sqrt(np.mean([e**2 for e in errors])))

        return summary


__all__ = ["BenchmarkReporter"]
