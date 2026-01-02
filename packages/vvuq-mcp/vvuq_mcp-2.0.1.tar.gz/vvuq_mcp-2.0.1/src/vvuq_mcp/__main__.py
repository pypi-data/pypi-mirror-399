"""
Entry point for running vvuq-mcp as a module: python -m vvuq_mcp
"""

import os
from pathlib import Path

from vvuq_mcp.mcp.fastmcp_server import create_vvuq_server
from vvuq_mcp.storage import VVUQStorage
from vvuq_mcp.verifiers import Lean4Verifier

def main():
    # Initialize Lean4 verifier with workspace from environment
    # Default to local path relative to current dir, or /tmp
    default_ws = str(Path.cwd() / "lean-workspace")
    lean_workspace = os.getenv("LEAN_WORKSPACE", default_ws)
    verifier = Lean4Verifier(workspace_dir=Path(lean_workspace))

    from dotenv import load_dotenv

    # Load environment variables from .env file
    load_dotenv()

    # Initialize Neo4j storage with connection details
    # Uses the same Neo4j instance as neo4j-memory MCP
    neo4j_password = os.getenv("NEO4J_PASSWORD")
    if not neo4j_password:
        raise ValueError("NEO4J_PASSWORD environment variable is not set")

    storage = VVUQStorage(
        uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        user=os.getenv("NEO4J_USER", "neo4j"),
        password=neo4j_password,
    )

    # Create and run the MCP server
    server = create_vvuq_server(storage=storage, verifier=verifier)
    server.run()

if __name__ == "__main__":
    main()
