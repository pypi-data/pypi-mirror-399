# Ollama Examples

This folder contains examples using Ollama (local LLM) with the SQL Agent Toolkit.

## Prerequisites

1. **Install Ollama**: https://ollama.ai/
2. **Pull llama3.1 model**:
   ```bash
   ollama pull llama3.1
   ```
3. **Install dependencies**:
   ```bash
   cd ../..  # Go to package root
   source venv/bin/activate
   pip install langchain-ollama psycopg2-binary pymysql cryptography
   ```

## Test Files

Each file is a comprehensive, standalone test for one database type:

### 1. SQLite Employee Database

```bash
python test_sqlite_employees.py
```

**What it tests:**
- ✓ Local SQLite database (creates DB automatically)
- ✓ Employee/department/project data
- ✓ 6+ example queries (salaries, departments, hiring, etc.)
- ✓ Schema inspection, conversation context, utility methods
- ✓ Ollama llama3.1 model

### 2. PostgreSQL Medical Records

```bash
# Make sure PostgreSQL is running with medical_db
python test_postgresql_medical.py
```

**Database Connection:**
```
Host: localhost
Port: 5432
Database: medical_db
User: postgres
Password: Source@321
```

**What it tests:**
- ✓ PostgreSQL database
- ✓ Medical domain context
- ✓ Complex medical queries (diagnoses, patients, appointments)
- ✓ JOINs and subqueries
- ✓ Conversation context

### 3. MySQL E-commerce

```bash
# Make sure MySQL is running with ecom database
python test_mysql_ecommerce.py
```

**Database Connection:**
```
Host: 127.0.0.1
Port: 3306
Database: ecom
User: ecom_user
Password: ecom_pass
```

**What it tests:**
- ✓ MySQL database
- ✓ E-commerce domain context
- ✓ Multi-table queries (users, products, orders, inventory)
- ✓ Aggregate functions (SUM, COUNT, GROUP BY)
- ✓ Complex JOINs

### 4. Spider Benchmark Evaluation

```bash
# First, download and setup the Spider dataset (one-time)
python setup_spider.py

# Then run the benchmark
python test_spider_benchmark.py
```

**What it tests:**
- ✓ Industry-standard text-to-SQL benchmark
- ✓ 166 cross-domain databases
- ✓ ~1000 dev set examples with varying difficulty
- ✓ Exact match and execution match evaluation
- ✓ Comprehensive performance metrics and reports
- ✓ Local LLM evaluation (no API costs!)

**Spider Benchmark Options:**
```bash
# Run on first 10 examples (quick test)
python test_spider_benchmark.py --limit 10

# Run on first 50 examples (standard)
python test_spider_benchmark.py --limit 50

# Run on all examples (~1000+)
python test_spider_benchmark.py --all

# Test specific database
python test_spider_benchmark.py --database concert_singer

# Filter by difficulty
python test_spider_benchmark.py --difficulty easy

# Use different Ollama model
python test_spider_benchmark.py --model mistral
python test_spider_benchmark.py --model codellama
```

## File Descriptions

| File | Description | Database |
|------|-------------|----------|
| `test_sqlite_employees.py` | Comprehensive SQLite test with employee data | SQLite |
| `test_postgresql_medical.py` | Comprehensive PostgreSQL test with medical data | PostgreSQL |
| `test_mysql_ecommerce.py` | Comprehensive MySQL test with e-commerce data | MySQL |
| `test_spider_benchmark.py` | Spider benchmark evaluation with detailed metrics | Spider (166 SQLite DBs) |
| `setup_spider.py` | Download and setup Spider dataset | - |
| `test_database.db` | SQLite database file (auto-generated) | - |
| `README.md` | This documentation file | - |

## Running the Tests

### Quick Test (SQLite only - no external database needed)
```bash
cd examples/ollama
python test_sqlite_employees.py
```
Creates database automatically and runs all tests (~2-3 minutes).

### Run Spider Benchmark
```bash
cd examples/ollama

# Step 1: Setup Spider dataset (one-time, shares with Groq examples)
python setup_spider.py

# Step 2: Run benchmark evaluation
python test_spider_benchmark.py --limit 10
```
Downloads Spider dataset (~200MB), then evaluates on 10 examples (~5-10 minutes with local LLM).

### Full Test Suite (all 3 databases)
```bash
cd examples/ollama

# SQLite (local, no setup needed)
python test_sqlite_employees.py        # ~2-3 minutes

# PostgreSQL (needs server running)
python test_postgresql_medical.py     # ~3-5 minutes

# MySQL (needs server running)
python test_mysql_ecommerce.py        # ~3-5 minutes
```

## Performance Notes

Ollama (local LLM) is slower than cloud-based LLMs:
- Simple queries: ~10-30 seconds
- Complex queries: ~30-60 seconds
- May hit iteration limits on very complex queries

For faster performance, use cloud LLMs:
- AWS Bedrock (Claude)
- OpenAI (GPT-4)
- Anthropic API (Claude)

See `../basic_usage.py` for examples with other LLM providers.

## Expected Output

Each test should show:
1. ✓ Connection successful
2. ✓ Tables discovered
3. ✓ Queries executed
4. 📊 Natural language answers
5. 🔍 Generated SQL queries
6. 📋 Query results

## Troubleshooting

### Ollama not responding
```bash
# Check if Ollama is running
ollama list

# Restart Ollama
ollama serve
```

### Database connection errors
- PostgreSQL: Check credentials and that server is running
- MySQL: Install cryptography: `pip install cryptography`
- SQLite: Run `create_test_db.py` first

### Slow performance
- Normal for Ollama (local processing)
- Consider using cloud LLMs for faster response
- Reduce `max_iterations` in agent config

## Next Steps

After testing with Ollama:
1. Try other LLM providers (see `../basic_usage.py`)
2. Try other database types
3. Add your own domain context
4. Connect to your own databases

## Comparison with Other Examples

- **examples/basic_usage.py** - Generic usage, any LLM provider
- **examples/medical_example.py** - Medical domain, AWS Bedrock
- **examples/multi_provider.py** - Different LLM providers comparison
- **examples/ollama/** (this folder) - Local LLM with 3 database types
