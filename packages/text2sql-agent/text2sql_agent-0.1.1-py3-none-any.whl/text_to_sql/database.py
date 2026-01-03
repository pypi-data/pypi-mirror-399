import json
import uuid
import datetime
from decimal import Decimal
from typing import Any
from langchain_community.utilities.sql_database import SQLDatabase
from sqlalchemy import text

class JSONSerializableSQLDatabase(SQLDatabase):
    """
    Custom SQLDatabase that returns JSON-serializable results instead of string representations
    """

    def _json_serializer(self, obj: Any) -> Any:
        """JSON serializer for database objects"""
        if isinstance(obj, uuid.UUID):
            return str(obj)
        elif isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        elif isinstance(obj, datetime.time):
            return obj.strftime('%H:%M:%S')
        elif isinstance(obj, Decimal):
            return float(obj)
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        return str(obj)

    def run(self, command: str, fetch: str = "all") -> str:
        """
        Execute a SQL command and return JSON-serialized results
        """
        try:
            with self._engine.connect() as connection:
                cursor = connection.execute(text(command))

                if cursor.returns_rows:
                    if fetch == "all":
                        results = cursor.fetchall()
                    elif fetch == "one":
                        results = cursor.fetchone()
                        if results:
                            results = [results]
                        else:
                            results = []
                    else:
                        results = cursor.fetchall()

                    # Convert to list of dictionaries with column names
                    if results:
                        columns = list(cursor.keys())
                        json_results = []

                        for row in results:
                            row_dict = {}
                            for i, value in enumerate(row):
                                row_dict[columns[i]] = self._json_serializer(value)
                            json_results.append(row_dict)

                        # Return as JSON string
                        return json.dumps(json_results, ensure_ascii=False, indent=None)
                    else:
                        return "[]"
                else:
                    # For non-SELECT queries (INSERT, UPDATE, etc.)
                    return f"Query executed successfully. Rows affected: {cursor.rowcount}"

        except Exception as e:
            return f"Error: {str(e)}"

    def run_no_throw(self, command: str, fetch: str = "all") -> str:
        """
        Execute a SQL command without raising exceptions
        """
        try:
            return self.run(command, fetch)
        except Exception as e:
            return f"Error: {str(e)}"
