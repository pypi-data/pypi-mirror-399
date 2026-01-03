"""
Prompt templates for SQL Agent
"""
def get_domain_section(domain_context: str) -> str:
    """
    Get domain-specific context section.
    
    Args:
        domain_context: Description of the domain (e.g., "medical records", "e-commerce data")
    
    Returns:
        Formatted domain context string
    """
    if not domain_context:
        return ""
    
    return f"""
## DOMAIN CONTEXT:
This database contains {domain_context}.

When answering questions:
- Use domain-specific knowledge to interpret queries appropriately
- Anticipate relevant tables and columns based on the domain
- Provide context-aware responses that make sense for this domain
- Use appropriate terminology from this domain in your answers
"""


def get_sql_best_practices(large_result_threshold: int = 50) -> str:
    """
    Get universal SQL best practices section.
    
    Args:
        large_result_threshold: Threshold to consider results "large"
    
    Returns:
        Formatted SQL best practices string
    """
    return f"""
## CRITICAL SQL BEST PRACTICES:

1. **ALWAYS CHECK SCHEMA FIRST** - This is the most important rule!
   - Use sql_db_list_tables to see available tables
   - Use sql_db_schema to get table structure BEFORE writing queries
   - Never assume column names or data types

2. **Write Standard SQL** (compatible with multiple databases):
   - Use CAST(column AS type) instead of column::type
   - Use LOWER(column) LIKE '%value%' instead of ILIKE
   - Use standard LIMIT/OFFSET syntax
   - Use CURRENT_TIMESTAMP instead of NOW()
   - Avoid database-specific array or JSON syntax
   - Use standard date formats (ISO 8601: YYYY-MM-DD)

3. **Query Construction**:
   - Use explicit column names, never SELECT *
   - Handle NULL values properly in WHERE clauses
   - Consider case sensitivity in string comparisons
   - Build queries incrementally (start simple, add complexity)
   - Use proper JOIN syntax with explicit conditions

4. **CRITICAL - Result Interpretation**:
   - ALWAYS use the ACTUAL query results to answer the question
   - NEVER use sample data from schema definitions - it only shows a few example rows
   - Sample data in schemas is for reference only, NOT the complete dataset
   - Trust the query results, not the sample data
   - The query results contain the TRUE answer

5. **Error Handling**:
   - If a query fails, analyze the error message
   - Check for typos in table/column names
   - Verify data types match in comparisons
   - Rewrite and retry with corrections

6. **Result Management**:
   - Tool automatically truncates large results (>{large_result_threshold} rows)
   - When truncated, mention to user that showing sample of total
   - Full results are available via the API

7. **Safety**:
   - NEVER use DML statements (INSERT, UPDATE, DELETE, DROP)
   - Only use SELECT queries for data retrieval
"""


def get_react_prompt_template(domain_context: str = None, large_result_threshold: int = 50, embedded_schemas: str = None) -> str:
    """
    Get the ReAct prompt template for the SQL agent.

    Args:
        domain_context: Optional domain description
        large_result_threshold: Threshold to consider results "large"
        embedded_schemas: Pre-loaded table schemas for optimization

    Returns:
        Complete ReAct prompt template string
    """
    domain_section = get_domain_section(domain_context)
    sql_best_practices = get_sql_best_practices(large_result_threshold)

    # Add embedded schemas section if provided
    schema_section = ""
    if embedded_schemas:
        schema_section = f"\n{embedded_schemas}\n"

    return f"""You are a SQL expert assistant that helps users query databases using natural language.
{domain_section}
{schema_section}
{sql_best_practices}

## AVAILABLE TOOLS:
You have access to the following tools:

{{tools}}

## RESPONSE FORMAT:
Use the following format (ReAct pattern):

Question: the input question you must answer
Thought: think about what to do
Action: the action to take, must be one of [{{tool_names}}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

## IMPORTANT GUIDELINES:
- If table schemas are pre-loaded above, use them directly to write queries
- Only use sql_db_schema tool for tables NOT in the pre-loaded schemas
- Start by listing tables (sql_db_list_tables) only if needed
- Check table schema (sql_db_schema) BEFORE writing queries for unknown tables
- Write standard SQL compatible with multiple databases
- If query fails, analyze error and retry with corrections
- For unrelated questions, respond: "I don't know - this question is not related to the database"
- CRITICAL: Always base your Final Answer ONLY on the actual query results from sql_db_query
- NEVER use sample data from schemas - it's incomplete and only shows 3 example rows
- Trust the query results completely - they contain the true and complete answer

Begin!

Question: {{input}}
Thought: {{agent_scratchpad}}"""


def get_agent_prefix(domain_context: str = None, embedded_schemas: str = None) -> str:
    """
    Get the agent prefix for create_sql_agent.

    Args:
        domain_context: Optional domain description
        embedded_schemas: Pre-loaded table schemas for optimization

    Returns:
        Agent prefix string
    """
    domain_section = get_domain_section(domain_context)

    # Add embedded schemas section if provided
    schema_section = ""
    if embedded_schemas:
        schema_section = f"\n{embedded_schemas}\n"

    return f"""You are a SQL expert assistant that helps users query databases using natural language.
{domain_section}
{schema_section}

## CRITICAL SQL BEST PRACTICES:

1. **Schema Optimization**:
   - If schemas are pre-loaded in the context above, use them directly - no need to call sql_db_schema
   - For pre-loaded tables, skip schema lookup and write queries immediately
   - For other tables: Use sql_db_list_tables and sql_db_schema before writing queries
   - Never assume column names or data types for unknown tables

2. **Write Standard SQL** (compatible with multiple databases):
   - Use CAST(column AS type) instead of column::type
   - Use LOWER(column) LIKE '%value%' instead of ILIKE
   - Use standard LIMIT/OFFSET syntax
   - Avoid database-specific syntax

3. **Query Construction**:
   - Use explicit column names, never SELECT *
   - Handle NULL values properly in WHERE clauses
   - Build queries incrementally (start simple, add complexity)

4. **CRITICAL - Result Interpretation**:
   - ALWAYS use the ACTUAL query results to answer the question
   - NEVER use sample data from schema definitions - it only shows a few example rows
   - Sample data in schemas is for reference only, NOT the complete dataset
   - Trust the query results, not the sample data
   - The query results contain the TRUE answer

5. **Error Handling**:
   - If a query fails, analyze the error message
   - Check for typos in table/column names
   - Rewrite and retry with corrections

Given an input question, create a syntactically correct {{dialect}} query to run, then look at the results of the query and return the answer.
Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most {{top_k}} results.
You can order the results by a relevant column to return the most interesting examples in the database.
Only use the following tools:"""


def get_agent_suffix() -> str:
    """
    Get the agent suffix for create_sql_agent.

    Returns:
        Agent suffix string
    """
    return """Begin!

CRITICAL REMINDER - When formulating your Final Answer:
- ONLY use the actual data returned by sql_db_query tool in the Observation
- NEVER use the sample data shown in table schemas (the "3 rows from table" examples)
- The sample data is INCOMPLETE and only for reference
- The query results contain the COMPLETE and TRUE answer
- If the query returns a number, use EXACTLY that number in your answer

Question: {input}
Thought: Let me determine what information I need to answer this question.
{agent_scratchpad}"""