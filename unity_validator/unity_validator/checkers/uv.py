# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2024 MatsubayashiAyaka
"""
UV validation checker.

Checks for UV issues that cause problems in Unity:
- No UV map exists
- UV map exists but has no data
"""

import bpy
from typing import List

from ..core import BaseChecker, ValidationResult, Severity, register_checker


@register_checker
class UVChecker(BaseChecker):
    """
    Validates UV maps for Unity compatibility.
    
    Checks:
    - Object has at least one UV map
    - UV map contains valid data
    
    Missing UVs cause textures to not display correctly in Unity.
    """
    
    name = "UV Map"
    description = "Check for missing or invalid UV maps"
    default_severity = Severity.ERROR
    
    # Optional: Check for UV2 (lightmap UVs)
    check_uv2: bool = False
    
    def check(self, obj: bpy.types.Object) -> List[ValidationResult]:
        """
        Perform UV validation on the object.
        
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
        
        # Check if mesh has any UV maps
        if not mesh.uv_layers:
            results.append(self.create_result(
                obj=obj,
                message="No UV map found",
                severity=Severity.ERROR,
                details={
                    "uv_layer_count": 0,
                    "has_polygons": len(mesh.polygons) > 0,
                },
                fix_hint="Add a UV map: Edit Mode > UV > Unwrap (U key)"
            ))
            return results
        
        # Check active UV layer
        active_uv = mesh.uv_layers.active
        if active_uv is None:
            results.append(self.create_result(
                obj=obj,
                message="No active UV map",
                severity=Severity.WARNING,
                details={
                    "uv_layer_count": len(mesh.uv_layers),
                    "uv_layer_names": [uv.name for uv in mesh.uv_layers],
                },
                fix_hint="Set an active UV map in Object Data Properties > UV Maps"
            ))
        
        # Check if UV data is valid (has data for all loops)
        uv_validity = self._check_uv_validity(mesh)
        if not uv_validity["is_valid"]:
            results.append(self.create_result(
                obj=obj,
                message="UV map has incomplete data",
                severity=Severity.WARNING,
                details=uv_validity,
                fix_hint="Re-unwrap the mesh to regenerate UV data"
            ))
        
        # Optional: Check for UV2 (lightmap)
        if self.check_uv2:
            uv2_result = self._check_uv2(obj, mesh)
            if uv2_result:
                results.append(uv2_result)
        
        return results
    
    def _check_uv_validity(self, mesh: bpy.types.Mesh) -> dict:
        """
        Check if the active UV layer has valid data.
        
        Returns a dict with validity info.
        """
        if not mesh.uv_layers.active:
            return {
                "is_valid": False,
                "reason": "no_active_uv",
            }
        
        uv_layer = mesh.uv_layers.active
        
        # Check if UV data exists
        if not uv_layer.data:
            return {
                "is_valid": False,
                "reason": "no_uv_data",
            }
        
        # Check if loop count matches
        expected_loops = len(mesh.loops)
        actual_loops = len(uv_layer.data)
        
        if expected_loops != actual_loops:
            return {
                "is_valid": False,
                "reason": "loop_count_mismatch",
                "expected": expected_loops,
                "actual": actual_loops,
            }
        
        return {
            "is_valid": True,
            "uv_name": uv_layer.name,
            "loop_count": actual_loops,
        }
    
    def _check_uv2(
        self, 
        obj: bpy.types.Object, 
        mesh: bpy.types.Mesh
    ) -> ValidationResult | None:
        """
        Check for UV2 (lightmap UVs).
        
        UV2 is required for lightmap baking in Unity.
        This check is optional and disabled by default.
        """
        uv_layers = mesh.uv_layers
        
        if len(uv_layers) < 2:
            return self.create_result(
                obj=obj,
                message="No UV2 (lightmap UV) found",
                severity=Severity.INFO,
                details={
                    "uv_layer_count": len(uv_layers),
                    "uv_layer_names": [uv.name for uv in uv_layers],
                },
                fix_hint="Add a second UV map for lightmapping if needed"
            )
        
        return None
