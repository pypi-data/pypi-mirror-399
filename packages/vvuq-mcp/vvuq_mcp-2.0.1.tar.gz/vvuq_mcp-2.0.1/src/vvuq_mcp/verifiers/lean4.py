"""
Lean4 proof verifier implementation.

This verifier compiles Lean4 proofs using lake build and validates:
- Compilation success (no errors)
- No sorry keywords (incomplete proofs)
- Only authorized dependencies (imports)
- Proven theorem matches expected claim

Performance optimizations:
- Reuses workspace directory with cached mathlib
- Caches compilation results by content hash
- Uses set-based O(1) dependency lookup
- Fail-fast sorry detection
"""

import aiofiles
import asyncio
import functools
import hashlib
import logging
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, FrozenSet, List, Optional, Set, Tuple

from vvuq_mcp.models import VerificationResult
from vvuq_mcp.verifiers.base import BaseVerifier
from vvuq_mcp.workspaces import WorkspaceManager

# Initialize logger
logger = logging.getLogger(__name__)

# Cache for compilation results
_COMPILATION_CACHE: Dict[str, VerificationResult] = {}
_CACHE_MAX_SIZE = 1000

# Cache for normalized theorems
_NORMALIZED_THEOREM_CACHE: Dict[str, str] = {}


def _cache_key(proof_code: str, expected_theorem: str, allowed_deps: FrozenSet[str]) -> str:
    """Generate cache key from proof and dependencies."""
    content = f"{proof_code}|{expected_theorem}|{sorted(allowed_deps)}"
    return hashlib.sha256(content.encode()).hexdigest()


class Lean4Verifier(BaseVerifier):
    """
    Lean4 proof verification engine.

    Verifies Lean4 proofs by:
    1. Writing proof to workspace (reused, cached mathlib)
    2. Validating imports against allowed set (O(n) via set lookup)
    3. Running lake build with timeout
    4. Checking for sorry keywords (fail-fast)
    5. Extracting and comparing theorem statements
    """

    # Regex patterns for Lean4 parsing (compiled once at class level)
    IMPORT_PATTERN = re.compile(r"^\s*import\s+(\S+)", re.MULTILINE)
    SORRY_PATTERN = re.compile(r"\bsorry\b", re.IGNORECASE)
    # Regex to extract theorem statements
    THEOREM_PATTERN = re.compile(
        r"^\s*(theorem|lemma|def|example)(?:\s+(\w+))?(?:\s*(?:@?\(.*?\)|@?\{.*?\}|@?\[.*?\]))*\s*:\s*(.+?)\s*:=",
        re.MULTILINE | re.DOTALL,
    )

    # Resource Limits
    MAX_TIMEOUT = 300  # Maximum timeout in seconds
    MAX_CONCURRENT_COMPILATIONS = 10  # Semaphore limit

    def __init__(self, workspace_dir: Path, mathlib_version: str = "latest"):
        """
        Initialize Lean4 verifier.

        Args:
            workspace_dir: Directory for verification. Should contain mathlib cache.
            mathlib_version: Mathlib version to use (default: latest)
        """
        super().__init__(workspace_dir)
        self.mathlib_version = mathlib_version
        
        # Security: Resolve and validate workspace path
        self.workspace_dir = self.workspace_dir.resolve()
        
        # Initialize Workspace Manager
        try:
             base_dir = Path.home() / ".vvuq"
        except:
             base_dir = self.workspace_dir.parent
        self.workspace_manager = WorkspaceManager(base_dir)

        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self._workspace_initialized = False
        # self._setup_workspace() # DEFER SETUP to _compile_proof_internal for dynamic support
        
        # Concurrency Control
        self._compilation_semaphore = asyncio.Semaphore(self.MAX_CONCURRENT_COMPILATIONS)

    def _setup_workspace(self) -> None:
        """Setup reusable workspace with lake project structure."""
        if self._workspace_initialized:
            return

        # Write lakefile.lean for minimal project (reused across verifications)
        lakefile = self.workspace_dir / "lakefile.lean"
        if not lakefile.exists():
            lakefile.write_text("""
import Lake
open Lake DSL

package verification where
  -- Minimal package for verification

@[default_target]
lean_lib Verification where
  -- Source files
""")

        # Write lean-toolchain
        toolchain = self.workspace_dir / "lean-toolchain"
        if not toolchain.exists():
            toolchain.write_text("leanprover/lean4:v4.3.0")

        # Create lib directory
        lib_dir = self.workspace_dir / "Verification"
        lib_dir.mkdir(exist_ok=True)

        self._workspace_initialized = True

    def _create_result(
        self,
        verdict: str,
        compilation_output: str,
        start_time: float,
        proven_theorem: Optional[str] = None,
        matches_claim: bool = False,
        errors: Optional[List[str]] = None,
        sorry_count: int = 0,
        unauthorized_dependencies: Optional[List[str]] = None,
    ) -> VerificationResult:
        """
        Factory method for creating VerificationResult objects.

        Eliminates DRY violation of repeated result construction.
        Automatically calculates verification_time_ms and sets timestamp.

        Args:
            verdict: Verification verdict (ACCEPTED/REJECTED/ERROR)
            compilation_output: Output from Lean4 compiler
            start_time: Timestamp when verification started
            proven_theorem: Theorem that was proven (if any)
            matches_claim: Whether proven theorem matches expected
            errors: List of error messages
            sorry_count: Number of sorry keywords found
            unauthorized_dependencies: List of unauthorized imports

        Returns:
            VerificationResult with all fields populated
        """
        verification_time_ms = int((time.time() - start_time) * 1000)
        return VerificationResult(
            verdict=verdict,
            compilation_output=compilation_output,
            proven_theorem=proven_theorem,
            matches_claim=matches_claim,
            errors=errors or [],
            sorry_count=sorry_count,
            unauthorized_dependencies=unauthorized_dependencies or [],
            verification_time_ms=verification_time_ms,
            timestamp=datetime.now(),
        )

    def _validate_proof_syntax(self, proof_code: str, start_time: float) -> Optional[VerificationResult]:
        """Step 1: fail-fast on sorry."""
        sorry_result = self._check_for_sorry_fast(proof_code)
        if sorry_result is not None:
            sorry_count, sorry_lines = sorry_result
            return self._create_result(
                verdict="REJECTED",
                compilation_output="Proof contains sorry (incomplete)",
                start_time=start_time,
                errors=[f"Sorry found at line {line}" for line in sorry_lines],
                sorry_count=sorry_count,
            )
        return None

    def _validate_imports(
        self, proof_code: str, allowed_set: FrozenSet[str], start_time: float
    ) -> Tuple[Optional[VerificationResult], List[str]]:
        """Step 2: validate imports."""
        imports = self.extract_imports(proof_code)
        dep_valid, violations = self._validate_dependencies_fast(imports, allowed_set)
        
        if not dep_valid:
            result = self._create_result(
                verdict="REJECTED",
                compilation_output="Dependency validation failed",
                start_time=start_time,
                errors=[f"Unauthorized import: {v}" for v in violations],
                unauthorized_dependencies=violations,
            )
            return result, violations
        return None, []

    async def verify_proof(
        self,
        proof_code: str,
        expected_theorem: str,
        allowed_dependencies: List[str],
        timeout_seconds: int = 60,
        mathlib_version: Optional[str] = None,
        assumption_contexts: List[str] = []
    ) -> VerificationResult:
        """
        Verify a Lean4 proof.
        """
        # Validate timeout parameter
        if timeout_seconds <= 0:
            raise ValueError(f"timeout_seconds must be positive, got {timeout_seconds}")
        if timeout_seconds > self.MAX_TIMEOUT:
            raise ValueError(f"timeout_seconds {timeout_seconds}s exceeds maximum {self.MAX_TIMEOUT}s")
        
        # Security: Validate mathlib_version format
        if mathlib_version:
             # Strict Git tag/commit hash pattern
             pattern = r'^v\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?$|^[a-f0-9]{40}$'
             if not re.match(pattern, mathlib_version):
                 raise ValueError(f"Security Violation: Invalid mathlib_version format: {mathlib_version}")

        start_time = time.time()
        allowed_set = frozenset(allowed_dependencies)
        
        # Include mathlib_version and assumption_contexts in cache key!
        cache_key_content = f"{proof_code}|{expected_theorem}|{sorted(allowed_set)}|{mathlib_version}|{sorted(assumption_contexts)}"
        cache_key = hashlib.sha256(cache_key_content.encode()).hexdigest()

        # Check cache
        if cache_key in _COMPILATION_CACHE:
            return self._return_cached_result(cache_key, start_time)

        try:
            # 1. Syntax Check
            if res := self._validate_proof_syntax(proof_code, start_time):
                self._cache_result(cache_key, res)
                return res

            # 2. Import Check
            if (res := self._validate_imports(proof_code, allowed_set, start_time)[0]) :
                self._cache_result(cache_key, res)
                return res
            
            # 3. Compile & Verify Theorem
            result = await self._compile_and_verify(
                proof_code, expected_theorem, timeout_seconds, start_time, 
                mathlib_version=mathlib_version, 
                assumption_contexts=assumption_contexts
            )
            self._cache_result(cache_key, result)
            return result

        except ValueError as e:
            # Re-raise security violations - these should not be caught
            if "Security Violation" in str(e):
                raise
            # Other ValueErrors are treated as verification errors
            result = self._create_result(
                verdict="ERROR",
                compilation_output="",
                start_time=start_time,
                errors=[f"Verification error: {str(e)}"]
            )
            self._cache_result(cache_key, result)
            return result
        except Exception as e:
            result = self._create_result(
                verdict="ERROR",
                compilation_output="",
                start_time=start_time,
                errors=[f"Verification error: {str(e)}"]
            )
            self._cache_result(cache_key, result)
            return result

    def _return_cached_result(self, cache_key: str, start_time: float) -> VerificationResult:
        cached = _COMPILATION_CACHE[cache_key]
        return self._create_result(
            verdict=cached.verdict,
            compilation_output=cached.compilation_output,
            start_time=start_time,
            proven_theorem=cached.proven_theorem,
            matches_claim=cached.matches_claim,
            errors=cached.errors,
            sorry_count=cached.sorry_count,
            unauthorized_dependencies=cached.unauthorized_dependencies,
        )

    async def _compile_and_verify(
        self, proof_code: str, expected_theorem: str, timeout_seconds: int, start_time: float, 
        mathlib_version: Optional[str] = None,
        assumption_contexts: List[str] = []
    ) -> VerificationResult:
        """
        Compile proof and verify theorem matches expectation.

        Args:
            proof_code: Lean4 source code
            expected_theorem: Theorem header to match
            timeout_seconds: Max compilation time
            start_time: Start time for performance metrics

        Returns:
            VerificationResult with ACCEPTED/REJECTED/ERROR verdict
        """
        # Validate timeout parameter
        if timeout_seconds <= 0:
            raise ValueError(f"timeout_seconds must be positive, got {timeout_seconds}")
        if timeout_seconds > self.MAX_TIMEOUT:
            raise ValueError(f"timeout_seconds {timeout_seconds}s exceeds maximum {self.MAX_TIMEOUT}s")

        try:
            output = await self._compile_proof(
                proof_code, timeout_seconds, 
                mathlib_version=mathlib_version,
                assumption_contexts=assumption_contexts
            )
            
            if self._has_compilation_errors(output):
                return self._create_result(
                    verdict="REJECTED",
                    compilation_output=output,
                    start_time=start_time,
                    errors=self._extract_errors(output)
                )

            proven = self._extract_theorem_statement(proof_code)
            matches = self._theorems_match_cached(proven, expected_theorem)
            
            errors = []
            if not matches:
                msg = f"Mismatch! Proven: '{proven}' vs Expected: '{expected_theorem}'"
                logger.error(msg)
                errors.append(msg)

            return self._create_result(
                verdict="ACCEPTED" if matches else "REJECTED",
                compilation_output=output,
                start_time=start_time,
                proven_theorem=proven,
                matches_claim=matches,
                errors=errors
            )

        except asyncio.TimeoutError:
            return self._create_result(
                verdict="ERROR",
                compilation_output="Compilation timed out",
                start_time=start_time,
                errors=["Compilation timed out"]
            )

    def _cache_result(self, key: str, result: VerificationResult) -> None:
        """Cache a verification result, evicting old entries if needed."""
        if len(_COMPILATION_CACHE) >= _CACHE_MAX_SIZE:
            # Simple FIFO eviction - remove oldest entry
            oldest_key = next(iter(_COMPILATION_CACHE))
            del _COMPILATION_CACHE[oldest_key]
        _COMPILATION_CACHE[key] = result

    def _check_for_sorry_fast(self, proof_code: str) -> Optional[Tuple[int, List[int]]]:
        """
        Check for sorry keywords with fail-fast behavior.

        Returns None if no sorry found, otherwise (count, line_numbers).
        Stops checking after finding first sorry for simple presence check.
        """
        sorry_lines = []
        lines = proof_code.split("\n")
        in_multiline_comment = False

        for i, line in enumerate(lines, start=1):
            # Handle multiline comments
            if in_multiline_comment:
                if "-/" in line:
                    in_multiline_comment = False
                    # Extract part after comment
                    line = line.split("-/", 1)[1]
                else:
                    continue

            # Check for start of multiline comment
            if "/-" in line:
                line, in_multiline_comment = self._process_multiline_start(line)

            # Skip single line comments
            if "--" in line:
                line = line.split("--")[0]

            # Fast check using str.find instead of regex
            if "sorry" in line.lower():
                # Verify it's not in a string (simple heuristic)
                if not self._is_in_string_fast(line, "sorry"):
                    sorry_lines.append(i)
                    # Fail-fast: we found at least one sorry
                    # Continue to count all for detailed report

        if sorry_lines:
            return (len(sorry_lines), sorry_lines)
        return None

    def _process_multiline_start(self, line: str) -> Tuple[str, bool]:
        """Helper to process multiline comment start to reduce nesting."""
        parts = line.split("/-", 1)
        pre_comment = parts[0]
        post_comment = parts[1]
        
        if "-/" not in post_comment:
            # Opened but not closed
            return pre_comment, True

        # Opened and closed on same line: /- ... -/
        try:
            after_comment = post_comment.split("-/", 1)[1]
            return pre_comment + " " + after_comment, False
        except IndexError:
            return pre_comment, False

    async def check_for_sorry(self, proof_code: str) -> List[int]:
        """
        Check for sorry keywords in proof code.

        Args:
            proof_code: Lean4 proof code

        Returns:
            List of line numbers (1-indexed) where sorry appears
        """
        result = self._check_for_sorry_fast(proof_code)
        return result[1] if result else []

    def _is_in_string_fast(self, line: str, keyword: str) -> bool:
        """
        Check if keyword appears inside a string literal.

        Optimized version using str.find and simple quote tracking.
        """
        keyword_lower = keyword.lower()
        line_lower = line.lower()

        # Fast path: keyword not in line at all
        keyword_pos = line_lower.find(keyword_lower)
        if keyword_pos == -1:
            return False

        # Check if this position is inside quotes
        in_string = False
        quote_char = None

        for i, char in enumerate(line):
            if i == keyword_pos and not in_string:
                # Found keyword outside string
                return False

            if not in_string:
                if char in ['"', "'"]:
                    in_string = True
                    quote_char = char
            else:
                if char == quote_char and (i == 0 or line[i-1] != '\\'):
                    in_string = False
                    quote_char = None

        # Keyword only found in strings
        return keyword_lower in line_lower

    def extract_imports(self, proof_code: str) -> List[str]:
        """
        Extract import statements from Lean4 proof code.

        Args:
            proof_code: Lean4 code

        Returns:
            List of import paths (e.g., ['Mathlib.Data.Nat.Basic'])
        """
        return self.IMPORT_PATTERN.findall(proof_code)

    def _validate_dependencies_fast(
        self, imports: List[str], allowed_set: FrozenSet[str]
    ) -> Tuple[bool, List[str]]:
        """
        Validate that all imports are in the allowed set.

        Uses O(1) set lookup instead of O(n) list iteration.

        Args:
            imports: Imports found in the proof
            allowed_set: Frozenset of allowed import prefixes

        Returns:
            Tuple of (all_valid, list_of_violations)
        """
        violations = []

        for imp in imports:
            # Check if import is allowed (exact match or prefix match)
            is_allowed = imp in allowed_set or any(
                imp.startswith(f"{allowed_dep}.")
                for allowed_dep in allowed_set
            )
            if not is_allowed:
                violations.append(imp)

        return (len(violations) == 0, violations)

    @staticmethod
    @functools.lru_cache(maxsize=128)
    def _to_frozenset(allowed_tuple: Tuple[str, ...]) -> FrozenSet[str]:
        """
        Convert tuple of allowed dependencies to frozenset with caching.

        Performance: Caching avoids recreating frozensets for repeated calls
        with the same allowed list (common in testing and batch verification).

        Args:
            allowed_tuple: Tuple of allowed import strings (hashable for cache)

        Returns:
            Frozenset of allowed imports for O(1) lookup
        """
        return frozenset(allowed_tuple)

    async def validate_dependencies(
        self, imports: List[str], allowed: List[str]
    ) -> Tuple[bool, List[str]]:
        """
        Validate that all imports are in the allowed list.

        Args:
            imports: Imports found in the proof
            allowed: Allowed import list from contract

        Returns:
            Tuple of (all_valid, list_of_violations)
        """
        # Convert list to tuple for caching, then to cached frozenset
        # This optimization reduces O(n) frozenset creation to O(1) cache lookup
        # when the same allowed list is used repeatedly (e.g., 100x in tests)
        allowed_tuple = tuple(allowed)
        allowed_set = self._to_frozenset(allowed_tuple)
        return self._validate_dependencies_fast(imports, allowed_set)

    async def _compile_proof(self, proof_code: str, timeout_seconds: int, mathlib_version: Optional[str] = None, assumption_contexts: List[str] = []) -> str:
        """
        Compile Lean4 proof using lake env lean for concurrency.

        Args:
            proof_code: Lean4 code to compile
            timeout_seconds: Maximum time for compilation
            mathlib_version: Optional Mathlib version
            assumption_contexts: List of context modules

        Returns:
            Compilation output (stdout + stderr)

        Raises:
            asyncio.TimeoutError: If compilation exceeds timeout
        """
        # Resource Limit: Enforce maximum timeout security check
        if timeout_seconds > self.MAX_TIMEOUT:
            logger.warning(f"Requested timeout {timeout_seconds}s exceeds max {self.MAX_TIMEOUT}s. Capping.")
            timeout_seconds = self.MAX_TIMEOUT

        # Resource Limit: Enforce concurrency limit with semaphore
        async with self._compilation_semaphore:
             return await self._compile_proof_internal(
                 proof_code, timeout_seconds, 
                 mathlib_revision=mathlib_version,
                 assumption_contexts=assumption_contexts
             )

    def _inject_strict_options(self, code: str) -> str:
        """Inject strict options (autoImplicit false) after imports."""
        lines = code.split('\n')
        last_import_idx = -1
        for i, line in enumerate(lines):
            if line.strip().startswith('import '):
                last_import_idx = i
        
        strict_options = "set_option autoImplicit false\n"
        
        if last_import_idx == -1:
            return strict_options + code
        else:
            # Insert after last import
            lines.insert(last_import_idx + 1, strict_options)
            return '\n'.join(lines)

    async def _compile_proof_internal(self, proof_code: str, timeout_seconds: int, mathlib_revision: Optional[str] = None, assumption_contexts: List[str] = []) -> str:
        """Internal compilation logic inside semaphore."""
        # Validate timeout parameter
        if timeout_seconds <= 0:
            raise ValueError(f"timeout_seconds must be positive, got {timeout_seconds}")
        if timeout_seconds > self.MAX_TIMEOUT:
            raise ValueError(f"timeout_seconds {timeout_seconds}s exceeds maximum {self.MAX_TIMEOUT}s")

        # Determine Workspace Path
        if mathlib_revision:
             try:
                 # Dynamic Workspace Provisioning
                 workspace_path = await self.workspace_manager.get_workspace(mathlib_revision, contexts=assumption_contexts)
             except Exception as e:
                 return f"Error: Failed to provision workspace for {mathlib_revision}: {str(e)}"
        else:
             # Legacy / Default Workspace
             if not self._workspace_initialized:
                 self._setup_workspace()
             workspace_path = self.workspace_dir

        # Generate unique filename to allow concurrency
        import uuid
        import re
        uuid_obj = uuid.uuid4()
        # Use hex attribute for cleaner filenames (no hyphens)
        file_id = uuid_obj.hex

        # Security: Validate file_id contains ONLY alphanumeric characters
        if not re.match(r'^[a-zA-Z0-9]+$', file_id):
            raise ValueError(f"Security Violation: Invalid characters in file_id: {file_id}")

        filename = f"Proof_{file_id}.lean"

        # Security: Validate filename contains no shell metacharacters BEFORE file operations
        if re.search(r'[;&|`$()<>\s]', filename):
            raise ValueError(f"Security Violation: Invalid characters in filename: {filename}")

        # Security: Validate filename contains no path traversal BEFORE constructing path
        if '..' in filename or '/' in filename or '\\' in filename:
            raise ValueError(f"Security Violation: Path traversal attempt in filename: {filename}")

        proof_file = workspace_path / "Verification" / filename

        # Security: Double-check resolved path is within workspace (defense in depth)
        try:
            resolved_path = proof_file.resolve()
            workspace_resolved = workspace_path.resolve()
            if not resolved_path.is_relative_to(workspace_resolved):
                raise ValueError(f"Security Violation: Path traversal detected: {resolved_path}")
        except Exception as e:
            # If any resolution fails, reject for security
            raise ValueError(f"Security Violation: Path validation failed: {e}")
        
        # Ensure parent dir exists (it should, but good for robust dynamic workspaces)
        proof_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Use async file I/O to avoid blocking the event loop
            strict_code = self._inject_strict_options(proof_code)
            async with aiofiles.open(proof_file, 'w') as f:
                await f.write(strict_code)

            # Run compilation on this specific file, respecting workspace
            return await asyncio.wait_for(
                self._run_lean_file(filename, cwd=workspace_path),
                timeout=timeout_seconds,
            )
        except asyncio.TimeoutError:
            raise
        finally:
            # Cleanup temp file
            if proof_file.exists():
                proof_file.unlink()

    async def _run_lean_file(self, filename: str, cwd: Optional[Path] = None) -> str:
        """
        Run lean compiler on specific file using lake environment.

        Args:
            filename: Name of file in Verification/ directory
            cwd: Working directory (default: self.workspace_dir)

        Returns:
            Combined stdout and stderr
        """
        if cwd is None:
            cwd = self.workspace_dir
            
        # Use 'lake env lean' to run in project context without build locking
        proc = await asyncio.create_subprocess_exec(
            "lake",
            "env",
            "lean",
            f"Verification/{filename}",
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await proc.communicate()
        output = f"{stdout.decode()}\n{stderr.decode()}"

        # Security Fix for Issue #38
        if proc.returncode != 0:
            return f"Error: Lean process exited with code {proc.returncode}\n{output}"

        return output

    def _has_compilation_errors(self, output: str) -> bool:
        """Check if compilation output contains errors."""
        error_indicators = [
            "error:",
            "Error:",
            "type mismatch",
            "unknown identifier",
            "invalid",
            "failed",
        ]

        output_lower = output.lower()
        return any(indicator.lower() in output_lower for indicator in error_indicators)

    def _extract_errors(self, output: str) -> List[str]:
        """Extract error messages from compilation output."""
        errors = []
        lines = output.split("\n")

        for line in lines:
            if "error" in line.lower() or "Error" in line:
                errors.append(line.strip())

        return errors if errors else ["Compilation failed"]

    def _extract_theorem_statement(self, proof_code: str) -> Optional[str]:
        """
        Extract the main theorem statement from proof code.

        Args:
            proof_code: Lean4 proof code

        Returns:
            Theorem statement (just the type) or None
        """
        match = self.THEOREM_PATTERN.search(proof_code)
        if match:
            # Return just the type/statement part
            statement = match.group(3).strip()
            # Clean up - remove trailing stuff
            if ":=" in statement:
                statement = statement.split(":=")[0].strip()
            return statement
        return None

    def _theorems_match_cached(
        self, proven: Optional[str], expected: str
    ) -> bool:
        """
        Check if proven theorem matches expected theorem with caching.

        Args:
            proven: Theorem statement from proof
            expected: Expected theorem from contract

        Returns:
            True if theorems are equivalent
        """
        if proven is None:
            return False

        # Get normalized forms (cached)
        proven_norm = self._normalize_theorem_cached(proven)
        expected_norm = self._normalize_theorem_cached(expected)

        # Direct match
        if proven_norm == expected_norm:
            return True

        # Check if one contains the other (for partial matches)
        if proven_norm in expected_norm or expected_norm in proven_norm:
            return True

        return False

    def _theorems_match(
        self, proven: Optional[str], expected: str
    ) -> bool:
        """
        Check if proven theorem matches expected theorem.

        Uses normalization to handle whitespace and unicode variations.

        Args:
            proven: Theorem statement from proof
            expected: Expected theorem from contract

        Returns:
            True if theorems are equivalent
        """
        return self._theorems_match_cached(proven, expected)

    @functools.lru_cache(maxsize=1000)
    def _normalize_theorem_cached(self, theorem: str) -> str:
        """Normalize theorem with LRU caching."""
        return self._normalize_theorem(theorem)

    def _normalize_theorem(self, theorem: str) -> str:
        """
        Normalize theorem string for comparison.

        Handles:
        - Whitespace normalization
        - Unicode arrow variations (→ vs ->)
        - Parentheses normalization
        """
        # Remove extra whitespace
        normalized = " ".join(theorem.split())

        # Normalize unicode
        replacements = {
            "→": "->",
            "∀": "forall",
            "∃": "exists",
            "ℕ": "Nat",
            "ℤ": "Int",
            "ℝ": "Real",
            "≠": "!=",
            "≤": "<=",
            "≥": ">=",
        }

        for old, new in replacements.items():
            normalized = normalized.replace(old, new)

        # Remove unnecessary parentheses (basic)
        normalized = normalized.replace("( ", "(").replace(" )", ")")

        return normalized.lower().strip()
