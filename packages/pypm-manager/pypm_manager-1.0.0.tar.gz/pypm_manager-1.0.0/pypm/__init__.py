"""
PyPM - Python Package Manager
A package manager that centralizes package storage and uses environment-specific manifests
"""

__version__ = "1.0.0"
__author__ = "PyPM Contributors"
__description__ = "Efficient Python package manager with centralized storage"
__url__ = "https://github.com/yourusername/pypm"

from .central_store import CentralPackageStore
from .environment_manager import EnvironmentManager
from .package_loader import PackageLoader

__all__ = [
    'CentralPackageStore',
    'EnvironmentManager',
    'PackageLoader',
    '__version__',
]
