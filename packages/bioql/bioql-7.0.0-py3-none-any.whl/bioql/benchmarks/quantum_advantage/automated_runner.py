# Copyright 2024-2025 SpectrixRD
# Licensed under the Apache License, Version 2.0
# See LICENSE file in the project root for full license text

"""
Automated Benchmark Runner

Schedule and run benchmarks automatically (nightly, weekly, etc.)
with email alerts and database storage.
"""

import json
import sqlite3
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, List, Optional, Any
from loguru import logger


class BenchmarkScheduler:
    """
    Automated benchmark scheduler.

    Example:
        >>> scheduler = BenchmarkScheduler()
        >>> scheduler.run_nightly_benchmarks()
        >>> scheduler.send_alert("team@bioql.bio")
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize scheduler.

        Args:
            db_path: Path to SQLite database for results storage
        """
        self.db_path = db_path or "benchmark_results.db"
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database for storing results."""
        logger.info(f"Initializing database: {self.db_path}")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS benchmark_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                scenario TEXT,
                num_results INTEGER,
                success_rate REAL,
                mean_speedup REAL,
                mean_error REAL,
                duration_seconds REAL,
                metadata TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS benchmark_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER,
                timestamp TEXT NOT NULL,
                scenario TEXT,
                molecule TEXT,
                method TEXT,
                wall_time REAL,
                computed_value REAL,
                reference_value REAL,
                absolute_error REAL,
                relative_error REAL,
                success BOOLEAN,
                qubits_used INTEGER,
                metadata TEXT,
                FOREIGN KEY (run_id) REFERENCES benchmark_runs(id)
            )
        """)

        conn.commit()
        conn.close()

        logger.info("Database initialized successfully")

    def run_nightly_benchmarks(
        self,
        backend: str = "ibm_torino",
        shots: int = 1024
    ) -> Dict[str, Any]:
        """
        Run complete nightly benchmark suite.

        Args:
            backend: Quantum backend to use
            shots: Number of shots per run

        Returns:
            Summary of benchmark run
        """
        logger.info("Starting nightly benchmark run")

        from .benchmark_suite import BenchmarkSuite

        start_time = datetime.now()

        # Initialize and run benchmark suite
        suite = BenchmarkSuite()
        results = suite.run_all_scenarios(backend=backend, shots=shots)

        duration = (datetime.now() - start_time).total_seconds()

        # Save results
        results_file = suite.save_results()

        # Store in database
        run_summary = self._store_results(suite, duration)

        logger.info(f"Nightly benchmark complete in {duration:.1f}s")

        return {
            'timestamp': start_time.isoformat(),
            'duration': duration,
            'num_results': len(results),
            'results_file': str(results_file),
            'summary': run_summary
        }

    def _store_results(self, suite: Any, duration: float) -> Dict[str, Any]:
        """Store results in database."""
        logger.info("Storing results in database")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Calculate summary statistics
        stats = suite.get_summary_statistics()

        # Insert run record
        cursor.execute("""
            INSERT INTO benchmark_runs
            (timestamp, num_results, success_rate, mean_error, duration_seconds, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            len(suite.results),
            stats.get('success_rate', 0),
            stats.get('accuracy', {}).get('mae', None),
            duration,
            json.dumps(stats)
        ))

        run_id = cursor.lastrowid

        # Insert individual results
        for result in suite.results:
            cursor.execute("""
                INSERT INTO benchmark_results
                (run_id, timestamp, scenario, molecule, method, wall_time,
                 computed_value, reference_value, absolute_error, relative_error,
                 success, qubits_used, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                run_id,
                result.timestamp,
                result.scenario,
                result.molecule,
                result.method,
                result.wall_time,
                result.computed_value,
                result.reference_value,
                result.absolute_error,
                result.relative_error,
                result.success,
                result.qubits_used,
                json.dumps(result.metadata)
            ))

        conn.commit()
        conn.close()

        logger.info(f"Stored run {run_id} with {len(suite.results)} results")

        return {
            'run_id': run_id,
            'stats': stats
        }

    def send_alert(
        self,
        recipients: List[str],
        subject: str = "BioQL Benchmark Alert",
        summary: Optional[Dict[str, Any]] = None
    ):
        """
        Send email alert with benchmark results.

        Args:
            recipients: List of email addresses
            subject: Email subject
            summary: Benchmark summary to include
        """
        logger.info(f"Sending alert to {len(recipients)} recipients")

        # Build email content
        body = self._build_alert_email(summary)

        # Send email (requires SMTP configuration)
        # This is a template - configure with actual SMTP settings
        try:
            msg = MIMEMultipart()
            msg['From'] = "benchmarks@bioql.bio"
            msg['To'] = ", ".join(recipients)
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'html'))

            # SMTP configuration needed
            # server = smtplib.SMTP('smtp.gmail.com', 587)
            # server.starttls()
            # server.login("user", "password")
            # server.send_message(msg)
            # server.quit()

            logger.info("Alert email prepared (SMTP not configured)")

        except Exception as e:
            logger.error(f"Failed to send alert: {e}")

    def _build_alert_email(self, summary: Optional[Dict[str, Any]]) -> str:
        """Build HTML email for alert."""
        html = f"""
        <html>
        <body>
            <h2>BioQL Benchmark Report</h2>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        """

        if summary:
            html += f"""
            <h3>Summary</h3>
            <ul>
                <li>Total runs: {summary.get('num_results', 'N/A')}</li>
                <li>Success rate: {summary.get('summary', {}).get('stats', {}).get('success_rate', 0)*100:.1f}%</li>
                <li>Duration: {summary.get('duration', 0):.1f} seconds</li>
            </ul>
            """

        html += """
        </body>
        </html>
        """

        return html

    def check_for_regressions(self, threshold: float = 0.1) -> List[Dict[str, Any]]:
        """
        Check for performance regressions compared to previous runs.

        Args:
            threshold: Threshold for regression detection (10% by default)

        Returns:
            List of detected regressions
        """
        logger.info("Checking for regressions")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get last two runs
        cursor.execute("""
            SELECT id, mean_speedup, mean_error
            FROM benchmark_runs
            ORDER BY timestamp DESC
            LIMIT 2
        """)

        runs = cursor.fetchall()
        conn.close()

        if len(runs) < 2:
            logger.info("Not enough runs for regression analysis")
            return []

        current_run = runs[0]
        previous_run = runs[1]

        regressions = []

        # Check speedup regression
        if current_run[1] and previous_run[1]:
            speedup_change = (current_run[1] - previous_run[1]) / previous_run[1]
            if speedup_change < -threshold:
                regressions.append({
                    'metric': 'speedup',
                    'change': speedup_change,
                    'current': current_run[1],
                    'previous': previous_run[1]
                })

        # Check accuracy regression
        if current_run[2] and previous_run[2]:
            error_change = (current_run[2] - previous_run[2]) / previous_run[2]
            if error_change > threshold:
                regressions.append({
                    'metric': 'error',
                    'change': error_change,
                    'current': current_run[2],
                    'previous': previous_run[2]
                })

        if regressions:
            logger.warning(f"Detected {len(regressions)} regressions")
        else:
            logger.info("No regressions detected")

        return regressions


__all__ = ["BenchmarkScheduler"]
