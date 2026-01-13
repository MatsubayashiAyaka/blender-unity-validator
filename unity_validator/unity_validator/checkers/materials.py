# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2024 MatsubayashiAyaka
"""
Material validation checker.

Checks for material issues that cause problems in Unity:
- Empty material slots (no material assigned)
- No materials at all (object appears pink/magenta)
- Unused material slots (assigned but not used by any face)
"""

import bpy
from typing import List, Set

from ..core import BaseChecker, ValidationResult, Severity, register_checker


@register_checker
class MaterialChecker(BaseChecker):
    """
    Validates material assignments for Unity compatibility.
    
    Checks:
    - Object has at least one material
    - No empty material slots
    - No unused material slots (materials not assigned to any face)
    
    Missing materials cause objects to appear pink/magenta in Unity.
    """
    
    name = "Material"
    description = "Check for missing or improperly assigned materials"
    default_severity = Severity.WARNING
    
    def check(self, obj: bpy.types.Object) -> List[ValidationResult]:
        """
        Perform material validation on the object.
        
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
        
        # Check if object has any material slots
        if not obj.material_slots:
            results.append(self.create_result(
                obj=obj,
                message="No material slots",
                severity=Severity.ERROR,
                details={"slot_count": 0},
                fix_hint="Add a material in the Material Properties panel"
            ))
            return results
        
        # Check for empty material slots
        empty_slots = self._find_empty_slots(obj)
        if empty_slots:
            results.append(self.create_result(
                obj=obj,
                message=f"Empty material slot(s): {', '.join(map(str, empty_slots))}",
                severity=Severity.WARNING,
                details={
                    "empty_slot_indices": empty_slots,
                    "total_slots": len(obj.material_slots),
                },
                fix_hint="Assign materials to empty slots or remove unused slots"
            ))
        
        # Check if all slots are empty (no usable materials)
        all_empty = all(slot.material is None for slot in obj.material_slots)
        if all_empty and len(obj.material_slots) > 0:
            results.append(self.create_result(
                obj=obj,
                message="All material slots are empty",
                severity=Severity.ERROR,
                details={"slot_count": len(obj.material_slots)},
                fix_hint="Assign at least one material"
            ))
        
        # Check for unused material slots (material assigned but not used)
        unused_slots = self._find_unused_slots(obj, mesh)
        if unused_slots:
            slot_names = [obj.material_slots[i].name or f"Slot {i}" for i in unused_slots]
            results.append(self.create_result(
                obj=obj,
                message=f"Unused material slot(s): {', '.join(slot_names)}",
                severity=Severity.INFO,
                details={
                    "unused_slot_indices": unused_slots,
                    "unused_slot_names": slot_names,
                },
                fix_hint="Remove unused material slots or assign them to faces"
            ))
        
        return results
    
    def _find_empty_slots(self, obj: bpy.types.Object) -> List[int]:
        """Find indices of material slots that have no material assigned."""
        empty = []
        for i, slot in enumerate(obj.material_slots):
            if slot.material is None:
                empty.append(i)
        return empty
    
    def _find_unused_slots(
        self, 
        obj: bpy.types.Object, 
        mesh: bpy.types.Mesh
    ) -> List[int]:
        """
        Find indices of material slots that are not used by any face.
        
        A slot is unused if it has a material but no polygon references it.
        """
        if not mesh.polygons:
            return []
        
        # Get set of all material indices used by polygons
        used_indices: Set[int] = set()
        for poly in mesh.polygons:
            used_indices.add(poly.material_index)
        
        # Find slots that have materials but aren't used
        unused = []
        for i, slot in enumerate(obj.material_slots):
            if slot.material is not None and i not in used_indices:
                unused.append(i)
        
        return unused
