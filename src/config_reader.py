from pathlib import Path
import yaml

def read_config(config_path: Path) -> dict:
    if not config_path.exists():
        print(f"Config file not found: {config_path}")
        return {}
    
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}
