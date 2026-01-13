# SPDX-License-Identifier: GPL-3.0-or-later
"""
Validation result data class.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    import bpy

from .severity import Severity


@dataclass
class ValidationResult:
    """
    Represents a single validation result.
    
    Attributes:
        checker_name: Name of the checker that produced this result
        severity: Severity level of the issue
        object_name: Name of the affected object
        message: Human-readable description of the issue
        details: Additional data (e.g., face indices, UV names)
        fix_hint: Optional suggestion for fixing the issue
    """
    checker_name: str
    severity: Severity
    object_name: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    fix_hint: Optional[str] = None
    
    def __post_init__(self):
        """Validate the result after initialization."""
        if not self.checker_name:
            raise ValueError("checker_name cannot be empty")
        if not self.message:
            raise ValueError("message cannot be empty")
    
    @property
    def is_error(self) -> bool:
        """Check if this result is an error."""
        return self.severity == Severity.ERROR
    
    @property
    def is_warning(self) -> bool:
        """Check if this result is a warning."""
        return self.severity == Severity.WARNING
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "checker_name": self.checker_name,
            "severity": self.severity.name,
            "object_name": self.object_name,
            "message": self.message,
            "details": self.details,
            "fix_hint": self.fix_hint,
        }
