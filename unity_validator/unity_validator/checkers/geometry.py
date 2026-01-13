# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2024 MatsubayashiAyaka
"""
Geometry validation checker.

Checks for geometry issues that cause problems in Unity:
- N-gons (faces with 5+ vertices)
- Extremely small faces
- Loose vertices/edges (optional)
"""

import bpy
import bmesh
from typing import List, Tuple

from ..core import BaseChecker, ValidationResult, Severity, register_checker


@register_checker
class GeometryChecker(BaseChecker):
    """
    Validates mesh geometry for Unity compatibility.
    
    Checks:
    - N-gons (faces with more than 4 vertices)
    - Very small faces that may cause issues
    
    N-gons are triangulated on export but can cause
    unpredictable results.
    """
    
    name = "Geometry"
    description = "Check for N-gons and problematic geometry"
    default_severity = Severity.WARNING
    
    # Configuration
    check_ngons: bool = True
    check_small_faces: bool = True
    small_face_threshold: float = 0.0001  # Square units
    max_reported_faces: int = 10  # Limit reported faces to avoid huge lists
    
    def check(self, obj: bpy.types.Object) -> List[ValidationResult]:
        """
        Perform geometry validation on the object.
        
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
        
        # Check for N-gons
        if self.check_ngons:
            ngon_result = self._check_ngons(obj, mesh)
            if ngon_result:
                results.append(ngon_result)
        
        # Check for small faces
        if self.check_small_faces:
            small_result = self._check_small_faces(obj, mesh)
            if small_result:
                results.append(small_result)
        
        return results
    
    def _check_ngons(
        self, 
        obj: bpy.types.Object, 
        mesh: bpy.types.Mesh
    ) -> ValidationResult | None:
        """
        Check for N-gons (faces with more than 4 vertices).
        
        Unity triangulates meshes, but N-gons can produce
        unexpected triangulation results.
        """
        ngon_indices = []
        ngon_vertex_counts = []
        
        for i, poly in enumerate(mesh.polygons):
            if poly.loop_total > 4:
                ngon_indices.append(i)
                ngon_vertex_counts.append(poly.loop_total)
                
                if len(ngon_indices) >= self.max_reported_faces:
                    break
        
        if not ngon_indices:
            return None
        
        total_ngons = sum(1 for p in mesh.polygons if p.loop_total > 4)
        
        # Build message
        if total_ngons <= self.max_reported_faces:
            message = f"{total_ngons} N-gon(s) found"
        else:
            message = f"{total_ngons} N-gon(s) found (showing first {self.max_reported_faces})"
        
        return self.create_result(
            obj=obj,
            message=message,
            severity=Severity.WARNING,
            details={
                "total_ngons": total_ngons,
                "face_indices": ngon_indices,
                "vertex_counts": ngon_vertex_counts,
            },
            fix_hint="Select N-gons: Edit Mode > Select > All by Trait > Faces by Sides"
        )
    
    def _check_small_faces(
        self, 
        obj: bpy.types.Object, 
        mesh: bpy.types.Mesh
    ) -> ValidationResult | None:
        """
        Check for extremely small faces.
        
        Very small faces can cause issues with:
        - Shading/normals
        - Texture mapping
        - Physics calculations
        """
        # Need to use bmesh or calculate areas manually
        # For performance, use polygon.area property
        small_face_indices = []
        small_face_areas = []
        
        for i, poly in enumerate(mesh.polygons):
            if poly.area < self.small_face_threshold:
                small_face_indices.append(i)
                small_face_areas.append(poly.area)
                
                if len(small_face_indices) >= self.max_reported_faces:
                    break
        
        if not small_face_indices:
            return None
        
        total_small = sum(1 for p in mesh.polygons if p.area < self.small_face_threshold)
        
        return self.create_result(
            obj=obj,
            message=f"{total_small} extremely small face(s) found",
            severity=Severity.INFO,
            details={
                "total_small_faces": total_small,
                "face_indices": small_face_indices,
                "face_areas": small_face_areas,
                "threshold": self.small_face_threshold,
            },
            fix_hint="Consider merging or dissolving tiny faces"
        )
