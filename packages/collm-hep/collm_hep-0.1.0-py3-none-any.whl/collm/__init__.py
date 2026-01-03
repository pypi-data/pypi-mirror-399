"""
CoLLM - An Automated, End-to-End Deep Learning Toolbox for Collider Physics Analysis
======================================================================================

Generate production-ready Python analysis scripts for LHCO particle physics data
using Large Language Models.

Example usage:
    >>> from collm import generate_lhco_code
    >>> code = generate_lhco_code(
    ...     user_input_path="user_input.txt",
    ...     output_path="generated_analysis.py",
    ...     model_id="Qwen/Qwen2.5-Coder-14B-Instruct"
    ... )

For more information, see: https://github.com/yourusername/CoLLM
"""

__version__ = "0.1.0"
__author__ = "CoLLM Authors"
__license__ = "MIT"

# Use lazy imports to avoid loading heavy dependencies (torch, transformers) on import
def __getattr__(name):
    """Lazy import of main functions to avoid loading heavy dependencies."""
    if name == "generate_lhco_code":
        from collm.llm.generator import generate_lhco_code
        return generate_lhco_code
    elif name == "fix_code":
        from collm.llm.fixer import fix_code
        return fix_code
    elif name == "run_analysis":
        from collm.runs.preselection import run_LLM
        return run_LLM
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "__version__",
    "__author__",
    "__license__",
    "generate_lhco_code",
    "fix_code",
]
