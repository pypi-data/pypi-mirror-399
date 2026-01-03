"""
MacAgent Core - Free, open-source AI orchestration for macOS

MIT Licensed. Your data never leaves your Mac.
"""

__version__ = "1.2.0"
__author__ = "Dallas McMillan"

from .cli import main
from .audit import AuditLog
from .hardware import get_system_status

__all__ = ["main", "AuditLog", "get_system_status", "__version__"]
