# SPDX-License-Identifier: GPL-3.0-or-later

from enum import IntEnum, auto


class Severity(IntEnum):
    """
    Validation result severity levels.
    
    Higher values indicate more severe issues.
    IntEnum allows comparison: ERROR > WARNING > INFO
    """
    INFO = auto()      # Informational, no action required
    WARNING = auto()   # Should be fixed, may cause issues
    ERROR = auto()     # Must be fixed before export
    
    @property
    def icon(self) -> str:
        """Return Blender icon name for this severity."""
        icons = {
            Severity.INFO: 'INFO',
            Severity.WARNING: 'ERROR',  # Blender's warning icon
            Severity.ERROR: 'CANCEL',   # Blender's error icon
        }
        return icons.get(self, 'QUESTION')
    
    @property
    def color(self) -> tuple:
        """Return RGBA color for this severity."""
        colors = {
            Severity.INFO: (0.3, 0.6, 1.0, 1.0),     # Blue
            Severity.WARNING: (1.0, 0.8, 0.2, 1.0),  # Yellow
            Severity.ERROR: (1.0, 0.3, 0.3, 1.0),    # Red
        }
        return colors.get(self, (0.5, 0.5, 0.5, 1.0))