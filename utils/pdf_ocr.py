import os
from select_folder import get_main_folder
from pdf2image import convert_from_path
import pytesseract
from PyPDF2 import PdfWriter
import csv
from datetime import datetime

def ocr_pdf(input_path, output_path):
    images = convert_from_path(input_path)
    pdf_writer = PdfWriter()
    for img in images:
        text_pdf = pytesseract.image_to_pdf_or_hocr(img, extension='pdf')
        pdf_writer.add_page(PdfWriter(text_pdf).pages[0])
    with open(output_path, "wb") as f_out:
        pdf_writer.write(f_out)

def log_action(logfile, original, new, action, status):
    with open(logfile, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().isoformat(), original, new, action, status])

def ocr_pdfs(folder):
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
                    ocr_pdf(input_path, txt_path)
                    log_action(logfile, file, txt_file, "OCR_EXECUTED", "SUCCESS")
                except Exception as e:
                    log_action(logfile, file, txt_file, "OCR_EXECUTED", f"ERROR: {e}")

if __name__ == "__main__":
    folder = get_main_folder()
    ocr_pdfs(folder)
