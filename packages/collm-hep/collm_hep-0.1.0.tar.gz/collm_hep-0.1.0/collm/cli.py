"""
CoLLM Command Line Interface
============================

Provides command-line tools for running CoLLM analysis.

Usage:
    collm --config config.yml         Run analysis with config file
    collm --input user.txt --output out.py  Generate code from input
    collm-gui                          Launch the GUI
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional


def main() -> int:
    """Main CLI entry point.
    
    Returns:
        Exit code (0 for success, 1 for error).
    """
    parser = argparse.ArgumentParser(
        prog="collm",
        description="CoLLM - Automated Deep Learning Toolbox for Collider Physics Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  collm --config config.yml
      Run analysis using a configuration file
      
  collm --input user_input.txt --output analysis.py
      Generate code from user input file
      
  collm --input user_input.txt --output analysis.py --api --api-key YOUR_KEY
      Generate code using HuggingFace API
      
  collm --gui
      Launch the Streamlit GUI
"""
    )
    
    parser.add_argument(
        "--version", "-V",
        action="store_true",
        help="Show version and exit"
    )
    
    parser.add_argument(
        "--config", "-c",
        type=str,
        metavar="FILE",
        help="Path to YAML configuration file"
    )
    
    parser.add_argument(
        "--input", "-i",
        type=str,
        metavar="FILE",
        help="Path to user input specification file"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        metavar="FILE",
        help="Path to save generated Python code"
    )
    
    parser.add_argument(
        "--model", "-m",
        type=str,
        default="Qwen/Qwen2.5-Coder-14B-Instruct",
        metavar="MODEL_ID",
        help="HuggingFace model ID (default: Qwen/Qwen2.5-Coder-14B-Instruct)"
    )
    
    parser.add_argument(
        "--api",
        action="store_true",
        help="Use HuggingFace Inference API instead of local model"
    )
    
    parser.add_argument(
        "--api-key",
        type=str,
        metavar="KEY",
        help="HuggingFace API key (required if --api is set)"
    )
    
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch Streamlit GUI"
    )
    
    parser.add_argument(
        "--check-env",
        action="store_true",
        help="Check and report the runtime environment"
    )
    
    parser.add_argument(
        "--ensure-deps",
        action="store_true", 
        help="Ensure all dependencies are properly configured (NumPy, PyTorch GPU support)"
    )
    
    parser.add_argument(
        "--test-file", "-t",
        type=str,
        metavar="FILE",
        help="LHCO test file for validation (used with --config)"
    )
    
    parser.add_argument(
        "--max-retries", "-r",
        type=int,
        default=3,
        metavar="N",
        help="Maximum retries for code fixing (default: 3)"
    )
    
    args = parser.parse_args()
    
    # Handle version
    if args.version:
        from collm import __version__
        print(f"collm {__version__}")
        return 0
    
    # Handle environment check
    if args.check_env:
        from collm.utils.requirements_check import print_environment_report
        print_environment_report()
        return 0
    
    # Handle ensure dependencies
    if args.ensure_deps:
        from collm.utils.requirements_check import ensure_packages
        ensure_packages(exit_on_restart=False)
        print("Dependencies check complete.")
        return 0
    
    # Handle GUI
    if args.gui:
        return run_gui()
    
    # Handle config file mode
    if args.config:
        from collm.runs.preselection import run_from_config
        success = run_from_config(args.config)
        return 0 if success else 1
    
    # Handle direct input/output mode
    if args.input and args.output:
        if args.api and not args.api_key:
            print("Error: --api-key is required when using --api", file=sys.stderr)
            return 1
        
        from collm import generate_lhco_code
        
        code = generate_lhco_code(
            output_path=args.output,
            user_input_path=args.input,
            model_id=args.model,
            use_api=args.api,
            api_key=args.api_key
        )
        
        if code:
            print(f"Code generated successfully: {args.output}")
            return 0
        else:
            print("Failed to generate code", file=sys.stderr)
            return 1
    
    # No valid arguments
    parser.print_help()
    return 0


def run_gui() -> int:
    """Launch the Streamlit GUI.
    
    Returns:
        Exit code.
    """
    import subprocess
    from collm.utils.paths import get_package_dir
    
    gui_path = get_package_dir() / "gui" / "main.py"
    
    if not gui_path.exists():
        print(f"Error: GUI file not found at {gui_path}", file=sys.stderr)
        return 1
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "streamlit", "run", str(gui_path)],
            check=False
        )
        return result.returncode
    except FileNotFoundError:
        print(
            "Error: streamlit not found. Try reinstalling: pip install --force-reinstall collm-hep",
            file=sys.stderr
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
