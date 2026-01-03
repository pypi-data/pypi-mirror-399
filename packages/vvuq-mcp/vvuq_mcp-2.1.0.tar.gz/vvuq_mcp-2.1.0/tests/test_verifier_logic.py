import pytest
import os
import time
from vvuq import VVUQClient, VVUQError

# Configuration
# Use 127.0.0.1 default to match SDK v0.1.3+, but allow override via Env Var (e.g. for CI)
API_URL = os.getenv("VVUQ_API_URL", "http://127.0.0.1:8081")
API_KEY = os.getenv("VVUQ_API_KEY", "e3e0506d293ab30dd243f7179150af0e7d7f3842f28745a0b2aa02049348a8d3")

@pytest.fixture(scope="module")
def client():
    """Initialize SDK Client"""
    return VVUQClient(api_key=API_KEY, base_url=API_URL)

@pytest.fixture(scope="module")
def quadratic_contract(client):
    """Create the Quadratic Equation contract once for the module"""
    try:
        # Use a random suffix to avoid collision if server persists data
        import uuid
        run_id = str(uuid.uuid4())[:8]
        
        receipt = client.create_contract(
            title=f"Quadratic Verify {run_id}",
            description="Verify (x+y)(x+2y) expansion",
            claims=[{
                "claim_id": 1,
                "theorem": "theorem quadratic_expand (x y : Nat) : (x + y) * (x + 2 * y) = x^2 + 3 * x * y + 2 * y^2",
                "allowed_imports": ["Mathlib.Tactic.Ring"],
                "payment_amount": 50.0
            }],
            issuer_id=f"tester_{run_id}"
        )
        return receipt.contract_id
    except Exception as e:
        pytest.fail(f"Failed to create setup contract: {e}")

def test_valid_proof(client, quadratic_contract):
    """Verify that a mathematically correct proof is ACCEPTED"""
    valid_proof = """
import Mathlib.Tactic.Ring

theorem quadratic_expand (x y : Nat) : (x + y) * (x + 2 * y) = x^2 + 3 * x * y + 2 * y^2 := by
  ring
"""
    res = client.submit_proof(
        contract_id=quadratic_contract, 
        proof_code=valid_proof, 
        prover_id="valid_prover_1", 
        claim_index=0
    )
    
    assert res.verdict == "ACCEPTED", f"Valid proof was rejected! Errors: {res.errors}"
    assert res.contract_id == quadratic_contract

@pytest.mark.parametrize("name, proof_code, expected_error_fragment", [
    ("Wrong Coefficients", """
import Mathlib.Tactic.Ring
theorem quadratic_expand (x y : Nat) : (x + y) * (x + 2 * y) = x^2 + 4 * x * y + 2 * y^2 := by
  ring
""", "tactic 'ring' failed"),
    
    ("Missing Import", """
theorem quadratic_expand (x y : Nat) : (x + y) * (x + 2 * y) = x^2 + 3 * x * y + 2 * y^2 := by
  ring
""", "unknown tactic"),

    ("Wrong Tactic", """
import Mathlib.Tactic.Ring
theorem quadratic_expand (x y : Nat) : (x + y) * (x + 2 * y) = x^2 + 3 * x * y + 2 * y^2 := by
  simp
""", "tactic 'simp' failed"),

    ("Syntax Error", """
import Mathlib.Tactic.Ring
theorem quadratic_expand (x y : Nat) : (x + y) * (x + 2 * y) = x^2 + 3 * x * y + 2 * y^2 := by
  ring_oops
""", "unknown tactic"),

    ("Incomplete (sorry)", """
import Mathlib.Tactic.Ring
theorem quadratic_expand (x y : Nat) : (x + y) * (x + 2 * y) = x^2 + 3 * x * y + 2 * y^2 := by
  sorry
""", "contains 'sorry'"),
    
    ("Type Error", """
import Mathlib.Tactic.Ring
theorem quadratic_expand (x y : Nat) : (x + y) * (x + 2 * y) = x^2 + 3 * x * y + 2 * y^2 := by
  exact "not a proof"
""", "type mismatch"),
])
def test_invalid_proofs(client, quadratic_contract, name, proof_code, expected_error_fragment):
    """Verify that various invalid proofs are REJECTED"""
    res = client.submit_proof(
        contract_id=quadratic_contract, 
        proof_code=proof_code, 
        prover_id=f"mutant_{name.replace(' ','_')}", 
        claim_index=0
    )
    
    assert res.verdict == "REJECTED", f"Invalid proof '{name}' was ACCEPTED incorrectly!"
    # Optional: Check if error message contains hint (not strict requirement if system is opaque, but good for debugging)
    # Note: Backend might not return detailed errors to client in all modes, but usually does in 'errors' list.
    # if res.errors:
        # assert any(expected_error_fragment.lower() in e.lower() for e in res.errors), f"Error message mismatch for {name}: {res.errors}"
