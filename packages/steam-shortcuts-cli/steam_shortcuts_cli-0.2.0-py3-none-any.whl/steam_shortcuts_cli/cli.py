"""Steam Shortcuts CLI.

Usage:
    steam-shortcuts-cli [--file=<path>] add <name> <path> [--icon=<icon>] [--tags=<tags>] [--launch-options=<opts>]
    steam-shortcuts-cli [--file=<path>] update <name> [--path=<path>] [--icon=<icon>] [--tags=<tags>] [--launch-options=<opts>]
    steam-shortcuts-cli [--file=<path>] remove <name>
    steam-shortcuts-cli [--file=<path>] list [--verbose]
    steam-shortcuts-cli [--file=<path>] info <name>
    steam-shortcuts-cli (-h | --help)
    steam-shortcuts-cli --version

Commands:
    add      Add a new shortcut to Steam
    update   Update an existing shortcut
    remove   Remove an existing shortcut from Steam
    list     List all shortcuts
    info     Show details about a specific shortcut

Options:
    -h --help              Show this help message
    --version              Show version
    --file=<path>          Path to shortcuts.vdf file (auto-detected if not specified)
    --path=<path>          Path to executable (for update command)
    --icon=<icon>          Path to icon file
    --tags=<tags>          Comma-separated list of tags/categories
    --launch-options=<opts>  Launch options (space-separated, use '\\ ' to escape spaces)
    --verbose              Show detailed information
"""

import sys

from docopt import docopt

from .manager import (
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
    manager = SteamShortcutManager(shortcuts_file)

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
    manager = SteamShortcutManager(shortcuts_file)

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
        return 0

    except ShortcutNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_remove(name: str, shortcuts_file: str | None = None) -> int:
    """Remove a shortcut from Steam."""
    manager = SteamShortcutManager(shortcuts_file)

    if manager.file_path is None:
        print("Error: Could not find Steam shortcuts.vdf file", file=sys.stderr)
        print("Specify the path with --file", file=sys.stderr)
        return 1

    try:
        shortcut = manager.remove(name)
        manager.save()
        print(f"Removed shortcut: {shortcut.appname}")
        return 0

    except ShortcutNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_list(verbose: bool = False, shortcuts_file: str | None = None) -> int:
    """List all shortcuts."""
    manager = SteamShortcutManager(shortcuts_file)

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
            steam_url = manager.get_steam_url(shortcut.appname)
            if steam_url:
                print(f"    Steam URL: {steam_url}")
            print()
        else:
            print(f"  - {shortcut.appname}")

    return 0


def cmd_info(name: str, shortcuts_file: str | None = None) -> int:
    """Show details about a specific shortcut."""
    manager = SteamShortcutManager(shortcuts_file)

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

    steam_url = manager.get_steam_url(name)
    if steam_url:
        print(f"Steam URL: {steam_url}")

    shortcut_id = manager.get_shortcut_id(name)
    if shortcut_id:
        print(f"Shortcut ID: {shortcut_id}")

    return 0


def main() -> int:
    args = docopt(__doc__, version="steam-shortcuts-cli 0.1.0")
    shortcuts_file = args["--file"]

    if args["add"]:
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
