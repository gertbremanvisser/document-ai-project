import os

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "..", "config.env")

def read_config():
    config = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    config[key] = value
    return config
