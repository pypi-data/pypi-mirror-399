"""VDF binary file format parser and formatter for Steam shortcuts.

The shortcuts.vdf file uses a binary format with special control characters:
- \\x00: Delimiter/null terminator
- \\x01: String type indicator
- \\x02: Boolean/int type indicator (4 bytes follow)
- \\x08: End of section/array
- \\x0a: End of file (optional)
"""

import re
from pathlib import Path

from .models import ShortcutsFile, SteamShortcut

# Control characters used in VDF format
NULL = b"\x00"
STRING_TYPE = b"\x01"
INT_TYPE = b"\x02"
END_SECTION = b"\x08"
END_FILE = b"\x0a"


class VDFParseError(Exception):
    """Raised when parsing a VDF file fails."""


class VDFParser:
    """Parses Steam shortcuts.vdf binary files into Python objects."""

    def parse(self, data: bytes) -> ShortcutsFile:
        """Parse binary VDF data into a ShortcutsFile object."""
        shortcuts = self._parse_shortcuts(data)
        return ShortcutsFile(shortcuts=shortcuts)

    def parse_file(self, path: Path | str) -> ShortcutsFile:
        """Parse a shortcuts.vdf file."""
        path = Path(path)
        data = path.read_bytes()
        return self.parse(data)

    def _parse_shortcuts(self, data: bytes) -> list[SteamShortcut]:
        """Parse the shortcuts array from VDF data."""
        # File format: \x00shortcuts\x00[array]\x08\x08[\x0a]
        # Match the outer structure
        pattern = rb"\x00shortcuts\x00(.*)\x08\x08"
        match = re.search(pattern, data, re.DOTALL)
        if not match:
            # Check if it's an empty file
            if data == b"\x00shortcuts\x00\x08\x08" or data == b"\x00shortcuts\x00\x08\x08\x0a":
                return []
            raise VDFParseError("Invalid VDF file format")

        array_data = match.group(1)
        return self._parse_array(array_data)

    def _parse_array(self, data: bytes) -> list[SteamShortcut]:
        """Parse an array of shortcuts from VDF data.

        Uses a backwards-matching approach similar to the original implementation.
        Each shortcut ends with \\x08\\x08 (one for tags section, one for shortcut).
        """
        if not data:
            return []

        shortcuts = []
        remaining = data

        while remaining:
            # Look for pattern: \x00[digits]\x00[shortcut_data]\x08\x08
            # Match backwards to find the last entry first, then recurse
            # Pattern matches: \x00 + digits + \x00 + (anything) + \x08\x08
            match = re.match(rb"(.*)\x00(\d+)\x00(.*)\x08\x08$", remaining, re.DOTALL)
            if not match:
                # Try without trailing \x08\x08 for partial data
                match = re.match(rb"(.*)\x00(\d+)\x00(.*)\x08$", remaining, re.DOTALL)
                if not match:
                    break

            groups = match.groups()
            prefix = groups[0]
            shortcut_data = groups[2]

            shortcut = self._parse_shortcut(shortcut_data)
            if shortcut:
                shortcuts.insert(0, shortcut)  # Insert at beginning since we match backwards

            remaining = prefix

        return shortcuts

    def _parse_shortcut(self, data: bytes) -> SteamShortcut | None:
        """Parse a single shortcut entry."""
        try:
            fields = self._extract_fields(data)
            return SteamShortcut(
                appname=fields.get("appname", fields.get("AppName", "")),
                exe=fields.get("exe", fields.get("Exe", "")),
                start_dir=fields.get("StartDir", fields.get("startdir", "")),
                icon=fields.get("icon", ""),
                shortcut_path=fields.get("ShortcutPath", ""),
                launch_options=fields.get("LaunchOptions", ""),
                is_hidden=fields.get("IsHidden", False),
                allow_desktop_config=fields.get("AllowDesktopConfig", True),
                allow_overlay=fields.get("AllowOverlay", True),
                openvr=fields.get("OpenVR", False),
                last_play_time=fields.get("LastPlayTime", 0),
                tags=fields.get("tags", []),
            )
        except Exception:
            return None

    def _extract_fields(self, data: bytes) -> dict:
        """Extract all fields from shortcut data."""
        fields = {}
        pos = 0

        while pos < len(data):
            byte = data[pos : pos + 1]

            if byte == STRING_TYPE:
                # String field: \x01[name]\x00[value]\x00
                pos += 1
                name_end = data.find(NULL, pos)
                if name_end == -1:
                    break
                name = data[pos:name_end].decode("utf-8", errors="replace")
                pos = name_end + 1

                value_end = data.find(NULL, pos)
                if value_end == -1:
                    break
                value = data[pos:value_end].decode("utf-8", errors="replace")
                pos = value_end + 1

                fields[name] = value

            elif byte == INT_TYPE:
                # Int/bool field: \x02[name]\x00[4 bytes]
                pos += 1
                name_end = data.find(NULL, pos)
                if name_end == -1:
                    break
                name = data[pos:name_end].decode("utf-8", errors="replace")
                pos = name_end + 1

                if pos + 4 <= len(data):
                    value = int.from_bytes(data[pos : pos + 4], "little")
                    pos += 4
                    # Convert to bool for known boolean fields
                    if name in ("IsHidden", "AllowDesktopConfig", "AllowOverlay", "OpenVR"):
                        fields[name] = bool(value)
                    else:
                        fields[name] = value
                else:
                    break

            elif byte == NULL:
                # Possible tags section or section marker: \x00[name]\x00
                pos += 1
                name_end = data.find(NULL, pos)
                if name_end == -1:
                    break
                name = data[pos:name_end].decode("utf-8", errors="replace")
                pos = name_end + 1

                if name == "tags":
                    tags, new_pos = self._parse_tags(data, pos)
                    fields["tags"] = tags
                    pos = new_pos
                else:
                    # Unknown section, skip to end
                    break

            elif byte == END_SECTION:
                break

            else:
                pos += 1

        return fields

    def _parse_tags(self, data: bytes, start: int) -> tuple[list[str], int]:
        """Parse the tags array."""
        tags = []
        pos = start

        while pos < len(data):
            byte = data[pos : pos + 1]

            if byte == STRING_TYPE:
                # Tag entry: \x01[index]\x00[tag]\x00
                pos += 1
                idx_end = data.find(NULL, pos)
                if idx_end == -1:
                    break
                pos = idx_end + 1

                tag_end = data.find(NULL, pos)
                if tag_end == -1:
                    break
                tag = data[pos:tag_end].decode("utf-8", errors="replace")
                tags.append(tag)
                pos = tag_end + 1

            elif byte == END_SECTION:
                pos += 1
                break

            else:
                pos += 1

        return tags, pos


class VDFFormatter:
    """Formats Python objects into Steam shortcuts.vdf binary format."""

    def format(self, shortcuts_file: ShortcutsFile) -> bytes:
        """Format a ShortcutsFile object into binary VDF data."""
        return self.format_shortcuts(shortcuts_file.shortcuts)

    def format_shortcuts(self, shortcuts: list[SteamShortcut]) -> bytes:
        """Format a list of shortcuts into binary VDF data."""
        result = NULL + b"shortcuts" + NULL
        result += self._format_array(shortcuts)
        result += END_SECTION + END_SECTION
        return result

    def format_file(self, shortcuts_file: ShortcutsFile, path: Path | str) -> None:
        """Format and write a ShortcutsFile to a file."""
        path = Path(path)
        data = self.format(shortcuts_file)
        path.write_bytes(data)

    def _format_array(self, shortcuts: list[SteamShortcut]) -> bytes:
        """Format the array of shortcuts."""
        result = b""
        for i, shortcut in enumerate(shortcuts):
            result += NULL + str(i).encode() + NULL
            result += self._format_shortcut(shortcut)
        return result

    def _format_shortcut(self, shortcut: SteamShortcut) -> bytes:
        """Format a single shortcut."""
        result = b""

        # String fields
        result += self._format_string("appname", shortcut.appname)
        result += self._format_string("exe", shortcut.exe)
        result += self._format_string("StartDir", shortcut.start_dir)
        result += self._format_string("icon", shortcut.icon)
        result += self._format_string("ShortcutPath", shortcut.shortcut_path)
        result += self._format_string("LaunchOptions", shortcut.launch_options)

        # Boolean/int fields
        result += self._format_int("IsHidden", 1 if shortcut.is_hidden else 0)
        result += self._format_int("AllowDesktopConfig", 1 if shortcut.allow_desktop_config else 0)
        result += self._format_int("AllowOverlay", 1 if shortcut.allow_overlay else 0)
        result += self._format_int("OpenVR", 1 if shortcut.openvr else 0)
        result += self._format_int("LastPlayTime", shortcut.last_play_time)

        # Tags section
        result += self._format_tags(shortcut.tags)

        result += END_SECTION
        return result

    def _format_string(self, name: str, value: str) -> bytes:
        """Format a string field."""
        return STRING_TYPE + name.encode() + NULL + value.encode() + NULL

    def _format_int(self, name: str, value: int) -> bytes:
        """Format an integer field (4 bytes, little-endian)."""
        return INT_TYPE + name.encode() + NULL + value.to_bytes(4, "little")

    def _format_tags(self, tags: list[str]) -> bytes:
        """Format the tags section."""
        result = NULL + b"tags" + NULL
        for i, tag in enumerate(tags):
            result += STRING_TYPE + str(i).encode() + NULL + tag.encode() + NULL
        result += END_SECTION
        return result
