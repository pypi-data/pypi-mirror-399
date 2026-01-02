"""
MCP Server registration for VVUQ-MCP.

Provides the server setup and tool registration.
"""

from typing import Dict, List

# Tool registry
_REGISTERED_TOOLS: Dict[str, callable] = {}


def register_tool(name: str, func: callable) -> None:
    """Register a tool with the server."""
    _REGISTERED_TOOLS[name] = func


def get_registered_tools() -> List[str]:
    """Get list of registered tool names."""
    return list(_REGISTERED_TOOLS.keys())


# Import and register all tools
def _setup_tools():
    """Initialize and register all MCP tools."""
    from .tools import (
        create_contract,
        query_contracts,
        get_contract,
        submit_proof,
        get_verification_history,
        process_payment,
    )

    register_tool("create_contract", create_contract)
    register_tool("query_contracts", query_contracts)
    register_tool("get_contract", get_contract)
    register_tool("submit_proof", submit_proof)
    register_tool("get_verification_history", get_verification_history)
    register_tool("process_payment", process_payment)


# Auto-register tools on import
_setup_tools()
