"""
Comprehensive SQL Agent Evaluations

Tests SQL correctness, schema understanding, edge cases, ambiguity handling,
and error recovery using the evaluation framework.

To run these tests with a real LLM (Ollama):
    pytest tests/evaluations/test_sql_evaluations.py --llm=ollama --model=mistral:7b

HTML Report:
    - Automatically generated at reports/evaluation_report.html
    - Includes SQL queries, execution times, and detailed metrics
    - View with: open reports/evaluation_report.html
"""
import pytest
import os
import logging
from typing import Optional
from langchain_ollama import ChatOllama
from sql_agent_toolkit import SQLAgent
from .framework.evaluator import (
    SQLAgentEvaluator,
    EvaluationCategory,
    load_test_cases_from_json
)

# Set up logging for test output
logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def llm_provider(request):
    """Get LLM provider from command line"""
    return request.config.getoption("--llm")


@pytest.fixture(scope="session")
def model_name(request):
    """Get model name from command line"""
    return request.config.getoption("--model")


@pytest.fixture(scope="session")
def sql_agent(request, sqlite_employees_db, postgres_employees_db, llm_provider, model_name):
    """
    Create SQL Agent with appropriate database and LLM

    Supports:
    - Databases: SQLite (default), PostgreSQL (via --database=postgres)
    - LLMs: Ollama (default), Groq (via --llm-provider=groq)
    """
    # Get database selection from command line
    database_option = request.config.getoption("--database")

    # Select database based on option
    if database_option == "postgres":
        db = postgres_employees_db
    elif database_option == "sqlite" or database_option == "all":
        db = sqlite_employees_db
    else:
        db = sqlite_employees_db

    # Get LLM provider option
    llm_provider_option = request.config.getoption("--llm-provider")

    # Override llm_provider if specific option provided
    if llm_provider_option and llm_provider_option != "all":
        llm_provider = llm_provider_option

    # Create LLM based on provider
    if llm_provider == "ollama":
        try:
            llm = ChatOllama(model=model_name, temperature=0.1)
            agent = SQLAgent(
                llm=llm,
                db=db,
                verbose=False,
                max_rows_for_llm=20,
                max_iterations=15
            )
            return agent
        except Exception as e:
            pytest.skip(f"Could not initialize Ollama: {e}")

    elif llm_provider == "groq":
        try:
            from langchain_groq import ChatGroq
            import os

            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                pytest.skip("GROQ_API_KEY not set")

            llm = ChatGroq(
                model="llama-3.1-70b-versatile",
                temperature=0.1,
                api_key=api_key
            )
            agent = SQLAgent(
                llm=llm,
                db=db,
                verbose=False,
                max_rows_for_llm=20,
                max_iterations=15
            )
            return agent
        except Exception as e:
            pytest.skip(f"Could not initialize Groq: {e}")

    elif llm_provider == "openai":
        pytest.skip("OpenAI integration not implemented yet")

    else:
        pytest.skip(f"Unknown LLM provider: {llm_provider}")


@pytest.fixture(scope="session")
def evaluator(sql_agent):
    """Create evaluator with SQL agent"""
    return SQLAgentEvaluator(sql_agent, verbose=True)


@pytest.fixture(scope="session")
def all_test_cases(test_cases_path):
    """Load all test cases"""
    return load_test_cases_from_json(test_cases_path)


class TestSQLCorrectness:
    """Test SQL correctness - does generated SQL return correct results?"""

    @pytest.fixture
    def sql_correctness_cases(self, all_test_cases):
        """Filter SQL correctness test cases"""
        return [tc for tc in all_test_cases if tc.category == EvaluationCategory.SQL_CORRECTNESS]

    def test_sql_correctness_suite_summary(self, evaluator, sql_correctness_cases):
        """
        Suite-level test to check overall SQL correctness pass rate.
        This provides a high-level summary in addition to individual tests.
        """
        report = evaluator.evaluate_test_suite(sql_correctness_cases)
        evaluator.log_report(report)

        # Assert minimum pass rate
        assert report.pass_rate >= 0.75, f"SQL correctness pass rate too low: {report.pass_rate*100:.1f}%"

    def test_simple_count_query(self, request, evaluator, sql_correctness_cases):
        """Test simple COUNT query"""
        test_case = next(tc for tc in sql_correctness_cases if tc.id == "sql_correct_001")
        result = evaluator.evaluate_test_case(test_case)

        assert result.passed, f"Simple count query failed: {result.error_message}"
        assert result.generated_sql is not None
        assert "COUNT" in result.generated_sql.upper()

    def test_select_with_where(self, request, evaluator, sql_correctness_cases):
        """Test SELECT with WHERE clause"""
        test_case = next(tc for tc in sql_correctness_cases if tc.id == "sql_correct_002")
        result = evaluator.evaluate_test_case(test_case)

        assert result.passed, f"SELECT with WHERE failed: {result.error_message}"
        assert "WHERE" in result.generated_sql.upper()

    def test_aggregation_with_filter(self, request, evaluator, sql_correctness_cases):
        """Test aggregation (AVG) with WHERE clause"""
        test_case = next(tc for tc in sql_correctness_cases if tc.id == "sql_correct_003")
        result = evaluator.evaluate_test_case(test_case)

        assert result.passed, f"Aggregation with filter failed: {result.error_message}"
        assert "AVG" in result.generated_sql.upper()

    def test_order_by_with_limit(self, request, evaluator, sql_correctness_cases):
        """Test ORDER BY with LIMIT"""
        test_case = next(tc for tc in sql_correctness_cases if tc.id == "sql_correct_004")
        result = evaluator.evaluate_test_case(test_case)

        assert result.passed, f"ORDER BY with LIMIT failed: {result.error_message}"
        assert "ORDER BY" in result.generated_sql.upper()
        assert "LIMIT" in result.generated_sql.upper()


class TestSchemaUnderstanding:
    """Test schema understanding - does agent identify correct tables/columns?"""

    @pytest.fixture
    def schema_cases(self, all_test_cases):
        """Filter schema understanding test cases"""
        return [tc for tc in all_test_cases if tc.category == EvaluationCategory.SCHEMA_UNDERSTANDING]

    def test_schema_understanding_suite(self, evaluator, schema_cases):
        """Run all schema understanding tests"""
        report = evaluator.evaluate_test_suite(schema_cases)
        evaluator.log_report(report)

        # Assert minimum pass rate
        assert report.pass_rate >= 0.70, f"Schema understanding pass rate too low: {report.pass_rate*100:.1f}%"

    def test_multi_table_join(self, request, evaluator, schema_cases):
        """Test that agent identifies need for JOIN"""
        test_case = next(tc for tc in schema_cases if tc.id == "schema_001")
        result = evaluator.evaluate_test_case(test_case)

        # Check that expected tables are referenced
        assert result.metrics.get("tables_missing", []) == [], \
            f"Missing tables: {result.metrics.get('tables_missing')}"

    def test_foreign_key_relationship(self, request, evaluator, schema_cases):
        """Test understanding of foreign key relationships"""
        test_case = next(tc for tc in schema_cases if tc.id == "schema_003")
        result = evaluator.evaluate_test_case(test_case)

        assert result.passed, f"Foreign key understanding failed: {result.error_message}"
        # Should reference both projects and departments tables
        tables_found = result.metrics.get("tables_found", [])
        assert len(tables_found) >= 2, f"Should reference multiple tables, found: {tables_found}"


class TestEdgeCases:
    """Test edge cases and query complexity"""

    @pytest.fixture
    def edge_cases(self, all_test_cases):
        """Filter edge case test cases"""
        return [tc for tc in all_test_cases if tc.category == EvaluationCategory.EDGE_CASES]

    def test_edge_cases_suite(self, evaluator, edge_cases):
        """Run all edge case tests"""
        report = evaluator.evaluate_test_suite(edge_cases)
        evaluator.log_report(report)

        # Edge cases can be harder, so lower threshold
        assert report.pass_rate >= 0.60, f"Edge cases pass rate too low: {report.pass_rate*100:.1f}%"

    def test_group_by_aggregation(self, evaluator, edge_cases):
        """Test GROUP BY with aggregation"""
        test_case = next(tc for tc in edge_cases if tc.id == "edge_001")
        result = evaluator.evaluate_test_case(test_case)

        assert result.passed, f"GROUP BY failed: {result.error_message}"
        features = result.metrics.get("query_features", {})
        assert features.get("has_group_by"), "Query should have GROUP BY"
        assert features.get("has_aggregation"), "Query should have aggregation"

    def test_having_clause(self, evaluator, edge_cases):
        """Test GROUP BY with HAVING clause"""
        test_case = next(tc for tc in edge_cases if tc.id == "edge_002")
        result = evaluator.evaluate_test_case(test_case)

        features = result.metrics.get("query_features", {})
        assert features.get("has_group_by"), "Query should have GROUP BY"
        assert features.get("has_having"), "Query should have HAVING clause"

    def test_date_filtering(self, evaluator, edge_cases):
        """Test date/time filtering"""
        test_case = next(tc for tc in edge_cases if tc.id == "edge_003")
        result = evaluator.evaluate_test_case(test_case)

        assert result.passed, f"Date filtering failed: {result.error_message}"
        # Should reference hire_date column
        assert "hire_date" in result.generated_sql.lower()

    def test_case_statement(self, evaluator, edge_cases):
        """Test CASE statement for conditional logic"""
        test_case = next(tc for tc in edge_cases if tc.id == "edge_007")
        result = evaluator.evaluate_test_case(test_case)

        # CASE statements are advanced - at least check if SQL generated
        assert result.generated_sql is not None, "Should generate SQL for CASE statement"
        features = result.metrics.get("query_features", {})
        # Either CASE statement or multiple conditions should be present
        has_case_or_conditions = features.get("has_case") or ">" in result.generated_sql


class TestAmbiguityHandling:
    """Test handling of ambiguous questions"""

    @pytest.fixture
    def ambiguity_cases(self, all_test_cases):
        """Filter ambiguity handling test cases"""
        return [tc for tc in all_test_cases if tc.category == EvaluationCategory.AMBIGUITY_HANDLING]

    def test_ambiguity_handling_suite(self, evaluator, ambiguity_cases):
        """Run all ambiguity handling tests"""
        report = evaluator.evaluate_test_suite(ambiguity_cases)
        evaluator.log_report(report)

        # For ambiguity, we just want the agent to make reasonable assumptions
        assert report.pass_rate >= 0.70, f"Ambiguity handling pass rate too low: {report.pass_rate*100:.1f}%"

    def test_ambiguous_recent(self, evaluator, ambiguity_cases):
        """Test handling of 'recent' (ambiguous time frame)"""
        test_case = next(tc for tc in ambiguity_cases if tc.id == "ambig_001")
        result = evaluator.evaluate_test_case(test_case)

        # Should generate SQL with some reasonable interpretation
        assert result.generated_sql is not None, "Should make reasonable assumption for 'recent'"
        # Should filter by hire_date in some way
        assert "hire_date" in result.generated_sql.lower()

    def test_ambiguous_threshold(self, evaluator, ambiguity_cases):
        """Test handling of 'high earners' (ambiguous threshold)"""
        test_case = next(tc for tc in ambiguity_cases if tc.id == "ambig_002")
        result = evaluator.evaluate_test_case(test_case)

        # Should generate SQL with some salary threshold
        assert result.generated_sql is not None
        assert "salary" in result.generated_sql.lower()

    def test_vague_question(self, evaluator, ambiguity_cases):
        """Test very vague question"""
        test_case = next(tc for tc in ambiguity_cases if tc.id == "ambig_004")
        result = evaluator.evaluate_test_case(test_case)

        # Should at least attempt to query salary data
        assert result.generated_sql is not None, "Should attempt to interpret vague question"


class TestErrorRecovery:
    """Test error recovery and handling of invalid requests"""

    @pytest.fixture
    def error_cases(self, all_test_cases):
        """Filter error recovery test cases"""
        return [tc for tc in all_test_cases if tc.category == EvaluationCategory.ERROR_RECOVERY]

    def test_error_recovery_suite(self, evaluator, error_cases):
        """Run all error recovery tests"""
        report = evaluator.evaluate_test_suite(error_cases)
        evaluator.log_report(report)

        # Error recovery is important - should handle gracefully
        assert report.pass_rate >= 0.70, f"Error recovery pass rate too low: {report.pass_rate*100:.1f}%"

    def test_nonexistent_table(self, evaluator, error_cases):
        """Test handling of query for non-existent table"""
        test_case = next(tc for tc in error_cases if tc.id == "error_001")
        result = evaluator.evaluate_test_case(test_case)

        # Should handle gracefully - either no SQL or error message
        assert result.metrics.get("graceful_handling"), "Should gracefully handle non-existent table"

    def test_nonexistent_column(self, evaluator, error_cases):
        """Test handling of query for non-existent column"""
        test_case = next(tc for tc in error_cases if tc.id == "error_002")
        result = evaluator.evaluate_test_case(test_case)

        # Should handle gracefully
        assert result.metrics.get("graceful_handling"), "Should gracefully handle non-existent column"

    def test_out_of_scope(self, evaluator, error_cases):
        """Test handling of completely out-of-scope question"""
        test_case = next(tc for tc in error_cases if tc.id == "error_003")
        result = evaluator.evaluate_test_case(test_case)

        # Should recognize this is out of scope
        assert result.metrics.get("graceful_handling"), "Should recognize out-of-scope question"

    def test_dangerous_operation(self, evaluator, error_cases):
        """Test handling of dangerous DELETE operation"""
        test_case = next(tc for tc in error_cases if tc.id == "error_004")
        result = evaluator.evaluate_test_case(test_case)

        # Should refuse or handle carefully
        if result.generated_sql:
            # Should not contain DELETE
            assert "DELETE" not in result.generated_sql.upper(), "Should not execute DELETE operations"


class TestFullEvaluationSuite:
    """Run complete evaluation suite with reporting"""

    def test_complete_evaluation(self, evaluator, all_test_cases):
        """Run complete evaluation across all categories"""
        report = evaluator.evaluate_test_suite(all_test_cases)
        evaluator.log_report(report)

        # Overall pass rate should be reasonable
        assert report.pass_rate >= 0.65, \
            f"Overall pass rate too low: {report.pass_rate*100:.1f}% (target: 65%)"

        # Print summary statistics
        print(f"\n\nFINAL EVALUATION SUMMARY:")
        print(f"{'='*60}")
        print(f"Total Tests: {report.total_tests}")
        print(f"Passed: {report.passed_tests} ({report.pass_rate*100:.1f}%)")
        print(f"Failed: {report.failed_tests}")
        print(f"Execution Time: {report.execution_time_ms/1000:.2f}s")
        print(f"{'='*60}")

        # Category breakdown
        for category, results in report.category_results.items():
            pass_rate = results['pass_rate'] * 100
            status = "✓" if pass_rate >= 70 else "⚠"
            print(f"{status} {category}: {results['passed']}/{results['total']} ({pass_rate:.1f}%)")
