import os
import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
import csv

def has_text(pdf_path):
    """Check of een PDF tekst bevat."""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text = page.get_text()
            if text.strip():
                return True
        return False
    except Exception as e:
        print(f"Fout bij {pdf_path}: {e}")
        return False

def rename_pdfs(root_folder):
    log_file = os.path.join(root_folder, "logs", "pdf_rename_log.csv")
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    with open(log_file, mode="a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        if os.stat(log_file).st_size == 0:
            writer.writerow(["timestamp", "old_path", "new_path", "status"])

        for dirpath, _, filenames in os.walk(root_folder):
            for filename in filenames:
                if filename.lower().endswith(".pdf"):
                    full_path = os.path.join(dirpath, filename)
                    base, ext = os.path.splitext(full_path)

                    # Check of er al een suffix is
                    if base.endswith("(TXT)") or base.endswith("(OCR)"):
                        writer.writerow([datetime.now(), full_path, full_path, "already tagged"])
                        continue

                    # Bepaal suffix
                    if has_text(full_path):
                        new_path = base + " (TXT)" + ext
                    else:
                        new_path = base + " (OCR)" + ext

                    try:
                        os.rename(full_path, new_path)
                        writer.writerow([datetime.now(), full_path, new_path, "renamed"])
                        print(f"Hernoemd: {filename} -> {os.path.basename(new_path)}")
                    except Exception as e:
                        writer.writerow([datetime.now(), full_path, full_path, f"error: {e}"])

# === Dialoog voor mapselectie ===
root = tk.Tk()
root.withdraw()  # Verberg hoofdvenster
chosen_dir = filedialog.askdirectory(title="Kies de hoofdmap met PDF-bestanden")

if chosen_dir:
    print(f"Gekozen hoofdmap: {chosen_dir}")
    rename_pdfs(chosen_dir)
else:
    print("Geen map gekozen, script gestopt.")
