"""
Basic tests for CoLLM package.
"""

import pytest
from pathlib import Path


def test_version():
    """Test that version is defined."""
    from collm import __version__
    assert __version__ is not None
    assert isinstance(__version__, str)


def test_imports():
    """Test that main functions can be imported."""
    from collm import generate_lhco_code, fix_code
    assert callable(generate_lhco_code)
    assert callable(fix_code)


def test_package_paths():
    """Test that package path utilities work."""
    from collm.utils.paths import (
        get_package_dir,
        get_configs_dir,
        get_templates_dir,
    )
    
    assert get_package_dir().exists()
    assert get_configs_dir().exists()
    assert get_templates_dir().exists()


def test_system_prompt_exists():
    """Test that system prompt file exists."""
    from collm.utils.paths import get_system_prompt_path
    
    path = get_system_prompt_path()
    assert path.exists()
    
    content = path.read_text()
    assert len(content) > 0


def test_config_loading():
    """Test configuration loading."""
    from collm.utils.config import CoLLMConfig
    from collm.utils.paths import get_templates_dir
    
    config_path = get_templates_dir() / "user_input_TUI.yml"
    if config_path.exists():
        config = CoLLMConfig.from_yaml(config_path)
        assert config.model_id is not None
        assert config.max_retries > 0


def test_parse_user_input_text():
    """Test parsing of user input text."""
    from collm.llm.generator import parse_user_input_text
    
    text = """[SELECTION_CUTS]
- Select electrons with pT > 10 GeV

[PLOTS_FOR_VALIDATION]
- Plot MET distribution

[OUTPUT_STRUCTURE]
- Save histograms
"""
    
    cuts, plots, output = parse_user_input_text(text)
    
    assert "electrons" in cuts
    assert "MET" in plots
    assert "histograms" in output


def test_extract_python_code():
    """Test Python code extraction from LLM response."""
    from collm.llm.generator import extract_python_code
    
    response = """Here's the code:

```python
import sys

def main():
    print("Hello")

if __name__ == "__main__":
    main()
```

This code does XYZ.
"""
    
    code = extract_python_code(response)
    
    assert "import sys" in code
    assert "def main():" in code
    assert "Here's the code" not in code


def test_cli_help():
    """Test that CLI help works."""
    import subprocess
    import sys
    
    result = subprocess.run(
        [sys.executable, "-m", "collm.cli", "--help"],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    assert "collm" in result.stdout.lower()


def test_check_environment():
    """Test environment checking function."""
    from collm.utils.requirements_check import check_environment
    
    info = check_environment()
    
    assert "python_version" in info
    assert "platform" in info
    assert "machine" in info
    assert "cuda_available" in info
    assert "mps_available" in info


def test_ensure_packages_import():
    """Test that ensure_packages can be imported."""
    from collm.utils.requirements_check import ensure_packages, print_environment_report
    
    assert callable(ensure_packages)
    assert callable(print_environment_report)
