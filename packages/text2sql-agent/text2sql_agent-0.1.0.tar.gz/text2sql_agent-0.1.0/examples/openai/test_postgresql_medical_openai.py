"""
Medical Database Test with PostgreSQL - OpenAI GPT-4o

Tests the SQL Agent Toolkit with medical database using OpenAI.
Demonstrates that the same code works across LLM providers.

Usage:
  1. pip install langchain-openai openai
  2. Set OPENAI_API_KEY in .env file
  3. python test_postgresql_medical_openai.py
"""
import os
import time
import logging
from text_to_sql import SQLAgent, JSONSerializableSQLDatabase
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# Environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL_MEDICAL")

print("="*80)
print("SQL AGENT TOOLKIT - Medical Database Test (OpenAI GPT-4o)")
print("="*80)

print("\n0. Checking environment variables...")
if not OPENAI_API_KEY:
    print("   ✗ ERROR: OPENAI_API_KEY not set!")
    print("   Please add to .env file: OPENAI_API_KEY=your-key-here")
    exit(1)
print("   ✓ OPENAI_API_KEY is set")

if not DATABASE_URL:
    print("   ✗ ERROR: DATABASE_URL_MEDICAL not set!")
    exit(1)
print(f"   ✓ DATABASE_URL_MEDICAL: {DATABASE_URL}")

# Step 1: Initialize components
print("\n1. Initializing components...")
try:
    SQLAgent.configure_logging(
        level=logging.INFO,
        log_file="medical_sql_queries_openai.log"
    )
    print("   ✓ Enhanced logging configured (logs: medical_sql_queries_openai.log)")

    # Initialize OpenAI GPT-4o
    llm = ChatOpenAI(
        model="gpt-4o",  # Options: gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo
        temperature=0.1,
        timeout=30
    )
    print("   ✓ OpenAI LLM initialized (GPT-4o)")

    db = JSONSerializableSQLDatabase.from_uri(DATABASE_URL)
    print("   ✓ Connected to PostgreSQL medical database")

    agent = SQLAgent(
        llm=llm,
        db=db,
        domain_context="medical patient records including diagnoses, conditions, medications, appointments, observations, and treatment history",
        important_tables="auto",
        enable_schema_caching=True,
        verbose=True,
        max_rows_for_llm=20,
        max_iterations=10,
        include_timestamp=True,
    )
    print(f"   ✓ SQL Agent created with OpenAI GPT-4o")

except Exception as e:
    print(f"   ✗ Error during initialization: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Step 2: Run test queries
print("\n2. Running medical domain queries...")
print("="*80)

medical_queries = [
    "How many patients are in the database?",
    "What are the most common conditions or diagnoses?",
    "How many patients have diabetes?",
    "How many appointments were scheduled in the last 30 days?",
]

for i, query in enumerate(medical_queries, 1):
    print(f"\n{'='*80}")
    print(f"Query {i}: {query}")
    print('='*80)

    try:
        result = agent.query(query)

        # Display answer
        answer = result['answer'].replace('$\\boxed{', '').replace('}$', '').strip()
        print(f"\n📊 Answer:")
        for line in answer.split('\n')[:5]:
            print(f"   {line}")

        # Display SQL
        if result.get('sql_query'):
            print(f"\n🔍 Generated SQL:")
            for line in result['sql_query'].strip().split('\n')[:3]:
                print(f"   {line}")

    except Exception as e:
        print(f"\n✗ Error executing query: {e}")

    # Rate limiting
    if i < len(medical_queries):
        time.sleep(2)  # OpenAI has higher rate limits than Groq

# Summary
print(f"\n{'='*80}")
print("✓ OpenAI Medical Database Test Completed!")
print('='*80)
print("\nKey Features:")
print("  • LLM Provider: OpenAI GPT-4o")
print("  • Database: PostgreSQL (medical)")
print("  • Expected Accuracy: 95-100%")
print("  • Cost: ~$0.005-0.015 per query")
print("\n💡 Model Options:")
print("  • gpt-4o: Best quality, fast, recommended")
print("  • gpt-4o-mini: Good quality, faster, cheaper")
print("  • gpt-4-turbo: Excellent quality, slower")
print("  • gpt-3.5-turbo: Fast & cheap but lower accuracy (not recommended)")
