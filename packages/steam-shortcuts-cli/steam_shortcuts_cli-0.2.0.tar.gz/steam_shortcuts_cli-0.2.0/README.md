# steam-shortcuts-cli

A simple CLI tool to manage Steam external shortcuts (non-Steam games).

## Installation

```bash
uv tool install steam-shortcuts-cli
```

Or run directly without installing:

```bash
uvx steam-shortcuts-cli --help
```

## Usage

### List all shortcuts

```bash
uvx steam-shortcuts-cli list
uvx steam-shortcuts-cli list --verbose
```

### Add a shortcut

```bash
uvx steam-shortcuts-cli add "My Game" /path/to/game
uvx steam-shortcuts-cli add "My Game" /path/to/game --icon=/path/to/icon.png --tags="Action,Indie"
uvx steam-shortcuts-cli add "My Game" /path/to/game --launch-options="--fullscreen"
```

### Remove a shortcut

```bash
uvx steam-shortcuts-cli remove "My Game"
```

### Get shortcut info

```bash
uvx steam-shortcuts-cli info "My Game"
```

### Specify a custom shortcuts.vdf path

```bash
uvx steam-shortcuts-cli --file=/path/to/shortcuts.vdf list
```

## Acknowledgements

This project is inspired by:

- [CorporalQuesadilla/Steam-Shortcut-Manager](https://github.com/CorporalQuesadilla/Steam-Shortcut-Manager)
- [chyyran/SteamShortcutManager](https://github.com/chyyran/SteamShortcutManager)
