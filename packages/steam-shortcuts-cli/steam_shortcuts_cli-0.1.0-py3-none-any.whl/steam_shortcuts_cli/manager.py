"""High-level manager for Steam shortcuts."""

import os
import platform
from pathlib import Path

from .crc import generate_shortcut_id, generate_steam_url
from .models import ShortcutsFile, SteamShortcut
from .vdf import VDFFormatter, VDFParseError, VDFParser


class ShortcutNotFoundError(Exception):
    """Raised when a shortcut cannot be found."""


class ShortcutExistsError(Exception):
    """Raised when trying to add a duplicate shortcut."""


class SteamNotFoundError(Exception):
    """Raised when Steam installation cannot be found."""


def find_steam_path() -> Path | None:
    """Attempt to find the Steam installation directory."""
    system = platform.system()

    if system == "Windows":
        candidates = [
            Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)")) / "Steam",
            Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Steam",
        ]
    elif system == "Darwin":  # macOS
        candidates = [
            Path.home() / "Library/Application Support/Steam",
        ]
    else:  # Linux
        candidates = [
            Path.home() / ".steam/steam",
            Path.home() / ".local/share/Steam",
            Path.home() / ".steam",
        ]

    for path in candidates:
        if path.exists():
            return path

    return None


def find_shortcuts_file(steam_path: Path | None = None, user_id: str | None = None) -> Path | None:
    """Find the shortcuts.vdf file for a Steam user.

    Args:
        steam_path: Path to Steam installation (auto-detected if None)
        user_id: Steam user ID (uses first found if None)

    Returns:
        Path to shortcuts.vdf or None if not found
    """
    if steam_path is None:
        steam_path = find_steam_path()
        if steam_path is None:
            return None

    userdata = steam_path / "userdata"
    if not userdata.exists():
        return None

    if user_id:
        shortcuts_file = userdata / user_id / "config" / "shortcuts.vdf"
        if shortcuts_file.exists():
            return shortcuts_file
        return None

    # Find first user directory with shortcuts.vdf
    for user_dir in userdata.iterdir():
        if user_dir.is_dir():
            shortcuts_file = user_dir / "config" / "shortcuts.vdf"
            if shortcuts_file.exists():
                return shortcuts_file

    # Check if any user directory exists (shortcuts.vdf might not exist yet)
    for user_dir in userdata.iterdir():
        if user_dir.is_dir():
            config_dir = user_dir / "config"
            if config_dir.exists():
                return config_dir / "shortcuts.vdf"

    return None


class SteamShortcutManager:
    """Manager for Steam non-Steam game shortcuts.

    Provides a high-level API for adding, removing, and listing shortcuts.
    """

    def __init__(self, shortcuts_file: Path | str | None = None):
        """Initialize the manager.

        Args:
            shortcuts_file: Path to shortcuts.vdf. Auto-detected if None.
        """
        self._parser = VDFParser()
        self._formatter = VDFFormatter()
        self._shortcuts_file: Path | None = None
        self._shortcuts: ShortcutsFile = ShortcutsFile()

        if shortcuts_file is not None:
            self._shortcuts_file = Path(shortcuts_file)
        else:
            self._shortcuts_file = find_shortcuts_file()

        if self._shortcuts_file and self._shortcuts_file.exists():
            self._load()

    @property
    def file_path(self) -> Path | None:
        """The path to the shortcuts.vdf file."""
        return self._shortcuts_file

    @property
    def shortcuts(self) -> list[SteamShortcut]:
        """List of all shortcuts."""
        return self._shortcuts.shortcuts

    def _load(self) -> None:
        """Load shortcuts from file."""
        if self._shortcuts_file and self._shortcuts_file.exists():
            try:
                self._shortcuts = self._parser.parse_file(self._shortcuts_file)
            except VDFParseError:
                self._shortcuts = ShortcutsFile()

    def save(self, path: Path | str | None = None) -> None:
        """Save shortcuts to file.

        Args:
            path: Path to save to. Uses the loaded file path if None.
        """
        if path is not None:
            save_path = Path(path)
        elif self._shortcuts_file is not None:
            save_path = self._shortcuts_file
        else:
            raise ValueError("No file path specified")

        # Ensure parent directory exists
        save_path.parent.mkdir(parents=True, exist_ok=True)
        self._formatter.format_file(self._shortcuts, save_path)

    def add(
        self,
        appname: str,
        exe: str,
        *,
        start_dir: str = "",
        icon: str = "",
        launch_options: str = "",
        tags: list[str] | None = None,
        is_hidden: bool = False,
        allow_overlay: bool = True,
        allow_desktop_config: bool = True,
        openvr: bool = False,
    ) -> SteamShortcut:
        """Add a new shortcut.

        Args:
            appname: Display name for the shortcut
            exe: Path to the executable
            start_dir: Working directory (defaults to exe's directory)
            icon: Path to icon file
            launch_options: Command line arguments
            tags: Category tags
            is_hidden: Whether to hide the shortcut
            allow_overlay: Allow Steam overlay
            allow_desktop_config: Allow controller desktop config
            openvr: Show in VR library

        Returns:
            The created SteamShortcut

        Raises:
            ShortcutExistsError: If a shortcut with the same name exists
        """
        # Check for existing shortcut with same name
        for existing in self._shortcuts.shortcuts:
            if existing.appname.lower() == appname.lower():
                raise ShortcutExistsError(f"Shortcut '{appname}' already exists")

        # Auto-detect start_dir if not provided
        if not start_dir:
            exe_path = Path(exe.strip('"'))
            if exe_path.parent.exists():
                start_dir = f'"{exe_path.parent}"'

        # Ensure exe is quoted if it contains spaces and isn't already quoted
        if " " in exe and not (exe.startswith('"') and exe.endswith('"')):
            exe = f'"{exe}"'

        shortcut = SteamShortcut(
            appname=appname,
            exe=exe,
            start_dir=start_dir,
            icon=icon,
            launch_options=launch_options,
            tags=tags or [],
            is_hidden=is_hidden,
            allow_overlay=allow_overlay,
            allow_desktop_config=allow_desktop_config,
            openvr=openvr,
        )

        self._shortcuts.shortcuts.append(shortcut)
        return shortcut

    def remove(self, appname: str) -> SteamShortcut:
        """Remove a shortcut by name.

        Args:
            appname: Name of the shortcut to remove

        Returns:
            The removed SteamShortcut

        Raises:
            ShortcutNotFoundError: If the shortcut doesn't exist
        """
        for i, shortcut in enumerate(self._shortcuts.shortcuts):
            if shortcut.appname.lower() == appname.lower():
                return self._shortcuts.shortcuts.pop(i)

        raise ShortcutNotFoundError(f"Shortcut '{appname}' not found")

    def get(self, appname: str) -> SteamShortcut | None:
        """Get a shortcut by name.

        Args:
            appname: Name of the shortcut

        Returns:
            The SteamShortcut or None if not found
        """
        for shortcut in self._shortcuts.shortcuts:
            if shortcut.appname.lower() == appname.lower():
                return shortcut
        return None

    def get_steam_url(self, appname: str) -> str | None:
        """Get the steam:// URL for a shortcut.

        Args:
            appname: Name of the shortcut

        Returns:
            The steam://rungameid/### URL or None if not found
        """
        shortcut = self.get(appname)
        if shortcut:
            return generate_steam_url(shortcut.exe, shortcut.appname)
        return None

    def get_shortcut_id(self, appname: str) -> int | None:
        """Get the Steam shortcut ID for a shortcut.

        Args:
            appname: Name of the shortcut

        Returns:
            The 64-bit shortcut ID or None if not found
        """
        shortcut = self.get(appname)
        if shortcut:
            return generate_shortcut_id(shortcut.exe, shortcut.appname)
        return None

    def clear(self) -> None:
        """Remove all shortcuts."""
        self._shortcuts.shortcuts.clear()

    def __len__(self) -> int:
        return len(self._shortcuts.shortcuts)

    def __iter__(self):
        return iter(self._shortcuts.shortcuts)

    def __contains__(self, appname: str) -> bool:
        return self.get(appname) is not None
