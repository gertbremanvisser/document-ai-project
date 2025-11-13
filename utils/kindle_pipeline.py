import os
import sys
from weasyprint import HTML

# Zorg dat KindleUnpack repo beschikbaar is
sys.path.append(os.path.join(os.path.dirname(__file__), "KindleUnpack"))
import kindleunpack

def unpack_to_html(input_path, output_html_path):
    """
    Unpack een Kindle-bestand naar HTML.
    """
    temp_dir = output_html_path + "_unpack"
    os.makedirs(temp_dir, exist_ok=True)

    # KindleUnpack schrijft alles naar temp_dir
    kindleunpack.unpackBook(input_path, temp_dir)

    # Zoek hoofd-HTML
    candidates = ["book.html", "index.html"]
    html_file = None
    for c in candidates:
        p = os.path.join(temp_dir, c)
        if os.path.exists(p):
            html_file = p
            break

    if not html_file:
        # fallback: eerste .html/.xhtml bestand
        for root, _, files in os.walk(temp_dir):
            for f in files:
                if f.lower().endswith((".html", ".xhtml")):
                    html_file = os.path.join(root, f)
                    break
            if html_file:
                break

    if not html_file:
        raise RuntimeError(f"Geen HTML gevonden in {input_path}")

    # Kopieer inhoud naar output_html_path
    with open(html_file, "r", encoding="utf-8", errors="ignore") as src, \
         open(output_html_path, "w", encoding="utf-8") as dst:
        dst.write(src.read())

def convert_html_to_pdf(html_path, pdf_path):
    """
    Zet HTML om naar PDF met WeasyPrint.
    """
    HTML(html_path).write_pdf(pdf_path)

def kindle_to_pdf_pipeline(base_folder):
    """
    Loop door alle Kindle-bestanden in base_folder en maak PDF's.
    """
    print(f"== Kindle → PDF pipeline gestart in {base_folder} ==")
    for root, _, files in os.walk(base_folder):
        for file in files:
            if file.lower().endswith((".mobi", ".azw", ".azw3")):
                in_path = os.path.join(root, file)
                stem = os.path.splitext(file)[0]
                html_path = os.path.join(root, stem + ".html")
                pdf_path = os.path.join(root, stem + ".pdf")

                if os.path.exists(pdf_path):
                    print(f"SKIP: {file} → PDF bestaat al")
                    continue

                try:
                    print(f"[UNPACK] {file}")
                    unpack_to_html(in_path, html_path)
                except Exception as e:
                    print(f"FOUT bij unpacken {file}: {e}")
                    continue

                try:
                    print(f"[PDF] {stem}.html → {stem}.pdf")
                    convert_html_to_pdf(html_path, pdf_path)
                    print(f"OK: {pdf_path}")
                except Exception as e:
                    print(f"FOUT bij HTML→PDF {file}: {e}")

    print("== Kindle → PDF pipeline afgerond ==")
