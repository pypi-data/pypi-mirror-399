# SQL Agent Toolkit - Quick Start Guide

## Installation

```bash
cd sql-agent-toolkit
pip install -e .

# Or with specific providers
pip install -e ".[bedrock]"
pip install -e ".[openai]"
pip install -e ".[all]"
```

## Basic Usage (3 Lines)

```python
from text_to_sql import SQLAgent
from langchain_aws import ChatBedrock
from langchain_community.utilities import SQLDatabase

llm = ChatBedrock(model_id="anthropic.claude-3-sonnet-20240229-v1:0")
db = SQLDatabase.from_uri("postgresql://user:pass@host/database")
agent = SQLAgent(llm=llm, db=db)

result = agent.query("What tables are available?")
print(result["answer"])
```

## Key Features

### 1. LLM Agnostic

Works with **any** LangChain `BaseChatModel`:

```python
# AWS Bedrock
from langchain_aws import ChatBedrock
llm = ChatBedrock(model_id="anthropic.claude-3-sonnet-20240229-v1:0")

# OpenAI
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4")

# Anthropic
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(model="claude-3-sonnet-20240229")

# All work the same
agent = SQLAgent(llm=llm, db=db)
```

### 2. Database Agnostic

Works with **any** SQL database:

```python
# PostgreSQL
db = SQLDatabase.from_uri("postgresql://user:pass@host/db")

# MySQL
db = SQLDatabase.from_uri("mysql+pymysql://user:pass@host/db")

# SQLite
db = SQLDatabase.from_uri("sqlite:///database.db")

# All work the same
agent = SQLAgent(llm=llm, db=db)
```

### 3. Domain Agnostic

Optional domain context for specialized behavior:

```python
# Generic (no domain)
agent = SQLAgent(llm=llm, db=db)

# Medical domain
agent = SQLAgent(llm=llm, db=db, domain_context="medical patient records")

# E-commerce domain
agent = SQLAgent(llm=llm, db=db, domain_context="e-commerce products and orders")
```

## API Reference

### SQLAgent Constructor

```python
agent = SQLAgent(
    llm=llm,                          # Required: Any BaseChatModel
    db=db,                            # Required: Any SQLDatabase
    domain_context=None,              # Optional: Domain description
    max_rows_for_llm=10,              # Max rows sent to LLM
    large_result_threshold=50,        # Threshold for "large" results
    verbose=False,                    # Show agent thinking
    max_iterations=10,                # Max agent iterations
)
```

### Query Method

```python
result = agent.query(
    question="Your natural language question",
    conversation_history=[...]  # Optional: Previous messages
)

# Returns:
{
    "answer": "Natural language answer",
    "sql_query": "SELECT * FROM table",
    "results": "[{...}, {...}]",
    "intermediate_steps": [...]
}
```

### Utility Methods

```python
# Get all table names
tables = agent.get_table_names()
# Returns: ['users', 'orders', 'products']

# Get schema information
schema = agent.get_schema_info()
schema = agent.get_schema_info(table_names=["users", "orders"])

# Get database dialect
dialect = agent.get_dialect()
# Returns: 'postgresql', 'mysql', 'sqlite', etc.

# Get full untruncated results
full_results = agent.get_full_results()

# Enable/disable verbose mode
agent.set_verbose(True)
```

## Examples

See the `examples/` directory:

- [`basic_usage.py`](examples/basic_usage.py) - Generic usage
- [`medical_example.py`](examples/medical_example.py) - Medical domain
- [`multi_provider.py`](examples/multi_provider.py) - Multiple LLM providers

Run examples:
```bash
python examples/basic_usage.py
python examples/medical_example.py
python examples/multi_provider.py
```

## Testing

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=text_to_sql
```

## How It Works

1. **Schema First**: Agent always checks table schemas before writing queries
2. **Standard SQL**: Generates SQL compatible with multiple databases
3. **ReAct Pattern**: Uses Thought-Action-Observation loop
4. **Intelligent Truncation**: Large results automatically summarized for LLM
5. **Error Recovery**: Automatically retries queries with corrections

## Common Use Cases

### Use Case 1: Business Intelligence

```python
agent = SQLAgent(llm=llm, db=db, domain_context="sales and revenue data")

result = agent.query("What were our top 5 products last quarter?")
print(result["answer"])
```

### Use Case 2: Healthcare Analytics

```python
agent = SQLAgent(llm=llm, db=db, domain_context="medical patient records")

result = agent.query("How many patients were diagnosed with diabetes in 2024?")
print(result["answer"])
```

### Use Case 3: Customer Support

```python
agent = SQLAgent(llm=llm, db=db, domain_context="customer orders and support tickets")

result = agent.query("Show me all pending support tickets from the last week")
print(result["answer"])
```

### Use Case 4: Data Exploration

```python
agent = SQLAgent(llm=llm, db=db)  # No domain context

result = agent.query("What tables are in this database and what do they contain?")
print(result["answer"])
```

## Configuration Tips

### For Small Databases

```python
agent = SQLAgent(
    llm=llm,
    db=db,
    max_rows_for_llm=50,           # Send more rows to LLM
    large_result_threshold=200,    # Higher threshold
)
```

### For Large Databases

```python
agent = SQLAgent(
    llm=llm,
    db=db,
    max_rows_for_llm=5,            # Send fewer rows to LLM
    large_result_threshold=20,     # Lower threshold
    max_iterations=15,             # Allow more iterations
)
```

### For Debugging

```python
agent = SQLAgent(
    llm=llm,
    db=db,
    verbose=True,                  # Show agent thinking
)
```

## Troubleshooting

### Issue: "No module named 'langchain_aws'"

```bash
pip install langchain-aws boto3
# Or: pip install sql-agent-toolkit[bedrock]
```

### Issue: "No module named 'psycopg2'"

```bash
pip install psycopg2-binary
# Or: pip install sql-agent-toolkit[postgresql]
```

### Issue: "Agent taking too long"

- Enable verbose mode to see what's happening
- Reduce `max_iterations`
- Check database indexes
- Make queries more specific

### Issue: "Results are truncated"

This is by design for large result sets. Get full results:

```python
result = agent.query("SELECT * FROM large_table")
full_data = agent.get_full_results()
```

## Environment Variables

```bash
# AWS Bedrock
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1

# OpenAI
export OPENAI_API_KEY=your_key

# Anthropic
export ANTHROPIC_API_KEY=your_key

# Database
export DATABASE_URL=postgresql://user:pass@host/db
```

## Next Steps

1. Check out the [README.md](README.md) for detailed documentation
2. Explore the [examples/](examples/) directory
3. Read the source code in [text_to_sql/](text_to_sql/)
4. Run the tests: `pytest tests/`
5. Customize for your use case

## Support

- Issues: File on GitHub
- Examples: See `examples/` directory
- Documentation: See `README.md`

## License

MIT License - see LICENSE file
