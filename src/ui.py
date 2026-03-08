import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path
from datetime import datetime

from scanner import scan_steam_saves_by_account
from steam_name_getter import get_steam_game_name
from steam_paths import get_steam_userdata_path
from zipper import zip_save
from config import get_config

class GameSaveBackupUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Steam Save Backup Tool")
        self.root.geometry("900x700")
        
        self.saves = {}
        self.saves_list = []

        CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"
        try:
            self.config = get_config(CONFIG_PATH)
        except (FileNotFoundError, ValueError) as e:
            messagebox.showerror("Configuration Error", f"Failed to load config: {e}")
            raise RuntimeError(f"Configuration error: {e}")
        
        self.backup_dir = Path(self.config["backup_dir"])
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.steam_path = Path(self.config["steam_path"])

        self.create_widgets()
        self.log_msg("Ready. Click 'Scan Saves' to begin.")

    def create_widgets(self):
        # === Top Frame: Controls ===
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(top_frame, text="Steam Backup Manager", font=("Arial", 14, "bold")).pack(side="left", padx=5)
        
        ttk.Button(top_frame, text="Scan Saves", command=self.scan_saves).pack(side="left", padx=5)
        ttk.Button(top_frame, text="Backup All", command=self.backup_all).pack(side="left", padx=5)
        ttk.Button(top_frame, text="Backup Selected", command=self.backup_selected).pack(side="left", padx=5)
        
        # === Status Frame ===
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(status_frame, text="Status:", font=("Arial", 10, "bold")).pack(side="left")
        self.status_label = ttk.Label(status_frame, text="Idle", foreground="blue")
        self.status_label.pack(side="left", padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(status_frame, length=300, mode="determinate")
        self.progress.pack(side="left", padx=20)
        
        # === Middle Frame: Saves Tree ===
        tree_frame = ttk.LabelFrame(self.root, text="Steam Saves", padding=10)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Scrollbars
        tree_scroll_y = ttk.Scrollbar(tree_frame)
        tree_scroll_y.pack(side="right", fill="y")
        
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")
        tree_scroll_x.pack(side="bottom", fill="x")
        
        # Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("Checkbox", "AppID", "Type"),
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set,
            height=12
        )
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        
        self.tree.column("#0", width=350)
        self.tree.heading("#0", text="Game Name / Steam ID")
        self.tree.column("Checkbox", width=60)
        self.tree.heading("Checkbox", text="Select")
        self.tree.column("AppID", width=100)
        self.tree.heading("AppID", text="AppID")
        self.tree.column("Type", width=80)
        self.tree.heading("Type", text="Type")
        
        # Track checked items (game items only)
        self.checked_games = set()
        
        # Bind click events for checkbox-like behavior
        self.tree.bind("<Button-1>", self.on_tree_click)
        
        self.tree.pack(fill="both", expand=True)
        
        # === Bottom Frame: Logs ===
        log_frame = ttk.LabelFrame(self.root, text="Log", padding=10)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        log_scroll = ttk.Scrollbar(log_frame)
        log_scroll.pack(side="right", fill="y")
        
        self.log = scrolledtext.ScrolledText(
            log_frame,
            height=8,
            yscrollcommand=log_scroll.set,
            font=("Courier", 9)
        )
        log_scroll.config(command=self.log.yview)
        self.log.pack(fill="both", expand=True)
        
        # === Footer: Info ===
        footer = ttk.Frame(self.root)
        footer.pack(fill="x", padx=10, pady=5)
        ttk.Label(footer, text=f"Backup dir: {self.backup_dir}", font=("Arial", 9)).pack(side="left")

    def log_msg(self, msg):
        """Add timestamped message to log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log.insert(tk.END, f"[{timestamp}] {msg}\n")
        self.log.see(tk.END)
        self.root.update()

    def update_status(self, status, color="black"):
        """Update status label."""
        self.status_label.config(text=status, foreground=color)
        self.root.update()

    def on_tree_click(self, event):
        """Handle tree clicks to toggle checkbox selection."""
        item = self.tree.identify("item", event.x, event.y)
        col = self.tree.identify_column(event.x)
        
        if not item or col != "#1":  # Only respond to clicks in Checkbox column
            return
        
        item_values = self.tree.item(item)
        # Only allow checking game items (AppID at values[1], Type at values[2])
        if len(item_values["values"]) >= 3 and item_values["values"][2] == "Game":
            app_id = item_values["values"][1]  # AppID is at index 1
            if app_id in self.checked_games:
                self.checked_games.discard(app_id)
                checkbox = "☐"
            else:
                self.checked_games.add(app_id)
                checkbox = "☑"
            
            # Update checkbox display, preserving AppID and Type
            self.tree.item(item, values=(checkbox, app_id, item_values["values"][2]))

    def get_game_info(self, app_id):
        """Find steam_id and save path for an app_id."""
        for steam_id, saves in self.saves.items():
            for save in saves:
                if save["app_id"] == app_id:
                    return steam_id, save
        return None, None

    def scan_saves(self):
        """Scan for Steam saves and populate tree."""
        self.update_status("Scanning for saves...", "orange")
        self.log_msg("Starting scan...")
        self.checked_games.clear()
        
        try:
            userdata = get_steam_userdata_path(self.steam_path)
            self.saves = scan_steam_saves_by_account(userdata)
            
            # Clear tree
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            total_saves = 0
            if not self.saves:
                self.log_msg("No Steam accounts or saves found.")
                self.update_status("No saves found", "red")
                return
            
            # Populate tree
            for steam_id in sorted(self.saves.keys()):
                save_list = self.saves[steam_id]
                steam_id_item = self.tree.insert("", "end", text=f"Steam ID: {steam_id}", values=("", "", "Account"))
                
                for save in save_list:
                    app_id = save["app_id"]
                    game_name = get_steam_game_name(int(app_id))
                    self.tree.insert(steam_id_item, "end", text=game_name, values=("☐", app_id, "Game"))
                    total_saves += 1
            
            self.log_msg(f"✓ Scan complete. Found {len(self.saves)} accounts and {total_saves} saves.")
            self.log_msg("Click checkboxes to select games, then click 'Backup Selected'.")
            self.update_status(f"Ready ({total_saves} saves)", "green")
            
        except Exception as e:
            self.log_msg(f"✗ Error during scan: {e}")
            self.update_status("Scan failed", "red")
            messagebox.showerror("Scan Error", f"Failed to scan saves:\n{e}")

    def backup_all(self):
        """Backup all discovered saves."""
        if not self.saves:
            messagebox.showwarning("No Saves", "Please scan for saves first.")
            return
        
        total = sum(len(saves) for saves in self.saves.values())
        if not messagebox.askyesno("Confirm", f"Backup all {total} saves?"):
            return
        
        self.update_status("Backing up all...", "orange")
        self.log_msg(f"Starting backup of {total} saves...")
        
        self.progress["maximum"] = total
        self.progress["value"] = 0
        
        count = 0
        for steam_id in sorted(self.saves.keys()):
            for save in self.saves[steam_id]:
                try:
                    game_name = get_steam_game_name(int(save["app_id"]))
                    zip_path = zip_save(save["path"], self.backup_dir, game_name, steam_id)
                    self.log_msg(f"✔ {game_name} (AppID: {save['app_id']}) → {zip_path.name}")
                    count += 1
                    self.progress["value"] = count
                except Exception as e:
                    self.log_msg(f"✗ Failed to backup AppID {save['app_id']}: {e}")
                
                self.root.update()
        
        self.log_msg(f"Backup complete! {count}/{total} saves backed up.")
        self.update_status(f"Complete ({count} backed up)", "green")
        self.progress["value"] = 0
        messagebox.showinfo("Success", f"Backup complete!\n{count} saves backed up.")

    def backup_selected(self):
        """Backup all checked games from tree."""
        if not self.checked_games:
            messagebox.showwarning("No Selection", "Please check at least one game to backup.")
            return
        
        if not messagebox.askyesno("Confirm", f"Backup {len(self.checked_games)} selected games?"):
            return
        
        self.update_status("Backing up selected...", "orange")
        self.log_msg(f"Starting backup of {len(self.checked_games)} selected games...")
        
        self.progress["maximum"] = len(self.checked_games)
        self.progress["value"] = 0
        
        count = 0
        failed = 0
        for app_id in self.checked_games:
            steam_id, save = self.get_game_info(app_id)
            if steam_id and save:
                try:
                    game_name = get_steam_game_name(int(app_id))
                    zip_path = zip_save(save["path"], self.backup_dir, game_name, steam_id)
                    self.log_msg(f"✔ {game_name} (AppID: {app_id}) → {zip_path.name}")
                    count += 1
                except Exception as e:
                    self.log_msg(f"✗ Failed to backup AppID {app_id}: {e}")
                    failed += 1
            
            self.progress["value"] = count + failed
            self.root.update()
        
        self.log_msg(f"Backup complete! {count} succeeded, {failed} failed.")
        self.update_status(f"Backup complete ({count} OK, {failed} failed)", "green" if failed == 0 else "orange")
        self.progress["value"] = 0
        messagebox.showinfo("Success", f"Backup complete!\n{count} games backed up.\n{failed} failed.")

if __name__ == "__main__":
    root = tk.Tk()
    app = GameSaveBackupUI(root)
    root.mainloop()
