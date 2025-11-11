import os
import fitz  # PyMuPDF
from utils.config_utils import read_config
from datetime import datetime

def analyse_pdfs(folder):
    """
    Analyseer alle PDF's in de opgegeven folder.
    - Bestanden met tekst krijgen suffix (TXT).pdf
    - Bestanden zonder tekst krijgen suffix (OCR).pdf
    - Case-insensitive checks voor .pdf, (TXT), (OCR)
    - Debug output per bestand
    """
    print("Analyse gestart...")

    if not os.path.isdir(folder):
        print(f"FOUT: folder bestaat niet of is niet toegankelijk: {folder}")
        return

    candidates = [f for f in os.listdir(folder)
                  if f.lower().endswith(".pdf")
                  and "(txt)" not in f.lower()
                  and "(ocr)" not in f.lower()]

    if not candidates:
        print("Geen nieuwe PDF-bestanden gevonden om te analyseren.")
        print("Analyse afgerond.")
        return

    for file in candidates:
        path = os.path.join(folder, file)
        print(f"Analyseer bestand: {file}")

        try:
            doc = fitz.open(path)
            text = "".join(page.get_text() for page in doc)
            doc.close()
        except Exception as e:
            print(f"FOUT bij openen {file}: {e}")
            continue

        if text.strip():
            new_name = file.replace(".pdf", "(TXT).pdf").replace(".PDF", "(TXT).pdf")
            print(f"Tekst gevonden in {file} → hernoemen naar {new_name}")
        else:
            new_name = file.replace(".pdf", "(OCR).pdf").replace(".PDF", "(OCR).pdf")
            print(f"Geen tekst gevonden in {file} → hernoemen naar {new_name}")

        new_path = os.path.join(folder, new_name)
        if not os.path.exists(new_path):
            try:
                os.rename(path, new_path)
                print(f"Hernoemd: {file} → {new_name}")
            except Exception as e_rename:
                print(f"FOUT bij hernoemen {file}: {e_rename}")
        else:
            print(f"SKIPPED: {new_name} bestaat al")

    print("Analyse afgerond.")

if __name__ == "__main__":
    config = read_config()
    folder = config.get("MAIN_FOLDER")
    if not folder:
        raise RuntimeError("MAIN_FOLDER ontbreekt in config.env")

    print(f"[{datetime.now().isoformat()}] Standalone analyse run")
    analyse_pdfs(folder)
