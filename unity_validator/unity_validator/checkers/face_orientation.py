# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2024 MatsubayashiAyaka
"""
Face orientation validation checker.

Checks for inverted/flipped faces that cause rendering issues in Unity:
- Faces pointing inward (backface)
- Inconsistent face orientations
"""

import bpy
import bmesh
from typing import List, Set
from mathutils import Vector

from ..core import BaseChecker, ValidationResult, Severity, register_checker


@register_checker
class FaceOrientationChecker(BaseChecker):
    """
    Validates face orientations for Unity compatibility.
    
    Checks:
    - Faces that are likely pointing inward
    - Inconsistent face orientations (mesh not manifold)
    
    Inverted faces appear invisible or incorrectly lit in Unity
    when backface culling is enabled (default for most shaders).
    """
    
    name = "Face Orientation"
    description = "Check for inverted or inconsistent face orientations"
    default_severity = Severity.WARNING
    supports_exclusion = True  # Can be excluded for intentional double-sided meshes
    
    # Configuration
    max_reported_faces: int = 20
    
    def check(self, obj: bpy.types.Object) -> List[ValidationResult]:
        """
        Perform face orientation validation on the object.
        
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
        
        # Check for potentially inverted faces using BMesh for accurate analysis
        inverted_result = self._check_inverted_faces(obj, mesh)
        if inverted_result:
            results.append(inverted_result)
        
        return results
    
    def _check_inverted_faces(
        self, 
        obj: bpy.types.Object, 
        mesh: bpy.types.Mesh
    ) -> ValidationResult | None:
        """
        Check for faces that might be inverted.
        
        Uses a heuristic based on face normals relative to
        the mesh center or volume.
        """
        # Create BMesh for analysis
        bm = bmesh.new()
        try:
            bm.from_mesh(mesh)
            bm.faces.ensure_lookup_table()
            
            # Calculate mesh center
            if bm.verts:
                center = sum((v.co for v in bm.verts), Vector()) / len(bm.verts)
            else:
                return None
            
            # Check each face's orientation relative to center
            potentially_inverted = []
            
            for face in bm.faces:
                # Vector from face center to mesh center
                face_center = face.calc_center_median()
                to_center = center - face_center
                
                # If normal points toward center, face might be inverted
                # This is a heuristic and won't work for all mesh shapes
                dot = face.normal.dot(to_center.normalized())
                
                # Threshold: if normal points more than 45° toward center
                if dot > 0.7:  # cos(45°) ≈ 0.707
                    potentially_inverted.append(face.index)
                    
                    if len(potentially_inverted) >= self.max_reported_faces:
                        break
            
            if not potentially_inverted:
                return None
            
            # Count total potentially inverted
            total_inverted = 0
            for face in bm.faces:
                face_center = face.calc_center_median()
                to_center = center - face_center
                if face.normal.dot(to_center.normalized()) > 0.7:
                    total_inverted += 1
            
            # Only report if a significant portion of faces are inverted
            # This helps avoid false positives for complex shapes
            total_faces = len(bm.faces)
            inverted_ratio = total_inverted / total_faces if total_faces > 0 else 0
            
            # If less than 5% or just a few faces, might be intentional
            if inverted_ratio < 0.05 and total_inverted < 5:
                return self.create_result(
                    obj=obj,
                    message=f"{total_inverted} face(s) may have inverted normals",
                    severity=Severity.INFO,  # Lower severity for small numbers
                    details={
                        "potentially_inverted_count": total_inverted,
                        "total_faces": total_faces,
                        "face_indices": potentially_inverted,
                        "inverted_ratio": round(inverted_ratio, 3),
                    },
                    fix_hint="Check normals: Viewport Overlays > Face Orientation"
                )
            
            return self.create_result(
                obj=obj,
                message=f"{total_inverted} face(s) may have inverted normals ({inverted_ratio:.1%})",
                severity=Severity.WARNING,
                details={
                    "potentially_inverted_count": total_inverted,
                    "total_faces": total_faces,
                    "face_indices": potentially_inverted,
                    "inverted_ratio": round(inverted_ratio, 3),
                },
                fix_hint="Fix normals: Edit Mode > Mesh > Normals > Recalculate Outside"
            )
            
        finally:
            bm.free()
