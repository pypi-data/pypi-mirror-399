"""
Thai DRG Grouper
================
Thai DRG (Diagnosis Related Group) Grouper for Linux/Mac/Windows

Supports multiple versions of Thai DRG and easy updates.

Repository: https://github.com/aegisx-platform/thai-drg-grouper
License: MIT

Usage:
    from thai_drg_grouper import ThaiDRGGrouperManager

    manager = ThaiDRGGrouperManager('./data/versions')
    result = manager.group_latest(pdx='S82201D', los=5)
    print(f"DRG: {result.drg}, RW: {result.rw}")
"""

__version__ = "2.0.0"
__author__ = "AegisX Platform"
__license__ = "MIT"

from .grouper import ThaiDRGGrouper
from .manager import ThaiDRGGrouperManager
from .types import GrouperResult, VersionInfo

__all__ = [
    "ThaiDRGGrouper",
    "ThaiDRGGrouperManager",
    "GrouperResult",
    "VersionInfo",
    "__version__",
]
