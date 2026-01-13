# SPDX-License-Identifier: GPL-3.0-or-later
"""
General utility functions.
"""

import bpy
from typing import List, Iterator


def get_mesh_objects(
    selected_only: bool = False,
    visible_only: bool = True
) -> List[bpy.types.Object]:
    """
    Get mesh objects from the scene.
    
    Args:
        selected_only: If True, only return selected objects
        visible_only: If True, only return visible objects
        
    Returns:
        List of mesh objects
    """
    objects = []
    
    source = bpy.context.selected_objects if selected_only else bpy.data.objects
    
    for obj in source:
        if obj.type != 'MESH':
            continue
        if visible_only and not obj.visible_get():
            continue
        objects.append(obj)
    
    return objects


def is_valid_mesh_object(obj: bpy.types.Object) -> bool:
    """
    Check if an object is a valid mesh object.
    
    Args:
        obj: The object to check
        
    Returns:
        True if it's a valid mesh object
    """
    if obj is None:
        return False
    if obj.type != 'MESH':
        return False
    if obj.data is None:
        return False
    return True


def select_object(obj: bpy.types.Object, add: bool = False) -> None:
    """
    Select an object in the viewport.
    
    Args:
        obj: The object to select
        add: If True, add to selection; if False, replace selection
    """
    if not add:
        bpy.ops.object.select_all(action='DESELECT')
    
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def focus_object(obj: bpy.types.Object) -> None:
    """
    Focus the viewport on an object.
    
    Args:
        obj: The object to focus on
    """
    select_object(obj)
    
    # Frame selected in all 3D views
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    override = {'area': area, 'region': region}
                    with bpy.context.temp_override(**override):
                        bpy.ops.view3d.view_selected()
                    break