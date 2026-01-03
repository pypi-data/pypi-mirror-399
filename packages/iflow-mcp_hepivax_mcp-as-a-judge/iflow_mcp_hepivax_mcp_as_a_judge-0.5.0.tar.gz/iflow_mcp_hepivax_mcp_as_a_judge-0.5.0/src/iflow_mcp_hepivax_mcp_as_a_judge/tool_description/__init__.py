"""
Tool description provider package.

This package provides a factory pattern for creating tool description providers
that load tool descriptions from various sources (local files, remote APIs, etc.).
"""

from iflow_mcp_hepivax_mcp_as_a_judge.tool_description.factory import ToolDescriptionProviderFactory
from iflow_mcp_hepivax_mcp_as_a_judge.tool_description.interface import ToolDescriptionProvider
from iflow_mcp_hepivax_mcp_as_a_judge.tool_description.local_storage_provider import LocalStorageProvider

__all__ = [
    "LocalStorageProvider",
    "ToolDescriptionProvider",
    "ToolDescriptionProviderFactory",
]
