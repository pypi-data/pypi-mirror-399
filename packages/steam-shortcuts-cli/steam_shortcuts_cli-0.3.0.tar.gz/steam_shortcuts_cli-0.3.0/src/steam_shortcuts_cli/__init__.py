"""Steam Shortcuts CLI - Manage Steam non-Steam game shortcuts."""

from .crc import generate_shortcut_id, generate_steam_url
from .manager import (
    ShortcutExistsError,
    ShortcutNotFoundError,
    SteamNotFoundError,
    SteamShortcutManager,
    find_shortcuts_file,
    find_steam_path,
)
from .models import ShortcutsFile, SteamShortcut
from .vdf import VDFFormatter, VDFParseError, VDFParser

__all__ = [
    # Models
    "SteamShortcut",
    "ShortcutsFile",
    # Manager
    "SteamShortcutManager",
    "ShortcutExistsError",
    "ShortcutNotFoundError",
    "SteamNotFoundError",
    "find_steam_path",
    "find_shortcuts_file",
    # VDF
    "VDFParser",
    "VDFFormatter",
    "VDFParseError",
    # CRC utilities
    "generate_shortcut_id",
    "generate_steam_url",
]
