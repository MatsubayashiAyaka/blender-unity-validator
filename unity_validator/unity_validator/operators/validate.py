# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2024 MatsubayashiAyaka
"""
Validation operator.

Runs all registered checkers on selected or all mesh objects.
"""

import bpy
from bpy.types import Operator
from bpy.props import BoolProperty, EnumProperty
from typing import List

from ..core import CheckerRegistry, ValidationResult, Severity
from ..utils.helpers import get_mesh_objects


class UNITY_VALIDATOR_OT_validate(Operator):
    """Run Unity export validation on mesh objects"""
    
    bl_idname = "unity_validator.validate"
    bl_label = "Run Validation"
    bl_description = "Validate mesh objects for Unity export"
    bl_options = {'REGISTER', 'UNDO'}
    
    # Operator properties
    selected_only: BoolProperty(
        name="Selected Only",
        description="Only validate selected objects",
        default=False
    )
    
    visible_only: BoolProperty(
        name="Visible Only", 
        description="Only validate visible objects",
        default=True
    )
    
    def execute(self, context):
        """Execute the validation."""
        # Get objects to validate
        objects = get_mesh_objects(
            selected_only=self.selected_only,
            visible_only=self.visible_only
        )
        
        if not objects:
            self.report({'WARNING'}, "No mesh objects to validate")
            return {'CANCELLED'}
        
        # Get all registered checkers
        checkers = CheckerRegistry.get_all()
        
        if not checkers:
            self.report({'ERROR'}, "No checkers registered")
            return {'CANCELLED'}
        
        # Run validation
        all_results: List[ValidationResult] = []
        
        for obj in objects:
            for checker in checkers:
                # Skip if checker doesn't support this object type
                if not checker.is_supported(obj):
                    continue
                
                # Skip if excluded
                if checker.is_excluded(obj):
                    continue
                
                # Run checker
                try:
                    results = checker.check(obj)
                    all_results.extend(results)
                except Exception as e:
                    self.report(
                        {'WARNING'}, 
                        f"Checker '{checker.name}' failed on '{obj.name}': {e}"
                    )
        
        # Store results in scene for UI access
        self._store_results(context, all_results)
        
        # Report summary
        error_count = sum(1 for r in all_results if r.severity == Severity.ERROR)
        warning_count = sum(1 for r in all_results if r.severity == Severity.WARNING)
        info_count = sum(1 for r in all_results if r.severity == Severity.INFO)
        
        if error_count > 0:
            self.report(
                {'ERROR'},
                f"Validation complete: {error_count} errors, {warning_count} warnings, {info_count} info"
            )
        elif warning_count > 0:
            self.report(
                {'WARNING'},
                f"Validation complete: {warning_count} warnings, {info_count} info"
            )
        elif info_count > 0:
            self.report(
                {'INFO'},
                f"Validation complete: {info_count} info items"
            )
        else:
            self.report({'INFO'}, "Validation complete: No issues found!")
        
        return {'FINISHED'}
    
    def _store_results(
        self, 
        context: bpy.types.Context, 
        results: List[ValidationResult]
    ):
        """Store validation results in scene properties for UI access."""
        # Clear existing results
        context.scene.unity_validator_results.clear()
        
        # Add new results
        for result in results:
            item = context.scene.unity_validator_results.add()
            item.checker_name = result.checker_name
            item.severity = result.severity.name
            item.object_name = result.object_name
            item.message = result.message
            item.fix_hint = result.fix_hint or ""
    
    def invoke(self, context, event):
        """Show options dialog."""
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        """Draw the options dialog."""
        layout = self.layout
        layout.prop(self, "selected_only")
        layout.prop(self, "visible_only")


class UNITY_VALIDATOR_OT_validate_quick(Operator):
    """Quick validation without dialog"""
    
    bl_idname = "unity_validator.validate_quick"
    bl_label = "Quick Validate"
    bl_description = "Run quick validation on all visible objects"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        """Execute quick validation."""
        bpy.ops.unity_validator.validate(
            selected_only=False,
            visible_only=True
        )
        return {'FINISHED'}


# Registration
classes = [
    UNITY_VALIDATOR_OT_validate,
    UNITY_VALIDATOR_OT_validate_quick,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
