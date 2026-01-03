"""
Database abstraction layer for MCP as a Judge.

This module provides database interfaces and providers for storing
conversation history and tool interactions.
"""

from iflow_mcp_hepivax_mcp_as_a_judge.db.factory import DatabaseFactory, create_database_provider
from iflow_mcp_hepivax_mcp_as_a_judge.db.interface import ConversationHistoryDB, ConversationRecord
from iflow_mcp_hepivax_mcp_as_a_judge.db.providers import SQLiteProvider

__all__ = [
    "ConversationHistoryDB",
    "ConversationRecord",
    "DatabaseFactory",
    "SQLiteProvider",
    "create_database_provider",
]
