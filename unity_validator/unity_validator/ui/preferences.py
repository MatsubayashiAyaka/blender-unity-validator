# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2024 MatsubayashiAyaka
"""
Addon preferences for Unity Validator.
"""

import bpy
from bpy.types import AddonPreferences
from bpy.props import BoolProperty, EnumProperty


class UNITY_VALIDATOR_Preferences(AddonPreferences):
    """Addon preferences for Unity Validator."""
    
    bl_idname = "unity_validator"
    
    # Global checker enable/disable
    enable_transform_checker: BoolProperty(
        name="Transform Checker",
        description="Enable transform validation",
        default=True
    )
    
    enable_material_checker: BoolProperty(
        name="Material Checker",
        description="Enable material validation",
        default=True
    )
    
    enable_uv_checker: BoolProperty(
        name="UV Checker",
        description="Enable UV validation",
        default=True
    )
    
    enable_naming_checker: BoolProperty(
        name="Naming Checker",
        description="Enable naming validation",
        default=True
    )
    
    enable_geometry_checker: BoolProperty(
        name="Geometry Checker",
        description="Enable geometry validation",
        default=True
    )
    
    enable_face_orientation_checker: BoolProperty(
        name="Face Orientation Checker",
        description="Enable face orientation validation",
        default=True
    )
    
    enable_normals_checker: BoolProperty(
        name="Normals Checker",
        description="Enable normals validation",
        default=True
    )
    
    # Severity settings
    negative_scale_severity: EnumProperty(
        name="Negative Scale Severity",
        description="Severity level for negative scale issues",
        items=[
            ('ERROR', "Error", "Treat as error"),
            ('WARNING', "Warning", "Treat as warning"),
        ],
        default='ERROR'
    )
    
    # UI settings
    auto_select_on_click: BoolProperty(
        name="Auto-select on Click",
        description="Automatically select object when clicking on result",
        default=True
    )
    
    def draw(self, context):
        layout = self.layout
        
        # Checker toggles
        box = layout.box()
        box.label(text="Enabled Checkers:", icon='CHECKMARK')
        
        col = box.column(align=True)
        col.prop(self, "enable_transform_checker")
        col.prop(self, "enable_material_checker")
        col.prop(self, "enable_uv_checker")
        col.prop(self, "enable_naming_checker")
        col.prop(self, "enable_geometry_checker")
        col.prop(self, "enable_face_orientation_checker")
        col.prop(self, "enable_normals_checker")
        
        # Severity settings
        box = layout.box()
        box.label(text="Severity Settings:", icon='ERROR')
        box.prop(self, "negative_scale_severity")
        
        # UI settings
        box = layout.box()
        box.label(text="UI Settings:", icon='PREFERENCES')
        box.prop(self, "auto_select_on_click")


# Registration
classes = [
    UNITY_VALIDATOR_Preferences,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
