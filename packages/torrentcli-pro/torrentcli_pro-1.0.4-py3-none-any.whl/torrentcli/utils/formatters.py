"""Formatting utilities for bytes, durations, etc."""

def format_bytes(bytes: int) -> str:
    """Format bytes to human-readable string."""
    for unit in ["B", "KiB", "MiB", "GiB", "TiB"]:
        if bytes < 1024:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024
    return f"{bytes:.1f} PiB"

def format_duration(seconds: int) -> str:
    """Format seconds to human-readable duration."""
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds // 60}m {seconds % 60}s"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours}h {minutes}m"
