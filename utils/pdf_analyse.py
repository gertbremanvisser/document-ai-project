import os
import fitz  # PyMuPDF
from utils.config_utils import read_config

def analyse_pdfs(folder):
    """Analyseer PDF's en hernoem naar (TXT) of (OCR)."""
    for file in os.listdir(folder):
        if file.endswith(".pdf") and not ("(TXT)" in file or "(OCR)" in file):
            path = os.path.join(folder, file)
            doc = fitz.open(path)

            # Tekst extractie
            text = "".join(page.get_text() for page in doc)

            # Bepaal suffix
            if text.strip():
                new_name = file.replace(".pdf", "(TXT).pdf")
            else:
                new_name = file.replace(".pdf", "(OCR).pdf")

            new_path = os.path.join(folder, new_name)

            # Alleen hernoemen als bestand nog niet bestaat
            if not os.path.exists(new_path):
                os.rename(path, new_path)
                print(f"{file} → {new_name}")
            else:
                print(f"SKIPPED: {new_name} bestaat al")

if __name__ == "__main__":
    config = read_config()
    folder = config.get("MAIN_FOLDER")

    if not folder or not os.path.isdir(folder):
        raise RuntimeError("MAIN_FOLDER ontbreekt of is ongeldig. Draai eerst select_folder.py.")

    analyse_pdfs(folder)
