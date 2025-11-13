import os
from weasyprint import HTML

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
                    # WeasyPrint kan direct een EPUB-bestand lezen en renderen
                    HTML(in_path).write_pdf(pdf_path)
                    print(f"OK: {pdf_path}")
                except Exception as e:
                    print(f"FOUT bij EPUB→PDF {file}: {e}")

    print("== EPUB → PDF pipeline afgerond ==")
