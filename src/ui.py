import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

from scanner import scan_steam_saves_by_account
from steam_name_getter import get_steam_game_name
from steam_paths import get_steam_userdata_path
from zipper import zip_save
from config_reader import read_config

class GameSaveBackupUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Steam Save Backup Tool")
        self.root.geometry("600x400")

        CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"
        self.config = read_config(CONFIG_PATH)
        self.backup_dir = Path(self.config["backup_dir"])
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        self.create_widgets()

    def create_widgets(self):
        ttk.Button(self.root, text="Scan Steam Saves", command=self.scan).pack(pady=10)
        ttk.Button(self.root, text="Backup All", command=self.backup_all).pack()

        self.log = tk.Text(self.root, height=15)
        self.log.pack(fill="both", expand=True, padx=10, pady=10)

    def log_msg(self, msg):
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)

    def scan(self):
        userdata = get_steam_userdata_path(Path(self.config["steam_path"]))
        self.saves = scan_steam_saves_by_account(userdata)
        self.log_msg(f"Found {len(self.saves)} Steam accounts")
        self.log_msg("Saves by account:")
        for steam_id, saves in self.saves.items():
            self.log_msg(f"  Steam ID: {steam_id} - {len(saves)} saves")            
            for save in saves:
                self.log_msg(f"    App: {get_steam_game_name(int(save['app_id']))} AppID: {save['app_id']}")
        self.log_msg("Scan complete.")

    def backup_all(self):
        for steam_id, saves in sorted(self.saves.items()):
            self.log_msg(f"Steam ID: {steam_id}")
            for save in saves:
                zip_save(
                    save["path"],
                    self.backup_dir,
                    save["app_id"],
                    steam_id
                )
                self.log_msg(f"✔ Backed up AppID {save['app_id']}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GameSaveBackupUI(root)
    root.mainloop()
