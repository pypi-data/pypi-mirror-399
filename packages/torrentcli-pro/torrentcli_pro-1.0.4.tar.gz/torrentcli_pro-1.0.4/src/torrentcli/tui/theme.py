"""
Theme system implementing distinctive terminal aesthetics.

Provides multiple visual styles with cohesive color palettes, typography,
and animation characteristics. Each theme is production-ready with
careful attention to readability and terminal compatibility.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

from rich.text import Text


@dataclass
class ThemeColors:
    """Color palette for a theme."""

    # Base colors
    background: str
    surface: str
    border: str

    # Text hierarchy
    text_primary: str
    text_secondary: str
    text_dim: str

    # Semantic accents
    accent_success: str
    accent_error: str
    accent_warning: str
    accent_info: str

    # Data-specific
    download_color: str
    upload_color: str
    peer_color: str
    tracker_color: str


@dataclass
class ThemeCharacters:
    """Character sets for visual elements."""

    progress_full: str = "█"
    progress_75: str = "▓"
    progress_50: str = "▒"
    progress_25: str = "░"
    progress_empty: str = " "

    sparkline_levels: List[str] = None  # type: ignore

    def __post_init__(self) -> None:
        if self.sparkline_levels is None:
            self.sparkline_levels = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]


class Theme(ABC):
    """Abstract base class for all themes."""

    def __init__(self) -> None:
        self.colors = self._init_colors()
        self.chars = self._init_characters()

    @abstractmethod
    def _init_colors(self) -> ThemeColors:
        """Initialize theme color palette."""
        pass

    @abstractmethod
    def _init_characters(self) -> ThemeCharacters:
        """Initialize theme character sets."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Theme name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Theme description."""
        pass

    def render_progress_bar(self, percent: float, width: int = 50) -> Text:
        """
        Render gradient progress bar with "spark" effect at leading edge.

        Args:
            percent: Progress percentage (0-100)
            width: Width in characters

        Returns:
            Rich Text object with styled progress bar
        """
        filled_width = int(width * percent / 100)

        bar = ""
        for i in range(width):
            if i < filled_width - 1:
                bar += self.chars.progress_full
            elif i == filled_width - 1:
                bar += self.chars.progress_75  # Spark at edge
            elif i == filled_width:
                bar += self.chars.progress_50  # Fade after spark
            else:
                bar += self.chars.progress_empty

        # Color gradient based on progress
        if percent < 30:
            color = self.colors.accent_error
        elif percent < 70:
            color = self.colors.download_color
        else:
            color = self.colors.accent_success

        return Text(bar, style=f"bold {color}")

    def render_sparkline(self, data: List[float], max_width: int = 60) -> str:
        """
        Render sparkline graph for time-series data.

        Args:
            data: List of data points (e.g., last 60 speeds)
            max_width: Maximum width to render

        Returns:
            String of sparkline characters
        """
        if not data or max(data) == 0:
            return self.chars.sparkline_levels[0] * min(len(data), max_width)

        # Truncate if too long
        if len(data) > max_width:
            data = data[-max_width:]

        # Normalize to 0-7 range (8 levels)
        max_val = max(data)
        normalized = [int((v / max_val) * 7) for v in data]

        return "".join(self.chars.sparkline_levels[n] for n in normalized)

    def render_heatmap(self, ratio: float, width: int = 20) -> Text:
        """
        Render visual heatmap based on success ratio.

        Args:
            ratio: Success ratio (0.0 to 1.0)
            width: Width in characters

        Returns:
            Rich Text object with gradient heatmap
        """
        filled = int(width * ratio)
        heatmap = ""

        for i in range(width):
            if i < filled:
                # Gradient from full to empty
                block_idx = min(int((i / filled) * 4) if filled > 0 else 0, 3)
                blocks = [
                    self.chars.progress_full,
                    self.chars.progress_75,
                    self.chars.progress_50,
                    self.chars.progress_25,
                ]
                heatmap += blocks[block_idx]
            else:
                heatmap += self.chars.progress_empty

        # Color based on ratio
        if ratio > 0.7:
            color = self.colors.accent_success
        elif ratio > 0.4:
            color = self.colors.accent_warning
        else:
            color = self.colors.accent_error

        return Text(heatmap, style=color)


class CyberpunkTheme(Theme):
    """
    Cyberpunk Noir theme - DEFAULT

    Deep void black with neon accents. Inspired by Blade Runner, Neuromancer,
    and underground torrent tracker aesthetics. Maximum contrast, aggressive
    color choices, data brutalism.
    """

    @property
    def name(self) -> str:
        return "cyberpunk"

    @property
    def description(self) -> str:
        return "Neon accents on deep black - data brutalism aesthetic"

    def _init_colors(self) -> ThemeColors:
        return ThemeColors(
            # Base
            background="#0a0e14",
            surface="#151a21",
            border="#1f2937",
            # Text
            text_primary="#e6e6e6",
            text_secondary="#8b92a3",
            text_dim="#4a5568",
            # Semantic
            accent_success="#00ff9f",  # Neon green
            accent_error="#ff0055",  # Neon red
            accent_warning="#ffff00",  # Neon yellow
            accent_info="#00d4ff",  # Neon cyan
            # Data
            download_color="#00d4ff",  # Cyan
            upload_color="#ff6b6b",  # Soft red
            peer_color="#7c3aed",  # Purple
            tracker_color="#f59e0b",  # Amber
        )

    def _init_characters(self) -> ThemeCharacters:
        return ThemeCharacters()


class MatrixTheme(Theme):
    """
    Matrix Rain theme

    Classic hacker terminal. Pure green-on-black, no compromises.
    All UI elements rendered in shades of green. Optional falling
    character animation on startup.
    """

    @property
    def name(self) -> str:
        return "matrix"

    @property
    def description(self) -> str:
        return "Classic green-on-black hacker terminal"

    def _init_colors(self) -> ThemeColors:
        return ThemeColors(
            # Base (pure black)
            background="#000000",
            surface="#001100",
            border="#003300",
            # Text (all green)
            text_primary="#00ff00",
            text_secondary="#00cc00",
            text_dim="#008000",
            # Semantic (green variants)
            accent_success="#00ff00",
            accent_error="#00cc00",  # Dimmer green for "errors"
            accent_warning="#33ff33",  # Brighter green
            accent_info="#00ff00",
            # Data (green)
            download_color="#00ff00",
            upload_color="#00cc00",
            peer_color="#33ff33",
            tracker_color="#00dd00",
        )

    def _init_characters(self) -> ThemeCharacters:
        return ThemeCharacters()


class SolarizedTheme(Theme):
    """
    Solarized Light theme

    For bright environments. Warm cream background with carefully
    chosen accent colors. Maintains readability in sunlight/office lighting.
    """

    @property
    def name(self) -> str:
        return "solar"

    @property
    def description(self) -> str:
        return "Solarized light - for bright environments"

    def _init_colors(self) -> ThemeColors:
        return ThemeColors(
            # Base (solarized light)
            background="#fdf6e3",
            surface="#eee8d5",
            border="#93a1a1",
            # Text
            text_primary="#073642",
            text_secondary="#586e75",
            text_dim="#93a1a1",
            # Semantic
            accent_success="#859900",  # Green
            accent_error="#dc322f",  # Red
            accent_warning="#b58900",  # Yellow
            accent_info="#268bd2",  # Blue
            # Data
            download_color="#268bd2",  # Blue
            upload_color="#cb4b16",  # Orange
            peer_color="#6c71c4",  # Violet
            tracker_color="#2aa198",  # Cyan
        )

    def _init_characters(self) -> ThemeCharacters:
        return ThemeCharacters()


class NordTheme(Theme):
    """
    Nord theme - Arctic-inspired

    Cool blues and frost colors. Easier on the eyes than cyberpunk
    while maintaining distinctiveness. Popular with developers.
    """

    @property
    def name(self) -> str:
        return "nord"

    @property
    def description(self) -> str:
        return "Arctic blues and frost - easy on the eyes"

    def _init_colors(self) -> ThemeColors:
        return ThemeColors(
            # Base (nord polar night)
            background="#2e3440",
            surface="#3b4252",
            border="#434c5e",
            # Text (nord snow storm)
            text_primary="#eceff4",
            text_secondary="#d8dee9",
            text_dim="#4c566a",
            # Semantic (nord frost)
            accent_success="#a3be8c",  # Green
            accent_error="#bf616a",  # Red
            accent_warning="#ebcb8b",  # Yellow
            accent_info="#88c0d0",  # Cyan
            # Data
            download_color="#88c0d0",  # Cyan
            upload_color="#d08770",  # Orange
            peer_color="#b48ead",  # Purple
            tracker_color="#5e81ac",  # Blue
        )

    def _init_characters(self) -> ThemeCharacters:
        return ThemeCharacters()


class GruvboxTheme(Theme):
    """
    Gruvbox theme - Warm retro

    Warm, retro terminal colors. Brown/orange base with muted accents.
    Nostalgic feel, very comfortable for long sessions.
    """

    @property
    def name(self) -> str:
        return "gruvbox"

    @property
    def description(self) -> str:
        return "Warm retro terminal - comfortable for long sessions"

    def _init_colors(self) -> ThemeColors:
        return ThemeColors(
            # Base (gruvbox dark)
            background="#282828",
            surface="#3c3836",
            border="#504945",
            # Text
            text_primary="#ebdbb2",
            text_secondary="#d5c4a1",
            text_dim="#665c54",
            # Semantic
            accent_success="#b8bb26",  # Green
            accent_error="#fb4934",  # Red
            accent_warning="#fabd2f",  # Yellow
            accent_info="#83a598",  # Blue
            # Data
            download_color="#83a598",  # Blue
            upload_color="#fe8019",  # Orange
            peer_color="#d3869b",  # Purple
            tracker_color="#8ec07c",  # Aqua
        )

    def _init_characters(self) -> ThemeCharacters:
        return ThemeCharacters()


class MidnightTheme(Theme):
    """
    Midnight theme - Deep blues and purples

    Softer than cyberpunk but still distinctive. Deep blue background
    with purple and blue accents. Good middle ground.
    """

    @property
    def name(self) -> str:
        return "midnight"

    @property
    def description(self) -> str:
        return "Deep blues and purples - softer cyberpunk alternative"

    def _init_colors(self) -> ThemeColors:
        return ThemeColors(
            # Base
            background="#0d1117",
            surface="#161b22",
            border="#30363d",
            # Text
            text_primary="#c9d1d9",
            text_secondary="#8b949e",
            text_dim="#484f58",
            # Semantic
            accent_success="#3fb950",  # Green
            accent_error="#f85149",  # Red
            accent_warning="#d29922",  # Yellow
            accent_info="#58a6ff",  # Blue
            # Data
            download_color="#58a6ff",  # Blue
            upload_color="#f78166",  # Orange
            peer_color="#bc8cff",  # Purple
            tracker_color="#56d364",  # Green
        )

    def _init_characters(self) -> ThemeCharacters:
        return ThemeCharacters()


# Theme registry for easy lookup
THEMES = {
    "cyberpunk": CyberpunkTheme,
    "matrix": MatrixTheme,
    "solar": SolarizedTheme,
    "nord": NordTheme,
    "gruvbox": GruvboxTheme,
    "midnight": MidnightTheme,
}


def get_theme(name: str) -> Theme:
    """Get theme instance by name."""
    if name not in THEMES:
        raise ValueError(
            f"Unknown theme: {name}. Available: {', '.join(THEMES.keys())}"
        )
    return THEMES[name]()
