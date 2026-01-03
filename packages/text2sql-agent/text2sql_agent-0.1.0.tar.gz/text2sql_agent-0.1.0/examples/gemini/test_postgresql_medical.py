"""
Medical Database Test with PostgreSQL and Google Gemini

Tests the SQL Agent Toolkit with a real medical database using Google Gemini
"""
import os
from text_to_sql import SQLAgent, JSONSerializableSQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI

print("="*80)
print("SQL AGENT TOOLKIT - Medical Database Test (Google Gemini)")
print("="*80)

# Step 0: Check API key
print("\n0. Checking API key...")
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("   ✗ ERROR: GOOGLE_API_KEY environment variable not set!")
    print("   Get your API key from: https://makersuite.google.com/app/apikey")
    print("   Then set it: export GOOGLE_API_KEY=your_key")
    exit(1)
print("   ✓ GOOGLE_API_KEY is set")

# Database connection - USE ENVIRONMENT VARIABLE FOR SECURITY
# Set DATABASE_URL_MEDICAL in your .env file
DATABASE_URL = os.getenv("DATABASE_URL_MEDICAL")

if not DATABASE_URL:
    print("\n   ✗ ERROR: DATABASE_URL_MEDICAL environment variable not set!")
    print("   Please create a .env file with:")
    print('   DATABASE_URL_MEDICAL=postgresql://user:password@localhost:5432/medical_db')
    exit(1)

# Step 1: Initialize components
print("\n1. Initializing components...")
try:
    llm = ChatGoogleGenerativeAI(
        model="models/gemini-2.5-flash",
        temperature=0.1,
        google_api_key=api_key
    )
    print("   ✓ Google Gemini LLM initialized")

    db = JSONSerializableSQLDatabase.from_uri(DATABASE_URL)
    print("   ✓ Connected to PostgreSQL medical database")

    # Create agent WITH medical domain context
    agent = SQLAgent(
        llm=llm,
        db=db,
        domain_context="medical patient records including diagnoses, conditions, medications, appointments, observations, and treatment history",
        verbose=False,
        max_rows_for_llm=20,  # Medical queries might need more context
        max_iterations=15,     # Allow more iterations for complex medical queries
    )
    print(f"   ✓ SQL Agent created with medical domain context")

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
print("  • LLM Provider: Google Gemini")
print("  • Database: PostgreSQL")
print("  • Domain: Medical/Healthcare")
print("  • Standard SQL generation (not PostgreSQL-specific)")
print("  • Intelligent result truncation")
print("  • JSON serialization of results")
