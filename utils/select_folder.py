import os
import tkinter as tk
from tkinter import filedialog

CONFIG_FILE = "config.env"

def read_config():
    """Lees alle key=value paren uit config.env in een dict."""
    config = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    config[key] = value
    return config

def update_config(key, value):
    """Update of voeg een key=value toe in config.env zonder andere te verwijderen."""
    config = read_config()
    config[key] = value
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        for k, v in config.items():
            f.write(f"{k}={v}\n")

def get_main_folder():
    """Dialoog om hoofdmap te kiezen en opslaan in environment + config.env."""
    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title="Selecteer hoofdmap met PDF's")

    if folder:
        # Normaliseer pad naar OS-stijl (voorkomt slash-verschillen)
        folder = os.path.normpath(folder)

        # Zet environment variabele voor huidige sessie
        os.environ["MAIN_FOLDER"] = folder

        # Update config.env zonder andere variabelen kwijt te raken
        update_config("MAIN_FOLDER", folder)

    return folder

if __name__ == "__main__":
    chosen = get_main_folder()
    print(f"Hoofdmap ingesteld op: {chosen}")
