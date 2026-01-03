"""
Path utilities for CoLLM package.

Provides functions to locate package resources like config files and templates.
"""

from __future__ import annotations

import importlib.resources
from pathlib import Path
from typing import Optional


def get_package_dir() -> Path:
    """Get the root directory of the collm package.
    
    Returns:
        Path to the collm package directory.
    """
    return Path(__file__).parent.parent


def get_configs_dir() -> Path:
    """Get the configs directory path.
    
    Returns:
        Path to the configs directory.
    """
    return get_package_dir() / "configs"


def get_templates_dir() -> Path:
    """Get the templates directory path.
    
    Returns:
        Path to the templates directory.
    """
    return get_package_dir() / "templates"


def get_system_prompt_path(filename: str = "system_prompt.txt") -> Path:
    """Get the path to a system prompt file.
    
    Args:
        filename: Name of the system prompt file.
        
    Returns:
        Path to the system prompt file.
        
    Raises:
        FileNotFoundError: If the file doesn't exist.
    """
    path = get_configs_dir() / filename
    if not path.exists():
        raise FileNotFoundError(f"System prompt file not found: {path}")
    return path


def get_template_path(filename: str = "user_input.txt") -> Path:
    """Get the path to a template file.
    
    Args:
        filename: Name of the template file.
        
    Returns:
        Path to the template file.
        
    Raises:
        FileNotFoundError: If the file doesn't exist.
    """
    path = get_templates_dir() / filename
    if not path.exists():
        raise FileNotFoundError(f"Template file not found: {path}")
    return path


def list_templates() -> list[str]:
    """List all available template files.
    
    Returns:
        List of template filenames.
    """
    templates_dir = get_templates_dir()
    if not templates_dir.exists():
        return []
    return [f.name for f in templates_dir.iterdir() if f.is_file()]


def list_system_prompts() -> list[str]:
    """List all available system prompt files.
    
    Returns:
        List of system prompt filenames.
    """
    configs_dir = get_configs_dir()
    if not configs_dir.exists():
        return []
    return [f.name for f in configs_dir.iterdir() if f.is_file() and f.suffix in ('.txt', '.md')]
