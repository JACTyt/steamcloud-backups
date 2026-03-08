from pathlib import Path
from src.config_reader import read_config

# Default configuration values
DEFAULT_CONFIG = {
    "backup_dir": "backups",
    "steam_path": "C:/Program Files (x86)/Steam",
    "keep_versions": 5,
}

# Required keys that must be present
REQUIRED_KEYS = {"backup_dir", "steam_path"}


def get_config(config_path: Path) -> dict:
    """
    Load and validate configuration from YAML file.
    
    Args:
        config_path: Path to config.yaml
        
    Returns:
        Validated config dict with all keys and defaults applied
        
    Raises:
        ValueError: If required keys are missing
        FileNotFoundError: If config file doesn't exist
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    raw_config = read_config(config_path)
    
    if raw_config is None:
        raw_config = {}
    
    # Check for required keys
    missing_keys = REQUIRED_KEYS - set(raw_config.keys())
    if missing_keys:
        raise ValueError(f"Missing required config keys: {missing_keys}")
    
    # Merge with defaults (user config overrides defaults)
    config = {**DEFAULT_CONFIG, **raw_config}
    
    return config
