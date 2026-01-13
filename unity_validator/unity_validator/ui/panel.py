# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2024 MatsubayashiAyaka
"""
Main UI panel for Unity Validator.

Displays validation results and provides controls.
"""

import bpy
from bpy.types import Panel, UIList, PropertyGroup
from bpy.props import (
    StringProperty, 
    IntProperty, 
    CollectionProperty,
    EnumProperty,
)

from ..core import Severity, CheckerRegistry


# -------------------------------------------------------------------
# Property Groups
# -------------------------------------------------------------------

class UNITY_VALIDATOR_ResultItem(PropertyGroup):
    """Property group for storing a single validation result."""
    
    checker_name: StringProperty(name="Checker")
    severity: StringProperty(name="Severity")
    object_name: StringProperty(name="Object")
    message: StringProperty(name="Message")
    fix_hint: StringProperty(name="Fix Hint")


# -------------------------------------------------------------------
# UI List
# -------------------------------------------------------------------

class UNITY_VALIDATOR_UL_results(UIList):
    """UI List for displaying validation results."""
    
    def draw_item(
        self, 
        context, 
        layout, 
        data, 
        item, 
        icon, 
        active_data, 
        active_propname, 
        index
    ):
        """Draw a single result item."""
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # Get icon based on severity
            severity_icons = {
                'ERROR': 'CANCEL',
                'WARNING': 'ERROR',
                'INFO': 'INFO',
            }
            icon = severity_icons.get(item.severity, 'QUESTION')
            
            # Main row
            row = layout.row(align=True)
            
            # Severity icon
            row.label(text="", icon=icon)
            
            # Object name and message
            split = row.split(factor=0.3)
            split.label(text=item.object_name)
            split.label(text=f"[{item.checker_name}] {item.message}")
            
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon='MESH_DATA')
    
    def filter_items(self, context, data, propname):
        """Filter and order items in the list."""
        items = getattr(data, propname)
        helper_funcs = bpy.types.UI_UL_list
        
        # Default filtering
        flt_flags = []
        flt_neworder = []
        
        if self.filter_name:
            flt_flags = helper_funcs.filter_items_by_name(
                self.filter_name, 
                self.bitflag_filter_item, 
                items, 
                "message",
                reverse=False
            )
        
        if not flt_flags:
            flt_flags = [self.bitflag_filter_item] * len(items)
        
        # Sort by severity (ERROR first, then WARNING, then INFO)
        severity_order = {'ERROR': 0, 'WARNING': 1, 'INFO': 2}
        flt_neworder = sorted(
            range(len(items)),
            key=lambda i: severity_order.get(items[i].severity, 3)
        )
        
        return flt_flags, flt_neworder


# -------------------------------------------------------------------
# Panels
# -------------------------------------------------------------------

class UNITY_VALIDATOR_PT_main(Panel):
    """Main panel for Unity Validator."""
    
    bl_label = "Unity Export Validator"
    bl_idname = "UNITY_VALIDATOR_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Unity Validator"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Validation buttons
        row = layout.row(align=True)
        row.scale_y = 1.5
        row.operator("unity_validator.validate", text="Run Validation", icon='PLAY')
        row.operator("unity_validator.validate_quick", text="", icon='FILE_REFRESH')
        
        # Results summary
        results = scene.unity_validator_results
        if results:
            error_count = sum(1 for r in results if r.severity == 'ERROR')
            warning_count = sum(1 for r in results if r.severity == 'WARNING')
            info_count = sum(1 for r in results if r.severity == 'INFO')
            
            box = layout.box()
            row = box.row()
            row.label(text="Summary:", icon='INFO')
            
            sub = row.row(align=True)
            if error_count > 0:
                sub.label(text=f"{error_count}", icon='CANCEL')
            if warning_count > 0:
                sub.label(text=f"{warning_count}", icon='ERROR')
            if info_count > 0:
                sub.label(text=f"{info_count}", icon='INFO')
            
            # Show "has errors" warning
            if error_count > 0:
                box.label(
                    text="Errors must be fixed before export!",
                    icon='ERROR'
                )


class UNITY_VALIDATOR_PT_results(Panel):
    """Panel for displaying validation results."""
    
    bl_label = "Results"
    bl_idname = "UNITY_VALIDATOR_PT_results"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Unity Validator"
    bl_parent_id = "UNITY_VALIDATOR_PT_main"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        results = scene.unity_validator_results
        
        if not results:
            layout.label(text="No results. Run validation first.")
            return
        
        # Results list
        row = layout.row()
        row.template_list(
            "UNITY_VALIDATOR_UL_results",
            "",
            scene,
            "unity_validator_results",
            scene,
            "unity_validator_result_index",
            rows=5
        )
        
        # Action buttons column
        col = row.column(align=True)
        col.operator("unity_validator.select_problem", text="", icon='RESTRICT_SELECT_OFF')
        col.operator("unity_validator.clear_results", text="", icon='X')
        
        # Selected result details
        if scene.unity_validator_result_index < len(results):
            result = results[scene.unity_validator_result_index]
            
            box = layout.box()
            box.label(text="Details:", icon='INFO')
            
            col = box.column(align=True)
            col.label(text=f"Object: {result.object_name}")
            col.label(text=f"Checker: {result.checker_name}")
            col.label(text=f"Severity: {result.severity}")
            
            if result.fix_hint:
                box.separator()
                box.label(text="Fix:", icon='TOOL_SETTINGS')
                # Word wrap for long hints
                col = box.column()
                col.scale_y = 0.8
                self._draw_wrapped_text(col, result.fix_hint, width=40)
        
        # Selection buttons
        layout.separator()
        row = layout.row(align=True)
        row.operator("unity_validator.select_errors", text="Select Errors", icon='CANCEL')
        row.operator(
            "unity_validator.select_all_problems",
            text="Select All",
            icon='SELECT_EXTEND'
        )
    
    def _draw_wrapped_text(self, layout, text, width=40):
        """Draw text with word wrapping."""
        words = text.split(' ')
        line = ""
        for word in words:
            if len(line) + len(word) + 1 > width:
                layout.label(text=line)
                line = word
            else:
                line = f"{line} {word}".strip()
        if line:
            layout.label(text=line)


class UNITY_VALIDATOR_PT_checkers(Panel):
    """Panel for checker settings."""
    
    bl_label = "Checkers"
    bl_idname = "UNITY_VALIDATOR_PT_checkers"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Unity Validator"
    bl_parent_id = "UNITY_VALIDATOR_PT_main"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        
        checkers = CheckerRegistry.get_all()
        
        if not checkers:
            layout.label(text="No checkers registered")
            return
        
        # List all checkers
        for checker in checkers:
            row = layout.row()
            
            # Severity icon
            severity_icons = {
                Severity.ERROR: 'CANCEL',
                Severity.WARNING: 'ERROR',
                Severity.INFO: 'INFO',
            }
            icon = severity_icons.get(checker.default_severity, 'QUESTION')
            
            row.label(text=checker.name, icon=icon)
            row.label(text=f"({checker.default_severity.name})")


# -------------------------------------------------------------------
# Registration
# -------------------------------------------------------------------

classes = [
    UNITY_VALIDATOR_ResultItem,
    UNITY_VALIDATOR_UL_results,
    UNITY_VALIDATOR_PT_main,
    UNITY_VALIDATOR_PT_results,
    UNITY_VALIDATOR_PT_checkers,
]


def register():
    """Register UI classes and properties."""
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Register scene properties
    bpy.types.Scene.unity_validator_results = CollectionProperty(
        type=UNITY_VALIDATOR_ResultItem
    )
    bpy.types.Scene.unity_validator_result_index = IntProperty(
        name="Result Index",
        default=0
    )


def unregister():
    """Unregister UI classes and properties."""
    # Remove scene properties
    del bpy.types.Scene.unity_validator_result_index
    del bpy.types.Scene.unity_validator_results
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
