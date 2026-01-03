# Google Gemini Examples

This folder contains examples using Google Gemini with the SQL Agent Toolkit.

## Prerequisites

1. **Get Google API Key**: https://makersuite.google.com/app/apikey
2. **Set environment variable**:
   ```bash
   export GOOGLE_API_KEY=your_google_api_key_here
   ```
   Or add to your `.env` file:
   ```bash
   echo "GOOGLE_API_KEY=your_api_key" >> ../../.env
   ```
3. **Install dependencies**:
   ```bash
   cd ../..  # Go to package root
   source venv/bin/activate
   pip install langchain-google-genai psycopg2-binary pymysql cryptography
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
- ✓ Google Gemini Pro model

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

## File Descriptions

| File | Description | Database |
|------|-------------|----------|
| `test_sqlite_employees.py` | Comprehensive SQLite test with employee data | SQLite |
| `test_postgresql_medical.py` | Comprehensive PostgreSQL test with medical data | PostgreSQL |
| `test_mysql_ecommerce.py` | Comprehensive MySQL test with e-commerce data | MySQL |
| `test_database.db` | SQLite database file (auto-generated) | - |
| `README.md` | This documentation file | - |

## Running the Tests

### Quick Test (SQLite only - no external database needed)
```bash
cd examples/gemini
python test_sqlite_employees.py
```
Creates database automatically and runs all tests (~30-60 seconds).

### Full Test Suite (all 3 databases)
```bash
cd examples/gemini

# SQLite (local, no setup needed)
python test_sqlite_employees.py        # ~30-60 seconds

# PostgreSQL (needs server running)
python test_postgresql_medical.py     # ~1-2 minutes

# MySQL (needs server running)
python test_mysql_ecommerce.py        # ~1-2 minutes
```

## Available Models

- **gemini-pro** (recommended) - Text generation and reasoning
- **gemini-1.5-pro** - Enhanced capabilities with larger context window
- **gemini-1.5-flash** - Faster responses with good performance

To change models, modify the `model` parameter:
```python
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",  # or "gemini-pro", "gemini-1.5-flash"
    temperature=0.1,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)
```

## Performance Notes

Google Gemini (cloud-based) is faster than local LLMs:
- Simple queries: ~5-15 seconds
- Complex queries: ~10-30 seconds
- Good handling of complex multi-step reasoning

For local/offline usage, consider:
- Ollama (local LLM)
- See `../ollama/` for examples

## Expected Output

Each test should show:
1. ✓ Connection successful
2. ✓ Tables discovered
3. ✓ Queries executed
4. 📊 Natural language answers
5. 🔍 Generated SQL queries
6. 📋 Query results

## Troubleshooting

### API Key not set
```bash
# Check if environment variable is set
echo $GOOGLE_API_KEY

# Set it for current session
export GOOGLE_API_KEY=your_api_key_here

# Or add to .env file
echo "GOOGLE_API_KEY=your_key" >> ../../.env
```

### Rate limit errors
- Gemini API has rate limits based on your tier
- Wait a few seconds between requests
- Consider upgrading API quota if needed

### Database connection errors
- PostgreSQL: Check credentials and that server is running
- MySQL: Install cryptography: `pip install cryptography`
- SQLite: Should work out of the box (creates DB automatically)

### Import errors
```bash
# Install Google Gemini support
pip install langchain-google-genai

# Or install all optional dependencies
pip install -e ".[google]"
```

## Next Steps

After testing with Gemini:
1. Try other LLM providers (see `../basic_usage.py`)
2. Try other database types
3. Add your own domain context
4. Connect to your own databases

## Comparison with Other Examples

- **examples/basic_usage.py** - Generic usage, any LLM provider
- **examples/medical_example.py** - Medical domain, AWS Bedrock
- **examples/multi_provider.py** - Different LLM providers comparison
- **examples/ollama/** - Local LLM with 3 database types
- **examples/gemini/** (this folder) - Google Gemini with 3 database types

## Cost Considerations

Google Gemini is a paid API service:
- Check current pricing at https://ai.google.dev/pricing
- Monitor your API usage in Google Cloud Console
- Consider using `gemini-1.5-flash` for cost-effective testing
- Each query typically uses 1000-5000 tokens depending on complexity
