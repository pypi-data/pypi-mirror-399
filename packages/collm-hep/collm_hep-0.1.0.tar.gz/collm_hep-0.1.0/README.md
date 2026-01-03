# CoLLM

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/collm-hep.svg)](https://badge.fury.io/py/collm-hep)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**An Automated, End-to-End Deep Learning Toolbox for Collider Physics Analysis**

CoLLM (Collider LLM) is an intelligent code generation tool that automates the creation of executable Python analysis scripts for **LHCO (Les Houches Collider Olympics)** files produced by fast detector simulations like Delphes. Simply describe your physics analysis in natural language, and CoLLM generates validated, runnable code.

## ✨ Key Features

- **🤖 LLM-Powered Code Generation** — Leverages state-of-the-art code models (Qwen, DeepSeek) to generate physics analysis code
- **🔄 Automatic Error Correction** — Self-healing code with automatic bug detection and fixing
- **🖥️ Dual Interface** — Choose between Terminal UI (TUI) or Streamlit-based Graphical UI (GUI)
- **⚡ GPU Acceleration** — Full support for CUDA (NVIDIA) and MPS (Apple Silicon)
- **📊 Built-in Validation** — Syntax checking and pattern validation before execution
- **🔌 API Support** — Use local models or HuggingFace Inference API

## 📦 Installation

```bash
pip install collm-hep
```

This installs everything you need, including the GUI.

## 🚀 Quick Start

### Python API

```python
from collm import generate_lhco_code

# Using local model
code = generate_lhco_code(
    user_input_path="user_input.txt",
    output_path="generated_analysis.py",
    model_id="Qwen/Qwen2.5-Coder-14B-Instruct"
)

# Using HuggingFace API
code = generate_lhco_code(
    user_input_path="user_input.txt",
    output_path="generated_analysis.py",
    model_id="Qwen/Qwen2.5-Coder-14B-Instruct",
    use_api=True,
    api_key="your_hf_api_key"
)
```

### Command Line

```bash
# Generate code from input file
collm --input user_input.txt --output analysis.py

# Use HuggingFace API
collm --input user_input.txt --output analysis.py --api --api-key YOUR_KEY

# Run with configuration file
collm --config config.yml

# Launch GUI
collm --gui
```

### User Input Format

Create a user input file with three sections:

```text
[SELECTION_CUTS]
- Select electrons with pT > 10 GeV and |eta| < 2.5
- Select muons with pT > 10 GeV and |eta| < 2.4
- Require at least two leptons
- Require at least two jets

[PLOTS_FOR_VALIDATION]
- Plot the missing energy distribution
- Plot the invariant mass of leading and subleading leptons
- Normalize all histograms to one

[OUTPUT_STRUCTURE]
- Save the produced histograms into png with dpi=150
- Print summary statistics
- Print the number of events before and after selection cuts
```

## ⚙️ Configuration

Create a YAML configuration file for batch processing:

```yaml
Output_dir: "./output/"
DEFAULT_MODEL: "Qwen/Qwen2.5-Coder-14B-Instruct"
MAX_RETRIES: 3
Input_file: "./data/signal.lhco"
User_input: "./templates/user_input.txt"
Use_api: False
Api_key: "your_huggingface_api_key"
```

## 🤖 Supported Models

| Model | Size | VRAM | Quality |
|-------|------|------|---------|
| `Qwen/Qwen2.5-Coder-32B-Instruct` | 32B | ~48GB | ⭐⭐⭐⭐⭐ |
| `deepseek-ai/DeepSeek-Coder-V2-Instruct` | 236B | ~40GB | ⭐⭐⭐⭐⭐ |
| `Qwen/Qwen2.5-Coder-14B-Instruct` | 14B | ~20GB | ⭐⭐⭐⭐ |
| `deepseek-ai/deepseek-coder-6.7b-instruct` | 6.7B | ~10GB | ⭐⭐⭐⭐ |
| `Qwen/Qwen2.5-Coder-7B-Instruct` | 7B | ~10GB | ⭐⭐⭐ |

## 📚 LHCO File Format Reference

| Column | Field | Description |
|--------|-------|-------------|
| 1 | `index` | Object index (0 = event header) |
| 2 | `type` | Particle type code |
| 3 | `eta` | Pseudorapidity |
| 4 | `phi` | Azimuthal angle (radians) |
| 5 | `pt` | Transverse momentum (GeV) |
| 6 | `jmass` | Jet mass (GeV) |
| 7 | `ntrk` | Track count (sign = charge) |
| 8 | `btag` | B-tag flag (1.0 = b-tagged) |
| 9 | `had/em` | Hadronic/EM energy ratio |

**Particle Type Codes:**
- `0` = Photon
- `1` = Electron
- `2` = Muon
- `3` = Tau
- `4` = Jet
- `6` = MET

## 🔧 API Reference

### Main Functions

```python
from collm import generate_lhco_code, fix_code

# Generate LHCO analysis code
code = generate_lhco_code(
    output_path: str,
    model_id: str = "Qwen/Qwen2.5-Coder-14B-Instruct",
    user_input_path: Optional[str] = None,
    user_input_text: Optional[str] = None,
    system_prompt_path: Optional[str] = None,
    use_api: bool = False,
    api_key: Optional[str] = None
) -> Optional[str]

# Fix buggy code
fixed_code = fix_code(
    code: str,
    error: str,
    model_id: str = "Qwen/Qwen2.5-Coder-14B-Instruct",
    use_api: bool = False,
    api_key: Optional[str] = None
) -> str
```

### Configuration Class

```python
from collm.utils.config import CoLLMConfig

# Load from YAML
config = CoLLMConfig.from_yaml("config.yml")

# Access configuration
print(config.model_id)
print(config.output_dir)

# Save to YAML
config.to_yaml("new_config.yml")
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📖 Citation

If you use CoLLM in your research, please cite:

```bibtex
@software{collm2025,
  title = {CoLLM: An Automated Deep Learning Toolbox for Collider Physics Analysis},
  year = {2025},
  url = {https://github.com/yourusername/CoLLM}
}
```
