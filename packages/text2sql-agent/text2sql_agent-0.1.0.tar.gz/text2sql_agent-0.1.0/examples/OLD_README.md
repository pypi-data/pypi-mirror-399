# Text-to-SQL

A flexible, LLM-agnostic text-to-SQL agent that works with **any** LLM provider and **any** SQL database.

## Features

- **LLM Provider Agnostic**: Works with any LangChain `BaseChatModel`
  - AWS Bedrock, OpenAI, Anthropic, Ollama, Google Gemini, and more
  - Just pass your LLM instance - no provider-specific code needed

- **Database Agnostic**: Works with any SQL database
  - PostgreSQL, MySQL, SQLite, SQL Server, BigQuery, and more
  - Just pass your database connection - no database-specific code needed

- **Domain Agnostic**: Optional domain context for specialized behavior
  - Generic by default - works with any data
  - Add domain context for specialized responses (medical, e-commerce, finance, etc.)

- **Intelligent Result Handling**: Automatically truncates large results for faster LLM processing
  - Full results available via API
  - Configurable thresholds

- **JSON Serializable**: Properly formatted JSON results with support for UUIDs, dates, decimals, etc.

## Quick Start

```python
from text_to_sql import SQLAgent
from langchain_aws import ChatBedrock
from langchain_community.utilities import SQLDatabase

# Setup LLM (any provider)
llm = ChatBedrock(model_id="anthropic.claude-3-sonnet-20240229-v1:0")

# Setup Database (any SQL database)
db = SQLDatabase.from_uri("postgresql://user:pass@host/database")

# Create agent
agent = SQLAgent(llm=llm, db=db)

# Ask questions in natural language
result = agent.query("What tables are in the database?")
print(result["answer"])
```

## Installation

### Basic Installation

```bash
pip install text2sql-agent
```

### With Specific Providers

```bash
# For AWS Bedrock
pip install text2sql-agent[bedrock]

# For OpenAI
pip install text2sql-agent[openai]

# For Anthropic
pip install text2sql-agent[anthropic]

# For PostgreSQL
pip install text2sql-agent[postgresql]

# For MySQL
pip install text2sql-agent[mysql]

# Install everything
pip install text2sql-agent[all]
```

### From Source

```bash
git clone https://github.com/jasminpsourcefuse/text-to-sql.git
cd text-to-sql
pip install -e .
```

## Usage Examples

### Generic Usage (Any Data)

```python
from text_to_sql import SQLAgent
from langchain_aws import ChatBedrock
from langchain_community.utilities import SQLDatabase

llm = ChatBedrock(model_id="anthropic.claude-3-sonnet-20240229-v1:0")
db = SQLDatabase.from_uri("postgresql://user:pass@host/database")

# Generic agent - no domain assumptions
agent = SQLAgent(llm=llm, db=db)

# Ask questions
result = agent.query("How many rows are in the users table?")
print(result["answer"])
print(result["sql_query"])
print(result["results"])
```

### Domain-Specific Usage

```python
# Medical domain
agent = SQLAgent(
    llm=llm,
    db=db,
    domain_context="medical patient records, diagnoses, medications, and treatment history"
)

result = agent.query("How many patients were admitted last month?")
print(result["answer"])
```

```python
# E-commerce domain
agent = SQLAgent(
    llm=llm,
    db=db,
    domain_context="e-commerce data including products, orders, customers, and transactions"
)

result = agent.query("What were the top 5 selling products this week?")
print(result["answer"])
```

### Multiple LLM Providers

```python
# AWS Bedrock
from langchain_aws import ChatBedrock
llm = ChatBedrock(model_id="anthropic.claude-3-sonnet-20240229-v1:0")

# OpenAI
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4")

# Anthropic API
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(model="claude-3-sonnet-20240229")

# Ollama (local)
from langchain_ollama import ChatOllama
llm = ChatOllama(model="llama2")

# All work the same way
agent = SQLAgent(llm=llm, db=db)
```

### Multiple Database Types

```python
from langchain_community.utilities import SQLDatabase

# PostgreSQL
db = SQLDatabase.from_uri("postgresql://user:pass@host/database")

# MySQL
db = SQLDatabase.from_uri("mysql+pymysql://user:pass@host/database")

# SQLite
db = SQLDatabase.from_uri("sqlite:///path/to/database.db")

# SQL Server
db = SQLDatabase.from_uri("mssql+pyodbc://user:pass@host/database?driver=ODBC+Driver+17+for+SQL+Server")

# All work the same way
agent = SQLAgent(llm=llm, db=db)
```

### With Conversation History

```python
conversation_history = [
    {"role": "user", "content": "Show me all patients"},
    {"role": "assistant", "content": "Here are all patients..."},
]

result = agent.query(
    "How many of them have diabetes?",
    conversation_history=conversation_history
)
```

### Advanced Configuration

```python
agent = SQLAgent(
    llm=llm,
    db=db,
    domain_context="financial transactions",
    max_rows_for_llm=20,           # Send up to 20 rows to LLM
    large_result_threshold=100,     # Consider 100+ rows as "large"
    verbose=True,                   # Show agent thinking process
    max_iterations=15,              # Allow more iterations for complex queries
)
```

### Utility Methods

```python
# Get database schema
schema = agent.get_schema_info()
print(schema)

# Get specific table schemas
schema = agent.get_schema_info(table_names=["users", "orders"])
print(schema)

# Get all table names
tables = agent.get_table_names()
print(tables)  # ['users', 'orders', 'products']

# Get database dialect
dialect = agent.get_dialect()
print(dialect)  # 'postgresql'

# Get full untruncated results
result = agent.query("SELECT * FROM large_table")
full_data = agent.get_full_results()
```

## API Reference

### SQLAgent

#### Constructor

```python
SQLAgent(
    llm: BaseChatModel,
    db: SQLDatabase,
    domain_context: Optional[str] = None,
    max_rows_for_llm: int = 10,
    large_result_threshold: int = 50,
    verbose: bool = False,
    max_iterations: int = 10,
)
```

**Parameters:**
- `llm`: Any LangChain `BaseChatModel` instance
- `db`: Any `SQLDatabase` instance
- `domain_context`: Optional domain description for specialized behavior
- `max_rows_for_llm`: Maximum rows to send to LLM for answer generation
- `large_result_threshold`: Threshold to consider results "large"
- `verbose`: Enable verbose output
- `max_iterations`: Maximum agent iterations

#### Methods

##### query()

```python
query(question: str, conversation_history: Optional[List[Dict]] = None) -> Dict[str, Any]
```

Execute a natural language query.

**Returns:**
```python
{
    "answer": "Natural language answer",
    "sql_query": "SELECT * FROM table",
    "results": "[{...}, {...}]",  # JSON string
    "intermediate_steps": [...]
}
```

##### get_full_results()

```python
get_full_results() -> str
```

Get complete untruncated results from the last query as JSON string.

##### get_schema_info()

```python
get_schema_info(table_names: Optional[List[str]] = None) -> str
```

Get database schema information.

##### get_table_names()

```python
get_table_names() -> List[str]
```

Get list of all table names.

##### get_dialect()

```python
get_dialect() -> str
```

Get the SQL dialect of the connected database.

## Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `llm` | `BaseChatModel` | Required | Any LangChain chat model |
| `db` | `SQLDatabase` | Required | Any SQLDatabase instance |
| `domain_context` | `str` | `None` | Optional domain description |
| `max_rows_for_llm` | `int` | `10` | Max rows to send to LLM |
| `large_result_threshold` | `int` | `50` | Threshold for "large" results |
| `verbose` | `bool` | `False` | Show agent thinking |
| `max_iterations` | `int` | `10` | Max agent iterations |

## Supported LLM Providers

- **AWS Bedrock** (Claude, Titan, etc.)
- **OpenAI** (GPT-3.5, GPT-4, etc.)
- **Anthropic** (Claude via API)
- **Ollama** (Local models)
- **Google** (Gemini, PaLM)
- **HuggingFace** (Various models)
- **Cohere**
- **Any custom LangChain BaseChatModel**

## Supported Databases

- **PostgreSQL**
- **MySQL**
- **SQLite**
- **SQL Server**
- **BigQuery**
- **Oracle**
- **Snowflake**
- **Redshift**
- **Any SQLAlchemy-compatible database**

## How It Works

1. **Schema First Approach**: Agent always checks table schemas before writing queries
2. **Standard SQL**: Generates SQL compatible with multiple databases
3. **ReAct Pattern**: Uses Thought-Action-Observation loop for reliable results
4. **Intelligent Truncation**: Large results are automatically summarized for LLM processing
5. **Error Recovery**: Automatically retries queries with corrections on errors

## Best Practices

1. **Use Domain Context**: Helps the agent understand your data better
   ```python
   agent = SQLAgent(llm=llm, db=db, domain_context="medical records")
   ```

2. **Enable Verbose Mode**: For debugging and understanding agent behavior
   ```python
   agent = SQLAgent(llm=llm, db=db, verbose=True)
   ```

3. **Adjust Result Thresholds**: Based on your use case
   ```python
   agent = SQLAgent(
       llm=llm,
       db=db,
       max_rows_for_llm=50,  # Send more rows to LLM
       large_result_threshold=200  # Higher threshold
   )
   ```

4. **Use Conversation History**: For follow-up questions
   ```python
   result = agent.query(question, conversation_history=history)
   ```

5. **Check Full Results**: When truncation occurs
   ```python
   result = agent.query("SELECT * FROM large_table")
   if "truncated" in result["results"]:
       full_data = agent.get_full_results()
   ```

## Security Best Practices

**IMPORTANT: Never commit credentials to version control!**

### Environment Variables Setup

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your actual credentials:**
   ```bash
   # Database connections
   DATABASE_URL=postgresql://your_user:your_password@localhost:5432/your_database

   # API Keys
   OPENAI_API_KEY=sk-your-actual-key-here
   ANTHROPIC_API_KEY=your-actual-key-here

   # AWS Configuration
   AWS_DEFAULT_REGION=us-east-1
   AWS_ACCESS_KEY_ID=your-access-key
   AWS_SECRET_ACCESS_KEY=your-secret-key
   ```

3. **Load environment variables in Python:**
   ```python
   import os
   from dotenv import load_dotenv

   # Load .env file
   load_dotenv()

   # Use environment variables
   database_url = os.getenv("DATABASE_URL")
   api_key = os.getenv("OPENAI_API_KEY")
   ```

### Security Checklist

- ✅ **DO** use environment variables for all credentials
- ✅ **DO** add `.env` to your `.gitignore` (already included)
- ✅ **DO** use `.env.example` for documentation (without real values)
- ✅ **DO** rotate credentials if accidentally committed
- ❌ **DON'T** hardcode passwords, API keys, or tokens in code
- ❌ **DON'T** commit `.env` files to version control
- ❌ **DON'T** share credentials in documentation or examples

### Database Connection Security

```python
# ✅ GOOD - Using environment variables
import os
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise ValueError("DATABASE_URL environment variable not set!")
db = SQLDatabase.from_uri(database_url)

# ❌ BAD - Hardcoded credentials
db = SQLDatabase.from_uri("postgresql://user:password123@host/db")
```

### API Key Security

```python
# ✅ GOOD - Using environment variables
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ❌ BAD - Hardcoded API key
llm = ChatOpenAI(api_key="sk-1234567890abcdef")
```

## Limitations

- Read-only operations (SELECT queries only)
- No support for DML statements (INSERT, UPDATE, DELETE, DROP)
- Requires LangChain-compatible LLM
- Requires SQLAlchemy-compatible database

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/jasminpsourcefuse/text-to-sql.git
cd text-to-sql

# Install with dev dependencies
pip install -e ".[dev]"

# Format code
black text_to_sql/

# Type checking
mypy text_to_sql/
```

## Testing

The SQL Agent Toolkit includes a comprehensive test suite with support for multiple databases and LLM providers.

### Test Categories

The test suite is organized into four categories:

1. **Unit Tests** (`@pytest.mark.unit`)
   - Fast tests using mocks
   - No external dependencies required
   - Test basic agent functionality

2. **Integration Tests** (`@pytest.mark.integration`)
   - Tests with real databases (SQLite, PostgreSQL)
   - Test database-specific behavior
   - Require database setup

3. **Feature Tests** (`@pytest.mark.feature_test`)
   - Test 7 advanced features:
     - Schema pre-loading & caching
     - Async support
     - Enhanced conversation context
     - Enhanced logging
     - Timestamp context
     - Singleton pattern
     - Better error recovery

4. **Evaluation Tests** (`@pytest.mark.evaluation`)
   - Domain-specific test suites (employees, medical, e-commerce)
   - Test SQL correctness, schema understanding, edge cases
   - Require real LLM provider

### Environment Variables

For full test coverage, set these environment variables:

```bash
# PostgreSQL Database (optional - SQLite used if not set)
export DATABASE_URL_POSTGRES="postgresql://user:password@localhost:5432/test_employees"
export DATABASE_URL_POSTGRES_MEDICAL="postgresql://user:password@localhost:5432/test_medical"
export DATABASE_URL_POSTGRES_ECOMMERCE="postgresql://user:password@localhost:5432/test_ecommerce"

# Groq API Key (optional - Ollama used if not set)
export GROQ_API_KEY="your_groq_api_key_here"

# Ollama (if not on default host)
export OLLAMA_HOST="http://localhost:11434"
```

### Running Tests

#### Basic Test Execution

```bash
# Run all tests (SQLite only, mock LLM)
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_agent.py

# Run specific test
pytest tests/test_agent.py::test_agent_initialization
```

#### Running Tests by Category

```bash
# Run only unit tests (fast, no dependencies)
pytest tests/ -m unit

# Run only integration tests
pytest tests/ -m integration

# Run only feature tests
pytest tests/ -m feature_test

# Run only evaluation tests
pytest tests/ -m evaluation
```

#### Running Tests with Different Databases

```bash
# Run with SQLite only (default)
pytest tests/ --database=sqlite

# Run with PostgreSQL only (requires DATABASE_URL_POSTGRES)
pytest tests/ --database=postgres

# Run with both SQLite and PostgreSQL
pytest tests/ --database=all
```

#### Running Tests with Different LLM Providers

```bash
# Run with mock LLM (fast, no API calls)
pytest tests/ --llm=mock

# Run with Ollama (requires Ollama running locally)
pytest tests/ --llm=ollama --model=mistral:7b

# Run with Groq (requires GROQ_API_KEY)
pytest tests/ --llm-provider=groq

# Run evaluation tests with Ollama
pytest tests/evaluations/ --llm=ollama --model=llama3.1
```

#### Combining Options

```bash
# PostgreSQL + Ollama
pytest tests/ --database=postgres --llm=ollama --model=mistral:7b

# SQLite + Groq
pytest tests/ --database=sqlite --llm-provider=groq

# Feature tests only with PostgreSQL
pytest tests/ -m feature_test --database=postgres

# Integration tests with both databases
pytest tests/ -m integration --database=all
```

#### Skipping Slow Tests

```bash
# Skip slow tests (async, LLM-dependent tests)
pytest tests/ -m "not slow"

# Run only fast tests
pytest tests/ -m "unit and not slow"
```

### Test Reports

#### HTML Evaluation Report

After running tests, an HTML report is automatically generated:

```bash
# Run tests to generate report
pytest tests/

# View report
open reports/evaluation_report.html
```

The HTML report includes:
- Test results by category
- Execution times
- Pass/fail status
- Detailed error messages
- SQL queries generated
- Query execution metrics

#### Comparison Report

A comparison report is automatically generated showing results across database and LLM combinations:

```bash
# Run tests with comparison report
pytest tests/ --generate-comparison

# Disable comparison report
pytest tests/ --generate-comparison=false

# View comparison report
open reports/comparison_report_*.html
```

The comparison report includes:
- **Database Comparison**: SQLite vs PostgreSQL performance
- **LLM Provider Comparison**: Ollama vs Groq accuracy
- **Combination Results**: All database/LLM combinations
- **Pass Rate Analysis**: Overall and by category
- **Performance Metrics**: Execution times and success rates

### Test Database Locations

Test databases are stored in `tests/test_databases/`:

```
tests/
├── test_databases/
│   ├── test_employees.db      # SQLite employees database
│   ├── test_medical.db         # SQLite medical database
│   └── test_ecommerce.db       # SQLite e-commerce database
```

### Example Test Workflows

#### Quick Development Check
```bash
# Fast tests only, no external dependencies
pytest tests/ -m "unit and not slow"
```

#### Full Local Testing
```bash
# All tests with SQLite and Ollama
pytest tests/ --database=sqlite --llm=ollama --model=mistral:7b
```

#### CI/CD Testing
```bash
# Mock LLM, SQLite only, skip slow tests
pytest tests/ --llm=mock --database=sqlite -m "not slow"
```

#### Comprehensive Testing
```bash
# Test all combinations (requires PostgreSQL and Groq setup)
pytest tests/ --database=all --llm-provider=all --llm=ollama
```

### Understanding Test Results

**Test Counts**:
- ~15 unit tests (mocks)
- ~7 parametrized integration tests (×2 databases = 14 test runs)
- ~19 feature tests
- ~64 evaluation tests (×databases×LLMs = variable)

**Expected Pass Rates**:
- Unit tests: 100%
- Integration tests: >95%
- Feature tests: >90%
- Evaluation tests: 70-85% (LLM-dependent)

### Troubleshooting Tests

**PostgreSQL Connection Errors**:
```bash
# Check PostgreSQL is running
pg_isready

# Verify connection string
psql "postgresql://user:password@localhost:5432/test_employees"
```

**Ollama Connection Errors**:
```bash
# Check Ollama is running
ollama list

# Pull required model
ollama pull mistral:7b
```

**Groq API Errors**:
```bash
# Verify API key is set
echo $GROQ_API_KEY

# Check API key is valid at https://console.groq.com/
```

**Skipped Tests**:
- Tests requiring PostgreSQL are skipped if `DATABASE_URL_POSTGRES` is not set
- Tests requiring Groq are skipped if `GROQ_API_KEY` is not set
- Evaluation tests are skipped if `--llm=mock` (require real LLM)

## Benchmarking with Spider

The SQL Agent Toolkit includes support for the **Spider benchmark**, the industry-standard evaluation dataset for text-to-SQL systems.

### What is Spider?

Spider is a large-scale, cross-domain text-to-SQL benchmark created by Yale University featuring:
- 200+ databases across diverse domains
- 10,000+ questions with varying difficulty levels
- Complex queries requiring joins, nested queries, and set operations
- Widely used in research and industry for evaluating text-to-SQL systems

### Quick Start with Spider Benchmark

```bash
# Navigate to Groq examples
cd examples/groq

# Step 1: Download and setup Spider dataset (one-time, ~5 minutes)
python setup_spider.py

# Step 2: Run benchmark evaluation (~5-10 minutes for 50 examples)
python test_spider_benchmark.py --limit 50
```

### Spider Benchmark Options

```bash
# Quick test with 10 examples
python test_spider_benchmark.py --limit 10

# Standard evaluation with 50 examples
python test_spider_benchmark.py --limit 50

# Full benchmark (1000+ examples, ~2-4 hours)
python test_spider_benchmark.py --all

# Test specific database
python test_spider_benchmark.py --database concert_singer

# Filter by difficulty level
python test_spider_benchmark.py --difficulty easy
python test_spider_benchmark.py --difficulty medium
python test_spider_benchmark.py --difficulty hard

# Use different Groq model
python test_spider_benchmark.py --model llama-3.3-70b-versatile
```

### Benchmark Metrics

The evaluation provides comprehensive metrics:

- **Exact Match**: Generated SQL matches expected SQL exactly (after normalization)
- **Execution Match**: Different SQL but produces same results (still correct!)
- **Overall Accuracy**: Percentage of successful queries
- **By Difficulty**: Performance breakdown (easy/medium/hard/extra)
- **By Database**: Performance across different domains

### Expected Performance

Typical accuracy ranges on Spider dev set:
- **Simple rule-based systems**: 10-30%
- **Early neural approaches**: 30-50%
- **Modern LLM-based systems**: 50-75%
- **State-of-the-art (2025)**: 75-85%
- **Human performance**: ~92%

### Results and Reports

Each benchmark run generates:
- **Console report**: Overall metrics and statistics
- **JSON file**: Detailed per-example results with generated SQL, success/failure status, and execution times

Example output:
```
================================================================================
EVALUATION REPORT
================================================================================

📊 Overall Results:
   • Total examples: 50
   • Successful: 35 (70.0%)
   • Exact matches: 25 (50.0%)
   • Execution matches: 10 (20.0%)
   • Total time: 225.5s
   • Avg time per query: 4.5s

📈 By Difficulty:
   • easy: 20/25 (80.0%)
   • medium: 12/18 (66.7%)
   • hard: 3/7 (42.9%)

💾 Detailed results saved to: spider_results_llama-3.3-70b-versatile_20250129_143022.json
```

### Documentation

For detailed instructions, see:
- [examples/groq/SPIDER_QUICKSTART.md](examples/groq/SPIDER_QUICKSTART.md) - Complete setup and usage guide
- [examples/groq/README.md](examples/groq/README.md) - Spider benchmark details and tips

### Prerequisites

- **Groq API key** (get from [console.groq.com/keys](https://console.groq.com/keys))
- **~500MB disk space** for Spider dataset
- **Python 3.8+** with `langchain-groq` installed

```bash
pip install langchain-groq
```

### Why Use Spider Benchmark?

- **Industry Standard**: Widely recognized benchmark for fair comparisons
- **Comprehensive**: Tests across domains, difficulty levels, and SQL complexity
- **Identify Weaknesses**: See exactly where your system struggles
- **Track Improvements**: Compare results before and after optimizations
- **Research Ready**: Results comparable with published papers

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

- Issues: https://github.com/jasminpsourcefuse/text-to-sql/issues
- Documentation: https://github.com/jasminpsourcefuse/text-to-sql
- Examples: See `examples/` directory

## Acknowledgments

Built on top of:
- [LangChain](https://github.com/langchain-ai/langchain)
- [SQLAlchemy](https://www.sqlalchemy.org/)

## Citation

If you use this package in your research, please cite:

```bibtex
@software{text_to_sql,
  title = {Text2SQL Agent: A Flexible Text-to-SQL Agent},
  author = {Jasmin Patel},
  year = {2025},
  url = {https://github.com/jasminpsourcefuse/text-to-sql}
}
```
