from pathlib import Path
from src.steam_paths import get_steam_userdata_path
from src.scanner import scan_steam_saves_by_account
from src.zipper import zip_save
from src.steam_name_getter import get_steam_game_name
from src.config_reader import read_config

CONFIG_PATH = Path(__file__).parent / "config.yaml"
CONFIG = read_config(CONFIG_PATH)
BACKUP_DIR = Path(CONFIG.get("backup_dir", "backups"))
BACKUP_DIR.mkdir(parents=True, exist_ok=True)
STEAM_PATH = Path(CONFIG.get("steam_path", "C:/Program Files (x86)/Steam"))

def main():
    userdata = get_steam_userdata_path(STEAM_PATH)
    saves = scan_steam_saves_by_account(userdata)

    # Sort by Steam ID
    for steam_id in sorted(saves.keys()):
        save_list = saves[steam_id]
        for save in save_list:
            game_name = get_steam_game_name(int(save["app_id"]))
            game_id = save["app_id"]
            zip_save(save["path"], BACKUP_DIR, game_name, steam_id)
            print(f"✔ Backed up {game_name} (AppID: {game_id}) (SteamID: {steam_id})")
            
if __name__ == "__main__":
    main()
