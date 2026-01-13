# SPDX-License-Identifier: GPL-3.0-or-later
"""
Blender version compatibility utilities.

This module provides version-agnostic APIs for features that changed
between Blender versions (especially 3.6 to 4.2+).
"""

import bpy
from typing import Tuple


def get_blender_version() -> Tuple[int, int, int]:
    """Get the current Blender version as a tuple."""
    return bpy.app.version


def is_blender_4_1_or_later() -> bool:
    """Check if running Blender 4.1 or later."""
    return bpy.app.version >= (4, 1, 0)


def has_auto_smooth(mesh: 'bpy.types.Mesh') -> bool:
    """
    Check if auto smooth is enabled for the mesh.
    
    Handles the API change in Blender 4.1 where mesh.use_auto_smooth
    was removed and replaced with custom normals.
    
    Args:
        mesh: The mesh to check
        
    Returns:
        True if auto smooth (or equivalent) is enabled
    """
    if is_blender_4_1_or_later():
        # In 4.1+, auto smooth is replaced by custom normals
        return mesh.has_custom_normals
    else:
        # In 3.6-4.0, use the traditional property
        return getattr(mesh, 'use_auto_smooth', False)


def get_auto_smooth_angle(mesh: 'bpy.types.Mesh') -> float:
    """
    Get the auto smooth angle for the mesh.
    
    Args:
        mesh: The mesh to check
        
    Returns:
        The auto smooth angle in radians, or 0.0 if not applicable
    """
    if is_blender_4_1_or_later():
        # In 4.1+, this is handled differently
        # Default 30 degrees in radians
        return 0.523599
    else:
        return getattr(mesh, 'auto_smooth_angle', 0.523599)
