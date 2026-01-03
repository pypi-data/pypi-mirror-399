# Spider Benchmark Quick Start Guide

This guide will help you get started with evaluating your SQL Agent on the Spider benchmark using Groq.

## What You'll Need

1. **Groq API Key** - Get it from [console.groq.com/keys](https://console.groq.com/keys)
2. **Python 3.8+** with required packages installed
3. **~500MB disk space** for the Spider dataset
4. **~10-60 minutes** depending on how many examples you want to evaluate

## Step-by-Step Setup

### 1. Install Dependencies

```bash
# Navigate to project root
cd /path/to/text-to-sql

# Activate virtual environment (if using one)
source venv/bin/activate

# Install required packages
pip install langchain-groq python-dotenv
```

### 2. Set Up Groq API Key

```bash
# Option A: Set environment variable
export GROQ_API_KEY=your_groq_api_key_here

# Option B: Add to .env file in project root
echo "GROQ_API_KEY=your_groq_api_key_here" >> .env
```

### 3. Download Spider Dataset

```bash
# Navigate to groq examples directory
cd examples/groq

# Run setup script (one-time, ~2-5 minutes)
python setup_spider.py
```

This will:
- Download the Spider dataset from GitHub (~200MB)
- Extract 200+ SQLite databases
- Verify dataset structure
- Show dataset statistics

**Expected output:**
```
================================================================================
SPIDER DATASET SETUP
================================================================================

1. Downloading Spider dataset...
   Progress: 100.0% (209715200/209715200 bytes)

2. Extracting dataset...
   ✓ Dataset extracted successfully

3. Verifying dataset structure...
   ✓ Found: dev.json
   ✓ Found: tables.json
   ✓ Found 206 databases

4. Spider Dataset Statistics...
   📊 Dev Set Statistics:
      • Total examples: 1034
      • Unique databases: 20
      • Difficulty distribution:
         - easy: 248 (24.0%)
         - extra: 165 (16.0%)
         - hard: 174 (16.8%)
         - medium: 446 (43.1%)

================================================================================
✓ SPIDER DATASET SETUP COMPLETE!
================================================================================
```

### 4. Run Your First Benchmark

Start with a small sample to test your setup:

```bash
# Test with 10 examples (fastest, ~2-3 minutes)
python test_spider_benchmark.py --limit 10
```

**Expected output:**
```
================================================================================
SPIDER BENCHMARK EVALUATION WITH GROQ
================================================================================

Configuration:
  • Model: llama-3.3-70b-versatile
  • Temperature: 0.1
  • Spider directory: spider_data

Evaluating 10 examples...

================================================================================
[1/10] Database: concert_singer | Difficulty: easy
Question: How many singers do we have?
================================================================================

Generated SQL:
SELECT COUNT(*) FROM singer

Expected SQL:
SELECT count(*) FROM singer

✓ EXACT MATCH!

[... more examples ...]

================================================================================
EVALUATION REPORT
================================================================================

📊 Overall Results:
   • Total examples: 10
   • Successful: 7 (70.0%)
   • Exact matches: 5 (50.0%)
   • Execution matches: 2 (20.0%)
   • Errors: 3
   • Total time: 45.2s
   • Avg time per query: 4.5s

📈 By Difficulty:
   • easy: 4/5 (80.0%)
   • medium: 2/3 (66.7%)
   • hard: 1/2 (50.0%)

💾 Detailed results saved to: spider_results_llama-3.3-70b-versatile_20250129_143022.json

================================================================================
✓ BENCHMARK COMPLETE!
================================================================================
```

## Running Different Evaluations

### Quick Test (10 examples, ~2-3 minutes)
```bash
python test_spider_benchmark.py --limit 10
```

### Standard Test (50 examples, ~8-12 minutes)
```bash
python test_spider_benchmark.py --limit 50
```

### Medium Test (100 examples, ~15-25 minutes)
```bash
python test_spider_benchmark.py --limit 100
```

### Full Benchmark (1000+ examples, ~2-4 hours)
```bash
python test_spider_benchmark.py --all
```

### Test Specific Database
```bash
python test_spider_benchmark.py --database concert_singer
python test_spider_benchmark.py --database pets_1
```

### Filter by Difficulty
```bash
python test_spider_benchmark.py --difficulty easy --limit 50
python test_spider_benchmark.py --difficulty medium --limit 50
python test_spider_benchmark.py --difficulty hard --limit 25
```

### Use Different Model
```bash
# Faster but less accurate
python test_spider_benchmark.py --model llama-3.1-8b-instant --limit 50

# Previous generation (still excellent)
python test_spider_benchmark.py --model llama-3.1-70b-versatile --limit 50

# Alternative model with large context
python test_spider_benchmark.py --model mixtral-8x7b-32768 --limit 50
```

## Understanding the Results

### Metrics Explained

1. **Total examples**: Number of questions evaluated
2. **Successful**: Questions where generated SQL returned correct results
3. **Exact matches**: Generated SQL exactly matches expected SQL (after normalization)
4. **Execution matches**: Different SQL but produces same results (still correct!)
5. **Errors**: Questions where SQL failed to execute or returned wrong results

### Success Rate Benchmarks

| Accuracy Range | Evaluation |
|---------------|-----------|
| 80%+ | Excellent! State-of-the-art performance |
| 60-80% | Very Good - Modern LLM baseline |
| 40-60% | Good - Significant room for improvement |
| 20-40% | Fair - Consider tuning parameters |
| <20% | Poor - Check configuration |

### What's a Good Score?

- **Easy queries**: Aim for >80%
- **Medium queries**: Aim for >60%
- **Hard queries**: Aim for >40%
- **Overall**: Aim for >60%

Human expert performance on Spider is ~92%, so don't expect 100%!

## Output Files

After each run, you get a JSON file with detailed results:

```
spider_results_llama-3.3-70b-versatile_20250129_143022.json
```

**Contains:**
- Overall metrics (accuracy, success rate, etc.)
- Per-example results (question, generated SQL, expected SQL, success/failure)
- Execution times
- Breakdown by difficulty and database

**Example result entry:**
```json
{
  "index": 0,
  "db_id": "concert_singer",
  "question": "How many singers do we have?",
  "expected_sql": "SELECT count(*) FROM singer",
  "difficulty": "easy",
  "success": true,
  "generated_sql": "SELECT COUNT(*) FROM singer",
  "exact_match": true,
  "execution_match": false,
  "error": null,
  "execution_time_ms": 3245
}
```

## Troubleshooting

### "GROQ_API_KEY not set"
```bash
# Check if set
echo $GROQ_API_KEY

# Set it
export GROQ_API_KEY=your_key_here

# Or add to .env file
echo "GROQ_API_KEY=your_key" >> ../../.env
```

### "Spider dataset not found"
```bash
# Run setup script first
python setup_spider.py
```

### "Rate limit exceeded"
- Groq free tier: 30 requests/minute, 14,400/day
- The script adds 2-second delays between queries
- If still hitting limits, reduce --limit or upgrade your API tier
- Check usage at [console.groq.com](https://console.groq.com)

### Low accuracy scores
Try these improvements:
1. Use larger model: `--model llama-3.3-70b-versatile`
2. Check if errors are concentrated in hard queries (this is expected)
3. Review failed examples in the output JSON
4. Consider adjusting agent parameters in the code (max_iterations, max_rows_for_llm)

### Import errors
```bash
# Install langchain-groq
pip install langchain-groq

# Install from project root
pip install -e .
```

## Next Steps

### 1. Analyze Results
Open the generated JSON file to see:
- Which types of queries failed
- Which databases performed poorly
- Execution times

### 2. Improve Performance
Based on results, try:
- Using different models
- Adjusting agent parameters (in test_spider_benchmark.py)
- Adding domain-specific context
- Increasing max_iterations for complex queries

### 3. Compare Models
Run benchmark with different models:
```bash
python test_spider_benchmark.py --limit 50 --model llama-3.3-70b-versatile
python test_spider_benchmark.py --limit 50 --model llama-3.1-70b-versatile
python test_spider_benchmark.py --limit 50 --model mixtral-8x7b-32768
```

Compare the results files to see which model performs best.

### 4. Test Your Changes
After improving your SQL Agent:
```bash
# Run same test for comparison
python test_spider_benchmark.py --limit 50
```

### 5. Full Evaluation
Once satisfied with small-scale results:
```bash
# Run on all examples for official benchmark
python test_spider_benchmark.py --all
```

## Tips for Better Results

1. **Start Small**: Test with --limit 10 first to verify setup
2. **Check Free Tier**: Monitor your Groq API usage
3. **Save Results**: Keep result JSON files for comparison
4. **Focus Areas**: If overall accuracy is good, focus on hard queries
5. **Database-Specific**: If some databases perform poorly, add domain context
6. **Iterate**: Make changes, test, compare results

## Cost Estimation

**Groq Free Tier:**
- 30 requests/minute
- 14,400 requests/day
- Usually sufficient for full benchmark

**Estimated costs (if using paid tier):**
- 10 examples: ~$0.01-0.05
- 50 examples: ~$0.05-0.25
- 100 examples: ~$0.10-0.50
- 1000+ examples: ~$1-5

*(Actual costs depend on query complexity and model chosen)*

## Getting Help

If you run into issues:

1. Check this guide's troubleshooting section
2. Review the main README: [examples/groq/README.md](README.md)
3. Check Spider official docs: https://yale-lily.github.io/spider
4. Review Groq docs: https://console.groq.com/docs

## Summary

```bash
# Complete workflow:

# 1. Setup (one-time)
python setup_spider.py

# 2. Quick test
python test_spider_benchmark.py --limit 10

# 3. Standard test
python test_spider_benchmark.py --limit 50

# 4. Analyze results
cat spider_results_*.json

# 5. Full benchmark
python test_spider_benchmark.py --all
```

Happy benchmarking! 🚀
