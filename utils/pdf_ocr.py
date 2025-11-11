import os
import io
import time
from datetime import datetime

import pytesseract
from pdf2image import convert_from_path
from PyPDF2 import PdfWriter, PdfReader

from utils.config_utils import read_config

def _debug_dir(base_folder, base_name):
    dbg = os.path.join(base_folder, f"{base_name}_ocr_debug")
    os.makedirs(dbg, exist_ok=True)
    return dbg

def _write_final_pdf(writer, out_path):
    tmp_path = out_path + ".tmp"
    with open(tmp_path, "wb") as f_out:
        writer.write(f_out)
    if os.path.exists(out_path):
        os.remove(out_path)
    os.replace(tmp_path, out_path)

def choose_dpi():
    print("\n=== Kies DPI voor OCR ===")
    print("1) 150 (snel, lagere kwaliteit)")
    print("2) 200 (balans snelheid/kwaliteit)")
    print("3) 300 (hogere kwaliteit, trager)")
    print("4) 400 (zeer hoge kwaliteit, traag)")
    print("5) Anders (voer zelf een getal in)")
    choice = input("Maak een keuze (1-5): ").strip()

    mapping = {"1": 150, "2": 200, "3": 300, "4": 400}
    if choice in mapping:
        return mapping[choice]
    elif choice == "5":
        try:
            dpi_val = int(input("Voer een DPI getal in (72-600): ").strip())
            if dpi_val < 72 or dpi_val > 600:
                print("Ongeldige waarde, gebruik standaard 200 DPI.")
                return 200
            return dpi_val
        except Exception:
            print("Kon invoer niet verwerken, gebruik standaard 200 DPI.")
            return 200
    else:
        print("Ongeldige keuze, gebruik standaard 200 DPI.")
        return 200

def ocr_pdfs(folder, poppler_path, tesseract_path, debug_ocr=False, dpi=200):
    """
    OCR per pagina:
    - Render elke pagina naar PNG (pdf2image).
    - OCR per pagina met Tesseract.
    - Voeg alle pagina's samen tot één (TXT).pdf.
    - Optioneel: debug PNG/HOCR per pagina.
    """
    print("OCR gestart...")
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

    candidates = [f for f in os.listdir(folder) if f.lower().endswith("(ocr).pdf")]
    if not candidates:
        print("Geen (OCR).pdf bestanden gevonden. Niets te doen.")
        print("OCR afgerond.")
        return

    for file in candidates:
        base_name = file[:-8]  # strip "(OCR).pdf"
        ocr_path = os.path.join(folder, file)
        txt_path = os.path.join(folder, base_name + "(TXT).pdf")

        if os.path.exists(txt_path):
            print(f"SKIPPED: {txt_path} bestaat al")
            continue

        print(f"OCR uitvoeren op: {ocr_path}")

        dbg_dir = None
        if debug_ocr:
            dbg_dir = _debug_dir(folder, base_name)
            print(f"Debug output: {dbg_dir}")

        try:
            src_reader = PdfReader(ocr_path)
            page_count = len(src_reader.pages)
            print(f"{page_count} pagina's gevonden")

            writer = PdfWriter()
            non_empty_pages = 0

            start_total = time.time()

            for i in range(1, page_count + 1):
                start_page = time.time()
                print(f"Render pagina {i}/{page_count} (DPI={dpi})")
                images = convert_from_path(
                    ocr_path,
                    poppler_path=poppler_path,
                    dpi=dpi,
                    first_page=i,
                    last_page=i
                )
                img = images[0]

                if dbg_dir:
                    img_path = os.path.join(dbg_dir, f"page_{i:03d}.png")
                    img.save(img_path, "PNG")
                    print(f"Saved debug image: {img_path}")

                print(f"OCR pagina {i}")
                try:
                    page_pdf_bytes = pytesseract.image_to_pdf_or_hocr(img, extension='pdf')
                    reader = PdfReader(io.BytesIO(page_pdf_bytes))
                    writer.add_page(reader.pages[0])

                    plain_text = pytesseract.image_to_string(img)
                    preview = plain_text[:120].replace("\n", " ").strip()
                    if preview:
                        non_empty_pages += 1
                    print(f"Preview pagina {i}: {repr(preview)}")

                    if dbg_dir:
                        hocr = pytesseract.image_to_pdf_or_hocr(img, extension='hocr')
                        hocr_path = os.path.join(dbg_dir, f"page_{i:03d}.hocr")
                        with open(hocr_path, "wb") as fh:
                            fh.write(hocr)
                        print(f"Saved debug HOCR: {hocr_path}")

                except Exception as e_page:
                    print(f"FOUT: OCR gefaald op pagina {i}: {e_page}")

                duration_page = time.time() - start_page
                print(f"Tijd voor pagina {i}: {duration_page:.2f} seconden")

            if len(writer.pages) == 0:
                print("FOUT: geen pagina's toegevoegd aan output. (TXT).pdf wordt niet aangemaakt.")
                continue

            _write_final_pdf(writer, txt_path)
            duration_total = time.time() - start_total
            print(f"OCR voltooid: {txt_path}")
            print(f"Niet-lege tekstpagina's: {non_empty_pages} van {page_count}")
            print(f"Totaal OCR duur: {duration_total:.2f} seconden")

        except Exception as e:
            print(f"FOUT bij OCR '{file}': {e}")

    print("OCR afgerond.")

if __name__ == "__main__":
    config = read_config()
    folder = config.get("MAIN_FOLDER")
    poppler_path = config.get("POPPLER_PATH")
    tesseract_path = config.get("TESSERACT_PATH")
    debug_flag = config.get("DEBUG_OCR", "0").strip() == "1"

    if not folder or not poppler_path or not tesseract_path:
        raise RuntimeError("MAIN_FOLDER, POPPLER_PATH of TESSERACT_PATH ontbreekt in config.env")

    dpi = choose_dpi()
    print(f"[{datetime.now().isoformat()}] Standalone OCR run (DPI={dpi})")
    ocr_pdfs(folder, poppler_path, tesseract_path, debug_ocr=debug_flag, dpi=dpi)
