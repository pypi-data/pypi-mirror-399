"""High-level manager for Steam shortcuts."""

import os
import platform
import shutil
from enum import Enum
from pathlib import Path

from PIL import Image

from .crc import generate_shortcut_id, generate_steam_url
from .models import ShortcutsFile, SteamShortcut
from .vdf import VDFFormatter, VDFParseError, VDFParser


class ImageType(Enum):
    """Types of images that can be added to a Steam shortcut."""

    PORTRAIT = "portrait"  # Grid image (600x900)
    HERO = "hero"  # Banner image (1920x620)
    LOGO = "logo"  # Logo image (transparent PNG)
    ICON = "icon"  # Icon (256x256)
    WIDE = "wide"  # Wide cover image (940x430)


# Expected dimensions for each image type (width, height)
IMAGE_DIMENSIONS: dict[ImageType, tuple[int, int]] = {
    ImageType.PORTRAIT: (600, 900),
    ImageType.HERO: (1920, 620),
    ImageType.LOGO: (640, 360),
    ImageType.ICON: (256, 256),
    ImageType.WIDE: (940, 430),
}


class InvalidImageError(Exception):
    """Raised when an image has invalid dimensions."""


class ShortcutNotFoundError(Exception):
    """Raised when a shortcut cannot be found."""


class ShortcutExistsError(Exception):
    """Raised when trying to add a duplicate shortcut."""


class SteamNotFoundError(Exception):
    """Raised when Steam installation cannot be found."""


class MultipleUsersError(Exception):
    """Raised when multiple Steam users are found and manual selection is required."""

    def __init__(self, paths: list[Path]):
        self.paths = paths
        paths_str = "\n  ".join(str(p) for p in paths)
        super().__init__(
            f"Multiple Steam users found. Please specify the shortcuts file with --file.\n"
            f"Available shortcuts files:\n  {paths_str}"
        )


def validate_image_dimensions(image_path: Path, image_type: ImageType) -> None:
    """Validate that an image has the correct dimensions for its type.

    Args:
        image_path: Path to the image file
        image_type: The type of image to validate against

    Raises:
        InvalidImageError: If the image dimensions don't match the expected size
        FileNotFoundError: If the image file doesn't exist
    """
    if not image_path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    expected_width, expected_height = IMAGE_DIMENSIONS[image_type]

    with Image.open(image_path) as img:
        width, height = img.size
        if width != expected_width or height != expected_height:
            raise InvalidImageError(
                f"Invalid dimensions for {image_type.value} image: "
                f"got {width}x{height}, expected {expected_width}x{expected_height}"
            )


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


def find_all_shortcuts_files(steam_path: Path | None = None) -> list[Path]:
    """Find all possible shortcuts.vdf files for all Steam users.

    Args:
        steam_path: Path to Steam installation (auto-detected if None)

    Returns:
        List of paths to shortcuts.vdf files (existing or potential)
    """
    if steam_path is None:
        steam_path = find_steam_path()
        if steam_path is None:
            return []

    userdata = steam_path / "userdata"
    if not userdata.exists():
        return []

    paths: list[Path] = []

    for user_dir in userdata.iterdir():
        if user_dir.is_dir():
            config_dir = user_dir / "config"
            if config_dir.exists():
                paths.append(config_dir / "shortcuts.vdf")

    return paths


def find_shortcuts_file(steam_path: Path | None = None, user_id: str | None = None) -> Path | None:
    """Find the shortcuts.vdf file for a Steam user.

    Args:
        steam_path: Path to Steam installation (auto-detected if None)
        user_id: Steam user ID (uses first found if None)

    Returns:
        Path to shortcuts.vdf or None if not found

    Raises:
        MultipleUsersError: If multiple users exist and no user_id specified
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

    # Find all possible shortcuts files
    all_paths = find_all_shortcuts_files(steam_path)

    if len(all_paths) == 0:
        return None
    elif len(all_paths) == 1:
        return all_paths[0]
    else:
        raise MultipleUsersError(all_paths)


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
        launch_options: list[str] | None = None,
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
            launch_options: Command line arguments as list of args
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

        # Convert launch_options list to string
        launch_options_str = " ".join(launch_options) if launch_options else ""

        shortcut = SteamShortcut(
            appname=appname,
            exe=exe,
            start_dir=start_dir,
            icon=icon,
            launch_options=launch_options_str,
            tags=tags or [],
            is_hidden=is_hidden,
            allow_overlay=allow_overlay,
            allow_desktop_config=allow_desktop_config,
            openvr=openvr,
        )

        self._shortcuts.shortcuts.append(shortcut)
        return shortcut

    def update(
        self,
        appname: str,
        *,
        exe: str | None = None,
        start_dir: str | None = None,
        icon: str | None = None,
        launch_options: list[str] | None = None,
        tags: list[str] | None = None,
        is_hidden: bool | None = None,
        allow_overlay: bool | None = None,
        allow_desktop_config: bool | None = None,
        openvr: bool | None = None,
    ) -> SteamShortcut:
        """Update an existing shortcut.

        Args:
            appname: Name of the shortcut to update
            exe: New path to the executable (None to keep existing)
            start_dir: New working directory (None to keep existing)
            icon: New path to icon file (None to keep existing)
            launch_options: New command line arguments (None to keep existing)
            tags: New category tags (None to keep existing)
            is_hidden: Whether to hide the shortcut (None to keep existing)
            allow_overlay: Allow Steam overlay (None to keep existing)
            allow_desktop_config: Allow controller desktop config (None to keep existing)
            openvr: Show in VR library (None to keep existing)

        Returns:
            The updated SteamShortcut

        Raises:
            ShortcutNotFoundError: If the shortcut doesn't exist
        """
        shortcut = self.get(appname)
        if shortcut is None:
            raise ShortcutNotFoundError(f"Shortcut '{appname}' not found")

        if exe is not None:
            # Ensure exe is quoted if it contains spaces and isn't already quoted
            if " " in exe and not (exe.startswith('"') and exe.endswith('"')):
                exe = f'"{exe}"'
            shortcut.exe = exe
            # Update start_dir if not explicitly provided
            if start_dir is None:
                exe_path = Path(exe.strip('"'))
                if exe_path.parent.exists():
                    shortcut.start_dir = f'"{exe_path.parent}"'

        if start_dir is not None:
            shortcut.start_dir = start_dir
        if icon is not None:
            shortcut.icon = icon
        if launch_options is not None:
            shortcut.launch_options = " ".join(launch_options)
        if tags is not None:
            shortcut.tags = tags
        if is_hidden is not None:
            shortcut.is_hidden = is_hidden
        if allow_overlay is not None:
            shortcut.allow_overlay = allow_overlay
        if allow_desktop_config is not None:
            shortcut.allow_desktop_config = allow_desktop_config
        if openvr is not None:
            shortcut.openvr = openvr

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

    def get_grid_path(self) -> Path | None:
        """Get the path to the Steam grid folder for custom images.

        Returns:
            Path to the grid folder (userdata/<user_id>/config/grid/) or None
        """
        if self._shortcuts_file is None:
            return None
        # Grid folder is at the same level as shortcuts.vdf (in config/)
        config_dir = self._shortcuts_file.parent
        grid_dir = config_dir / "grid"
        return grid_dir

    def add_image(
        self,
        appname: str,
        image_type: ImageType,
        image_path: Path | str,
    ) -> Path:
        """Add a custom image for a shortcut.

        Args:
            appname: Name of the shortcut
            image_type: Type of image (portrait, hero, logo, icon)
            image_path: Path to the source image file

        Returns:
            Path to the copied image in the grid folder

        Raises:
            ShortcutNotFoundError: If the shortcut doesn't exist
            InvalidImageError: If the image has incorrect dimensions
            FileNotFoundError: If the image file doesn't exist
            ValueError: If the grid path cannot be determined
        """
        shortcut = self.get(appname)
        if shortcut is None:
            raise ShortcutNotFoundError(f"Shortcut '{appname}' not found")

        image_path = Path(image_path)
        validate_image_dimensions(image_path, image_type)

        grid_path = self.get_grid_path()
        if grid_path is None:
            raise ValueError("Cannot determine grid folder path")

        # Ensure grid directory exists
        grid_path.mkdir(parents=True, exist_ok=True)

        # Get the app ID for the filename (from shortcuts.vdf appid field)
        appid = shortcut.extra_ints.get("appid")
        if appid is None:
            raise ValueError(f"Shortcut '{appname}' has no appid field")

        # Determine the filename suffix based on image type
        suffix_map = {
            ImageType.PORTRAIT: "p",
            ImageType.HERO: "_hero",
            ImageType.LOGO: "_logo",
            ImageType.ICON: "_icon",
            ImageType.WIDE: "",
        }
        suffix = suffix_map[image_type]

        # Use the original file extension
        ext = image_path.suffix.lower()
        if ext not in (".png", ".jpg", ".jpeg"):
            ext = ".png"

        dest_filename = f"{appid}{suffix}{ext}"
        dest_path = grid_path / dest_filename

        # Copy the image
        shutil.copy2(image_path, dest_path)

        return dest_path

    def remove_image(self, appname: str, image_type: ImageType) -> Path | None:
        """Remove a custom image for a shortcut.

        Args:
            appname: Name of the shortcut
            image_type: Type of image to remove

        Returns:
            Path to the removed image, or None if it didn't exist

        Raises:
            ShortcutNotFoundError: If the shortcut doesn't exist
            ValueError: If the grid path cannot be determined
        """
        shortcut = self.get(appname)
        if shortcut is None:
            raise ShortcutNotFoundError(f"Shortcut '{appname}' not found")

        grid_path = self.get_grid_path()
        if grid_path is None:
            raise ValueError("Cannot determine grid folder path")

        appid = shortcut.extra_ints.get("appid")
        if appid is None:
            raise ValueError(f"Shortcut '{appname}' has no appid field")

        suffix_map = {
            ImageType.PORTRAIT: "p",
            ImageType.HERO: "_hero",
            ImageType.LOGO: "_logo",
            ImageType.ICON: "_icon",
            ImageType.WIDE: "",
        }
        suffix = suffix_map[image_type]

        # Check for all possible extensions
        for ext in (".png", ".jpg", ".jpeg"):
            image_path = grid_path / f"{appid}{suffix}{ext}"
            if image_path.exists():
                image_path.unlink()
                return image_path

        return None

    def list_images(self, appname: str) -> dict[ImageType, Path]:
        """List all custom images for a shortcut.

        Args:
            appname: Name of the shortcut

        Returns:
            Dictionary mapping image types to their file paths

        Raises:
            ShortcutNotFoundError: If the shortcut doesn't exist
            ValueError: If the grid path cannot be determined
        """
        shortcut = self.get(appname)
        if shortcut is None:
            raise ShortcutNotFoundError(f"Shortcut '{appname}' not found")

        grid_path = self.get_grid_path()
        if grid_path is None:
            raise ValueError("Cannot determine grid folder path")

        appid = shortcut.extra_ints.get("appid")
        if appid is None:
            raise ValueError(f"Shortcut '{appname}' has no appid field")

        suffix_map = {
            ImageType.PORTRAIT: "p",
            ImageType.HERO: "_hero",
            ImageType.LOGO: "_logo",
            ImageType.ICON: "_icon",
            ImageType.WIDE: "",
        }

        found_images: dict[ImageType, Path] = {}

        for image_type, suffix in suffix_map.items():
            for ext in (".png", ".jpg", ".jpeg"):
                image_path = grid_path / f"{appid}{suffix}{ext}"
                if image_path.exists():
                    found_images[image_type] = image_path
                    break

        return found_images
