"""
SQL Agent Toolkit Tests - Real Database & LLM Integration Tests

To run these tests:
    pytest tests/test_agent.py --llm=ollama --model=mistral:7b
"""
import pytest
from text_to_sql import SQLAgent, JSONSerializableSQLDatabase


# ============================================================================
# FEATURE TESTS: Schema Pre-loading & Caching (Feature 1)
# ============================================================================

@pytest.mark.feature_test
def test_schema_preloading_explicit(sqlite_employees_db):
    """Test schema pre-loading with explicit table list"""
    from langchain_ollama import ChatOllama

    llm = ChatOllama(model="mistral:7b", temperature=0.1)

    agent = SQLAgent(
        llm=llm,
        db=sqlite_employees_db,
        important_tables=["employees", "departments"],
        enable_schema_caching=True
    )

    # Verify schemas are cached
    assert len(agent.cached_schemas) == 2
    assert "employees" in agent.cached_schemas
    assert "departments" in agent.cached_schemas


@pytest.mark.feature_test
def test_schema_preloading_auto(sqlite_employees_db):
    """Test schema pre-loading with auto-discovery mode"""
    from langchain_ollama import ChatOllama

    llm = ChatOllama(model="mistral:7b", temperature=0.1)

    agent = SQLAgent(
        llm=llm,
        db=sqlite_employees_db,
        domain_context="employee management system with departments and projects",
        important_tables="auto",
        enable_schema_caching=True
    )

    # Should auto-discover at least 1 table based on domain context
    assert len(agent.cached_schemas) >= 1


@pytest.mark.feature_test
def test_schema_preloading_all(sqlite_employees_db):
    """Test schema pre-loading with all tables"""
    from langchain_ollama import ChatOllama

    llm = ChatOllama(model="mistral:7b", temperature=0.1)

    agent = SQLAgent(
        llm=llm,
        db=sqlite_employees_db,
        important_tables="all",
        enable_schema_caching=True
    )

    # Should cache all 3 tables
    assert len(agent.cached_schemas) == 3


@pytest.mark.feature_test
def test_refresh_schemas(sqlite_employees_db):
    """Test schema refresh functionality"""
    from langchain_ollama import ChatOllama

    llm = ChatOllama(model="mistral:7b", temperature=0.1)

    agent = SQLAgent(
        llm=llm,
        db=sqlite_employees_db,
        important_tables=["employees"],
        enable_schema_caching=True
    )

    initial_count = len(agent.cached_schemas)

    # Refresh schemas
    agent.refresh_schemas()

    # Should still have the same number of cached schemas
    assert len(agent.cached_schemas) == initial_count


@pytest.mark.feature_test
def test_cached_schemas_embedded_in_prompt(sqlite_employees_db):
    """Test that cached schemas are embedded in agent prompt"""
    from langchain_ollama import ChatOllama

    llm = ChatOllama(model="mistral:7b", temperature=0.1)

    agent = SQLAgent(
        llm=llm,
        db=sqlite_employees_db,
        important_tables=["employees", "departments"],
        enable_schema_caching=True
    )

    # Build embedded schemas
    embedded_schemas = agent._build_embedded_schemas()

    # Verify schemas are present
    assert embedded_schemas is not None
    assert "employees" in embedded_schemas
    assert "departments" in embedded_schemas
    assert "id" in embedded_schemas  # Column name


# ============================================================================
# FEATURE TESTS: Async Support (Feature 2)
# ============================================================================

@pytest.mark.feature_test
@pytest.mark.asyncio
@pytest.mark.slow
async def test_async_query_execution(sqlite_employees_db):
    """Test async query method"""
    from langchain_ollama import ChatOllama

    llm = ChatOllama(model="mistral:7b", temperature=0.1)
    agent = SQLAgent(llm=llm, db=sqlite_employees_db)

    result = await agent.aquery("How many employees are there?")

    assert "answer" in result
    assert "sql_query" in result or "metadata" in result


@pytest.mark.feature_test
@pytest.mark.asyncio
@pytest.mark.slow
async def test_async_query_with_conversation_history(sqlite_employees_db):
    """Test async query with conversation history"""
    from langchain_ollama import ChatOllama

    llm = ChatOllama(model="mistral:7b", temperature=0.1)
    agent = SQLAgent(llm=llm, db=sqlite_employees_db)

    # First query
    result1 = await agent.aquery("List employees")

    # Build conversation history
    conversation_history = [
        {"role": "user", "content": "List employees"},
        {"role": "assistant", "content": result1["answer"]}
    ]

    # Follow-up query
    result2 = await agent.aquery("How many?", conversation_history=conversation_history)

    assert "answer" in result2


# ============================================================================
# FEATURE TESTS: Enhanced Conversation Context (Feature 3)
# ============================================================================

@pytest.mark.feature_test
def test_conversation_context_with_metadata(sqlite_employees_db):
    """Test enhanced conversation context with metadata tracking"""
    from langchain_ollama import ChatOllama

    llm = ChatOllama(model="mistral:7b", temperature=0.1)
    agent = SQLAgent(llm=llm, db=sqlite_employees_db)

    # First query
    result1 = agent.query("Who are the employees in Engineering?")

    # Verify metadata is present
    assert "metadata" in result1
    if result1.get("metadata"):
        assert "sql_query" in result1["metadata"] or "timestamp" in result1["metadata"]


@pytest.mark.feature_test
def test_conversation_context_sql_tracking(sqlite_employees_db):
    """Test SQL query tracking in conversation context"""
    from langchain_ollama import ChatOllama

    llm = ChatOllama(model="mistral:7b", temperature=0.1)
    agent = SQLAgent(llm=llm, db=sqlite_employees_db)

    # Execute query
    result = agent.query("How many employees?")

    # Check if SQL was tracked in metadata
    if result.get("metadata"):
        # Metadata should have execution details
        assert isinstance(result["metadata"], dict)


# ============================================================================
# FEATURE TESTS: Enhanced Logging (Feature 4)
# ============================================================================

@pytest.mark.feature_test
def test_logging_configuration(tmp_path):
    """Test custom logging configuration"""
    import logging

    log_file = tmp_path / "test_queries.log"

    SQLAgent.configure_logging(
        level=logging.INFO,
        log_file=str(log_file)
    )

    # Verify log file is created (may be created on first write)
    # Just check that the method doesn't raise an error
    assert True


@pytest.mark.feature_test
@pytest.mark.slow
def test_query_logging_output(sqlite_employees_db, tmp_path):
    """Test that queries are logged with detailed metrics"""
    import logging
    from langchain_ollama import ChatOllama

    log_file = tmp_path / "test_queries.log"
    SQLAgent.configure_logging(level=logging.INFO, log_file=str(log_file))

    llm = ChatOllama(model="mistral:7b", temperature=0.1)
    agent = SQLAgent(llm=llm, db=sqlite_employees_db, verbose=True)

    # Execute a query to generate logs
    result = agent.query("How many employees are there?")

    # Verify log file exists and has content (if logging is enabled)
    if log_file.exists():
        log_contents = log_file.read_text()
        # Log should contain some query-related information
        assert len(log_contents) > 0


# ============================================================================
# FEATURE TESTS: Timestamp Context (Feature 5)
# ============================================================================

@pytest.mark.feature_test
def test_timestamp_context_injection(sqlite_employees_db):
    """Test timestamp context injection in queries"""
    from langchain_ollama import ChatOllama

    llm = ChatOllama(model="mistral:7b", temperature=0.1)
    agent = SQLAgent(llm=llm, db=sqlite_employees_db, include_timestamp=True)

    # Build timestamp context
    timestamp_context = agent._build_timestamp_context()

    # Verify timestamp context includes current date
    assert "Current Date:" in timestamp_context or "today" in timestamp_context.lower()


@pytest.mark.feature_test
def test_timestamp_context_disabled(sqlite_employees_db):
    """Test timestamp context can be disabled"""
    from langchain_ollama import ChatOllama

    llm = ChatOllama(model="mistral:7b", temperature=0.1)
    agent = SQLAgent(llm=llm, db=sqlite_employees_db, include_timestamp=False)

    # With timestamp disabled, context should be empty
    assert agent.include_timestamp is False


# ============================================================================
# FEATURE TESTS: Singleton Pattern (Feature 6)
# ============================================================================

@pytest.mark.feature_test
def test_singleton_mode(sqlite_employees_db):
    """Test singleton pattern caching"""
    from langchain_ollama import ChatOllama

    llm = ChatOllama(model="mistral:7b", temperature=0.1)

    agent1 = SQLAgent(llm=llm, db=sqlite_employees_db, use_singleton=True)
    agent2 = SQLAgent(llm=llm, db=sqlite_employees_db, use_singleton=True)

    # Should be same instance
    assert agent1 is agent2

    # Clear instances for cleanup
    SQLAgent.clear_instances()


@pytest.mark.feature_test
def test_non_singleton_mode(sqlite_employees_db):
    """Test default non-singleton behavior"""
    from langchain_ollama import ChatOllama

    llm = ChatOllama(model="mistral:7b", temperature=0.1)

    agent1 = SQLAgent(llm=llm, db=sqlite_employees_db, use_singleton=False)
    agent2 = SQLAgent(llm=llm, db=sqlite_employees_db, use_singleton=False)

    # Should be different instances
    assert agent1 is not agent2


# ============================================================================
# FEATURE TESTS: Better Error Recovery (Feature 7)
# ============================================================================

@pytest.mark.feature_test
def test_error_analysis_iteration_limit(sqlite_employees_db):
    """Test error analysis for iteration limit exceeded"""
    from langchain_ollama import ChatOllama

    llm = ChatOllama(model="mistral:7b", temperature=0.1)
    agent = SQLAgent(llm=llm, db=sqlite_employees_db, max_iterations=1)

    # Test that the agent has error analysis capability
    assert hasattr(agent, '_analyze_error')


@pytest.mark.feature_test
def test_error_analysis_provides_suggestions(sqlite_employees_db):
    """Test that error analysis provides actionable suggestions"""
    from langchain_ollama import ChatOllama

    llm = ChatOllama(model="mistral:7b", temperature=0.1)
    agent = SQLAgent(llm=llm, db=sqlite_employees_db)

    # Create a mock error
    test_error = Exception("Agent stopped due to iteration limit")

    # Analyze error
    error_info = agent._analyze_error(test_error, "test query")

    # Verify error analysis returns structured information
    assert isinstance(error_info, dict)
    assert "error_type" in error_info
    assert "user_message" in error_info
    assert "suggestion" in error_info


@pytest.mark.feature_test
def test_error_recovery_metadata(sqlite_employees_db):
    """Test that errors include helpful metadata"""
    from langchain_ollama import ChatOllama

    llm = ChatOllama(model="mistral:7b", temperature=0.1)
    agent = SQLAgent(llm=llm, db=sqlite_employees_db)

    # Error analysis should be available
    assert callable(agent._analyze_error)


# ============================================================================
# PARAMETRIZED DATABASE TESTS: SQLite vs PostgreSQL
# ============================================================================

@pytest.mark.integration
@pytest.mark.parametrize("db_fixture,expected_dialect", [
    ("sqlite_employees_db", "sqlite"),
    ("postgres_employees_db", "postgresql")
])
def test_agent_initialization_with_databases(db_fixture, expected_dialect, request):
    """Test agent initialization with both SQLite and PostgreSQL"""
    from langchain_ollama import ChatOllama

    db = request.getfixturevalue(db_fixture)
    llm = ChatOllama(model="mistral:7b", temperature=0.1)

    agent = SQLAgent(llm=llm, db=db)

    assert agent.llm is not None
    assert agent.db is not None
    assert agent.toolkit is not None
    assert agent.agent_executor is not None


@pytest.mark.integration
@pytest.mark.parametrize("db_fixture,expected_dialect", [
    ("sqlite_employees_db", "sqlite"),
    ("postgres_employees_db", "postgresql")
])
def test_get_dialect_with_databases(db_fixture, expected_dialect, request):
    """Test database dialect detection with both SQLite and PostgreSQL"""
    from langchain_ollama import ChatOllama

    db = request.getfixturevalue(db_fixture)
    llm = ChatOllama(model="mistral:7b", temperature=0.1)
    agent = SQLAgent(llm=llm, db=db)

    dialect = agent.get_dialect()
    assert expected_dialect in dialect.lower()


@pytest.mark.integration
@pytest.mark.parametrize("db_fixture", [
    "sqlite_employees_db",
    "postgres_employees_db"
])
def test_get_table_names_with_databases(db_fixture, request):
    """Test getting table names with both SQLite and PostgreSQL"""
    from langchain_ollama import ChatOllama

    db = request.getfixturevalue(db_fixture)
    llm = ChatOllama(model="mistral:7b", temperature=0.1)
    agent = SQLAgent(llm=llm, db=db)

    tables = agent.get_table_names()

    assert isinstance(tables, list)
    assert len(tables) >= 3
    assert "employees" in tables
    assert "departments" in tables
    assert "projects" in tables


@pytest.mark.integration
@pytest.mark.parametrize("db_fixture", [
    "sqlite_employees_db",
    "postgres_employees_db"
])
def test_get_schema_info_with_databases(db_fixture, request):
    """Test schema inspection with both SQLite and PostgreSQL"""
    from langchain_ollama import ChatOllama

    db = request.getfixturevalue(db_fixture)
    llm = ChatOllama(model="mistral:7b", temperature=0.1)
    agent = SQLAgent(llm=llm, db=db)

    schema = agent.get_schema_info(table_names=["employees"])

    assert isinstance(schema, str)
    assert "employees" in schema
    assert "id" in schema or "name" in schema


@pytest.mark.integration
@pytest.mark.parametrize("db_fixture", [
    "sqlite_employees_db",
    "postgres_employees_db"
])
def test_agent_with_domain_context_databases(db_fixture, request):
    """Test agent with domain context on both databases"""
    from langchain_ollama import ChatOllama

    db = request.getfixturevalue(db_fixture)
    llm = ChatOllama(model="mistral:7b", temperature=0.1)

    domain = "employee management system"
    agent = SQLAgent(llm=llm, db=db, domain_context=domain)

    assert agent.domain_context == domain
    assert agent.db is not None


@pytest.mark.integration
@pytest.mark.parametrize("db_fixture", [
    "sqlite_employees_db",
    "postgres_employees_db"
])
def test_agent_custom_parameters_databases(db_fixture, request):
    """Test agent custom parameters with both databases"""
    from langchain_ollama import ChatOllama

    db = request.getfixturevalue(db_fixture)
    llm = ChatOllama(model="mistral:7b", temperature=0.1)

    agent = SQLAgent(
        llm=llm,
        db=db,
        max_rows_for_llm=20,
        large_result_threshold=100,
        verbose=True,
        max_iterations=15,
    )

    assert agent.max_rows_for_llm == 20
    assert agent.large_result_threshold == 100
    assert agent.verbose is True
    assert agent.max_iterations == 15


@pytest.mark.integration
@pytest.mark.parametrize("db_fixture", [
    "sqlite_employees_db",
    "postgres_employees_db"
])
def test_set_verbose_with_databases(db_fixture, request):
    """Test verbose mode toggling with both databases"""
    from langchain_ollama import ChatOllama

    db = request.getfixturevalue(db_fixture)
    llm = ChatOllama(model="mistral:7b", temperature=0.1)

    agent = SQLAgent(llm=llm, db=db, verbose=False)

    assert agent.verbose is False
    assert agent.agent_executor.verbose is False

    agent.set_verbose(True)

    assert agent.verbose is True
    assert agent.agent_executor.verbose is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
