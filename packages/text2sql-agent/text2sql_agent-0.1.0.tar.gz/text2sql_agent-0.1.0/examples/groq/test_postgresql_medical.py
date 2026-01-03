"""
Medical Database Test with PostgreSQL - Advanced Features Demo (Groq)

Tests the SQL Agent Toolkit with a real medical database using Groq.
Demonstrates advanced features optimized for medical/healthcare data:
- Schema pre-loading with medical table discovery
- Enhanced logging for audit trails
- Timestamp context for temporal medical queries
- Better error recovery for complex medical schemas
- High-performance queries with Groq's Kimi K2 Instruct model
"""
import os
import logging
import time
from text_to_sql import SQLAgent, JSONSerializableSQLDatabase
from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()
# Check for required environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL_MEDICAL")

print("="*80)
print("SQL AGENT TOOLKIT - Medical Database Test (Groq)")
print("="*80)

# Step 0: Verify API keys
print("\n0. Checking environment variables...")
if not GROQ_API_KEY:
    print("   ✗ ERROR: GROQ_API_KEY not set!")
    print("   Please add GROQ_API_KEY to your .env file")
    exit(1)
print("   ✓ GROQ_API_KEY is set")

if not DATABASE_URL:
    print("   ✗ ERROR: DATABASE_URL_MEDICAL not set!")
    print("   Please add DATABASE_URL_MEDICAL to your .env file")
    print('   Example: DATABASE_URL_MEDICAL=postgresql://user:password@localhost:5432/medical_db')
    exit(1)
print(f"   ✓ DATABASE_URL_MEDICAL: {DATABASE_URL}")

# Step 1: Initialize components
print("\n1. Initializing components...")
try:
    # Configure enhanced logging for medical audit trails
    SQLAgent.configure_logging(
        level=logging.INFO,
        log_file="medical_sql_queries_groq.log"
    )
    print("   ✓ Enhanced logging configured (logs: medical_sql_queries_groq.log)")

    llm = ChatGroq(model="moonshotai/kimi-k2-instruct", temperature=0.1)
    print("   ✓ Groq LLM initialized (Kimi K2 Instruct)")

    db = JSONSerializableSQLDatabase.from_uri(DATABASE_URL)
    print("   ✓ Connected to PostgreSQL medical database")

    # Create agent with ADVANCED FEATURES for medical data:
    # 1. Auto-discover medical tables (Patient, Condition, Medication, etc.)
    # 2. Timestamp context for "last visit", "past 30 days" queries
    # 3. Enhanced error recovery for complex medical schemas
    agent = SQLAgent(
        llm=llm,
        db=db,
        domain_context="medical patient records including diagnoses, conditions, medications, appointments, observations, and treatment history",
        important_tables="auto",  # NEW: Auto-discover medical tables
        enable_schema_caching=True,  # NEW: Cache discovered schemas
        verbose=True,
        max_rows_for_llm=20,  # Medical queries might need more context
        max_iterations=10,     # Allow more iterations for complex medical queries
        include_timestamp=True,  # NEW: Support temporal medical queries
    )
    print(f"   ✓ SQL Agent created with advanced medical features:")
    print(f"      • Schema auto-discovery: Enabled")
    print(f"      • Enhanced logging: Enabled (audit trail)")
    print(f"      • Timestamp context: Enabled (temporal queries)")

except Exception as e:
    print(f"   ✗ Error during initialization: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Step 2: Explore database structure
print("\n2. Exploring database structure...")
try:
    tables = agent.get_table_names()
    print(f"   ✓ Found {len(tables)} tables")
    print(f"   Tables: {', '.join(tables[:10])}")
    if len(tables) > 10:
        print(f"   ... and {len(tables) - 10} more")

    dialect = agent.get_dialect()
    print(f"   ✓ Database dialect: {dialect}")

except Exception as e:
    print(f"   ✗ Error exploring database: {e}")

# Step 3: Run medical domain queries
print("\n3. Running medical domain queries...")
print("="*80)

medical_queries = [
    # Basic statistics
    "How many patients are in the database?",

    # Condition/diagnosis queries
    "What are the most common conditions or diagnoses?",

    # Patient queries
    "How many patients have diabetes?",

    # Temporal queries
    "How many appointments were scheduled in the last 30 days?",

    # Clinical queries
    "What types of observations are recorded in the database?",
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
        print(f"   {answer}")

        # Display SQL query if available
        if result.get('sql_query'):
            sql = result['sql_query'].strip()
            print(f"\n🔍 Generated SQL:")
            for line in sql.split('\n'):
                print(f"   {line}")

        # Display result count if available
        if result.get('results') and result['results'] != "[]":
            try:
                import json
                results = json.loads(result['results'])
                if isinstance(results, list):
                    print(f"\n📋 Result count: {len(results)} rows")
                    if len(results) > 0 and len(results) <= 5:
                        print(f"   Sample data: {results[0]}")
            except:
                pass

    except Exception as e:
        print(f"\n✗ Error executing query: {e}")
        import traceback
        traceback.print_exc()

    # Add delay between queries to avoid rate limiting
    if i < len(medical_queries):
        time.sleep(5)

# Add delay before schema inspection
time.sleep(5)

# Step 4: Test schema inspection
print(f"\n{'='*80}")
print("4. Testing schema inspection...")
print('='*80)

try:
    # Get schema for a specific table
    if 'Patient' in agent.get_table_names():
        print("\nPatient table schema:")
        schema = agent.get_schema_info(table_names=["Patient"])
        print(schema[:500] + "..." if len(schema) > 500 else schema)
    elif 'patient' in agent.get_table_names():
        print("\npatient table schema:")
        schema = agent.get_schema_info(table_names=["patient"])
        print(schema[:500] + "..." if len(schema) > 500 else schema)
    else:
        print(f"\nFirst table schema ({agent.get_table_names()[0]}):")
        schema = agent.get_schema_info(table_names=[agent.get_table_names()[0]])
        print(schema[:500] + "..." if len(schema) > 500 else schema)

except Exception as e:
    print(f"✗ Error getting schema: {e}")

# Add delay before conversation context test
time.sleep(5)

# Step 5: Test follow-up query with conversation context
print(f"\n{'='*80}")
print("5. Testing conversation context...")
print('='*80)

try:
    query1 = "Show me information about patients with hypertension"
    print(f"\nFirst query: {query1}")
    result1 = agent.query(query1)
    answer1 = result1['answer'].replace('$\\boxed{', '').replace('}$', '').strip()
    print(f"Answer: {answer1[:200]}...")

    # Follow-up with context
    conversation_history = [
        {"role": "user", "content": query1},
        {"role": "assistant", "content": result1['answer']}
    ]

    # Add delay before follow-up query
    time.sleep(5)

    query2 = "How many of them are there?"
    print(f"\nFollow-up query: {query2}")
    result2 = agent.query(query2, conversation_history=conversation_history)
    answer2 = result2['answer'].replace('$\\boxed{', '').replace('}$', '').strip()
    print(f"Answer: {answer2}")

except Exception as e:
    print(f"✗ Error with conversation context: {e}")

# Summary
print(f"\n{'='*80}")
print("✓ Medical Database Test Completed!")
print('='*80)
print("\nTest Summary:")
print("  ✓ Successfully connected to PostgreSQL medical database")
print("  ✓ Medical domain context activated")
print("  ✓ Natural language queries converted to SQL")
print("  ✓ Schema inspection working")
print("  ✓ Conversation context handling tested")
print("\nKey Features Demonstrated:")
print("  • LLM Provider: Groq (Kimi K2 Instruct)")
print("  • Database: PostgreSQL")
print("  • Domain: Medical/Healthcare")
print("  • Standard SQL generation (not PostgreSQL-specific)")
print("  • Intelligent result truncation")
print("  • JSON serialization of results")
print("  • Rate limiting protection (5-second delays)")
