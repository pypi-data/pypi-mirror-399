"""
SQL Agent - A flexible, LLM-agnostic text-to-SQL agent with advanced features
"""
import json
import re
import logging
import threading
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List, Union, Tuple
from langchain_core.language_models import BaseChatModel
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_core.prompts import PromptTemplate

from .database import JSONSerializableSQLDatabase
from .tools import JSONSQLDatabaseToolkit
from .prompts import get_react_prompt_template, get_agent_prefix, get_agent_suffix

# Configure logging
logger = logging.getLogger(__name__)
sql_logger = logging.getLogger('sql_queries')


class SQLAgent:
    """
    A flexible SQL agent with advanced features for production use.

    Features:
    - LLM Provider Agnostic: Works with any LangChain BaseChatModel
    - Database Agnostic: Works with any SQL database (PostgreSQL, MySQL, SQLite, etc.)
    - Domain Agnostic: Optional domain context for specialized behavior
    - Schema Pre-loading: Cache table schemas for 70-80% performance improvement
    - Async Support: Non-blocking query execution with async/await
    - Enhanced Conversation Context: Track SQL queries across conversation
    - Enhanced Logging: Comprehensive SQL query logging with metrics
    - Timestamp Context: Temporal query support for "last week", "past 30 days"
    - Singleton Pattern: Optional resource management mode
    - Error Recovery: User-friendly error messages with actionable suggestions
    - Intelligent Result Handling: Automatically truncates large results for LLM processing
    - JSON Serializable: Returns properly formatted JSON results

    Example:
        >>> from text_to_sql import SQLAgent
        >>> from text_to_sql.database import JSONSerializableSQLDatabase
        >>> from langchain_aws import ChatBedrock
        >>>
        >>> llm = ChatBedrock(model_id="anthropic.claude-3-sonnet-20240229-v1:0")
        >>> db = JSONSerializableSQLDatabase.from_uri("postgresql://user:pass@host/db")
        >>>
        >>> # Basic usage
        >>> agent = SQLAgent(llm=llm, db=db)
        >>> result = agent.query("What tables are available?")
        >>>
        >>> # With schema pre-loading for better performance
        >>> agent = SQLAgent(llm=llm, db=db, important_tables=["users", "orders"])
        >>>
        >>> # With async support
        >>> result = await agent.aquery("How many users?")
    """

    # Class-level instance cache for singleton pattern
    _instances: Dict[Tuple, 'SQLAgent'] = {}
    _instance_lock = threading.Lock()

    def __new__(
        cls,
        llm: BaseChatModel,
        db: JSONSerializableSQLDatabase,
        use_singleton: bool = False,
        **kwargs
    ):
        """
        Create or return existing instance based on singleton configuration.

        Args:
            llm: Language model instance
            db: Database instance
            use_singleton: If True, returns cached instance for same database
            **kwargs: Additional initialization parameters

        Returns:
            SQLAgent instance (new or cached)
        """
        if not use_singleton:
            # Normal instantiation - create new instance every time
            return super().__new__(cls)

        # Singleton mode - cache instances by database URI and domain
        with cls._instance_lock:
            # Create cache key from database URI and domain context
            db_uri = str(db._engine.url)
            domain_context = kwargs.get('domain_context', None)
            cache_key = (db_uri, domain_context)

            # Return existing instance if available
            if cache_key in cls._instances:
                logger.info(f"Returning cached SQLAgent instance for {db_uri}")
                return cls._instances[cache_key]

            # Create new instance
            instance = super().__new__(cls)
            cls._instances[cache_key] = instance
            logger.info(f"Created new SQLAgent instance for {db_uri}")
            return instance

    def __init__(
        self,
        llm: BaseChatModel,
        db: JSONSerializableSQLDatabase,
        domain_context: Optional[str] = None,
        important_tables: Optional[Union[List[str], str]] = None,
        enable_schema_caching: bool = True,
        max_rows_for_llm: int = 10,
        large_result_threshold: int = 50,
        verbose: bool = False,
        max_iterations: int = 10,
        use_singleton: bool = False,
        include_timestamp: bool = True,
    ):
        """
        Initialize the SQL Agent with advanced features.

        Args:
            llm: Any LangChain BaseChatModel (ChatBedrock, ChatOpenAI, ChatAnthropic, etc.)
            db: JSONSerializableSQLDatabase instance (required for proper JSON serialization)
            domain_context: Optional domain description for specialized behavior
                Examples: "medical records", "e-commerce data", "financial transactions"
            important_tables: Tables to pre-load for performance. Options:
                - List[str]: Explicit table names like ["users", "orders"]
                - "auto": Auto-discover based on domain context and heuristics
                - "all": Cache all tables (recommended for small schemas <10 tables)
                - None: No schema caching (default)
            enable_schema_caching: Enable/disable schema caching (default: True)
            max_rows_for_llm: Maximum rows to send to LLM for answer generation (default: 10)
            large_result_threshold: Threshold to consider results "large" (default: 50)
            verbose: Enable verbose output (default: False)
            max_iterations: Maximum agent iterations (default: 10)
            use_singleton: Use singleton pattern for resource management (default: False)
            include_timestamp: Include timestamp context for temporal queries (default: True)

        Raises:
            TypeError: If db is not an instance of JSONSerializableSQLDatabase
        """
        # Prevent re-initialization in singleton mode
        if hasattr(self, '_initialized') and self._initialized:
            return

        # Validate database type
        if not isinstance(db, JSONSerializableSQLDatabase):
            raise TypeError(
                f"db must be an instance of JSONSerializableSQLDatabase, got {type(db).__name__}. "
                "Please use JSONSerializableSQLDatabase.from_uri() to create the database instance."
            )

        self.llm = llm
        self.db = db
        self.domain_context = domain_context
        self.important_tables = important_tables
        self.enable_schema_caching = enable_schema_caching
        self.max_rows_for_llm = max_rows_for_llm
        self.large_result_threshold = large_result_threshold
        self.verbose = verbose
        self.max_iterations = max_iterations
        self.use_singleton = use_singleton
        self.include_timestamp = include_timestamp

        # Schema caching attributes
        self.cached_schemas: Dict[str, str] = {}
        self.cached_table_list: str = ""
        self._schema_cache_lock = threading.Lock()

        # Setup toolkit
        self.toolkit = self._create_toolkit()

        # Pre-load schemas if enabled and tables specified
        if self.enable_schema_caching and self.important_tables:
            self._preload_schemas()

        # Create agent executor
        self.agent_executor = self._create_agent()

        logger.info(
            f"SQLAgent initialized with {type(llm).__name__} and "
            f"{self.db._engine.dialect.name} database"
        )
        if domain_context:
            logger.info(f"Domain context: {domain_context}")
        if self.cached_schemas:
            logger.info(f"Pre-loaded {len(self.cached_schemas)} table schemas")

        # Mark as initialized
        self._initialized = True

    # ==================== SCHEMA PRE-LOADING (Feature 1) ====================

    def _preload_schemas(self) -> None:
        """
        Pre-load database schemas for important tables.
        This significantly improves performance by embedding schemas in the prompt.
        """
        with self._schema_cache_lock:
            try:
                # Step 1: Get table list
                all_tables = self.get_table_names()
                self.cached_table_list = ", ".join(all_tables)

                # Step 2: Determine which tables to cache
                tables_to_cache = self._determine_important_tables(all_tables)

                # Step 3: Cache schemas for important tables
                if tables_to_cache:
                    schema_info = self.get_schema_info(table_names=tables_to_cache)
                    self.cached_schemas = self._parse_schema_by_table(
                        schema_info, tables_to_cache
                    )

                    logger.info(
                        f"Pre-loaded schemas for {len(tables_to_cache)} tables: "
                        f"{', '.join(tables_to_cache)}"
                    )
                else:
                    logger.info("Schema pre-loading disabled or no tables specified")

            except Exception as e:
                logger.warning(
                    f"Failed to pre-load schemas: {e}. "
                    "Will fall back to dynamic schema lookup."
                )
                self.cached_schemas = {}

    def _determine_important_tables(self, all_tables: List[str]) -> List[str]:
        """
        Determine which tables to cache based on configuration.

        Args:
            all_tables: List of all available table names

        Returns:
            List of table names to cache
        """
        if not self.important_tables:
            return []

        # Strategy 1: Explicit list
        if isinstance(self.important_tables, list):
            # Validate tables exist
            valid_tables = [t for t in self.important_tables if t in all_tables]
            if len(valid_tables) != len(self.important_tables):
                missing = set(self.important_tables) - set(valid_tables)
                logger.warning(f"Tables not found in database: {missing}")
            return valid_tables

        # Strategy 2: Auto-discovery
        if self.important_tables == "auto":
            return self._auto_discover_important_tables(all_tables)

        # Strategy 3: All tables (small schemas)
        if self.important_tables == "all":
            if len(all_tables) <= 10:
                return all_tables
            else:
                logger.warning(
                    f"Database has {len(all_tables)} tables. "
                    "Consider specifying important_tables explicitly for better performance."
                )
                return all_tables[:10]  # Limit to first 10

        return []

    def _auto_discover_important_tables(self, all_tables: List[str]) -> List[str]:
        """
        Auto-discover important tables based on naming patterns and domain context.

        Args:
            all_tables: List of all available table names

        Returns:
            List of discovered important table names
        """
        important = []

        # Heuristic 1: Domain-specific keywords
        if self.domain_context:
            domain_keywords = self._extract_domain_keywords(self.domain_context)
            for table in all_tables:
                if any(keyword.lower() in table.lower() for keyword in domain_keywords):
                    important.append(table)

        # Heuristic 2: Common important table patterns
        common_patterns = [
            "user", "customer", "patient", "client",
            "order", "transaction", "purchase",
            "product", "item", "service",
            "account", "profile", "contact"
        ]

        for table in all_tables:
            table_lower = table.lower()
            if any(pattern in table_lower for pattern in common_patterns):
                if table not in important:
                    important.append(table)

        # Heuristic 3: Limit to reasonable size (5-10 tables)
        if len(important) > 10:
            important = important[:10]
        elif len(important) == 0 and len(all_tables) <= 5:
            # If no matches and small schema, cache everything
            important = all_tables

        return important

    def _extract_domain_keywords(self, domain_context: str) -> List[str]:
        """Extract key nouns from domain context for table matching"""
        # Simple keyword extraction
        words = domain_context.lower().split()
        # Filter out common words
        stopwords = {
            "the", "a", "an", "and", "or", "but", "including",
            "with", "for", "data", "records"
        }
        keywords = [
            w.strip(",.;:")
            for w in words
            if w not in stopwords and len(w) > 3
        ]
        return keywords

    def _parse_schema_by_table(
        self,
        schema_info: str,
        table_names: List[str]
    ) -> Dict[str, str]:
        """
        Parse combined schema info into per-table schemas.

        Args:
            schema_info: Combined schema information string
            table_names: List of table names to parse

        Returns:
            Dict mapping table_name -> schema_string
        """
        schemas = {}
        current_table = None
        current_schema = []

        for line in schema_info.split("\n"):
            # Detect table header
            matched = False
            for table_name in table_names:
                if f"CREATE TABLE {table_name}" in line or f"Table: {table_name}" in line:
                    # Save previous table's schema
                    if current_table:
                        schemas[current_table] = "\n".join(current_schema)
                    # Start new table
                    current_table = table_name
                    current_schema = [line]
                    matched = True
                    break

            if not matched and current_table:
                # Continuation of current table schema
                current_schema.append(line)

        # Save last table
        if current_table:
            schemas[current_table] = "\n".join(current_schema)

        return schemas

    def _build_embedded_schemas(self) -> str:
        """
        Build a formatted string of pre-loaded schemas for prompt injection.

        Returns:
            Formatted schema string ready for prompt inclusion
        """
        with self._schema_cache_lock:
            if not self.cached_schemas:
                return ""

            schema_parts = ["## PRE-LOADED TABLE SCHEMAS:\n"]
            schema_parts.append(
                "The following table schemas are provided for your immediate use. "
                "You can query these tables directly without checking their schema first.\n"
            )

            for table_name, schema in self.cached_schemas.items():
                schema_parts.append(f"\n### {table_name}:")
                schema_parts.append(schema)

            schema_parts.append(
                "\n**OPTIMIZATION RULE**: For queries involving these pre-loaded tables, "
                "skip the schema lookup step and write the query directly."
            )

            return "\n".join(schema_parts)

    def refresh_schemas(self) -> None:
        """
        Refresh cached schemas (useful when database schema changes).
        Thread-safe operation.
        """
        logger.info("Refreshing cached schemas...")
        self._preload_schemas()
        logger.info("Schema cache refreshed successfully")

    # ==================== TIMESTAMP CONTEXT (Feature 5) ====================

    def _build_timestamp_context(self) -> str:
        """
        Build timestamp context for temporal queries.

        Returns:
            Formatted timestamp context string
        """
        now = datetime.now(timezone.utc)

        context = f"""## CURRENT TIMESTAMP INFORMATION:
- Current UTC DateTime: {now.isoformat()}
- Current Date: {now.strftime('%Y-%m-%d')}
- Current Time: {now.strftime('%H:%M:%S')}
- Day of Week: {now.strftime('%A')}
- Month: {now.strftime('%B')}
- Year: {now.year}

Use this timestamp information to interpret relative date/time queries like:
- "last week" = dates from {(now - timedelta(days=7)).strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')}
- "past 30 days" = dates from {(now - timedelta(days=30)).strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')}
- "this month" = dates from {now.strftime('%Y-%m-01')} to {now.strftime('%Y-%m-%d')}
- "today" = date {now.strftime('%Y-%m-%d')}
"""
        return context

    # ==================== ENHANCED CONVERSATION CONTEXT (Feature 3) ====================

    def _build_conversation_context(
        self,
        conversation_history: List[Dict],
        max_messages: int = 5
    ) -> str:
        """
        Build enhanced context string from conversation history.

        Args:
            conversation_history: List of message dicts with structure:
                {
                    "role": "user" | "assistant",
                    "content": "message text",
                    "metadata": {  # Optional
                        "sql_query": "SELECT ...",
                        "result_count": 42,
                        "tables_accessed": ["users", "orders"]
                    }
                }
            max_messages: Maximum number of recent messages to include

        Returns:
            Formatted context string for prompt injection
        """
        if not conversation_history:
            return ""

        context_parts = []

        # Process last N messages for context
        recent_messages = conversation_history[-max_messages:]

        # Track SQL queries for context
        sql_context = []

        for i, msg in enumerate(recent_messages):
            role = msg.get('role', 'unknown').capitalize()
            content = msg.get('content', '')
            metadata = msg.get('metadata', {})

            # Add message content
            context_parts.append(f"{role}: {content}")

            # Extract SQL query from metadata if available
            if metadata and 'sql_query' in metadata:
                sql_query = metadata['sql_query']
                if sql_query:
                    sql_context.append(f"  SQL: {sql_query}")

                    # Add result count if available
                    if 'result_count' in metadata:
                        sql_context.append(f"  Returned: {metadata['result_count']} rows")

        # Build final context
        result = []

        if context_parts:
            result.append("## CONVERSATION HISTORY:")
            result.extend(context_parts)

        if sql_context:
            result.append("\n## PREVIOUS SQL QUERIES:")
            result.extend(sql_context)
            result.append("\nUse these previous queries as context for follow-up questions.")

        return "\n".join(result) if result else ""

    def _extract_tables_from_query(self, sql_query: str) -> List[str]:
        """Extract table names from SQL query using regex"""
        if not sql_query:
            return []

        # Simple regex to extract table names after FROM and JOIN
        pattern = r'\b(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)\b'
        matches = re.findall(pattern, sql_query, re.IGNORECASE)
        return list(set(matches))  # Remove duplicates

    # ==================== ERROR RECOVERY (Feature 7) ====================

    def _analyze_error(self, exception: Exception, question: str) -> Dict[str, str]:
        """
        Analyze exception and provide user-friendly error information.

        Args:
            exception: The caught exception
            question: The original user question

        Returns:
            Dict with error_type, user_message, and suggestion
        """
        error_str = str(exception).lower()
        error_type = type(exception).__name__

        # ERROR PATTERN 1: Iteration Limit
        if "agent stopped due to iteration limit" in error_str or "max iterations" in error_str:
            return {
                "error_type": "iteration_limit",
                "user_message": (
                    "The query took too many steps to complete. This usually means the "
                    "question is very complex or the agent encountered difficulties. "
                    "Try breaking down your question into simpler parts or rephrasing it."
                ),
                "suggestion": (
                    "1. Simplify your question\n"
                    "2. Ask in multiple steps\n"
                    "3. Be more specific about what you want\n"
                    f"4. Increase max_iterations if this query is inherently complex (currently: {self.max_iterations})"
                )
            }

        # ERROR PATTERN 2: Timeout
        if "timeout" in error_str or "timed out" in error_str:
            return {
                "error_type": "timeout",
                "user_message": (
                    "The query timed out. This might be due to a very large dataset, "
                    "complex query, or slow database connection."
                ),
                "suggestion": (
                    "1. Try limiting the date range or scope of your question\n"
                    "2. Check database performance\n"
                    "3. Add indexes to relevant tables\n"
                    "4. Use more specific filters in your question"
                )
            }

        # ERROR PATTERN 3: Table Not Found
        if "table" in error_str and ("not found" in error_str or "does not exist" in error_str):
            # Try to extract table name
            table_match = re.search(r"table['\"\s]+([a-zA-Z_][a-zA-Z0-9_]*)", error_str, re.IGNORECASE)
            table_name = table_match.group(1) if table_match else "unknown"

            available_tables = self.get_table_names()

            return {
                "error_type": "table_not_found",
                "user_message": (
                    f"The table '{table_name}' does not exist in the database. "
                    f"Available tables are: {', '.join(available_tables)}"
                ),
                "suggestion": (
                    f"1. Check the spelling of table names\n"
                    f"2. Available tables: {', '.join(available_tables)}\n"
                    f"3. Rephrase your question using the correct table names"
                )
            }

        # ERROR PATTERN 4: Column Not Found
        if "column" in error_str and ("not found" in error_str or "does not exist" in error_str):
            return {
                "error_type": "column_not_found",
                "user_message": (
                    "A column referenced in the query does not exist. "
                    "The agent may have assumed a column name incorrectly."
                ),
                "suggestion": (
                    "1. Use get_schema_info() to see available columns\n"
                    "2. Be more specific about what data you're looking for\n"
                    "3. Rephrase your question with different terminology"
                )
            }

        # ERROR PATTERN 5: Syntax Error
        if "syntax error" in error_str or "syntaxerror" in error_str:
            return {
                "error_type": "sql_syntax_error",
                "user_message": (
                    "The generated SQL query had a syntax error. "
                    "This might be due to database-specific SQL features or complex query logic."
                ),
                "suggestion": (
                    "1. Try rephrasing your question more simply\n"
                    "2. Break complex questions into multiple steps\n"
                    "3. Check if you're asking for database-specific features"
                )
            }

        # ERROR PATTERN 6: Permission Denied
        if "permission denied" in error_str or "access denied" in error_str:
            return {
                "error_type": "permission_denied",
                "user_message": (
                    "Database permission denied. The database user does not have "
                    "sufficient privileges to execute this query."
                ),
                "suggestion": (
                    "1. Check database user permissions\n"
                    "2. Ensure read access to required tables\n"
                    "3. Contact your database administrator"
                )
            }

        # ERROR PATTERN 7: Connection Error
        if "connection" in error_str or "connect" in error_str:
            return {
                "error_type": "connection_error",
                "user_message": (
                    "Database connection error. Unable to connect to the database."
                ),
                "suggestion": (
                    "1. Check database connection string\n"
                    "2. Verify database server is running\n"
                    "3. Check network connectivity\n"
                    "4. Verify credentials are correct"
                )
            }

        # ERROR PATTERN 8: LLM/API Error
        if "api" in error_str or "rate limit" in error_str or "quota" in error_str:
            return {
                "error_type": "llm_api_error",
                "user_message": (
                    "LLM API error. The language model API encountered an issue "
                    "(rate limit, quota exceeded, or service unavailable)."
                ),
                "suggestion": (
                    "1. Check LLM API status\n"
                    "2. Verify API key and permissions\n"
                    "3. Check rate limits and quotas\n"
                    "4. Try again in a few moments"
                )
            }

        # DEFAULT: Generic Error
        return {
            "error_type": "unknown_error",
            "user_message": (
                f"An unexpected error occurred: {str(exception)}"
            ),
            "suggestion": (
                "1. Check the error details above\n"
                "2. Try rephrasing your question\n"
                "3. Enable verbose mode for more details: agent.set_verbose(True)\n"
                "4. Contact support if the issue persists"
            )
        }

    # ==================== ENHANCED LOGGING (Feature 4) ====================

    @staticmethod
    def configure_logging(
        level: int = logging.INFO,
        format_string: Optional[str] = None,
        log_file: Optional[str] = None
    ):
        """
        Configure SQL query logging.

        Args:
            level: Logging level (logging.DEBUG, INFO, WARNING, ERROR)
            format_string: Custom format string for log messages
            log_file: Optional file path for log output

        Example:
            >>> SQLAgent.configure_logging(
            ...     level=logging.DEBUG,
            ...     log_file="sql_queries.log"
            ... )
        """
        sql_logger.setLevel(level)

        # Clear existing handlers
        sql_logger.handlers = []

        # Default format
        if not format_string:
            format_string = '%(asctime)s - SQL_AGENT - %(levelname)s - %(message)s'

        formatter = logging.Formatter(format_string)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        sql_logger.addHandler(console_handler)

        # File handler if specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            sql_logger.addHandler(file_handler)

    # ==================== TOOLKIT & AGENT CREATION ====================

    def _create_toolkit(self) -> JSONSQLDatabaseToolkit:
        """Create the SQL toolkit with custom tools"""
        return JSONSQLDatabaseToolkit(
            db=self.db,
            llm=self.llm,
            max_rows_for_llm=self.max_rows_for_llm,
            large_result_threshold=self.large_result_threshold,
        )

    def _build_prompt(self) -> PromptTemplate:
        """Build the ReAct prompt with optional domain context and cached schemas"""
        # Get embedded schemas if available
        embedded_schemas = self._build_embedded_schemas()

        # Get the complete prompt template from prompts module
        template = get_react_prompt_template(
            domain_context=self.domain_context,
            large_result_threshold=self.large_result_threshold,
            embedded_schemas=embedded_schemas
        )

        prompt = PromptTemplate(
            input_variables=["input", "tools", "tool_names", "agent_scratchpad"],
            template=template,
        )

        return prompt

    def _create_agent(self):
        """Create the SQL agent executor"""
        # Get embedded schemas if available
        embedded_schemas = self._build_embedded_schemas()

        # Get prefix and suffix from prompts module
        # CRITICAL: Pass embedded_schemas to prefix so agent knows about cached schemas
        prefix = get_agent_prefix(
            domain_context=self.domain_context,
            embedded_schemas=embedded_schemas
        )
        suffix = get_agent_suffix()

        # Create SQL agent using langchain_community
        agent_executor = create_sql_agent(
            llm=self.llm,
            toolkit=self.toolkit,
            verbose=self.verbose,
            max_iterations=self.max_iterations,
            prefix=prefix,
            suffix=suffix,
            agent_executor_kwargs={
                "handle_parsing_errors": True,
                "return_intermediate_steps": True,
            }
        )

        return agent_executor

    # ==================== QUERY METHODS (Features 2, 3, 4, 5, 7) ====================

    def query(
        self,
        question: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Execute a natural language query against the database (synchronous).

        This method blocks until the query completes. For async applications,
        use `aquery()` instead.

        Args:
            question: Natural language question to ask
            conversation_history: Optional list of previous messages for context

        Returns:
            Dictionary containing:
                - answer: Natural language answer
                - sql_query: Generated SQL query (if any)
                - results: Query results as JSON string
                - intermediate_steps: List of agent actions taken
                - metadata: Query metadata (sql_query, result_count, tables_accessed, timestamp)
        """
        query_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(question)}"

        try:
            # === PHASE 1: QUERY INITIATION (Enhanced Logging) ===
            sql_logger.info("="*80)
            sql_logger.info(f"QUERY_ID: {query_id}")
            sql_logger.info(f"USER_QUERY: {question}")
            sql_logger.info(f"TIMESTAMP: {datetime.now().isoformat()}")
            sql_logger.info(f"DATABASE: {self.get_dialect()}")
            if self.domain_context:
                sql_logger.info(f"DOMAIN: {self.domain_context}")
            if conversation_history:
                sql_logger.info(f"CONVERSATION_CONTEXT: {len(conversation_history)} messages")

            # Build enhanced query with timestamp context
            enhanced_question = question

            # Add timestamp context for temporal queries
            if self.include_timestamp:
                timestamp_context = self._build_timestamp_context()
                enhanced_question = f"{timestamp_context}\n\n{question}"

            # Add conversation context if provided
            if conversation_history:
                context = self._build_conversation_context(conversation_history)
                if context:
                    enhanced_question = f"{enhanced_question}\n\n{context}"
                    sql_logger.debug(f"ENHANCED_QUERY_LENGTH: {len(enhanced_question)} chars")

            # === PHASE 2: AGENT EXECUTION ===
            start_time = datetime.now()
            sql_logger.info("AGENT_STATUS: Executing...")

            response = self.agent_executor.invoke({"input": enhanced_question})

            execution_time = (datetime.now() - start_time).total_seconds()
            sql_logger.info(f"EXECUTION_TIME: {execution_time:.2f}s")

            # === PHASE 3: RESULT EXTRACTION ===
            sql_query = None
            sql_results = None
            all_tables = set()  # Track all tables accessed across all queries
            num_iterations = len(response.get("intermediate_steps", []))

            sql_logger.info(f"AGENT_ITERATIONS: {num_iterations}")

            # Iterate through ALL intermediate steps to capture the LAST query and ALL tables
            for action, observation in response.get("intermediate_steps", []):
                if hasattr(action, 'tool') and action.tool == "sql_db_query":
                    current_query = (
                        action.tool_input.get("query")
                        if isinstance(action.tool_input, dict)
                        else action.tool_input
                    )
                    # Update to track the LAST query execution
                    sql_query = current_query
                    sql_results = observation

                    # Accumulate tables from this query
                    tables_in_query = self._extract_tables_from_query(current_query)
                    all_tables.update(tables_in_query)

            # Log the final SQL query (the last one executed)
            if sql_query:
                sql_logger.info("GENERATED_SQL:")
                for line in sql_query.split('\n'):
                    sql_logger.info(f"  {line}")

            # Get full results if available
            full_results = self.toolkit.get_full_results()

            # Use full results if available, otherwise use observation
            if full_results and full_results != "[]":
                final_results = full_results
            elif sql_results:
                final_results = sql_results
            else:
                final_results = "[]"

            # === PHASE 4: RESULT METRICS ===
            result_count = 0
            try:
                parsed = json.loads(final_results)
                if isinstance(parsed, list):
                    result_count = len(parsed)
                elif isinstance(parsed, dict) and "total_rows" in parsed:
                    result_count = parsed["total_rows"]
            except:
                pass

            # Use accumulated tables from all queries
            tables_accessed = list(all_tables)

            sql_logger.info(f"RESULT_COUNT: {result_count} rows")
            sql_logger.info("SQL_EXECUTION_STATUS: SUCCESS")
            sql_logger.info("QUERY_STATUS: COMPLETED")
            sql_logger.info("="*80)

            return {
                "answer": response.get("output", "Query completed."),
                "sql_query": sql_query,
                "results": final_results,
                "intermediate_steps": response.get("intermediate_steps", []),
                "metadata": {
                    "sql_query": sql_query,
                    "result_count": result_count,
                    "tables_accessed": tables_accessed,
                    "timestamp": datetime.now().isoformat(),
                    "execution_time": execution_time,
                }
            }

        except Exception as e:
            # === ERROR LOGGING & RECOVERY ===
            error_info = self._analyze_error(e, question)

            sql_logger.error("="*80)
            sql_logger.error(f"QUERY_ID: {query_id}")
            sql_logger.error(f"SQL_EXECUTION_STATUS: FAILED")
            sql_logger.error(f"ERROR_TYPE: {error_info['error_type']}")
            sql_logger.error(f"ERROR_MESSAGE: {str(e)}")
            sql_logger.error("="*80)

            logger.error(f"Error executing query: {str(e)}", exc_info=True)

            return {
                "answer": error_info["user_message"],
                "sql_query": None,
                "results": "[]",
                "error": str(e),
                "error_type": error_info["error_type"],
                "error_suggestion": error_info["suggestion"],
            }
        finally:
            # Always reset full results to prevent memory leaks
            self.toolkit.reset_full_results()

    # ==================== ASYNC SUPPORT (Feature 2) ====================

    async def aquery(
        self,
        question: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Execute a natural language query against the database (asynchronous).

        This method is non-blocking and suitable for async applications.
        For synchronous code, use `query()` instead.

        Args:
            question: Natural language question to ask
            conversation_history: Optional list of previous messages for context

        Returns:
            Dictionary containing:
                - answer: Natural language answer
                - sql_query: Generated SQL query (if any)
                - results: Query results as JSON string
                - intermediate_steps: List of agent actions taken
                - metadata: Query metadata

        Example:
            >>> result = await agent.aquery("How many users?")
            >>> print(result["answer"])
        """
        query_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(question)}"

        try:
            # === PHASE 1: QUERY INITIATION ===
            sql_logger.info("="*80)
            sql_logger.info(f"ASYNC_QUERY_ID: {query_id}")
            sql_logger.info(f"USER_QUERY: {question}")
            sql_logger.info(f"TIMESTAMP: {datetime.now().isoformat()}")
            sql_logger.info(f"DATABASE: {self.get_dialect()}")
            if self.domain_context:
                sql_logger.info(f"DOMAIN: {self.domain_context}")
            if conversation_history:
                sql_logger.info(f"CONVERSATION_CONTEXT: {len(conversation_history)} messages")

            # Build enhanced query
            enhanced_question = question

            # Add timestamp context
            if self.include_timestamp:
                timestamp_context = self._build_timestamp_context()
                enhanced_question = f"{timestamp_context}\n\n{question}"

            # Add conversation context
            if conversation_history:
                context = self._build_conversation_context(conversation_history)
                if context:
                    enhanced_question = f"{enhanced_question}\n\n{context}"

            # === PHASE 2: ASYNC AGENT EXECUTION ===
            start_time = datetime.now()
            sql_logger.info("ASYNC_AGENT_STATUS: Executing...")

            response = await self.agent_executor.ainvoke({"input": enhanced_question})

            execution_time = (datetime.now() - start_time).total_seconds()
            sql_logger.info(f"ASYNC_EXECUTION_TIME: {execution_time:.2f}s")

            # === PHASE 3: RESULT EXTRACTION ===
            sql_query = None
            sql_results = None
            num_iterations = len(response.get("intermediate_steps", []))

            sql_logger.info(f"ASYNC_AGENT_ITERATIONS: {num_iterations}")

            for action, observation in response.get("intermediate_steps", []):
                if hasattr(action, 'tool') and action.tool == "sql_db_query":
                    sql_query = (
                        action.tool_input.get("query")
                        if isinstance(action.tool_input, dict)
                        else action.tool_input
                    )
                    sql_results = observation

                    sql_logger.info("ASYNC_GENERATED_SQL:")
                    for line in sql_query.split('\n'):
                        sql_logger.info(f"  {line}")
                    break

            # Get full results
            full_results = self.toolkit.get_full_results()

            if full_results and full_results != "[]":
                final_results = full_results
            elif sql_results:
                final_results = sql_results
            else:
                final_results = "[]"

            # === PHASE 4: RESULT METRICS ===
            result_count = 0
            try:
                parsed = json.loads(final_results)
                if isinstance(parsed, list):
                    result_count = len(parsed)
                elif isinstance(parsed, dict) and "total_rows" in parsed:
                    result_count = parsed["total_rows"]
            except:
                pass

            tables_accessed = self._extract_tables_from_query(sql_query) if sql_query else []

            sql_logger.info(f"ASYNC_RESULT_COUNT: {result_count} rows")
            sql_logger.info("ASYNC_SQL_EXECUTION_STATUS: SUCCESS")
            sql_logger.info("ASYNC_QUERY_STATUS: COMPLETED")
            sql_logger.info("="*80)

            return {
                "answer": response.get("output", "Query completed."),
                "sql_query": sql_query,
                "results": final_results,
                "intermediate_steps": response.get("intermediate_steps", []),
                "metadata": {
                    "sql_query": sql_query,
                    "result_count": result_count,
                    "tables_accessed": tables_accessed,
                    "timestamp": datetime.now().isoformat(),
                    "execution_time": execution_time,
                }
            }

        except Exception as e:
            # === ERROR RECOVERY ===
            error_info = self._analyze_error(e, question)

            sql_logger.error("="*80)
            sql_logger.error(f"ASYNC_QUERY_ID: {query_id}")
            sql_logger.error(f"ASYNC_SQL_EXECUTION_STATUS: FAILED")
            sql_logger.error(f"ASYNC_ERROR_TYPE: {error_info['error_type']}")
            sql_logger.error(f"ASYNC_ERROR_MESSAGE: {str(e)}")
            sql_logger.error("="*80)

            logger.error(f"Async error executing query: {str(e)}", exc_info=True)

            return {
                "answer": error_info["user_message"],
                "sql_query": None,
                "results": "[]",
                "error": str(e),
                "error_type": error_info["error_type"],
                "error_suggestion": error_info["suggestion"],
            }
        finally:
            # Always reset full results
            self.toolkit.reset_full_results()

    # ==================== UTILITY METHODS ====================

    def get_full_results(self) -> str:
        """
        Get the full untruncated results from the last query.

        Returns:
            JSON string of complete query results
        """
        return self.toolkit.get_full_results()

    def get_schema_info(self, table_names: Optional[List[str]] = None) -> str:
        """
        Get database schema information.

        Args:
            table_names: Optional list of specific tables to get schema for.
                        If None, returns info for all tables.

        Returns:
            String containing schema information
        """
        try:
            tools = self.toolkit.get_tools()
            info_tool = next((tool for tool in tools if tool.name == "sql_db_schema"), None)

            if not info_tool:
                return "Schema tool not available"

            if table_names:
                # Get schema for specific tables
                table_list = ", ".join(table_names)
                return info_tool._run(table_list)
            else:
                # Get all table names first, then their schemas
                list_tool = next((tool for tool in tools if tool.name == "sql_db_list_tables"), None)
                if list_tool:
                    all_tables = list_tool._run("")
                    return info_tool._run(all_tables)
                return "Could not retrieve table list"

        except Exception as e:
            logger.error(f"Error getting schema info: {str(e)}")
            return f"Error: {str(e)}"

    def get_table_names(self) -> List[str]:
        """
        Get list of all table names in the database.

        Returns:
            List of table names
        """
        try:
            tools = self.toolkit.get_tools()
            list_tool = next((tool for tool in tools if tool.name == "sql_db_list_tables"), None)

            if not list_tool:
                return []

            tables_str = list_tool._run("")
            # Parse the comma-separated list
            tables = [t.strip() for t in tables_str.split(",") if t.strip()]
            return tables

        except Exception as e:
            logger.error(f"Error getting table names: {str(e)}")
            return []

    def get_dialect(self) -> str:
        """
        Get the SQL dialect of the connected database.

        Returns:
            String describing the database dialect (e.g., 'postgresql', 'mysql', 'sqlite')
        """
        return self.db._engine.dialect.name

    def set_verbose(self, verbose: bool):
        """Enable or disable verbose output"""
        self.verbose = verbose
        self.agent_executor.verbose = verbose

    # ==================== SINGLETON PATTERN (Feature 6) ====================

    @classmethod
    def clear_instances(cls):
        """
        Clear all cached singleton instances.

        Useful for testing or when you need to force re-initialization.
        """
        with cls._instance_lock:
            cls._instances.clear()
            logger.info("Cleared all cached SQLAgent instances")
