import json
import re
import logging
import threading
from typing import Any, Optional
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit

# Configure logging for SQL queries
sql_logger = logging.getLogger('sql_queries')
sql_logger.setLevel(logging.INFO)
if not sql_logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - SQL_QUERY - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    sql_logger.addHandler(handler)

class JSONQuerySQLTool(QuerySQLDataBaseTool):
    """
    Custom SQL query tool that returns properly formatted JSON results with intelligent result limiting.
    Thread-safe implementation using locks to prevent race conditions.
    """

    def __init__(self, db, max_rows_for_llm=10, large_result_threshold=50, **kwargs):
        super().__init__(db=db, **kwargs)
        # Use private attributes to avoid Pydantic validation issues
        self._max_rows_for_llm = max_rows_for_llm
        self._large_result_threshold = large_result_threshold
        self._full_results: Optional[str] = None  # Store full results for later retrieval
        self._results_lock = threading.Lock()  # Thread-safe access to results

    def _run(self, query: str) -> str:
        """Execute the query and return optimally formatted results for LLM processing"""
        try:
            # Clean the query by removing any markdown formatting
            cleaned_query = self._clean_sql_query(query)

            # Log the SQL query execution at the tool level
            sql_logger.info(f"TOOL_EXECUTING_SQL: {cleaned_query}")

            # Use the custom database's run method if available
            if hasattr(self.db, 'run'):
                full_result = self.db.run(cleaned_query)

                # Store full results for later retrieval (thread-safe)
                with self._results_lock:
                    self._full_results = full_result

                # Log execution success and result info
                sql_logger.info("TOOL_SQL_EXECUTION: SUCCESS")

                # If it's already JSON, process it intelligently
                try:
                    parsed_results = json.loads(full_result)

                    # Check if we have a large result set
                    if isinstance(parsed_results, list) and len(parsed_results) > self._large_result_threshold:
                        # Create a summary for the LLM with limited rows
                        limited_results = parsed_results[:self._max_rows_for_llm]
                        total_rows = len(parsed_results)

                        # Log result statistics
                        sql_logger.info(f"TOOL_RESULT_COUNT: {total_rows} rows (truncated to {len(limited_results)} for LLM)")

                        # Create an optimized response for LLM processing
                        summary_response = {
                            "sample_data": limited_results,
                            "total_rows": total_rows,
                            "message": f"Query returned {total_rows} rows. Showing first {len(limited_results)} rows as sample.",
                            "truncated": True
                        }

                        return json.dumps(summary_response, ensure_ascii=False)
                    else:
                        # Small result set - return as is
                        if isinstance(parsed_results, list):
                            sql_logger.info(f"TOOL_RESULT_COUNT: {len(parsed_results)} rows")
                        return full_result

                except (json.JSONDecodeError, TypeError):
                    # If not JSON, it might be an error message
                    return full_result
            else:
                # Fallback to parent implementation
                return super()._run(query)
        except Exception as e:
            # Log SQL execution error
            sql_logger.error(f"TOOL_SQL_EXECUTION: ERROR - {str(e)}")
            return f"Error executing query: {str(e)}"

    def get_full_results(self) -> str:
        """Get the full untruncated results from the last query (thread-safe)"""
        with self._results_lock:
            return self._full_results if self._full_results else "[]"

    def reset_full_results(self) -> None:
        """Reset the stored full results (thread-safe)"""
        with self._results_lock:
            self._full_results = None

    def _clean_sql_query(self, query: str) -> str:
        """Clean SQL query by removing markdown formatting and extra whitespace"""
        # Remove SQL code block markers
        query = re.sub(r'^```sql\s*', '', query, flags=re.MULTILINE | re.IGNORECASE)
        query = re.sub(r'^```\s*', '', query, flags=re.MULTILINE)
        query = re.sub(r'```\s*$', '', query, flags=re.MULTILINE)

        # Remove any remaining backticks
        query = query.replace('`', '')

        # Clean up whitespace
        query = query.strip()

        return query

class JSONSQLDatabaseToolkit(SQLDatabaseToolkit):
    """
    Custom toolkit that uses JSON-serializable SQL tools with result optimization.
    Inherits from SQLDatabaseToolkit to maintain compatibility.
    Thread-safe implementation for concurrent query handling.
    """

    def __init__(self, db: SQLDatabase, llm: Any = None, max_rows_for_llm=10, large_result_threshold=50, **kwargs):
        # Call parent constructor to set up all required attributes
        super().__init__(db=db, llm=llm, **kwargs)
        # Store optimization parameters as private attributes to avoid Pydantic validation
        self._max_rows_for_llm = max_rows_for_llm
        self._large_result_threshold = large_result_threshold
        self._query_tool: Optional[JSONQuerySQLTool] = None  # Store reference to query tool for result retrieval
        self._toolkit_lock = threading.Lock()  # Thread-safe access to toolkit state

    def get_tools(self):
        """Get SQL tools that return optimized JSON-formatted results"""
        from langchain_community.tools.sql_database.tool import (
            InfoSQLDatabaseTool,
            ListSQLDatabaseTool,
            QuerySQLCheckerTool,
        )

        # Thread-safe tool creation
        with self._toolkit_lock:
            # Create optimized query tool
            self._query_tool = JSONQuerySQLTool(
                db=self.db,
                max_rows_for_llm=self._max_rows_for_llm,
                large_result_threshold=self._large_result_threshold,
                description="Input to this tool is a detailed and correct SQL query, "
                "output is an optimized JSON-formatted result from the database. "
                "Large result sets are automatically summarized for faster processing. "
                "If the query is not correct, an error message will be returned.",
            )

            tools = [
                self._query_tool,
                InfoSQLDatabaseTool(db=self.db),
                ListSQLDatabaseTool(db=self.db),
            ]

            if self.llm:
                tools.append(QuerySQLCheckerTool(db=self.db, llm=self.llm))

            return tools

    def get_full_results(self) -> str:
        """Get the full untruncated results from the last query (thread-safe)"""
        with self._toolkit_lock:
            if self._query_tool:
                return self._query_tool.get_full_results()
            return "[]"

    def reset_full_results(self) -> None:
        """Reset the stored full results (thread-safe)"""
        with self._toolkit_lock:
            if self._query_tool:
                self._query_tool.reset_full_results()
            else:
                raise ValueError("Query tool not initialized. Cannot reset full results.")