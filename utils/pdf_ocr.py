import os
import io
import pytesseract
from pdf2image import convert_from_path
from PyPDF2 import PdfWriter, PdfReader
from utils.config_utils import read_config

def ocr_pdfs(folder, poppler_path, tesseract_path):
    """
    Voer OCR uit op alle (OCR).pdf bestanden in de opgegeven folder.
    - Alleen bestanden die nog geen (TXT).pdf hebben worden verwerkt.
    - Resultaat wordt opgeslagen als (TXT).pdf.
    """
    print("OCR gestart...")
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

    for file in os.listdir(folder):
        if file.endswith("(OCR).pdf"):
            base_name = file.replace("(OCR).pdf", "")
            txt_file = os.path.join(folder, base_name + "(TXT).pdf")

            if os.path.exists(txt_file):
                print(f"SKIPPED: {txt_file} bestaat al")
                continue

            ocr_path = os.path.join(folder, file)
            print(f"OCR uitvoeren op: {ocr_path}")

            try:
                images = convert_from_path(ocr_path, poppler_path=poppler_path)
                writer = PdfWriter()
                for img in images:
                    text_pdf = pytesseract.image_to_pdf_or_hocr(img, extension='pdf')
                    reader = PdfReader(io.BytesIO(text_pdf))
                    writer.add_page(reader.pages[0])

                with open(txt_file, "wb") as f_out:
                    writer.write(f_out)

                print(f"OCR voltooid: {txt_file}")

            except Exception as e:
                print(f"FOUT bij OCR {file}: {e}")
    print("OCR afgerond.")

if __name__ == "__main__":
    config = read_config()
    folder = config.get("MAIN_FOLDER")
    poppler_path = config.get("POPPLER_PATH")
    tesseract_path = config.get("TESSERACT_PATH")

    if not folder or not poppler_path or not tesseract_path:
        raise RuntimeError("MAIN_FOLDER, POPPLER_PATH of TESSERACT_PATH ontbreekt in config.env")

    ocr_pdfs(folder, poppler_path, tesseract_path)
