"""
Configuration management with profile system.

Handles loading/merging config from:
1. Built-in defaults (hardcoded)
2. User config file (~/.config/torrentcli/config.toml)
3. Environment variables (TORRENTCLI_*)
4. CLI flags (highest priority)
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # type: ignore

import tomli_w


@dataclass
class Profile:
    """Download profile with aria2c options and behavior settings."""

    name: str
    description: str
    use_case: str
    aria2c_options: Dict[str, Any] = field(default_factory=dict)
    trackers: list[str] = field(default_factory=lambda: ["best"])
    retry_escalation: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for TOML serialization."""
        return {
            "description": self.description,
            "use_case": self.use_case,
            "aria2c_options": self.aria2c_options,
            "trackers": self.trackers,
            "retry_escalation": self.retry_escalation,
        }


# Built-in profiles (production-ready defaults)
BUILTIN_PROFILES: Dict[str, Profile] = {
    "default": Profile(
        name="default",
        description="Balanced profile for general use",
        use_case="Popular torrents with 10+ seeders",
        aria2c_options={
            "max-connection-per-server": 8,
            "split": 8,
            "bt-max-peers": 55,
            "enable-dht": True,
            "enable-ipv6": True,
            "bt-enable-lpd": True,
            "enable-peer-exchange": True,
            "check-integrity": True,
            "file-allocation": "prealloc",
            "seed-time": 15,  # 15 minutes
            "seed-ratio": 0.5,
        },
        trackers=["best"],
        retry_escalation=False,
    ),
    "rare": Profile(
        name="rare",
        description="Aggressive peer discovery for rare/dead torrents",
        use_case="Torrents with 0-10 seeders, rare content",
        aria2c_options={
            "max-connection-per-server": 16,
            "split": 16,
            "bt-max-peers": 200,
            "bt-request-peer-speed-limit": 0,
            "enable-dht": True,
            "enable-ipv6": True,
            "dht-entry-point": "router.bittorrent.com:6881",
            "dht-entry-point6": "router.bittorrent.com:6881",
            "bt-enable-lpd": True,
            "enable-peer-exchange": True,
            "check-integrity": True,
            "file-allocation": "prealloc",
            "seed-time": 30,
            "seed-ratio": 1.0,
        },
        trackers=["all"],  # Use comprehensive tracker lists
        retry_escalation=True,
    ),
    "fast": Profile(
        name="fast",
        description="Maximum speed for high-bandwidth connections",
        use_case="LAN downloads, very fast internet (100+ Mbps)",
        aria2c_options={
            "max-connection-per-server": 32,
            "split": 32,
            "max-overall-download-limit": 0,  # Unlimited
            "bt-max-peers": 100,
            "bt-request-peer-speed-limit": 0,
            "min-split-size": "1M",
            "enable-dht": True,
            "enable-ipv6": True,
            "check-integrity": True,
            "file-allocation": "none",  # Skip prealloc for speed
            "seed-time": 0,  # No seeding
        },
        trackers=["best"],
        retry_escalation=False,
    ),
    "seeder": Profile(
        name="seeder",
        description="Download and seed aggressively",
        use_case="Contributing back to swarm, long-term seeding",
        aria2c_options={
            "max-connection-per-server": 8,
            "split": 8,
            "bt-max-peers": 100,
            "enable-dht": True,
            "enable-ipv6": True,
            "check-integrity": True,
            "file-allocation": "prealloc",
            "seed-time": 1440,  # 24 hours
            "seed-ratio": 2.0,
        },
        trackers=["best"],
        retry_escalation=False,
    ),
    "privacy": Profile(
        name="privacy",
        description="VPN-friendly, minimal tracker exposure",
        use_case="Privacy-conscious users, VPN connections",
        aria2c_options={
            "max-connection-per-server": 8,
            "split": 8,
            "bt-max-peers": 50,
            "enable-dht": False,  # Disable DHT for privacy
            "bt-enable-lpd": False,  # Disable local peer discovery
            "enable-peer-exchange": False,  # Disable PEX
            "follow-torrent": "mem",  # Store metadata in memory
            "check-integrity": True,
            "file-allocation": "prealloc",
            "seed-time": 0,
        },
        trackers=["best"],
        retry_escalation=False,
    ),
    "batch": Profile(
        name="batch",
        description="Download multiple torrents concurrently",
        use_case="Batch downloads, server environments",
        aria2c_options={
            "max-connection-per-server": 4,
            "split": 4,
            "bt-max-peers": 30,
            "max-concurrent-downloads": 5,
            "bt-max-open-files": 50,
            "enable-dht": True,
            "enable-ipv6": True,
            "check-integrity": True,
            "file-allocation": "prealloc",
            "seed-time": 0,
        },
        trackers=["best"],
        retry_escalation=False,
    ),
}


@dataclass
class Config:
    """Main configuration container."""

    # General settings
    default_profile: str = "auto"
    download_dir: Path = field(default_factory=lambda: Path.home() / "Downloads")
    tracker_update_interval: int = 86400  # 24 hours in seconds

    # UI settings
    ui_theme: str = "cyberpunk"
    ui_mode: str = "interactive"  # interactive | quiet | json
    notify_level: str = "important"  # all | important | none

    # aria2c global overrides (applied to all profiles)
    max_download_speed: Optional[str] = None  # e.g., "10M"
    disk_cache: str = "16M"

    # Seeding defaults (profile can override)
    seed_time: int = 15  # minutes
    seed_ratio: float = 0.5

    # User-defined profiles (merged with built-in)
    custom_profiles: Dict[str, Profile] = field(default_factory=dict)

    @staticmethod
    def default() -> "Config":
        """Create default configuration."""
        return Config()

    @classmethod
    def from_toml(cls, toml_str: str) -> "Config":
        """Load configuration from TOML string."""
        data = tomllib.loads(toml_str)

        # Parse custom profiles
        custom_profiles = {}
        if "profiles" in data:
            for name, profile_data in data["profiles"].items():
                if name not in BUILTIN_PROFILES:  # Don't override built-ins
                    custom_profiles[name] = Profile(
                        name=name,
                        description=profile_data.get("description", ""),
                        use_case=profile_data.get("use_case", ""),
                        aria2c_options=profile_data.get("aria2c_options", {}),
                        trackers=profile_data.get("trackers", ["best"]),
                        retry_escalation=profile_data.get("retry_escalation", False),
                    )

        return cls(
            default_profile=data.get("general", {}).get("default_profile", "auto"),
            download_dir=Path(
                data.get("general", {}).get(
                    "download_dir", str(Path.home() / "Downloads")
                )
            ),
            tracker_update_interval=data.get("general", {}).get(
                "tracker_update_interval", 86400
            ),
            ui_theme=data.get("ui", {}).get("theme", "cyberpunk"),
            ui_mode=data.get("ui", {}).get("mode", "interactive"),
            notify_level=data.get("notifications", {}).get("level", "important"),
            max_download_speed=data.get("aria2c", {}).get("max_overall_download_limit"),
            disk_cache=data.get("aria2c", {}).get("disk_cache", "16M"),
            seed_time=data.get("general", {}).get("seed_time", 15),
            seed_ratio=data.get("general", {}).get("seed_ratio", 0.5),
            custom_profiles=custom_profiles,
        )

    def to_toml(self) -> str:
        """Serialize to TOML string."""
        data = {
            "general": {
                "default_profile": self.default_profile,
                "download_dir": str(self.download_dir),
                "tracker_update_interval": self.tracker_update_interval,
                "seed_time": self.seed_time,
                "seed_ratio": self.seed_ratio,
            },
            "ui": {
                "theme": self.ui_theme,
                "mode": self.ui_mode,
            },
            "notifications": {
                "level": self.notify_level,
            },
            "aria2c": {
                "disk_cache": self.disk_cache,
            },
        }

        if self.max_download_speed:
            data["aria2c"]["max_overall_download_limit"] = self.max_download_speed

        # Add custom profiles
        if self.custom_profiles:
            data["profiles"] = {
                name: profile.to_dict() for name, profile in self.custom_profiles.items()
            }

        return tomli_w.dumps(data)

    def get_profile(self, name: str) -> Profile:
        """Get profile by name (built-in or custom)."""
        if name in BUILTIN_PROFILES:
            return BUILTIN_PROFILES[name]
        if name in self.custom_profiles:
            return self.custom_profiles[name]
        raise ValueError(f"Unknown profile: {name}")

    def get_all_profiles(self) -> Dict[str, Profile]:
        """Get all available profiles (built-in + custom)."""
        return {**BUILTIN_PROFILES, **self.custom_profiles}


def load_config() -> Config:
    """
    Load configuration from multiple sources with priority:
    1. Built-in defaults
    2. User config file (~/.config/torrentcli/config.toml)
    3. Environment variables (TORRENTCLI_*)

    CLI flags override in cli.py after this function returns.
    """
    # Start with defaults
    config = Config.default()

    # Load from config file if exists
    config_path = Path.home() / ".config" / "torrentcli" / "config.toml"
    if config_path.exists():
        try:
            toml_str = config_path.read_text()
            config = Config.from_toml(toml_str)
        except Exception as e:
            # Non-fatal: warn and use defaults
            print(f"⚠️  Warning: Failed to load config from {config_path}: {e}")
            print("   Using defaults.")

    # Override with environment variables
    if "TORRENTCLI_PROFILE" in os.environ:
        config.default_profile = os.environ["TORRENTCLI_PROFILE"]
    if "TORRENTCLI_DOWNLOAD_DIR" in os.environ:
        config.download_dir = Path(os.environ["TORRENTCLI_DOWNLOAD_DIR"])
    if "TORRENTCLI_THEME" in os.environ:
        config.ui_theme = os.environ["TORRENTCLI_THEME"]
    if "TORRENTCLI_QUIET" in os.environ and os.environ["TORRENTCLI_QUIET"] == "1":
        config.ui_mode = "quiet"
    if "TORRENTCLI_NOTIFY" in os.environ:
        config.notify_level = os.environ["TORRENTCLI_NOTIFY"]

    return config
