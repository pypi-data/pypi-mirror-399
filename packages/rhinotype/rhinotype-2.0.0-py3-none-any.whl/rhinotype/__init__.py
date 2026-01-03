from importlib import metadata as _metadata

"""
rhinotype package top-level.

Provides a robust way to expose the package version without importing
submodules at package import time.
"""

def _get_version():
    try:
        return _metadata.version("rhinotype")
    except Exception:
        # Fall back to a safe default if package metadata isn't available
        return "0.0.0"

__all__ = ["__version__"]
__version__ = _get_version()

# Clean up names from the package namespace
del _get_version, _metadata
