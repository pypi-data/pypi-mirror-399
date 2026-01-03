"""
Prompts package for SQL Agent
"""
from .prompts import (
    get_domain_section,
    get_sql_best_practices,
    get_react_prompt_template,
    get_agent_prefix,
    get_agent_suffix,
)

__all__ = [
    "get_domain_section",
    "get_sql_best_practices",
    "get_react_prompt_template",
    "get_agent_prefix",
    "get_agent_suffix",
]