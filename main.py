import sys
import os
import csv
from datetime import datetime
from utils import select_folder, pdf_analyse, pdf_ocr
from utils.config_utils import read_config

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

    # Stap 2: analyse uitvoeren
    config = read_config()
    folder = config.get("MAIN_FOLDER")
    if not folder:
        log_action("ERROR", "MAIN_FOLDER ontbreekt")
        raise RuntimeError("MAIN_FOLDER ontbreekt. Draai select_folder opnieuw.")
    pdf_analyse.analyse_pdfs(folder)

    # Stap 3: OCR uitvoeren
    poppler_path = config.get("POPPLER_PATH")
    tesseract_path = config.get("TESSERACT_PATH")
    if not poppler_path or not tesseract_path:
        log_action("ERROR", "POPPLER_PATH of TESSERACT_PATH ontbreekt")
        raise RuntimeError("POPPLER_PATH of TESSERACT_PATH ontbreekt in config.env.")
    pdf_ocr.ocr_pdfs(folder, poppler_path, tesseract_path)

    log_action("WORKFLOW_END", "Workflow afgerond")

if __name__ == "__main__":
    sys.exit(main())
