# VVUQ-MCP: Verification, Validation & Uncertainty Quantification

**MCP Server for automated marketplace contract verification**

## Overview

VVUQ-MCP is a FastMCP server that acts as an automated judge for marketplace contracts. It verifies formal proofs (starting with Lean4), validates contract fulfillment, and executes cryptographic payments.

## Features

- **Lean4 Proof Verification** - Compile and verify proofs against contract claims
- **Pre-built Mathlib Cache** - Fast verification (< 5s per proof)
- **Cryptographic Payments** - Secure payment settlement with audit trail
- **Neo4j Integration** - Contract storage and query
- **MCP Protocol** - Standard interface for AI agents

## Quick Start

```bash
# Setup
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Build Lean4 mathlib cache (one-time, ~30 min)
cd lean-workspace
lake update && lake build
cd ..

# Run MCP server
python -m vvuq_mcp.server

# Run tests
pytest tests/ -v
```

## Architecture

See `VVUQ_MCP_ARCHITECTURE.md` (in mcp-marketplace repo) for complete architecture documentation.

**Core components:**
- `server.py` - FastMCP server with 4 core tools
- `verifiers/lean4.py` - Lean4 compilation and verification
- `payments/ledger.py` - Simple cryptographic ledger
- `storage/neo4j_client.py` - Async Neo4j integration

## MCP Tools

### verify_lean4_proof
Verify a Lean4 proof against a contract claim.

**Input:**
```python
{
  "contract_id": "lean4-uuid-123",
  "claim_id": 1,
  "proof_code": "theorem my_theorem : ... := by ...",
  "dependencies": ["Mathlib.Data.Nat.Basic"]
}
```

**Output:**
```python
{
  "verdict": "ACCEPTED",  # or REJECTED/ERROR
  "matches_claim": true,
  "payment_executed": {...},
  "verification_time_ms": 4823
}
```

### submit_contract_proof
Submit a proof file for verification (convenience wrapper).

### get_contract_requirements
Retrieve contract requirements for a specific contract.

### query_verification_history
Query past verification attempts and outcomes.

## Development

### TDD Workflow
```bash
# 1. Write test FIRST (RED)
pytest tests/unit/test_lean4_verifier.py::test_new_feature -v

# 2. Implement (GREEN)
# Edit src/vvuq_mcp/verifiers/lean4.py

# 3. Verify
pytest tests/unit/test_lean4_verifier.py::test_new_feature -v

# 4. Refactor
```

### Running Tests
```bash
# All tests
pytest tests/ -v

# Unit tests only (fast)
pytest tests/unit/ -v

# Integration tests (require Neo4j)
pytest tests/integration/ -v

# With coverage
pytest tests/ -v --cov=vvuq_mcp --cov-report=term-missing
```

## Configuration

Create `.env` file:
```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

LEAN_WORKSPACE=/Users/englund/Projects/20251203.vvuq-mcp/lean-workspace
LEAN_TIMEOUT_SECONDS=60
LEAN_MEMORY_LIMIT_MB=2048

PAYMENT_SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_hex(32))">
PAYMENT_LEDGER_MODE=simple
```

## Security

- **Sandboxed Execution** - Lean4 compilation in isolated directories
- **Resource Limits** - CPU/memory/timeout enforcement
- **Input Validation** - Pydantic models for all inputs
- **Cryptographic Signatures** - HMAC-SHA256 for payment authorization
- **Audit Trail** - Complete verification history in Neo4j

## Status

**Phase:** MVP Development (Phase 1)
**Progress:** 100% (MVP Complete - API, Auth, & Verification functional)
**Next:** Production hardening and Dockerization

## License

MIT

## Contact

Dirk Englund - englund@mit.edu
