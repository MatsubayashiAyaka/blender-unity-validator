# SPDX-License-Identifier: GPL-3.0-or-later
"""
Operators package.

Contains all Blender operators for the Unity Validator addon.
"""

from . import validate
from . import select_problem


def register():
    """Register all operators."""
    validate.register()
    select_problem.register()


def unregister():
    """Unregister all operators."""
    select_problem.unregister()
    validate.unregister()
