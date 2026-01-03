import pytest
import re
from pathlib import Path
from vvuq_mcp.verifiers.lean4 import Lean4Verifier

# Mock workspace for init
MOCK_WS = Path("/tmp/mock_ws")

class TestTheoremExtraction:
    def test_single_argument(self):
        code = "theorem foo (x : Nat) : x = x := by rfl"
        match = Lean4Verifier.THEOREM_PATTERN.search(code)
        assert match
        assert match.group(3).strip() == "x = x"

    def test_multiple_arguments_bug(self):
        # This corresponds to Ticket #24
        code = "theorem foo (x : Nat) (y : Nat) : x + y = y + x := by sorry"
        match = Lean4Verifier.THEOREM_PATTERN.search(code)
        assert match, "Failed to match theorem with multiple argument groups"
        assert match.group(3).strip() == "x + y = y + x"

    def test_implicit_arguments(self):
        code = "theorem foo {x : Nat} : x = x := by rfl"
        match = Lean4Verifier.THEOREM_PATTERN.search(code)
        assert match, "Failed to match theorem with implicit arguments"

    def test_type_class_arguments(self):
        code = "theorem foo [Semiring R] (x : R) : x = x := by rfl"
        match = Lean4Verifier.THEOREM_PATTERN.search(code)
        assert match, "Failed to match theorem with type class arguments"

    def test_no_arguments(self):
        code = "theorem foo : 1 = 1 := by rfl"
        match = Lean4Verifier.THEOREM_PATTERN.search(code)
        assert match
        assert match.group(3).strip() == "1 = 1"

    def test_quadratic_proof_exact(self):
        code = """
import Mathlib.Tactic.Ring

theorem quadratic_expand (x y : Nat) : (x + y) * (x + 2 * y) = x^2 + 3 * x * y + 2 * y^2 := by
  ring
"""
        match = Lean4Verifier.THEOREM_PATTERN.search(code)
        assert match, "Failed to match Quadratic Proof structure"
        statement = match.group(3).strip()
        if ":=" in statement:
             statement = statement.split(":=")[0].strip()
        
        assert "(x + y)" in statement

    def test_example_syntax(self):
        code = "example (x : Nat) : x = x := by rfl"
        match = Lean4Verifier.THEOREM_PATTERN.search(code)
        assert match, "Failed to match example syntax"
        assert match.group(1) == "example"
        assert match.group(2) is None
        assert match.group(3).strip() == "x = x"
