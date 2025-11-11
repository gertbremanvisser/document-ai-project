import os
import io
import sys
from datetime import datetime

import pytesseract
from pdf2image import convert_from_path
from PyPDF2 import PdfWriter, PdfReader

from utils.config_utils import read_config

def _debug_dir(base_folder, base_name):
    """
    Create and return a debug folder path for a given PDF.
    Only used when DEBUG_OCR=1 in config.
    """
    dbg = os.path.join(base_folder, f"{base_name}_ocr_debug")
    os.makedirs(dbg, exist_ok=True)
    return dbg

def _write_final_pdf(writer, out_path):
    """
    Safely write the combined OCR PDF.
    """
    tmp_path = out_path + ".tmp"
    with open(tmp_path, "wb") as f_out:
        writer.write(f_out)
    # Atomic-like move on Windows
    if os.path.exists(out_path):
        os.remove(out_path)
    os.replace(tmp_path, out_path)

def ocr_pdfs(folder, poppler_path, tesseract_path, debug_ocr=False, dpi=300):
    """
    Run OCR on all (OCR).pdf files in the folder, creating (TXT).pdf if missing.

    - Converts each page to an image via Poppler (pdf2image).
    - Uses Tesseract to produce a per-page searchable PDF (image_to_pdf_or_hocr).
    - Merges pages into one (TXT).pdf using PyPDF2.
    - With debug_ocr=True, saves intermediate PNGs and HOCR files per page for inspection.

    Args:
        folder (str): Folder containing PDFs.
        poppler_path (str): Path to Poppler binaries (bin directory).
        tesseract_path (str): Full path to tesseract.exe.
        debug_ocr (bool): If True, dump per-page images and HOCR outputs.
        dpi (int): Render DPI for pdf2image. Higher DPI increases quality and time.
    """
    print("OCR gestart...")
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

    # Sanity check
    if not os.path.isdir(folder):
        print(f"FOUT: folder bestaat niet of is niet toegankelijk: {folder}")
        return

    # Collect candidates
    candidates = [f for f in os.listdir(folder) if f.endswith("(OCR).pdf")]
    if not candidates:
        print("Geen (OCR).pdf bestanden gevonden. Niets te doen.")
        print("OCR afgerond.")
        return

    for file in candidates:
        base_name = file.replace("(OCR).pdf", "")
        ocr_path = os.path.join(folder, file)
        txt_path = os.path.join(folder, base_name + "(TXT).pdf")

        if os.path.exists(txt_path):
            print(f"SKIPPED: {txt_path} bestaat al")
            continue

        print(f"OCR uitvoeren op: {ocr_path}")

        # Optional debug dir
        dbg_dir = None
        if debug_ocr:
            dbg_dir = _debug_dir(folder, base_name)
            print(f"Debug output: {dbg_dir}")

        try:
            print(f"Converteer {ocr_path} naar afbeeldingen (DPI={dpi})...")
            images = convert_from_path(ocr_path, poppler_path=poppler_path, dpi=dpi)
            page_count = len(images)
            print(f"{page_count} pagina's gevonden")

            writer = PdfWriter()
            non_empty_pages = 0

            for i, img in enumerate(images, start=1):
                # Optional: persist image for inspection
                if dbg_dir:
                    img_path = os.path.join(dbg_dir, f"page_{i:03d}.png")
                    try:
                        img.save(img_path, "PNG")
                        print(f"Saved debug image: {img_path}")
                    except Exception as e_img:
                        print(f"WAARSCHUWING: kon debug image niet opslaan voor pagina {i}: {e_img}")

                print(f"OCR pagina {i}/{page_count}")
                try:
                    # PDF output (searchable image overlaid with text)
                    page_pdf_bytes = pytesseract.image_to_pdf_or_hocr(img, extension='pdf')
                    reader = PdfReader(io.BytesIO(page_pdf_bytes))
                    writer.add_page(reader.pages[0])

                    # Plain text check (helps detect empty or non-recognized pages)
                    plain_text = pytesseract.image_to_string(img)
                    preview = plain_text[:120].replace("\n", " ").strip()
                    if preview:
                        non_empty_pages += 1
                    print(f"Pagina {i} tekst preview: {repr(preview)}")

                    # Optional: write HOCR for deeper analysis
                    if dbg_dir:
                        try:
                            hocr = pytesseract.image_to_pdf_or_hocr(img, extension='hocr')
                            hocr_path = os.path.join(dbg_dir, f"page_{i:03d}.hocr")
                            with open(hocr_path, "wb") as fh:
                                fh.write(hocr)
                            print(f"Saved debug HOCR: {hocr_path}")
                        except Exception as e_h:
                            print(f"WAARSCHUWING: kon HOCR niet genereren voor pagina {i}: {e_h}")

                except Exception as e_page:
                    print(f"FOUT: OCR gefaald op pagina {i}: {e_page}")

            if writer.get_num_pages() == 0:
                print("FOUT: geen pagina's toegevoegd aan output. (TXT).pdf wordt niet aangemaakt.")
                continue

            try:
                _write_final_pdf(writer, txt_path)
                print(f"OCR voltooid: {txt_path}")
                print(f"Niet-lege tekstpagina's: {non_empty_pages} van {page_count}")
            except Exception as e_write:
                print(f"FOUT: kon (TXT).pdf niet wegschrijven: {e_write}")

        except Exception as e:
            print(f"FOUT bij OCR '{file}': {e}")

    print("OCR afgerond.")

if __name__ == "__main__":
    # Allow standalone runs for quick tests
    config = read_config()
    folder = config.get("MAIN_FOLDER")
    poppler_path = config.get("POPPLER_PATH")
    tesseract_path = config.get("TESSERACT_PATH")
    debug_flag = config.get("DEBUG_OCR", "0").strip() == "1"

    if not folder or not poppler_path or not tesseract_path:
        raise RuntimeError("MAIN_FOLDER, POPPLER_PATH of TESSERACT_PATH ontbreekt in config.env")

    print(f"[{datetime.now().isoformat()}] Standalone OCR run")
    ocr_pdfs(folder, poppler_path, tesseract_path, debug_ocr=debug_flag, dpi=300)
