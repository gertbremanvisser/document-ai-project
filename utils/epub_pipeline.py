import os
import zipfile
import traceback
from weasyprint import HTML

def unpack_epub(epub_path, output_dir):
    """
    Unzip een EPUB-bestand naar een tijdelijke map.
    """
    os.makedirs(output_dir, exist_ok=True)
    with zipfile.ZipFile(epub_path, 'r') as z:
        z.extractall(output_dir)

def merge_html_files(unpacked_dir, merged_html_path):
    """
    Zoek alle .xhtml/.html bestanden en voeg ze samen tot één HTML-document.
    Inclusief encoding-fix zodat rare tekens verdwijnen.
    Print ook een lijst van alle samengevoegde bestanden en hun encoding.
    """
    html_parts = []
    merged_files = []

    for root, _, files in os.walk(unpacked_dir):
        for f in sorted(files):
            if f.lower().endswith((".xhtml", ".html")):
                file_path = os.path.join(root, f)
                try:
                    with open(file_path, "rb") as src:
                        raw = src.read()
                    try:
                        text = raw.decode("utf-8")
                        encoding_used = "utf-8"
                    except UnicodeDecodeError:
                        text = raw.decode("latin1").encode("utf-8").decode("utf-8")
                        encoding_used = "latin1→utf-8"
                    html_parts.append(text)
                    merged_files.append((file_path, encoding_used))
                except Exception as e:
                    print(f"FOUT bij lezen van {f}: {e}")

    if not html_parts:
        raise RuntimeError("Geen HTML-bestanden gevonden in EPUB")

    # Debug: print alle samengevoegde bestanden en hun encoding
    print("Samengevoegde bestanden:")
    for path, enc in merged_files:
        print(f" - {path} (encoding: {enc})")

    with open(merged_html_path, "w", encoding="utf-8") as dst:
        dst.write("<html><body>")
        for part in html_parts:
            dst.write(part)
            dst.write("<hr/>")  # scheiding tussen hoofdstukken
        dst.write("</body></html>")

def epub_to_pdf_pipeline(base_folder):
    """
    Loop door alle EPUB-bestanden in base_folder en maak PDF's.
    """
    print(f"== EPUB → PDF pipeline gestart in {base_folder} ==")

    for root, _, files in os.walk(base_folder):
        for file in files:
            if file.lower().endswith(".epub"):
                in_path = os.path.join(root, file)
                stem = os.path.splitext(file)[0]
                pdf_path = os.path.join(root, stem + ".pdf")

                if os.path.exists(pdf_path):
                    print(f"SKIP: {file} → PDF bestaat al")
                    continue

                try:
                    print(f"[EPUB] {file} → {stem}.pdf")
                    temp_dir = os.path.join(root, stem + "_unpack")
                    unpack_epub(in_path, temp_dir)

                    merged_html = os.path.join(root, stem + "_merged.html")
                    merge_html_files(temp_dir, merged_html)

                    HTML(merged_html).write_pdf(pdf_path)
                    print(f"OK: {pdf_path}")
                except Exception as e:
                    print(f"FOUT bij EPUB→PDF {file}: {e}")
                    traceback.print_exc()

    print("== EPUB → PDF pipeline afgerond ==")
