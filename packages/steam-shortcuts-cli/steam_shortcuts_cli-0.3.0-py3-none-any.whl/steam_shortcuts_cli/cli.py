"""Steam Shortcuts CLI.

Usage:
    steam-shortcuts-cli [--file=<path>] add <name> <path> [--icon=<icon>] [--tags=<tags>] [--launch-options=<opts>]
    steam-shortcuts-cli [--file=<path>] update <name> [--path=<path>] [--icon=<icon>] [--tags=<tags>] [--launch-options=<opts>]
    steam-shortcuts-cli [--file=<path>] remove <name>
    steam-shortcuts-cli [--file=<path>] list [--verbose]
    steam-shortcuts-cli [--file=<path>] info <name>
    steam-shortcuts-cli [--file=<path>] image set <name> [--portrait=<path>] [--hero=<path>] [--logo=<path>] [--grid-icon=<path>] [--wide=<path>]
    steam-shortcuts-cli [--file=<path>] image remove <name> (<type> | --all)
    steam-shortcuts-cli [--file=<path>] image list <name>
    steam-shortcuts-cli (-h | --help)
    steam-shortcuts-cli --version

Commands:
    add           Add a new shortcut to Steam
    update        Update an existing shortcut
    remove        Remove an existing shortcut from Steam
    list          List all shortcuts
    info          Show details about a specific shortcut
    image set     Set custom images for a shortcut
    image remove  Remove custom images from a shortcut
    image list    List custom images for a shortcut

Arguments:
    <type>                 Image type: portrait, hero, logo, icon, or wide

Options:
    -h --help              Show this help message
    --version              Show version
    --file=<path>          Path to shortcuts.vdf file (auto-detected if not specified)
    --path=<path>          Path to executable (for update command)
    --icon=<icon>          Path to icon file (for add command)
    --tags=<tags>          Comma-separated list of tags/categories
    --launch-options=<opts>  Launch options (space-separated, use '\\ ' to escape spaces)
    --verbose              Show detailed information
    --portrait=<path>      Path to portrait/grid image (600x900)
    --hero=<path>          Path to hero/banner image (1920x620)
    --logo=<path>          Path to logo image (640x360)
    --grid-icon=<path>     Path to grid icon image (256x256)
    --wide=<path>          Path to wide cover image (940x430)
    --all                  Remove all images (for image remove)
"""

import sys

from docopt import docopt

from .manager import (
    IMAGE_DIMENSIONS,
    ImageType,
    InvalidImageError,
    MultipleUsersError,
    ShortcutExistsError,
    ShortcutNotFoundError,
    SteamShortcutManager,
)


def split_launch_options(opts: str) -> list[str]:
    """Split launch options on spaces, respecting '\\ ' escapes.

    Args:
        opts: Launch options string

    Returns:
        List of individual launch option arguments
    """
    if not opts:
        return []

    # Use a placeholder for escaped spaces
    placeholder = "\x00"
    escaped = opts.replace(r"\ ", placeholder)
    parts = escaped.split()
    return [part.replace(placeholder, " ") for part in parts]


def cmd_add(
    name: str,
    path: str,
    icon: str | None = None,
    tags: str | None = None,
    launch_options: str | None = None,
    shortcuts_file: str | None = None,
) -> int:
    """Add a new shortcut to Steam."""
    try:
        manager = SteamShortcutManager(shortcuts_file)
    except MultipleUsersError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if manager.file_path is None:
        print("Error: Could not find Steam shortcuts.vdf file", file=sys.stderr)
        print("Make sure Steam is installed and you have logged in at least once,", file=sys.stderr)
        print("or specify the path with --file", file=sys.stderr)
        return 1

    tag_list = [t.strip() for t in tags.split(",")] if tags else []
    launch_options_list = split_launch_options(launch_options or "")

    try:
        shortcut = manager.add(
            appname=name,
            exe=path,
            icon=icon or "",
            tags=tag_list,
            launch_options=launch_options_list,
        )
        manager.save()

        print(f"Added shortcut: {shortcut.appname}")
        steam_url = manager.get_steam_url(name)
        if steam_url:
            print(f"Steam URL: {steam_url}")
        print("Note: Restart Steam for changes to take effect.")
        return 0

    except ShortcutExistsError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_update(
    name: str,
    path: str | None = None,
    icon: str | None = None,
    tags: str | None = None,
    launch_options: str | None = None,
    shortcuts_file: str | None = None,
) -> int:
    """Update an existing shortcut."""
    try:
        manager = SteamShortcutManager(shortcuts_file)
    except MultipleUsersError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if manager.file_path is None:
        print("Error: Could not find Steam shortcuts.vdf file", file=sys.stderr)
        print("Specify the path with --file", file=sys.stderr)
        return 1

    tag_list = [t.strip() for t in tags.split(",")] if tags else None
    launch_options_list = split_launch_options(launch_options) if launch_options else None

    try:
        shortcut = manager.update(
            appname=name,
            exe=path,
            icon=icon,
            tags=tag_list,
            launch_options=launch_options_list,
        )
        manager.save()

        print(f"Updated shortcut: {shortcut.appname}")
        print("Note: Restart Steam for changes to take effect.")
        return 0

    except ShortcutNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_remove(name: str, shortcuts_file: str | None = None) -> int:
    """Remove a shortcut from Steam."""
    try:
        manager = SteamShortcutManager(shortcuts_file)
    except MultipleUsersError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if manager.file_path is None:
        print("Error: Could not find Steam shortcuts.vdf file", file=sys.stderr)
        print("Specify the path with --file", file=sys.stderr)
        return 1

    try:
        shortcut = manager.remove(name)
        manager.save()
        print(f"Removed shortcut: {shortcut.appname}")
        print("Note: Restart Steam for changes to take effect.")
        return 0

    except ShortcutNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_list(verbose: bool = False, shortcuts_file: str | None = None) -> int:
    """List all shortcuts."""
    try:
        manager = SteamShortcutManager(shortcuts_file)
    except MultipleUsersError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if manager.file_path is None:
        print("Error: Could not find Steam shortcuts.vdf file", file=sys.stderr)
        print("Specify the path with --file", file=sys.stderr)
        return 1

    if not manager.shortcuts:
        print("No shortcuts found")
        return 0

    print(f"Found {len(manager.shortcuts)} shortcut(s):")
    print()

    for shortcut in manager.shortcuts:
        if verbose:
            print(f"  Name: {shortcut.appname}")
            print(f"    Exe: {shortcut.exe}")
            if shortcut.start_dir:
                print(f"    Start Dir: {shortcut.start_dir}")
            if shortcut.icon:
                print(f"    Icon: {shortcut.icon}")
            if shortcut.launch_options:
                print(f"    Launch Options: {shortcut.launch_options}")
            if shortcut.tags:
                print(f"    Tags: {', '.join(shortcut.tags)}")
            for name, value in shortcut.extra_strings.items():
                print(f"    {name}: {value}")
            for name, value in shortcut.extra_ints.items():
                print(f"    {name}: {value}")
            steam_url = manager.get_steam_url(shortcut.appname)
            if steam_url:
                print(f"    Steam URL: {steam_url}")
            print()
        else:
            print(f"  - {shortcut.appname}")

    return 0


def cmd_info(name: str, shortcuts_file: str | None = None) -> int:
    """Show details about a specific shortcut."""
    try:
        manager = SteamShortcutManager(shortcuts_file)
    except MultipleUsersError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if manager.file_path is None:
        print("Error: Could not find Steam shortcuts.vdf file", file=sys.stderr)
        print("Specify the path with --file", file=sys.stderr)
        return 1

    shortcut = manager.get(name)
    if shortcut is None:
        print(f"Error: Shortcut '{name}' not found", file=sys.stderr)
        return 1

    print(f"Name: {shortcut.appname}")
    print(f"Executable: {shortcut.exe}")
    print(f"Start Directory: {shortcut.start_dir or '(not set)'}")
    print(f"Icon: {shortcut.icon or '(not set)'}")
    print(f"Launch Options: {shortcut.launch_options or '(not set)'}")
    print(f"Tags: {', '.join(shortcut.tags) if shortcut.tags else '(none)'}")
    print(f"Hidden: {'Yes' if shortcut.is_hidden else 'No'}")
    print(f"Allow Overlay: {'Yes' if shortcut.allow_overlay else 'No'}")
    print(f"VR Library: {'Yes' if shortcut.openvr else 'No'}")

    # Display extra fields from VDF
    for field_name, value in shortcut.extra_strings.items():
        print(f"{field_name}: {value or '(not set)'}")
    for field_name, value in shortcut.extra_ints.items():
        print(f"{field_name}: {value}")

    steam_url = manager.get_steam_url(name)
    if steam_url:
        print(f"Steam URL: {steam_url}")

    shortcut_id = manager.get_shortcut_id(name)
    if shortcut_id:
        print(f"Shortcut ID: {shortcut_id}")

    return 0


def cmd_image_set(
    name: str,
    portrait: str | None = None,
    hero: str | None = None,
    logo: str | None = None,
    grid_icon: str | None = None,
    wide: str | None = None,
    shortcuts_file: str | None = None,
) -> int:
    """Set custom images for a shortcut."""
    if not any([portrait, hero, logo, grid_icon, wide]):
        print("Error: At least one image option must be specified", file=sys.stderr)
        print("Use --portrait, --hero, --logo, --grid-icon, or --wide", file=sys.stderr)
        return 1

    try:
        manager = SteamShortcutManager(shortcuts_file)
    except MultipleUsersError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if manager.file_path is None:
        print("Error: Could not find Steam shortcuts.vdf file", file=sys.stderr)
        print("Specify the path with --file", file=sys.stderr)
        return 1

    # Map options to image types
    images: list[tuple[ImageType, str]] = []
    if portrait:
        images.append((ImageType.PORTRAIT, portrait))
    if hero:
        images.append((ImageType.HERO, hero))
    if logo:
        images.append((ImageType.LOGO, logo))
    if grid_icon:
        images.append((ImageType.ICON, grid_icon))
    if wide:
        images.append((ImageType.WIDE, wide))

    added_count = 0
    for image_type, image_path in images:
        try:
            dest_path = manager.add_image(name, image_type, image_path)
            dims = IMAGE_DIMENSIONS[image_type]
            print(f"Set {image_type.value} image ({dims[0]}x{dims[1]}): {dest_path}")
            added_count += 1
        except ShortcutNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        except InvalidImageError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    if added_count > 0:
        print("Note: Restart Steam for changes to take effect.")

    return 0


def cmd_image_remove(
    name: str,
    image_type_str: str | None = None,
    all_images: bool = False,
    shortcuts_file: str | None = None,
) -> int:
    """Remove custom images from a shortcut."""
    try:
        manager = SteamShortcutManager(shortcuts_file)
    except MultipleUsersError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if manager.file_path is None:
        print("Error: Could not find Steam shortcuts.vdf file", file=sys.stderr)
        print("Specify the path with --file", file=sys.stderr)
        return 1

    # Determine which image types to remove
    image_types: list[ImageType] = []
    if all_images:
        image_types = list(ImageType)
    elif image_type_str:
        type_map = {
            "portrait": ImageType.PORTRAIT,
            "hero": ImageType.HERO,
            "logo": ImageType.LOGO,
            "icon": ImageType.ICON,
            "wide": ImageType.WIDE,
        }
        if image_type_str.lower() not in type_map:
            print(f"Error: Invalid image type '{image_type_str}'", file=sys.stderr)
            print("Valid types: portrait, hero, logo, icon, wide", file=sys.stderr)
            return 1
        image_types.append(type_map[image_type_str.lower()])

    removed_count = 0
    for image_type in image_types:
        try:
            removed_path = manager.remove_image(name, image_type)
            if removed_path:
                print(f"Removed {image_type.value} image: {removed_path}")
                removed_count += 1
        except ShortcutNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    if removed_count == 0:
        print("No images found to remove")
    else:
        print("Note: Restart Steam for changes to take effect.")

    return 0


def cmd_image_list(name: str, shortcuts_file: str | None = None) -> int:
    """List custom images for a shortcut."""
    try:
        manager = SteamShortcutManager(shortcuts_file)
    except MultipleUsersError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if manager.file_path is None:
        print("Error: Could not find Steam shortcuts.vdf file", file=sys.stderr)
        print("Specify the path with --file", file=sys.stderr)
        return 1

    try:
        images = manager.list_images(name)
    except ShortcutNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if not images:
        print(f"No custom images found for '{name}'")
        return 0

    print(f"Custom images for '{name}':")
    for image_type, path in images.items():
        dims = IMAGE_DIMENSIONS[image_type]
        print(f"  {image_type.value} ({dims[0]}x{dims[1]}): {path}")

    return 0


def main() -> int:
    args = docopt(__doc__, version="steam-shortcuts-cli 0.1.0")
    shortcuts_file = args["--file"]

    # Check for image subcommands first (before list/remove which would otherwise match)
    if args["image"]:
        if args["set"]:
            return cmd_image_set(
                args["<name>"],
                portrait=args["--portrait"],
                hero=args["--hero"],
                logo=args["--logo"],
                grid_icon=args["--grid-icon"],
                wide=args["--wide"],
                shortcuts_file=shortcuts_file,
            )
        elif args["remove"]:
            return cmd_image_remove(
                args["<name>"],
                image_type_str=args["<type>"],
                all_images=args["--all"],
                shortcuts_file=shortcuts_file,
            )
        elif args["list"]:
            return cmd_image_list(args["<name>"], shortcuts_file=shortcuts_file)
    elif args["add"]:
        return cmd_add(
            args["<name>"],
            args["<path>"],
            icon=args["--icon"],
            tags=args["--tags"],
            launch_options=args["--launch-options"],
            shortcuts_file=shortcuts_file,
        )
    elif args["update"]:
        return cmd_update(
            args["<name>"],
            path=args["--path"],
            icon=args["--icon"],
            tags=args["--tags"],
            launch_options=args["--launch-options"],
            shortcuts_file=shortcuts_file,
        )
    elif args["remove"]:
        return cmd_remove(args["<name>"], shortcuts_file=shortcuts_file)
    elif args["list"]:
        return cmd_list(verbose=args["--verbose"], shortcuts_file=shortcuts_file)
    elif args["info"]:
        return cmd_info(args["<name>"], shortcuts_file=shortcuts_file)

    return 0


if __name__ == "__main__":
    sys.exit(main())
