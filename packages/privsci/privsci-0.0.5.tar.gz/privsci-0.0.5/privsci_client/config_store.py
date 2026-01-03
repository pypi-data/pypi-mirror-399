from pathlib import Path
import json

APP_DIR = Path.home() / ".privsci"
CONFIG_PATH = APP_DIR / "config.json"
DEFAULT_DB_PATH = f"sqlite:///{APP_DIR}/privsci.db"

DEFAULTS = {
    "DEFAULT_DB": True,
    "DB_URL": DEFAULT_DB_PATH,
    "ORG_NAME": "",
    "DOMAIN": "",
    "REPRESENTATION": ""
}

def load_config():
    config = DEFAULTS.copy()
    if not CONFIG_PATH.exists():
        return config
    
    try:
        with open(CONFIG_PATH, "r") as f:
            content = f.read().strip()
            if content:
                user_config = json.loads(content)
                config.update(user_config)
    except json.JSONDecodeError:
        pass

    return config

def save_config(config: dict):
    APP_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)

_current_config = load_config()

DEFAULT_DB = _current_config["DEFAULT_DB"]
DB_URL = _current_config["DB_URL"]
ORG_NAME = _current_config["ORG_NAME"]
DOMAIN = _current_config["DOMAIN"]
REPRESENTATION = _current_config["REPRESENTATION"]