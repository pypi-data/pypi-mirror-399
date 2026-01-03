"""
SQL Agent Evaluation Framework

Provides tools for evaluating SQL agent performance across multiple dimensions:
- SQL Correctness
- Schema Understanding
- Edge Cases and Complexity
- Ambiguity Handling
- Error Recovery
"""
from .evaluator import (
    SQLAgentEvaluator,
    EvaluationCategory,
    TestCase,
    EvaluationResult,
    EvaluationReport,
    load_test_cases_from_json,
    attach_result_to_pytest,
    create_pytest_html_extra
)

__all__ = [
    'SQLAgentEvaluator',
    'EvaluationCategory',
    'TestCase',
    'EvaluationResult',
    'EvaluationReport',
    'load_test_cases_from_json',
    'attach_result_to_pytest',
    'create_pytest_html_extra'
]
