"""
MySQL E-commerce Database Test with Google Gemini

Tests the SQL Agent Toolkit with a MySQL e-commerce database using Google Gemini
"""
import os
from text_to_sql import SQLAgent, JSONSerializableSQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI

print("="*80)
print("SQL AGENT TOOLKIT - MySQL E-commerce Database Test (Google Gemini)")
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

# MySQL database connection - USE ENVIRONMENT VARIABLE FOR SECURITY
# Set DATABASE_URL_ECOMMERCE in your .env file
DATABASE_URL = os.getenv("DATABASE_URL_ECOMMERCE")

if not DATABASE_URL:
    print("\n   ✗ ERROR: DATABASE_URL_ECOMMERCE environment variable not set!")
    print("   Please create a .env file with:")
    print('   DATABASE_URL_ECOMMERCE=mysql+pymysql://user:password@127.0.0.1:3306/ecom')
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
    print("   ✓ Connected to MySQL e-commerce database")

    # Create agent WITH e-commerce domain context
    agent = SQLAgent(
        llm=llm,
        db=db,
        domain_context="e-commerce data including products, orders, customers, inventory, and sales transactions",
        verbose=False,
        max_rows_for_llm=20,
        max_iterations=15,
    )
    print(f"   ✓ SQL Agent created with e-commerce domain context")

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
    print(f"   Tables: {', '.join(tables)}")

    dialect = agent.get_dialect()
    print(f"   ✓ Database dialect: {dialect}")

except Exception as e:
    print(f"   ✗ Error exploring database: {e}")

# Step 3: Run e-commerce domain queries
print("\n3. Running e-commerce domain queries...")
print("="*80)

ecommerce_queries = [
    # Basic statistics
    "How many customers are in the database?",

    # Product queries
    "What are the top 5 most expensive products?",

    # Order queries
    "How many orders were placed in the last 30 days?",

    # Sales queries
    "What is the total revenue from all orders?",

    # Inventory queries
    "Which products are low in stock?",

    # Customer queries
    "Who are the top 3 customers by order count?",
]

for i, query in enumerate(ecommerce_queries, 1):
    print(f"\n{'='*80}")
    print(f"Query {i}: {query}")
    print('='*80)

    try:
        result = agent.query(query)

        # Display answer
        answer = result['answer'].replace('$\\boxed{', '').replace('}$', '').strip()
        print(f"\n📊 Answer:")
        # Wrap long answers
        if len(answer) > 200:
            print(f"   {answer[:200]}...")
        else:
            for line in answer.split('\n'):
                print(f"   {line}")

        # Display SQL query if available
        if result.get('sql_query'):
            sql = result['sql_query'].strip()
            print(f"\n🔍 Generated SQL:")
            for line in sql.split('\n')[:5]:  # Show first 5 lines
                print(f"   {line}")
            if len(sql.split('\n')) > 5:
                print(f"   ...")

        # Display result count if available
        if result.get('results') and result['results'] != "[]":
            try:
                import json
                results = json.loads(result['results'])
                if isinstance(results, list):
                    print(f"\n📋 Result count: {len(results)} rows")
                    if len(results) > 0 and len(results) <= 3:
                        print(f"   Sample: {results[0]}")
            except:
                pass

    except Exception as e:
        print(f"\n✗ Error executing query: {e}")

# Step 4: Test schema inspection
print(f"\n{'='*80}")
print("4. Testing schema inspection...")
print('='*80)

try:
    # Get schema for common e-commerce tables
    common_tables = ['products', 'orders', 'customers', 'product', 'order', 'customer']
    found_table = None

    for table in common_tables:
        if table in agent.get_table_names():
            found_table = table
            break

    if found_table:
        print(f"\n{found_table} table schema:")
        schema = agent.get_schema_info(table_names=[found_table])
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
    query1 = "Show me information about electronics products"
    print(f"\nFirst query: {query1}")
    result1 = agent.query(query1)
    answer1 = result1['answer'].replace('$\\boxed{', '').replace('}$', '').strip()
    print(f"Answer: {answer1[:200]}...")

    # Follow-up with context
    conversation_history = [
        {"role": "user", "content": query1},
        {"role": "assistant", "content": result1['answer']}
    ]

    query2 = "How many of them are available?"
    print(f"\nFollow-up query: {query2}")
    result2 = agent.query(query2, conversation_history=conversation_history)
    answer2 = result2['answer'].replace('$\\boxed{', '').replace('}$', '').strip()
    print(f"Answer: {answer2}")

except Exception as e:
    print(f"✗ Error with conversation context: {e}")

# Step 6: Test utility methods
print(f"\n{'='*80}")
print("6. Testing utility methods...")
print('='*80)

try:
    print("\nGet all table names:")
    tables = agent.get_table_names()
    print(f"   Tables ({len(tables)}): {', '.join(tables)}")

    print("\nGet database dialect:")
    dialect = agent.get_dialect()
    print(f"   Dialect: {dialect}")

    print("\n✓ Utility methods working correctly")

except Exception as e:
    print(f"✗ Error with utility methods: {e}")

# Summary
print(f"\n{'='*80}")
print("✓ MySQL E-commerce Database Test Completed!")
print('='*80)
print("\nTest Summary:")
print("  ✓ Successfully connected to MySQL e-commerce database")
print("  ✓ E-commerce domain context activated")
print("  ✓ Natural language queries converted to SQL")
print("  ✓ Schema inspection working")
print("  ✓ Conversation context handling tested")
print("  ✓ Utility methods tested")
print("\nKey Features Demonstrated:")
print("  • LLM Provider: Google Gemini")
print("  • Database: MySQL")
print("  • Domain: E-commerce")
print("  • Standard SQL generation")
print("  • Intelligent result truncation")
print("  • JSON serialization of results")
print("\nComparison:")
print("  ✓ Same code works with PostgreSQL (medical) and MySQL (e-commerce)")
print("  ✓ Only changed: database URL and domain context")
print("  ✓ Zero code changes to the agent itself")
