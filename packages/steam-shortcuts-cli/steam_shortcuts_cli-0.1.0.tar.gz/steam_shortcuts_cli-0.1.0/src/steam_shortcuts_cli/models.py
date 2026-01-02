"""Pydantic models for Steam shortcuts."""

from pydantic import BaseModel, Field


class SteamShortcut(BaseModel):
    """Represents a Steam non-Steam game shortcut.

    This model contains all the fields that Steam uses for shortcuts in the
    shortcuts.vdf file.
    """

    appname: str = Field(description="Display name of the shortcut")
    exe: str = Field(description="Path to the executable (usually quoted)")
    start_dir: str = Field(default="", description="Working directory for the executable")
    icon: str = Field(default="", description="Path to the icon file")
    shortcut_path: str = Field(default="", description="Shortcut path (rarely used)")
    launch_options: str = Field(default="", description="Command line arguments")
    is_hidden: bool = Field(default=False, description="Whether shortcut is hidden")
    allow_desktop_config: bool = Field(
        default=True, description="Allow controller desktop config"
    )
    allow_overlay: bool = Field(default=True, description="Allow Steam overlay")
    openvr: bool = Field(default=False, description="Show in VR library")
    last_play_time: int = Field(default=0, description="Unix timestamp of last play")
    tags: list[str] = Field(default_factory=list, description="Category tags")

    def __hash__(self) -> int:
        return hash(
            (
                self.appname,
                self.exe,
                self.start_dir,
                self.icon,
                tuple(self.tags),
            )
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SteamShortcut):
            return NotImplemented
        return (
            self.appname == other.appname
            and self.exe == other.exe
            and self.start_dir == other.start_dir
            and self.icon == other.icon
            and self.tags == other.tags
        )


class ShortcutsFile(BaseModel):
    """Represents the contents of a shortcuts.vdf file."""

    shortcuts: list[SteamShortcut] = Field(default_factory=list)
