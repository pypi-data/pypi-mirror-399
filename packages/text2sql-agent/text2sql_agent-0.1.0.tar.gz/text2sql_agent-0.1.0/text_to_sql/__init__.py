"""
Text2SQL Agent - A flexible, LLM-agnostic text-to-SQL agent
"""

from .agent import SQLAgent
from .database import JSONSerializableSQLDatabase
from .tools import JSONSQLDatabaseToolkit, JSONQuerySQLTool

__version__ = "0.1.0"
__all__ = [
    "SQLAgent",
    "JSONSerializableSQLDatabase",
    "JSONSQLDatabaseToolkit",
    "JSONQuerySQLTool",
]
