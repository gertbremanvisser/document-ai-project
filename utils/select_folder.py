import os
import tkinter as tk
from tkinter import filedialog

def get_main_folder():
    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title="Selecteer hoofdmap met PDF's")

    if folder:
        # Zet environment‑variabele voor deze sessie
        os.environ["MAIN_FOLDER"] = folder

        # Optioneel: schrijf naar config zodat het ook bij volgende runs beschikbaar is
        with open("config.env", "w", encoding="utf-8") as f:
            f.write(f"MAIN_FOLDER={folder}\n")

    return folder

if __name__ == "__main__":
    chosen = get_main_folder()
    print(f"Hoofdmap ingesteld op: {chosen}")
