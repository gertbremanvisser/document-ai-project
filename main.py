# main.py
import sys
from utils import select_folder, pdf_analyse, pdf_ocr
from utils.config_utils import read_config

def main():
    # Stap 1: hoofdmap bevestigen/kiezen
    select_folder.main()

    # Stap 2: analyse uitvoeren
    config = read_config()
    folder = config.get("MAIN_FOLDER")
    if not folder:
        raise RuntimeError("MAIN_FOLDER ontbreekt. Draai select_folder opnieuw.")
    pdf_analyse.analyse_pdfs(folder)

    # Stap 3: OCR uitvoeren
    poppler_path = config.get("POPPLER_PATH")
    tesseract_path = config.get("TESSERACT_PATH")
    if not poppler_path or not tesseract_path:
        raise RuntimeError("POPPLER_PATH of TESSERACT_PATH ontbreekt in config.env.")
    pdf_ocr.ocr_pdfs(folder, poppler_path, tesseract_path)

if __name__ == "__main__":
    sys.exit(main())
