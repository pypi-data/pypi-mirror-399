"""
PyPM - Python Package Manager
Works like venv + pip but with centralized package storage (zero duplication)
"""

__version__ = "2.0.3"
__author__ = "Avishek"
__description__ = "Python package manager with centralized storage and zero duplication"
__url__ = "https://github.com/Avishek8136/pypm"

from .central_store import CentralPackageStore
from .environment_manager import EnvironmentManager

__all__ = [
    'CentralPackageStore',
    'EnvironmentManager',
    '__version__',
]
