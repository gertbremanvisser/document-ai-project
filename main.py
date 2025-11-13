import sys
import os
import csv
from datetime import datetime
from utils import select_folder, pdf_analyse, pdf_ocr
from utils.config_utils import read_config, set_env_from_config, ensure_msys2_path
from utils.kindle_pipeline import kindle_to_pdf_pipeline
from utils.epub_pipeline import epub_to_pdf_pipeline

LOG_FILE = os.path.join(os.path.dirname(__file__), "logs", "project_setup_log.csv")

def log_action(action, detail=""):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().isoformat(), action, detail])

def main():
    log_action("WORKFLOW_START", "Workflow gestart")

    # Stap 1: hoofdmap bevestigen/kiezen
    select_folder.main()
    print("Stap 1: select_folder klaar")

    # Config laden en MSYS2 path injecteren
    config = read_config()
    set_env_from_config(config)
    ensure_msys2_path()

    folder = config.get("MAIN_FOLDER")
    if not folder:
        log_action("ERROR", "MAIN_FOLDER ontbreekt")
        raise RuntimeError("MAIN_FOLDER ontbreekt. Draai select_folder opnieuw.")

    # Stap 2: Kindle → PDF
    print("Stap 2: Kindle-bestanden omzetten naar PDF")
    try:
        kindle_to_pdf_pipeline(folder)
        log_action("KINDLE_TO_PDF", "Kindle-bestanden verwerkt")
    except Exception as e:
        log_action("ERROR", f"Kindle pipeline fout: {e}")
    print("Stap 2: Kindle → PDF klaar")

    # Stap 3: EPUB → PDF
    print("Stap 3: EPUB-bestanden omzetten naar PDF")
    try:
        epub_to_pdf_pipeline(folder)
        log_action("EPUB_TO_PDF", "EPUB-bestanden verwerkt")
    except Exception as e:
        log_action("ERROR", f"EPUB pipeline fout: {e}")
    print("Stap 3: EPUB → PDF klaar")

    # Stap 4: analyse uitvoeren
    print("Stap 4: analyse uitvoeren")
    try:
        pdf_analyse.analyse_pdfs(folder)
        log_action("PDF_ANALYSE", "Analyse uitgevoerd")
    except Exception as e:
        log_action("ERROR", f"Analyse fout: {e}")
    print("Stap 4: analyse klaar")

    # Stap 5: OCR uitvoeren
    print("Stap 5: OCR uitvoeren")
    poppler_path = config.get("POPPLER_PATH")
    tesseract_path = config.get("TESSERACT_PATH")
    if not poppler_path or not tesseract_path:
        log_action("ERROR", "POPPLER_PATH of TESSERACT_PATH ontbreekt")
        raise RuntimeError("POPPLER_PATH of TESSERACT_PATH ontbreekt in config.env.")
    try:
        pdf_ocr.ocr_pdfs(folder, poppler_path, tesseract_path)
        log_action("PDF_OCR", "OCR uitgevoerd")
    except Exception as e:
        log_action("ERROR", f"OCR fout: {e}")
    print("Stap 5: OCR klaar")

    log_action("WORKFLOW_END", "Workflow afgerond")

if __name__ == "__main__":
    sys.exit(main())
