# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2024 あなたの名前

bl_info = {
    "name": "Unity Export Validator",
    "author": "あなたの名前",
    "version": (0, 1, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > Unity Validator",
    "description": "Validate assets before exporting to Unity (URP)",
    "warning": "",
    "doc_url": "https://github.com/MatsubayashiAyaka/blender-unity-validator.git",
    "category": "Import-Export",
}

import bpy

from . import core
from . import checkers
from . import operators
from . import ui


def register():
    """Register all addon components."""
    core.register()
    checkers.register()
    operators.register()
    ui.register()


def unregister():
    """Unregister all addon components."""
    ui.unregister()
    operators.unregister()
    checkers.unregister()
    core.unregister()


if __name__ == "__main__":
    register()