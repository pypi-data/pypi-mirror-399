"""
QuantumLock CLI - License Management Tool
==========================================

Protected build - core logic is compiled for security.

Version: 1.0.4
Copyright (c) 2026 SoftQuantus
"""

__version__ = "1.0.4"
__author__ = "SoftQuantus"

# Import from compiled modules
try:
    from .main import app, main
except ImportError as e:
    raise ImportError(
        "QuantumLock CLI compiled modules not found. "
        "Please ensure the package is installed correctly."
    ) from e

__all__ = ["app", "main", "__version__"]

if __name__ == "__main__":
    main()
