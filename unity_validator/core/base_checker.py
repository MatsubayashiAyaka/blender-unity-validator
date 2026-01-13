# SPDX-License-Identifier: GPL-3.0-or-later

from abc import ABC, abstractmethod
from typing import List, Optional, Set, TYPE_CHECKING

if TYPE_CHECKING:
    import bpy

from .severity import Severity
from .result import ValidationResult


class BaseChecker(ABC):
    """
    Abstract base class for all validation checkers.
    
    Subclasses must implement the `check` method and define
    class attributes for name, description, and default_severity.
    
    Example:
        @register_checker
        class MyChecker(BaseChecker):
            name = "My Checker"
            description = "Checks for something"
            default_severity = Severity.WARNING
            
            def check(self, obj):
                results = []
                # ... validation logic ...
                return results
    """
    
    # Required class attributes (must be overridden)
    name: str = ""
    description: str = ""
    default_severity: Severity = Severity.WARNING
    
    # Optional attributes
    supported_types: Set[str] = {'MESH'}  # Object types this checker supports
    supports_exclusion: bool = True        # Can be excluded via custom property
    
    def __init__(self):
        """Initialize the checker."""
        if not self.name:
            raise ValueError(f"{self.__class__.__name__} must define 'name'")
        if not self.description:
            raise ValueError(f"{self.__class__.__name__} must define 'description'")
    
    @abstractmethod
    def check(self, obj: 'bpy.types.Object') -> List[ValidationResult]:
        """
        Perform validation on the given object.
        
        Args:
            obj: The Blender object to validate
            
        Returns:
            List of ValidationResult objects (empty if no issues found)
        """
        pass
    
    def is_supported(self, obj: 'bpy.types.Object') -> bool:
        """Check if this checker supports the given object type."""
        return obj.type in self.supported_types
    
    def is_excluded(self, obj: 'bpy.types.Object') -> bool:
        """
        Check if this checker is excluded for the given object.
        
        Uses custom property: unity_validator_exclude_{checker_id}
        """
        if not self.supports_exclusion:
            return False
        
        prop_name = f"unity_validator_exclude_{self.get_id()}"
        return obj.get(prop_name, False)
    
    def get_id(self) -> str:
        """
        Get unique identifier for this checker.
        
        Default: lowercase class name without 'Checker' suffix
        """
        class_name = self.__class__.__name__
        if class_name.endswith('Checker'):
            class_name = class_name[:-7]
        return class_name.lower()
    
    def create_result(
        self,
        obj: 'bpy.types.Object',
        message: str,
        severity: Optional[Severity] = None,
        details: Optional[dict] = None,
        fix_hint: Optional[str] = None
    ) -> ValidationResult:
        """
        Helper method to create a ValidationResult.
        
        Args:
            obj: The object with the issue
            message: Description of the issue
            severity: Override default severity (optional)
            details: Additional data (optional)
            fix_hint: Suggestion for fixing (optional)
            
        Returns:
            ValidationResult instance
        """
        return ValidationResult(
            checker_name=self.name,
            severity=severity or self.default_severity,
            object_name=obj.name,
            message=message,
            details=details or {},
            fix_hint=fix_hint
        )