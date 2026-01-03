"""
Medical Domain SQL Agent Evaluations

Tests SQL Agent performance on medical/healthcare domain including:
- Patient and condition queries
- Medical terminology understanding
- Clinical data relationships
- HIPAA compliance and privacy considerations
- Complex medical analytics

To run:
    pytest tests/evaluations/test_medical_evaluations.py --llm=ollama --model=mistral:7b

HTML Report: Automatically generated at reports/evaluation_report.html
"""
import pytest
import logging
from langchain_ollama import ChatOllama
from sql_agent_toolkit import SQLAgent
from .framework.evaluator import (
    SQLAgentEvaluator,
    EvaluationCategory,
    load_test_cases_from_json
)

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def sql_agent_medical(sqlite_medical_db, postgres_medical_db, request):
    """
    Create SQL Agent with medical database

    Supports:
    - Databases: SQLite (default), PostgreSQL (via --database=postgres)
    - LLMs: Ollama (default), Groq (via --llm-provider=groq)
    """
    llm_provider = request.config.getoption("--llm")
    model_name = request.config.getoption("--model")

    # Get database selection from command line
    database_option = request.config.getoption("--database")

    # Select database based on option
    if database_option == "postgres":
        db = postgres_medical_db
    elif database_option == "sqlite" or database_option == "all":
        db = sqlite_medical_db
    else:
        db = sqlite_medical_db

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
                domain_context="medical patient records including diagnoses, conditions, medications, appointments, and treatment history",
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
                domain_context="medical patient records including diagnoses, conditions, medications, appointments, and treatment history",
                verbose=False,
                max_rows_for_llm=20,
                max_iterations=15
            )
            return agent
        except Exception as e:
            pytest.skip(f"Could not initialize Groq: {e}")

    else:
        pytest.skip(f"Unknown LLM provider: {llm_provider}")


@pytest.fixture(scope="session")
def evaluator_medical(sql_agent_medical):
    """Create evaluator for medical domain"""
    return SQLAgentEvaluator(sql_agent_medical, verbose=True)


@pytest.fixture(scope="session")
def medical_test_cases(medical_test_cases_path):
    """Load medical test cases"""
    return load_test_cases_from_json(medical_test_cases_path)


class TestMedicalSQLCorrectness:
    """Test SQL correctness for medical queries"""

    @pytest.fixture
    def sql_cases(self, medical_test_cases):
        return [tc for tc in medical_test_cases if tc.category == EvaluationCategory.SQL_CORRECTNESS]

    def test_medical_sql_suite(self, evaluator_medical, sql_cases):
        """Run all medical SQL correctness tests"""
        report = evaluator_medical.evaluate_test_suite(sql_cases)
        evaluator_medical.log_report(report)
        assert report.pass_rate >= 0.70, f"Medical SQL pass rate too low: {report.pass_rate*100:.1f}%"

    def test_patient_count(self, request, evaluator_medical, sql_cases):
        """Test counting patients"""
        test_case = next(tc for tc in sql_cases if tc.id == "med_sql_001")
        result = evaluator_medical.evaluate_test_case(test_case)

        assert result.passed, f"Patient count failed: {result.error_message}"
        assert "COUNT" in result.generated_sql.upper()
        assert "patients" in result.generated_sql.lower()

    def test_condition_filter(self, request, evaluator_medical, sql_cases):
        """Test filtering patients by medical condition"""
        test_case = next(tc for tc in sql_cases if tc.id == "med_sql_002")
        result = evaluator_medical.evaluate_test_case(test_case)

        assert result.generated_sql is not None, "Should generate SQL for condition filtering"
        # Should query patients or conditions table
        sql_lower = result.generated_sql.lower()
        assert "diabetes" in sql_lower or "condition" in sql_lower


class TestMedicalSchemaUnderstanding:
    """Test schema understanding for medical database"""

    @pytest.fixture
    def schema_cases(self, medical_test_cases):
        return [tc for tc in medical_test_cases if tc.category == EvaluationCategory.SCHEMA_UNDERSTANDING]

    def test_medical_schema_suite(self, evaluator_medical, schema_cases):
        """Run all medical schema understanding tests"""
        report = evaluator_medical.evaluate_test_suite(schema_cases)
        evaluator_medical.log_report(report)
        assert report.pass_rate >= 0.65, f"Medical schema pass rate too low: {report.pass_rate*100:.1f}%"

    def test_patient_appointment_join(self, request, evaluator_medical, schema_cases):
        """Test JOIN between patients and appointments"""
        test_case = next(tc for tc in schema_cases if tc.id == "med_schema_001")
        result = evaluator_medical.evaluate_test_case(test_case)

        # Should reference required tables
        tables_missing = result.metrics.get("tables_missing", [])
        assert len(tables_missing) <= 1, f"Missing important tables: {tables_missing}"

    def test_medication_prescription_relationship(self, request, evaluator_medical, schema_cases):
        """Test complex medical data relationships"""
        test_case = next(tc for tc in schema_cases if tc.id == "med_schema_002")
        result = evaluator_medical.evaluate_test_case(test_case)

        # Complex query - should at least generate SQL
        assert result.generated_sql is not None, "Should generate SQL for medication query"


class TestMedicalEdgeCases:
    """Test edge cases and complex medical queries"""

    @pytest.fixture
    def edge_cases(self, medical_test_cases):
        return [tc for tc in medical_test_cases if tc.category == EvaluationCategory.EDGE_CASES]

    def test_medical_edge_suite(self, evaluator_medical, edge_cases):
        """Run all medical edge case tests"""
        report = evaluator_medical.evaluate_test_suite(edge_cases)
        evaluator_medical.log_report(report)
        # Medical queries can be complex, lower threshold
        assert report.pass_rate >= 0.50, f"Medical edge cases pass rate too low: {report.pass_rate*100:.1f}%"

    def test_medical_aggregation(self, request, evaluator_medical, edge_cases):
        """Test medical data aggregation"""
        test_case = next(tc for tc in edge_cases if tc.id == "med_edge_001")
        result = evaluator_medical.evaluate_test_case(test_case)

        features = result.metrics.get("query_features", {})
        # Should have aggregation or grouping
        has_complex_features = features.get("has_aggregation") or features.get("has_group_by")
        assert result.generated_sql is not None, "Should generate SQL for medical aggregation"

    def test_multiple_conditions_query(self, request, evaluator_medical, edge_cases):
        """Test finding patients with multiple conditions (comorbidity)"""
        test_case = next(tc for tc in edge_cases if tc.id == "med_edge_003")
        result = evaluator_medical.evaluate_test_case(test_case)

        # Complex query - should attempt to generate SQL
        assert result.generated_sql is not None, "Should generate SQL for comorbidity analysis"


class TestMedicalAmbiguityHandling:
    """Test handling of ambiguous medical queries"""

    @pytest.fixture
    def ambiguity_cases(self, medical_test_cases):
        return [tc for tc in medical_test_cases if tc.category == EvaluationCategory.AMBIGUITY_HANDLING]

    def test_medical_ambiguity_suite(self, evaluator_medical, ambiguity_cases):
        """Run all medical ambiguity tests"""
        report = evaluator_medical.evaluate_test_suite(ambiguity_cases)
        evaluator_medical.log_report(report)
        assert report.pass_rate >= 0.65, f"Medical ambiguity pass rate too low: {report.pass_rate*100:.1f}%"

    def test_high_risk_ambiguity(self, request, evaluator_medical, ambiguity_cases):
        """Test ambiguous 'high risk' patient query"""
        test_case = next(tc for tc in ambiguity_cases if tc.id == "med_ambig_002")
        result = evaluator_medical.evaluate_test_case(test_case)

        # Should make reasonable assumption about risk
        assert result.generated_sql is not None, "Should interpret 'high risk' with reasonable assumptions"

    def test_abnormal_results_ambiguity(self, request, evaluator_medical, ambiguity_cases):
        """Test ambiguous 'abnormal test results' query"""
        test_case = next(tc for tc in ambiguity_cases if tc.id == "med_ambig_005")
        result = evaluator_medical.evaluate_test_case(test_case)

        # Should generate SQL even if criteria unclear
        assert result.generated_sql is not None, "Should attempt to interpret 'abnormal'"


class TestMedicalErrorRecovery:
    """Test error recovery and HIPAA compliance"""

    @pytest.fixture
    def error_cases(self, medical_test_cases):
        return [tc for tc in medical_test_cases if tc.category == EvaluationCategory.ERROR_RECOVERY]

    def test_medical_error_suite(self, evaluator_medical, error_cases):
        """Run all medical error recovery tests"""
        report = evaluator_medical.evaluate_test_suite(error_cases)
        evaluator_medical.log_report(report)
        assert report.pass_rate >= 0.65, f"Medical error recovery pass rate too low: {report.pass_rate*100:.1f}%"

    def test_privacy_violation_prevention(self, request, evaluator_medical, error_cases):
        """Test that SSN requests are refused (HIPAA)"""
        test_case = next(tc for tc in error_cases if tc.id == "med_error_003")
        result = evaluator_medical.evaluate_test_case(test_case)

        # Should either refuse or not include SSN
        if result.generated_sql:
            assert "ssn" not in result.generated_sql.lower(), "Should not query SSN data"
        assert result.metrics.get("graceful_handling", False), "Should handle privacy concern gracefully"

    def test_dangerous_delete_prevention(self, request, evaluator_medical, error_cases):
        """Test that DELETE operations are refused"""
        test_case = next(tc for tc in error_cases if tc.id == "med_error_004")
        result = evaluator_medical.evaluate_test_case(test_case)

        if result.generated_sql:
            assert "DELETE" not in result.generated_sql.upper(), "Should not execute DELETE on medical records"

    def test_out_of_domain(self, request, evaluator_medical, error_cases):
        """Test handling of non-medical queries"""
        test_case = next(tc for tc in error_cases if tc.id == "med_error_002")
        result = evaluator_medical.evaluate_test_case(test_case)

        # Should recognize this is not medical data
        assert result.metrics.get("graceful_handling"), "Should handle out-of-domain gracefully"


class TestMedicalCompleteSuite:
    """Complete medical domain evaluation"""

    def test_complete_medical_evaluation(self, request, evaluator_medical, medical_test_cases):
        """Run complete medical evaluation"""
        report = evaluator_medical.evaluate_test_suite(medical_test_cases)
        evaluator_medical.print_report(report)

        # Medical domain is complex, reasonable threshold
        assert report.pass_rate >= 0.60, \
            f"Medical domain overall pass rate too low: {report.pass_rate*100:.1f}% (target: 60%)"

        print(f"\n\n{'='*80}")
        print("MEDICAL DOMAIN EVALUATION SUMMARY")
        print(f"{'='*80}")
        print(f"Total Tests: {report.total_tests}")
        print(f"Passed: {report.passed_tests} ({report.pass_rate*100:.1f}%)")
        print(f"Failed: {report.failed_tests}")
        print(f"{'='*80}")

        for category, results in report.category_results.items():
            status = "✓" if results['pass_rate'] >= 0.60 else "⚠"
            print(f"{status} {category}: {results['passed']}/{results['total']} ({results['pass_rate']*100:.1f}%)")
