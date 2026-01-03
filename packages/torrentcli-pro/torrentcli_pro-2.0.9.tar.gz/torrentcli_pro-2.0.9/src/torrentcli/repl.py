"""
Interactive REPL (Read-Eval-Print Loop) for TorrentCLI Pro.

Provides a command-line interface with readline support for history,
command parsing, and interactive torrent management via aria2c RPC.

Supports:
- Magnet URIs, HTTP/HTTPS URLs, .torrent files, .metalink files
- Info hash to magnet conversion
- RPC secret/token authentication
- Auto-reconnect on connection loss
- Filter by status or name
- Per-download and global options
"""

import atexit
import base64
import re
import readline
import shlex
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import quote

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from torrentcli.config import Config, load_config
from torrentcli.tui.theme import THEMES, get_theme


# Example magnet link for documentation and help
EXAMPLE_MAGNET = (
    "magnet:?xt=urn:btih:dd8255ecdc7ca55fb0bbf81323d87062db1f6d1c"
    "&dn=Big+Buck+Bunny"
    "&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce"
)


class CommandType(Enum):
    """Types of REPL commands."""
    ADD = "add"
    PAUSE = "pause"
    RESUME = "resume"
    REMOVE = "remove"
    LIST = "list"
    DETAILS = "details"
    FILTER = "filter"
    SET = "set"
    HELP = "help"
    QUIT = "quit"
    RETRY = "retry"


class SourceType(Enum):
    """Types of download sources."""
    MAGNET = "magnet"
    URL = "url"
    TORRENT_FILE = "torrent"
    METALINK_FILE = "metalink"
    INFO_HASH = "hash"


@dataclass
class ParsedCommand:
    """A parsed REPL command."""
    command_type: CommandType
    args: List[str]
    kwargs: Dict[str, str]
    raw: str


@dataclass
class CommandResult:
    """Result from executing a command."""
    success: bool
    message: str
    data: Optional[Any] = None


@dataclass
class FilterState:
    """Current filter state for list command."""
    status: Optional[str] = None
    name_pattern: Optional[str] = None

    def is_active(self) -> bool:
        return self.status is not None or self.name_pattern is not None

    def matches(self, download: Dict[str, Any]) -> bool:
        """Check if download matches current filter."""
        # Status filter
        if self.status:
            dl_status = download.get("status", download.get("_status", ""))
            if dl_status != self.status:
                return False

        # Name filter (case-insensitive substring)
        if self.name_pattern:
            name = ""
            if "bittorrent" in download and download["bittorrent"].get("info"):
                name = download["bittorrent"]["info"].get("name", "")
            elif "files" in download and download["files"]:
                name = Path(download["files"][0].get("path", "")).name
            if self.name_pattern.lower() not in name.lower():
                return False

        return True


class REPLBackend:
    """
    Backend interface for REPL operations.

    Interfaces with aria2c JSON-RPC with support for:
    - RPC secret/token authentication
    - Auto-reconnect on failure
    - .torrent and .metalink file uploads
    - Global and per-download options
    - Auto-start aria2c if not running
    """

    def __init__(
        self,
        config: Config,
        rpc_url: str = "http://localhost:6800/jsonrpc",
        rpc_secret: Optional[str] = None,
    ):
        self.config = config
        self.rpc_url = rpc_url
        self.rpc_secret = rpc_secret
        self._connected = False
        self._aria2_version: Optional[str] = None
        self._aria2_process: Optional[subprocess.Popen] = None
        self._we_started_aria2c = False

    def _find_aria2c(self) -> Optional[str]:
        """Find aria2c binary path."""
        return shutil.which("aria2c")

    def _start_aria2c(self) -> Tuple[bool, str]:
        """
        Start aria2c daemon with RPC enabled.

        Returns:
            Tuple of (success, message)
        """
        aria2c_path = self._find_aria2c()
        if not aria2c_path:
            return False, "aria2c not found. Install with: brew install aria2 (macOS) or apt install aria2 (Linux)"

        # Build aria2c command
        cmd = [
            aria2c_path,
            "--enable-rpc",
            "--rpc-listen-all=false",
            "--rpc-listen-port=6800",
            "--daemon=false",  # Run in foreground so we can manage it
            "--quiet=true",
            f"--dir={self.config.download_dir}",
        ]

        # Add RPC secret if configured
        if self.rpc_secret:
            cmd.append(f"--rpc-secret={self.rpc_secret}")

        try:
            # Start aria2c as subprocess
            self._aria2_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,  # Detach from terminal
            )
            self._we_started_aria2c = True

            # Register cleanup on exit
            atexit.register(self._stop_aria2c)

            # Wait for RPC to be ready (max 5 seconds)
            for _ in range(50):
                time.sleep(0.1)
                success, _ = self._make_rpc_call("aria2.getVersion", timeout=1.0)
                if success:
                    return True, "Started aria2c daemon"

            return False, "aria2c started but RPC not responding"

        except Exception as e:
            return False, f"Failed to start aria2c: {e}"

    def _stop_aria2c(self) -> None:
        """Stop aria2c if we started it."""
        if self._aria2_process and self._we_started_aria2c:
            try:
                # Try graceful shutdown via RPC first
                self._make_rpc_call("aria2.shutdown", timeout=2.0)
                self._aria2_process.wait(timeout=3)
            except Exception:
                # Force kill if graceful shutdown fails
                try:
                    self._aria2_process.terminate()
                    self._aria2_process.wait(timeout=2)
                except Exception:
                    self._aria2_process.kill()
            finally:
                self._aria2_process = None
                self._we_started_aria2c = False

    def ensure_aria2c_running(self) -> Tuple[bool, str]:
        """
        Ensure aria2c is running, starting it if necessary.

        Returns:
            Tuple of (success, message)
        """
        # First try to connect to existing aria2c
        success, result = self.connect()
        if success:
            return True, result

        # No existing aria2c, try to start one
        started, message = self._start_aria2c()
        if not started:
            return False, message

        # Now connect
        return self.connect()

    def _make_rpc_call(
        self,
        method: str,
        params: Optional[List[Any]] = None,
        timeout: float = 10.0,
    ) -> Tuple[bool, Any]:
        """
        Make an RPC call to aria2c with optional secret token.

        Returns:
            Tuple of (success, result_or_error)
        """
        import httpx

        # Prepend secret token if configured
        if params is None:
            params = []
        if self.rpc_secret:
            params = [f"token:{self.rpc_secret}"] + list(params)

        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": method,
        }

        try:
            response = httpx.post(self.rpc_url, json=payload, timeout=timeout)
            data = response.json()

            if "error" in data:
                error_msg = data["error"].get("message", "Unknown RPC error")
                # Mark as disconnected on certain errors
                if "Unauthorized" in error_msg or "connection" in error_msg.lower():
                    self._connected = False
                return False, error_msg

            if "result" in data:
                return True, data["result"]

            return False, "Unexpected RPC response format"

        except Exception as e:
            self._connected = False
            return False, str(e)

    def connect(self) -> Tuple[bool, str]:
        """
        Attempt to connect to aria2c RPC.

        Returns:
            Tuple of (success, message)
        """
        success, result = self._make_rpc_call("aria2.getVersion", timeout=5.0)

        if success:
            self._connected = True
            self._aria2_version = result.get("version", "unknown")
            return True, f"Connected to aria2c v{self._aria2_version}"
        else:
            self._connected = False
            return False, result

    def _try_reconnect(self) -> bool:
        """Attempt to reconnect if disconnected."""
        if self._connected:
            return True
        success, _ = self.connect()
        return success

    @property
    def is_connected(self) -> bool:
        return self._connected

    def add_uri(self, uris: List[str], options: Optional[Dict[str, Any]] = None) -> CommandResult:
        """Add download from URI(s) - magnet or HTTP/HTTPS."""
        if not self._try_reconnect():
            return CommandResult(False, "Not connected to aria2c RPC. Type 'retry' to reconnect.")

        params: List[Any] = [uris]
        if options:
            params.append(options)

        success, result = self._make_rpc_call("aria2.addUri", params)

        if success:
            return CommandResult(True, f"Added download with GID: {result}", {"gid": result})
        return CommandResult(False, f"Failed to add: {result}")

    def add_torrent(self, torrent_path: Path, options: Optional[Dict[str, Any]] = None) -> CommandResult:
        """Add download from .torrent file (base64 encoded)."""
        if not self._try_reconnect():
            return CommandResult(False, "Not connected to aria2c RPC. Type 'retry' to reconnect.")

        try:
            # Read and base64 encode the torrent file
            torrent_data = torrent_path.read_bytes()
            torrent_b64 = base64.b64encode(torrent_data).decode("ascii")

            # aria2.addTorrent params: [torrent, uris?, options?]
            # Must include empty uris list before options
            params: List[Any] = [torrent_b64]
            if options:
                params.append([])  # Empty uris list
                params.append(options)

            success, result = self._make_rpc_call("aria2.addTorrent", params)

            if success:
                return CommandResult(True, f"Added torrent with GID: {result}", {"gid": result})
            return CommandResult(False, f"Failed to add torrent: {result}")

        except Exception as e:
            return CommandResult(False, f"Failed to read torrent file: {e}")

    def add_metalink(self, metalink_path: Path, options: Optional[Dict[str, Any]] = None) -> CommandResult:
        """Add download from .metalink file (base64 encoded)."""
        if not self._try_reconnect():
            return CommandResult(False, "Not connected to aria2c RPC. Type 'retry' to reconnect.")

        try:
            # Read and base64 encode the metalink file
            metalink_data = metalink_path.read_bytes()
            metalink_b64 = base64.b64encode(metalink_data).decode("ascii")

            params: List[Any] = [metalink_b64]
            if options:
                params.append(options)

            success, result = self._make_rpc_call("aria2.addMetalink", params)

            if success:
                gids = result if isinstance(result, list) else [result]
                return CommandResult(True, f"Added metalink with GID(s): {', '.join(gids)}", {"gids": gids})
            return CommandResult(False, f"Failed to add metalink: {result}")

        except Exception as e:
            return CommandResult(False, f"Failed to read metalink file: {e}")

    def pause_download(self, gid: str) -> CommandResult:
        """Pause a download by GID."""
        if not self._try_reconnect():
            return CommandResult(False, "Not connected to aria2c RPC. Type 'retry' to reconnect.")

        success, result = self._make_rpc_call("aria2.pause", [gid])

        if success:
            return CommandResult(True, f"Paused download: {gid}")
        return CommandResult(False, f"Failed to pause: {result}")

    def resume_download(self, gid: str) -> CommandResult:
        """Resume a paused download."""
        if not self._try_reconnect():
            return CommandResult(False, "Not connected to aria2c RPC. Type 'retry' to reconnect.")

        success, result = self._make_rpc_call("aria2.unpause", [gid])

        if success:
            return CommandResult(True, f"Resumed download: {gid}")
        return CommandResult(False, f"Failed to resume: {result}")

    def remove_download(self, gid: str) -> CommandResult:
        """Remove a download."""
        if not self._try_reconnect():
            return CommandResult(False, "Not connected to aria2c RPC. Type 'retry' to reconnect.")

        success, result = self._make_rpc_call("aria2.remove", [gid])

        if success:
            return CommandResult(True, f"Removed download: {gid}")
        return CommandResult(False, f"Failed to remove: {result}")

    def list_downloads(self) -> CommandResult:
        """List all downloads (active, waiting, stopped)."""
        if not self._try_reconnect():
            return CommandResult(False, "Not connected to aria2c RPC. Type 'retry' to reconnect.")

        downloads = []
        warnings = []

        # Get active downloads
        success, result = self._make_rpc_call("aria2.tellActive")
        if success and isinstance(result, list):
            for item in result:
                item["_status"] = "active"
                downloads.append(item)
        elif not success:
            warnings.append(f"Failed to fetch active downloads: {result}")

        # Get waiting downloads
        success, result = self._make_rpc_call("aria2.tellWaiting", [0, 100])
        if success and isinstance(result, list):
            for item in result:
                item["_status"] = "waiting"
                downloads.append(item)
        elif not success:
            warnings.append(f"Failed to fetch waiting downloads: {result}")

        # Get stopped downloads
        success, result = self._make_rpc_call("aria2.tellStopped", [0, 100])
        if success and isinstance(result, list):
            for item in result:
                item["_status"] = "stopped"
                downloads.append(item)
        elif not success:
            warnings.append(f"Failed to fetch stopped downloads: {result}")

        # Build response with warnings if any
        data: Dict[str, Any] = {"downloads": downloads}
        if warnings:
            data["warnings"] = warnings
            message = f"Found {len(downloads)} downloads (with {len(warnings)} warning(s))"
        else:
            message = f"Found {len(downloads)} downloads"

        return CommandResult(True, message, data)

    def get_download_details(self, gid: str) -> CommandResult:
        """Get detailed info about a download."""
        if not self._try_reconnect():
            return CommandResult(False, "Not connected to aria2c RPC. Type 'retry' to reconnect.")

        success, result = self._make_rpc_call("aria2.tellStatus", [gid])

        if success:
            return CommandResult(True, "Download details", {"details": result})
        return CommandResult(False, f"Failed to get details: {result}")

    def set_option(self, gid: str, key: str, value: str) -> CommandResult:
        """Set a per-download option."""
        if not self._try_reconnect():
            return CommandResult(False, "Not connected to aria2c RPC. Type 'retry' to reconnect.")

        success, result = self._make_rpc_call("aria2.changeOption", [gid, {key: value}])

        if success:
            return CommandResult(True, f"Set {key}={value} for {gid}")
        return CommandResult(False, f"Failed to set option: {result}")

    def set_global_option(self, key: str, value: str) -> CommandResult:
        """Set a global aria2c option."""
        if not self._try_reconnect():
            return CommandResult(False, "Not connected to aria2c RPC. Type 'retry' to reconnect.")

        success, result = self._make_rpc_call("aria2.changeGlobalOption", [{key: value}])

        if success:
            return CommandResult(True, f"Set global {key}={value}")
        return CommandResult(False, f"Failed to set global option: {result}")

    def get_global_option(self, key: Optional[str] = None) -> CommandResult:
        """Get global aria2c options."""
        if not self._try_reconnect():
            return CommandResult(False, "Not connected to aria2c RPC. Type 'retry' to reconnect.")

        success, result = self._make_rpc_call("aria2.getGlobalOption")

        if success:
            if key:
                value = result.get(key, "<not set>")
                return CommandResult(True, f"{key}={value}", {"options": {key: value}})
            return CommandResult(True, "Global options", {"options": result})
        return CommandResult(False, f"Failed to get global options: {result}")


class CommandParser:
    """Parses user input into structured commands."""

    # Regex patterns
    MAGNET_PATTERN = re.compile(r'^magnet:\?', re.IGNORECASE)
    URL_PATTERN = re.compile(r'^https?://', re.IGNORECASE)
    INFO_HASH_PATTERN = re.compile(r'^[a-fA-F0-9]{40}$|^[a-zA-Z2-7]{32}$')
    TORRENT_FILE_PATTERN = re.compile(r'\.torrent$', re.IGNORECASE)
    METALINK_FILE_PATTERN = re.compile(r'\.(metalink|meta4)$', re.IGNORECASE)

    # Status values that can be used as filters
    VALID_STATUSES = {"active", "waiting", "paused", "complete", "error", "stopped", "removed"}

    @classmethod
    def parse(cls, input_str: str) -> Optional[ParsedCommand]:
        """
        Parse a raw input string into a ParsedCommand.

        IMPORTANT: Only parse key=value as kwargs for the SET command.
        For ADD, preserve URLs and paths exactly as provided.
        """
        input_str = input_str.strip()
        if not input_str:
            return None

        # Handle quit variants
        if input_str.lower() in ("quit", "exit", "q", ":q", ":wq"):
            return ParsedCommand(CommandType.QUIT, [], {}, input_str)

        # Handle help variants
        if input_str.lower() in ("help", "?", "h"):
            return ParsedCommand(CommandType.HELP, [], {}, input_str)

        # Handle retry
        if input_str.lower() == "retry":
            return ParsedCommand(CommandType.RETRY, [], {}, input_str)

        try:
            tokens = shlex.split(input_str)
        except ValueError:
            tokens = input_str.split()

        if not tokens:
            return None

        command = tokens[0].lower()
        args = tokens[1:]

        # Map command strings to types
        command_map = {
            "add": CommandType.ADD,
            "a": CommandType.ADD,
            "download": CommandType.ADD,
            "dl": CommandType.ADD,
            "pause": CommandType.PAUSE,
            "p": CommandType.PAUSE,
            "resume": CommandType.RESUME,
            "r": CommandType.RESUME,
            "unpause": CommandType.RESUME,
            "remove": CommandType.REMOVE,
            "rm": CommandType.REMOVE,
            "delete": CommandType.REMOVE,
            "del": CommandType.REMOVE,
            "list": CommandType.LIST,
            "ls": CommandType.LIST,
            "l": CommandType.LIST,
            "details": CommandType.DETAILS,
            "info": CommandType.DETAILS,
            "d": CommandType.DETAILS,
            "filter": CommandType.FILTER,
            "f": CommandType.FILTER,
            "set": CommandType.SET,
            "option": CommandType.SET,
            "help": CommandType.HELP,
            "?": CommandType.HELP,
            "h": CommandType.HELP,
            "quit": CommandType.QUIT,
            "exit": CommandType.QUIT,
            "q": CommandType.QUIT,
            "retry": CommandType.RETRY,
        }

        if command not in command_map:
            return None

        cmd_type = command_map[command]
        kwargs: Dict[str, str] = {}

        # Only parse key=value for SET command
        if cmd_type == CommandType.SET:
            remaining_args = []
            for arg in args:
                if "=" in arg:
                    key, value = arg.split("=", 1)
                    kwargs[key] = value
                else:
                    remaining_args.append(arg)
            args = remaining_args

        return ParsedCommand(
            command_type=cmd_type,
            args=args,
            kwargs=kwargs,
            raw=input_str,
        )

    @classmethod
    def hash_to_magnet(cls, info_hash: str, name: Optional[str] = None) -> str:
        """Convert an info hash to a magnet URI."""
        magnet = f"magnet:?xt=urn:btih:{info_hash}"
        if name:
            magnet += f"&dn={quote(name)}"
        return magnet

    @classmethod
    def validate_magnet(cls, uri: str) -> Tuple[bool, str]:
        """Validate a magnet URI."""
        if not uri.startswith("magnet:?"):
            return False, "Invalid magnet URI: must start with 'magnet:?'"

        if "xt=urn:btih:" not in uri.lower():
            return False, "Invalid magnet URI: missing 'xt=urn:btih:' parameter"

        match = re.search(r'xt=urn:btih:([a-zA-Z0-9]+)', uri, re.IGNORECASE)
        if not match:
            return False, "Invalid magnet URI: could not extract info hash"

        info_hash = match.group(1)

        # Check constraints based on length
        if len(info_hash) == 40:
            # Must be Hex
            if not re.match(r'^[0-9a-fA-F]{40}$', info_hash):
                 return False, "Invalid 40-char info hash: must be Hex (0-9, A-F)"
        elif len(info_hash) == 32:
            # Must be Base32 (RFC 4648)
            if not re.match(r'^[a-z2-7]{32}$', info_hash, re.IGNORECASE):
                return False, "Invalid 32-char info hash: must be Base32 (a-z, 2-7)"
        else:
            return False, f"Invalid info hash length: expected 32 or 40, got {len(info_hash)}"

        return True, info_hash

    @classmethod
    def classify_source(cls, source: str) -> Tuple[SourceType, str]:
        """
        Classify and validate a download source.

        Returns:
            Tuple of (SourceType, processed_source_or_error)
        """
        # Check for magnet URI
        if cls.MAGNET_PATTERN.match(source):
            is_valid, result = cls.validate_magnet(source)
            if is_valid:
                return SourceType.MAGNET, source
            return SourceType.MAGNET, f"Error: {result}"

        # Check for HTTP/HTTPS URL
        if cls.URL_PATTERN.match(source):
            return SourceType.URL, source

        # Check for bare info hash (40 hex chars or 32 base32 chars)
        if cls.INFO_HASH_PATTERN.match(source):
            magnet = cls.hash_to_magnet(source)
            return SourceType.INFO_HASH, magnet

        # Check for .torrent file
        if cls.TORRENT_FILE_PATTERN.search(source):
            path = Path(source).expanduser().resolve()
            if path.exists():
                return SourceType.TORRENT_FILE, str(path)
            return SourceType.TORRENT_FILE, f"Error: File not found: {source}"

        # Check for .metalink file
        if cls.METALINK_FILE_PATTERN.search(source):
            path = Path(source).expanduser().resolve()
            if path.exists():
                return SourceType.METALINK_FILE, str(path)
            return SourceType.METALINK_FILE, f"Error: File not found: {source}"

        return SourceType.URL, f"Error: Unknown source type: {source}"


class REPL:
    """
    Interactive REPL for TorrentCLI Pro.

    Features:
    - Readline history with arrow key navigation
    - Tab completion for commands
    - Auto-reconnect on aria2c restart
    - Filter by status or name
    - Support for .torrent, .metalink, magnet, URL, and info hash
    """

    HISTORY_FILE = Path.home() / ".torrentcli_history"
    MAX_HISTORY = 1000

    def __init__(
        self,
        config: Optional[Config] = None,
        backend: Optional[REPLBackend] = None,
        console: Optional[Console] = None,
        rpc_secret: Optional[str] = None,
    ):
        self.config = config or load_config()
        self.rpc_secret = rpc_secret
        self.backend = backend or REPLBackend(self.config, rpc_secret=rpc_secret)
        self.console = console or Console()
        self.theme = get_theme(self.config.ui_theme)
        self.running = False
        self._filter = FilterState()

        self._setup_readline()

    def _setup_readline(self) -> None:
        """Configure readline for history and completion."""
        try:
            if self.HISTORY_FILE.exists():
                readline.read_history_file(str(self.HISTORY_FILE))
        except Exception:
            pass

        readline.set_history_length(self.MAX_HISTORY)
        readline.set_completer(self._completer)
        readline.parse_and_bind("tab: complete")

    def _save_history(self) -> None:
        """Save readline history to file."""
        try:
            readline.write_history_file(str(self.HISTORY_FILE))
        except Exception:
            pass

    def _completer(self, text: str, state: int) -> Optional[str]:
        """Tab completion for commands."""
        commands = [
            "add", "pause", "resume", "remove", "list",
            "details", "filter", "set", "help", "quit", "retry"
        ]
        matches = [c for c in commands if c.startswith(text.lower())]
        return matches[state] if state < len(matches) else None

    def _print_banner(self) -> None:
        """Print the REPL welcome banner."""
        banner = Text()
        banner.append("▓▓▓▓ ", style=self.theme.colors.download_color)
        banner.append("TORRENTCLI PRO REPL", style=f"bold {self.theme.colors.text_primary}")
        banner.append("\n")
        banner.append("Interactive torrent management. Type 'help' for commands.",
                     style=self.theme.colors.text_secondary)

        self.console.print(Panel(banner, border_style=self.theme.colors.border))

    def _print_connection_error(self, error_msg: str) -> None:
        """Print aria2c connection error with actionable guidance."""
        rpc_note = ""
        if self.rpc_secret:
            rpc_note = f"\n[dim]Using RPC secret: {self.rpc_secret[:4]}...[/dim]"

        error_panel = Panel(
            f"""[bold red]Could not connect to aria2c RPC[/bold red]

[yellow]Error:[/yellow] {error_msg}{rpc_note}

[bold]To start aria2c with RPC enabled:[/bold]

  aria2c --enable-rpc --rpc-listen-all=true --rpc-allow-origin-all

[bold]With RPC secret:[/bold]

  aria2c --enable-rpc --rpc-secret=YOUR_SECRET

[bold]In daemon mode:[/bold]

  aria2c --enable-rpc --daemon

[bold]To reconnect:[/bold]
  Type 'retry' or just press Enter""",
            title="Connection Error",
            border_style="red",
        )
        self.console.print(error_panel)

    def _print_help(self) -> None:
        """Print help message with all commands."""
        help_table = Table(
            title="REPL Commands",
            show_header=True,
            header_style=f"bold {self.theme.colors.accent_info}",
        )
        help_table.add_column("Command", style="bold")
        help_table.add_column("Alias", style="dim")
        help_table.add_column("Description")
        help_table.add_column("Example")

        commands = [
            ("add", "a, dl", "Add download (magnet/URL/hash/file)",
             "add <magnet|URL|hash|.torrent|.metalink>"),
            ("pause", "p", "Pause a download by GID", "pause abc123"),
            ("resume", "r", "Resume a paused download", "resume abc123"),
            ("remove", "rm, del", "Remove a download", "remove abc123"),
            ("list", "ls, l", "List all downloads", "list"),
            ("details", "d, info", "Show download details", "details abc123"),
            ("filter", "f", "Filter by status or name", "filter active  OR  filter ubuntu"),
            ("set", "option", "Set option (per-download or global)",
             "set abc123 max-download-limit=1M\nset global max-overall-download-limit=5M"),
            ("retry", "", "Reconnect to aria2c", "retry"),
            ("help", "?, h", "Show this help", "help"),
            ("quit", "q, exit", "Exit the REPL", "quit"),
        ]

        for cmd, alias, desc, example in commands:
            help_table.add_row(cmd, alias, desc, example)

        self.console.print(help_table)

        # Supported source types
        self.console.print()
        self.console.print(Panel(
            """[bold]Supported source types for 'add':[/bold]

• Magnet URI:  magnet:?xt=urn:btih:...
• HTTP/HTTPS:  https://example.com/file.torrent
• Info hash:   dd8255ecdc7ca55fb0bbf81323d87062db1f6d1c
• Torrent:     /path/to/file.torrent
• Metalink:    /path/to/file.metalink

[bold]Example magnet (Big Buck Bunny):[/bold]
""" + EXAMPLE_MAGNET,
            title="Download Sources",
            border_style=self.theme.colors.accent_info,
        ))

    def _get_download_name(self, dl: Dict[str, Any]) -> str:
        """Extract name from download info."""
        if "bittorrent" in dl and dl["bittorrent"].get("info"):
            return dl["bittorrent"]["info"].get("name", "Unknown")
        if "files" in dl and dl["files"]:
            return Path(dl["files"][0].get("path", "Unknown")).name
        return "Unknown"

    def _format_downloads_table(self, downloads: List[Dict[str, Any]]) -> Table:
        """Format downloads list as a Rich table."""
        table = Table(
            show_header=True,
            header_style=f"bold {self.theme.colors.accent_info}",
        )
        table.add_column("GID", style="dim", width=16)
        table.add_column("Name", width=40)
        table.add_column("Progress", width=12)
        table.add_column("Speed", width=12)
        table.add_column("Status", width=10)

        for dl in downloads:
            gid = dl.get("gid", "?")[:16]
            name = self._get_download_name(dl)
            name = (name[:37] + "...") if len(name) > 40 else name

            total = int(dl.get("totalLength", 0))
            completed = int(dl.get("completedLength", 0))
            progress = f"{(completed / total) * 100:.1f}%" if total > 0 else "0%"

            speed = int(dl.get("downloadSpeed", 0))
            if speed >= 1024 * 1024:
                speed_str = f"{speed / (1024 * 1024):.1f} MiB/s"
            elif speed >= 1024:
                speed_str = f"{speed / 1024:.1f} KiB/s"
            else:
                speed_str = f"{speed} B/s"

            status = dl.get("status", dl.get("_status", "?"))
            status_color = {
                "active": self.theme.colors.accent_success,
                "waiting": self.theme.colors.accent_warning,
                "paused": self.theme.colors.accent_warning,
                "complete": self.theme.colors.accent_success,
                "error": self.theme.colors.accent_error,
                "stopped": self.theme.colors.text_dim,
            }.get(status, self.theme.colors.text_primary)

            table.add_row(gid, name, progress, speed_str, f"[{status_color}]{status}[/]")

        return table

    def _execute_command(self, cmd: ParsedCommand) -> bool:
        """Execute a parsed command. Returns False to exit REPL."""

        if cmd.command_type == CommandType.QUIT:
            self.console.print("[yellow]Goodbye![/yellow]")
            return False

        if cmd.command_type == CommandType.RETRY:
            connected, message = self.backend.connect()
            if connected:
                self.console.print(f"[green]{message}[/green]")
            else:
                self._print_connection_error(message)
            return True

        if cmd.command_type == CommandType.HELP:
            self._print_help()
            return True

        if cmd.command_type == CommandType.ADD:
            if not cmd.args:
                self.console.print("[red]Usage: add <magnet|URL|hash|.torrent|.metalink>[/red]")
                return True

            source = cmd.args[0]
            source_type, processed = CommandParser.classify_source(source)

            if processed.startswith("Error:"):
                self.console.print(f"[red]{processed}[/red]")
                return True

            # Route to appropriate backend method
            if source_type == SourceType.TORRENT_FILE:
                result = self.backend.add_torrent(Path(processed))
            elif source_type == SourceType.METALINK_FILE:
                result = self.backend.add_metalink(Path(processed))
            else:
                # MAGNET, URL, or INFO_HASH (converted to magnet)
                result = self.backend.add_uri([processed])

            if result.success:
                self.console.print(f"[green]{result.message}[/green]")
            else:
                self.console.print(f"[red]{result.message}[/red]")
            return True

        if cmd.command_type == CommandType.PAUSE:
            if not cmd.args:
                self.console.print("[red]Usage: pause <GID>[/red]")
                return True
            result = self.backend.pause_download(cmd.args[0])
            color = "green" if result.success else "red"
            self.console.print(f"[{color}]{result.message}[/]")
            return True

        if cmd.command_type == CommandType.RESUME:
            if not cmd.args:
                self.console.print("[red]Usage: resume <GID>[/red]")
                return True
            result = self.backend.resume_download(cmd.args[0])
            color = "green" if result.success else "red"
            self.console.print(f"[{color}]{result.message}[/]")
            return True

        if cmd.command_type == CommandType.REMOVE:
            if not cmd.args:
                self.console.print("[red]Usage: remove <GID>[/red]")
                return True
            result = self.backend.remove_download(cmd.args[0])
            color = "green" if result.success else "red"
            self.console.print(f"[{color}]{result.message}[/]")
            return True

        if cmd.command_type == CommandType.LIST:
            result = self.backend.list_downloads()
            if not result.success:
                self.console.print(f"[red]{result.message}[/red]")
                return True

            downloads = result.data.get("downloads", [])

            # Apply filter
            if self._filter.is_active():
                downloads = [d for d in downloads if self._filter.matches(d)]
                filter_desc = []
                if self._filter.status:
                    filter_desc.append(f"status={self._filter.status}")
                if self._filter.name_pattern:
                    filter_desc.append(f"name contains '{self._filter.name_pattern}'")
                self.console.print(f"[dim]Filter: {', '.join(filter_desc)}[/dim]")

            if downloads:
                table = self._format_downloads_table(downloads)
                self.console.print(table)
            else:
                self.console.print("[dim]No downloads found.[/dim]")
            return True

        if cmd.command_type == CommandType.DETAILS:
            if not cmd.args:
                self.console.print("[red]Usage: details <GID>[/red]")
                return True
            result = self.backend.get_download_details(cmd.args[0])
            if result.success:
                self.console.print_json(data=result.data.get("details", {}))
            else:
                self.console.print(f"[red]{result.message}[/red]")
            return True

        if cmd.command_type == CommandType.FILTER:
            if not cmd.args:
                self._filter = FilterState()
                self.console.print("[green]Filter cleared[/green]")
                return True

            filter_value = cmd.args[0].lower()

            # Check if it's a status filter
            if filter_value in CommandParser.VALID_STATUSES:
                self._filter = FilterState(status=filter_value)
                self.console.print(f"[green]Filter set: status={filter_value}[/green]")
            else:
                # Treat as name filter
                self._filter = FilterState(name_pattern=cmd.args[0])
                self.console.print(f"[green]Filter set: name contains '{cmd.args[0]}'[/green]")
            return True

        if cmd.command_type == CommandType.SET:
            # Check for 'set global ...' pattern
            if cmd.args and cmd.args[0].lower() == "global":
                if not cmd.kwargs:
                    # Show global options
                    result = self.backend.get_global_option()
                    if result.success:
                        self.console.print("[bold]Global options:[/bold]")
                        for k, v in sorted(result.data.get("options", {}).items()):
                            self.console.print(f"  {k}={v}")
                    else:
                        self.console.print(f"[red]{result.message}[/red]")
                else:
                    for key, value in cmd.kwargs.items():
                        result = self.backend.set_global_option(key, value)
                        color = "green" if result.success else "red"
                        self.console.print(f"[{color}]{result.message}[/]")
                return True

            # Per-download option
            if not cmd.args:
                self.console.print("[red]Usage: set <GID> <key>=<value>  OR  set global <key>=<value>[/red]")
                return True

            gid = cmd.args[0]
            if not cmd.kwargs:
                self.console.print("[red]Usage: set <GID> <key>=<value>[/red]")
                return True

            for key, value in cmd.kwargs.items():
                result = self.backend.set_option(gid, key, value)
                color = "green" if result.success else "red"
                self.console.print(f"[{color}]{result.message}[/]")
            return True

        return True

    def run(self) -> None:
        """Run the interactive REPL loop."""
        self._print_banner()

        # Auto-start aria2c if not running
        self.console.print("[dim]Connecting to aria2c...[/dim]")
        connected, message = self.backend.ensure_aria2c_running()
        if connected:
            if self.backend._we_started_aria2c:
                self.console.print(f"[green]Started aria2c automatically. {message}[/green]\n")
            else:
                self.console.print(f"[green]{message}[/green]\n")
        else:
            self._print_connection_error(message)

        self.running = True
        prompt = f"[{self.theme.colors.download_color}]torrentcli>[/] "

        try:
            while self.running:
                try:
                    user_input = self.console.input(prompt)

                    # Empty input when disconnected = retry with auto-start
                    if not user_input.strip() and not self.backend.is_connected:
                        connected, message = self.backend.ensure_aria2c_running()
                        if connected:
                            self.console.print(f"[green]{message}[/green]")
                        else:
                            self._print_connection_error(message)
                        continue

                    if not user_input.strip():
                        continue

                    cmd = CommandParser.parse(user_input)
                    if cmd is None:
                        self.console.print(f"[red]Unknown command: {user_input.split()[0]}. Type 'help' for usage.[/red]")
                        continue

                    if not self._execute_command(cmd):
                        self.running = False

                except KeyboardInterrupt:
                    self.console.print("\n[yellow]Type 'quit' to exit[/yellow]")
                except EOFError:
                    self.running = False
        finally:
            self._save_history()
            # Stop aria2c if we started it
            if self.backend._we_started_aria2c:
                self.console.print("[dim]Stopping aria2c...[/dim]")
                self.backend._stop_aria2c()


def run_repl(config: Optional[Config] = None, rpc_secret: Optional[str] = None) -> None:
    """Entry point for running the REPL."""
    repl = REPL(config=config, rpc_secret=rpc_secret)
    repl.run()
