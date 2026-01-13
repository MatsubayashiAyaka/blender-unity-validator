# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2024 MatsubayashiAyaka
"""
Naming validation checker.

Checks for naming issues that cause problems in Unity:
- Spaces in object names
- Japanese/non-ASCII characters
- Default Blender names (Cube.001, Sphere.002, etc.)
- Special characters that are invalid on some filesystems
"""

import bpy
import re
from typing import List, Set

from ..core import BaseChecker, ValidationResult, Severity, register_checker


# Default Blender primitive names (patterns)
DEFAULT_NAME_PATTERNS = [
    r'^Cube(\.\d+)?$',
    r'^Sphere(\.\d+)?$',
    r'^Cylinder(\.\d+)?$',
    r'^Plane(\.\d+)?$',
    r'^Cone(\.\d+)?$',
    r'^Torus(\.\d+)?$',
    r'^Circle(\.\d+)?$',
    r'^Grid(\.\d+)?$',
    r'^Monkey(\.\d+)?$',
    r'^Suzanne(\.\d+)?$',
    r'^Icosphere(\.\d+)?$',
    r'^UV Sphere(\.\d+)?$',
    r'^Empty(\.\d+)?$',
    r'^Camera(\.\d+)?$',
    r'^Light(\.\d+)?$',
    r'^Point(\.\d+)?$',
    r'^Sun(\.\d+)?$',
    r'^Spot(\.\d+)?$',
    r'^Area(\.\d+)?$',
]

# Characters that are problematic for file systems or Unity
INVALID_CHARACTERS = set('/\\:*?"<>|')

# Windows reserved names
WINDOWS_RESERVED = {
    'CON', 'PRN', 'AUX', 'NUL',
    'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
    'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9',
}


@register_checker
class NamingChecker(BaseChecker):
    """
    Validates object names for Unity compatibility.
    
    Checks:
    - No spaces in names
    - No Japanese/non-ASCII characters
    - Not a default Blender name (Cube.001, etc.)
    - No invalid filesystem characters
    - Not a Windows reserved name
    """
    
    name = "Naming"
    description = "Check for problematic object names"
    default_severity = Severity.INFO
    
    # Configuration options
    check_spaces: bool = True
    check_non_ascii: bool = True
    check_default_names: bool = True
    check_invalid_chars: bool = True
    check_reserved_names: bool = True
    check_starts_with_number: bool = True
    
    def check(self, obj: bpy.types.Object) -> List[ValidationResult]:
        """
        Perform naming validation on the object.
        
        Args:
            obj: The Blender object to validate
            
        Returns:
            List of ValidationResult for any issues found
        """
        results = []
        name = obj.name
        
        # Check for spaces
        if self.check_spaces and ' ' in name:
            results.append(self.create_result(
                obj=obj,
                message=f"Name contains spaces",
                severity=Severity.INFO,
                details={"name": name, "issue": "spaces"},
                fix_hint="Replace spaces with underscores: 'My Object' → 'My_Object'"
            ))
        
        # Check for non-ASCII (Japanese, etc.)
        if self.check_non_ascii:
            non_ascii = self._find_non_ascii(name)
            if non_ascii:
                results.append(self.create_result(
                    obj=obj,
                    message=f"Name contains non-ASCII characters",
                    severity=Severity.WARNING,
                    details={
                        "name": name,
                        "issue": "non_ascii",
                        "non_ascii_chars": list(non_ascii),
                    },
                    fix_hint="Use only ASCII characters (A-Z, a-z, 0-9, _)"
                ))
        
        # Check for default Blender names
        if self.check_default_names and self._is_default_name(name):
            results.append(self.create_result(
                obj=obj,
                message=f"Default Blender name",
                severity=Severity.INFO,
                details={"name": name, "issue": "default_name"},
                fix_hint="Rename to something descriptive"
            ))
        
        # Check for invalid characters
        if self.check_invalid_chars:
            invalid = self._find_invalid_chars(name)
            if invalid:
                results.append(self.create_result(
                    obj=obj,
                    message=f"Name contains invalid characters: {', '.join(invalid)}",
                    severity=Severity.WARNING,
                    details={
                        "name": name,
                        "issue": "invalid_chars",
                        "invalid_chars": list(invalid),
                    },
                    fix_hint="Remove or replace invalid characters"
                ))
        
        # Check for Windows reserved names
        if self.check_reserved_names:
            base_name = name.split('.')[0].upper()
            if base_name in WINDOWS_RESERVED:
                results.append(self.create_result(
                    obj=obj,
                    message=f"Name is a Windows reserved word",
                    severity=Severity.WARNING,
                    details={
                        "name": name,
                        "issue": "reserved_name",
                        "reserved_word": base_name,
                    },
                    fix_hint="Use a different name"
                ))
        
        # Check for names starting with a number
        if self.check_starts_with_number and name and name[0].isdigit():
            results.append(self.create_result(
                obj=obj,
                message=f"Name starts with a number",
                severity=Severity.INFO,
                details={"name": name, "issue": "starts_with_number"},
                fix_hint="Start names with a letter or underscore"
            ))
        
        return results
    
    def _find_non_ascii(self, name: str) -> Set[str]:
        """Find non-ASCII characters in the name."""
        non_ascii = set()
        for char in name:
            if ord(char) > 127:
                non_ascii.add(char)
        return non_ascii
    
    def _is_default_name(self, name: str) -> bool:
        """Check if name matches a default Blender primitive name."""
        for pattern in DEFAULT_NAME_PATTERNS:
            if re.match(pattern, name, re.IGNORECASE):
                return True
        return False
    
    def _find_invalid_chars(self, name: str) -> Set[str]:
        """Find filesystem-invalid characters in the name."""
        return set(name) & INVALID_CHARACTERS
