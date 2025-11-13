import os
import subprocess
from utils.config_utils import read_config

def convert_kindle_to_pdf(folder):
    print("Kindle-conversie gestart...")

    for root, _, files in os.walk(folder):
        for file in files:
            fname = file.lower()
            if fname.endswith((".mobi", ".azw", ".azw3")):
                base = os.path.splitext(file)[0]
                pdf_path = os.path.join(root, base + ".pdf")
                txt_pdf_path = os.path.join(root, base + "(TXT).pdf")

                # Skip als er al een PDF of TXT bestaat
                if os.path.exists(pdf_path) or os.path.exists(txt_pdf_path):
                    print(f"SKIPPED: {file} → PDF bestaat al")
                    continue

                input_path = os.path.join(root, file)
                html_path = os.path.join(root, base + ".html")

                print(f"Stap 1: unpack {file} → {html_path}")
                try:
                    # KindleUnpack via command line
                    subprocess.run(["kindleunpack", input_path, html_path], check=True)
                except Exception as e:
                    print(f"FOUT bij unpacken {file}: {e}")
                    continue

                print(f"Stap 2: HTML → PDF {pdf_path}")
                try:
                    from weasyprint import HTML
                    HTML(html_path).write_pdf(pdf_path)
                    print(f"Succes: {pdf_path}")
                except Exception as e:
                    print(f"FOUT bij HTML→PDF {file}: {e}")

    print("Kindle-conversie afgerond.")

if __name__ == "__main__":
    config = read_config()
    folder = config.get("MAIN_FOLDER")
    if not folder:
        raise RuntimeError("MAIN_FOLDER ontbreekt in config.env")
    convert_kindle_to_pdf(folder)
