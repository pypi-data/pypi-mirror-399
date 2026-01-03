"""
Preselection Runner - Main code that runs the LLM analysis.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import warnings
from pathlib import Path
from typing import Optional

from collm.llm.generator import generate_lhco_code
from collm.llm.fixer import fix_code
from collm.utils.config import read_config, CoLLMConfig
from collm.utils.requirements_check import ensure_packages

warnings.filterwarnings("ignore", message="To copy construct from a tensor")


def recreate_dir(path: str | Path) -> None:
    """Recreate a directory (delete if exists, then create).
    
    Args:
        path: Path to the directory.
    """
    path = Path(path)
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def run_and_capture_error(
    script_path: str,
    *args,
    output_dir: Optional[str] = None
) -> str:
    """Run a Python script and return any error output.
    
    Args:
        script_path: Path to the Python script.
        *args: Arguments to pass to the script.
        output_dir: Working directory for execution.
        
    Returns:
        Error output if script failed, empty string if successful.
    """
    env = os.environ.copy()
    env['MPLBACKEND'] = 'Agg'
    
    result = subprocess.run(
        [sys.executable, script_path] + list(args),
        capture_output=True,
        text=True,
        cwd=output_dir,
        env=env
    )
    
    return result.stderr if result.returncode != 0 else ""


def run_LLM(
    output_dir: str,
    model_id: str,
    input_test: str,
    input_user: str,
    output_code: str,
    max_retries: int,
    use_api: bool = False,
    api_key: Optional[str] = None
) -> bool:
    """Run LLM code generation with automatic error fixing.
    
    Args:
        output_dir: Directory to save outputs.
        model_id: HuggingFace model identifier.
        input_test: Path to test LHCO file.
        input_user: Path to user input specification.
        output_code: Path to save generated code.
        max_retries: Maximum fix/regenerate attempts.
        use_api: Use HuggingFace API instead of local model.
        api_key: HuggingFace API key.
        
    Returns:
        True if code was generated and executed successfully, False otherwise.
    """
    env = os.environ.copy()
    env['MPLBACKEND'] = 'Agg'
    
    # Generate initial code
    generate_lhco_code(
        user_input_path=input_user,
        output_path=output_code,
        model_id=model_id,
        use_api=use_api,
        api_key=api_key
    )
    
    error = run_and_capture_error(output_code, input_test, output_dir=output_dir)
    retries = 0

    while error and retries < max_retries:
        print(f"Trial {retries + 1}/{max_retries}")
    
        # Try to fix the code
        print("  Attempting to fix...")
        code = Path(output_code).read_text()
        fixed = fix_code(code, error, model_id, use_api=use_api, api_key=api_key)
        Path(output_code).write_text(fixed)
        error = run_and_capture_error(output_code, input_test, output_dir=output_dir)
    
        if not error:
            break  
       
        # If fix failed, regenerate from scratch
        print("  Fix failed, regenerating...")
        generate_lhco_code(
            user_input_path=input_user,
            output_path=output_code,
            model_id=model_id,
            use_api=use_api,
            api_key=api_key
        )
        error = run_and_capture_error(output_code, input_test, output_dir=output_dir)
    
        if not error:
            break  
       
        retries += 1

    if error:
        print("""Failed to execute the analysis code. Please check the following:  
    1- Please make sure the requested plots are ensured in the selection cuts.
    2- Make sure to write the code in an understandable and clear way.
    3- You may increase the number of trials to fix the generated code.
    4- You may consider larger LLM model for complicated analysis.
    """)
        return False
    else:
        print(f"Analysis code generated successfully. Output is stored in {output_dir}")
        subprocess.run([sys.executable, output_code, input_test], cwd=output_dir, env=env)
        return True


def run_from_config(config_path: str) -> bool:
    """Run LLM analysis from a configuration file.
    
    Args:
        config_path: Path to YAML configuration file.
        
    Returns:
        True if successful, False otherwise.
    """
    # Ensure runtime environment is properly configured
    ensure_packages()
    
    output_dir, model_id, max_retries, input_test, input_user, use_api, api_key = read_config(
        config_path
    )
    
    output_code = str(Path(output_dir) / "generated_lhco_analysis.py")
    recreate_dir(output_dir)
    
    return run_LLM(
        output_dir=output_dir,
        model_id=model_id,
        input_test=input_test,
        input_user=input_user,
        output_code=output_code,
        max_retries=max_retries,
        use_api=use_api,
        api_key=api_key
    )
