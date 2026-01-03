"""
QuantumLock CLI - License Management Tool
==========================================

Protected build - core logic is compiled for security.

Version: 1.0.0
"""

__version__ = "1.0.0"

try:
    from .main import app, main
except ImportError as e:
    raise ImportError(
        "QuantumLock CLI compiled modules not found."
    ) from e

__all__ = ["app", "main", "__version__"]

if __name__ == "__main__":
    main()
