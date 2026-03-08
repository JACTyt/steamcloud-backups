# SteamCloud Backups

SteamCloud Backups scans local Steam `userdata` folders and creates ZIP backups of each game's `remote` save directory.

## What It Does

- Reads settings from `config.yaml`.
- Scans Steam accounts under `<steam_path>/userdata`.
- Finds game save folders that contain a `remote` directory.
- Creates timestamped ZIP backups per game and Steam account.
- Resolves game names via Steam Store API when possible.

## Current Behavior

- Main entrypoint is `main.py`.
- Backups are stored under `<backup_dir>/<steam_id>/`.
- ZIP filename format:
	`<game_name>_<steam_id>_<YYYY.MM.DD_HH:MM>.zip`
- If game name lookup fails, filename uses `Unknown application`.
- Every run creates new ZIPs; old backups are not pruned.

## Requirements

- Python 3.9+
- Installed Steam client with local `userdata`
- Internet access (optional, only for game name lookup)

Python dependencies (from `requirements.txt`):

- `PyYAML==6.0.3`
- `Requests==2.32.5`

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Edit `config.yaml`:

```yaml
backup_dir: D:/Backups/Steam
steam_path: C:/Program Files (x86)/Steam
keep_versions: 5
```

### Config keys

- `backup_dir`: Folder where ZIP files are written.
- `steam_path`: Steam installation root (tool scans `<steam_path>/userdata`).
- `keep_versions`: Currently not used by the code.

## Usage

Run from project root:

```bash
python main.py
```

Example console output:

```text
✔ Backed up Portal 2 (AppID: 620) (SteamID: 7656119xxxxxxxxxx)
✔ Backed up Unknown application (AppID: 12345) (SteamID: 7656119xxxxxxxxxx)
```

## Project Structure

- `main.py`: CLI workflow (scan + backup).
- `src/config_reader.py`: Reads YAML config.
- `src/steam_paths.py`: Builds Steam `userdata` path.
- `src/scanner.py`: Detects save folders by account/AppID.
- `src/steam_name_getter.py`: Fetches game names from Steam API.
- `src/zipper.py`: Creates ZIP archives.
- `src/ui.py`: Tkinter UI prototype.

## Notes and Limitations

- Backup retention is not implemented (`keep_versions` is ignored).
- `src/ui.py` uses direct module imports and may require import path adjustments if run as-is.
- No built-in validation for invalid `steam_path` or missing permissions.
- API/network failures do not stop backup; they only affect displayed game names.

## License

See `LICENSE.md`.