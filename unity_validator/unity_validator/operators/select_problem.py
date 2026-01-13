# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2024 MatsubayashiAyaka
"""
Problem selection operators.

Operators for selecting objects with validation issues.
"""

import bpy
from bpy.types import Operator
from bpy.props import IntProperty, StringProperty

from ..utils.helpers import select_object, focus_object


class UNITY_VALIDATOR_OT_select_problem(Operator):
    """Select the object with this validation issue"""
    
    bl_idname = "unity_validator.select_problem"
    bl_label = "Select Problem Object"
    bl_description = "Select and focus on the object with this issue"
    bl_options = {'REGISTER', 'UNDO'}
    
    index: IntProperty(
        name="Result Index",
        description="Index of the validation result",
        default=0
    )
    
    def execute(self, context):
        """Select the object from the validation result."""
        results = context.scene.unity_validator_results
        
        if self.index < 0 or self.index >= len(results):
            self.report({'WARNING'}, "Invalid result index")
            return {'CANCELLED'}
        
        result = results[self.index]
        obj_name = result.object_name
        
        # Find the object
        obj = bpy.data.objects.get(obj_name)
        
        if obj is None:
            self.report({'WARNING'}, f"Object '{obj_name}' not found")
            return {'CANCELLED'}
        
        # Select and focus
        focus_object(obj)
        
        self.report({'INFO'}, f"Selected: {obj_name}")
        return {'FINISHED'}


class UNITY_VALIDATOR_OT_select_all_problems(Operator):
    """Select all objects with validation issues"""
    
    bl_idname = "unity_validator.select_all_problems"
    bl_label = "Select All Problem Objects"
    bl_description = "Select all objects that have validation issues"
    bl_options = {'REGISTER', 'UNDO'}
    
    severity_filter: StringProperty(
        name="Severity Filter",
        description="Filter by severity (ERROR, WARNING, INFO, or empty for all)",
        default=""
    )
    
    def execute(self, context):
        """Select all objects with issues."""
        results = context.scene.unity_validator_results
        
        if not results:
            self.report({'INFO'}, "No validation results")
            return {'CANCELLED'}
        
        # Collect unique object names
        object_names = set()
        for result in results:
            if self.severity_filter:
                if result.severity != self.severity_filter:
                    continue
            object_names.add(result.object_name)
        
        if not object_names:
            self.report({'INFO'}, "No matching objects")
            return {'CANCELLED'}
        
        # Deselect all first
        bpy.ops.object.select_all(action='DESELECT')
        
        # Select matching objects
        selected_count = 0
        for name in object_names:
            obj = bpy.data.objects.get(name)
            if obj:
                obj.select_set(True)
                selected_count += 1
        
        # Set active object to first found
        for name in object_names:
            obj = bpy.data.objects.get(name)
            if obj:
                context.view_layer.objects.active = obj
                break
        
        self.report({'INFO'}, f"Selected {selected_count} object(s)")
        return {'FINISHED'}


class UNITY_VALIDATOR_OT_select_errors(Operator):
    """Select all objects with errors"""
    
    bl_idname = "unity_validator.select_errors"
    bl_label = "Select Error Objects"
    bl_description = "Select all objects with ERROR severity issues"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bpy.ops.unity_validator.select_all_problems(severity_filter='ERROR')
        return {'FINISHED'}


class UNITY_VALIDATOR_OT_clear_results(Operator):
    """Clear all validation results"""
    
    bl_idname = "unity_validator.clear_results"
    bl_label = "Clear Results"
    bl_description = "Clear all validation results"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        context.scene.unity_validator_results.clear()
        context.scene.unity_validator_result_index = 0
        self.report({'INFO'}, "Validation results cleared")
        return {'FINISHED'}


# Registration
classes = [
    UNITY_VALIDATOR_OT_select_problem,
    UNITY_VALIDATOR_OT_select_all_problems,
    UNITY_VALIDATOR_OT_select_errors,
    UNITY_VALIDATOR_OT_clear_results,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
