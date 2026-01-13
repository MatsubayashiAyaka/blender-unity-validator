# SPDX-License-Identifier: GPL-3.0-or-later
"""
Core module for Unity Validator.

Contains base classes, registry, and common utilities.
"""

from .severity import Severity
from .result import ValidationResult
from .base_checker import BaseChecker
from .registry import CheckerRegistry, register_checker

__all__ = [
    "Severity",
    "ValidationResult",
    "BaseChecker",
    "CheckerRegistry",
    "register_checker",
]


def register():
    """Register core module."""
    pass


def unregister():
    """Unregister core module."""
    CheckerRegistry.clear()
