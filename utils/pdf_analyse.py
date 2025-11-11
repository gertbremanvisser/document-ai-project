import os
import fitz  # PyMuPDF
from utils.config_utils import read_config

def analyse_pdfs(folder):
    """
    Analyseer alle PDF's in de opgegeven folder.
    - Bestanden met tekst krijgen suffix (TXT).pdf
    - Bestanden zonder tekst krijgen suffix (OCR).pdf
    """
    print("Analyse gestart...")
    for file in os.listdir(folder):
        fname = file.lower()
        if fname.endswith(".pdf") and not ("(txt)" in fname or "(ocr)" in fname):
            path = os.path.join(folder, file)
            try:
                doc = fitz.open(path)
                text = "".join(page.get_text() for page in doc)
                doc.close()
            except Exception as e:
                print(f"FOUT bij openen {file}: {e}")
                continue

            if text.strip():
                new_name = file.replace(".pdf", "(TXT).pdf").replace(".PDF", "(TXT).pdf")
            else:
                new_name = file.replace(".pdf", "(OCR).pdf").replace(".PDF", "(OCR).pdf")

            new_path = os.path.join(folder, new_name)
            if not os.path.exists(new_path):
                os.rename(path, new_path)
                print(f"{file} → {new_name}")
            else:
                print(f"SKIPPED: {new_name} bestaat al")
    print("Analyse afgerond.")

if __name__ == "__main__":
    config = read_config()
    folder = config.get("MAIN_FOLDER")
    if not folder:
        raise RuntimeError("MAIN_FOLDER ontbreekt in config.env")
    analyse_pdfs(folder)
