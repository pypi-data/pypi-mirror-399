"""
TUI animations for startup and completion effects.

Provides distinctive visual effects for:
- Application startup (ASCII art reveal, matrix rain)
- Download completion (confetti, success banner)
- Error states (glitch effect)
"""

import random
import time
from typing import List, Optional

from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from torrentcli.tui.theme import Theme


def play_startup_animation(theme: Theme, duration: float = 1.0) -> None:
    """
    Play startup animation with ASCII art reveal.

    Args:
        theme: Theme to use for styling
        duration: Animation duration in seconds
    """
    console = Console()

    # ASCII art logo
    logo_lines = [
        "TfWTPWfPWfPWTPWTWTTfW  TPWf  f",
        " Q Q Q`f]`f]Qc QQQ Q   Q  Q  Q",
        " i ZP]iZPiZPZP]]Z] i   ZP]iP]i",
    ]

    # Reveal animation (fade in line by line)
    with console.screen():
        for i, line in enumerate(logo_lines):
            console.clear()

            # Show lines up to current
            for j in range(i + 1):
                styled_line = Text(logo_lines[j], style=theme.colors.accent_info)
                console.print(Align.center(styled_line))

            time.sleep(duration / len(logo_lines))

        # Hold final logo
        console.clear()
        for line in logo_lines:
            styled_line = Text(line, style=f"bold {theme.colors.accent_success}")
            console.print(Align.center(styled_line))

        # Tagline
        tagline = Text("Pro Edition", style=theme.colors.text_dim)
        console.print("\n")
        console.print(Align.center(tagline))

        time.sleep(0.5)


def play_matrix_rain(theme: Theme, duration: float = 2.0) -> None:
    """
    Play Matrix-style rain animation (for matrix theme).

    Args:
        theme: Theme to use
        duration: Animation duration in seconds
    """
    console = Console()

    # Matrix characters
    chars = list("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@#$%^&*")

    width = console.width
    height = console.height - 2

    # Initialize columns
    columns: List[List[str]] = [[] for _ in range(width)]

    start_time = time.time()

    with console.screen():
        while (time.time() - start_time) < duration:
            console.clear()

            # Update columns
            for col_idx in range(width):
                # Randomly add new characters at top
                if random.random() < 0.1:
                    columns[col_idx].insert(0, random.choice(chars))

                # Remove characters that scroll off bottom
                if len(columns[col_idx]) > height:
                    columns[col_idx].pop()

            # Render columns
            for row in range(height):
                line = Text()
                for col in range(width):
                    if row < len(columns[col]):
                        char = columns[col][row]

                        # Brightest at top
                        if row == 0:
                            style = f"bold {theme.colors.accent_success}"
                        elif row < 3:
                            style = theme.colors.text_primary
                        else:
                            style = theme.colors.text_dim

                        line.append(char, style=style)
                    else:
                        line.append(" ")

                console.print(line, end="")

            time.sleep(0.05)  # ~20 FPS


def play_completion_animation(
    theme: Theme,
    name: str,
    size_bytes: int,
    duration_sec: float,
) -> None:
    """
    Play download completion animation with success banner.

    Args:
        theme: Theme to use
        name: Download name
        size_bytes: Download size
        duration_sec: Download duration
    """
    console = Console()

    # Success ASCII art
    success_art = [
        "   _____ _    _  _____ _____ ______  _____ _____ ",
        "  / ____| |  | |/ ____/ ____|  ____|/ ____/ ____|",
        " | (___ | |  | | |   | |    | |__  | (___| (___  ",
        "  \\___ \\| |  | | |   | |    |  __|  \\___ \\\\___ \\ ",
        "  ____) | |__| | |___| |____| |____ ____) |___) |",
        " |_____/ \\____/ \\_____\\_____|______|_____/_____/ ",
    ]

    # Animate success banner
    console.clear()

    for line in success_art:
        styled_line = Text(line, style=f"bold {theme.colors.accent_success}")
        console.print(Align.center(styled_line))
        time.sleep(0.1)

    console.print("\n")

    # Download details
    details = Panel(
        Text.assemble(
            ("File: ", theme.colors.text_dim),
            (f"{name}\n", theme.colors.text_primary),
            ("Size: ", theme.colors.text_dim),
            (f"{_format_bytes(size_bytes)}\n", theme.colors.text_primary),
            ("Duration: ", theme.colors.text_dim),
            (f"{_format_duration(duration_sec)}", theme.colors.text_primary),
        ),
        border_style=theme.colors.accent_success,
        title="Download Complete",
    )

    console.print(Align.center(details))


def play_error_animation(theme: Theme, error_message: str) -> None:
    """
    Play error animation with glitch effect.

    Args:
        theme: Theme to use
        error_message: Error message to display
    """
    console = Console()

    # Glitch effect: show error message with random artifacts
    glitch_chars = "ˆ“’‘!@#$%^&*"

    console.clear()

    for i in range(5):
        # Add random glitch characters
        glitched = list(error_message)
        for _ in range(random.randint(2, 5)):
            pos = random.randint(0, len(glitched) - 1)
            glitched[pos] = random.choice(glitch_chars)

        glitched_text = Text("".join(glitched), style=theme.colors.accent_error)

        console.clear()
        console.print("\n" * 5)
        console.print(Align.center(glitched_text))

        time.sleep(0.1)

    # Final clean error
    console.clear()

    error_panel = Panel(
        Text(error_message, style=theme.colors.text_primary),
        border_style=theme.colors.accent_error,
        title="ERROR",
        title_align="left",
    )

    console.print("\n" * 5)
    console.print(Align.center(error_panel))


def play_confetti_animation(theme: Theme, duration: float = 2.0) -> None:
    """
    Play confetti animation for completion.

    Args:
        theme: Theme to use
        duration: Animation duration in seconds
    """
    console = Console()

    confetti_chars = ["*", """, "æ", "Ë", "Ï", "f", "e", "`", "c"]
    colors = [
        theme.colors.accent_success,
        theme.colors.accent_info,
        theme.colors.download_color,
        theme.colors.peer_color,
    ]

    width = console.width
    height = console.height - 2

    # Initialize confetti particles
    particles: List[dict] = []

    start_time = time.time()

    with console.screen():
        while (time.time() - start_time) < duration:
            console.clear()

            # Spawn new particles
            if random.random() < 0.3:
                particles.append({
                    "x": random.randint(0, width - 1),
                    "y": 0,
                    "char": random.choice(confetti_chars),
                    "color": random.choice(colors),
                })

            # Update particles (fall down)
            for particle in particles:
                particle["y"] += 1

            # Remove particles that fell off screen
            particles = [p for p in particles if p["y"] < height]

            # Render particles
            grid = [[" " for _ in range(width)] for _ in range(height)]
            styles = [[theme.colors.text_dim for _ in range(width)] for _ in range(height)]

            for particle in particles:
                x, y = particle["x"], particle["y"]
                if 0 <= x < width and 0 <= y < height:
                    grid[y][x] = particle["char"]
                    styles[y][x] = particle["color"]

            # Print grid
            for row_idx, row in enumerate(grid):
                line = Text()
                for col_idx, char in enumerate(row):
                    line.append(char, style=styles[row_idx][col_idx])
                console.print(line, end="")

            time.sleep(0.05)  # ~20 FPS


def show_progress_spinner(
    theme: Theme,
    message: str = "Loading...",
    duration: float = 2.0,
) -> None:
    """
    Show spinner animation.

    Args:
        theme: Theme to use
        message: Message to display
        duration: How long to spin
    """
    console = Console()

    spinner_chars = ["", "", "9", "8", "<", "4", "&", "'", "", ""]

    start_time = time.time()
    idx = 0

    with console.screen():
        while (time.time() - start_time) < duration:
            console.clear()

            spinner = Text()
            spinner.append(spinner_chars[idx], style=f"bold {theme.colors.accent_info}")
            spinner.append(f" {message}", style=theme.colors.text_primary)

            console.print("\n" * 10)
            console.print(Align.center(spinner))

            idx = (idx + 1) % len(spinner_chars)
            time.sleep(0.1)


def pulse_text(
    console: Console,
    text: str,
    color: str,
    duration: float = 1.0,
) -> None:
    """
    Pulse text brightness effect.

    Args:
        console: Rich console
        text: Text to pulse
        color: Base color
        duration: Pulse duration
    """
    steps = 10
    for i in range(steps):
        console.clear()

        # Calculate brightness (sine wave)
        brightness = 0.5 + 0.5 * (i / steps)

        # Render with varying brightness (dim -> bright -> dim)
        styled_text = Text(text, style=f"{color} {int(brightness * 100)}%")

        console.print("\n" * 10)
        console.print(Align.center(styled_text))

        time.sleep(duration / steps)


# Helper functions

def _format_bytes(bytes_val: int) -> str:
    """Format bytes to human-readable size."""
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(bytes_val)
    unit_idx = 0

    while value >= 1024 and unit_idx < len(units) - 1:
        value /= 1024
        unit_idx += 1

    return f"{value:.2f} {units[unit_idx]}"


def _format_duration(seconds: float) -> str:
    """Format duration to human-readable time."""
    total_secs = int(seconds)
    hours = total_secs // 3600
    minutes = (total_secs % 3600) // 60
    secs = total_secs % 60

    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"
