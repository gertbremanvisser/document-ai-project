import os
import zipfile
import shutil
import traceback
from weasyprint import HTML

def unpack_epub(epub_path, output_dir):
    """
    Unzip een EPUB-bestand naar een tijdelijke map.
    """
    os.makedirs(output_dir, exist_ok=True)
    with zipfile.ZipFile(epub_path, 'r') as z:
        z.extractall(output_dir)

def fix_mojibake(document_text):
    """
    Herstelt veelvoorkomende UTF-8→latin1 mojibake in één keer.
    """
    markers = ("â€", "Ã", "â€œ", "â€˜", "â€™", "â€“", "â€”")
    if any(m in document_text for m in markers):
        try:
            return document_text.encode("latin1").decode("utf-8")
        except UnicodeError:
            return document_text
    return document_text

def gather_html_files(unpacked_dir):
    """
    Vind alle .xhtml/.html-bestanden (alfabetische volgorde als fallback).
    """
    found = []
    for root, _, files in os.walk(unpacked_dir):
        for f in files:
            if f.lower().endswith((".xhtml", ".html")):
                found.append(os.path.join(root, f))
    return sorted(found)

def merge_html_files(unpacked_dir, merged_html_path):
    """
    Voeg alle HTML/XHTML-bestanden samen tot één UTF-8 HTML-document.
    Inclusief encoding-fix en debug-output.
    """
    html_paths = gather_html_files(unpacked_dir)
    if not html_paths:
        raise RuntimeError("Geen HTML/XHTML-bestanden gevonden in EPUB")

    print("Samengevoegde bestanden:")
    parts = []
    for p in html_paths:
        try:
            with open(p, "rb") as src:
                raw = src.read()
            try:
                txt = raw.decode("utf-8")
                enc = "utf-8"
            except UnicodeDecodeError:
                txt = raw.decode("latin1")
                enc = "latin1"
            parts.append(f"<!-- BEGIN {os.path.relpath(p, unpacked_dir)} ({enc}) -->\n{txt}\n<!-- END -->")
            print(f" - {p} (encoding: {enc})")
        except Exception as e:
            print(f"FOUT bij lezen van {p}: {e}")

    if not parts:
        raise RuntimeError("Kon geen leesbare HTML delen samenstellen")

    merged = [
        "<!doctype html>",
        "<html>",
        "<head>",
        '<meta charset="utf-8">',
        "<title>EPUB merged</title>",
        "<style>hr{page-break-after:always;border:none;margin:0;padding:0}</style>",
        "</head>",
        "<body>",
    ]
    merged.extend(parts)
    merged.append("</body></html>")
    merged_text = "\n".join(merged)

    merged_text = fix_mojibake(merged_text)

    with open(merged_html_path, "w", encoding="utf-8") as dst:
        dst.write(merged_text)

def epub_to_pdf_pipeline(base_folder):
    """
    Loop door alle EPUB-bestanden in base_folder en maak volledige PDF's.
    Opruimen van alle tijdelijke bestanden en mappen na afloop.
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

                temp_dir = os.path.join(root, stem + "_unpack")
                merged_html = os.path.join(root, stem + "_merged.html")

                try:
                    print(f"[EPUB] {file} → {stem}.pdf")
                    unpack_epub(in_path, temp_dir)
                    merge_html_files(temp_dir, merged_html)

                    HTML(filename=merged_html, base_url=temp_dir).write_pdf(pdf_path)
                    print(f"OK: {pdf_path}")
                except Exception as e:
                    print(f"FOUT bij EPUB→PDF {file}: {e}")
                    traceback.print_exc()
                finally:
                    # Opruimen van tijdelijke bestanden en mappen
                    for temp in [temp_dir, merged_html]:
                        if os.path.exists(temp):
                            try:
                                if os.path.isdir(temp):
                                    shutil.rmtree(temp)
                                    print(f"Opruimen: map {temp} verwijderd")
                                else:
                                    os.remove(temp)
                                    print(f"Opruimen: bestand {temp} verwijderd")
                            except Exception as e:
                                print(f"Kon {temp} niet verwijderen: {e}")

    print("== EPUB → PDF pipeline afgerond ==")
