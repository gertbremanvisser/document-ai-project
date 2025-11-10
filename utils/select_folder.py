import tkinter as tk
from tkinter import filedialog

def get_main_folder():
    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title="Selecteer hoofdmap met PDF's")
    return folder

if __name__ == "__main__":
    print(get_main_folder())
