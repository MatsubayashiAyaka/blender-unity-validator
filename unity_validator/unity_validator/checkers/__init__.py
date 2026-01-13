# SPDX-License-Identifier: GPL-3.0-or-later
"""
Validation checkers package.

This package contains all validation checker implementations.
Each checker is automatically registered when imported via the
@register_checker decorator.
"""

# Import checkers to trigger registration
from .transform import TransformChecker
from .materials import MaterialChecker
from .uv import UVChecker
from .naming import NamingChecker
from .geometry import GeometryChecker
from .face_orientation import FaceOrientationChecker
from .normals import NormalsChecker

# List of all checker classes for reference
__all__ = [
    "TransformChecker",
    "MaterialChecker",
    "UVChecker",
    "NamingChecker",
    "GeometryChecker",
    "FaceOrientationChecker",
    "NormalsChecker",
]


def register():
    """Register all checkers."""
    # Checkers are auto-registered via decorator on import
    pass


def unregister():
    """Unregister all checkers."""
    # Cleanup is handled by CheckerRegistry.clear()
    pass
