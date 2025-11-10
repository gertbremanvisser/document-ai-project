import os
import csv
from datetime import datetime
from pdf2image import convert_from_path
import pytesseract
from PyPDF2 import PdfWriter

CONFIG_FILE = "config.env"

def read_config():
    """Lees config.env en haal MAIN_FOLDER en POPPLER_PATH op."""
    config = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    config[key] = value
    return config

def get_folder(config):
    folder = config.get("MAIN_FOLDER")
    if folder and os.path.isdir(folder):
        return folder
    raise RuntimeError("Geen hoofdmap ingesteld. Draai eerst select_folder.py.")

def get_poppler_path(config):
    return config.get("POPPLER_PATH")

def ocr_pdf(input_path, output_path, poppler_path=None):
    """Voer OCR uit op een PDF en schrijf een nieuwe (TXT)-versie."""
    images = convert_from_path(input_path, poppler_path=poppler_path)
    pdf_writer = PdfWriter()
    for img in images:
        text_pdf = pytesseract.image_to_pdf_or_hocr(img, extension='pdf')
        pdf_writer.add_page(PdfWriter(text_pdf).pages[0])
    with open(output_path, "wb") as f_out:
        pdf_writer.write(f_out)

def log_action(logfile, original, new, action, status):
    """Schrijf een logregel naar ocr_log.csv."""
    with open(logfile, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().isoformat(), original, new, action, status])

def ocr_pdfs(folder, poppler_path=None):
    logfile = os.path.join(folder, "ocr_log.csv")
    for file in os.listdir(folder):
        if file.endswith("(OCR).pdf"):
            base = file.replace("(OCR).pdf", "")
            txt_file = f"{base}(TXT).pdf"
            txt_path = os.path.join(folder, txt_file)

            if os.path.exists(txt_path):
                log_action(logfile, file, txt_file, "SKIPPED", "TXT_EXISTS")
            else:
                try:
                    input_path = os.path.join(folder, file)
                    ocr_pdf(input_path, txt_path, poppler_path=poppler_path)
                    log_action(logfile, file, txt_file, "OCR_EXECUTED", "SUCCESS")
                except Exception as e:
                    log_action(logfile, file, txt_file, "OCR_EXECUTED", f"ERROR: {e}")

if __name__ == "__main__":
    config = read_config()
    folder = get_folder(config)
    poppler_path = get_poppler_path(config)
    ocr_pdfs(folder, poppler_path=poppler_path)
