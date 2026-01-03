"""
SQL Agent Evaluation Framework

Evaluates SQL correctness, schema understanding, edge cases, ambiguity handling,
and error recovery for the SQL Agent Toolkit.
"""
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import time
import logging
from sqlalchemy import text
from sql_agent_toolkit import SQLAgent

# Set up logging for evaluation framework
logger = logging.getLogger(__name__)


class EvaluationCategory(Enum):
    """Categories of evaluations"""
    SQL_CORRECTNESS = "sql_correctness"
    SCHEMA_UNDERSTANDING = "schema_understanding"
    EDGE_CASES = "edge_cases"
    AMBIGUITY_HANDLING = "ambiguity_handling"
    ERROR_RECOVERY = "error_recovery"


@dataclass
class TestCase:
    """Individual test case for evaluation"""
    id: str
    category: EvaluationCategory
    question: str
    expected_sql: Optional[str] = None
    expected_results: Optional[List[Dict]] = None
    expected_tables: Optional[List[str]] = None  # For schema understanding
    expected_columns: Optional[List[str]] = None
    should_error: bool = False  # For error recovery tests
    description: str = ""
    difficulty: str = "medium"  # easy, medium, hard
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationResult:
    """Result of evaluating a single test case"""
    test_case_id: str
    category: EvaluationCategory
    passed: bool
    generated_sql: Optional[str] = None
    actual_results: Optional[List[Dict]] = None
    expected_results: Optional[List[Dict]] = None
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationReport:
    """Aggregated evaluation report"""
    total_tests: int
    passed_tests: int
    failed_tests: int
    pass_rate: float
    category_results: Dict[str, Dict[str, Any]]
    execution_time_ms: float
    failed_test_ids: List[str]
    results: List[EvaluationResult]


class SQLAgentEvaluator:
    """
    Main evaluator for SQL Agent Toolkit

    Evaluates:
    1. SQL Correctness - Does generated SQL return correct results?
    2. Schema Understanding - Does agent identify correct tables/columns?
    3. Edge Cases - Complex queries, aggregations, joins, etc.
    4. Ambiguity Handling - How does it handle vague questions?
    5. Error Recovery - How does it handle invalid requests?
    """

    def __init__(self, agent: SQLAgent, verbose: bool = False):
        """
        Initialize evaluator

        Args:
            agent: SQLAgent instance to evaluate
            verbose: Print detailed output during evaluation
        """
        self.agent = agent
        self.verbose = verbose

    def evaluate_test_case(self, test_case: TestCase) -> EvaluationResult:
        """
        Evaluate a single test case

        Args:
            test_case: Test case to evaluate

        Returns:
            EvaluationResult with pass/fail and metrics
        """
        start_time = time.time()

        try:
            # Execute query through agent
            result = self.agent.query(test_case.question)
            execution_time_ms = (time.time() - start_time) * 1000

            generated_sql = result.get('sql_query', '')
            answer = result.get('answer', '')
            results_str = result.get('results', '[]')

            # Parse results
            try:
                actual_results = json.loads(results_str) if results_str else []
            except json.JSONDecodeError:
                actual_results = []

            # Evaluate based on category
            if test_case.category == EvaluationCategory.SQL_CORRECTNESS:
                passed, metrics = self._evaluate_sql_correctness(
                    test_case, generated_sql, actual_results
                )
            elif test_case.category == EvaluationCategory.SCHEMA_UNDERSTANDING:
                passed, metrics = self._evaluate_schema_understanding(
                    test_case, generated_sql
                )
            elif test_case.category == EvaluationCategory.EDGE_CASES:
                passed, metrics = self._evaluate_edge_case(
                    test_case, generated_sql, actual_results
                )
            elif test_case.category == EvaluationCategory.AMBIGUITY_HANDLING:
                passed, metrics = self._evaluate_ambiguity_handling(
                    test_case, generated_sql, answer
                )
            elif test_case.category == EvaluationCategory.ERROR_RECOVERY:
                passed, metrics = self._evaluate_error_recovery(
                    test_case, result, generated_sql
                )
            else:
                passed = False
                metrics = {"error": "Unknown category"}

            return EvaluationResult(
                test_case_id=test_case.id,
                category=test_case.category,
                passed=passed,
                generated_sql=generated_sql,
                actual_results=actual_results,
                expected_results=test_case.expected_results,
                execution_time_ms=execution_time_ms,
                metrics=metrics
            )

        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000

            # For error recovery tests, errors might be expected
            if test_case.category == EvaluationCategory.ERROR_RECOVERY and test_case.should_error:
                return EvaluationResult(
                    test_case_id=test_case.id,
                    category=test_case.category,
                    passed=True,
                    error_message=str(e),
                    execution_time_ms=execution_time_ms,
                    metrics={"error_handled": True}
                )

            return EvaluationResult(
                test_case_id=test_case.id,
                category=test_case.category,
                passed=False,
                error_message=str(e),
                execution_time_ms=execution_time_ms,
                metrics={"unexpected_error": True}
            )

    def _evaluate_sql_correctness(
        self,
        test_case: TestCase,
        generated_sql: str,
        actual_results: List[Dict]
    ) -> Tuple[bool, Dict]:
        """Evaluate SQL correctness"""
        metrics = {}

        # Check if SQL was generated
        if not generated_sql:
            return False, {"error": "No SQL generated"}

        metrics["sql_generated"] = True

        # Compare with expected SQL (if provided)
        if test_case.expected_sql:
            sql_match = self._normalize_sql(generated_sql) == self._normalize_sql(test_case.expected_sql)
            metrics["sql_exact_match"] = sql_match

        # Compare results (if expected results provided)
        if test_case.expected_results is not None:
            results_match = self._compare_results(actual_results, test_case.expected_results)
            metrics["results_match"] = results_match

            # Pass if results match
            if results_match:
                return True, metrics

        # If only expected SQL provided, check if it's similar
        if test_case.expected_sql and not test_case.expected_results:
            # For now, consider it passed if SQL was generated successfully
            # In production, you might want more sophisticated SQL comparison
            return True, metrics

        # If expected results provided but don't match
        if test_case.expected_results is not None:
            return False, metrics

        # No expectations provided, consider pass if SQL generated
        return True, metrics

    def _evaluate_schema_understanding(
        self,
        test_case: TestCase,
        generated_sql: str
    ) -> Tuple[bool, Dict]:
        """Evaluate schema understanding"""
        metrics = {}

        if not generated_sql:
            return False, {"error": "No SQL generated"}

        sql_upper = generated_sql.upper()

        # Check if expected tables are referenced
        if test_case.expected_tables:
            tables_found = []
            tables_missing = []

            for table in test_case.expected_tables:
                if table.upper() in sql_upper:
                    tables_found.append(table)
                else:
                    tables_missing.append(table)

            metrics["tables_found"] = tables_found
            metrics["tables_missing"] = tables_missing
            metrics["tables_coverage"] = len(tables_found) / len(test_case.expected_tables)

        # Check if expected columns are referenced
        if test_case.expected_columns:
            columns_found = []
            columns_missing = []

            for column in test_case.expected_columns:
                if column.upper() in sql_upper or column.split('.')[-1].upper() in sql_upper:
                    columns_found.append(column)
                else:
                    columns_missing.append(column)

            metrics["columns_found"] = columns_found
            metrics["columns_missing"] = columns_missing
            metrics["columns_coverage"] = len(columns_found) / len(test_case.expected_columns)

        # Passed if all expected tables and columns found
        passed = (
            (not test_case.expected_tables or len(metrics.get("tables_missing", [])) == 0) and
            (not test_case.expected_columns or len(metrics.get("columns_missing", [])) == 0)
        )

        return passed, metrics

    def _evaluate_edge_case(
        self,
        test_case: TestCase,
        generated_sql: str,
        actual_results: List[Dict]
    ) -> Tuple[bool, Dict]:
        """Evaluate edge case handling"""
        metrics = {}

        if not generated_sql:
            return False, {"error": "No SQL generated"}

        sql_upper = generated_sql.upper()

        # Detect query complexity features
        features = {
            "has_join": any(join in sql_upper for join in ["JOIN", "INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "OUTER JOIN"]),
            "has_aggregation": any(agg in sql_upper for agg in ["COUNT", "SUM", "AVG", "MAX", "MIN"]),
            "has_group_by": "GROUP BY" in sql_upper,
            "has_having": "HAVING" in sql_upper,
            "has_subquery": "SELECT" in sql_upper and sql_upper.count("SELECT") > 1,
            "has_order_by": "ORDER BY" in sql_upper,
            "has_limit": "LIMIT" in sql_upper,
            "has_where": "WHERE" in sql_upper,
            "has_case": "CASE" in sql_upper,
        }

        metrics["query_features"] = features
        metrics["complexity_score"] = sum(features.values())

        # Compare with expected results if provided
        if test_case.expected_results is not None:
            results_match = self._compare_results(actual_results, test_case.expected_results)
            metrics["results_match"] = results_match
            return results_match, metrics

        # Otherwise, pass if SQL was generated with appropriate complexity
        return True, metrics

    def _evaluate_ambiguity_handling(
        self,
        test_case: TestCase,
        generated_sql: str,
        answer: str
    ) -> Tuple[bool, Dict]:
        """Evaluate ambiguity handling"""
        metrics = {}

        # For ambiguous questions, we check if:
        # 1. SQL was generated (agent made reasonable assumptions)
        # 2. Answer acknowledges assumptions or provides clarification

        if not generated_sql:
            metrics["sql_generated"] = False
        else:
            metrics["sql_generated"] = True

        # Check if answer mentions assumptions or clarifications
        assumption_keywords = [
            "assuming", "interpreted", "considered", "default",
            "recent", "last", "past", "current"
        ]

        answer_lower = answer.lower()
        mentions_assumptions = any(keyword in answer_lower for keyword in assumption_keywords)
        metrics["acknowledges_ambiguity"] = mentions_assumptions

        # For ambiguity tests, we consider it passed if SQL was generated
        # The agent made reasonable assumptions to handle ambiguity
        passed = metrics.get("sql_generated", False)

        return passed, metrics

    def _evaluate_error_recovery(
        self,
        test_case: TestCase,
        result: Dict,
        generated_sql: str
    ) -> Tuple[bool, Dict]:
        """Evaluate error recovery"""
        metrics = {}

        answer = result.get('answer', '').lower()

        # Check if agent provided helpful error message
        error_indicators = [
            "cannot", "unable", "don't have", "doesn't exist",
            "not found", "invalid", "error", "sorry"
        ]

        provides_error_message = any(indicator in answer for indicator in error_indicators)
        metrics["provides_error_message"] = provides_error_message

        # For error recovery, we expect either:
        # 1. No SQL generated (agent recognized invalid request)
        # 2. SQL generated but with helpful error message

        if test_case.should_error:
            # We expect the agent to handle this gracefully
            if not generated_sql or provides_error_message:
                metrics["graceful_handling"] = True
                return True, metrics
            else:
                metrics["graceful_handling"] = False
                return False, metrics

        # If shouldn't error, pass if SQL generated
        return bool(generated_sql), metrics

    def _normalize_sql(self, sql: str) -> str:
        """Normalize SQL for comparison"""
        # Remove extra whitespace, convert to uppercase
        return ' '.join(sql.upper().split())

    def _compare_results(
        self,
        actual: List[Dict],
        expected: List[Dict]
    ) -> bool:
        """Compare actual and expected results"""
        if len(actual) != len(expected):
            return False

        # Sort both lists for comparison (order might differ)
        try:
            actual_sorted = sorted(actual, key=lambda x: json.dumps(x, sort_keys=True))
            expected_sorted = sorted(expected, key=lambda x: json.dumps(x, sort_keys=True))
            return actual_sorted == expected_sorted
        except (TypeError, ValueError):
            # If sorting fails, do direct comparison
            return actual == expected

    def evaluate_test_suite(self, test_cases: List[TestCase]) -> EvaluationReport:
        """
        Evaluate a full test suite

        Args:
            test_cases: List of test cases to evaluate

        Returns:
            EvaluationReport with aggregated results
        """
        start_time = time.time()
        results = []

        for i, test_case in enumerate(test_cases, 1):
            if self.verbose:
                print(f"[{i}/{len(test_cases)}] Evaluating: {test_case.id}")

            result = self.evaluate_test_case(test_case)
            results.append(result)

            if self.verbose:
                status = "✓ PASS" if result.passed else "✗ FAIL"
                print(f"  {status} ({result.execution_time_ms:.1f}ms)")
                if not result.passed and result.error_message:
                    print(f"  Error: {result.error_message}")

        # Aggregate results
        total_time_ms = (time.time() - start_time) * 1000
        passed = [r for r in results if r.passed]
        failed = [r for r in results if not r.passed]

        # Results by category
        category_results = {}
        for category in EvaluationCategory:
            cat_results = [r for r in results if r.category == category]
            if cat_results:
                cat_passed = [r for r in cat_results if r.passed]
                category_results[category.value] = {
                    "total": len(cat_results),
                    "passed": len(cat_passed),
                    "failed": len(cat_results) - len(cat_passed),
                    "pass_rate": len(cat_passed) / len(cat_results) if cat_results else 0
                }

        return EvaluationReport(
            total_tests=len(test_cases),
            passed_tests=len(passed),
            failed_tests=len(failed),
            pass_rate=len(passed) / len(test_cases) if test_cases else 0,
            category_results=category_results,
            execution_time_ms=total_time_ms,
            failed_test_ids=[r.test_case_id for r in failed],
            results=results
        )

    def print_report(self, report: EvaluationReport):
        """Print formatted evaluation report to console (for backwards compatibility)"""
        print("\n" + "="*80)
        print("SQL AGENT EVALUATION REPORT")
        print("="*80)

        print(f"\nOverall Results:")
        print(f"  Total Tests: {report.total_tests}")
        print(f"  Passed: {report.passed_tests} ({report.pass_rate*100:.1f}%)")
        print(f"  Failed: {report.failed_tests}")
        print(f"  Execution Time: {report.execution_time_ms/1000:.2f}s")

        print(f"\nResults by Category:")
        for category, results in report.category_results.items():
            print(f"\n  {category.replace('_', ' ').title()}:")
            print(f"    Total: {results['total']}")
            print(f"    Passed: {results['passed']} ({results['pass_rate']*100:.1f}%)")
            print(f"    Failed: {results['failed']}")

        if report.failed_test_ids:
            print(f"\nFailed Tests:")
            for test_id in report.failed_test_ids:
                result = next(r for r in report.results if r.test_case_id == test_id)
                print(f"  - {test_id}")
                if result.error_message:
                    print(f"    Error: {result.error_message}")

        print("\n" + "="*80)

    def log_report(self, report: EvaluationReport):
        """Log evaluation report using Python logging (captured by pytest)"""
        logger.info("="*80)
        logger.info("SQL AGENT EVALUATION REPORT")
        logger.info("="*80)

        logger.info(f"Overall Results:")
        logger.info(f"  Total Tests: {report.total_tests}")
        logger.info(f"  Passed: {report.passed_tests} ({report.pass_rate*100:.1f}%)")
        logger.info(f"  Failed: {report.failed_tests}")
        logger.info(f"  Execution Time: {report.execution_time_ms/1000:.2f}s")

        logger.info(f"Results by Category:")
        for category, results in report.category_results.items():
            logger.info(f"  {category.replace('_', ' ').title()}:")
            logger.info(f"    Total: {results['total']}")
            logger.info(f"    Passed: {results['passed']} ({results['pass_rate']*100:.1f}%)")
            logger.info(f"    Failed: {results['failed']}")

        if report.failed_test_ids:
            logger.warning(f"Failed Tests: {', '.join(report.failed_test_ids)}")


def load_test_cases_from_json(file_path: str) -> List[TestCase]:
    """Load test cases from JSON file"""
    with open(file_path, 'r') as f:
        data = json.load(f)

    test_cases = []
    for item in data:
        test_case = TestCase(
            id=item['id'],
            category=EvaluationCategory(item['category']),
            question=item['question'],
            expected_sql=item.get('expected_sql'),
            expected_results=item.get('expected_results'),
            expected_tables=item.get('expected_tables'),
            expected_columns=item.get('expected_columns'),
            should_error=item.get('should_error', False),
            description=item.get('description', ''),
            difficulty=item.get('difficulty', 'medium'),
            metadata=item.get('metadata', {})
        )
        test_cases.append(test_case)

    return test_cases


def create_pytest_html_extra(result: EvaluationResult) -> Dict[str, Any]:
    """
    Create pytest-html extra information for an evaluation result.

    This formats the evaluation result data for display in HTML reports.

    Args:
        result: EvaluationResult from evaluate_test_case

    Returns:
        Dictionary with formatted data for pytest-html extras
    """
    extra_data = {
        "Test Case ID": result.test_case_id,
        "Category": result.category.value,
        "Execution Time (ms)": round(result.execution_time_ms, 2),
        "Passed": result.passed,
    }

    # Add SQL query if available
    if result.generated_sql:
        extra_data["Generated SQL"] = result.generated_sql

    # Add actual results if available (limited to first 5 rows for readability)
    if result.actual_results:
        limited_results = result.actual_results[:5]
        extra_data["Actual Results (first 5)"] = limited_results
        if len(result.actual_results) > 5:
            extra_data["Total Result Rows"] = len(result.actual_results)

    # Add expected results if available
    if result.expected_results:
        extra_data["Expected Results"] = result.expected_results

    # Add metrics if available
    if result.metrics:
        extra_data["Metrics"] = result.metrics

    # Add error message if test failed
    if not result.passed and result.error_message:
        extra_data["Error Message"] = result.error_message

    return extra_data


def attach_result_to_pytest(request, result: EvaluationResult):
    """
    Attach evaluation result to pytest test item for HTML report display.

    Usage in test functions:
        result = evaluator.evaluate_test_case(test_case)
        attach_result_to_pytest(request, result)
        assert result.passed

    Args:
        request: pytest request fixture
        result: EvaluationResult from evaluate_test_case
    """
    try:
        # Import pytest_html if available
        import pytest_html

        # Create extra data
        extra_data = create_pytest_html_extra(result)

        # Attach as JSON extra for structured display
        if not hasattr(request.node, 'extras'):
            request.node.extras = []

        request.node.extras.append(
            pytest_html.extras.json(extra_data, name="Evaluation Details")
        )

        # Also attach SQL as code block if available
        if result.generated_sql:
            request.node.extras.append(
                pytest_html.extras.text(result.generated_sql, name="Generated SQL")
            )

    except ImportError:
        # pytest-html not installed, skip
        pass
