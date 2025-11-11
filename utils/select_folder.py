import os
import csv
from datetime import datetime
import tkinter as tk
from tkinter import filedialog
from utils.config_utils import read_config, write_config

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "..", "config.env")
LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "logs", "project_setup_log.csv")

def ensure_dir_valid(path):
    return bool(path and os.path.isdir(path))

def pick_folder_dialog(initial=None):
    root = tk.Tk()
    root.withdraw()
    if initial and ensure_dir_valid(initial):
        folder = filedialog.askdirectory(title="Bevestig of kies hoofdmap", initialdir=initial)
    else:
        folder = filedialog.askdirectory(title="Selecteer hoofdmap met PDF's")
    return os.path.normpath(folder) if folder else None

def log_action(action, folder):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().isoformat(), action, folder])

def set_main_folder(folder, config):
    folder = os.path.normpath(folder)
    os.environ["MAIN_FOLDER"] = folder
    config["MAIN_FOLDER"] = folder
    write_config(config)
    log_action("MAIN_FOLDER_SET", folder)

def main():
    config = read_config()
    current = config.get("MAIN_FOLDER")

    # Dialoog altijd tonen, met default selectie indien geldig
    chosen = pick_folder_dialog(initial=current)

    if not chosen:
        raise RuntimeError("Geen map geselecteerd. MAIN_FOLDER blijft ongewijzigd.")

    if not ensure_dir_valid(chosen):
        raise RuntimeError(f"Gekozen map ongeldig of niet toegankelijk: {chosen}")

    set_main_folder(chosen, config)
    print(f"MAIN_FOLDER ingesteld/bevestigd op: {chosen}")

if __name__ == "__main__":
    main()
