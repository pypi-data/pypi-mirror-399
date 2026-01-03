"""
TUI (Terminal User Interface) layer with distinctive cyberpunk aesthetics.

Implements:
- Multiple themes (cyberpunk, matrix, solarized, nord, etc.)
- Responsive layouts (80 col, 120 col, compact)
- Live animations (sparklines, progress bars, spinners)
- Keyboard controls
"""

from torrentcli.tui.renderer import TUIRenderer
from torrentcli.tui.theme import CyberpunkTheme, MatrixTheme, SolarizedTheme, Theme

__all__ = [
    "TUIRenderer",
    "Theme",
    "CyberpunkTheme",
    "MatrixTheme",
    "SolarizedTheme",
]
