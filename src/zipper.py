import zipfile
from pathlib import Path
from datetime import datetime

def zip_save(save_path: Path, backup_dir: Path, game_name: str, steam_id: str):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    steam_folder = backup_dir / steam_id
    steam_folder.mkdir(parents=True, exist_ok=True)

    zip_name = f"{game_name}_{steam_id}_{timestamp}.zip"
    zip_path = steam_folder / zip_name

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in save_path.rglob("*"):
            zipf.write(file, file.relative_to(save_path))

    return zip_path
