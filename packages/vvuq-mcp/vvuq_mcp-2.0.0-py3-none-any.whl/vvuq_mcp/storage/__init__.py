"""
Storage layer for VVUQ-MCP.

Provides Neo4j-backed persistence for contracts, verification attempts, and payments.
"""

from .neo4j_client import VVUQStorage

__all__ = ["VVUQStorage"]
