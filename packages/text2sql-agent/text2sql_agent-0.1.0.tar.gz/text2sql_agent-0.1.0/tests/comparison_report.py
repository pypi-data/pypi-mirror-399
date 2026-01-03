"""
Comparison Report Generator for SQL Agent Toolkit Tests

Generates HTML comparison reports showing test results across different
database (SQLite vs PostgreSQL) and LLM provider (Ollama vs Groq) combinations.

Usage:
    # Automatically generated after pytest run via conftest.py hook
    # Or manually:
    from comparison_report import ComparisonReportGenerator
    generator = ComparisonReportGenerator()
    html = generator.generate_report(test_results)
    generator.save_report(html, "reports/comparison_report.html")
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict


class ComparisonReportGenerator:
    """Generate comparison reports for test results across databases and LLMs"""

    def __init__(self, report_dir: str = "reports"):
        """
        Initialize comparison report generator

        Args:
            report_dir: Directory to save reports (default: "reports")
        """
        self.report_dir = report_dir
        os.makedirs(report_dir, exist_ok=True)

    def collect_results(self, pytest_session) -> Dict[str, Any]:
        """
        Collect test results from pytest session

        Args:
            pytest_session: pytest session object

        Returns:
            Dictionary with organized test results by database and LLM
        """
        results = {
            "sqlite": {"ollama": [], "groq": [], "gemini": [], "openai": [], "anthropic": []},
            "postgres": {"ollama": [], "groq": [], "gemini": [], "openai": [], "anthropic": []},
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "by_database": defaultdict(lambda: {"passed": 0, "failed": 0, "skipped": 0}),
                "by_llm": defaultdict(lambda: {"passed": 0, "failed": 0, "skipped": 0}),
            }
        }

        # Iterate through all test items
        for item in pytest_session.items:
            # Get test result from session
            test_result = {
                "name": item.nodeid,
                "outcome": "unknown",
                "duration": 0,
                "database": "unknown",
                "llm": "unknown",
            }

            # Try to extract database and LLM info from markers or test name
            if hasattr(item, 'callspec') and hasattr(item.callspec, 'params'):
                params = item.callspec.params
                if 'db_fixture' in params:
                    db_name = params['db_fixture']
                    test_result["database"] = "postgres" if "postgres" in db_name else "sqlite"

            # Check markers
            if hasattr(item, 'keywords'):
                if 'postgres' in item.keywords:
                    test_result["database"] = "postgres"
                elif 'sqlite' in item.keywords:
                    test_result["database"] = "sqlite"

                if 'ollama' in item.keywords:
                    test_result["llm"] = "ollama"
                elif 'groq' in item.keywords:
                    test_result["llm"] = "groq"

            # Store result
            db = test_result["database"]
            llm = test_result["llm"]

            if db in results and llm in results[db]:
                results[db][llm].append(test_result)

        return results

    def generate_html_report(self, results: Dict[str, Any], summary_stats: Optional[Dict] = None) -> str:
        """
        Generate HTML comparison report

        Args:
            results: Test results dictionary
            summary_stats: Optional summary statistics

        Returns:
            HTML string
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Calculate statistics if not provided
        if summary_stats is None:
            summary_stats = self._calculate_statistics(results)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SQL Agent Toolkit - Comparison Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-left: 4px solid #3498db;
            padding-left: 12px;
        }}
        .timestamp {{
            color: #7f8c8d;
            font-size: 14px;
            margin-bottom: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background-color: white;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border: 1px solid #ddd;
        }}
        th {{
            background-color: #3498db;
            color: white;
            font-weight: 600;
        }}
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        tr:hover {{
            background-color: #e8f4f8;
        }}
        .pass {{
            color: #27ae60;
            font-weight: bold;
        }}
        .fail {{
            color: #e74c3c;
            font-weight: bold;
        }}
        .skip {{
            color: #f39c12;
            font-weight: bold;
        }}
        .metric {{
            display: inline-block;
            padding: 8px 16px;
            margin: 5px;
            border-radius: 4px;
            font-weight: 600;
        }}
        .metric.pass {{
            background-color: #d5f4e6;
            border: 1px solid #27ae60;
        }}
        .metric.fail {{
            background-color: #fadbd8;
            border: 1px solid #e74c3c;
        }}
        .metric.skip {{
            background-color: #fdeaa8;
            border: 1px solid #f39c12;
        }}
        .comparison-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .card {{
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 20px;
        }}
        .card h3 {{
            margin-top: 0;
            color: #2c3e50;
        }}
        .percentage {{
            font-size: 32px;
            font-weight: bold;
            margin: 10px 0;
        }}
        .percentage.high {{
            color: #27ae60;
        }}
        .percentage.medium {{
            color: #f39c12;
        }}
        .percentage.low {{
            color: #e74c3c;
        }}
        .legend {{
            margin: 20px 0;
            padding: 15px;
            background-color: #ecf0f1;
            border-radius: 4px;
        }}
        .legend-item {{
            display: inline-block;
            margin-right: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔬 SQL Agent Toolkit - Comparison Report</h1>
        <div class="timestamp">Generated: {timestamp}</div>

        <!-- Overall Summary -->
        <h2>📊 Overall Summary</h2>
        <div class="comparison-grid">
            <div class="card">
                <h3>Total Tests</h3>
                <div class="percentage">{summary_stats.get('total_tests', 0)}</div>
                <div class="metric pass">✓ Passed: {summary_stats.get('passed', 0)}</div>
                <div class="metric fail">✗ Failed: {summary_stats.get('failed', 0)}</div>
                <div class="metric skip">⊘ Skipped: {summary_stats.get('skipped', 0)}</div>
            </div>
            <div class="card">
                <h3>Pass Rate</h3>
                <div class="percentage high">{summary_stats.get('pass_rate', 0):.1f}%</div>
            </div>
        </div>

        <!-- Database Comparison -->
        <h2>💾 Database Comparison: SQLite vs PostgreSQL</h2>
        <table>
            <thead>
                <tr>
                    <th>Database</th>
                    <th>Passed</th>
                    <th>Failed</th>
                    <th>Skipped</th>
                    <th>Pass Rate</th>
                </tr>
            </thead>
            <tbody>
                {self._generate_db_comparison_rows(summary_stats)}
            </tbody>
        </table>

        <!-- LLM Provider Comparison -->
        <h2>🤖 LLM Provider Comparison: Ollama vs Groq</h2>
        <table>
            <thead>
                <tr>
                    <th>LLM Provider</th>
                    <th>Passed</th>
                    <th>Failed</th>
                    <th>Skipped</th>
                    <th>Pass Rate</th>
                </tr>
            </thead>
            <tbody>
                {self._generate_llm_comparison_rows(summary_stats)}
            </tbody>
        </table>

        <!-- Detailed Results by Combination -->
        <h2>📋 Detailed Results by Combination</h2>
        <div class="comparison-grid">
            {self._generate_combination_cards(summary_stats)}
        </div>

        <!-- Legend -->
        <div class="legend">
            <strong>Legend:</strong>
            <div class="legend-item"><span class="pass">✓ Pass</span> - Test executed successfully</div>
            <div class="legend-item"><span class="fail">✗ Fail</span> - Test failed</div>
            <div class="legend-item"><span class="skip">⊘ Skip</span> - Test skipped (missing dependencies)</div>
        </div>

        <!-- Environment Info -->
        <h2>⚙️ Environment Information</h2>
        <table>
            <tr>
                <th>Item</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>Report Generated</td>
                <td>{timestamp}</td>
            </tr>
            <tr>
                <td>Databases Tested</td>
                <td>SQLite, PostgreSQL</td>
            </tr>
            <tr>
                <td>LLM Providers Tested</td>
                <td>Ollama, Groq</td>
            </tr>
        </table>

        <!-- Footer -->
        <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #7f8c8d; text-align: center;">
            <p>SQL Agent Toolkit - Test Comparison Report</p>
            <p>For more information, see the project README</p>
        </div>
    </div>
</body>
</html>"""
        return html

    def _calculate_statistics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate summary statistics from results"""
        stats = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "pass_rate": 0,
            "by_database": {},
            "by_llm": {},
            "by_combination": {}
        }

        # Placeholder for now - will be populated from actual test results
        return stats

    def _generate_db_comparison_rows(self, summary_stats: Dict) -> str:
        """Generate HTML rows for database comparison"""
        db_stats = summary_stats.get('by_database', {})

        rows = []
        for db_name in ['sqlite', 'postgres']:
            db_data = db_stats.get(db_name, {"passed": 0, "failed": 0, "skipped": 0})
            total = db_data['passed'] + db_data['failed']
            pass_rate = (db_data['passed'] / total * 100) if total > 0 else 0

            rows.append(f"""
                <tr>
                    <td><strong>{db_name.upper()}</strong></td>
                    <td class="pass">{db_data['passed']}</td>
                    <td class="fail">{db_data['failed']}</td>
                    <td class="skip">{db_data['skipped']}</td>
                    <td>{pass_rate:.1f}%</td>
                </tr>
            """)

        return "\n".join(rows)

    def _generate_llm_comparison_rows(self, summary_stats: Dict) -> str:
        """Generate HTML rows for LLM provider comparison"""
        llm_stats = summary_stats.get('by_llm', {})

        rows = []
        for llm_name in ['ollama', 'groq', 'gemini', 'openai', 'anthropic']:
            llm_data = llm_stats.get(llm_name, {"passed": 0, "failed": 0, "skipped": 0})
            total = llm_data['passed'] + llm_data['failed']
            pass_rate = (llm_data['passed'] / total * 100) if total > 0 else 0

            rows.append(f"""
                <tr>
                    <td><strong>{llm_name.upper()}</strong></td>
                    <td class="pass">{llm_data['passed']}</td>
                    <td class="fail">{llm_data['failed']}</td>
                    <td class="skip">{llm_data['skipped']}</td>
                    <td>{pass_rate:.1f}%</td>
                </tr>
            """)

        return "\n".join(rows)

    def _generate_combination_cards(self, summary_stats: Dict) -> str:
        """Generate HTML cards for each database/LLM combination"""
        combinations = [
            ("sqlite", "ollama", "SQLite + Ollama"),
            ("sqlite", "groq", "SQLite + Groq"),
            ("postgres", "ollama", "PostgreSQL + Ollama"),
            ("postgres", "groq", "PostgreSQL + Groq"),
        ]

        cards = []
        for db, llm, title in combinations:
            combo_key = f"{db}_{llm}"
            combo_data = summary_stats.get('by_combination', {}).get(
                combo_key,
                {"passed": 0, "failed": 0, "skipped": 0}
            )
            total = combo_data['passed'] + combo_data['failed']
            pass_rate = (combo_data['passed'] / total * 100) if total > 0 else 0

            # Determine color class
            color_class = "high" if pass_rate >= 75 else ("medium" if pass_rate >= 50 else "low")

            cards.append(f"""
                <div class="card">
                    <h3>{title}</h3>
                    <div class="percentage {color_class}">{pass_rate:.1f}%</div>
                    <div class="metric pass">✓ {combo_data['passed']}</div>
                    <div class="metric fail">✗ {combo_data['failed']}</div>
                    <div class="metric skip">⊘ {combo_data['skipped']}</div>
                </div>
            """)

        return "\n".join(cards)

    def save_report(self, html: str, filename: Optional[str] = None) -> str:
        """
        Save HTML report to file

        Args:
            html: HTML string to save
            filename: Optional custom filename

        Returns:
            Path to saved report
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"comparison_report_{timestamp}.html"

        filepath = os.path.join(self.report_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)

        return filepath

    def generate_and_save(self, summary_stats: Dict[str, Any]) -> str:
        """
        Generate and save comparison report

        Args:
            summary_stats: Summary statistics dictionary

        Returns:
            Path to saved report
        """
        html = self.generate_html_report({}, summary_stats)
        return self.save_report(html)


def generate_comparison_report(session) -> Optional[str]:
    """
    Generate comparison report from pytest session

    This function is called from conftest.py pytest_sessionfinish hook

    Args:
        session: pytest session object

    Returns:
        Path to generated report or None if generation failed
    """
    try:
        generator = ComparisonReportGenerator()

        # Extract summary statistics from session
        summary_stats = {
            "total_tests": session.testscollected,
            "passed": session.testscollected - session.testsfailed,
            "failed": session.testsfailed,
            "skipped": 0,
            "pass_rate": 0,
            "by_database": {},
            "by_llm": {},
            "by_combination": {}
        }

        # Calculate pass rate
        if summary_stats["total_tests"] > 0:
            summary_stats["pass_rate"] = (summary_stats["passed"] / summary_stats["total_tests"]) * 100

        # Generate report
        report_path = generator.generate_and_save(summary_stats)
        return report_path

    except Exception as e:
        print(f"Warning: Could not generate comparison report: {e}")
        return None
