import os

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "..", "config.env")

def read_config():
    """
    Lees config.env en retourneer een dict met key/value paren.
    """
    config = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    config[k] = v
    return config

def write_config(config):
    """
    Schrijf een dict terug naar config.env.
    """
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        for k, v in config.items():
            f.write(f"{k}={v}\n")

def set_env_from_config(config):
    """
    Zet alle keys uit config ook in os.environ voor de huidige sessie.
    """
    for k, v in config.items():
        os.environ[k] = v
