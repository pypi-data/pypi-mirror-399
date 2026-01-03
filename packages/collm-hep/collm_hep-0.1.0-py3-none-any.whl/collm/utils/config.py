"""
Configuration utilities for CoLLM.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class CoLLMConfig:
    """Configuration for CoLLM analysis run.
    
    Attributes:
        output_dir: Directory to save generated code and outputs.
        model_id: HuggingFace model identifier.
        max_retries: Maximum number of code fix attempts.
        input_file: Path to input LHCO file for testing.
        user_input: Path to user input specification file.
        use_api: Whether to use HuggingFace Inference API.
        api_key: HuggingFace API key (if using API).
    """
    output_dir: str
    model_id: str
    max_retries: int
    input_file: str
    user_input: str
    use_api: bool = False
    api_key: Optional[str] = None
    
    @classmethod
    def from_yaml(cls, path: str | Path) -> "CoLLMConfig":
        """Load configuration from a YAML file.
        
        Args:
            path: Path to the YAML configuration file.
            
        Returns:
            CoLLMConfig instance.
        """
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        
        return cls(
            output_dir=data.get("Output_dir", "./output/"),
            model_id=data.get("DEFAULT_MODEL", "Qwen/Qwen2.5-Coder-14B-Instruct"),
            max_retries=data.get("MAX_RETRIES", 3),
            input_file=data.get("Input_file", ""),
            user_input=data.get("User_input", ""),
            use_api=data.get("Use_api", False),
            api_key=data.get("Api_key"),
        )
    
    def to_yaml(self, path: str | Path) -> None:
        """Save configuration to a YAML file.
        
        Args:
            path: Path to save the YAML configuration file.
        """
        data = {
            "Output_dir": self.output_dir,
            "DEFAULT_MODEL": self.model_id,
            "MAX_RETRIES": self.max_retries,
            "Input_file": self.input_file,
            "User_input": self.user_input,
            "Use_api": self.use_api,
            "Api_key": self.api_key or "",
        }
        
        with open(path, 'w') as f:
            yaml.safe_dump(data, f, default_flow_style=False)


def read_config(file_path: str | Path) -> tuple:
    """Read configuration file and return values.
    
    This is a backward-compatible function that returns a tuple.
    For new code, use CoLLMConfig.from_yaml() instead.
    
    Args:
        file_path: Path to YAML configuration file.
        
    Returns:
        Tuple of (output_dir, model_id, max_retries, input_file, user_input, use_api, api_key).
    """
    config = CoLLMConfig.from_yaml(file_path)
    return (
        config.output_dir,
        config.model_id,
        config.max_retries,
        config.input_file,
        config.user_input,
        config.use_api,
        config.api_key,
    )
