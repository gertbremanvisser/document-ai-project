import os
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
    # Configureer Tesseract
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
                # Converteer PDF naar afbeeldingen
                images = convert_from_path(ocr_path, poppler_path=poppler_path)

                # OCR uitvoeren per pagina
                writer = PdfWriter()
                for i, img in enumerate(images):
                    text = pytesseract.image_to_pdf_or_hocr(img, extension='pdf')
                    reader = PdfReader(io.BytesIO(text))
                    writer.add_page(reader.pages[0])

                # Opslaan als (TXT).pdf
                with open(txt_file, "wb") as f_out:
                    writer.write(f_out)

                print(f"OCR voltooid: {txt_file}")

            except Exception as e:
                print(f"FOUT bij OCR {file}: {e}")

if __name__ == "__main__":
    config = read_config()
    folder = config.get("MAIN_FOLDER")
    poppler_path = config.get("POPPLER_PATH")
    tesseract_path = config.get("TESSERACT_PATH")

    if not folder or not poppler_path or not tesseract_path:
        raise RuntimeError("MAIN_FOLDER, POPPLER_PATH of TESSERACT_PATH ontbreekt in config.env")

    ocr_pdfs(folder, poppler_path, tesseract_path)
