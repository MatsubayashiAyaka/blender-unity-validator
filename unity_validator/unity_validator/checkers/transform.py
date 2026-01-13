# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2024 MatsubayashiAyaka
"""
Transform validation checker.

Checks for common transform issues that cause problems in Unity:
- Unapplied scale (not 1,1,1)
- Unapplied rotation (not 0,0,0)
- Negative scale values (causes inverted normals in Unity)
"""

import bpy
from typing import List
from mathutils import Vector, Euler

from ..core import BaseChecker, ValidationResult, Severity, register_checker


# Tolerance for floating point comparison
FLOAT_TOLERANCE = 1e-6


def is_nearly_equal(a: float, b: float, tolerance: float = FLOAT_TOLERANCE) -> bool:
    """Check if two floats are nearly equal within tolerance."""
    return abs(a - b) < tolerance


def is_vector_nearly_equal(
    vec: Vector, 
    target: tuple, 
    tolerance: float = FLOAT_TOLERANCE
) -> bool:
    """Check if a vector is nearly equal to target values."""
    return all(is_nearly_equal(v, t, tolerance) for v, t in zip(vec, target))


@register_checker
class TransformChecker(BaseChecker):
    """
    Validates object transforms for Unity compatibility.
    
    Checks:
    - Scale should be (1, 1, 1) - unapplied scale causes issues
    - Rotation should be (0, 0, 0) - optional, can be excluded
    - No negative scale values - causes normal inversion in Unity
    """
    
    name = "Transform"
    description = "Check for unapplied transforms and negative scale"
    default_severity = Severity.WARNING
    
    # Configuration options
    check_scale: bool = True
    check_rotation: bool = True
    check_negative_scale: bool = True
    
    def check(self, obj: bpy.types.Object) -> List[ValidationResult]:
        """
        Perform transform validation on the object.
        
        Args:
            obj: The Blender object to validate
            
        Returns:
            List of ValidationResult for any issues found
        """
        results = []
        
        # Check for negative scale (most critical - causes normal issues)
        if self.check_negative_scale:
            negative_result = self._check_negative_scale(obj)
            if negative_result:
                results.append(negative_result)
        
        # Check for unapplied scale
        if self.check_scale:
            scale_result = self._check_unapplied_scale(obj)
            if scale_result:
                results.append(scale_result)
        
        # Check for unapplied rotation
        if self.check_rotation:
            rotation_result = self._check_unapplied_rotation(obj)
            if rotation_result:
                results.append(rotation_result)
        
        return results
    
    def _check_negative_scale(self, obj: bpy.types.Object) -> ValidationResult | None:
        """
        Check for negative scale values.
        
        Negative scale causes normals to be inverted in Unity,
        leading to incorrect lighting and invisible faces.
        """
        scale = obj.scale
        negative_axes = []
        
        if scale.x < 0:
            negative_axes.append('X')
        if scale.y < 0:
            negative_axes.append('Y')
        if scale.z < 0:
            negative_axes.append('Z')
        
        if negative_axes:
            # Count negative axes for severity
            # Odd number of negative axes = inverted normals
            is_inverted = len(negative_axes) % 2 == 1
            
            return self.create_result(
                obj=obj,
                message=f"Negative scale on {', '.join(negative_axes)} axis",
                severity=Severity.ERROR,  # Elevated to ERROR
                details={
                    "scale": tuple(scale),
                    "negative_axes": negative_axes,
                    "normals_inverted": is_inverted,
                },
                fix_hint="Apply scale with Ctrl+A > Scale, or use Object > Apply > Scale"
            )
        
        return None
    
    def _check_unapplied_scale(self, obj: bpy.types.Object) -> ValidationResult | None:
        """
        Check if scale is not applied (not 1,1,1).
        
        Unapplied scale can cause unexpected behavior in Unity,
        especially with physics and colliders.
        """
        scale = obj.scale
        
        if not is_vector_nearly_equal(scale, (1.0, 1.0, 1.0)):
            return self.create_result(
                obj=obj,
                message=f"Unapplied scale: ({scale.x:.3f}, {scale.y:.3f}, {scale.z:.3f})",
                severity=Severity.WARNING,
                details={
                    "scale": tuple(scale),
                    "expected": (1.0, 1.0, 1.0),
                },
                fix_hint="Apply scale with Ctrl+A > Scale"
            )
        
        return None
    
    def _check_unapplied_rotation(self, obj: bpy.types.Object) -> ValidationResult | None:
        """
        Check if rotation is not applied (not 0,0,0).
        
        Note: This check is optional as some workflows intentionally
        keep rotation values. The severity is INFO by default.
        """
        rotation = obj.rotation_euler
        
        if not is_vector_nearly_equal(rotation, (0.0, 0.0, 0.0)):
            # Convert to degrees for display
            rot_degrees = tuple(round(r * 57.2958, 2) for r in rotation)
            
            return self.create_result(
                obj=obj,
                message=f"Unapplied rotation: ({rot_degrees[0]}°, {rot_degrees[1]}°, {rot_degrees[2]}°)",
                severity=Severity.INFO,  # Lower severity as this is often intentional
                details={
                    "rotation_euler": tuple(rotation),
                    "rotation_degrees": rot_degrees,
                    "expected": (0.0, 0.0, 0.0),
                },
                fix_hint="Apply rotation with Ctrl+A > Rotation (if needed)"
            )
        
        return None
