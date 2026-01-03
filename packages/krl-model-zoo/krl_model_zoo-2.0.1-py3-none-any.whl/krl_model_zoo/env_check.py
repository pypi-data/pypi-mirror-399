"""
© 2025 KR-Labs. All rights reserved.
KR-Labs™ and KRL Model Zoo™ are trademarks of Deloatch, Williams, Faison, & Parker, LLLP

SPDX-License-Identifier: Apache-2.0
"""

import os
import sys
from pathlib import Path
import platform


def get_user_bin_directory():
    """
    Get the expected user bin directory for the current OS and Python version.
    
    Returns:
        Path: The user bin directory path
    """
    system = platform.system()
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    
    if system == "Darwin":  # macOS
        return Path.home() / "Library" / "Python" / py_version / "bin"
    elif system == "Windows":
        # Windows uses Scripts instead of bin
        return Path.home() / "AppData" / "Roaming" / "Python" / f"Python{sys.version_info.major}{sys.version_info.minor}" / "Scripts"
    else:  # Linux and others
        return Path.home() / ".local" / "bin"


def is_user_bin_in_path():
    """
    Check if the user bin directory is in the system PATH.
    
    Returns:
        tuple: (bool, Path) - Whether the directory is in PATH, and the directory path
    """
    user_bin = get_user_bin_directory()
    path_env = os.environ.get("PATH", "")
    return str(user_bin) in path_env, user_bin


def check_environment():
    """
    Check the Python environment and PATH configuration.
    
    Prints diagnostic information and recommendations if issues are found.
    """
    print("=" * 70)
    print("KRL Model Zoo - Environment Check")
    print("=" * 70)
    print()
    
    # Python version
    print(f"✓ Python Version: {sys.version.split()[0]}")
    print(f"✓ Python Executable: {sys.executable}")
    print()
    
    # Virtual environment check
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if in_venv:
        print("✓ Virtual Environment: Active")
        print(f"  Environment Path: {sys.prefix}")
        print("  → Scripts are automatically available in PATH")
    else:
        print("⚠ Virtual Environment: Not detected")
        print("  → Using system/user Python installation")
    
    print()
    
    # PATH check
    in_path, user_bin = is_user_bin_in_path()
    
    if in_venv:
        print("✓ PATH Configuration: Managed by virtual environment")
    elif in_path:
        print("✓ PATH Configuration: User bin directory is in PATH")
        print(f"  {user_bin}")
    else:
        print("⚠ PATH Configuration: User bin directory NOT in PATH")
        print(f"  Directory: {user_bin}")
        print()
        print("  This is NORMAL and usually not a problem!")
        print("  → KRL Model Zoo works perfectly via Python imports")
        print("  → Only matters if you need CLI tools from dependencies")
        print()
        print("  If you need to add it to PATH:")
        
        system = platform.system()
        if system == "Darwin":  # macOS
            shell = os.environ.get("SHELL", "")
            if "zsh" in shell:
                print(f"  echo 'export PATH=\"{user_bin}:$PATH\"' >> ~/.zshrc")
                print("  source ~/.zshrc")
            else:
                print(f"  echo 'export PATH=\"{user_bin}:$PATH\"' >> ~/.bash_profile")
                print("  source ~/.bash_profile")
        elif system == "Windows":
            print(f"  Add {user_bin} to System PATH via Control Panel")
        else:  # Linux
            print(f"  echo 'export PATH=\"{user_bin}:$PATH\"' >> ~/.bashrc")
            print("  source ~/.bashrc")
    
    print()
    
    # KRL Model Zoo check
    try:
        import krl_model_zoo
        print(f"✓ KRL Model Zoo: v{krl_model_zoo.__version__} installed")
        
        # Try importing models
        from krl_model_zoo import get_available_models
        models = get_available_models()
        print(f"✓ Available Models: {len(models)} models loaded")
        
    except ImportError as e:
        print(f"✗ KRL Model Zoo: Not installed or import error")
        print(f"  Error: {e}")
        print()
        print("  Install with: pip install krl-model-zoo")
    
    print()
    print("=" * 70)
    
    # Recommendations
    if not in_venv:
        print()
        print("💡 RECOMMENDATION:")
        print("   Use a virtual environment for better isolation:")
        print()
        print("   python3 -m venv krl-env")
        print("   source krl-env/bin/activate  # macOS/Linux")
        print("   krl-env\\Scripts\\activate     # Windows")
        print("   pip install krl-model-zoo")
        print()


def main():
    """Main entry point for the environment checker."""
    try:
        check_environment()
    except KeyboardInterrupt:
        print("\n\nCheck interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error during check: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
