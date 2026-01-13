# SPDX-License-Identifier: GPL-3.0-or-later
"""
UI package.

Contains all UI elements for the Unity Validator addon.
"""

from . import panel
from . import preferences


def register():
    """Register all UI components."""
    panel.register()
    preferences.register()


def unregister():
    """Unregister all UI components."""
    preferences.unregister()
    panel.unregister()
