import os
import csv
from datetime import datetime
from pdf2image import convert_from_path
import pytesseract
from PyPDF2 import PdfWriter
from utils.config_utils import read_config

def ocr_pdf(input_path, output_path, poppler_path, tesseract_path):
    # Zet expliciet het pad naar tesseract.exe
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

    images = convert_from_path(input_path, poppler_path=poppler_path)
    pdf_writer = PdfWriter()
    for img in images:
        text_pdf = pytesseract.image_to_pdf_or_hocr(img, extension='pdf')
        pdf_writer.add_page(PdfWriter(text_pdf).pages[0])
    with open(output_path, "wb") as f_out:
        pdf_writer.write(f_out)

def ocr_pdfs(folder, poppler_path, tesseract_path):
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
                    ocr_pdf(input_path, txt_path, poppler_path, tesseract_path)
                    log_action(logfile, file, txt_file, "OCR_EXECUTED", "SUCCESS")
                except Exception as e:
                    log_action(logfile, file, txt_file, "OCR_EXECUTED", f"ERROR: {e}")

def log_action(logfile, original, new, action, status):
    with open(logfile, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().isoformat(), original, new, action, status])

if __name__ == "__main__":
    config = read_config()
    folder = config.get("MAIN_FOLDER")
    poppler_path = config.get("POPPLER_PATH")
    tesseract_path = config.get("TESSERACT_PATH")
    if not folder or not poppler_path or not tesseract_path:
        raise RuntimeError("Config mist MAIN_FOLDER, POPPLER_PATH of TESSERACT_PATH")
    ocr_pdfs(folder, poppler_path, tesseract_path)
