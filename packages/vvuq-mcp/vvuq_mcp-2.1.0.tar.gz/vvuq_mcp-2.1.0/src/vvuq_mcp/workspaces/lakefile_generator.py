"""
Lakefile Generator.

Generates lakefile.lean content for Lean4 workspaces with configurable
mathlib dependencies and optional context libraries.
"""


class LakefileGenerator:
    """Generate lakefile.lean for Lean4 workspaces."""

    DEFAULT_MATHLIB_URL = "https://github.com/leanprover-community/mathlib4"
    DEFAULT_LEAN_VERSION = "leanprover/lean4:v4.15.0"

    def __init__(
        self,
        mathlib_url: str = DEFAULT_MATHLIB_URL,
        lean_version: str = DEFAULT_LEAN_VERSION
    ):
        """
        Initialize lakefile generator.

        Args:
            mathlib_url: Git URL for mathlib repository
            lean_version: Lean toolchain version
        """
        self.mathlib_url = mathlib_url
        self.lean_version = lean_version

    def generate(self, revision: str, has_contexts: bool = False) -> str:
        """
        Generate lakefile.lean content.

        Args:
            revision: Mathlib git revision (tag or commit hash)
            has_contexts: Whether to include Contexts library

        Returns:
            lakefile.lean content as string
        """
        context_library = (
            '\nlean_lib «Contexts» {\n  srcDir := "Contexts"\n}\n'
            if has_contexts else ""
        )

        return f"""
import Lake
open Lake DSL

package «vvuq-verification» {{
  -- add package configuration options here
}}

require mathlib from git
  "{self.mathlib_url}" @ "{revision}"

@[default_target]
lean_lib «VvuqVerification» {{
  -- add library configuration options here
}}
{context_library}
"""
