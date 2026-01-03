"""
MCP Server for VVUQ-MCP.

Provides tools for formal verification contracts and proof submission.
"""

from .tools import (
    create_contract,
    query_contracts,
    get_contract,
    submit_proof,
    get_verification_history,
    process_payment,
)
from .server import get_registered_tools
from .fastmcp_server import create_vvuq_server

__all__ = [
    "create_contract",
    "query_contracts",
    "get_contract",
    "submit_proof",
    "get_verification_history",
    "process_payment",
    "get_registered_tools",
    "create_vvuq_server",
]
