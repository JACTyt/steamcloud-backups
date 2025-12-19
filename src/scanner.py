from pathlib import Path
from collections import defaultdict

def scan_steam_saves_by_account(userdata_path: Path):
    saves = []

    saves_by_account = defaultdict(list)

    for steam_id_folder in userdata_path.iterdir():
        if not steam_id_folder.is_dir():
            continue
        steam_id = steam_id_folder.name

        for app_id_folder in steam_id_folder.iterdir():
            remote = app_id_folder / "remote"
            if remote.exists():
                saves_by_account[steam_id].append({
                    "app_id": app_id_folder.name,
                    "path": remote
                })

    return dict(saves_by_account)