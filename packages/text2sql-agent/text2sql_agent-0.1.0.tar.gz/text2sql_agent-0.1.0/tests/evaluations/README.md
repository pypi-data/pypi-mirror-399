# SQL Agent Evaluation Suite

Comprehensive evaluation framework for SQL Agent Toolkit covering:

1. **SQL Correctness** - Does generated SQL return correct results?
2. **Schema Understanding** - Does agent identify correct tables/columns/relationships?
3. **Edge Cases & Complexity** - Handles complex queries (joins, aggregations, subqueries)?
4. **Ambiguity Handling** - How does it handle vague questions?
5. **Error Recovery** - Graceful handling of invalid requests?

## Quick Start

### Run All Evaluations with Ollama

```bash
# Make sure Ollama is running with llama3.1 model
ollama serve

# Run evaluations - HTML report automatically generated
pytest tests/evaluations/test_sql_evaluations.py --llm=ollama
```

**📊 HTML Report:** After running tests, an HTML report is automatically generated at `reports/evaluation_report.html`. Open it in your browser to see:
- Pass/fail rates by category
- Detailed test results with SQL queries
- Execution times
- Test metadata (LLM provider, model, timestamp)

### Run Specific Test Categories

```bash
# Only SQL correctness tests
pytest tests/evaluations/test_sql_evaluations.py::TestSQLCorrectness --llm=ollama

# Only schema understanding tests
pytest tests/evaluations/test_sql_evaluations.py::TestSchemaUnderstanding --llm=ollama

# Only edge cases
pytest tests/evaluations/test_sql_evaluations.py::TestEdgeCases --llm=ollama

# Only ambiguity handling
pytest tests/evaluations/test_sql_evaluations.py::TestAmbiguityHandling --llm=ollama

# Only error recovery
pytest tests/evaluations/test_sql_evaluations.py::TestErrorRecovery --llm=ollama
```

### Run Complete Evaluation Suite

```bash
# Full evaluation with detailed report
pytest tests/evaluations/test_sql_evaluations.py::TestFullEvaluationSuite --llm=ollama -v
```

### Run with Different Models

```bash
# Use different Ollama model
pytest tests/evaluations/test_sql_evaluations.py --llm=ollama --model=llama3.2

# Use OpenAI (when implemented)
pytest tests/evaluations/test_sql_evaluations.py --llm=openai --model=gpt-4
```

### Generate Custom Report Names

```bash
# Custom report filename
pytest tests/evaluations/test_sql_evaluations.py --llm=ollama --html=reports/my_report.html --self-contained-html

# Timestamped report
pytest tests/evaluations/test_sql_evaluations.py --llm=ollama --html=reports/eval_$(date +%Y%m%d_%H%M%S).html --self-contained-html
```

## Test Data

Test cases are defined in JSON format in `tests/evaluations/data/`:

- `employee_test_cases.json` - Tests for employee database schema

Each test case includes:
```json
{
  "id": "sql_correct_001",
  "category": "sql_correctness",
  "question": "How many employees are there?",
  "expected_sql": "SELECT COUNT(*) FROM employees",
  "expected_results": [{"COUNT(*)": 10}],
  "description": "Simple count query",
  "difficulty": "easy"
}
```

## Understanding Results

### Evaluation Metrics

**SQL Correctness:**
- `sql_generated`: Was SQL successfully generated?
- `sql_exact_match`: Does SQL match expected query?
- `results_match`: Do results match expected output?

**Schema Understanding:**
- `tables_found`: List of correctly identified tables
- `tables_missing`: List of missed tables
- `tables_coverage`: Percentage of expected tables found
- `columns_coverage`: Percentage of expected columns found

**Edge Cases:**
- `query_features`: Detected SQL features (joins, aggregations, etc.)
- `complexity_score`: Number of advanced features used
- `results_match`: Correctness of results

**Ambiguity Handling:**
- `sql_generated`: Made reasonable assumptions?
- `acknowledges_ambiguity`: Mentions assumptions in answer?

**Error Recovery:**
- `provides_error_message`: Gives helpful error message?
- `graceful_handling`: Handles error gracefully?

### Pass Criteria

- **SQL Correctness**: Results match expected output
- **Schema Understanding**: All expected tables/columns referenced
- **Edge Cases**: Correct results with appropriate SQL features
- **Ambiguity**: Generates reasonable SQL despite vagueness
- **Error Recovery**: Handles errors gracefully, no dangerous operations

### Target Pass Rates

- SQL Correctness: ≥75%
- Schema Understanding: ≥70%
- Edge Cases: ≥60% (harder queries)
- Ambiguity Handling: ≥70%
- Error Recovery: ≥70%
- **Overall: ≥65%**

## Adding New Test Cases

1. Create test case in JSON file:

```json
{
  "id": "your_test_id",
  "category": "sql_correctness",
  "question": "Your natural language question",
  "expected_sql": "Expected SQL query",
  "expected_results": [{"column": "value"}],
  "expected_tables": ["table1", "table2"],
  "expected_columns": ["column1", "column2"],
  "should_error": false,
  "description": "What this tests",
  "difficulty": "easy|medium|hard"
}
```

2. Categories:
   - `sql_correctness`
   - `schema_understanding`
   - `edge_cases`
   - `ambiguity_handling`
   - `error_recovery`

3. Run tests to validate

## Evaluation Framework API

### Programmatic Usage

```python
from sql_agent_toolkit import SQLAgent
from langchain_ollama import ChatOllama
from langchain_community.utilities import SQLDatabase
from tests.evaluations.framework import (
    SQLAgentEvaluator,
    load_test_cases_from_json
)

# Create agent
llm = ChatOllama(model="llama3.1", temperature=0.1)
db = SQLDatabase.from_uri("sqlite:///your_db.db")
agent = SQLAgent(llm=llm, db=db)

# Create evaluator
evaluator = SQLAgentEvaluator(agent, verbose=True)

# Load test cases
test_cases = load_test_cases_from_json("path/to/test_cases.json")

# Run evaluation
report = evaluator.evaluate_test_suite(test_cases)

# Print report
evaluator.print_report(report)

# Access results
print(f"Pass rate: {report.pass_rate * 100:.1f}%")
print(f"Failed tests: {report.failed_test_ids}")

# Evaluate single test case
from tests.evaluations.framework import TestCase, EvaluationCategory

test_case = TestCase(
    id="custom_001",
    category=EvaluationCategory.SQL_CORRECTNESS,
    question="How many users?",
    expected_sql="SELECT COUNT(*) FROM users"
)

result = evaluator.evaluate_test_case(test_case)
print(f"Passed: {result.passed}")
print(f"Generated SQL: {result.generated_sql}")
```

## Continuous Evaluation

### CI/CD Integration

Add to your GitHub Actions workflow:

```yaml
name: Evaluations

on: [push, pull_request]

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
          pip install pytest

      - name: Start Ollama
        run: |
          # Install and start Ollama
          curl https://ollama.ai/install.sh | sh
          ollama serve &
          ollama pull llama3.1

      - name: Run evaluations
        run: |
          pytest tests/evaluations/ --llm=ollama -v
```

### Monitoring Performance Over Time

Track evaluation metrics across commits to detect regressions:

```python
# Save results to file
import json
from datetime import datetime

with open(f"eval_results_{datetime.now().isoformat()}.json", "w") as f:
    json.dump({
        "commit": "abc123",
        "date": datetime.now().isoformat(),
        "pass_rate": report.pass_rate,
        "category_results": report.category_results,
        "failed_tests": report.failed_test_ids
    }, f)
```

## Troubleshooting

### Tests Failing

1. **Check Ollama is running**: `curl http://localhost:11434/api/tags`
2. **Check model is available**: `ollama list`
3. **Verify database**: Test database is created in conftest.py
4. **Check test case format**: Validate JSON test cases

### Slow Tests

- Evaluation tests require LLM inference (10-30s per query)
- Run specific test categories instead of full suite
- Use faster/smaller LLM models for quick iteration

### Adding More Databases

Create fixtures in `tests/conftest.py`:

```python
@pytest.fixture
def sqlite_ecommerce_db():
    # Create e-commerce test database
    pass

@pytest.fixture
def postgres_medical_db():
    # Create PostgreSQL test database (use testcontainers)
    pass
```

## Contributing

1. Add test cases for new scenarios
2. Expand evaluation metrics
3. Add support for more LLM providers
4. Improve evaluation accuracy

## References

- [Spider Benchmark](https://yale-lily.github.io/spider)
- [WikiSQL Dataset](https://github.com/salesforce/WikiSQL)
- [Text-to-SQL Evaluation Best Practices](https://arxiv.org/abs/2010.12773)
