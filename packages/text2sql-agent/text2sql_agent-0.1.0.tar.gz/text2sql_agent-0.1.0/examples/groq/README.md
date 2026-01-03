# Groq Examples

This folder contains examples using Groq (fast cloud inference) with the SQL Agent Toolkit.

## Prerequisites

1. **Get Groq API Key**: https://console.groq.com/keys
2. **Set environment variable**:
   ```bash
   export GROQ_API_KEY=your_groq_api_key_here
   ```
   Or add to your `.env` file:
   ```bash
   echo "GROQ_API_KEY=your_api_key" >> ../../.env
   ```
3. **Install dependencies**:
   ```bash
   cd ../..  # Go to package root
   source venv/bin/activate
   pip install langchain-groq psycopg2-binary pymysql cryptography
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
- ✓ Groq with Llama 3.3 70B model

### 2. PostgreSQL Medical Database

```bash
python test_postgresql_medical.py
```

**What it tests:**
- ✓ PostgreSQL database with medical data
- ✓ Patient records, conditions, medications, appointments
- ✓ Temporal queries (last 30 days, etc.)
- ✓ Schema auto-discovery and caching
- ✓ Groq with Kimi K2 Instruct model

### 3. Spider Benchmark Evaluation

```bash
# First, download and setup the Spider dataset
python setup_spider.py

# Then run the benchmark
python test_spider_benchmark.py
```

**What it tests:**
- ✓ Industry-standard text-to-SQL benchmark
- ✓ 200+ cross-domain databases
- ✓ ~1000 dev set examples with varying difficulty
- ✓ Exact match and execution match evaluation
- ✓ Comprehensive performance metrics and reports

**Spider Benchmark Options:**
```bash
# Run on first 50 examples (default)
python test_spider_benchmark.py

# Run on first 100 examples
python test_spider_benchmark.py --limit 100

# Run on all examples (~1000+)
python test_spider_benchmark.py --all

# Test specific database
python test_spider_benchmark.py --database concert_singer

# Filter by difficulty
python test_spider_benchmark.py --difficulty easy

# Use different Groq model
python test_spider_benchmark.py --model llama-3.1-70b-versatile
```

## Available Models

Groq offers ultra-fast inference with several models:

- **llama-3.3-70b-versatile** (recommended) - Best balance of speed and quality
- **llama-3.1-70b-versatile** - Previous generation, still excellent
- **llama-3.1-8b-instant** - Fastest option for simple queries
- **mixtral-8x7b-32768** - Alternative with large context window
- **gemma2-9b-it** - Google's Gemma model

To change models, modify the `model` parameter:
```python
llm = ChatGroq(
    model="llama-3.3-70b-versatile",  # or any other Groq model
    temperature=0.1,
    groq_api_key=os.getenv("GROQ_API_KEY")
)
```

## Running the Tests

### Quick Test (SQLite only - no external database needed)
```bash
cd examples/groq
python test_sqlite_employees.py
```
Creates database automatically and runs all tests (~20-40 seconds).

### Run Spider Benchmark
```bash
cd examples/groq

# Step 1: Setup Spider dataset (one-time)
python setup_spider.py

# Step 2: Run benchmark evaluation
python test_spider_benchmark.py --limit 50
```
Downloads Spider dataset (~200MB), then evaluates on 50 examples (~5-10 minutes).

## Performance Notes

Groq offers extremely fast cloud-based inference:
- Simple queries: ~3-10 seconds
- Complex queries: ~8-20 seconds
- Excellent handling of complex multi-step reasoning
- Much faster than local LLMs
- Comparable or faster than other cloud providers

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
echo $GROQ_API_KEY

# Set it for current session
export GROQ_API_KEY=your_api_key_here

# Or add to .env file
echo "GROQ_API_KEY=your_key" >> ../../.env
```

### Rate limit errors
- Groq API has rate limits based on your tier
- Free tier: 30 requests/minute, 14,400 requests/day
- Wait a few seconds between requests if hitting limits
- Consider upgrading API quota if needed

### Database connection errors
- PostgreSQL: Check credentials and that server is running
- MySQL: Install cryptography: `pip install cryptography`
- SQLite: Should work out of the box (creates DB automatically)

### Import errors
```bash
# Install Groq support
pip install langchain-groq

# Or install from setup.py
pip install -e ".[groq]"
```

## Next Steps

After testing with Groq:
1. Try other LLM providers (see `../basic_usage.py`)
2. Try other database types
3. Add your own domain context
4. Connect to your own databases

## Comparison with Other Examples

- **examples/basic_usage.py** - Generic usage, any LLM provider
- **examples/medical_example.py** - Medical domain, AWS Bedrock
- **examples/multi_provider.py** - Different LLM providers comparison
- **examples/ollama/** - Local LLM with 3 database types
- **examples/gemini/** - Google Gemini with 3 database types
- **examples/groq/** (this folder) - Groq with ultra-fast inference

## Cost Considerations

Groq offers very competitive pricing:
- Free tier available with generous limits
- Check current pricing at https://console.groq.com/
- Monitor your API usage in the Groq console
- Groq is generally more cost-effective than many alternatives
- Each query typically uses 1000-5000 tokens depending on complexity

## Why Choose Groq?

- ⚡ **Speed**: Fastest inference among cloud providers
- 💰 **Cost**: Competitive pricing with generous free tier
- 🎯 **Quality**: State-of-the-art models (Llama 3.3, Mixtral, etc.)
- 🔧 **Easy**: Simple API compatible with LangChain
- 📊 **Reliable**: High uptime and consistent performance

## Spider Benchmark Details

### What is Spider?

Spider is a large-scale, complex, and cross-domain text-to-SQL benchmark dataset created by Yale University. It's widely used in research and industry to evaluate text-to-SQL systems.

**Key Features:**
- 200+ databases across diverse domains (music, sports, geography, etc.)
- 10,181 questions (8,659 train, 1,034 dev, 2,147 test)
- Complex queries requiring joins, nested queries, set operations
- Four difficulty levels: easy, medium, hard, extra hard
- Real-world database schemas with multiple tables

**Why Use Spider?**
- Industry-standard benchmark for text-to-SQL evaluation
- Covers wide range of SQL complexity and domains
- Enables fair comparison with other systems
- Identifies strengths and weaknesses of your approach

### Spider Benchmark Metrics

The evaluation reports several key metrics:

1. **Exact Match**: Generated SQL matches expected SQL exactly (after normalization)
2. **Execution Match**: Different SQL but produces same results
3. **Overall Accuracy**: Percentage of successful queries (exact or execution match)
4. **By Difficulty**: Accuracy breakdown by difficulty level (easy/medium/hard/extra)
5. **By Database**: Performance across different database domains

### Expected Performance

Typical accuracy ranges for text-to-SQL systems on Spider dev set:
- **Simple rule-based systems**: 10-30%
- **Early neural approaches**: 30-50%
- **Modern LLM-based systems**: 50-75%
- **State-of-the-art (2025)**: 75-85%
- **Human performance**: ~92%

Your mileage may vary depending on:
- LLM model quality and size
- Prompt engineering and context
- Schema understanding capabilities
- Maximum iterations and token limits

### Interpreting Results

**Good Performance:**
- Easy queries: >80% accuracy
- Medium queries: >60% accuracy
- Hard queries: >40% accuracy
- Overall: >60% accuracy

**Areas to Improve:**
- Low exact match but high execution match → SQL structure differs but logic is correct
- Low accuracy on specific databases → Domain-specific knowledge may help
- Low accuracy on complex queries → Consider increasing max_iterations or context

### Output Files

After running the benchmark, you'll get:
- Console report with overall metrics
- JSON file with detailed results: `spider_results_<model>_<timestamp>.json`
  - Per-example results with generated SQL
  - Success/failure status
  - Execution times
  - Accuracy by difficulty and database

### Tips for Better Performance

1. **Model Selection**: Use larger models (llama-3.3-70b-versatile) for better accuracy
2. **Temperature**: Keep low (0.1) for more deterministic SQL generation
3. **Context**: Provide relevant domain context when possible
4. **Iterations**: Allow sufficient max_iterations for complex queries (5-10)
5. **Rate Limits**: Be mindful of Groq API rate limits when running full benchmark

### Spider Dataset Structure

```
spider_data/
├── dev.json              # Dev set questions and SQL
├── train.json            # Training set (if needed)
├── tables.json           # Database schema metadata
└── database/             # SQLite database files
    ├── concert_singer/
    │   └── concert_singer.sqlite
    ├── pets_1/
    │   └── pets_1.sqlite
    └── ... (200+ databases)
```

### References

- **Spider Paper**: "Spider: A Large-Scale Human-Labeled Dataset for Complex and Cross-Domain Semantic Parsing and Text-to-SQL Task"
- **Website**: https://yale-lily.github.io/spider
- **GitHub**: https://github.com/taoyds/spider
- **Leaderboard**: Check the official leaderboard to compare with other systems
