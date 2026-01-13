# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2024 MatsubayashiAyaka
"""
Normals and smoothing validation checker.

Checks for normal/smoothing issues:
- Auto Smooth not applied (Blender 3.6-4.0)
- Custom normals not present (Blender 4.1+)
- Inconsistent smooth/flat shading
"""

import bpy
from typing import List

from ..core import BaseChecker, ValidationResult, Severity, register_checker
from ..utils.compat import (
    is_blender_4_1_or_later,
    has_auto_smooth,
)


@register_checker
class NormalsChecker(BaseChecker):
    """
    Validates normals and smoothing for Unity compatibility.
    
    Checks vary by Blender version:
    
    Blender 3.6 - 4.0:
    - Auto Smooth enabled
    
    Blender 4.1+:
    - Custom normals present (equivalent to Auto Smooth applied)
    - Smooth by Angle modifier (optional)
    
    Also checks for mixed smooth/flat shading.
    """
    
    name = "Normals"
    description = "Check for smoothing and normal issues"
    default_severity = Severity.INFO
    
    # Configuration
    check_auto_smooth: bool = True
    check_mixed_shading: bool = True
    
    def check(self, obj: bpy.types.Object) -> List[ValidationResult]:
        """
        Perform normals validation on the object.
        
        Args:
            obj: The Blender object to validate
            
        Returns:
            List of ValidationResult for any issues found
        """
        results = []
        
        # Must be a mesh object
        if obj.type != 'MESH':
            return results
        
        mesh = obj.data
        
        # Skip if no polygons
        if not mesh.polygons:
            return results
        
        # Check auto smooth / custom normals
        if self.check_auto_smooth:
            smooth_result = self._check_smoothing(obj, mesh)
            if smooth_result:
                results.append(smooth_result)
        
        # Check for mixed smooth/flat shading
        if self.check_mixed_shading:
            mixed_result = self._check_mixed_shading(obj, mesh)
            if mixed_result:
                results.append(mixed_result)
        
        return results
    
    def _check_smoothing(
        self, 
        obj: bpy.types.Object, 
        mesh: bpy.types.Mesh
    ) -> ValidationResult | None:
        """
        Check if appropriate smoothing is applied.
        
        The check differs based on Blender version:
        - 3.6-4.0: Check mesh.use_auto_smooth
        - 4.1+: Check mesh.has_custom_normals
        """
        if is_blender_4_1_or_later():
            return self._check_smoothing_4_1(obj, mesh)
        else:
            return self._check_smoothing_legacy(obj, mesh)
    
    def _check_smoothing_legacy(
        self, 
        obj: bpy.types.Object, 
        mesh: bpy.types.Mesh
    ) -> ValidationResult | None:
        """Check smoothing for Blender 3.6 - 4.0."""
        # Check if use_auto_smooth exists and is False
        use_auto_smooth = getattr(mesh, 'use_auto_smooth', None)
        
        if use_auto_smooth is None:
            # Attribute doesn't exist (shouldn't happen in 3.6-4.0)
            return None
        
        if not use_auto_smooth:
            # Check if object uses smooth shading
            has_smooth = any(p.use_smooth for p in mesh.polygons)
            
            if has_smooth:
                return self.create_result(
                    obj=obj,
                    message="Auto Smooth is OFF but object uses smooth shading",
                    severity=Severity.INFO,
                    details={
                        "use_auto_smooth": False,
                        "has_smooth_faces": True,
                        "blender_version": "legacy",
                    },
                    fix_hint="Enable Auto Smooth: Object > Shade Auto Smooth"
                )
        
        return None
    
    def _check_smoothing_4_1(
        self, 
        obj: bpy.types.Object, 
        mesh: bpy.types.Mesh
    ) -> ValidationResult | None:
        """Check smoothing for Blender 4.1+."""
        has_custom = mesh.has_custom_normals
        
        # Check if there's a Smooth by Angle modifier
        has_modifier = self._has_smooth_by_angle_modifier(obj)
        
        if not has_custom and not has_modifier:
            # Check if object uses smooth shading
            has_smooth = any(p.use_smooth for p in mesh.polygons)
            
            if has_smooth:
                return self.create_result(
                    obj=obj,
                    message="No custom normals (Auto Smooth not applied)",
                    severity=Severity.INFO,
                    details={
                        "has_custom_normals": False,
                        "has_smooth_modifier": False,
                        "has_smooth_faces": True,
                        "blender_version": "4.1+",
                    },
                    fix_hint="Apply: Object > Shade Auto Smooth, or add Smooth by Angle modifier"
                )
        
        return None
    
    def _has_smooth_by_angle_modifier(self, obj: bpy.types.Object) -> bool:
        """Check if object has a Smooth by Angle modifier."""
        for mod in obj.modifiers:
            # In Blender 4.1+, this is a geometry nodes modifier
            # or a specific modifier type
            if mod.type == 'NODES':
                # Check if it's a smooth by angle node group
                if mod.node_group and 'smooth' in mod.node_group.name.lower():
                    return True
        return False
    
    def _check_mixed_shading(
        self, 
        obj: bpy.types.Object, 
        mesh: bpy.types.Mesh
    ) -> ValidationResult | None:
        """
        Check for mixed smooth/flat shading.
        
        While mixed shading can be intentional, it's worth
        flagging as it may cause unexpected results.
        """
        if not mesh.polygons:
            return None
        
        smooth_count = sum(1 for p in mesh.polygons if p.use_smooth)
        flat_count = len(mesh.polygons) - smooth_count
        
        # Only report if both exist (mixed)
        if smooth_count > 0 and flat_count > 0:
            total = len(mesh.polygons)
            smooth_ratio = smooth_count / total
            
            return self.create_result(
                obj=obj,
                message=f"Mixed shading: {smooth_count} smooth, {flat_count} flat faces",
                severity=Severity.INFO,
                details={
                    "smooth_faces": smooth_count,
                    "flat_faces": flat_count,
                    "total_faces": total,
                    "smooth_ratio": round(smooth_ratio, 3),
                },
                fix_hint="This may be intentional. To unify: Object > Shade Smooth/Flat"
            )
        
        return None
