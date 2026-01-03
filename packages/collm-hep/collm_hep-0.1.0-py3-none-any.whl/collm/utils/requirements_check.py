"""
Runtime Environment Checker for CoLLM
=====================================

Checks and ensures the correct runtime environment:
- NumPy version compatibility (requires < 2.0)
- PyTorch installation with GPU support (CUDA/MPS)
- macOS-specific PyTorch version handling

Note: Basic dependencies are handled by pip during installation.
This module handles runtime checks that can't be done at install time.
"""

from __future__ import annotations

import logging
import platform
import subprocess
import sys
from typing import Optional, Tuple

# Set up logger
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def _ensure_compatible_numpy() -> bool:
    """Check NumPy version and downgrade if 2.x is installed.
    
    NumPy 2.x has breaking changes that cause compatibility issues with
    packages compiled against NumPy 1.x (like PyTorch and transformers).
    
    Returns:
        True if restart is needed, False otherwise.
    """
    try:
        result = subprocess.run(
            [sys.executable, "-c", "import numpy; print(numpy.__version__)"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            major_version = int(version.split(".")[0])
            
            if major_version >= 2:
                logger.warning(f"NumPy {version} detected. Downgrading to NumPy<2 for compatibility...")
                try:
                    subprocess.check_call([
                        sys.executable, "-m", "pip", "install", "numpy<2",
                        "--force-reinstall", "--quiet"
                    ], stdout=subprocess.DEVNULL)
                    logger.info("Successfully downgraded NumPy")
                    logger.warning("=" * 50)
                    logger.warning("NumPy was downgraded. Please RESTART Python!")
                    logger.warning(" Run your script again after restarting.")
                    logger.warning("=" * 50)
                    return True
                except subprocess.CalledProcessError as e:
                    logger.error(f"Failed to downgrade NumPy: {e}")
                    raise
    except FileNotFoundError:
        pass  # NumPy not installed yet
    except Exception:
        pass  # Ignore other errors
    
    return False


def _get_macos_version() -> Tuple[Optional[int], Optional[int]]:
    """Get macOS major and minor version numbers.
    
    Returns:
        Tuple of (major, minor) version numbers, or (None, None) if not macOS.
    """
    mac_ver = platform.mac_ver()[0]
    if mac_ver:
        parts = mac_ver.split(".")
        major = int(parts[0])
        minor = int(parts[1]) if len(parts) > 1 else 0
        return major, minor
    return None, None


def _get_pytorch_version_for_macos() -> Optional[dict]:
    """Determine the appropriate PyTorch version based on macOS version.
    
    Returns:
        Dictionary with torch, torchvision, torchaudio versions, or None for latest.
    """
    system = platform.system()
    if system != "Darwin":
        return None  # Not macOS, use latest
    
    major, minor = _get_macos_version()
    if major is None:
        return None  # Can't determine version, use latest
    
    # PyTorch version requirements for MPS:
    # - PyTorch 2.4+ requires macOS 14.0+ (Sonoma)
    # - PyTorch 2.2.x - 2.3.x supports macOS 12.3+ (Monterey/Ventura)
    
    if major >= 14:
        return None  # Use latest PyTorch
    elif major == 13 or (major == 12 and minor >= 3):
        # macOS 12.3 - 13.x: Use PyTorch 2.2.2
        return {
            "torch": "torch==2.2.2",
            "torchvision": "torchvision==0.17.2",
            "torchaudio": "torchaudio==2.2.2"
        }
    elif major == 12 and minor < 3:
        logger.warning("macOS 12.3+ required for MPS support")
        return None
    else:
        logger.warning(f"macOS {major}.{minor} is too old for MPS support")
        return None


def _get_installed_torch_version() -> Optional[str]:
    """Get installed torch version without importing torch.
    
    Returns:
        Version string or None if not installed.
    """
    try:
        result = subprocess.run(
            [sys.executable, "-c", "import torch; print(torch.__version__)"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def _check_mps_available() -> Tuple[bool, bool]:
    """Check if MPS is available without keeping torch imported.
    
    Returns:
        Tuple of (mps_built, mps_available).
    """
    try:
        result = subprocess.run(
            [sys.executable, "-c", 
             "import torch; print(torch.backends.mps.is_built(), torch.backends.mps.is_available())"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            parts = result.stdout.strip().split()
            mps_built = parts[0] == "True"
            mps_available = parts[1] == "True"
            return mps_built, mps_available
    except Exception:
        pass
    return False, False


def _check_cuda_available() -> Tuple[bool, str]:
    """Check if CUDA is available.
    
    Returns:
        Tuple of (cuda_available, device_name).
    """
    try:
        result = subprocess.run(
            [sys.executable, "-c", 
             "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else '')"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            parts = result.stdout.strip().split(maxsplit=1)
            cuda_available = parts[0] == "True"
            device_name = parts[1] if len(parts) > 1 else ""
            return cuda_available, device_name
    except Exception:
        pass
    return False, ""


def _install_pytorch(reason: str, version_dict: Optional[dict] = None) -> bool:
    """Install or reinstall PyTorch.
    
    Args:
        reason: Reason for installation (for logging).
        version_dict: Specific versions to install, or None for latest.
        
    Returns:
        True if successful.
    """
    logger.warning(f"Installing PyTorch ({reason})...")
    
    system = platform.system()
    
    try:
        # Uninstall existing torch first to avoid conflicts
        subprocess.check_call([
            sys.executable, "-m", "pip", "uninstall", "-y",
            "torch", "torchvision", "torchaudio"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        pass  # May not be installed
    
    try:
        if system == "Darwin":  # macOS
            if version_dict:
                # Install specific versions for older macOS
                major, minor = _get_macos_version()
                logger.info(f"Installing PyTorch {version_dict['torch']} for macOS {major}.{minor}")
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install",
                    version_dict["torch"],
                    version_dict["torchvision"],
                    version_dict["torchaudio"]
                ], stdout=subprocess.DEVNULL)
            else:
                # Install latest for macOS 14+
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install",
                    "torch", "torchvision", "torchaudio"
                ], stdout=subprocess.DEVNULL)
            logger.info("Successfully installed PyTorch for macOS")
            
        elif system == "Linux":
            # For Linux with CUDA support
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                "torch", "torchvision", "torchaudio",
                "--index-url", "https://download.pytorch.org/whl/cu121"
            ], stdout=subprocess.DEVNULL)
            logger.info("Successfully installed PyTorch with CUDA support")
            
        else:  # Windows or other
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                "torch", "torchvision", "torchaudio"
            ], stdout=subprocess.DEVNULL)
            logger.info("Successfully installed PyTorch")
        
        return True
            
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install PyTorch: {e}")
        raise


def _is_pytorch_too_new(version: str) -> bool:
    """Check if PyTorch version requires macOS 14+.
    
    Args:
        version: PyTorch version string.
        
    Returns:
        True if version requires macOS 14+.
    """
    try:
        parts = version.split(".")
        major = int(parts[0])
        minor = int(parts[1])
        # PyTorch 2.4+ requires macOS 14+
        return major >= 2 and minor >= 4
    except Exception:
        return False


def _print_mps_diagnostics() -> None:
    """Print diagnostic information for MPS issues."""
    installed_version = _get_installed_torch_version()
    mps_built, mps_available = _check_mps_available()
    
    logger.info("=" * 40)
    logger.info("MPS Diagnostics")
    logger.info("=" * 40)
    logger.info(f"macOS version: {platform.mac_ver()[0]}")
    logger.info(f"Chip: {platform.processor()}")
    logger.info(f"Architecture: {platform.machine()}")
    logger.info(f"PyTorch version: {installed_version}")
    logger.info(f"MPS built: {mps_built}")
    logger.info(f"MPS available: {mps_available}")
    logger.info("=" * 40)
    
    major, minor = _get_macos_version()
    
    if major is not None:
        if major < 12 or (major == 12 and minor < 3):
            logger.error("macOS 12.3+ required for MPS. Please upgrade macOS.")
        elif major < 14:
            logger.info(f"macOS {major}.{minor} detected. Requires PyTorch 2.2.x - 2.3.x for MPS.")
            logger.info("For latest PyTorch, upgrade to macOS 14.0+ (Sonoma)")
    
    if platform.machine() != "arm64":
        logger.warning("MPS works best on Apple Silicon (M1/M2/M3/M4)")


def _ensure_pytorch() -> bool:
    """Install PyTorch with proper GPU support (CUDA or MPS).
    
    Returns:
        True if restart is needed, False otherwise.
    """
    system = platform.system()
    machine = platform.machine()
    
    # Get appropriate PyTorch version for macOS
    pytorch_versions = _get_pytorch_version_for_macos()
    
    # Check if torch is installed (without importing)
    installed_version = _get_installed_torch_version()
    pytorch_reinstalled = False
    
    if installed_version is None:
        # Not installed
        _install_pytorch("not installed", pytorch_versions)
        pytorch_reinstalled = True
        installed_version = _get_installed_torch_version()
    
    logger.info(f"PyTorch {installed_version} installed")
    
    # Check MPS/CUDA support
    if system == "Darwin" and machine == "arm64":
        # Apple Silicon Mac - should have MPS
        major, minor = _get_macos_version()
        mps_built, mps_available = _check_mps_available()
        
        if not mps_built:
            logger.warning("PyTorch installed without MPS support, reinstalling...")
            _install_pytorch("MPS not built", pytorch_versions)
            pytorch_reinstalled = True
            mps_built, mps_available = _check_mps_available()
            
        elif not mps_available and major is not None and major < 14:
            # MPS is built but not available - likely version mismatch
            if installed_version and _is_pytorch_too_new(installed_version):
                logger.warning(f"PyTorch {installed_version} requires macOS 14+, but you have macOS {major}.{minor}")
                logger.warning("Downgrading to compatible PyTorch version...")
                _install_pytorch("macOS version compatibility", pytorch_versions)
                pytorch_reinstalled = True
                mps_built, mps_available = _check_mps_available()
        
        # Final status check
        if mps_available:
            logger.info("MPS support available")
        elif mps_built:
            logger.warning("MPS built but not available")
            _print_mps_diagnostics()
        else:
            logger.warning("MPS not available")
            _print_mps_diagnostics()
        
        # If we reinstalled, warn user about restart
        if pytorch_reinstalled:
            logger.warning("=" * 50)
            logger.warning("PyTorch was reinstalled. Please RESTART Python!")
            logger.warning(" Run your script again after restarting.")
            logger.warning("=" * 50)
            return True
                
    elif system == "Linux" or (system == "Darwin" and machine == "x86_64"):
        # Linux or Intel Mac - check for CUDA
        cuda_available, device_name = _check_cuda_available()
        if cuda_available:
            logger.info(f"CUDA support available ({device_name})")
        else:
            logger.info("CUDA not available, using CPU")
    
    return False


def ensure_packages(exit_on_restart: bool = True) -> bool:
    """Ensure all required packages are properly installed and configured.
    
    This function checks:
    1. NumPy version (must be < 2.0)
    2. PyTorch with GPU support (CUDA/MPS)
    
    Args:
        exit_on_restart: If True, exit the process when restart is needed.
        
    Returns:
        True if restart is needed, False if ready to use.
        
    Note:
        Basic package dependencies are handled by pip during installation.
        This function handles runtime environment checks.
    """
    restart_needed = False
    
    # First, check if NumPy 2.x is installed and downgrade if needed
    # This must happen before importing packages that depend on NumPy
    if _ensure_compatible_numpy():
        restart_needed = True
    
    # Ensure PyTorch is properly installed with GPU support
    if _ensure_pytorch():
        restart_needed = True
    
    if restart_needed and exit_on_restart:
        sys.exit(0)
    
    return restart_needed


def check_environment() -> dict:
    """Check and report the current environment status.
    
    Returns:
        Dictionary with environment information.
    """
    info = {
        "python_version": sys.version,
        "platform": platform.system(),
        "machine": platform.machine(),
        "numpy_version": None,
        "torch_version": None,
        "cuda_available": False,
        "cuda_device": None,
        "mps_available": False,
    }
    
    # Check NumPy
    try:
        result = subprocess.run(
            [sys.executable, "-c", "import numpy; print(numpy.__version__)"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            info["numpy_version"] = result.stdout.strip()
    except Exception:
        pass
    
    # Check PyTorch
    info["torch_version"] = _get_installed_torch_version()
    
    # Check CUDA
    cuda_available, device_name = _check_cuda_available()
    info["cuda_available"] = cuda_available
    info["cuda_device"] = device_name if cuda_available else None
    
    # Check MPS
    _, mps_available = _check_mps_available()
    info["mps_available"] = mps_available
    
    return info


def print_environment_report() -> None:
    """Print a formatted environment report."""
    info = check_environment()
    
    print("=" * 50)
    print("CoLLM Environment Report")
    print("=" * 50)
    print(f"Python: {info['python_version'].split()[0]}")
    print(f"Platform: {info['platform']} ({info['machine']})")
    print(f"NumPy: {info['numpy_version'] or 'Not installed'}")
    print(f"PyTorch: {info['torch_version'] or 'Not installed'}")
    print("-" * 50)
    print("GPU Support:")
    if info['cuda_available']:
        print(f"  CUDA: ✓ Available ({info['cuda_device']})")
    else:
        print("  CUDA: ✗ Not available")
    if info['mps_available']:
        print("  MPS: ✓ Available (Apple Silicon)")
    else:
        print("  MPS: ✗ Not available")
    print("=" * 50)
